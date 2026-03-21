from __future__ import annotations

import builtins
import importlib
import sys


def test_database_table_manager_part1_tolerates_taos_runtime_import_errors(monkeypatch) -> None:
    module_name = "src.storage.database.database_manager.database_table_manager_methods.part1"
    original_import_module = importlib.import_module

    def guarded_import(name: str, package: str | None = None):
        if name == "taos":
            raise RuntimeError("libtaos.so missing")
        return original_import_module(name, package)

    monkeypatch.setattr(importlib, "import_module", guarded_import)
    sys.modules.pop("taos", None)
    sys.modules.pop(module_name, None)

    module = importlib.import_module(module_name)

    assert module.TAOS_AVAILABLE is False
    assert module.TAOS_MODULE_TYPE is None
