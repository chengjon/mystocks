from __future__ import annotations

import logging
import math
from datetime import datetime

import pandas as pd

from src.core.data_classification import DataClassification
from src.data_access._tdengine_validation import (
    validate_identifier,
    validate_symbol,
    validate_table_name,
    validate_suffix,
)

logger = logging.getLogger("TDengineDataAccess")
_MAX_INSERT_ROWS = 1_000_000



def _ensure_reasonable_batch_size(data: pd.DataFrame) -> None:
    if len(data) > _MAX_INSERT_ROWS:
        raise ValueError(
            f"DataFrame too large: {len(data)} rows. "
            f"Maximum allowed: {_MAX_INSERT_ROWS:,} rows. "
            "Please split the data into smaller chunks."
        )



def _format_timestamp(ts) -> str:
    timestamp = ts if hasattr(ts, "strftime") else datetime.now()
    return timestamp.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]



def _quoted_txn_id(raw_txn_id) -> str:
    if not raw_txn_id:
        return "NULL"
    txn_id_value = str(raw_txn_id).replace("'", "''")
    return f"'{txn_id_value}'"



def _insert_tick_data(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
    """插入 Tick 数据。"""
    try:
        _ensure_reasonable_batch_size(data)
        safe_table_name = validate_table_name(table_name)
        has_txn = "txn_id" in data.columns and "is_valid" in data.columns

        for row in data.itertuples():
            symbol = validate_symbol(str(getattr(row, "symbol", "unknown")))
            exchange = validate_identifier(str(getattr(row, "exchange", "sh")).lower(), "exchange")
            subtable = self._get_subtable_name(safe_table_name, symbol, exchange)
            ts_str = _format_timestamp(getattr(row, "ts", datetime.now()))

            price = float(getattr(row, "price", 0.0))
            volume = int(getattr(row, "volume", 0))
            amount = float(getattr(row, "amount", 0.0))
            txn_id = _quoted_txn_id(getattr(row, "txn_id", None)) if has_txn else "NULL"
            is_valid = str(getattr(row, "is_valid", True)).lower() if has_txn else "true"

            sql = f"""
                INSERT INTO {subtable} USING {safe_table_name}
                TAGS ('{symbol}', '{exchange}')
                VALUES ('{ts_str}', {price}, {volume}, {amount}, {txn_id}, {is_valid})
            """
            cursor.execute(sql)
        return True
    except Exception:
        logger.error("Tick 插入错误: %(e)s")
        return False



def _insert_minute_kline(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
    """插入分钟 K 线数据。"""
    try:
        _ensure_reasonable_batch_size(data)
        safe_table_name = validate_table_name(table_name)
        has_txn = "txn_id" in data.columns and "is_valid" in data.columns

        for row in data.itertuples():
            symbol = validate_symbol(str(getattr(row, "symbol", "unknown")))
            frequency = validate_suffix(str(getattr(row, "frequency", "1m")).lower(), "frequency")
            subtable = self._get_subtable_name(safe_table_name, symbol, frequency)
            ts_str = _format_timestamp(getattr(row, "ts", datetime.now()))

            open_p = float(getattr(row, "open", 0.0))
            high = float(getattr(row, "high", 0.0))
            low = float(getattr(row, "low", 0.0))
            close = float(getattr(row, "close", 0.0))
            volume = int(getattr(row, "volume", 0))
            amount = float(getattr(row, "amount", 0.0))
            txn_id = _quoted_txn_id(getattr(row, "txn_id", None)) if has_txn else "NULL"
            is_valid = str(getattr(row, "is_valid", True)).lower() if has_txn else "true"

            sql = f"""
                INSERT INTO {subtable} USING {safe_table_name}
                TAGS ('{symbol}', '{frequency}')
                VALUES ('{ts_str}', {open_p}, {high}, {low}, {close}, {volume}, {amount}, {txn_id}, {is_valid})
            """
            cursor.execute(sql)
        return True
    except Exception:
        logger.error("K线插入错误: %(e)s")
        return False



def _safe_float(value, default: float = 0.0) -> float:
    float_value = float(value or default)
    return float_value if not math.isnan(float_value) else default



def _safe_volume(value) -> int:
    if isinstance(value, (int, float)) and math.isnan(value):
        return 0
    return int(value or 0)



def _insert_realtime_quotes(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
    """插入实时行情数据。"""
    try:
        has_txn = "txn_id" in data.columns and "is_valid" in data.columns

        for _, row in data.iterrows():
            symbol = validate_symbol(str(row.get("symbol", "unknown")))
            subtable = f"rt_{symbol.lower().replace('.', '_')}"
            fetch_ts_str = _format_timestamp(row.get("fetch_timestamp", datetime.now()))

            name = str(row.get("name", ""))
            pct_chg = _safe_float(row.get("pct_chg"), 0.0)
            close_p = _safe_float(row.get("close"), 0.0)
            high = _safe_float(row.get("high"), 0.0)
            low = _safe_float(row.get("low"), 0.0)
            open_p = _safe_float(row.get("open"), 0.0)
            change = _safe_float(row.get("change"), 0.0)
            turnover = _safe_float(row.get("turnover_rate"), 0.0)
            volume = _safe_volume(row.get("volume", 0))
            amount = _safe_float(row.get("amount"), 0.0)
            total_mv = _safe_float(row.get("total_mv"), 0.0)
            circ_mv = _safe_float(row.get("circ_mv"), 0.0)
            data_source = str(row.get("data_source", ""))
            data_type = str(row.get("data_type", ""))
            market = str(row.get("market", ""))
            txn_id = _quoted_txn_id(row.get("txn_id")) if has_txn else "NULL"
            is_valid = str(row.get("is_valid", True)).lower() if has_txn else "true"

            sql = f"""
                INSERT INTO {subtable} USING {table_name}
                TAGS ('{symbol}', '{market}')
                VALUES ('{fetch_ts_str}', '{name}', {pct_chg}, {close_p}, {high}, {low}, {open_p}, {change}, {turnover}, {volume}, {amount}, {total_mv}, {circ_mv}, '{data_source}', '{data_type}', {txn_id}, {is_valid})
            """
            cursor.execute(sql)
        return True
    except Exception:
        logger.error("实时行情插入错误: %(e)s")
        return False



def _insert_generic_timeseries(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
    """通用时间序列插入。"""
    try:
        columns = ", ".join(data.columns)
        placeholders = ", ".join(["?"] * len(data.columns))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor.executemany(sql, data.values.tolist())
        return True
    except Exception:
        logger.error("通用插入错误: %(e)s")
        return False



def save_data(
    self,
    data: pd.DataFrame,
    classification: DataClassification,
    table_name: str | None = None,
    **kwargs,
) -> bool:
    """保存数据。"""
    if data is None or data.empty:
        return True

    actual_table_name = table_name or self._get_default_table_name(classification)

    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        cursor = conn.cursor()

        if classification == DataClassification.TICK_DATA:
            success = self._insert_tick_data(cursor, data, actual_table_name)
        elif classification == DataClassification.MINUTE_KLINE:
            success = self._insert_minute_kline(cursor, data, actual_table_name)
        elif classification == DataClassification.INDEX_QUOTES:
            success = self._insert_realtime_quotes(cursor, data, actual_table_name)
        else:
            success = self._insert_generic_timeseries(cursor, data, actual_table_name)

        return success
    except Exception:
        logger.error("TDengine 保存失败: %(e)s")
        return False



def invalidate_data_by_txn_id(self, table_name: str, txn_id: str) -> bool:
    """Saga 补偿：按事务 ID 失效数据。"""
    try:
        safe_table_name = validate_table_name(table_name)
        if not txn_id:
            raise ValueError("txn_id cannot be empty")

        conn = self.db_manager.get_connection(self.db_type, "market_data")
        select_sql = f"SELECT * FROM {safe_table_name} WHERE txn_id = ?"
        df = pd.read_sql(select_sql, conn, params=[txn_id])

        if df.empty:
            return True

        df["is_valid"] = False
        classification = DataClassification.MINUTE_KLINE if "kline" in safe_table_name else DataClassification.TICK_DATA
        return self.save_data(df, classification, table_name)
    except Exception:
        logger.error("补偿操作失败: %(e)s")
        return False
