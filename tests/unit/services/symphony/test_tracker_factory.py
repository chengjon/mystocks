from pathlib import Path

from src.services.symphony.config import ServiceConfig
from src.services.symphony.linear_client import LinearIssueTrackerClient
from src.services.symphony.local_tracker import LocalIssueTrackerClient
from src.services.symphony.models import WorkflowDefinition
from src.services.symphony.mongo_tracker import MongoWorkItemTrackerClient
from src.services.symphony.tracker_factory import create_tracker_client


def test_create_tracker_client_builds_linear_tracker() -> None:
    config = ServiceConfig.from_workflow_definition(
        WorkflowDefinition(
            config={
                "tracker": {
                    "kind": "linear",
                    "project_slug": "mystocks",
                    "api_key": "token",
                }
            },
            prompt_template="Prompt",
        )
    )

    tracker_client = create_tracker_client(config.tracker)
    try:
        assert isinstance(tracker_client, LinearIssueTrackerClient)
    finally:
        tracker_client.close()


def test_create_tracker_client_builds_local_tracker(tmp_path: Path) -> None:
    config = ServiceConfig.from_workflow_definition(
        WorkflowDefinition(
            config={
                "tracker": {
                    "kind": "local",
                    "sqlite_path": str(tmp_path / "tracker.db"),
                }
            },
            prompt_template="Prompt",
        )
    )

    tracker_client = create_tracker_client(config.tracker)
    try:
        assert isinstance(tracker_client, LocalIssueTrackerClient)
    finally:
        tracker_client.close()


def test_create_tracker_client_builds_mongo_tracker(monkeypatch) -> None:
    config = ServiceConfig.from_workflow_definition(
        WorkflowDefinition(
            config={
                "tracker": {
                    "kind": "mongo",
                    "mongo_uri": "mongodb://mongo:27017",
                    "mongo_db": "mystocks_coord",
                    "active_states": ["created", "dispatched", "in_progress"],
                    "terminal_states": ["verified", "merged"],
                }
            },
            prompt_template="Prompt",
        )
    )
    monkeypatch.setattr("src.services.symphony.tracker_factory.MongoClient", lambda _uri: _FakeMongoClient())

    tracker_client = create_tracker_client(config.tracker)
    try:
        assert isinstance(tracker_client, MongoWorkItemTrackerClient)
    finally:
        tracker_client.close()


class _FakeMongoClient:
    def __getitem__(self, _name: str):
        return {
            "work_items": _FakeMongoCollection(),
            "worker_status_views": _FakeMongoCollection(),
        }


class _FakeMongoCollection:
    def find(self, _query: dict):
        return _FakeMongoCursor([])

    def find_one(self, _query: dict):
        return None


class _FakeMongoCursor:
    def __init__(self, docs):
        self._docs = docs

    def sort(self, _key: str, _direction: int):
        return self

    def __iter__(self):
        return iter(self._docs)
