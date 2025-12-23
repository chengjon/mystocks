"""
数据库访问模块
提供统一的数据库访问接口
"""

import structlog
from typing import List, Dict, Any
from .database_pool import DatabaseConnectionManager
from .exceptions import DataValidationError

logger = structlog.get_logger()


# 延迟初始化的数据库会话
_db_manager = None


async def get_db_manager():
    """获取数据库管理器"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseConnectionManager()
        await _db_manager.initialize()
    return _db_manager


async def get_postgresql_session():
    """
    获取PostgreSQL数据库会话

    Returns:
        DatabaseConnectionManager: 数据库连接管理器
    """
    return await get_db_manager()


# 数据库操作辅助函数
class DatabaseHelper:
    """数据库操作辅助类"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        """
        初始化数据库助手

        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager

    def validate_pagination(self, page: int = 1, page_size: int = 10) -> tuple:
        """
        验证分页参数

        Args:
            page: 页码
            page_size: 页大小

        Returns:
            tuple: (offset, limit)

        Raises:
            DataValidationError: 参数验证失败
        """
        if not isinstance(page, int) or page < 1:
            raise DataValidationError(
                message="Page must be a positive integer",
                code="INVALID_PAGE",
                severity="MEDIUM",
            )

        if not isinstance(page_size, int) or page_size < 1 or page_size > 100:
            raise DataValidationError(
                message="Page size must be an integer between 1 and 100",
                code="INVALID_PAGE_SIZE",
                severity="MEDIUM",
            )

        offset = (page - 1) * page_size
        return offset, page_size

    def build_where_clause(self, conditions: Dict[str, Any]) -> tuple:
        """
        构建WHERE子句

        Args:
            conditions: 条件字典

        Returns:
            tuple: (where_clause, params)
        """
        if not conditions:
            return "", []

        where_parts = []
        params = []

        for key, value in conditions.items():
            if value is None:
                continue

            if isinstance(value, (list, tuple)):
                # IN 查询
                placeholders = [f"${i + 1}" for i in range(len(value))]
                where_parts.append(f"{key} IN ({', '.join(placeholders)})")
                params.extend(value)
            elif isinstance(value, dict) and "operator" in value:
                # 自定义操作符
                operator = value["operator"]
                param_value = value["value"]
                where_parts.append(f"{key} {operator} ${len(params) + 1}")
                params.append(param_value)
            else:
                # 等值查询
                where_parts.append(f"{key} = ${len(params) + 1}")
                params.append(value)

        where_clause = " AND ".join(where_parts)
        return where_clause, params

    def build_order_by_clause(self, order_by: Dict[str, str]) -> str:
        """
        构建ORDER BY子句

        Args:
            order_by: 排序字段

        Returns:
            str: ORDER BY子句
        """
        if not order_by:
            return ""

        order_parts = []
        for field, direction in order_by.items():
            if direction.upper() in ["ASC", "DESC"]:
                order_parts.append(f"{field} {direction}")
            else:
                order_parts.append(f"{field} ASC")

        return " ORDER BY " + ", ".join(order_parts)


# 数据库查询构建器
class DatabaseQueryBuilder:
    """数据库查询构建器"""

    def __init__(self, table_name: str):
        """
        初始化查询构建器

        Args:
            table_name: 表名
        """
        self.table_name = table_name
        self.select_fields = ["*"]
        self.where_conditions = {}
        self.order_by = {}
        self.limit = None
        self.offset = None

    def select(self, *fields):
        """
        选择字段

        Args:
            *fields: 字段名

        Returns:
            DatabaseQueryBuilder: 查询构建器
        """
        if fields:
            self.select_fields = list(fields)
        else:
            self.select_fields = ["*"]
        return self

    def where(self, **conditions):
        """
        添加WHERE条件

        Args:
            **conditions: 条件

        Returns:
            DatabaseQueryBuilder: 查询构建器
        """
        self.where_conditions.update(conditions)
        return self

    def order(self, **order_by):
        """
        添加排序

        Args:
            **order_by: 排序条件

        Returns:
            DatabaseQueryBuilder: 查询构建器
        """
        self.order_by.update(order_by)
        return self

    def paginate(self, page: int = 1, page_size: int = 10):
        """
        添加分页

        Args:
            page: 页码
            page_size: 页大小

        Returns:
            DatabaseQueryBuilder: 查询构建器
        """
        offset, limit = DatabaseHelper(None).validate_pagination(page, page_size)
        self.limit = limit
        self.offset = offset
        return self

    def build_select_query(self) -> tuple:
        """
        构建SELECT查询

        Returns:
            tuple: (query, params)
        """
        # SELECT部分
        select_clause = ", ".join(self.select_fields)

        # FROM部分
        from_clause = self.table_name

        # WHERE部分
        helper = DatabaseHelper(None)
        where_clause, params = helper.build_where_clause(self.where_conditions)

        # ORDER BY部分
        order_by_clause = helper.build_order_by_clause(self.order_by)

        # LIMIT和OFFSET部分
        limit_clause = ""
        if self.limit is not None:
            limit_clause = f" LIMIT {self.limit}"
        if self.offset is not None:
            limit_clause += f" OFFSET {self.offset}"

        # 组合查询
        query = f"SELECT {select_clause} FROM {from_clause}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += order_by_clause
        query += limit_clause

        return query, params

    async def execute(
        self, db_manager: DatabaseConnectionManager
    ) -> List[Dict[str, Any]]:
        """
        执行查询

        Args:
            db_manager: 数据库管理器

        Returns:
            List[Dict[str, Any]]: 查询结果
        """
        query, params = self.build_select_query()
        result = await db_manager.execute_query(query, params)
        return [dict(row) for row in result]


