from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

import pandas as pd

from src.core.data_classification import DataClassification
from src.data_access._tdengine_validation import validate_symbol, validate_table_name

logger = logging.getLogger("TDengineDataAccess")



def load_data(self, table_name: str, **filters) -> Optional[pd.DataFrame]:
    """加载数据。"""
    try:
        safe_table_name = validate_table_name(table_name)
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        sql = f"SELECT * FROM {safe_table_name}"
        params = []
        conditions = []

        if "start_time" in filters:
            conditions.append("ts >= ?")
            params.append(filters["start_time"])
        if "end_time" in filters:
            conditions.append("ts <= ?")
            params.append(filters["end_time"])
        if "symbol" in filters:
            safe_symbol = validate_symbol(filters["symbol"])
            conditions.append(f"symbol = '{safe_symbol}'")
        if filters.get("include_invalid") is not True:
            conditions.append("is_valid = true")
        if conditions:
            sql += " WHERE " + " AND ".join(conditions)
        sql += " ORDER BY ts DESC"
        sql += f" LIMIT {filters['limit']}" if "limit" in filters else " LIMIT 1000"
        return pd.read_sql(sql, conn)
    except Exception:
        logger.error("加载数据失败: %(e)s")
        return None



def _get_default_table_name(self, classification: DataClassification) -> str:
    """获取默认表名。"""
    mapping = {
        DataClassification.MINUTE_KLINE: "market_data.minute_kline",
        DataClassification.TICK_DATA: "market_data.tick_data",
        DataClassification.INDEX_QUOTES: "market_data.realtime_market_quotes",
    }
    return mapping.get(classification, "market_data.generic_data")



def _get_connection(self):
    """获取 TDengine 连接。"""
    if hasattr(self.db_manager, "get_tdx_connection"):
        return self.db_manager.get_tdx_connection()
    return self.db_manager.get_connection(self.db_type, "market_data")



def execute_sql(self, sql: str, **kwargs) -> Any:
    """执行 SQL 并返回结果。"""
    try:
        if self._connection is None:
            self._connection = self._get_connection()

        cursor = self._connection.cursor()
        sql_prefix = sql.strip().upper()
        if sql_prefix.startswith(("SELECT", "SHOW", "DESCRIBE")):
            cursor.execute(sql)
            return cursor.fetchall()
        return cursor.execute(sql, **kwargs)
    except Exception:
        logger.error("执行SQL失败: %(e)s")
        return None



def query_sql(self, sql: str) -> pd.DataFrame:
    """执行原生 SQL 查询。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        return pd.read_sql(sql, conn)
    except Exception:
        logger.error("TDengine SQL 查询失败: %(e)s")
        return pd.DataFrame()



def execute_update(self, sql: str) -> bool:
    """执行原生更新 SQL。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        cursor = conn.cursor()
        cursor.execute(sql)
        return True
    except Exception:
        logger.error("TDengine SQL 执行失败: %(e)s")
        return False



def close(self):
    """关闭连接。"""
    if self.db_manager:
        self.db_manager.close_all_connections()



def check_connection(self) -> bool:
    """检查连接状态。"""
    try:
        if self._connection is None:
            self._connection = self._get_connection()
        self._connection.execute_sql("SELECT 1")
        return True
    except Exception:
        logger.error("TDengine连接检查失败: %(e)s")
        return False



def connect(self):
    """建立连接。"""
    try:
        self._connection = self._get_connection()
        return True
    except Exception:
        logger.error("TDengine连接失败: %(e)s")
        return False



def query_all(self, table_name: str, limit: int = 1000) -> pd.DataFrame:
    """查询表中的所有数据。"""
    try:
        sql = f"SELECT * FROM {table_name} LIMIT {limit}"
        return self.query_sql(sql)
    except Exception:
        logger.error("TDengine查询所有数据失败: %(e)s")
        return pd.DataFrame()



def query_count(self, table_name: str) -> int:
    """查询表中的记录数。"""
    try:
        sql = f"SELECT COUNT(*) as count FROM {table_name}"
        result = self.query_sql(sql)
        if not result.empty:
            return int(result.iloc[0, 0])
        return 0
    except Exception:
        logger.error("TDengine查询记录数失败: %(e)s")
        return 0



