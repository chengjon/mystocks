from __future__ import annotations

import json

import pytest
from pymongo.errors import OperationFailure

from scripts.runtime import smoke_mongo_multicli
from scripts.runtime.smoke_mongo_multicli import run_smoke


def test_run_smoke_returns_summary_with_control_plane_and_status_views(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    monkeypatch.setattr("scripts.runtime.smoke_mongo_multicli.build_project_runtime_mongo_client", lambda *_args, **_kwargs: fake_client)

    summary = run_smoke(mongo_uri="mongodb://localhost:27017", mongo_db="smoke_test_db")

    assert summary["work_item_id"] == "SMOKE-1"
    assert summary["assignment_status"] == "retrying"
    assert summary["control_plane_status"] == "ready_for_review"
    assert summary["status_api_control_plane_count"] == 1
    assert summary["db_name"] == "smoke_test_db"
    assert fake_client.dropped == ["smoke_test_db"]


def test_run_smoke_can_use_env_driven_mongo_connection(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    captured: dict[str, object] = {}
    monkeypatch.setattr(
        "scripts.runtime.smoke_mongo_multicli.build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or fake_client,
    )

    summary = run_smoke(mongo_uri=None, mongo_db="smoke_env_db")

    assert summary["db_name"] == "smoke_env_db"
    assert fake_client.dropped == ["smoke_env_db"]
    assert captured == {
        "project_root": str(smoke_mongo_multicli.PROJECT_ROOT),
        "mongo_uri": None,
        "server_selection_timeout_ms": 3000,
    }


def test_build_mongo_client_can_fallback_to_local_docker_container_credentials(monkeypatch) -> None:
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        smoke_mongo_multicli,
        "build_project_runtime_mongo_client",
        lambda project_root, mongo_uri, server_selection_timeout_ms=3000: captured.update(
            {"project_root": str(project_root), "mongo_uri": mongo_uri, "server_selection_timeout_ms": server_selection_timeout_ms}
        )
        or _FakeMongoClient(),
    )

    smoke_mongo_multicli._build_mongo_client(None)

    assert str(smoke_mongo_multicli.PROJECT_ROOT) == captured["project_root"]
    assert captured["mongo_uri"] is None
    assert captured["server_selection_timeout_ms"] == 3000


def test_run_smoke_skips_drop_database_when_mongo_setup_fails(monkeypatch) -> None:
    fake_client = _FailingMongoClient()
    monkeypatch.setattr("scripts.runtime.smoke_mongo_multicli.build_project_runtime_mongo_client", lambda *_args, **_kwargs: fake_client)

    with pytest.raises(RuntimeError, match="mongo unavailable"):
        run_smoke(mongo_uri="mongodb://localhost:27017", mongo_db="smoke_fail_db")

    assert fake_client.drop_attempts == 0
    assert fake_client.closed is True


def test_run_smoke_skips_drop_database_when_write_access_fails_after_db_resolution(monkeypatch) -> None:
    fake_client = _UnauthorizedMongoClient()
    monkeypatch.setattr("scripts.runtime.smoke_mongo_multicli.build_project_runtime_mongo_client", lambda *_args, **_kwargs: fake_client)

    with pytest.raises(RuntimeError, match="Mongo smoke requires writable credentials"):
        run_smoke(mongo_uri="mongodb://localhost:27017", mongo_db="smoke_unauthorized_db")

    assert fake_client.drop_attempts == 0
    assert fake_client.closed is True


def test_main_emits_structured_json_error_when_run_smoke_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        smoke_mongo_multicli,
        "run_smoke",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Mongo smoke requires writable credentials")),
    )

    exit_code = smoke_mongo_multicli.main(["--mongo-uri", "mongodb://bad:bad@localhost:27017/admin?authSource=admin"])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_code"] == "RuntimeError"
    assert "Mongo smoke requires writable credentials" in payload["message"]


class _FakeMongoClient:
    def __init__(self) -> None:
        self.databases: dict[str, _FakeDatabase] = {}
        self.dropped: list[str] = []

    def __getitem__(self, name: str) -> "_FakeDatabase":
        database = self.databases.get(name)
        if database is None:
            database = _FakeDatabase()
            self.databases[name] = database
        return database

    def drop_database(self, name: str) -> None:
        self.dropped.append(name)
        self.databases.pop(name, None)

    def close(self) -> None:
        return None


class _FailingMongoClient:
    def __init__(self) -> None:
        self.drop_attempts = 0
        self.closed = False

    def __getitem__(self, name: str):
        raise RuntimeError("mongo unavailable")

    def drop_database(self, name: str) -> None:
        self.drop_attempts += 1
        raise AssertionError("drop_database should not run when setup never succeeded")

    def close(self) -> None:
        self.closed = True


class _UnauthorizedMongoClient:
    def __init__(self) -> None:
        self.drop_attempts = 0
        self.closed = False

    def __getitem__(self, _name: str):
        return _UnauthorizedDatabase()

    def drop_database(self, _name: str) -> None:
        self.drop_attempts += 1
        raise AssertionError("drop_database should not run when setup never completed")

    def close(self) -> None:
        self.closed = True


class _UnauthorizedDatabase:
    def __getitem__(self, _name: str):
        return _UnauthorizedCollection()


class _UnauthorizedCollection:
    def create_indexes(self, _indexes) -> None:
        raise OperationFailure(
            "createIndexes requires authentication",
            13,
            {"ok": 0.0, "errmsg": "createIndexes requires authentication", "code": 13, "codeName": "Unauthorized"},
        )


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "work_updates": _FakeCollection(),
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
            "issue_assignments": _FakeCollection(),
            "worktree_registry": _FakeCollection(),
            "worker_heartbeats": _FakeCollection(),
        }

    def __getitem__(self, name: str) -> "_FakeCollection":
        return self._collections[name]


class _FakeCollection:
    def __init__(self) -> None:
        self.docs: list[dict] = []
        self.indexes = []

    def create_indexes(self, indexes) -> None:
        self.indexes.extend(indexes)

    def replace_one(self, filter_query: dict, document: dict, *, upsert: bool = False) -> None:
        for index, existing in enumerate(self.docs):
            if _matches(existing, filter_query):
                self.docs[index] = document.copy()
                return
        if upsert:
            self.docs.append(document.copy())

    def find_one(self, filter_query: dict) -> dict | None:
        for document in self.docs:
            if _matches(document, filter_query):
                return document.copy()
        return None

    def insert_one(self, document: dict) -> None:
        self.docs.append(document.copy())

    def find(self, filter_query: dict):
        return _FakeCursor([document.copy() for document in self.docs if _matches(document, filter_query)])


class _FakeCursor:
    def __init__(self, docs: list[dict]) -> None:
        self._docs = docs

    def sort(self, key: str, _direction: int):
        self._docs.sort(key=lambda document: str(document.get(key, "")))
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
