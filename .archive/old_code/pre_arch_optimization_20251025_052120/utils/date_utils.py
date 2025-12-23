"""
日期处理工具
提供日期格式化和转换功能
"""

import datetime
from typing import Optional, Union


def normalize_date(date_str: Union[str, datetime.date, datetime.datetime]) -> str:
    """
    将各种格式的日期转换为标准格式 YYYY-MM-DD

    支持的输入格式:
    - YYYY-MM-DD (标准格式)
    - YYYYMMDD (紧凑格式)
    - YYYY/MM/DD (斜杠分隔)
    - datetime.date 对象
    - datetime.datetime 对象

    Args:
        date_str: 需要格式化的日期字符串或日期对象

    Returns:
        str: 格式化后的日期字符串 (YYYY-MM-DD)

    Raises:
        ValueError: 如果日期格式无法识别
    """
    # 如果是None，返回空字符串
    if date_str is None:
        return ""

    # 如果是日期对象，直接格式化
    if isinstance(date_str, (datetime.date, datetime.datetime)):
        return date_str.strftime("%Y-%m-%d")

    # 如果是字符串，尝试解析
    if isinstance(date_str, str):
        date_str = date_str.strip()

        # 已经是标准格式
        if len(date_str) == 10 and date_str[4] == "-" and date_str[7] == "-":
            return date_str

        # 紧凑格式 YYYYMMDD
        if len(date_str) == 8 and date_str.isdigit():
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

        # 斜杠分隔 YYYY/MM/DD
        if len(date_str) == 10 and date_str[4] == "/" and date_str[7] == "/":
            return date_str.replace("/", "-")

        # 尝试其他常见格式
        try:
            # 尝试解析各种格式
            for fmt in ["%Y-%m-%d", "%Y%m%d", "%Y/%m/%d", "%d-%m-%Y", "%m/%d/%Y"]:
                try:
                    dt = datetime.datetime.strptime(date_str, fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # 如果所有格式都失败，尝试使用dateutil库(如果可用)
            try:
                from dateutil import parser

                dt = parser.parse(date_str)
                return dt.strftime("%Y-%m-%d")
            except (ImportError, ValueError):
                pass

            raise ValueError(f"无法识别的日期格式: {date_str}")
        except Exception as e:
            raise ValueError(f"日期格式化失败: {date_str}, 错误: {str(e)}")

    raise ValueError(f"不支持的日期类型: {type(date_str)}")


def get_date_range(
    start_date: Union[str, datetime.date],
    end_date: Optional[Union[str, datetime.date]] = None,
    days: Optional[Union[int, str]] = None,
) -> tuple:
    """
    获取标准化的日期范围

    Args:
        start_date: 开始日期
        end_date: 结束日期 (如果提供了days参数，则忽略此参数)
        days: 从开始日期算起的天数 (可选)，可以是整数或字符串

    Returns:
        tuple: (标准化开始日期, 标准化结束日期)
    """
    # 标准化开始日期
    start = normalize_date(start_date)

    # 如果提供了天数，计算结束日期
    if days is not None:
        # 确保days是整数
        try:
            days_int = int(days)
        except (ValueError, TypeError):
            raise ValueError(f"天数必须是整数，收到的是: {days} (类型: {type(days)})")

        start_dt = datetime.datetime.strptime(start, "%Y-%m-%d")
        end_dt = start_dt + datetime.timedelta(days=days_int)
        end = end_dt.strftime("%Y-%m-%d")
    else:
        # 否则使用提供的结束日期
        end = (
            normalize_date(end_date)
            if end_date
            else datetime.datetime.now().strftime("%Y-%m-%d")
        )

    return start, end


def is_valid_date(date_str: str) -> bool:
    """
    检查日期字符串是否有效

    Args:
        date_str: 日期字符串

    Returns:
        bool: 日期是否有效
    """
    try:
        normalize_date(date_str)
        return True
    except ValueError:
        return False
