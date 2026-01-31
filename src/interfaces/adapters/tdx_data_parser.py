"""
TDX数据解析器 - 从 tdx_adapter.py 拆分
职责：TDX协议数据解析、格式转换、验证
遵循 TDD 原则：仅实现满足测试的最小功能
"""

import logging
from typing import Any, Dict, List

import pandas as pd

# 设置日志
logger = logging.getLogger(__name__)


class TdxDataParser:
    """TDX数据解析器 - 专注于数据解析和格式转换"""


def __init__(self):
    """初始化TDX数据解析器"""
    self.required_columns = ["time", "open", "high", "low", "close", "volume"]


def validate_kline_data(self, data: pd.DataFrame) -> pd.DataFrame:
    """
    验证K线数据

    Args:
        data: 原始K线数据

    Returns:
        pd.DataFrame: 验证后的数据
    """
    if data is None or data.empty:
        return pd.DataFrame()

    # 检查必要的列
    if not all(col in data.columns for col in self.required_columns):
        logger.warning("Missing required columns. Available: %s", list(data.columns))
        return pd.DataFrame()

    # 验证数据逻辑
    validated_data = data.copy()

    # 检查价格逻辑：high >= max(open, close), low <= min(open, close)
    valid_rows = []
    for idx, row in validated_data.iterrows():
        if (
            row["high"] >= max(row["open"], row["close"])
            and row["low"] <= min(row["open"], row["close"])
            and row["volume"] >= 0
        ):
            valid_rows.append(True)
        else:
            logger.warning("Invalid data at row %s: %s", idx, dict(row))
            valid_rows.append(False)

    validated_data = validated_data[valid_rows]
    return validated_data.reset_index(drop=True)


def parse_kline_response(self, response: Dict[str, Any]) -> pd.DataFrame:
    """
    解析K线响应

    Args:
        response: TDX K线响应

    Returns:
        pd.DataFrame: 解析后的K线数据
    """
    if not response or "data" not in response:
        logger.warning("Invalid response format")
        return pd.DataFrame()

    raw_data = response["data"]
    if not isinstance(raw_data, list):
        logger.warning("Response data is not a list")
        return pd.DataFrame()

    # 转换为DataFrame
    df = self.convert_to_dataframe(raw_data)
    return self.validate_kline_data(df)


def convert_to_dataframe(self, raw_data: List[Dict]) -> pd.DataFrame:
    """
    转换原始数据为DataFrame

    Args:
        raw_data: 原始数据列表

    Returns:
        pd.DataFrame: 转换后的DataFrame
    """
    if not raw_data:
        return pd.DataFrame()

    # 确保所有数据都有必要的字段
    processed_data = []
    for item in raw_data:
        if isinstance(item, dict):
            processed_item = {
                "time": item.get("time", 0),
                "open": float(item.get("open", 0)),
                "high": float(item.get("high", 0)),
                "low": float(item.get("low", 0)),
                "close": float(item.get("close", 0)),
                "volume": float(item.get("volume", 0)),
            }
            processed_data.append(processed_item)

    if not processed_data:
        return pd.DataFrame()

    df = pd.DataFrame(processed_data)

    # 按时间排序
    if "time" in df.columns:
        df = df.sort_values("time").reset_index(drop=True)

    return df


def normalize_symbol(self, symbol: str) -> str:
    """
    标准化股票代码

    Args:
        symbol: 原始股票代码

    Returns:
        str: 标准化后的股票代码
    """
    if not symbol or not isinstance(symbol, str):
        return ""

    # 移除前缀
    symbol = symbol.upper()

    # 移除交易所前缀
    if symbol.startswith("SH"):
        return symbol[2:]
    elif symbol.startswith("SZ"):
        return symbol[2:]

    return symbol


def validate_numeric_data(self, value: Any) -> float:
    """
    验证数值数据

    Args:
        value: 输入值

    Returns:
        float: 验证后的数值
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        logger.warning("Invalid numeric value: %s", value)
        return 0.0


def format_timestamp(self, timestamp: int) -> int:
    """
    格式化时间戳

    Args:
        timestamp: 时间戳

    Returns:
        int: 格式化后的时间戳
    """
    try:
        return int(timestamp)
    except (ValueError, TypeError):
        logger.warning("Invalid timestamp: %s", timestamp)
        return 0


def clean_data_dict(self, data_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    清理数据字典

    Args:
        data_dict: 原始数据字典

    Returns:
        Dict[str, Any]: 清理后的数据字典
    """
    cleaned = {}

    # 定义预期的键和它们的转换函数
    key_mapping = {
        "time": self.format_timestamp,
        "open": self.validate_numeric_data,
        "high": self.validate_numeric_data,
        "low": self.validate_numeric_data,
        "close": self.validate_numeric_data,
        "volume": self.validate_numeric_data,
    }

    for key, value in data_dict.items():
        if key in key_mapping:
            cleaned[key] = key_mapping[key](value)

    return cleaned
