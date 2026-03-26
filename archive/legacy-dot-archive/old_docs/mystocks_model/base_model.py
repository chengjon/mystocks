"""
BaseModel - Unified Model Interface

Provides a standard interface for all ML models (Random Forest, LightGBM, LSTM, etc.)

Purpose:
- Unified fit/predict interface
- Model persistence (save/load)
- Compatible with backtest system

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd
import numpy as np


class BaseModel(ABC):
    """
    Base Model Interface (Simplified)

    All ML models should inherit from this class and implement:
    - fit(): Train the model
    - predict(): Generate predictions
    - save_model(): Persist model to disk
    - load_model(): Load model from disk

    Example:
        >>> class MyModel(BaseModel):
        ...     def fit(self, X, y, **kwargs):
        ...         self.model.fit(X, y)
        ...         self.is_trained = True
        ...     def predict(self, X):
        ...         return self.model.predict(X)
    """

    def __init__(self):
        """Initialize base model"""
        self.is_trained = False
        self.model_name = self.__class__.__name__

    @abstractmethod
    def fit(self, X: pd.DataFrame, y: pd.Series, **kwargs) -> Dict[str, Any]:
        """
        Train the model

        Args:
            X: Feature matrix
            y: Target variable
            **kwargs: Additional training parameters

        Returns:
            Dict: Training metrics
        """
        pass

    @abstractmethod
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Generate predictions

        Args:
            X: Feature matrix

        Returns:
            np.ndarray: Predictions
        """
        pass

    @abstractmethod
    def save_model(self, file_path: str) -> None:
        """
        Save model to file

        Args:
            file_path: Save path
        """
        pass

    @abstractmethod
    def load_model(self, file_path: str) -> None:
        """
        Load model from file

        Args:
            file_path: Model file path
        """
        pass

    def is_fitted(self) -> bool:
        """Check if model is trained"""
        return self.is_trained

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        return {"model_name": self.model_name, "is_trained": self.is_trained}
