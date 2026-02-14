"""数据访问层 - 接口定义"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)
def _get_database_name_from_classification(classification: DataClassification) -> str:
    """
    从数据分类获取数据库名称 (US3架构简化)

    Args:
        classification: 数据分类

    Returns:
        数据库名称字符串
    """
    target_db = _data_manager.get_target_database(classification)
    # 将DatabaseTarget转换为数据库名称
    database_name_map = {
        DatabaseTarget.TDENGINE: "market_data",  # TDengine数据库名
        DatabaseTarget.POSTGRESQL: "mystocks",  # PostgreSQL数据库名
    }
    return database_name_map.get(target_db, "mystocks")


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


