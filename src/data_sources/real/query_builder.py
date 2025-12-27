"""
PostgreSQL查询构建器
从 postgresql_relational.py 中提取，专门用于SQL查询构建和执行
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, date
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class QueryBuilder:
    """
    PostgreSQL查询构建器

    提供链式API构建SQL查询，避免SQL注入，简化参数绑定
    """

    def __init__(self, connection_provider):
        """
        初始化查询构建器

        Args:
            connection_provider: 数据库连接提供者
        """
        self.connection_provider = connection_provider
        self.reset()

    def reset(self):
        """重置查询构建器"""
        self._query_type = None
        self._select_fields = []
        self._table_name = None
        self._joins = []
        self._where_conditions = []
        self._group_by_fields = []
        self._having_conditions = []
        self._order_by_fields = []
        self._limit_count = None
        self._offset_count = None
        self._values = []
        self._returning_fields = []
        return self

    # ==================== SELECT 查询构建 ====================

    def select(self, *fields: str) -> "QueryBuilder":
        """
        设置查询字段

        Args:
            *fields: 字段列表

        Returns:
            QueryBuilder: 链式调用
        """
        self._query_type = "SELECT"
        self._select_fields.extend(fields)
        return self

    def from_table(self, table: str, alias: Optional[str] = None) -> "QueryBuilder":
        """
        设置主表

        Args:
            table: 表名
            alias: 表别名

        Returns:
            QueryBuilder: 链式调用
        """
        self._table_name = f"{table} AS {alias}" if alias else table
        return self

    def join(self, table: str, on_condition: str, join_type: str = "INNER") -> "QueryBuilder":
        """
        添加JOIN

        Args:
            table: 连接表
            on_condition: 连接条件
            join_type: JOIN类型 (INNER, LEFT, RIGHT, FULL)

        Returns:
            QueryBuilder: 链式调用
        """
        self._joins.append(f"{join_type} JOIN {table} ON {on_condition}")
        return self

    def left_join(self, table: str, on_condition: str) -> "QueryBuilder":
        """添加LEFT JOIN的快捷方法"""
        return self.join(table, on_condition, "LEFT")

    def where(self, condition: str, *args) -> "QueryBuilder":
        """
        添加WHERE条件

        Args:
            condition: 条件字符串，使用%s作为参数占位符
            *args: 参数值

        Returns:
            QueryBuilder: 链式调用
        """
        self._where_conditions.append(condition)
        self._values.extend(args)
        return self

    def where_in(self, field: str, values: List[Any]) -> "QueryBuilder":
        """
        添加WHERE IN条件

        Args:
            field: 字段名
            values: 值列表

        Returns:
            QueryBuilder: 链式调用
        """
        placeholders = ",".join(["%s"] * len(values))
        condition = f"{field} IN ({placeholders})"
        return self.where(condition, *values)

    def where_between(self, field: str, start_value: Any, end_value: Any) -> "QueryBuilder":
        """
        添加WHERE BETWEEN条件

        Args:
            field: 字段名
            start_value: 开始值
            end_value: 结束值

        Returns:
            QueryBuilder: 链式调用
        """
        condition = f"{field} BETWEEN %s AND %s"
        return self.where(condition, start_value, end_value)

    def group_by(self, *fields: str) -> "QueryBuilder":
        """
        添加GROUP BY

        Args:
            *fields: 分组字段

        Returns:
            QueryBuilder: 链式调用
        """
        self._group_by_fields.extend(fields)
        return self

    def having(self, condition: str, *args) -> "QueryBuilder":
        """
        添加HAVING条件

        Args:
            condition: 条件字符串
            *args: 参数值

        Returns:
            QueryBuilder: 链式调用
        """
        self._having_conditions.append(condition)
        self._values.extend(args)
        return self

    def order_by(self, field: str, direction: str = "ASC") -> "QueryBuilder":
        """
        添加排序

        Args:
            field: 排序字段
            direction: 排序方向 (ASC, DESC)

        Returns:
            QueryBuilder: 链式调用
        """
        self._order_by_fields.append(f"{field} {direction}")
        return self

    def limit(self, count: int) -> "QueryBuilder":
        """
        设置LIMIT

        Args:
            count: 限制数量

        Returns:
            QueryBuilder: 链式调用
        """
        self._limit_count = count
        return self

    def offset(self, count: int) -> "QueryBuilder":
        """
        设置OFFSET

        Args:
            count: 偏移数量

        Returns:
            QueryBuilder: 链式调用
        """
        self._offset_count = count
        return self

    # ==================== INSERT 查询构建 ====================

    def insert_into(self, table: str) -> "QueryBuilder":
        """
        开始INSERT查询

        Args:
            table: 表名

        Returns:
            QueryBuilder: 链式调用
        """
        self._query_type = "INSERT"
        self._table_name = table
        return self

    def values(self, data: Dict[str, Any]) -> "QueryBuilder":
        """
        设置插入数据

        Args:
            data: 插入数据字典

        Returns:
            QueryBuilder: 链式调用
        """
        if not hasattr(self, "_insert_fields"):
            self._insert_fields = []
            self._insert_values = []

        self._insert_fields.extend(data.keys())
        self._insert_values.extend(data.values())
        self._values.extend(data.values())
        return self

    def on_conflict_do_nothing(self) -> "QueryBuilder":
        """设置冲突时不做任何操作"""
        self._conflict_action = "DO NOTHING"
        return self

    def on_conflict_update(self, update_data: Dict[str, Any]) -> "QueryBuilder":
        """
        设置冲突时更新

        Args:
            update_data: 更新数据字典

        Returns:
            QueryBuilder: 链式调用
        """
        self._conflict_action = "DO UPDATE SET"
        self._conflict_updates = []
        for field, value in update_data.items():
            self._conflict_updates.append(f"{field} = %s")
            self._values.append(value)
        return self

    def returning(self, *fields: str) -> "QueryBuilder":
        """
        设置RETURNING字段

        Args:
            *fields: 返回字段列表

        Returns:
            QueryBuilder: 链式调用
        """
        self._returning_fields.extend(fields)
        return self

    # ==================== UPDATE 查询构建 ====================

    def update(self, table: str) -> "QueryBuilder":
        """
        开始UPDATE查询

        Args:
            table: 表名

        Returns:
            QueryBuilder: 链式调用
        """
        self._query_type = "UPDATE"
        self._table_name = table
        return self

    def set(self, data: Dict[str, Any]) -> "QueryBuilder":
        """
        设置更新数据

        Args:
            data: 更新数据字典

        Returns:
            QueryBuilder: 链式调用
        """
        if not hasattr(self, "_update_fields"):
            self._update_fields = []

        for field, value in data.items():
            self._update_fields.append(f"{field} = %s")
            self._values.append(value)
        return self

    # ==================== DELETE 查询构建 ====================

    def delete_from(self, table: str) -> "QueryBuilder":
        """
        开始DELETE查询

        Args:
            table: 表名

        Returns:
            QueryBuilder: 链式调用
        """
        self._query_type = "DELETE"
        self._table_name = table
        return self

    # ==================== 查询执行 ====================

    def build(self) -> Tuple[str, List[Any]]:
        """
        构建SQL查询

        Returns:
            Tuple[str, List[Any]]: SQL语句和参数列表
        """
        if not self._query_type:
            raise ValueError("查询类型未指定")

        if self._query_type == "SELECT":
            return self._build_select()
        elif self._query_type == "INSERT":
            return self._build_insert()
        elif self._query_type == "UPDATE":
            return self._build_update()
        elif self._query_type == "DELETE":
            return self._build_delete()
        else:
            raise ValueError(f"不支持的查询类型: {self._query_type}")

    def _build_select(self) -> Tuple[str, List[Any]]:
        """构建SELECT查询"""
        sql_parts = []

        # SELECT子句
        if self._select_fields:
            sql_parts.append(f"SELECT {', '.join(self._select_fields)}")
        else:
            sql_parts.append("SELECT *")

        # FROM子句
        if not self._table_name:
            raise ValueError("表名未指定")
        sql_parts.append(f"FROM {self._table_name}")

        # JOIN子句
        sql_parts.extend(self._joins)

        # WHERE子句
        if self._where_conditions:
            sql_parts.append(f"WHERE {' AND '.join(self._where_conditions)}")

        # GROUP BY子句
        if self._group_by_fields:
            sql_parts.append(f"GROUP BY {', '.join(self._group_by_fields)}")

        # HAVING子句
        if self._having_conditions:
            sql_parts.append(f"HAVING {' AND '.join(self._having_conditions)}")

        # ORDER BY子句
        if self._order_by_fields:
            sql_parts.append(f"ORDER BY {', '.join(self._order_by_fields)}")

        # LIMIT子句
        if self._limit_count is not None:
            sql_parts.append(f"LIMIT {self._limit_count}")

        # OFFSET子句
        if self._offset_count is not None:
            sql_parts.append(f"OFFSET {self._offset_count}")

        return " ".join(sql_parts), self._values.copy()

    def _build_insert(self) -> Tuple[str, List[Any]]:
        """构建INSERT查询"""
        if not self._table_name:
            raise ValueError("表名未指定")
        if not hasattr(self, "_insert_fields"):
            raise ValueError("插入数据未指定")

        sql_parts = [
            f"INSERT INTO {self._table_name}",
            f"({', '.join(self._insert_fields)})",
            f"VALUES ({', '.join(['%s'] * len(self._insert_values))})",
        ]

        # 冲突处理
        if hasattr(self, "_conflict_action"):
            sql_parts.append(f"ON CONFLICT {self._conflict_action}")
            if hasattr(self, "_conflict_updates"):
                sql_parts.append(", ".join(self._conflict_updates))

        # RETURNING子句
        if self._returning_fields:
            sql_parts.append(f"RETURNING {', '.join(self._returning_fields)}")

        return " ".join(sql_parts), self._values.copy()

    def _build_update(self) -> Tuple[str, List[Any]]:
        """构建UPDATE查询"""
        if not self._table_name:
            raise ValueError("表名未指定")
        if not hasattr(self, "_update_fields"):
            raise ValueError("更新数据未指定")

        sql_parts = [
            f"UPDATE {self._table_name}",
            f"SET {', '.join(self._update_fields)}",
        ]

        # WHERE子句
        if self._where_conditions:
            sql_parts.append(f"WHERE {' AND '.join(self._where_conditions)}")

        return " ".join(sql_parts), self._values.copy()

    def _build_delete(self) -> Tuple[str, List[Any]]:
        """构建DELETE查询"""
        if not self._table_name:
            raise ValueError("表名未指定")

        sql_parts = [f"DELETE FROM {self._table_name}"]

        # WHERE子句
        if self._where_conditions:
            sql_parts.append(f"WHERE {' AND '.join(self._where_conditions)}")

        return " ".join(sql_parts), self._values.copy()

    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = self.connection_provider._get_connection()
        try:
            yield conn
        finally:
            self.connection_provider._return_connection(conn)

    def fetch_one(self) -> Optional[Dict[str, Any]]:
        """
        执行查询并返回单条记录

        Returns:
            Optional[Dict[str, Any]]: 查询结果
        """
        sql, params = self.build()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                return self._row_to_dict(cursor, row) if row else None
            finally:
                cursor.close()

    def fetch_all(self) -> List[Dict[str, Any]]:
        """
        执行查询并返回所有记录

        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        sql, params = self.build()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, params)
                rows = cursor.fetchall()
                return [self._row_to_dict(cursor, row) for row in rows]
            finally:
                cursor.close()

    def fetch_count(self) -> int:
        """
        执行COUNT查询

        Returns:
            int: 记录数量
        """
        original_select = self._select_fields.copy()

        # 临时修改为COUNT查询
        self._select_fields = ["COUNT(*)"]
        sql, params = self.build()

        # 恢复原始SELECT字段
        self._select_fields = original_select

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, params)
                row = cursor.fetchone()
                return row[0] if row else 0
            finally:
                cursor.close()

    def execute(self) -> int:
        """
        执行INSERT/UPDATE/DELETE查询

        Returns:
            int: 受影响的行数
        """
        sql, params = self.build()

        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(sql, params)
                affected_rows = cursor.rowcount
                conn.commit()

                # 处理RETURNING结果
                if self._returning_fields and self._query_type == "INSERT":
                    row = cursor.fetchone()
                    return row if row else affected_rows

                return affected_rows
            except Exception:
                conn.rollback()
                raise
            finally:
                cursor.close()

    def _row_to_dict(self, cursor, row) -> Dict[str, Any]:
        """
        将查询结果行转换为字典

        Args:
            cursor: 数据库游标
            row: 查询结果行

        Returns:
            Dict[str, Any]: 字典形式的结果
        """
        if not row:
            return {}

        columns = [desc[0] for desc in cursor.description]
        result = {}

        for i, value in enumerate(row):
            if i < len(columns):
                # 处理日期时间类型
                if isinstance(value, (datetime, date)):
                    if isinstance(value, datetime):
                        result[columns[i]] = value.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        result[columns[i]] = value.strftime("%Y-%m-%d")
                else:
                    result[columns[i]] = value

        return result


