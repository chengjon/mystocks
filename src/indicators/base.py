from abc import ABC, abstractmethod
from typing import Dict, Any, Union, Optional
import pandas as pd
import numpy as np

class BaseIndicator(ABC):
    """
    Abstract base class for all indicators.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}

    @property
    def name(self) -> str:
        return self.config.get("indicator_name", "Unknown")

class BatchIndicator(BaseIndicator):
    """
    Interface for Batch (Vectorized) Indicators.
    Used primarily for backtesting and historical data analysis.
    """
    @abstractmethod
    def calculate(self, data: pd.DataFrame, **kwargs) -> pd.Series:
        """
        Calculate the indicator for the entire dataset.
        
        Args:
            data (pd.DataFrame): Input data (must contain required columns like 'close').
            **kwargs: Indicator parameters (e.g., period=14).
            
        Returns:
            pd.Series: The calculated indicator values. 
                       MUST align with the input DataFrame's index.
        """
        pass

class StreamingIndicator(BaseIndicator):
    """
    Interface for Streaming (Stateful) Indicators.
    Used primarily for realtime trading.
    """
    @abstractmethod
    def update(self, bar: Dict[str, float]) -> float:
        """
        Update the indicator with a new bar of data.
        
        Args:
            bar (Dict[str, float]): A dictionary containing the latest bar data
                                    (e.g., {'close': 10.5, 'high': 11.0, ...}).
            
        Returns:
            float: The latest calculated indicator value.
        """
        pass

    @abstractmethod
    def snapshot(self) -> Dict[str, Any]:
        """
        Get a snapshot of the current state.
        Used for system persistence/recovery.
        
        Returns:
            Dict[str, Any]: Serializable state dictionary.
        """
        pass

    @abstractmethod
    def load_snapshot(self, state: Dict[str, Any]):
        """
        Restore state from a snapshot.
        
        Args:
            state (Dict[str, Any]): The state dictionary to restore.
        """
        pass
