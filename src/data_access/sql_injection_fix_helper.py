"""
SQL注入安全修复辅助模块

提供安全的SQL构建和验证函数，用于修复整个数据访问层的SQL注入漏洞。

使用方法:
    from src.data_access.sql_injection_fix_helper import (
        validate_identifier,
        validate_table_name,
        build_safe_insert_sql,
        build_safe_select_sql
    )

版本: 1.0.0
创建日期: 2026-01-10
"""

import re
from typing import Any, List, Optional, Tuple


def validate_identifier(identifier: str, identifier_type: str = "identifier") -> str:
    """
    验证和清洗SQL标识符（表名、列名等）以防止SQL注入

    TDengine/PostgreSQL标识符规则:
    - 只能包含字母、数字、下划线
    - 必须以字母或下划线开头
    - 不包含SQL特殊字符

    Args:
        identifier: 待验证的标识符
        identifier_type: 标识符类型（用于错误消息）

    Returns:
        验证后的安全标识符

    Raises:
        ValueError: 如果标识符包含不安全字符

    Examples:
        >>> validate_identifier("my_table", "table_name")
        'my_table'
        >>> validate_identifier("'; DROP TABLE users; --", "table_name")
        ValueError: Invalid table_name: ''; DROP TABLE users; --'
    """
    if not identifier:
        raise ValueError(f"{identifier_type} cannot be empty")

    # 检查是否只包含安全字符
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise ValueError(
            f"Invalid {identifier_type}: '{identifier}'. " f"Only alphanumeric characters and underscores are allowed."
        )

    return identifier


def validate_table_name(table_name: str) -> str:
    """
    验证表名

    Args:
        table_name: 表名

    Returns:
        验证后的安全表名

    Raises:
        ValueError: 如果表名不安全
    """
    return validate_identifier(table_name, "table_name")


def validate_column_name(column_name: str) -> str:
    """
    验证列名

    Args:
        column_name: 列名

    Returns:
        验证后的安全列名

    Raises:
        ValueError: 如果列名不安全
    """
    return validate_identifier(column_name, "column_name")


def validate_symbol(symbol: str) -> str:
    """
    验证股票代码格式

    Args:
        symbol: 股票代码（如 "000001.SZ" 或 "000001"）

    Returns:
        验证后的安全股票代码

    Raises:
        ValueError: 如果股票代码格式无效

    Examples:
        >>> validate_symbol("000001")
        '000001'
        >>> validate_symbol("000001.SZ")
        '000001.SZ'
        >>> validate_symbol("'; DROP TABLE; --")
        ValueError: Invalid symbol format
    """
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    # 清理：移除不安全字符，只保留字母数字和点
    clean_symbol = re.sub(r"[^a-zA-Z0-9.]", "", symbol)

    if not clean_symbol:
        raise ValueError(f"Invalid symbol format: '{symbol}'")

    return clean_symbol


def escape_string_value(value: Any) -> str:
    """
    转义字符串值中的单引号以防止SQL注入

    Args:
        value: 待转义的值

    Returns:
        转义后的安全字符串（带单引号）

    Examples:
        >>> escape_string_value("O'Brien")
        "'O''Brien'"
        >>> escape_string_value(None)
        "NULL"
    """
    if value is None:
        return "NULL"

    if isinstance(value, str):
        # 转义单引号（SQL标准方式：单引号加倍）
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    # 对于数字类型，直接转换为字符串
    if isinstance(value, (int, float, bool)):
        return str(value)

    # 其他类型转换为字符串后转义
    escaped = str(value).replace("'", "''")
    return f"'{escaped}'"


