from __future__ import annotations

"""数据访问层 - 接口定义"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, List

import pandas as pd
from src.core import DataClassification

logger = logging.getLogger(__name__)


_TDENGINE_CLASSIFICATIONS = {
    DataClassification.TICK_DATA,
    DataClassification.MINUTE_KLINE,
    DataClassification.DEPTH_DATA,
    DataClassification.ORDER_BOOK_DEPTH,
    DataClassification.LEVEL2_SNAPSHOT,
    DataClassification.INDEX_QUOTES,
}


def _get_database_name_from_classification(classification: DataClassification) -> str:
    """
    从数据分类获取数据库名称 (US3架构简化)

    Args:
        classification: 数据分类

    Returns:
        数据库名称字符串
    """
    if classification in _TDENGINE_CLASSIFICATIONS:
        return "market_data"
    return "mystocks"


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

    @abstractmethod
    def load_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> pd.DataFrame:
        """加载数据"""

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

    @abstractmethod
    def delete_data(
        self,
        classification: DataClassification,
        table_name: str = None,
        filters: Dict = None,
        **kwargs,
    ) -> bool:
        """删除数据"""

