import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock

from scripts.maintenance.saga_smoke_test import run_smoke


def test_run_smoke_success_cleans_up_transaction_log():
    coordinator = MagicMock()
    coordinator.execute_kline_sync.return_value = True

    pg = MagicMock()

    result = run_smoke(
        coordinator=coordinator,
        pg=pg,
        mode="success",
        table_name="minute_kline",
        symbol="SAGA001",
        frequency="1m",
        cleanup=True,
    )

    assert result["success"]["result"] is True
    assert result["success"]["business_id"].startswith("SAGA_SMOKE_success_")
    assert pg.execute_sql.called


def test_run_smoke_failure_cleans_up_transaction_log():
    coordinator = MagicMock()
    coordinator.execute_kline_sync.return_value = False

    pg = MagicMock()

    result = run_smoke(
        coordinator=coordinator,
        pg=pg,
        mode="fail",
        table_name="minute_kline",
        symbol="SAGA001",
        frequency="1m",
        cleanup=True,
    )

    assert result["fail"]["result"] is False
    assert result["fail"]["business_id"].startswith("SAGA_SMOKE_fail_")
    assert pg.execute_sql.called


def test_cli_direct_execution_works():
    repo_root = Path(__file__).resolve().parents[2]
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    result = subprocess.run(
        [sys.executable, "scripts/maintenance/saga_smoke_test.py", "--help"],
        cwd=repo_root,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "Saga smoke test utility" in result.stdout