def create_stable(self, stable_name: str, schema: dict, tags: Optional[dict] = None) -> bool:
    """创建超表。"""
    try:
        tag_cols = ", ".join(f"'{key}' {value}" for key, value in (tags or {}).items())
        columns = ", ".join(f"{key} {value}" for key, value in schema.items())
        sql = f"""
            CREATE STABLE IF NOT EXISTS {stable_name} ({columns})
            TAGS ({tag_cols})
        """
        return self.execute_sql(sql) is not None
    except Exception:
        logger.error("创建超表失败: %(e)s")
        return False



def create_table(self, table_name: str, stable_name: str, tag_values: Optional[dict] = None) -> bool:
    """创建子表。"""
    try:
        if tag_values:
            tag_cols = ", ".join(f"'{key}' = '{value}'" for key, value in tag_values.items())
            tag_clause = f"TAGS ({tag_cols})"
        else:
            tag_clause = ""

        sql = f"""
            CREATE TABLE IF NOT EXISTS {table_name}
            USING {stable_name}
            {tag_clause}
        """
        return self.execute_sql(sql) is not None
    except Exception:
        logger.error("创建表失败: %(e)s")
        return False



def insert_dataframe(self, table_name: str, data: pd.DataFrame, timestamp_col: str = "ts") -> bool:
    """插入 DataFrame 到 TDengine 表。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        columns = ", ".join(data.columns)
        placeholders = ", ".join(["%s"] * len(data.columns))
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        cursor = conn.cursor()
        cursor.executemany(sql, data.values.tolist())
        conn.close()
        return True
    except Exception:
        logger.error("插入DataFrame失败: %(e)s")
        return False



def query_by_time_range(
    self,
    table_name: str,
    start_time: datetime,
    end_time: datetime,
    limit: int = 1000,
) -> Optional[pd.DataFrame]:
    """按时间范围查询数据。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        sql = f"""
            SELECT * FROM {table_name}
            WHERE ts >= '{start_time}' AND ts <= '{end_time}'
            ORDER BY ts DESC
            LIMIT {limit}
        """
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception:
        logger.error("时间范围查询失败: %(e)s")
        return None



def query_latest(self, table_name: str, symbol: Optional[str] = None, limit: int = 1) -> Optional[pd.DataFrame]:
    """查询最新数据。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        sql = f"SELECT * FROM {table_name}"
        if symbol:
            safe_symbol = validate_symbol(symbol)
            sql += f" WHERE symbol = '{safe_symbol}'"
        sql += f" ORDER BY ts DESC LIMIT {limit}"
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception:
        logger.error("查询最新数据失败: %(e)s")
        return None



def delete_by_time_range(self, table_name: str, start_time: datetime, end_time: datetime) -> bool:
    """按时间范围删除数据。"""
    try:
        sql = f"""
            DELETE FROM {table_name}
            WHERE ts >= '{start_time}' AND ts <= '{end_time}'
        """
        return self.execute_sql(sql) is not None
    except Exception:
        logger.error("删除数据失败: %(e)s")
        return False



def aggregate_to_kline(
    self,
    table_name: str,
    frequency: str = "1m",
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
) -> Optional[pd.DataFrame]:
    """聚合数据到 K 线。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1h", "1d": "1d"}
        interval = interval_map.get(frequency, "1m")
        sql = f"""
            SELECT
                _wstart as ts,
                first(close) as open,
                max(high) as high,
                min(low) as low,
                last(close) as close,
                sum(volume) as volume
            FROM {table_name}
            WHERE ts >= '{start_time or "1970-01-01"}' AND ts <= '{end_time or "now()"}'
            INTERVAL({interval}) SLIDING(1) FILL(NULL)
            GROUP BY symbol
        """
        df = pd.read_sql(sql, conn)
        conn.close()
        return df
    except Exception:
        logger.error("聚合到K线失败: %(e)s")
        return None



def get_table_info(self, table_name: str) -> dict:
    """获取表信息。"""
    try:
        conn = self.db_manager.get_connection(self.db_type, "market_data")
        cursor = conn.cursor()
        cursor.execute(f"DESCRIBE {table_name}")
        columns_info = cursor.fetchall()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        row_count = cursor.fetchone()[0]
        conn.close()
        return {
            "table_name": table_name,
            "columns": [{"name": col[0], "type": col[1]} for col in columns_info],
            "row_count": row_count,
        }
    except Exception:
        logger.error("获取表信息失败: %(e)s")
        return {"table_name": table_name, "columns": [], "row_count": 0}
