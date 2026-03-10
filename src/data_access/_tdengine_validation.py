from __future__ import annotations

import re


def validate_identifier(identifier: str, identifier_type: str = "identifier") -> str:
    """验证和清洗 SQL 标识符。"""
    dangerous_chars = ["`", "'", ";", "--", "/*", "*/", "\\"]
    for char in dangerous_chars:
        if char in identifier:
            raise ValueError(
                f"Invalid {identifier_type}: '{identifier}' contains dangerous character. "
                f"SQL injection attempt detected."
            )

    if not identifier:
        raise ValueError(f"{identifier_type} cannot be empty")

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", identifier):
        raise ValueError(
            f"Invalid {identifier_type}: '{identifier}'. Only alphanumeric characters and underscores are allowed."
        )

    return identifier



def validate_suffix(suffix: str, suffix_type: str = "suffix") -> str:
    """验证子表后缀。"""
    if not suffix:
        raise ValueError(f"{suffix_type} cannot be empty")

    dangerous_chars = ["`", "'", ";", "--", "/*", "*/", "\\"]
    for char in dangerous_chars:
        if char in suffix:
            raise ValueError(
                f"Invalid {suffix_type}: '{suffix}' contains dangerous character. "
                f"SQL injection attempt detected."
            )

    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", suffix):
        raise ValueError(
            f"Invalid {suffix_type}: '{suffix}'. Must start with a letter or underscore, "
            f"followed by alphanumeric characters or underscores only."
        )

    return suffix



def validate_table_name(table_name: str) -> str:
    """验证表名。"""
    return validate_identifier(table_name, "table_name")



def validate_symbol(symbol: str) -> str:
    """验证股票代码格式。"""
    if not symbol:
        raise ValueError("Symbol cannot be empty")

    clean_symbol = re.sub(r"[^a-zA-Z0-9.]", "", symbol)
    if not clean_symbol:
        raise ValueError(f"Invalid symbol format: '{symbol}'")

    return clean_symbol



def _get_subtable_name(self, super_table: str, symbol: str, suffix: str = "") -> str:
    """生成安全的子表名。"""
    clean_symbol = validate_symbol(symbol).lower().replace(".", "_").replace("-", "_")
    prefix = "k" if "kline" in super_table else "t"

    if suffix:
        clean_suffix = validate_suffix(suffix.lower(), "suffix")
        return f"{prefix}_{clean_symbol}_{clean_suffix}"
    return f"{prefix}_{clean_symbol}"
