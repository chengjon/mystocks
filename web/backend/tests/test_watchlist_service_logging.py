from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path

import psycopg2


def load_watchlist_module(monkeypatch):
    module_path = Path("web/backend/app/services/watchlist_service.py")
    module_name = "test_watchlist_service_logging_module"
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    monkeypatch.setattr(module.WatchlistService, "_ensure_table_exists", lambda self: None)
    return module


class StubCursor:
    def __init__(self, fetchone_result=None):
        self.fetchone_result = fetchone_result
        self.rowcount = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, *_args, **_kwargs):
        return None

    def fetchone(self):
        return self.fetchone_result


class StubConnection:
    def __init__(self, cursor: StubCursor):
        self._cursor = cursor

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self, *args, **kwargs):
        return self._cursor

    def commit(self):
        return None


def test_watchlist_service_source_contains_no_print_statements():
    source = Path("web/backend/app/services/watchlist_service.py").read_text(encoding="utf-8")

    assert "print(" not in source


def test_add_to_watchlist_logs_database_errors(monkeypatch, caplog):
    module = load_watchlist_module(monkeypatch)
    service = module.WatchlistService(db_config={})

    def raise_db_error():
        raise psycopg2.Error("db unavailable")

    monkeypatch.setattr(service, "_get_connection", raise_db_error)

    with caplog.at_level(logging.ERROR, logger=module.__name__):
        result = service.add_to_watchlist(user_id=1, symbol="000001", display_name="平安银行")

    assert result is False
    assert any("添加自选股时发生错误" in record.getMessage() for record in caplog.records)
    assert any(record.exc_info is not None for record in caplog.records)


def test_delete_group_logs_warning_for_default_group(monkeypatch, caplog):
    module = load_watchlist_module(monkeypatch)
    service = module.WatchlistService(db_config={})
    cursor = StubCursor(fetchone_result=("默认分组",))

    monkeypatch.setattr(service, "_get_connection", lambda: StubConnection(cursor))

    with caplog.at_level(logging.WARNING, logger=module.__name__):
        result = service.delete_group(user_id=1, group_id=101)

    assert result is False
    assert any(
        record.levelno == logging.WARNING and record.getMessage() == "不能删除默认分组" for record in caplog.records
    )
