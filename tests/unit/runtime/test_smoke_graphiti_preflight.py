from __future__ import annotations

import json
from urllib.parse import parse_qs, urlparse

import pytest
import subprocess

from scripts.runtime import smoke_graphiti_preflight
from scripts.runtime import graphiti_smoke_common


def test_run_smoke_creates_temp_work_item_and_runs_shared_preflight(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    calls: list[list[str]] = []

    monkeypatch.setattr(smoke_graphiti_preflight, "_build_mongo_client", lambda _mongo_uri: fake_client)
    monkeypatch.setattr(smoke_graphiti_preflight, "get_effective_runtime_mongo_uri", lambda _mongo_uri: "mongodb://localhost:27017")

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


def test_main_emits_structured_json_error_when_run_smoke_fails(monkeypatch, capsys) -> None:
    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "run_smoke",
        lambda **_: (_ for _ in ()).throw(RuntimeError("Graphiti preflight smoke requires writable credentials")),
    )

    exit_code = smoke_graphiti_preflight.main(["--actor-cli", "cli-preflight"])

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["error_code"] == "RuntimeError"
    assert "Graphiti preflight smoke requires writable credentials" in payload["message"]


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


def test_resolve_effective_mongo_uri_can_fallback_to_local_docker_container_credentials(monkeypatch) -> None:
    monkeypatch.setattr(smoke_graphiti_preflight, "load_dotenv", lambda path, override=False: None)
    monkeypatch.setattr(
        smoke_graphiti_preflight,
        "get_effective_runtime_mongo_uri",
        lambda _mongo_uri: "mongodb://mongo:secret@127.0.0.1:27017/admin?authSource=admin",
    )

    resolved = smoke_graphiti_preflight._resolve_effective_mongo_uri(None)
    parsed = urlparse(resolved)

    assert parsed.username == "mongo"
    assert parsed.password == "secret"
    assert parsed.hostname == "127.0.0.1"
    assert parsed.port == 27017
    assert parse_qs(parsed.query)["authSource"] == ["admin"]


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


def test_run_coordctl_json_wraps_external_command_failure_as_runtime_error(monkeypatch) -> None:
    monkeypatch.setenv("GRAPHITI_SMOKE_COMMAND", "/tmp/fake-cmd")

    def _raise(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, ["fake", "cmd"], output="out", stderr="boom")

    monkeypatch.setattr(graphiti_smoke_common.subprocess, "run", _raise)

    with pytest.raises(RuntimeError, match="external smoke command failed"):
        smoke_graphiti_preflight._run_coordctl_json(["graphiti", "preflight"])


def test_run_coordctl_json_wraps_invalid_external_json_as_runtime_error(monkeypatch) -> None:
    monkeypatch.setenv("GRAPHITI_SMOKE_COMMAND", "/tmp/fake-cmd")
    monkeypatch.setattr(
        graphiti_smoke_common.subprocess,
        "run",
        lambda *_args, **_kwargs: type(
            "CompletedProcess",
            (),
            {"stdout": "not-json", "stderr": "", "returncode": 0},
        )(),
    )

    with pytest.raises(RuntimeError, match="external smoke command returned invalid JSON"):
        smoke_graphiti_preflight._run_coordctl_json(["graphiti", "preflight"])


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
