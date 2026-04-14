from __future__ import annotations

import importlib
import sys
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


def _load_module():
    sys.modules.pop("app.api.data_lineage", None)
    return importlib.import_module("app.api.data_lineage")


async def test_get_lineage_tracker_wraps_asyncpg_connection_for_storage():
    fake_asyncpg = ModuleType("asyncpg")
    fake_lineage = ModuleType("src.data_governance.lineage")

    class FakeConnection:
        def __init__(self):
            self.closed = False

        async def close(self):
            self.closed = True

    raw_connection = FakeConnection()

    async def fake_connect(**kwargs):
        return raw_connection

    class FakeLineageStorage:
        def __init__(self, db):
            self.db = db

    class FakeLineageTracker:
        def __init__(self, storage):
            self._storage = storage

    fake_asyncpg.connect = fake_connect
    fake_lineage.LineageStorage = FakeLineageStorage
    fake_lineage.LineageTracker = FakeLineageTracker

    previous_asyncpg = sys.modules.get("asyncpg")
    previous_lineage = sys.modules.get("src.data_governance.lineage")
    sys.modules["asyncpg"] = fake_asyncpg
    sys.modules["src.data_governance.lineage"] = fake_lineage

    try:
        module = _load_module()
        tracker, connection_adapter = await module.get_lineage_tracker()
    finally:
        if previous_asyncpg is None:
            sys.modules.pop("asyncpg", None)
        else:
            sys.modules["asyncpg"] = previous_asyncpg

        if previous_lineage is None:
            sys.modules.pop("src.data_governance.lineage", None)
        else:
            sys.modules["src.data_governance.lineage"] = previous_lineage

    assert tracker._storage.db is connection_adapter

    async with connection_adapter.acquire_connection() as conn:
        assert conn is raw_connection

    await connection_adapter.close()
    assert raw_connection.closed is True
