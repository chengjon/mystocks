from __future__ import annotations

import asyncio
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


class FakeBackupManager:
    def __init__(self, backup_dir: Path):
        self.postgresql_backup_dir = backup_dir
        self.tdengine_backup_dir = backup_dir
        self._metadata = SimpleNamespace(
            backup_id="postgresql_full_20260517_120000",
            backup_type="full",
            database="postgresql",
            tables_backed_up=["orders"],
            total_rows=12,
            status="success",
        )

    def get_backup_list(self):
        return [self._metadata]


class FakeIntegrityChecker:
    def __init__(self):
        self.calls = []

    def verify_backup_integrity(self, backup_path, backup_metadata, expected_row_count=0):
        self.calls.append((backup_path, backup_metadata, expected_row_count))
        return True, {"tables_checked": 1, "errors": []}


def test_verify_backup_integrity_impl_uses_metadata_path_and_returns_result(tmp_path):
    from app.api.backup_recovery_secure._integrity_verification import verify_backup_integrity_impl

    backup_file = tmp_path / "postgresql_full_20260517_120000.sql.gz"
    backup_file.write_text("backup", encoding="utf-8")
    backup_manager = FakeBackupManager(tmp_path)
    integrity_checker = FakeIntegrityChecker()
    user = SimpleNamespace(id="u-1", username="ops", role="admin")

    response = asyncio.run(
        verify_backup_integrity_impl(
            "postgresql_full_20260517_120000",
            user,
            backup_manager,
            integrity_checker,
        )
    )

    assert response.success is True
    assert response.data["valid"] is True
    assert response.data["backup_id"] == "postgresql_full_20260517_120000"
    assert integrity_checker.calls == [(str(backup_file), backup_manager._metadata.__dict__, 12)]
