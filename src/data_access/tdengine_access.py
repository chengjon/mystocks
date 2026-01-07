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
        self._connection = None

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

    def _get_connection(self):
        """获取TDengine连接（兼容测试）"""
        # 兼容测试：优先使用get_tdx_connection
        if hasattr(self.db_manager, "get_tdx_connection"):
            return self.db_manager.get_tdx_connection()
        return self.db_manager.get_connection(self.db_type, "market_data")

    def execute_sql(self, sql: str, **kwargs) -> any:
        """执行SQL并返回结果（兼容测试）"""
        try:
            if self._connection is None:
                self._connection = self._get_connection()

            cursor = self._connection.cursor()

            if sql.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
                cursor.execute(sql)
                result = cursor.fetchall()
            elif sql.strip().upper().startswith(("INSERT", "CREATE", "DELETE", "UPDATE", "ALTER")):
                result = cursor.execute(sql, **kwargs)
            else:
                result = cursor.execute(sql, **kwargs)

            return result
        except Exception as e:
            logger.error(f"执行SQL失败: {e}")
            return None

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
        if self.db_manager:
            self.db_manager.close_all_connections()

    def check_connection(self) -> bool:
        """检查连接状态"""
        try:
            # 使用execute_sql而不是直接查询
            if self._connection is None:
                self._connection = self._get_connection()

            self._connection.execute_sql("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"TDengine连接检查失败: {e}")
            return False

    def create_stable(
        self,
        stable_name: str,
        schema: dict,
        tags: dict = None,
    ) -> bool:
        """创建超表"""
        try:
            # 构建TAGS子句
            tag_cols = ", ".join(f"'{k}' {v}" for k, v in (tags or {}).items())

            # 构建列定义
            columns = ", ".join(f"{k} {v}" for k, v in schema.items())

            sql = f"""
                CREATE STABLE IF NOT EXISTS {stable_name} ({columns})
                TAGS ({tag_cols})
            """
            result = self.execute_sql(sql)
            return result is not None
        except Exception as e:
            logger.error(f"创建超表失败: {e}")
            return False

    def create_table(
        self,
        table_name: str,
        stable_name: str,
        tag_values: dict = None,
    ) -> bool:
        """创建子表"""
        try:
            # 构建TAGS值子句
            if tag_values:
                tag_cols = ", ".join(f"'{k}' = '{v}'" for k, v in tag_values.items())
                tag_clause = f"TAGS ({tag_cols})"
            else:
                tag_clause = ""

            sql = f"""
                CREATE TABLE IF NOT EXISTS {table_name}
                USING {stable_name}
                {tag_clause}
            """
            result = self.execute_sql(sql)
            return result is not None
        except Exception as e:
            logger.error(f"创建表失败: {e}")
            return False

    def insert_dataframe(
        self,
        table_name: str,
        data: pd.DataFrame,
        timestamp_col: str = "ts",
    ) -> bool:
        """插入DataFrame到TDengine表"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")

            # 使用executemany插入数据
            columns = ", ".join(data.columns)
            placeholders = ", ".join(["%s"] * len(data.columns))

            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor = conn.cursor()
            cursor.executemany(sql, data.values.tolist())
            conn.close()
            return True
        except Exception as e:
            logger.error(f"插入DataFrame失败: {e}")
            return False

    def query_by_time_range(
        self,
        table_name: str,
        start_time: datetime,
        end_time: datetime,
        limit: int = 1000,
    ) -> Optional[pd.DataFrame]:
        """按时间范围查询数据"""
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
        except Exception as e:
            logger.error(f"时间范围查询失败: {e}")
            return None

    def query_latest(
        self,
        table_name: str,
        symbol: str = None,
        limit: int = 1,
    ) -> Optional[pd.DataFrame]:
        """查询最新数据"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")
            sql = f"SELECT * FROM {table_name}"
            if symbol:
                sql += f" WHERE symbol = '{symbol}'"
            sql += f" ORDER BY ts DESC LIMIT {limit}"
            df = pd.read_sql(sql, conn)
            conn.close()
            return df
        except Exception as e:
            logger.error(f"查询最新数据失败: {e}")
            return None

    def delete_by_time_range(
        self,
        table_name: str,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        """按时间范围删除数据"""
        try:
            sql = f"""
                DELETE FROM {table_name}
                WHERE ts >= '{start_time}' AND ts <= '{end_time}'
            """
            result = self.execute_sql(sql)
            return result is not None
        except Exception as e:
            logger.error(f"删除数据失败: {e}")
            return False

    def aggregate_to_kline(
        self,
        table_name: str,
        frequency: str = "1m",
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> Optional[pd.DataFrame]:
        """聚合数据到K线"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")

            # TDengine的聚合函数
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
        except Exception as e:
            logger.error(f"聚合到K线失败: {e}")
            return None

    def get_table_info(self, table_name: str) -> dict:
        """获取表信息"""
        try:
            conn = self.db_manager.get_connection(self.db_type, "market_data")
            cursor = conn.cursor()

            # 查询表结构
            sql = f"DESCRIBE {table_name}"
            cursor.execute(sql)
            columns_info = cursor.fetchall()

            # 查询表行数
            count_sql = f"SELECT COUNT(*) FROM {table_name}"
            cursor.execute(count_sql)
            row_count = cursor.fetchone()[0]

            conn.close()

            return {
                "table_name": table_name,
                "columns": [{"name": col[0], "type": col[1]} for col in columns_info],
                "row_count": row_count,
            }
        except Exception as e:
            logger.error(f"获取表信息失败: {e}")
            return {"table_name": table_name, "columns": [], "row_count": 0}
