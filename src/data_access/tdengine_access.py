"""
TDengine数据访问层

封装TDengine WebSocket连接的所有CRUD操作。
专门处理高频时序数据(Tick/分钟线/盘口快照)的存储和查询。

创建日期: 2025-10-11
版本: 1.0.0
"""

import pandas as pd
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta

from src.storage.database.connection_manager import get_connection_manager


class TDengineDataAccess:
    """
    TDengine数据访问类

    提供高频时序数据的存储和查询接口:
    - 超表(STable)管理
    - 批量写入(自动按timestamp分区)
    - 时间范围查询
    - 聚合查询(OHLC等)
    """

    def __init__(self):
        """初始化TDengine连接"""
        self.conn_manager = get_connection_manager()
        self.conn = None

    def _get_connection(self):
        """获取TDengine连接(懒加载)"""
        if self.conn is None:
            self.conn = self.conn_manager.get_tdengine_connection()
        return self.conn

    def create_stable(
        self, stable_name: str, schema: Dict[str, str], tags: Dict[str, str]
    ):
        """
        创建超表(STable)

        Args:
            stable_name: 超表名称
            schema: 字段定义 {'ts': 'TIMESTAMP', 'price': 'FLOAT', 'volume': 'INT'}
            tags: 标签定义 {'symbol': 'BINARY(20)', 'exchange': 'BINARY(10)'}

        Example:
            create_stable('tick_data',
                         {'ts': 'TIMESTAMP', 'price': 'FLOAT', 'volume': 'INT'},
                         {'symbol': 'BINARY(20)', 'exchange': 'BINARY(10)'})
        """
        conn = self._get_connection()

        # 构建字段列表
        fields = ", ".join([f"{name} {dtype}" for name, dtype in schema.items()])
        tag_fields = ", ".join([f"{name} {dtype}" for name, dtype in tags.items()])

        # 创建超表SQL
        sql = (
            f"CREATE STABLE IF NOT EXISTS {stable_name} ({fields}) TAGS ({tag_fields})"
        )

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.close()
            print(f"✅ 超表创建成功: {stable_name}")
        except Exception as e:
            print(f"❌ 超表创建失败: {e}")
            raise

    def create_table(
        self, table_name: str, stable_name: str, tag_values: Dict[str, Any]
    ):
        """
        创建子表(基于超表)

        Args:
            table_name: 子表名称 (建议: {stable_name}_{symbol})
            stable_name: 超表名称
            tag_values: 标签值 {'symbol': '600000.SH', 'exchange': 'SSE'}

        Example:
            create_table('tick_data_600000', 'tick_data', {'symbol': '600000.SH', 'exchange': 'SSE'})
        """
        conn = self._get_connection()

        # 构建标签值列表
        tags = ", ".join(
            [f"'{v}'" if isinstance(v, str) else str(v) for v in tag_values.values()]
        )

        # 创建子表SQL
        sql = (
            f"CREATE TABLE IF NOT EXISTS {table_name} USING {stable_name} TAGS ({tags})"
        )

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            cursor.close()
        except Exception as e:
            print(f"❌ 子表创建失败: {e}")
            raise

    def insert_dataframe(
        self, table_name: str, df: pd.DataFrame, timestamp_col: str = "ts"
    ):
        """
        批量插入DataFrame数据

        Args:
            table_name: 表名
            df: 数据DataFrame (必须包含timestamp列)
            timestamp_col: 时间戳列名 (默认'ts')

        Returns:
            插入的行数

        Example:
            df = pd.DataFrame({
                'ts': pd.date_range('2025-01-01', periods=1000, freq='1s'),
                'price': np.random.uniform(10, 20, 1000),
                'volume': np.random.randint(100, 10000, 1000)
            })
            insert_dataframe('tick_data_600000', df)
        """
        if df.empty:
            return 0

        conn = self._get_connection()

        # 确保时间戳列为datetime类型
        if not pd.api.types.is_datetime64_any_dtype(df[timestamp_col]):
            df[timestamp_col] = pd.to_datetime(df[timestamp_col])

        # 构建批量插入SQL
        columns = ", ".join(df.columns)

        # 准备数据行
        rows = []
        for _, row in df.iterrows():
            values = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val):
                    values.append("NULL")
                elif isinstance(val, str):
                    values.append(f"'{val}'")
                elif isinstance(val, datetime):
                    values.append(f"'{val.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}'")
                else:
                    values.append(str(val))
            rows.append(f"({', '.join(values)})")

        # 分批插入(每批10000条)
        batch_size = 10000
        total_inserted = 0

        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            sql = f"INSERT INTO {table_name} ({columns}) VALUES {', '.join(batch)}"

            try:
                cursor = conn.cursor()
                cursor.execute(sql)
                total_inserted += len(batch)
                cursor.close()
            except Exception as e:
                print(f"❌ 批量插入失败 (批次{i // batch_size + 1}): {e}")
                raise

        return total_inserted

    def query_by_time_range(
        self,
        table_name: str,
        start_time: datetime,
        end_time: datetime,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame:
        """
        按时间范围查询数据

        Args:
            table_name: 表名
            start_time: 开始时间
            end_time: 结束时间
            columns: 查询字段列表 (None表示所有字段)
            limit: 返回行数限制

        Returns:
            查询结果DataFrame

        Example:
            df = query_by_time_range(
                'tick_data_600000',
                datetime(2025, 1, 1, 9, 30),
                datetime(2025, 1, 1, 15, 0),
                columns=['ts', 'price', 'volume'],
                limit=10000
            )
        """
        conn = self._get_connection()

        # 构建查询SQL
        cols = ", ".join(columns) if columns else "*"
        sql = f"""
            SELECT {cols}
            FROM {table_name}
            WHERE ts >= '{start_time.strftime('%Y-%m-%d %H:%M:%S')}'
              AND ts < '{end_time.strftime('%Y-%m-%d %H:%M:%S')}'
            ORDER BY ts ASC
        """

        if limit:
            sql += f" LIMIT {limit}"

        try:
            cursor = conn.cursor()
            cursor.execute(sql)

            # 获取列名
            column_names = [desc[0] for desc in cursor.description]

            # 获取数据
            rows = cursor.fetchall()
            cursor.close()

            # 转换为DataFrame
            df = pd.DataFrame(rows, columns=column_names)

            return df

        except Exception as e:
            print(f"❌ 查询失败: {e}")
            raise

    def query_latest(self, table_name: str, limit: int = 100) -> pd.DataFrame:
        """
        查询最新N条数据

        Args:
            table_name: 表名
            limit: 返回行数 (默认100)

        Returns:
            最新数据DataFrame
        """
        conn = self._get_connection()

        sql = f"""
            SELECT *
            FROM {table_name}
            ORDER BY ts DESC
            LIMIT {limit}
        """

        try:
            cursor = conn.cursor()
            cursor.execute(sql)

            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            df = pd.DataFrame(rows, columns=column_names)
            return df

        except Exception as e:
            print(f"❌ 查询最新数据失败: {e}")
            raise

    def aggregate_to_kline(
        self,
        table_name: str,
        start_time: datetime,
        end_time: datetime,
        interval: str = "1m",
        price_col: str = "price",
        volume_col: str = "volume",
    ) -> pd.DataFrame:
        """
        聚合为K线数据

        Args:
            table_name: 表名
            start_time: 开始时间
            end_time: 结束时间
            interval: 聚合周期 ('1m', '5m', '15m', '1h', '1d')
            price_col: 价格字段名
            volume_col: 成交量字段名

        Returns:
            K线DataFrame (columns: ts, open, high, low, close, volume)

        Example:
            kline = aggregate_to_kline(
                'tick_data_600000',
                datetime(2025, 1, 1),
                datetime(2025, 1, 2),
                interval='5m'
            )
        """
        conn = self._get_connection()

        sql = f"""
            SELECT
                _wstart as ts,
                FIRST({price_col}) as open,
                MAX({price_col}) as high,
                MIN({price_col}) as low,
                LAST({price_col}) as close,
                SUM({volume_col}) as volume
            FROM {table_name}
            WHERE ts >= '{start_time.strftime('%Y-%m-%d %H:%M:%S')}'
              AND ts < '{end_time.strftime('%Y-%m-%d %H:%M:%S')}'
            INTERVAL({interval})
        """

        try:
            cursor = conn.cursor()
            cursor.execute(sql)

            column_names = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            cursor.close()

            df = pd.DataFrame(rows, columns=column_names)
            return df

        except Exception as e:
            print(f"❌ K线聚合失败: {e}")
            raise

    def delete_by_time_range(
        self, table_name: str, start_time: datetime, end_time: datetime
    ) -> int:
        """
        删除时间范围内的数据

        Args:
            table_name: 表名
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            删除的行数
        """
        conn = self._get_connection()

        sql = f"""
            DELETE FROM {table_name}
            WHERE ts >= '{start_time.strftime('%Y-%m-%d %H:%M:%S')}'
              AND ts < '{end_time.strftime('%Y-%m-%d %H:%M:%S')}'
        """

        try:
            cursor = conn.cursor()
            cursor.execute(sql)
            affected_rows = cursor.rowcount or 0
            cursor.close()

            return int(affected_rows)

        except Exception as e:
            print(f"❌ 删除数据失败: {e}")
            raise

    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取表信息(行数、时间范围、磁盘占用)

        Args:
            table_name: 表名

        Returns:
            表信息字典
        """
        conn = self._get_connection()

        sql = f"""
            SELECT
                COUNT(*) as row_count,
                MIN(ts) as start_time,
                MAX(ts) as end_time
            FROM {table_name}
        """

        try:
            cursor = conn.cursor()
            cursor.execute(sql)

            row = cursor.fetchone()
            cursor.close()

            return {
                "row_count": row[0] if row else 0,
                "start_time": row[1] if row else None,
                "end_time": row[2] if row else None,
            }

        except Exception as e:
            print(f"❌ 获取表信息失败: {e}")
            return {"row_count": 0, "start_time": None, "end_time": None}

    def save_data(
        self, data: pd.DataFrame, classification, table_name: str, **kwargs
    ) -> bool:
        """
        保存数据（DataManager API适配器）

        Args:
            data: 数据DataFrame
            classification: 数据分类（US3架构参数，此处未使用）
            table_name: 表名
            **kwargs: 其他参数

        Returns:
            bool: 保存是否成功
        """
        try:
            self.insert_dataframe(
                table_name, data, timestamp_col=kwargs.get("timestamp_col", "ts")
            )
            return True
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False

    def load_data(self, table_name: str, **filters) -> Optional[pd.DataFrame]:
        """
        加载数据（DataManager API适配器）

        Args:
            table_name: 表名
            **filters: 过滤条件（如start_time, end_time）

        Returns:
            pd.DataFrame or None: 查询结果
        """
        try:
            if "start_time" in filters and "end_time" in filters:
                return self.query_by_time_range(
                    table_name,
                    filters["start_time"],
                    filters["end_time"],
                    columns=filters.get("columns"),
                )
            else:
                # 如果没有时间范围，返回最新数据
                return self.query_latest(table_name, limit=filters.get("limit", 100))
        except Exception as e:
            print(f"❌ 加载数据失败: {e}")
            return None

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            self.conn = None


if __name__ == "__main__":
    """测试TDengine数据访问层"""
    print("\n正在测试TDengine数据访问层...\n")

    access = TDengineDataAccess()

    # 测试连接
    try:
        conn = access._get_connection()
        print("✅ TDengine连接成功\n")
    except Exception as e:
        print(f"❌ TDengine连接失败: {e}")
        exit(1)

    print("TDengine数据访问层基础功能已实现")
    print("主要功能:")
    print("  - 超表/子表管理")
    print("  - DataFrame批量写入")
    print("  - 时间范围查询")
    print("  - 最新数据查询")
    print("  - K线聚合")
    print("  - 数据删除")
    print("  - 表信息统计")

    access.close()
