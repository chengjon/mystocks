"""股票搜索服务模块
支持多数据源：
- AKShare: A股数据和港股数据
- 统一搜索接口

迁移自 OpenStock 项目
"""

from datetime import datetime


def parse_datetime_to_timestamp(value) -> float:
    """将各种格式的日期时间转换为 Unix 时间戳

    Args:
        value: 日期时间值（可能是 datetime 对象、字符串或其他类型）

    Returns:
        float: Unix 时间戳

    """
    if isinstance(value, datetime):
        return value.timestamp()
    if isinstance(value, str):
        try:
            # 尝试解析常见的日期格式
            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d",
            ]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.timestamp()
                except ValueError:
                    continue
        except Exception:
            pass
    # 如果无法解析，返回当前时间戳
    return datetime.now().timestamp()


def normalize_stock_code(code: str, market: str = "cn") -> str:
    """Normalize stock code by adding exchange suffix if missing

    Args:
        code: 6-digit stock code (e.g., "600519" or "600519.SH")
        market: Market type ("cn" for A-share, "hk" for H-share)

    Returns:
        Normalized code with exchange suffix (e.g., "600519.SH")

    Raises:
        ValueError: If code format is invalid

    """
    import re

    # Remove whitespace and convert to uppercase
    code = code.strip().upper()

    # If already has exchange suffix, validate and return
    if re.match(r"^\d{6}\.(SH|SZ|HK)$", code):
        return code

    # Validate 6-digit code without suffix
    if not re.match(r"^\d{6}$", code):
        raise ValueError(f"Invalid stock code format: {code}. Expected 6 digits optionally followed by .SH/.SZ/.HK")

    # Auto-detect exchange for A-share
    if market in ["cn", "auto"]:
        first_digit = code[0]
        first_three = code[:3]

        # Shanghai Stock Exchange
        if first_three in ["600", "601", "603", "688"] or first_digit == "6":
            return f"{code}.SH"

        # Shenzhen Stock Exchange
        if first_three in ["000", "001", "002", "003", "300", "301"] or first_digit in ["0", "3"]:
            return f"{code}.SZ"

    # H-share (Hong Kong)
    if market == "hk":
        return f"{code}.HK"

    # Default to Shanghai if ambiguous
    return f"{code}.SH"


class StockSearchError(Exception):
    """股票搜索错误"""


class FinnhubAPIError(Exception):
    """Finnhub API 错误"""


