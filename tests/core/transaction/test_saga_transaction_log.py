from datetime import datetime
from unittest.mock import MagicMock

import pandas as pd

from src.core import DataClassification
from src.core.transaction.saga_coordinator import SagaCoordinator


def test_saga_logs_transaction_with_duration_on_success():
    pg = MagicMock()
    td = MagicMock()
    td.save_data.return_value = True

    coordinator = SagaCoordinator(pg, td)

    kline_data = pd.DataFrame(
        {
            "ts": [datetime(2026, 1, 3, 9, 30)],
            "open": [10.0],
            "high": [10.5],
            "low": [9.8],
            "close": [10.2],
            "volume": [1000],
            "amount": [10200.0],
            "symbol": ["TEST001"],
            "frequency": ["1m"],
        }
    )

    result = coordinator.execute_kline_sync(
        business_id="TEST001.SH_DAILY",
        kline_data=kline_data,
        classification=DataClassification.MINUTE_KLINE,
        table_name="market_data.minute_kline",
        metadata_update_func=lambda _session: None,
    )

    assert result is True

    txn_calls = [
        call
        for call in pg.execute_sql.call_args_list
        if call.args and "transaction_log" in call.args[0]
    ]
    assert txn_calls, "Expected transaction_log writes for Saga success"

    committed_found = False
    for call in txn_calls:
        if "COMMITTED" in call.args[0]:
            committed_found = True
            break
        params = None
        if len(call.args) > 1:
            params = call.args[1]
        elif "params" in call.kwargs:
            params = call.kwargs["params"]
        if params and "COMMITTED" in params:
            committed_found = True
            break

    assert committed_found, "Expected COMMITTED status update in transaction_log"

    duration_values = []
    for call in txn_calls:
        params = None
        if len(call.args) > 1:
            params = call.args[1]
        elif "params" in call.kwargs:
            params = call.kwargs["params"]
        if params:
            duration_values.extend([p for p in params if isinstance(p, (int, float))])

    assert any(v > 0 for v in duration_values), "Expected positive duration_ms in transaction_log"
