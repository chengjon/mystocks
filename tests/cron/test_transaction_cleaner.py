from datetime import datetime

import pandas as pd

from src.core.transaction.saga_coordinator import TransactionStatus
from src.cron.transaction_cleaner import TransactionCleaner


def test_load_pending_transactions_queries_pg(mocker):
    fake_pg = mocker.Mock()
    fake_pg.execute_sql.return_value = mocker.Mock(empty=True)
    cleaner = TransactionCleaner(pg=fake_pg, td=mocker.Mock(), coordinator=mocker.Mock())

    cleaner._load_pending_transactions(limit=5, threshold=datetime(2025, 1, 1))

    fake_pg.execute_sql.assert_called_once()


def test_process_zombie_commits_when_td_and_pg_success(mocker):
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=mocker.Mock())
    cleaner.update_txn_status = mocker.Mock()

    cleaner.process_zombie(
        {
            "transaction_id": "t1",
            "business_id": "kline_1",
            "td_status": "SUCCESS",
            "pg_status": "SUCCESS",
        }
    )

    cleaner.update_txn_status.assert_called_once_with("t1", TransactionStatus.COMMITTED.value)


def test_process_zombie_rolls_back_and_compensates(mocker):
    coordinator = mocker.Mock()
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=coordinator)
    cleaner.update_txn_status = mocker.Mock()

    cleaner.process_zombie(
        {
            "transaction_id": "t2",
            "business_id": "kline_1",
            "td_status": "SUCCESS",
            "pg_status": "FAIL",
        }
    )

    coordinator._compensate_tdengine.assert_called_once()
    cleaner.update_txn_status.assert_called_once_with("t2", TransactionStatus.ROLLED_BACK.value)


def test_dry_run_skips_updates(mocker):
    pg = mocker.Mock()
    cleaner = TransactionCleaner(pg=pg, td=mocker.Mock(), coordinator=mocker.Mock(), dry_run=True)

    cleaner.update_txn_status("t1", TransactionStatus.COMMITTED.value)

    pg.execute_update.assert_not_called()


def test_cleanup_invalid_data_executes_delete(mocker):
    td = mocker.Mock()
    td.query_sql.return_value = pd.DataFrame([[3]])
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=td, coordinator=mocker.Mock(), dry_run=False)

    cleaner.cleanup_invalid_data()

    assert td.execute_update.called


def test_dry_run_skips_compensation(mocker):
    coordinator = mocker.Mock()
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=coordinator, dry_run=True)

    cleaner.process_zombie(
        {
            "transaction_id": "t3",
            "business_id": "kline_1",
            "td_status": "SUCCESS",
            "pg_status": "FAIL",
        }
    )

    coordinator._compensate_tdengine.assert_not_called()


def test_env_defaults_loaded(mocker):
    mocker.patch.dict("os.environ", {"TXN_ZOMBIE_MINUTES": "7", "TXN_ZOMBIE_BATCH_LIMIT": "12"})
    cleaner = TransactionCleaner(pg=mocker.Mock(), td=mocker.Mock(), coordinator=mocker.Mock())

    assert cleaner.zombie_minutes == 7
    assert cleaner.zombie_limit == 12
