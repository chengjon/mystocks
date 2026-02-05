#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Saga smoke test utility.

Runs success/failure Saga flows and cleans up transaction_log records.
"""

from __future__ import annotations

import argparse
import time
from datetime import datetime
from typing import Dict, Optional

import pandas as pd

from src.core.data_classification import DataClassification
from src.core.transaction.saga_coordinator import SagaCoordinator
from src.data_access.postgresql_access import PostgreSQLDataAccess
from src.data_access.tdengine_access import TDengineDataAccess


def _make_kline_data(symbol: str, frequency: str) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "ts": [datetime.utcnow()],
            "open": [10.0],
            "high": [10.5],
            "low": [9.8],
            "close": [10.2],
            "volume": [1000],
            "amount": [10200.0],
            "symbol": [symbol],
            "frequency": [frequency],
        }
    )


def _cleanup_transaction_log(pg: PostgreSQLDataAccess, business_id: str) -> None:
    sql = "DELETE FROM transaction_log WHERE business_id = %s"
    pg.execute_sql(sql, (business_id,))


def run_smoke(
    coordinator: Optional[SagaCoordinator] = None,
    pg: Optional[PostgreSQLDataAccess] = None,
    *,
    mode: str = "both",
    table_name: str = "minute_kline",
    symbol: str = "SAGA001",
    frequency: str = "1m",
    cleanup: bool = True,
) -> Dict[str, Dict[str, object]]:
    if pg is None:
        pg = PostgreSQLDataAccess()
    if coordinator is None:
        coordinator = SagaCoordinator(pg, TDengineDataAccess())

    results: Dict[str, Dict[str, object]] = {}

    if mode in ("success", "both"):
        business_id = f"SAGA_SMOKE_success_{int(time.time())}"
        data = _make_kline_data(symbol, frequency)
        result = coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=data,
            classification=DataClassification.MINUTE_KLINE,
            table_name=table_name,
            metadata_update_func=lambda _session: None,
        )
        results["success"] = {"business_id": business_id, "result": result}
        if cleanup:
            _cleanup_transaction_log(pg, business_id)

    if mode in ("fail", "both"):
        business_id = f"SAGA_SMOKE_fail_{int(time.time())}"
        data = _make_kline_data(symbol, frequency)

        def fail_metadata(_session):
            raise RuntimeError("Simulated metadata failure for Saga smoke test")

        result = coordinator.execute_kline_sync(
            business_id=business_id,
            kline_data=data,
            classification=DataClassification.MINUTE_KLINE,
            table_name=table_name,
            metadata_update_func=fail_metadata,
        )
        results["fail"] = {"business_id": business_id, "result": result}
        if cleanup:
            _cleanup_transaction_log(pg, business_id)

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Saga smoke test utility")
    parser.add_argument("--mode", choices=["success", "fail", "both"], default="both")
    parser.add_argument("--table-name", default="minute_kline")
    parser.add_argument("--symbol", default="SAGA001")
    parser.add_argument("--frequency", default="1m")
    parser.add_argument("--no-cleanup", action="store_true", help="Keep transaction_log entries")
    args = parser.parse_args()

    results = run_smoke(
        mode=args.mode,
        table_name=args.table_name,
        symbol=args.symbol,
        frequency=args.frequency,
        cleanup=not args.no_cleanup,
    )

    for key, value in results.items():
        print(f"{key.upper()} business_id={value['business_id']} result={value['result']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