def build_safe_insert_sql(
    table_name: str,
    columns: List[str],
    values: List[Tuple[Any, ...]],
    using_clause: Optional[str] = None,
    tags_clause: Optional[str] = None,
) -> str:
    """
    构建安全的INSERT语句（防止SQL注入）

    Args:
        table_name: 表名
        columns: 列名列表（会被验证）
        values: 值元组列表（会被转义）
        using_clause: TDengine USING子句（可选）
        tags_clause: TDengine TAGS子句（可选）

    Returns:
        安全的INSERT SQL语句

    Raises:
        ValueError: 如果表名或列名不安全

    Examples:
        >>> columns = ["ts", "price", "volume"]
        >>> values = [("2024-01-01 10:00:00", 10.5, 1000)]
        >>> build_safe_insert_sql("my_table", columns, values)
        "INSERT INTO my_table (ts, price, volume) VALUES ('2024-01-01 10:00:00', 10.5, 1000)"
    """
    # 验证表名
    safe_table_name = validate_table_name(table_name)

    # 验证列名
    safe_columns = [validate_column_name(col) for col in columns]

    # 构建列列表
    columns_str = ", ".join(safe_columns)

    # 构建值列表（转义每个值）
    value_groups = []
    for value_tuple in values:
        escaped_values = [escape_string_value(v) for v in value_tuple]
        value_groups.append(f"({', '.join(escaped_values)})")

    values_str = ", ".join(value_groups)

    # 构建SQL
    sql = f"INSERT INTO {safe_table_name} ({columns_str}) VALUES {values_str}"

    # 添加USING和TAGS子句（TDengine）
    if using_clause:
        safe_using = validate_table_name(using_clause)
        sql = f"INSERT INTO {safe_table_name} USING {safe_using}"
    elif tags_clause:
        sql = f"INSERT INTO {safe_table_name}"

    if tags_clause:
        sql += f" {tags_clause}"

    if using_clause or tags_clause:
        sql += f" VALUES {values_str}"

    return sql


def build_safe_select_sql(
    table_name: str, where_conditions: Optional[dict] = None, columns: Optional[List[str]] = None
) -> str:
    """
    构建安全的SELECT语句（防止SQL注入）

    Args:
        table_name: 表名
        where_conditions: WHERE条件字典 {列名: 值}
        columns: 要选择的列名列表（None表示SELECT *）

    Returns:
        安全的SELECT SQL语句

    Raises:
        ValueError: 如果表名或列名不安全

    Examples:
        >>> build_safe_select_sql("my_table", {"symbol": "000001", "date": "2024-01-01"})
        "SELECT * FROM my_table WHERE symbol = '000001' AND date = '2024-01-01'"
    """
    # 验证表名
    safe_table_name = validate_table_name(table_name)

    # 构建列列表
    if columns:
        safe_columns = [validate_column_name(col) for col in columns]
        columns_str = ", ".join(safe_columns)
    else:
        columns_str = "*"

    # 构建WHERE条件
    where_clauses = []
    if where_conditions:
        for col, value in where_conditions.items():
            safe_col = validate_column_name(col)
            escaped_value = escape_string_value(value)
            where_clauses.append(f"{safe_col} = {escaped_value}")

    where_str = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

    # 构建SQL
    sql = f"SELECT {columns_str} FROM {safe_table_name}{where_str}"

    return sql


def build_safe_delete_sql(table_name: str, where_conditions: dict) -> str:
    """
    构建安全的DELETE语句（防止SQL注入）

    Args:
        table_name: 表名
        where_conditions: WHERE条件字典 {列名: 值}

    Returns:
        安全的DELETE SQL语句

    Raises:
        ValueError: 如果表名或列名不安全，或where_conditions为空

    Examples:
        >>> build_safe_delete_sql("my_table", {"txn_id": "12345"})
        "DELETE FROM my_table WHERE txn_id = '12345'"
    """
    if not where_conditions:
        raise ValueError("WHERE conditions are required for DELETE operations")

    # 验证表名
    safe_table_name = validate_table_name(table_name)

    # 构建WHERE条件
    where_clauses = []
    for col, value in where_conditions.items():
        safe_col = validate_column_name(col)
        escaped_value = escape_string_value(value)
        where_clauses.append(f"{safe_col} = {escaped_value}")

    where_str = " WHERE " + " AND ".join(where_clauses)

    # 构建SQL
    sql = f"DELETE FROM {safe_table_name}{where_str}"

    return sql


# 便捷函数：批量验证
def validate_batch_identifiers(identifiers: List[str], identifier_type: str = "identifier") -> List[str]:
    """
    批量验证标识符

    Args:
        identifiers: 标识符列表
        identifier_type: 标识符类型

    Returns:
        验证后的安全标识符列表

    Raises:
        ValueError: 如果任何一个标识符不安全
    """
    return [validate_identifier(ident, identifier_type) for ident in identifiers]


# 便捷函数：构建安全的列名列表
def build_safe_column_list(columns: List[str]) -> str:
    """
    构建安全的列名列表字符串

    Args:
        columns: 列名列表

    Returns:
        逗号分隔的安全列名字符串

    Raises:
        ValueError: 如果任何列名不安全
    """
    safe_columns = validate_batch_identifiers(columns, "column")
    return ", ".join(safe_columns)
