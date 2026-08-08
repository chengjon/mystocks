"""
TDengine 数据访问层 (统一重构版)

封装 TDengine 的所有数据操作，支持超级表插入、自动去重、以及基于数据列的 Saga 事务。
专门处理高频时序数据 (Tick/分钟线/盘口快照) 的存储和查询。

版本: 2.0.2 (Fix for taospy placeholder bug)
修改日期: 2026-01-03
"""

from __future__ import annotations

import logging


from src.data_access._tdengine_query_operations import (
    _get_connection,
    _get_default_table_name,
    aggregate_to_kline,
    check_connection,
    close,
    connect,
    create_stable,
    create_table,
    delete_by_time_range,
    execute_sql,
    execute_update,
    get_table_info,
    load_data,
    query_all,
    query_by_time_range,
    query_count,
    query_latest,
    query_sql,
    insert_dataframe,
)
from src.data_access._tdengine_validation import (
    _get_subtable_name,
    validate_identifier,
    validate_suffix,
    validate_symbol,
    validate_table_name,
)
from src.data_access._tdengine_write_operations import (
    _insert_generic_timeseries,
    _insert_minute_kline,
    _insert_realtime_quotes,
    _insert_tick_data,
    invalidate_data_by_txn_id,
    save_data,
)
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

logger = logging.getLogger("TDengineDataAccess")


class TDengineDataAccess:
    """TDengine 数据访问类。"""

    def __init__(self, db_manager=None, monitoring_db=None):
        self.db_manager = db_manager or DatabaseTableManager()
        self.monitoring_db = monitoring_db
        self.db_type = DatabaseType.TDENGINE
        self._connection = None

    _get_subtable_name = _get_subtable_name
    save_data = save_data
    _insert_tick_data = _insert_tick_data
    _insert_minute_kline = _insert_minute_kline
    _insert_realtime_quotes = _insert_realtime_quotes
    _insert_generic_timeseries = _insert_generic_timeseries
    invalidate_data_by_txn_id = invalidate_data_by_txn_id
    load_data = load_data
    _get_default_table_name = _get_default_table_name
    _get_connection = _get_connection
    execute_sql = execute_sql
    query_sql = query_sql
    execute_update = execute_update
    close = close
    check_connection = check_connection
    connect = connect
    query_all = query_all
    query_count = query_count
    create_stable = create_stable
    create_table = create_table
    insert_dataframe = insert_dataframe
    query_by_time_range = query_by_time_range
    query_latest = query_latest
    delete_by_time_range = delete_by_time_range
    aggregate_to_kline = aggregate_to_kline
    get_table_info = get_table_info


__all__ = [
    "TDengineDataAccess",
    "validate_identifier",
    "validate_suffix",
    "validate_table_name",
    "validate_symbol",
]
