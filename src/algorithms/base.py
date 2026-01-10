"""
Base algorithm framework for quantitative trading algorithms.

This module provides the abstract base class and common interfaces that all
quantitative trading algorithms must implement. It integrates with the existing
GPU acceleration framework and provides standardized training, prediction,
and evaluation methods.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
import pandas as pd
import numpy as np
from datetime import datetime

from .types import AlgorithmType


@dataclass
class AlgorithmMetadata:
    """Metadata for algorithm instances."""

    algorithm_type: AlgorithmType
    name: str
    version: str
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    author: Optional[str] = None
    tags: Optional[List[str]] = None


class BaseAlgorithm(ABC):
    """
    Abstract base class for all quantitative trading algorithms.

    This class defines the standard interface that all algorithms must implement,
    ensuring consistency across different algorithm types and enabling
    integration with the broader MyStocks system.
    """

    def __init__(self, metadata: AlgorithmMetadata):
        self.metadata = metadata
        self.is_trained = False
        self.training_metrics = {}
        self.gpu_context = None

    @property
    def algorithm_type(self) -> AlgorithmType:
        """Get the algorithm type."""
        return self.metadata.algorithm_type

    @property
    def name(self) -> str:
        """Get the algorithm name."""
        return self.metadata.name

    @abstractmethod
    async def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train the algorithm on historical data.

        Args:
            data: Training data as pandas DataFrame
            config: Training configuration parameters

        Returns:
            Dictionary containing trained model and training metrics
        """
        pass

    @abstractmethod
    async def predict(self, data: pd.DataFrame, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using trained model.

        Args:
            data: Input data for prediction
            model: Trained model from train() method

        Returns:
            Dictionary containing predictions and confidence scores
        """
        pass

    @abstractmethod
    def evaluate(self, predictions: Dict[str, Any], actual: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate algorithm performance.

        Args:
            predictions: Predictions from predict() method
            actual: Actual values for comparison

        Returns:
            Dictionary containing evaluation metrics
        """
        pass

    async def validate_input(self, data: pd.DataFrame) -> bool:
        """
        Validate input data format and requirements.

        Args:
            data: Input data to validate

        Returns:
            True if data is valid, False otherwise
        """
        if data.empty:
            return False
        return True

    def get_metadata(self) -> AlgorithmMetadata:
        """Get algorithm metadata."""
        return self.metadata

    def update_metadata(self, **kwargs):
        """Update algorithm metadata."""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)
        self.metadata.updated_at = datetime.now()

    def reset(self):
        """Reset algorithm to untrained state."""
        self.is_trained = False
        self.training_metrics = {}


class GPUAcceleratedAlgorithm(BaseAlgorithm):
    """
    Base class for GPU-accelerated algorithms.

    This class extends BaseAlgorithm with GPU-specific functionality,
    integrating with the existing GPU resource management system.
    """

    def __init__(self, metadata: AlgorithmMetadata):
        super().__init__(metadata)
        self.gpu_enabled = True
        self.gpu_memory_limit = None

    async def initialize_gpu_context(self):
        """Initialize GPU context for algorithm execution."""
        # Integration with existing GPU framework would go here
        pass

    async def release_gpu_context(self):
        """Release GPU resources."""
        pass

    def set_gpu_memory_limit(self, limit_mb: int):
        """Set GPU memory limit for this algorithm."""
        self.gpu_memory_limit = limit_mb

    async def fallback_to_cpu(self) -> bool:
        """
        Fallback to CPU execution if GPU is unavailable.

        Returns:
            True if fallback was successful
        """
        self.gpu_enabled = False
        return True
