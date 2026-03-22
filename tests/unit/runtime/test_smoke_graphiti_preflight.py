from __future__ import annotations

import json

import pytest

from scripts.runtime import smoke_graphiti_preflight


def test_run_smoke_creates_temp_work_item_and_runs_shared_preflight(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    calls: list[list[str]] = []

    monkeypatch.setattr(smoke_graphiti_preflight, "_build_mongo_client", lambda _mongo_uri: fake_client)

    def _fake_run(argv: list[str]) -> dict[str, object]:
        calls.append(argv)
        return {
            "server_status": "ok",
            "ingest_status": "completed",
            "search_outcome": "hit",
            "search_summary": "nodes hit=1, facts hit=1",
            "episode_uuid": "ep-preflight",
        }

    monkeypatch.setattr(smoke_graphiti_preflight, "_run_coordctl_json", _fake_run)

    summary = smoke_graphiti_preflight.run_smoke(
        mongo_uri="mongodb://localhost:27017",
        mongo_db="graphiti_preflight_smoke_db",
        actor_cli="cli-preflight",
    )

    assert summary["work_item_id"] == "GRAPHITI-PREFLIGHT-SMOKE"
    assert summary["server_status"] == "ok"
    assert summary["search_outcome"] == "hit"
    assert calls[0][:4] == ["--mongo-uri", "mongodb://localhost:27017", "--mongo-db", "graphiti_preflight_smoke_db"]
    assert calls[0][4:6] == ["graphiti", "preflight"]
    assert "--write-memory" in calls[0]
    assert fake_client.dropped == ["graphiti_preflight_smoke_db"]


def test_main_emits_json_summary(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "run_smoke",
        lambda **_: {
            "work_item_id": "GRAPHITI-PREFLIGHT-SMOKE",
            "server_status": "ok",
            "search_outcome": "hit",
        },
    )

    assert smoke_graphiti_preflight.main(
        [
            "--mongo-uri",
            "mongodb://localhost:27017",
            "--mongo-db",
            "graphiti_preflight_smoke_db",
            "--actor-cli",
            "cli-preflight",
        ]
    ) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["work_item_id"] == "GRAPHITI-PREFLIGHT-SMOKE"


def test_run_smoke_passes_resolved_mongo_uri_when_env_driven(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    calls: list[list[str]] = []

    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "_resolve_effective_mongo_uri",
        lambda _mongo_uri: "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin",
    )
    monkeypatch.setattr(smoke_graphiti_preflight, "_build_mongo_client", lambda _mongo_uri: fake_client)
    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "_run_coordctl_json",
        lambda argv: calls.append(argv) or {
            "server_status": "ok",
            "ingest_status": "completed",
            "search_outcome": "hit",
            "search_summary": "nodes hit=1, facts hit=1",
        },
    )

    smoke_graphiti_preflight.run_smoke(
        mongo_uri=None,
        mongo_db="graphiti_preflight_smoke_db",
        actor_cli="cli-preflight",
    )

    assert calls[0][:4] == [
        "--mongo-uri",
        "mongodb://coord-user:coord-pass@mongo-host:27017/admin?authSource=admin",
        "--mongo-db",
        "graphiti_preflight_smoke_db",
    ]


def test_run_smoke_uses_unique_default_db_name(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    calls: list[list[str]] = []

    monkeypatch.setattr(smoke_graphiti_preflight, "_resolve_effective_mongo_uri", lambda _mongo_uri: "mongodb://localhost:27017")
    monkeypatch.setattr(smoke_graphiti_preflight, "_build_mongo_client", lambda _mongo_uri: fake_client)
    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "uuid4",
        lambda: type("FakeUUID", (), {"hex": "abc12345ffff"})(),
    )
    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "_run_coordctl_json",
        lambda argv: calls.append(argv) or {
            "server_status": "ok",
            "ingest_status": "completed",
            "search_outcome": "hit",
            "search_summary": "nodes hit=1, facts hit=1",
            "episode_uuid": "ep-preflight",
        },
    )

    summary = smoke_graphiti_preflight.run_smoke(
        mongo_uri=None,
        mongo_db=None,
        actor_cli="cli-preflight",
    )

    assert summary["db_name"] == "graphiti_preflight_smoke_abc12345"
    assert calls[0][:4] == ["--mongo-uri", "mongodb://localhost:27017", "--mongo-db", "graphiti_preflight_smoke_abc12345"]
    assert fake_client.dropped == ["graphiti_preflight_smoke_abc12345"]


def test_run_smoke_skips_drop_database_when_mongo_setup_fails(monkeypatch) -> None:
    fake_client = _FailingMongoClient()

    monkeypatch.setattr(smoke_graphiti_preflight, "_build_mongo_client", lambda _mongo_uri: fake_client)

    with pytest.raises(RuntimeError, match="mongo unavailable"):
        smoke_graphiti_preflight.run_smoke(
            mongo_uri=None,
            mongo_db="graphiti_preflight_smoke_db",
            actor_cli="cli-preflight",
        )

    assert fake_client.closed is True
    assert fake_client.drop_attempts == 0


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
        self.closed = False
        self.drop_attempts = 0

    def __getitem__(self, name: str):
        raise RuntimeError("mongo unavailable")

    def drop_database(self, name: str) -> None:
        self.drop_attempts += 1
        raise AssertionError("drop_database should not run when setup never succeeded")

    def close(self) -> None:
        self.closed = True


class _FakeDatabase:
    def __init__(self) -> None:
        self._collections = {
            "work_items": _FakeCollection(),
            "work_updates": _FakeCollection(),
            "work_requests": _FakeCollection(),
            "work_events": _FakeCollection(),
            "worker_status_views": _FakeCollection(),
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
        if document.get(key) != value:
            return False
    return True
