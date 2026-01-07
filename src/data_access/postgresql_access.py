"""
PostgreSQL数据访问层

封装PostgreSQL+TimescaleDB的所有CRUD操作。
专门处理历史分析数据和衍生计算结果(日线/技术指标/回测结果)。

创建日期: 2025-10-11
版本: 1.1.0 (Added Transaction Scope)
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from contextlib import contextmanager

import pandas as pd
from psycopg2 import sql
from psycopg2.extras import execute_values

from src.storage.database.connection_manager import get_connection_manager


class PostgreSQLDataAccess:
    """
    PostgreSQL+TimescaleDB数据访问类

    提供历史分析数据的存储和查询接口:
    - 时序表(Hypertable)管理
    - 批量写入(execute_values优化)
    - 复杂时间范围查询
    - JOIN查询支持
    - 聚合和窗口函数
    - 事务管理 (transaction_scope)
    """

    def __init__(self, db_manager=None, monitoring_db=None):
        """初始化PostgreSQL连接池"""
        self.db_manager = db_manager
        self.monitoring_db = monitoring_db
        self.conn_manager = get_connection_manager()
        self.pool = None

    async def connect(self):
        """连接数据库(异步接口)"""
        self._get_pool()
        return True

    def check_connection(self):
        """检查数据库连接状态"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            self._return_connection(conn)
            return True
        except Exception:
            return False

    def _get_pool(self):
        """获取连接池(懒加载)"""
        if self.pool is None:
            self.pool = self.conn_manager.get_postgresql_connection()
        return self.pool

    def _get_connection(self):
        """从连接池获取连接"""
        if self.pool is None:
            self.pool = self.conn_manager.get_postgresql_connection()
        return self.pool.getconn()

    def _return_connection(self, conn):
        """归还连接到连接池"""
        if self.pool:
            self.pool.putconn(conn)

    @contextmanager
    def transaction_scope(self):
        """
        事务上下文管理器

        Usage:
            with pg.transaction_scope() as session:
                pg.execute_sql("", session=session)
                pg.execute_sql("", session=session)
            # 退出时自动 commit, 异常时自动 rollback
        """
        conn = self._get_connection()
        try:
            # 开启事务 (psycopg2 默认开启事务，只要不 autocommit)
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            self._return_connection(conn)

    def create_table(self, table_name: str, schema: Dict[str, str], primary_key: Optional[str] = None):
        """创建普通表"""
        conn = self._get_connection()
        try:
            fields = ",\n    ".join([f"{name} {dtype}" for name, dtype in schema.items()])
            if primary_key:
                fields += f",\n    PRIMARY KEY ({primary_key})"
            sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {fields}\n)"
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            print(f"✅ 表创建成功: {table_name}")
        except Exception as e:
            conn.rollback()
            print(f"❌ 表创建失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def create_hypertable(self, table_name: str, time_column: str = "time", chunk_interval: str = "7 days"):
        """将表转换为TimescaleDB时序表(Hypertable)"""
        conn = self._get_connection()
        try:
            sql = f"""
                SELECT create_hypertable(
                    '{table_name}',
                    '{time_column}',
                    chunk_time_interval => INTERVAL
'{chunk_interval}',
                    if_not_exists => TRUE
                )
            """
            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()
            print(f"✅ 时序表创建成功: {table_name}")
        except Exception as e:
            conn.rollback()
            print(f"❌ 时序表创建失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def insert_dataframe(self, table_name: str, df: pd.DataFrame) -> int:
        """批量插入DataFrame数据"""
        if df.empty:
            return 0
        conn = self._get_connection()
        try:
            columns = list(df.columns)
            columns_str = ", ".join(columns)
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]
            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"
            cursor = conn.cursor()
            execute_values(cursor, sql, data)
            conn.commit()
            rows_inserted = cursor.rowcount or 0
            cursor.close()
            return int(rows_inserted)
        except Exception as e:
            conn.rollback()
            print(f"❌ 批量插入失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def upsert_dataframe(
        self,
        table_name: str,
        df: pd.DataFrame,
        conflict_columns: List[str],
        update_columns: Optional[List[str]] = None,
    ) -> int:
        """批量Upsert"""
        if df.empty:
            return 0
        conn = self._get_connection()
        try:
            columns = list(df.columns)
            columns_str = ", ".join(columns)
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]
            conflict_str = ", ".join(conflict_columns)
            if update_columns is None:
                update_columns = [col for col in columns if col not in conflict_columns]
            update_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            sql = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES %s
                ON CONFLICT ({conflict_str})
                DO UPDATE SET {update_str}
            """
            cursor = conn.cursor()
            execute_values(cursor, sql, data)
            conn.commit()
            rows_affected = cursor.rowcount or 0
            cursor.close()
            return int(rows_affected)
        except Exception as e:
            conn.rollback()
            print(f"❌ Upsert失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def query(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
        params: Optional[Tuple] = None,
    ) -> pd.DataFrame:
        """通用查询"""
        conn = self._get_connection()
        try:
            # SECURITY FIX: Whitelist table names
            ALLOWED_TABLES = {
                "daily_kline",
                "minute_kline",
                "tick_data",
                "symbols_info",
                "technical_indicators",
                "quantitative_factors",
                "model_outputs",
                "trading_signals",
                "order_records",
                "transaction_records",
                "position_records",
                "account_funds",
                "realtime_quotes",
                "market_data",
                "stock_basic",
                "trade_cal",
                "income_statement",
                "balance_sheet",
                "cash_flow",
                "financial_indicators",
                "monitoring_logs",
                "alerts",
                "system_metrics",
                "concepts",
                "industries",
                "transaction_log",  # Added transaction_log
            }
            if table_name not in ALLOWED_TABLES:
                raise ValueError(f"Invalid table name: {table_name}")

            if columns:
                # Basic validation for columns
                cols = ", ".join(columns)
            else:
                cols = "*"

            if cols == "*":
                sql_query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            else:
                col_identifiers = [sql.Identifier(col.strip()) for col in cols.split(",")]
                sql_query = sql.SQL("SELECT {} FROM {}").format(
                    sql.SQL(", ").join(col_identifiers), sql.Identifier(table_name)
                )

            if where:
                if "%s" in where or "%" in where:
                    sql_query = sql.SQL("{} WHERE {}").format(sql_query, sql.SQL(where))
                else:
                    # Simple validation
                    if any(x in where.lower() for x in [";", "--", "drop", "truncate"]):
                        raise ValueError("Potentially dangerous SQL pattern")
                    sql_query = sql.SQL("{} WHERE {}").format(sql_query, sql.SQL(where))

            if order_by:
                # Basic validation
                if any(x in order_by.lower() for x in [";", "--", "drop"]):
                    raise ValueError("Invalid order by")
                sql_query = sql.SQL("{} ORDER BY {}").format(sql_query, sql.SQL(order_by))

            if limit:
                sql_query = sql.SQL("{} LIMIT {}").format(sql_query, sql.Literal(limit))

            df = pd.read_sql(sql_query.as_string(conn), conn, params=params)
            return df

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def query_by_time_range(
        self,
        table_name: str,
        time_column: str,
        start_time: datetime,
        end_time: datetime,
        columns: Optional[List[str]] = None,
        filters: Optional[str] = None,
    ) -> pd.DataFrame:
        """按时间范围查询"""
        where_clause = f"{time_column} >= '{start_time}' AND {time_column} < '{end_time}'"
        if filters:
            where_clause += f" AND {filters}"
        return self.query(table_name, columns, where_clause, order_by=f"{time_column} ASC")

    def execute_sql(self, sql_str: str, params: Optional[Tuple] = None, session=None) -> pd.DataFrame:
        """
        执行自定义SQL查询

        Args:
            session: 可选的数据库连接对象 (如果在事务中)
        """
        # 如果提供了 session (conn)，直接使用，不负责关闭
        # 如果未提供，从池中获取并负责归还
        conn = session if session else self._get_connection()
        should_close = session is None

        try:
            # 如果是 SELECT 语句，返回 DataFrame
            if sql_str.strip().upper().startswith("SELECT"):
                df = pd.read_sql(sql_str, conn, params=params)
                return df
            else:
                # 如果是 UPDATE/INSERT/DELETE
                cursor = conn.cursor()
                cursor.execute(sql_str, params)
                if should_close:  # 只有非事务模式下才自动提交
                    conn.commit()
                cursor.close()
                return pd.DataFrame()  # 返回空 DF

        except Exception as e:
            if should_close:
                conn.rollback()
            print(f"❌ SQL执行失败: {e}")
            raise
        finally:
            if should_close:
                self._return_connection(conn)

    def delete(self, table_name: str, where: str, params: Optional[Tuple] = None) -> int:
        """删除数据"""
        conn = self._get_connection()
        try:
            if params:
                sql = f"DELETE FROM {table_name} WHERE {where}"
                cursor = conn.cursor()
                cursor.execute(sql, params)
            else:
                sql = f"DELETE FROM {table_name} WHERE {where}"
                cursor = conn.cursor()
                cursor.execute(sql)
            conn.commit()
            rows_deleted = cursor.rowcount or 0
            cursor.close()
            return int(rows_deleted)
        except Exception as e:
            conn.rollback()
            print(f"❌ 删除失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """获取表统计信息"""
        conn = self._get_connection()
        try:
            query = sql.SQL(
                "SELECT COUNT(*) as row_count, pg_size_pretty(pg_total_relation_size(%s)) as total_size FROM {}"
            ).format(sql.Identifier(table_name))
            cursor = conn.cursor()
            cursor.execute(query, (table_name,))
            row = cursor.fetchone()
            cursor.close()
            return {"row_count": row[0] if row else 0, "total_size": row[1] if row else "0 bytes"}
        except Exception as e:
            print(f"❌ 获取表统计失败: {e}")
            return {"row_count": 0, "total_size": "0 bytes"}
        finally:
            self._return_connection(conn)

    def save_data(self, data: pd.DataFrame, classification, table_name: str, **kwargs) -> bool:
        """保存数据"""
        try:
            if kwargs.get("upsert", False):
                conflict_columns = kwargs.get("conflict_columns", ["id"])
                row_count = self.upsert_dataframe(table_name, data, conflict_columns)
            else:
                row_count = self.insert_dataframe(table_name, data)
            return row_count > 0
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False

    def load_data(self, table_name: str, **filters) -> Optional[pd.DataFrame]:
        """加载数据"""
        try:
            if "start_time" in filters and "end_time" in filters:
                time_column = filters.get("time_column", "time")
                return self.query_by_time_range(table_name, time_column, filters["start_time"], filters["end_time"])
            elif "where" in filters:
                return self.query(table_name, where=filters["where"], limit=filters.get("limit"))
            else:
                return self.query(table_name, limit=filters.get("limit"))
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None

    def execute_update(self, sql_str: str, params: Optional[Tuple] = None) -> bool:
        """执行更新操作 (Alias for execute_sql for API consistency)"""
        try:
            self.execute_sql(sql_str, params)
            return True
        except Exception:
            return False

    def close(self):
        """关闭所有连接"""
        if self.pool:
            self.pool.closeall()
            self.pool = None

    def close_all(self):
        self.close()


if __name__ == "__main__":
    pass