# 数据库操作装饰器
def with_db_connection(func):
    """
    数据库连接装饰器

    Args:
        func: 被装饰的函数

    Returns:
        function: 装饰后的函数
    """

    async def wrapper(*args, **kwargs):
        db_manager = await get_db_manager()
        return await func(*args, db_manager, **kwargs)

    return wrapper


# 批量操作
class BatchOperation:
    """批量操作"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        """
        初始化批量操作

        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.operations = []

    def insert(self, table: str, data: List[Dict[str, Any]]):
        """
        添加批量插入操作

        Args:
            table: 表名
            data: 数据列表
        """
        if not data:
            return

        columns = list(data[0].keys())
        placeholders = [f"${i + 1}" for i in range(len(columns))]

        query = f"""
            INSERT INTO {table} ({", ".join(columns)})
            VALUES ({", ".join(placeholders)})
        """

        for item in data:
            params = [item[col] for col in columns]
            self.operations.append(("insert", query, params))

    def update(self, table: str, data: List[Dict[str, Any]], where_key: str = "id"):
        """
        添加批量更新操作

        Args:
            table: 表名
            data: 数据列表
            where_key: 更新条件字段
        """
        if not data:
            return

        set_columns = [col for col in data[0].keys() if col != where_key]
        set_placeholders = [f"{col} = ${i + 2}" for i, col in enumerate(set_columns)]

        query = f"""
            UPDATE {table}
            SET {", ".join(set_placeholders)}
            WHERE {where_key} = $1
        """

        for item in data:
            params = [item[where_key]] + [item[col] for col in set_columns]
            self.operations.append(("update", query, params))

    async def execute(self) -> Dict[str, int]:
        """
        执行批量操作

        Returns:
            Dict[str, int]: 操作结果统计
        """
        results = {
            "total": len(self.operations),
            "success": 0,
            "failed": 0,
            "errors": [],
        }

        for operation_type, query, params in self.operations:
            try:
                await self.db_manager.execute_command(query, params)
                results["success"] += 1
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(
                    {
                        "operation": operation_type,
                        "query": query,
                        "params": params,
                        "error": str(e),
                    }
                )

        return results


# 事务管理
class DatabaseTransaction:
    """数据库事务"""

    def __init__(self, db_manager: DatabaseConnectionManager):
        """
        初始化事务

        Args:
            db_manager: 数据库管理器
        """
        self.db_manager = db_manager
        self.connection = None

    async def __aenter__(self):
        """进入事务"""
        self.connection = await self.db_manager.get_connection()
        await self.connection.execute("BEGIN")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """退出事务"""
        if exc_type is None:
            await self.connection.execute("COMMIT")
        else:
            await self.connection.execute("ROLLBACK")

        if self.connection:
            await self.db_manager.pool.release(self.connection)

    async def execute(self, query: str, params: tuple = None):
        """在事务中执行查询"""
        if params:
            return await self.connection.fetch(query, *params)
        else:
            return await self.connection.fetch(query)

    async def execute_command(self, command: str, params: tuple = None):
        """在事务中执行命令"""
        if params:
            return await self.connection.execute(command, *params)
        else:
            return await self.connection.execute(command)
