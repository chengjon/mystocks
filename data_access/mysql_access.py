"""
MySQL数据访问层

封装MySQL/MariaDB的所有CRUD操作。
专门处理参考数据和元数据(股票信息/交易日历/系统配置)。

创建日期: 2025-10-11
版本: 1.0.0
"""

import pandas as pd
from typing import Optional, Dict, Any, List, Tuple
import pymysql
from pymysql.cursors import DictCursor

from db_manager.connection_manager import get_connection_manager


class MySQLDataAccess:
    """
    MySQL/MariaDB数据访问类

    提供参考数据和元数据的存储和查询接口:
    - 表管理(CREATE/ALTER)
    - 批量写入(executemany优化)
    - ACID事务支持
    - 复杂JOIN查询
    - 索引管理
    """

    def __init__(self):
        """初始化MySQL连接"""
        self.conn_manager = get_connection_manager()
        self.conn = None

    def _get_connection(self):
        """获取MySQL连接(懒加载)"""
        if self.conn is None:
            self.conn = self.conn_manager.get_mysql_connection()
        return self.conn

    def _reconnect_if_needed(self):
        """检查连接并在需要时重连"""
        try:
            conn = self._get_connection()
            conn.ping(reconnect=True)
        except Exception:
            self.conn = None
            self.conn = self._get_connection()

    def create_table(self, table_name: str, schema: Dict[str, str], primary_key: Optional[str] = None):
        """
        创建表

        Args:
            table_name: 表名
            schema: 字段定义 {'symbol': 'VARCHAR(20)', 'name': 'VARCHAR(100)', 'list_date': 'DATE'}
            primary_key: 主键字段

        Example:
            create_table('stock_info', {
                'symbol': 'VARCHAR(20)',
                'name': 'VARCHAR(100)',
                'exchange': 'VARCHAR(10)',
                'list_date': 'DATE',
                'delist_date': 'DATE',
                'is_active': 'TINYINT DEFAULT 1'
            }, primary_key='symbol')
        """
        conn = self._get_connection()

        try:
            # 构建字段列表
            fields = ',\n    '.join([f"{name} {dtype}" for name, dtype in schema.items()])

            # 添加主键
            if primary_key:
                fields += f",\n    PRIMARY KEY ({primary_key})"

            sql = f"CREATE TABLE IF NOT EXISTS {table_name} (\n    {fields}\n) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4"

            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()

            print(f"✅ 表创建成功: {table_name}")

        except Exception as e:
            conn.rollback()
            print(f"❌ 表创建失败: {e}")
            raise

    def create_index(self, table_name: str, index_name: str, columns: List[str], unique: bool = False):
        """
        创建索引

        Args:
            table_name: 表名
            index_name: 索引名
            columns: 索引列列表
            unique: 是否唯一索引

        Example:
            create_index('stock_info', 'idx_exchange', ['exchange'])
            create_index('stock_info', 'idx_unique_name', ['name'], unique=True)
        """
        conn = self._get_connection()

        try:
            unique_str = 'UNIQUE' if unique else ''
            columns_str = ', '.join(columns)

            sql = f"CREATE {unique_str} INDEX {index_name} ON {table_name} ({columns_str})"

            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()
            cursor.close()

            print(f"✅ 索引创建成功: {index_name}")

        except Exception as e:
            conn.rollback()
            print(f"❌ 索引创建失败: {e}")
            # 索引已存在时不抛出异常
            if 'Duplicate key name' not in str(e):
                raise

    def insert_dataframe(self, table_name: str, df: pd.DataFrame, batch_size: int = 1000) -> int:
        """
        批量插入DataFrame数据

        Args:
            table_name: 表名
            df: 数据DataFrame
            batch_size: 批次大小 (默认1000)

        Returns:
            插入的行数

        Example:
            df = pd.DataFrame({
                'symbol': ['600000.SH', '000001.SZ'],
                'name': ['浦发银行', '平安银行'],
                'exchange': ['SSE', 'SZSE']
            })
            insert_dataframe('stock_info', df)
        """
        if df.empty:
            return 0

        conn = self._get_connection()

        try:
            columns = list(df.columns)
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            # 转换数据为tuple列表
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]

            # 分批插入
            cursor = conn.cursor()
            total_inserted = 0

            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                cursor.executemany(sql, batch)
                total_inserted += cursor.rowcount

            conn.commit()
            cursor.close()

            return total_inserted

        except Exception as e:
            conn.rollback()
            print(f"❌ 批量插入失败: {e}")
            raise

    def upsert_dataframe(
        self,
        table_name: str,
        df: pd.DataFrame,
        update_columns: Optional[List[str]] = None,
        batch_size: int = 1000
    ) -> int:
        """
        批量Upsert (INSERT ... ON DUPLICATE KEY UPDATE)

        Args:
            table_name: 表名
            df: 数据DataFrame
            update_columns: 需要更新的列 (None表示更新所有列)
            batch_size: 批次大小

        Returns:
            影响的行数

        Example:
            upsert_dataframe('stock_info', df, update_columns=['name', 'is_active'])
        """
        if df.empty:
            return 0

        conn = self._get_connection()

        try:
            columns = list(df.columns)
            columns_str = ', '.join(columns)
            placeholders = ', '.join(['%s'] * len(columns))

            # 构建UPDATE子句
            if update_columns is None:
                update_columns = columns

            update_str = ', '.join([f"{col} = VALUES({col})" for col in update_columns])

            sql = f"""
                INSERT INTO {table_name} ({columns_str})
                VALUES ({placeholders})
                ON DUPLICATE KEY UPDATE {update_str}
            """

            # 转换数据
            data = [tuple(row) for row in df.itertuples(index=False, name=None)]

            # 分批执行
            cursor = conn.cursor()
            total_affected = 0

            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                cursor.executemany(sql, batch)
                total_affected += cursor.rowcount

            conn.commit()
            cursor.close()

            return total_affected

        except Exception as e:
            conn.rollback()
            print(f"❌ Upsert失败: {e}")
            raise

    def query(
        self,
        table_name: str,
        columns: Optional[List[str]] = None,
        where: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """
        通用查询

        Args:
            table_name: 表名
            columns: 查询字段列表 (None表示所有字段)
            where: WHERE子句
            order_by: ORDER BY子句
            limit: 返回行数限制

        Returns:
            查询结果DataFrame

        Example:
            df = query('stock_info',
                      columns=['symbol', 'name', 'exchange'],
                      where="exchange = 'SSE' AND is_active = 1",
                      order_by='symbol ASC',
                      limit=100)
        """
        conn = self._get_connection()

        try:
            cols = ', '.join(columns) if columns else '*'
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

    def execute_sql(self, sql: str, params: Optional[Tuple] = None, fetch: bool = True) -> Optional[pd.DataFrame]:
        """
        执行自定义SQL

        Args:
            sql: SQL语句
            params: 参数元组
            fetch: 是否返回结果 (False用于INSERT/UPDATE/DELETE)

        Returns:
            查询结果DataFrame (fetch=True时)

        Example:
            # 查询
            df = execute_sql(
                "SELECT * FROM stock_info WHERE exchange = %s",
                params=('SSE',)
            )

            # 更新
            execute_sql(
                "UPDATE stock_info SET is_active = 0 WHERE delist_date < %s",
                params=('2020-01-01',),
                fetch=False
            )
        """
        conn = self._get_connection()

        try:
            if fetch:
                df = pd.read_sql(sql, conn, params=params)
                return df
            else:
                cursor = conn.cursor()
                cursor.execute(sql, params)
                conn.commit()
                cursor.close()
                return None

        except Exception as e:
            if not fetch:
                conn.rollback()
            print(f"❌ SQL执行失败: {e}")
            raise

    def delete(self, table_name: str, where: str) -> int:
        """
        删除数据

        Args:
            table_name: 表名
            where: WHERE子句

        Returns:
            删除的行数

        Example:
            deleted = delete('stock_info', "delist_date < '2020-01-01'")
        """
        conn = self._get_connection()

        try:
            sql = f"DELETE FROM {table_name} WHERE {where}"

            cursor = conn.cursor()
            cursor.execute(sql)
            conn.commit()

            rows_deleted = cursor.rowcount
            cursor.close()

            return rows_deleted

        except Exception as e:
            conn.rollback()
            print(f"❌ 删除失败: {e}")
            raise

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息

        Args:
            table_name: 表名

        Returns:
            表信息字典
        """
        conn = self._get_connection()

        try:
            cursor = conn.cursor()

            # 获取行数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]

            # 获取表大小
            cursor.execute(f"""
                SELECT
                    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS size_mb
                FROM information_schema.TABLES
                WHERE table_schema = DATABASE()
                  AND table_name = '{table_name}'
            """)
            size_row = cursor.fetchone()
            size_mb = size_row[0] if size_row else 0

            cursor.close()

            return {
                'row_count': row_count,
                'size_mb': size_mb
            }

        except Exception as e:
            print(f"❌ 获取表信息失败: {e}")
            return {'row_count': 0, 'size_mb': 0}

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


if __name__ == "__main__":
    """测试MySQL数据访问层"""
    print("\n正在测试MySQL数据访问层...\n")

    access = MySQLDataAccess()

    # 测试连接
    try:
        conn = access._get_connection()
        print("✅ MySQL连接成功\n")
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        exit(1)

    print("MySQL数据访问层基础功能已实现")
    print("主要功能:")
    print("  - 表管理 (CREATE TABLE)")
    print("  - 索引管理 (CREATE INDEX)")
    print("  - DataFrame批量写入 (executemany)")
    print("  - Upsert操作 (ON DUPLICATE KEY UPDATE)")
    print("  - 通用查询")
    print("  - 自定义SQL执行")
    print("  - 数据删除")
    print("  - 表信息统计")

    access.close()
