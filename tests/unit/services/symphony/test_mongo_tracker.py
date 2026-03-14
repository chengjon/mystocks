from __future__ import annotations

from datetime import UTC, datetime

from src.services.symphony.config import TrackerConfig
from src.services.symphony.mongo_tracker import MongoWorkItemTrackerClient


def test_mongo_tracker_fetches_candidates_from_work_items_and_status_views() -> None:
    client = MongoWorkItemTrackerClient(_tracker_config(), _FakeDatabase())
    client._work_items.docs.extend(  # noqa: SLF001
        [
            {
                "work_item_id": "MT-700",
                "title": "Dispatch me",
                "objective": "Use mongo tracker",
                "branch": "feat/mongo-tracker",
                "owner_cli": "gemini",
                "status": "dispatched",
                "created_at": "2026-03-14T04:00:00+00:00",
                "updated_at": "2026-03-14T04:00:00+00:00",
            },
            {
                "work_item_id": "MT-701",
                "title": "Not active",
                "objective": "Done item",
                "branch": "feat/done",
                "owner_cli": "codex",
                "status": "merged",
                "created_at": "2026-03-14T05:00:00+00:00",
                "updated_at": "2026-03-14T05:00:00+00:00",
            },
        ]
    )
    client._worker_status_views.docs.append(  # noqa: SLF001
        {
            "work_item_id": "MT-700",
            "branch": "feat/mongo-tracker",
            "owner_cli": "gemini",
            "status": "in_progress",
            "latest_update": "Collected runtime wiring failures",
            "blocker": None,
            "has_pending_request": False,
            "updated_at": "2026-03-14T04:05:00+00:00",
        }
    )

    candidates = client.fetch_candidate_issues()

    assert [issue.identifier for issue in candidates] == ["MT-700"]
    assert candidates[0].state == "in_progress"
    assert candidates[0].branch_name == "feat/mongo-tracker"


def test_mongo_tracker_fetches_issue_state_by_ids() -> None:
    client = MongoWorkItemTrackerClient(_tracker_config(), _FakeDatabase())
    client._work_items.docs.extend(  # noqa: SLF001
        [
            {
                "work_item_id": "MT-710",
                "title": "Alpha",
                "objective": "Alpha objective",
                "branch": "feat/alpha",
                "owner_cli": "gemini",
                "status": "created",
                "created_at": "2026-03-14T06:00:00+00:00",
                "updated_at": "2026-03-14T06:00:00+00:00",
            },
            {
                "work_item_id": "MT-711",
                "title": "Beta",
                "objective": "Beta objective",
                "branch": "feat/beta",
                "owner_cli": "codex",
                "status": "verified",
                "created_at": "2026-03-14T07:00:00+00:00",
                "updated_at": "2026-03-14T07:00:00+00:00",
            },
        ]
    )

    issues = client.fetch_issue_states_by_ids(["MT-711", "MT-710"])

    assert [issue.identifier for issue in issues] == ["MT-711", "MT-710"]
    assert [issue.state for issue in issues] == ["verified", "created"]


def test_mongo_tracker_close_closes_underlying_client() -> None:
    fake_client = _ClosableClient()
    client = MongoWorkItemTrackerClient(_tracker_config(), _FakeDatabase(), mongo_client=fake_client)

    client.close()

    assert fake_client.closed is True


def _tracker_config() -> TrackerConfig:
    return TrackerConfig(
        kind="mongo",
        endpoint="",
        api_key="",
        project_slug="",
        active_states=["created", "dispatched", "in_progress", "ready_for_review"],
        terminal_states=["verified", "merged", "archived"],
        sqlite_path=None,
        active_state_names=["created", "dispatched", "in_progress", "ready_for_review"],
        terminal_state_names=["verified", "merged", "archived"],
        mongo_uri="mongodb://localhost:27017",
        mongo_db="mystocks_coord",
    )


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
        }

    def __getitem__(self, name: str) -> _FakeCollection:
        return self._collections[name]


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict] = []

    def find(self, filter_query: dict):
        return _FakeCursor([doc.copy() for doc in self.docs if _matches(doc, filter_query)])

    def find_one(self, filter_query: dict) -> dict | None:
        for document in self.docs:
            if _matches(document, filter_query):
                return document.copy()
        return None


class _FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def sort(self, key: str, _direction: int):
        self._docs.sort(key=lambda document: document[key])
        return self

    def __iter__(self):
        return iter(self._docs)


def _matches(document: dict, filter_query: dict) -> bool:
    for key, value in filter_query.items():
        expected = value
        actual = document.get(key)
        if isinstance(expected, dict) and "$in" in expected:
            if actual not in expected["$in"]:
                return False
        elif actual != expected:
            return False
    return True


class _ClosableClient:
    def __init__(self) -> None:
        self.closed = False

    def close(self) -> None:
        self.closed = True
