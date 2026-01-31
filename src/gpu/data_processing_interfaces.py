from abc import ABC, abstractmethod
from typing import Any, Dict, List

import pandas as pd


class IDataProcessor(ABC):
    """
    数据处理器接口
    定义了数据处理的核心功能，允许CPU和GPU实现共享同一接口
    """

    @abstractmethod
    def process_batch(self, batch_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        处理一批数据。
        Args:
            batch_data: 包含数据点的字典列表。
        Returns:
            处理后的数据字典列表。
        """

    @abstractmethod
    def compute_features(self, historical_data: List[Dict], feature_types: List[str]) -> Dict[str, float]:
        """
        计算给定历史数据的特征。
        Args:
            historical_data: 历史数据字典列表。
            feature_types: 要计算的特征类型列表。
        Returns:
            计算出的特征字典。
        """

    @abstractmethod
    def load_and_preprocess(self, data: pd.DataFrame) -> Dict[str, Any]:
        """
        加载并预处理数据。
        Args:
            data: 输入的Pandas DataFrame。
        Returns:
            包含处理后数据和相关元数据的字典。
        """