class QueryExecutor:
    """
    查询执行器
    提供更高级的查询执行和结果处理功能
    """

    def __init__(self, connection_provider):
        self.connection_provider = connection_provider
        self.query_builder = QueryBuilder(connection_provider)

    def create_query(self) -> QueryBuilder:
        """创建新的查询构建器"""
        return QueryBuilder(self.connection_provider)

    def execute_transaction(self, queries: List[Tuple[str, List[Any]]]) -> bool:
        """
        执行事务

        Args:
            queries: 查询列表，每个元素为 (sql, params) 元组

        Returns:
            bool: 是否成功
        """
        with self.query_builder._get_connection() as conn:
            cursor = conn.cursor()
            try:
                for sql, params in queries:
                    cursor.execute(sql, params)
                conn.commit()
                return True
            except Exception as e:
                conn.rollback()
                logger.error(f"事务执行失败: {e}")
                return False
            finally:
                cursor.close()

    def batch_insert(self, table: str, data_list: List[Dict[str, Any]]) -> int:
        """
        批量插入数据

        Args:
            table: 表名
            data_list: 数据列表

        Returns:
            int: 插入的记录数
        """
        if not data_list:
            return 0

        # 构建批量插入SQL
        fields = list(data_list[0].keys())
        placeholders = ",".join(["%s"] * len(fields))

        sql = f"""
            INSERT INTO {table} ({", ".join(fields)})
            VALUES ({placeholders})
        """

        values = [[item[field] for field in fields] for item in data_list]

        with self.query_builder._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.executemany(sql, values)
                affected_rows = cursor.rowcount
                conn.commit()
                return affected_rows
            except Exception as e:
                conn.rollback()
                logger.error(f"批量插入失败: {e}")
                raise
            finally:
                cursor.close()
