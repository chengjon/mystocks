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
