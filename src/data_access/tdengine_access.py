"""
TDengine 数据访问层 (统一重构版)

封装 TDengine 的所有数据操作，支持超级表插入、自动去重、以及基于数据列的 Saga 事务。
专门处理高频时序数据 (Tick/分钟线/盘口快照) 的存储和查询。

版本: 2.0.2 (Fix for taospy placeholder bug)
修改日期: 2026-01-03
"""

import pandas as pd
import logging
from datetime import datetime
from typing import Optional

# 导入核心定义
from src.core.data_classification import DataClassification
from src.storage.database.database_manager import DatabaseTableManager, DatabaseType

logger = logging.getLogger("TDengineDataAccess")


class TDengineDataAccess:
    """
    TDengine 数据访问类
    """

    def __init__(self, db_manager=None, monitoring_db=None):
        """
        初始化 TDengine 访问层
        """
        self.db_manager = db_manager or DatabaseTableManager()
        self.monitoring_db = monitoring_db
        self.db_type = DatabaseType.TDENGINE

    def _get_subtable_name(self, super_table: str, symbol: str, suffix: str = "") -> str:
        """生成子表名"""
        # 简单清洗 symbol
        clean_symbol = symbol.lower().replace(".", "_").replace("-", "_")
        prefix = "k" if "kline" in super_table else "t"

        if suffix:
            return f"{prefix}_{clean_symbol}_{suffix.lower()}"
        return f"{prefix}_{clean_symbol}"

    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """保存数据"""
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

        except Exception as e:
            logger.error(f"TDengine 保存失败: {e}")
            return False

    def _insert_tick_data(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
        """插入 Tick 数据 (使用直接 SQL 避免 taospy 占位符 Bug)"""
        try:
            has_txn = "txn_id" in data.columns and "is_valid" in data.columns

            for _, row in data.iterrows():
                symbol = str(row.get("symbol", "unknown"))
                exchange = str(row.get("exchange", "sh")).lower()
                subtable = self._get_subtable_name(table_name, symbol, exchange)

                ts = row.get("ts", datetime.now())
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                price = float(row.get("price", 0.0))
                volume = int(row.get("volume", 0))
                amount = float(row.get("amount", 0.0))
                txn_id = f"'{row.get('txn_id')}'" if has_txn and row.get("txn_id") else "NULL"
                is_valid = str(row.get("is_valid", True)).lower() if has_txn else "true"

                sql = f"""
                    INSERT INTO {subtable} USING {table_name}
                    TAGS ('{symbol}', '{exchange}')
                    VALUES ('{ts_str}', {price}, {volume}, {amount}, {txn_id}, {is_valid})
                """
                cursor.execute(sql)
            return True
        except Exception as e:
            logger.error(f"Tick 插入错误: {e}")
            return False

    def _insert_minute_kline(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
        """插入分钟 K 线数据 (使用直接 SQL)"""
        try:
            has_txn = "txn_id" in data.columns and "is_valid" in data.columns

            for _, row in data.iterrows():
                symbol = str(row.get("symbol", "unknown"))
                frequency = str(row.get("frequency", "1m")).lower()
                subtable = self._get_subtable_name(table_name, symbol, frequency)

                ts = row.get("ts", datetime.now())
                ts_str = ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

                open_p = float(row.get("open", 0.0))
                high = float(row.get("high", 0.0))
                low = float(row.get("low", 0.0))
                close = float(row.get("close", 0.0))
                volume = int(row.get("volume", 0))
                amount = float(row.get("amount", 0.0))
                txn_id = f"'{row.get('txn_id')}'" if has_txn and row.get("txn_id") else "NULL"
                is_valid = str(row.get("is_valid", True)).lower() if has_txn else "true"

                # 按照 STABLE 定义: ts, open, high, low, close, volume, amount, txn_id, is_valid
                sql = f"""
                    INSERT INTO {subtable} USING {table_name}
                    TAGS ('{symbol}', '{frequency}')
                    VALUES ('{ts_str}', {open_p}, {high}, {low}, {close}, {volume}, {amount}, {txn_id}, {is_valid})
                """
                cursor.execute(sql)
            return True
        except Exception as e:
            logger.error(f"K线插入错误: {e}")
            return False

    def _insert_realtime_quotes(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
        """插入实时行情数据 (超级表语法)"""
        try:
            has_txn = "txn_id" in data.columns and "is_valid" in data.columns

            for _, row in data.iterrows():
                symbol = str(row.get("symbol", "unknown"))
                # 生成子表名: rt_<code>
                subtable = f"rt_{symbol.lower().replace('.', '_')}"

                # 确保 ts 存在，如果数据中没有，使用当前时间
                ts = row.get("ts", datetime.now())
                if hasattr(ts, "strftime"):
                    ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                else:
                    str(ts)

                # 准备字段（处理 NaN 值）
                import math

                name = str(row.get("name", ""))

                # 辅助函数：安全转换 float，处理 NaN
                def safe_float(val, default=0.0):
                    fval = float(val or default)
                    return fval if not math.isnan(fval) else default

                pct_chg = safe_float(row.get("pct_chg"), 0.0)
                close_p = safe_float(row.get("close"), 0.0)
                high = safe_float(row.get("high"), 0.0)
                low = safe_float(row.get("low"), 0.0)
                open_p = safe_float(row.get("open"), 0.0)
                change = safe_float(row.get("change"), 0.0)
                turnover = safe_float(row.get("turnover_rate"), 0.0)

                # 处理 volume 的 NaN 值（BIGINT 不能接受 NaN）
                vol_val = row.get("volume", 0)
                if isinstance(vol_val, (int, float)) and math.isnan(vol_val):
                    volume = 0
                else:
                    volume = int(vol_val or 0)

                amount = safe_float(row.get("amount"), 0.0)
                total_mv = safe_float(row.get("total_mv"), 0.0)
                circ_mv = safe_float(row.get("circ_mv"), 0.0)

                fetch_ts = row.get("fetch_timestamp", datetime.now())
                if hasattr(fetch_ts, "strftime"):
                    fetch_ts_str = fetch_ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
                else:
                    fetch_ts_str = str(fetch_ts)

                data_source = str(row.get("data_source", ""))
                data_type = str(row.get("data_type", ""))
                market = str(row.get("market", ""))

                txn_id = f"'{row.get('txn_id')}'" if has_txn and row.get("txn_id") else "NULL"
                is_valid = str(row.get("is_valid", True)).lower() if has_txn else "true"

                # 按照 CREATE STABLE 定义的列顺序:
                # fetch_timestamp, name, pct_chg, close, high, low, open, change, turnover_rate, volume, amount, total_mv, circ_mv, data_source, data_type, txn_id, is_valid
                # TAGS: (symbol, market)
                sql = f"""
                    INSERT INTO {subtable} USING {table_name}
                    TAGS ('{symbol}', '{market}')
                    VALUES ('{fetch_ts_str}', '{name}', {pct_chg}, {close_p}, {high}, {low}, {open_p}, {change}, {turnover}, {volume}, {amount}, {total_mv}, {circ_mv}, '{data_source}', '{data_type}', {txn_id}, {is_valid})
                """
                cursor.execute(sql)
            return True
        except Exception as e:
            logger.error(f"实时行情插入错误: {e}")
            return False

    def _insert_generic_timeseries(self, cursor, data: pd.DataFrame, table_name: str) -> bool:
        """通用插入"""
        try:
            # 对于通用插入，我们仍尝试 executemany，如果失败再退化
            columns = ", ".join(data.columns)
            placeholders = ", ".join(["?"] * len(data.columns))
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.executemany(sql, data.values.tolist())
            return True
        except Exception as e:
            logger.error(f"通用插入错误: {e}")
            return False

    def invalidate_data_by_txn_id(self, table_name: str, txn_id: str) -> bool:
        """Saga 补偿操作: 标记数据为无效"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")
            select_sql = f"SELECT * FROM {table_name} WHERE txn_id = '{txn_id}'"
            df = pd.read_sql(select_sql, conn)

            if df.empty:
                return True

            df["is_valid"] = False
            classification = DataClassification.MINUTE_KLINE if "kline" in table_name else DataClassification.TICK_DATA
            return self.save_data(df, classification, table_name)
        except Exception as e:
            logger.error(f"补偿操作失败: {e}")
            return False

    def load_data(self, table_name: str, **filters) -> Optional[pd.DataFrame]:
        """加载数据"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")
            sql = f"SELECT * FROM {table_name}"
            conditions = []
            if "start_time" in filters:
                conditions.append(f"ts >= '{filters['start_time']}'")
            if "end_time" in filters:
                conditions.append(f"ts <= '{filters['end_time']}'")
            if "symbol" in filters:
                conditions.append(f"symbol = '{filters['symbol']}'")
            if filters.get("include_invalid") is not True:
                conditions.append("is_valid = true")
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)
            sql += " ORDER BY ts DESC"
            if "limit" in filters:
                sql += f" LIMIT {filters['limit']}"
            else:
                sql += " LIMIT 1000"
            return pd.read_sql(sql, conn)
        except Exception as e:
            logger.error(f"加载数据失败: {e}")
            return None

    def _get_default_table_name(self, classification: DataClassification) -> str:
        """获取默认表名"""
        mapping = {
            DataClassification.MINUTE_KLINE: "market_data.minute_kline",
            DataClassification.TICK_DATA: "market_data.tick_data",
            DataClassification.INDEX_QUOTES: "market_data.realtime_market_quotes",
        }
        return mapping.get(classification, "market_data.generic_data")

    def query_sql(self, sql: str) -> pd.DataFrame:
        """执行原生 SQL 查询并返回 DataFrame"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")
            return pd.read_sql(sql, conn)
        except Exception as e:
            logger.error(f"TDengine SQL 查询失败: {e}")
            return pd.DataFrame()

    def execute_update(self, sql: str) -> bool:
        """执行原生 SQL 更新/删除操作"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")
            cursor = conn.cursor()
            cursor.execute(sql)
            return True
        except Exception as e:
            logger.error(f"TDengine SQL 执行失败: {e}")
            return False

    def close(self):
        """关闭连接"""
        pass
