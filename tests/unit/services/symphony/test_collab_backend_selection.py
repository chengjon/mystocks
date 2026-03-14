from __future__ import annotations

from pathlib import Path

from src.services.maestro.collab.registry import SQLiteCollaborationRegistry
from src.services.maestro.collab.runtime_registry import DualWriteCollaborationRegistry, MongoCollaborationRegistry
from src.services.symphony.config import ServiceConfig
from src.services.symphony.models import WorkflowDefinition
from src.services.symphony.service import SymphonyService


def test_service_config_reads_collab_backend_runtime_settings() -> None:
    definition = WorkflowDefinition(
        config={
            "tracker": {"kind": "local"},
            "runtime": {
                "collab_backend": "dual-write",
                "collab_mongo_uri": "mongodb://mongo:27017",
                "collab_mongo_db": "runtime_coord",
            },
        },
        prompt_template="Prompt",
    )

    config = ServiceConfig.from_workflow_definition(definition)

    assert config.runtime.collab_backend == "dual-write"
    assert config.runtime.collab_mongo_uri == "mongodb://mongo:27017"
    assert config.runtime.collab_mongo_db == "runtime_coord"


def test_create_collab_registry_returns_sqlite_by_default(tmp_path: Path) -> None:
    config = _service_config()

    registry = SymphonyService._create_collab_registry(config)

    assert isinstance(registry, SQLiteCollaborationRegistry)


def test_create_collab_registry_can_return_mongo_registry(monkeypatch, tmp_path: Path) -> None:
    config = _service_config(
        runtime={
            "collab_backend": "mongo",
            "collab_mongo_uri": "mongodb://mongo:27017",
            "collab_mongo_db": "runtime_coord",
        }
    )
    monkeypatch.setattr("src.services.symphony.service.MongoClient", lambda _uri: _FakeMongoClient())

    registry = SymphonyService._create_collab_registry(config)

    assert isinstance(registry, MongoCollaborationRegistry)


def test_create_collab_registry_can_return_dual_write_registry(monkeypatch, tmp_path: Path) -> None:
    config = _service_config(
        runtime={
            "collab_backend": "dual-write",
            "collab_mongo_uri": "mongodb://mongo:27017",
            "collab_mongo_db": "runtime_coord",
        }
    )
    monkeypatch.setattr("src.services.symphony.service.MongoClient", lambda _uri: _FakeMongoClient())

    registry = SymphonyService._create_collab_registry(config)

    assert isinstance(registry, DualWriteCollaborationRegistry)


def test_create_collab_registry_can_return_mongo_registry_for_mongo_tracker(monkeypatch) -> None:
    definition = WorkflowDefinition(
        config={
            "tracker": {
                "kind": "mongo",
                "mongo_uri": "mongodb://mongo:27017",
                "mongo_db": "runtime_coord",
                "active_states": ["created", "dispatched", "in_progress"],
                "terminal_states": ["verified", "merged"],
            },
            "runtime": {
                "collab_backend": "mongo",
                "collab_mongo_uri": "mongodb://mongo:27017",
                "collab_mongo_db": "runtime_coord",
            },
        },
        prompt_template="Prompt",
    )
    config = ServiceConfig.from_workflow_definition(definition)
    monkeypatch.setattr("src.services.symphony.service.MongoClient", lambda _uri: _FakeMongoClient())

    registry = SymphonyService._create_collab_registry(config)

    assert isinstance(registry, MongoCollaborationRegistry)


def _service_config(runtime: dict | None = None) -> ServiceConfig:
    definition = WorkflowDefinition(
        config={
            "tracker": {"kind": "local", "sqlite_path": ".symphony/tracker.db"},
            "runtime": runtime or {},
        },
        prompt_template="Prompt",
    )
    return ServiceConfig.from_workflow_definition(definition)


class _FakeMongoClient:
    def __getitem__(self, _name: str):
        return {
            "issue_assignments": _FakeMongoCollection(),
            "worktree_registry": _FakeMongoCollection(),
            "worker_heartbeats": _FakeMongoCollection(),
        }


class _FakeMongoCollection:
    def create_indexes(self, _indexes) -> None:
        return None
