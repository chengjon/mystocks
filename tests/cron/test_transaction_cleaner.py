from datetime import datetime

from src.cron.transaction_cleaner import TransactionCleaner


def test_load_pending_transactions_queries_pg(mocker):
    fake_pg = mocker.Mock()
    fake_pg.execute_sql.return_value = mocker.Mock(empty=True)
    cleaner = TransactionCleaner(pg=fake_pg, td=mocker.Mock(), coordinator=mocker.Mock())

    cleaner._load_pending_transactions(limit=5, threshold=datetime(2025, 1, 1))

    fake_pg.execute_sql.assert_called_once()
