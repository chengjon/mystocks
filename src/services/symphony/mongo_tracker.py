from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo import ASCENDING

from src.services.symphony.config import TrackerConfig
from src.services.symphony.models import Issue


class MongoWorkItemTrackerClient:
    """Mongo-backed tracker client that dispatches from Maestro work items."""

    def __init__(self, tracker: TrackerConfig, database: Any, *, mongo_client: Any | None = None) -> None:
        self.tracker = tracker
        self._database = database
        self._mongo_client = mongo_client
        self._work_items = database["work_items"]
        self._worker_status_views = database["worker_status_views"]

    def close(self) -> None:
        if self._mongo_client is not None and hasattr(self._mongo_client, "close"):
            self._mongo_client.close()

    def fetch_candidate_issues(self) -> list[Issue]:
        return self.fetch_issues_by_states(self.tracker.active_states)

    def fetch_issues_by_states(self, state_names: list[str]) -> list[Issue]:
        normalized_states = [state.strip().lower() for state in state_names if state.strip()]
        if not normalized_states:
            return []

        issues: list[Issue] = []
        for work_item in self._work_items.find({}).sort("created_at", ASCENDING):
            issue = self._to_issue(work_item)
            if issue.state.strip().lower() in normalized_states:
                issues.append(issue)
        return issues

    def fetch_issue_states_by_ids(self, issue_ids: list[str]) -> list[Issue]:
        if not issue_ids:
            return []

        issues_by_id: dict[str, Issue] = {}
        for work_item in self._work_items.find({}).sort("created_at", ASCENDING):
            issue = self._to_issue(work_item)
            if issue.id in issue_ids:
                issues_by_id[issue.id] = issue
        return [issues_by_id[issue_id] for issue_id in issue_ids if issue_id in issues_by_id]

    def _to_issue(self, work_item: dict[str, Any]) -> Issue:
        status_view = self._worker_status_views.find_one({"work_item_id": work_item["work_item_id"]})
        state = status_view["status"] if status_view is not None else work_item["status"]
        updated_at = status_view["updated_at"] if status_view is not None else work_item.get("updated_at")
        return Issue(
            id=str(work_item["work_item_id"]),
            identifier=str(work_item["work_item_id"]),
            title=str(work_item["title"]),
            description=str(work_item.get("objective") or ""),
            priority=None,
            state=str(state),
            branch_name=work_item.get("branch"),
            url=None,
            labels=[],
            blocked_by=[],
            created_at=_parse_timestamp(work_item.get("created_at")),
            updated_at=_parse_timestamp(updated_at),
        )


def _parse_timestamp(value: Any) -> datetime | None:
    if not value:
        return None
    normalized = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None
