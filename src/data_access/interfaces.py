#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
# pylint: disable=no-member  # TODO: 实现缺失的 GPU/业务方法
MyStocks 量化交易数据访问接口定义
提供统一的数据访问抽象接口

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-12-16
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd

# 导入核心模块
from src.core import (
    DataClassification,
)

logger = logging.getLogger("MyStocksDataAccess")


def _get_database_name_from_classification(classification: DataClassification) -> str:
    """
    从数据分类获取数据库名称 (US3架构简化)
    """
    mapping = {
        DataClassification.MARKET_DATA: "market_data",
        DataClassification.REFERENCE_DATA: "reference_data",
        DataClassification.DERIVATIVE_DATA: "derivative_data",
        DataClassification.TRADE_DATA: "trade_data",
        DataClassification.METADATA: "metadata",
    }
    return mapping.get(classification, "unknown")


class IDataAccessLayer(ABC):
    """
    数据访问层抽象接口

    US3架构的核心接口，提供5大数据类型的统一访问方法：
    1. 市场数据 (Market Data) - 股票价格、成交量、技术指标等
    2. 参考数据 (Reference Data) - 股票基本信息、行业分类等
    3. 衍生数据 (Derivative Data) - 财务指标、估值数据等
    4. 交易数据 (Trade Data) - 订单、成交记录等
    5. 元数据 (Metadata) - 数据源、更新时间等
    """

    @abstractmethod
    def get_data(
        self,
        classification: DataClassification,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        columns: Optional[List[str]] = None,
        filters: Optional[Dict] = None,
    ) -> pd.DataFrame:
        """
        获取数据的核心方法

        Args:
            classification: 数据分类
            symbol: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            columns: 需要的列
            filters: 过滤条件

        Returns:
            pd.DataFrame: 查询结果
        """

    @abstractmethod
    def save_data(
        self,
        classification: DataClassification,
        data: pd.DataFrame,
        symbol: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> bool:
        """
        保存数据的核心方法

        Args:
            classification: 数据分类
            data: 要保存的数据
            symbol: 股票代码 (可选)
            metadata: 元数据 (可选)

        Returns:
            bool: 保存是否成功
        """

    @abstractmethod
    def delete_data(
        self,
        classification: DataClassification,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
    ) -> bool:
        """
        删除数据的核心方法

        Args:
            classification: 数据分类
            symbol: 股票代码
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            bool: 删除是否成功
        """

    @abstractmethod
    def get_latest_timestamp(self, classification: DataClassification, symbol: str) -> Optional[datetime]:
        """
        获取最新时间戳

        Args:
            classification: 数据分类
            symbol: 股票代码

        Returns:
            Optional[datetime]: 最新时间戳
        """

    @abstractmethod
    def check_connection(self) -> bool:
        """
        检查数据库连接

        Returns:
            bool: 连接是否正常
        """

    # 市场数据专用方法
    def get_market_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        data_type: str = "kline",  # kline, tick, realtime
        frequency: str = "1d",  # 1m, 5m, 15m, 1h, 1d
    ) -> pd.DataFrame:
        """
        获取市场数据

        Args:
            symbol: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            data_type: 数据类型
            frequency: 数据频率

        Returns:
            pd.DataFrame: 市场数据
        """
        filters = {"data_type": data_type, "frequency": frequency}
        return self.get_data(
            DataClassification.MARKET_DATA,
            symbol,
            start_time,
            end_time,
            filters=filters,
        )

    # 参考数据专用方法
    def get_reference_data(
        self,
        symbol: Optional[str] = None,
        data_type: str = "stock_info",  # stock_info, industry, concept
        filters: Optional[Dict] = None,
    ) -> pd.DataFrame:
        """
        获取参考数据

        Args:
            symbol: 股票代码 (可选)
            data_type: 数据类型
            filters: 过滤条件

        Returns:
            pd.DataFrame: 参考数据
        """
        if filters is None:
            filters = {}
        filters["data_type"] = data_type

        # 对于参考数据，时间范围可选
        start_time = datetime(2020, 1, 1)  # 默认较早的时间
        end_time = datetime.now()

        return self.get_data(
            DataClassification.REFERENCE_DATA,
            symbol or "",
            start_time,
            end_time,
            filters=filters,
        )

    # 衍生数据专用方法
    def get_derivative_data(
        self,
        symbol: str,
        start_time: datetime,
        end_time: datetime,
        data_type: str = "financial",  # financial, valuation, technical
        indicators: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        """
        获取衍生数据

        Args:
            symbol: 股票代码
            start_time: 开始时间
            end_time: 结束时间
            data_type: 数据类型
            indicators: 指标列表

        Returns:
            pd.DataFrame: 衍生数据
        """
        filters = {"data_type": data_type, "indicators": indicators or []}
        return self.get_data(
            DataClassification.DERIVATIVE_DATA,
            symbol,
            start_time,
            end_time,
            filters=filters,
        )

    # 交易数据专用方法
    def get_trade_data(
        self,
        symbol: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        trade_type: str = "order",  # order, transaction, position
        filters: Optional[Dict] = None,
    ) -> pd.DataFrame:
        """
        获取交易数据

        Args:
            symbol: 股票代码 (可选)
            start_time: 开始时间 (可选)
            end_time: 结束时间 (可选)
            trade_type: 交易类型
            filters: 过滤条件

        Returns:
            pd.DataFrame: 交易数据
        """
        if filters is None:
            filters = {}
        filters["trade_type"] = trade_type

        # 交易数据的时间范围更灵活
        if start_time is None:
            start_time = datetime.now() - pd.Timedelta(days=30)
        if end_time is None:
            end_time = datetime.now()

        return self.get_data(
            DataClassification.TRADE_DATA,
            symbol or "",
            start_time,
            end_time,
            filters=filters,
        )

    # 元数据专用方法
    def get_metadata(
        self,
        data_type: str = "data_source",  # data_source, update_time, schema
        filters: Optional[Dict] = None,
    ) -> pd.DataFrame:
        """
        获取元数据

        Args:
            data_type: 数据类型
            filters: 过滤条件

        Returns:
            pd.DataFrame: 元数据
        """
        if filters is None:
            filters = {}
        filters["data_type"] = data_type

        # 元数据通常不需要时间范围
        start_time = datetime(2020, 1, 1)
        end_time = datetime.now()

        return self.get_data(DataClassification.METADATA, "", start_time, end_time, filters=filters)


class DataAccessError(Exception):
    """数据访问异常"""


class ConnectionError(DataAccessError):
    """连接异常"""


class DataNotFoundError(DataAccessError):
    """数据未找到异常"""


class InvalidParameterError(DataAccessError):
    """无效参数异常"""
