#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 数据访问层基础模块

统一数据访问层的接口定义和公共工具函数

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-11-25
"""

import pandas as pd
from typing import Dict, List
from abc import ABC, abstractmethod
import logging

from src.core import (
    DataClassification,
    DataManager,
)

logger = logging.getLogger("MyStocksDataAccess")


class IDataAccessLayer(ABC):
    """数据访问层接口"""

    @abstractmethod
    def save_data(
        self,
        data: pd.DataFrame,
        classification: DataClassification,
        table_name: str = None,
        **kwargs,
    ) -> bool:
        """保存数据"""
        pass

    @abstractmethod
    def load_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> pd.DataFrame:
        """加载数据"""
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
        """更新数据"""
        pass

    @abstractmethod
    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """删除数据"""
        pass


def normalize_dataframe(data: pd.DataFrame) -> pd.DataFrame:
    """
    标准化DataFrame，确保列名和数据类型一致

    Args:
        data: 原始DataFrame

    Returns:
        标准化后的DataFrame
    """
    if data.empty:
        return data

    # 创建副本
    normalized = data.copy()

    # 清理列名：移除空格和特殊字符
    normalized.columns = [str(col).strip().replace(" ", "_") for col in normalized.columns]

    # 数据类型转换
    for col in normalized.columns:
        # 如果列名包含"volume"，确保它是数字类型
        if "volume" in col.lower():
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0)
        # 如果列名包含"price"或"close"或"open"，确保它是浮点类型
        elif any(name in col.lower() for name in ["price", "amount", "close", "open", "high", "low"]):
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce").fillna(0.0)
        # 如果列名包含"timestamp"或"date"，确保它是datetime类型
        elif any(name in col.lower() for name in ["timestamp", "date", "time"]):
            normalized[col] = pd.to_datetime(normalized[col], errors="coerce")

    # 排序时间列（如果有）
    time_cols = [col for col in normalized.columns if "time" in col.lower() or "date" in col.lower()]
    if time_cols:
        for col in time_cols:
            if pd.api.types.is_datetime64_any_dtype(normalized[col]):
                normalized = normalized.sort_values(by=col)

    return normalized


def validate_time_series_data(data: pd.DataFrame) -> bool:
    """
    验证数据是否为有效的时序数据

    Args:
        data: 要验证的DataFrame

    Returns:
        bool: 是否为有效的时序数据
    """
    if data.empty:
        return False

    # 检查是否存在时间列
    time_cols = [col for col in data.columns if "time" in col.lower() or "date" in col.lower() or "ts" in col.lower()]
    if not time_cols:
        return False

    # 检查时间列的数据类型
    for col in time_cols:
        if not pd.api.types.is_datetime64_any_dtype(data[col]):
            return False

    return True


def get_database_name_from_classification(classification: DataClassification) -> str:
    """
    根据数据分类获取数据库名称

    Args:
        classification: 数据分类

    Returns:
        数据库名称
    """
    return DataManager().get_database_name(classification)
