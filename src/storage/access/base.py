#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 数据访问基础层

提供统一的数据访问接口和共享工具函数

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import pandas as pd
from datetime import datetime
from typing import Dict, List, Tuple
from abc import ABC, abstractmethod
import logging
from enum import Enum

# 导入核心模块
from src.core import DataClassification
from src.monitoring.monitoring_database import MonitoringDatabase

logger = logging.getLogger("MyStocksDataAccessBase")


class DatabaseType(Enum):
    """数据库类型枚举"""

    TDENGINE = "TDENGINE"
    POSTGRESQL = "POSTGRESQL"


class IDataAccessLayer(ABC):
    """数据访问层接口 - 所有数据访问器的抽象基类"""

    def __init__(self, monitoring_db: MonitoringDatabase):
        """
        初始化数据访问器

        Args:
            monitoring_db: 监控数据库实例
        """
        self.monitoring_db = monitoring_db

    @abstractmethod
    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """
        保存数据到数据库

        Args:
            data: 数据DataFrame
            classification: 数据分类
            table_name: 表名（可选）
            **kwargs: 其他参数

        Returns:
            bool: 保存是否成功
        """
        pass

    @abstractmethod
    def load_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> pd.DataFrame:
        """
        从数据库加载数据

        Args:
            classification: 数据分类
            table_name: 表名（可选）
            filters: 过滤条件
            **kwargs: 其他参数

        Returns:
            pd.DataFrame: 加载的数据
        """
        pass

    @abstractmethod
    def update_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        key_columns: List[str] = None,
        **kwargs,
    ) -> bool:
        """
        更新数据库中的数据

        Args:
            data: 数据DataFrame
            classification: 数据分类
            table_name: 表名（可选）
            key_columns: 主键列
            **kwargs: 其他参数

        Returns:
            bool: 更新是否成功
        """
        pass

    @abstractmethod
    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """
        删除数据库中的数据

        Args:
            classification: 数据分类
            table_name: 表名（可选）
            filters: 过滤条件
            **kwargs: 其他参数

        Returns:
            bool: 删除是否成功
        """
        pass


def get_database_name_from_classification(classification: DataClassification) -> str:
    """
    从数据分类获取数据库名称

    Args:
        classification: 数据分类

    Returns:
        数据库名称字符串
    """
    from src.core.data_manager import DataManager
    from src.core import DatabaseTarget

    data_manager = DataManager(enable_monitoring=False)
    target_db = data_manager.get_target_database(classification)

    # 将DatabaseTarget转换为数据库名称
    database_name_map = {
        DatabaseTarget.TDENGINE: "market_data",  # TDengine数据库名
        DatabaseTarget.POSTGRESQL: "mystocks",  # PostgreSQL数据库名
    }
    return database_name_map.get(target_db, "mystocks")


def normalize_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """
    标准化DataFrame，确保所有必要字段存在且格式正确

    Args:
        data: 原始数据DataFrame

    Returns:
        pd.DataFrame: 标准化后的数据
    """
    if data.empty:
        return data

    result = data.copy()

    # 确保created_at和updated_at字段存在
    if "created_at" not in result.columns:
        result["created_at"] = datetime.now()
    if "updated_at" not in result.columns:
        result["updated_at"] = datetime.now()

    # 处理NaN值
    result = result.fillna(None)

    # 确保时间戳格式正确
    timestamp_columns = ["timestamp", "ts", "created_at", "updated_at"]
    for col in timestamp_columns:
        if col in result.columns:
            result[col] = pd.to_datetime(result[col])

    return result


def validate_data_for_classification(data: pd.DataFrame, classification: DataClassification) -> Tuple[bool, List[str]]:
    """
    验证DataFrame是否符合特定数据分类的要求

    Args:
        data: 要验证的数据
        classification: 数据分类

    Returns:
        Tuple[bool, List[str]]: (验证是否通过, 错误消息列表)
    """
    errors = []

    if data.empty:
        errors.append("数据为空")
        return False, errors

    # 根据数据分类验证必要字段
    required_fields = get_required_fields_for_classification(classification)
    missing_fields = [f for f in required_fields if f not in data.columns]

    if missing_fields:
        errors.append(f"缺少必要字段: {missing_fields}")

    return len(errors) == 0, errors


def get_required_fields_for_classification(
    classification: DataClassification,
) -> List[str]:
    """
    获取特定数据分类的必要字段

    Args:
        classification: 数据分类

    Returns:
        List[str]: 必要字段列表
    """
    # 定义每个数据分类的必要字段
    required_fields_map = {
        DataClassification.TICK_DATA: ["ts", "symbol", "price", "volume"],
        DataClassification.MINUTE_KLINE: [
            "ts",
            "symbol",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
        DataClassification.DAILY_KLINE: [
            "symbol",
            "trade_date",
            "open",
            "high",
            "low",
            "close",
            "volume",
        ],
        DataClassification.REALTIME_QUOTES: ["symbol", "fetch_timestamp", "price"],
        DataClassification.TECHNICAL_INDICATORS: [
            "symbol",
            "calc_date",
            "indicator_name",
            "indicator_value",
        ],
        DataClassification.QUANTITATIVE_FACTORS: [
            "symbol",
            "calc_date",
            "factor_name",
            "factor_value",
        ],
        DataClassification.MODEL_OUTPUTS: [
            "model_id",
            "symbol",
            "calc_date",
            "output_value",
        ],
        DataClassification.TRADING_SIGNALS: [
            "signal_id",
            "symbol",
            "signal_type",
            "signal_time",
        ],
        DataClassification.ORDER_RECORDS: [
            "order_id",
            "symbol",
            "order_type",
            "order_status",
        ],
        DataClassification.TRANSACTION_RECORDS: [
            "transaction_id",
            "order_id",
            "trade_price",
            "trade_volume",
        ],
        DataClassification.POSITION_RECORDS: [
            "position_id",
            "symbol",
            "position_quantity",
            "position_value",
        ],
        DataClassification.ACCOUNT_FUNDS: ["account_id", "record_date", "cash_balance"],
    }

    return required_fields_map.get(classification, ["id", "created_at", "updated_at"])


def validate_time_series_data(data: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    验证时序数据的有效性

    Args:
        data: 要验证的时序数据

    Returns:
        Tuple[bool, List[str]]: (验证是否通过, 错误消息列表)
    """
    errors = []

    if data.empty:
        errors.append("数据为空")
        return False, errors

    # 检查时间戳列
    time_column = None
    for col in ["timestamp", "ts", "trade_date"]:
        if col in data.columns:
            time_column = col
            break

    if not time_column:
        errors.append("缺少时间戳列")
        return False, errors

    # 验证时间戳格式
    try:
        pd.to_datetime(data[time_column])
    except Exception as e:
        errors.append(f"时间戳格式错误: {e}")

    # 检查时间戳是否按时间顺序排列（可选）
    if time_column in data.columns:
        try:
            timestamps = pd.to_datetime(data[time_column])
            if not timestamps.is_monotonic_increasing:
                # 只有警告，不算错误
                logger.warning("时间戳未按顺序排列")
        except Exception:
            # 时间戳转换错误已经是上面的错误了，这里不需要重复添加
            pass

    return len(errors) == 0, errors
