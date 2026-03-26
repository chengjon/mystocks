from __future__ import annotations

import importlib.util
import sys
import tarfile
import types
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = PROJECT_ROOT / "src" / "infrastructure" / "backup_recovery" / "recovery_manager.py"


def _load_recovery_manager_module():
    postgresql_module = types.ModuleType("src.data_access.postgresql_access")
    postgresql_module.PostgreSQLDataAccess = type("PostgreSQLDataAccess", (), {})

    tdengine_module = types.ModuleType("src.data_access.tdengine_access")
    tdengine_module.TDengineDataAccess = type("TDengineDataAccess", (), {})

    connection_module = types.ModuleType("src.storage.database.connection_manager")
    connection_module.DatabaseConnectionManager = type("DatabaseConnectionManager", (), {})

    sys.modules["src.data_access.postgresql_access"] = postgresql_module
    sys.modules["src.data_access.tdengine_access"] = tdengine_module
    sys.modules["src.storage.database.connection_manager"] = connection_module

    spec = importlib.util.spec_from_file_location("recovery_manager_under_test", MODULE_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validated_tar_members_accepts_safe_relative_paths(tmp_path: Path) -> None:
    module = _load_recovery_manager_module()
    safe_member = tarfile.TarInfo("nested/data.parquet")

    safe_members = module._validated_tar_members([safe_member], tmp_path)

    assert safe_members == [safe_member]


def test_validated_tar_members_rejects_path_traversal_entries(tmp_path: Path) -> None:
    module = _load_recovery_manager_module()
    unsafe_member = tarfile.TarInfo("../escape.txt")

    with pytest.raises(ValueError, match="Unsafe path in tar file"):
        module._validated_tar_members([unsafe_member], tmp_path)
