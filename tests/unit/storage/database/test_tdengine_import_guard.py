from __future__ import annotations

import builtins
import importlib
import sys


def test_database_table_manager_part1_tolerates_taos_runtime_import_errors(monkeypatch) -> None:
    module_name = "src.storage.database.database_manager.database_table_manager_methods.part1"
    original_import = builtins.__import__

    def guarded_import(name: str, globals_dict=None, locals_dict=None, fromlist=(), level: int = 0):
        if name == "taos":
            raise RuntimeError("libtaos.so missing")
        return original_import(name, globals_dict, locals_dict, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", guarded_import)
    sys.modules.pop("taos", None)
    sys.modules.pop(module_name, None)

    module = importlib.import_module(module_name)

    assert module.TAOS_AVAILABLE is False
    assert module.TAOS_MODULE_TYPE is None
