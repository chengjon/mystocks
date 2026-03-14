from __future__ import annotations

import os

from scripts.runtime.smoke_mongo_multicli import run_smoke


def test_run_smoke_returns_summary_with_control_plane_and_status_views(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    monkeypatch.setattr("scripts.runtime.smoke_mongo_multicli.MongoClient", lambda *_args, **_kwargs: fake_client)

    summary = run_smoke(mongo_uri="mongodb://localhost:27017", mongo_db="smoke_test_db")

    assert summary["work_item_id"] == "SMOKE-1"
    assert summary["assignment_status"] == "retrying"
    assert summary["control_plane_status"] == "ready_for_review"
    assert summary["status_api_control_plane_count"] == 1
    assert summary["db_name"] == "smoke_test_db"
    assert fake_client.dropped == ["smoke_test_db"]


def test_run_smoke_can_use_env_driven_mongo_connection(monkeypatch) -> None:
    fake_client = _FakeMongoClient()
    calls: list[str] = []
    monkeypatch.setattr("scripts.runtime.smoke_mongo_multicli.MongoClient", lambda **_kwargs: fake_client)
    monkeypatch.setattr("scripts.runtime.smoke_mongo_multicli.load_dotenv", lambda path, override=False: calls.append(str(path)))
    monkeypatch.setattr(
        "scripts.runtime.smoke_mongo_multicli.get_mongo_connection_kwargs",
        lambda **_kwargs: {"host": "localhost", "port": 27017, "username": "mongo", "password": "secret"},
    )

    summary = run_smoke(mongo_uri=None, mongo_db="smoke_env_db")

    assert summary["db_name"] == "smoke_env_db"
    assert fake_client.dropped == ["smoke_env_db"]
    assert calls


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
