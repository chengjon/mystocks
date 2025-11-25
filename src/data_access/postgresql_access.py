"""
PostgreSQL数据访问层

封装PostgreSQL+TimescaleDB的所有CRUD操作。
专门处理历史分析数据和衍生计算结果(日线/技术指标/回测结果)。

创建日期: 2025-10-11
版本: 1.0.0
"""

import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
import psycopg2
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
    """

    def __init__(self):
        """初始化PostgreSQL连接池"""
        self.conn_manager = get_connection_manager()
        self.pool = None

    def _get_connection(self):
        """从连接池获取连接"""
        if self.pool is None:
            self.pool = self.conn_manager.get_postgresql_connection()
        return self.pool.getconn()

    def _return_connection(self, conn):
        """归还连接到连接池"""
        if self.pool:
            self.pool.putconn(conn)

    def create_table(
        self, table_name: str, schema: Dict[str, str], primary_key: Optional[str] = None
    ):
        """
        创建普通表

        Args:
            table_name: 表名
            schema: 字段定义 {'symbol': 'VARCHAR(20)', 'date': 'DATE', 'close': 'DECIMAL(10,2)'}
            primary_key: 主键字段 (可选)

        Example:
            create_table('daily_kline', {
                'symbol': 'VARCHAR(20)',
                'date': 'DATE',
                'open': 'DECIMAL(10,2)',
                'high': 'DECIMAL(10,2)',
                'low': 'DECIMAL(10,2)',
                'close': 'DECIMAL(10,2)',
                'volume': 'BIGINT'
            }, primary_key='symbol, date')
        """
        conn = self._get_connection()

        try:
            # 构建字段列表
            fields = ",\n    ".join(
                [f"{name} {dtype}" for name, dtype in schema.items()]
            )

            # 添加主键约束
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

    def create_hypertable(
        self, table_name: str, time_column: str = "time", chunk_interval: str = "7 days"
    ):
        """
        将表转换为TimescaleDB时序表(Hypertable)

        Args:
            table_name: 表名
            time_column: 时间列名 (默认'time')
            chunk_interval: 分块间隔 (默认7天)

        Example:
            create_hypertable('daily_kline', 'date', '30 days')
        """
        conn = self._get_connection()

        try:
            sql = f"""
                SELECT create_hypertable(
                    '{table_name}',
                    '{time_column}',
                    chunk_time_interval => INTERVAL '{chunk_interval}',
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
        """
        批量插入DataFrame数据 (使用execute_values优化)

        Args:
            table_name: 表名
            df: 数据DataFrame

        Returns:
            插入的行数

        Example:
            df = pd.DataFrame({
                'symbol': ['600000.SH'] * 100,
                'date': pd.date_range('2025-01-01', periods=100),
                'close': np.random.uniform(10, 20, 100)
            })
            insert_dataframe('daily_kline', df)
        """
        if df.empty:
            return 0

        conn = self._get_connection()

        try:
            # 准备列名和数据
            columns = list(df.columns)
            columns_str = ", ".join(columns)

            # 转换DataFrame为tuple列表
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]

            # 构建插入SQL
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
        """
        批量Upsert (INSERT ... ON CONFLICT UPDATE)

        Args:
            table_name: 表名
            df: 数据DataFrame
            conflict_columns: 冲突检测列 (通常是主键)
            update_columns: 需要更新的列 (None表示更新所有非冲突列)

        Returns:
            影响的行数

        Example:
            upsert_dataframe('daily_kline', df,
                           conflict_columns=['symbol', 'date'],
                           update_columns=['close', 'volume'])
        """
        if df.empty:
            return 0

        conn = self._get_connection()

        try:
            columns = list(df.columns)
            columns_str = ", ".join(columns)

            # 准备数据
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]

            # 构建冲突处理子句
            conflict_str = ", ".join(conflict_columns)

            if update_columns is None:
                update_columns = [col for col in columns if col not in conflict_columns]

            update_str = ", ".join(
                [f"{col} = EXCLUDED.{col}" for col in update_columns]
            )

            # Upsert SQL
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
    ) -> pd.DataFrame:
        """
        通用查询

        Args:
            table_name: 表名
            columns: 查询字段列表 (None表示所有字段)
            where: WHERE子句 (不含WHERE关键字)
            order_by: ORDER BY子句 (不含ORDER BY关键字)
            limit: 返回行数限制

        Returns:
            查询结果DataFrame

        Example:
            df = query('daily_kline',
                      columns=['symbol', 'date', 'close'],
                      where="symbol = '600000.SH' AND date >= '2025-01-01'",
                      order_by='date DESC',
                      limit=100)
        """
        conn = self._get_connection()

        try:
            cols = ", ".join(columns) if columns else "*"
            sql = f"SELECT {cols} FROM {table_name}"

            if where:
                sql += f" WHERE {where}"

            if order_by:
                sql += f" ORDER BY {order_by}"

            if limit:
                sql += f" LIMIT {limit}"

            df = pd.read_sql(sql, conn)
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
        """
        按时间范围查询

        Args:
            table_name: 表名
            time_column: 时间列名
            start_time: 开始时间
            end_time: 结束时间
            columns: 查询字段列表
            filters: 额外过滤条件

        Returns:
            查询结果DataFrame
        """
        where_clause = (
            f"{time_column} >= '{start_time}' AND {time_column} < '{end_time}'"
        )

        if filters:
            where_clause += f" AND {filters}"

        return self.query(
            table_name, columns, where_clause, order_by=f"{time_column} ASC"
        )

    def execute_sql(self, sql: str, params: Optional[Tuple] = None) -> pd.DataFrame:
        """
        执行自定义SQL查询

        Args:
            sql: SQL语句
            params: 参数元组 (用于参数化查询)

        Returns:
            查询结果DataFrame

        Example:
            df = execute_sql(
                \"\"\"
                SELECT symbol, AVG(close) as avg_close
                FROM daily_kline
                WHERE date >= %s
                GROUP BY symbol
                HAVING AVG(close) > %s
                \"\"\",
                params=('2025-01-01', 50.0)
            )
        """
        conn = self._get_connection()

        try:
            df = pd.read_sql(sql, conn, params=params)
            return df

        except Exception as e:
            print(f"❌ SQL执行失败: {e}")
            raise
        finally:
            self._return_connection(conn)

    def delete(self, table_name: str, where: str) -> int:
        """
        删除数据

        Args:
            table_name: 表名
            where: WHERE子句 (不含WHERE关键字)

        Returns:
            删除的行数

        Example:
            deleted = delete('daily_kline', "date < '2020-01-01'")
        """
        conn = self._get_connection()

        try:
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
        """
        获取表统计信息

        Args:
            table_name: 表名

        Returns:
            统计信息字典
        """
        conn = self._get_connection()

        try:
            sql = f"""
                SELECT
                    COUNT(*) as row_count,
                    pg_size_pretty(pg_total_relation_size('{table_name}')) as total_size
                FROM {table_name}
            """

            cursor = conn.cursor()
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()

            return {
                "row_count": row[0] if row else 0,
                "total_size": row[1] if row else "0 bytes",
            }

        except Exception as e:
            print(f"❌ 获取表统计失败: {e}")
            return {"row_count": 0, "total_size": "0 bytes"}
        finally:
            self._return_connection(conn)

    def save_data(
        self, data: pd.DataFrame, classification, table_name: str, **kwargs
    ) -> bool:
        """
        保存数据（DataManager API适配器）

        Args:
            data: 数据DataFrame
            classification: 数据分类（US3架构参数，此处未使用）
            table_name: 表名
            **kwargs: 其他参数（如upsert=True, conflict_columns）

        Returns:
            bool: 保存是否成功
        """
        try:
            if kwargs.get("upsert", False):
                # 使用upsert操作
                conflict_columns = kwargs.get("conflict_columns", ["id"])
                row_count = self.upsert_dataframe(table_name, data, conflict_columns)
            else:
                # 使用普通插入
                row_count = self.insert_dataframe(table_name, data)
            return row_count > 0
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False

    def load_data(self, table_name: str, **filters) -> Optional[pd.DataFrame]:
        """
        加载数据（DataManager API适配器）

        Args:
            table_name: 表名
            **filters: 过滤条件

        Returns:
            pd.DataFrame or None: 查询结果
        """
        try:
            if "start_time" in filters and "end_time" in filters:
                # 时间范围查询
                time_column = filters.get("time_column", "time")
                return self.query_by_time_range(
                    table_name,
                    time_column,
                    filters["start_time"],
                    filters["end_time"],
                )
            elif "where" in filters:
                # 自定义where条件
                sql = f"SELECT * FROM {table_name} WHERE {filters['where']}"
                if "limit" in filters:
                    sql += f" LIMIT {filters['limit']}"
                return self.query(
                    table_name, where=filters["where"], limit=filters.get("limit")
                )
            else:
                # 查询全表（带limit）
                sql = f"SELECT * FROM {table_name}"
                if "limit" in filters:
                    sql += f" LIMIT {filters['limit']}"
                return self.execute_sql(sql)
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None

    def close(self):
        """关闭所有连接"""
        if self.pool:
            self.pool.closeall()
            self.pool = None
            
    def close_all(self):
        """关闭所有连接（兼容旧接口）"""
        self.close()


if __name__ == "__main__":
    """测试PostgreSQL数据访问层"""
    print("\n正在测试PostgreSQL数据访问层...\n")

    access = PostgreSQLDataAccess()

    # 测试连接
    try:
        conn = access._get_connection()
        print("✅ PostgreSQL连接成功\n")
        access._return_connection(conn)
    except Exception as e:
        print(f"❌ PostgreSQL连接失败: {e}")
        exit(1)

    print("PostgreSQL数据访问层基础功能已实现")
    print("主要功能:")
    print("  - 普通表/时序表(Hypertable)管理")
    print("  - DataFrame批量写入 (execute_values优化)")
    print("  - Upsert操作 (ON CONFLICT)")
    print("  - 时间范围查询")
    print("  - 自定义SQL执行")
    print("  - 数据删除")
    print("  - 表统计信息")

    access.close_all()
