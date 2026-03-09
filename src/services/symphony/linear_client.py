from __future__ import annotations

from datetime import datetime
from typing import Any

import httpx

from .config import TrackerConfig
from .errors import TrackerRequestError
from .models import BlockerRef, Issue

CANDIDATE_ISSUES_QUERY = """
query CandidateIssues($projectSlug: String!, $stateNames: [String!], $after: String, $first: Int!) {
  issues(
    first: $first
    after: $after
    filter: {
      project: { slugId: { eq: $projectSlug } }
      state: { name: { in: $stateNames } }
    }
  ) {
    nodes {
      id
      identifier
      title
      description
      priority
      branchName
      url
      createdAt
      updatedAt
      state { name }
      labels { nodes { name } }
      relations {
        nodes {
          type
          issue { id identifier state { name } }
          relatedIssue { id identifier state { name } }
        }
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
""".strip()

ISSUES_BY_STATE_QUERY = """
query IssuesByStates($projectSlug: String!, $stateNames: [String!]) {
  issues(
    filter: {
      project: { slugId: { eq: $projectSlug } }
      state: { name: { in: $stateNames } }
    }
  ) {
    nodes {
      id
      identifier
      title
      description
      priority
      branchName
      url
      createdAt
      updatedAt
      state { name }
      labels { nodes { name } }
      relations {
        nodes {
          type
          issue { id identifier state { name } }
          relatedIssue { id identifier state { name } }
        }
      }
    }
  }
}
""".strip()

ISSUE_STATES_BY_IDS_QUERY = """
query IssueStatesByIds($issueIds: [ID!]) {
  issues(filter: { id: { in: $issueIds } }) {
    nodes {
      id
      identifier
      title
      description
      priority
      branchName
      url
      createdAt
      updatedAt
      state { name }
      labels { nodes { name } }
      relations {
        nodes {
          type
          issue { id identifier state { name } }
          relatedIssue { id identifier state { name } }
        }
      }
    }
  }
}
""".strip()


class LinearIssueTrackerClient:
    """Linear-compatible tracker reader for Symphony orchestration."""

    def __init__(
        self,
        tracker: TrackerConfig,
        timeout_ms: int = 30000,
        page_size: int = 50,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.tracker = tracker
        self.page_size = page_size
        self._client = httpx.Client(
            transport=transport,
            timeout=timeout_ms / 1000,
            headers={
                "Authorization": self.tracker.api_key,
                "Content-Type": "application/json",
            },
        )

    def close(self) -> None:
        self._client.close()

    def fetch_candidate_issues(self) -> list[Issue]:
        issues: list[Issue] = []
        after: str | None = None

        while True:
            payload = self._execute_graphql(
                CANDIDATE_ISSUES_QUERY,
                {
                    "projectSlug": self.tracker.project_slug,
                    "stateNames": self.tracker.active_state_names,
                    "after": after,
                    "first": self.page_size,
                },
            )
            issues_payload = payload.get("issues", {})
            issues.extend(self._normalize_issues(issues_payload.get("nodes", [])))

            page_info = issues_payload.get("pageInfo", {})
            if not page_info.get("hasNextPage"):
                return issues

            after = page_info.get("endCursor")
            if not after:
                raise TrackerRequestError("Missing endCursor for paginated Linear response.")

    def fetch_issues_by_states(self, state_names: list[str]) -> list[Issue]:
        if not state_names:
            return []

        payload = self._execute_graphql(
            ISSUES_BY_STATE_QUERY,
            {
                "projectSlug": self.tracker.project_slug,
                "stateNames": state_names,
            },
        )
        return self._normalize_issues(payload.get("issues", {}).get("nodes", []))

    def fetch_issue_states_by_ids(self, issue_ids: list[str]) -> list[Issue]:
        if not issue_ids:
            return []

        payload = self._execute_graphql(ISSUE_STATES_BY_IDS_QUERY, {"issueIds": issue_ids})
        return self._normalize_issues(payload.get("issues", {}).get("nodes", []))

    def execute_raw_graphql(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        return self._execute_graphql(query, variables or {}, operation_name=operation_name)

    def _execute_graphql(
        self,
        query: str,
        variables: dict[str, Any],
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        try:
            request_payload: dict[str, Any] = {
                "query": query,
                "variables": variables,
            }
            if operation_name:
                request_payload["operationName"] = operation_name
            response = self._client.post(
                self.tracker.endpoint,
                json=request_payload,
            )
        except httpx.HTTPError as exc:
            raise TrackerRequestError("Linear API request failed.") from exc

        if response.status_code != 200:
            raise TrackerRequestError(f"Linear API returned status {response.status_code}.")

        payload = response.json()
        if payload.get("errors"):
            raise TrackerRequestError("Linear GraphQL response contained errors.")

        data = payload.get("data")
        if not isinstance(data, dict):
            raise TrackerRequestError("Linear response did not include a valid data payload.")

        return data

    def _normalize_issues(self, raw_issues: list[dict[str, Any]]) -> list[Issue]:
        return [self._normalize_issue(raw_issue) for raw_issue in raw_issues]

    def _normalize_issue(self, raw_issue: dict[str, Any]) -> Issue:
        labels = [str(node.get("name", "")).strip().lower() for node in raw_issue.get("labels", {}).get("nodes", [])]
        labels = [label for label in labels if label]

        blocked_by: list[BlockerRef] = []
        for relation in raw_issue.get("relations", {}).get("nodes", []):
            if str(relation.get("type", "")).strip().lower() != "blocks":
                continue
            related_issue = relation.get("relatedIssue") or relation.get("issue") or {}
            blocked_by.append(
                BlockerRef(
                    id=related_issue.get("id"),
                    identifier=related_issue.get("identifier"),
                    state=(related_issue.get("state") or {}).get("name"),
                )
            )

        priority = raw_issue.get("priority")
        if not isinstance(priority, int):
            priority = None

        return Issue(
            id=str(raw_issue.get("id", "")),
            identifier=str(raw_issue.get("identifier", "")),
            title=str(raw_issue.get("title", "")),
            description=raw_issue.get("description"),
            priority=priority,
            state=(raw_issue.get("state") or {}).get("name", ""),
            branch_name=raw_issue.get("branchName"),
            url=raw_issue.get("url"),
            labels=labels,
            blocked_by=blocked_by,
            created_at=_parse_timestamp(raw_issue.get("createdAt")),
            updated_at=_parse_timestamp(raw_issue.get("updatedAt")),
        )


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    if not isinstance(value, str):
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
