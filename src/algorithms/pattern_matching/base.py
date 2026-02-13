"""
Pattern Matching Base Classes for Quantitative Trading.

This module provides the base classes and interfaces for pattern matching
algorithms used in quantitative trading. These algorithms are designed to
identify recurring patterns in financial time series data.
"""

import logging
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from src.algorithms.base import GPUAcceleratedAlgorithm

logger = logging.getLogger(__name__)


@dataclass
class PatternMatch:
    """Represents a single pattern match result."""

    start_index: int
    end_index: int
    pattern_length: int
    confidence: float
    matched_sequence: List[float]
    pattern_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Pattern:
    """Represents a trading pattern to match."""

    id: str
    sequence: List[float]
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    min_confidence: float = 0.8
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if not self.sequence:
            raise ValueError("Pattern sequence cannot be empty")


@dataclass
class PatternMatchResult:
    """Result of pattern matching operation."""

    pattern_id: str
    matches: List[PatternMatch]
    total_matches: int
    execution_time: float
    algorithm_used: str
    gpu_used: bool
    search_range: Tuple[int, int]  # (start, end) indices in the data


class PatternMatchingAlgorithm(GPUAcceleratedAlgorithm):
    """
    Base class for pattern matching algorithms.

    Provides common functionality for algorithms that search for specific
    patterns in financial time series data. Supports GPU acceleration for
    large-scale pattern matching operations.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.patterns: Dict[str, Pattern] = {}
        self.match_history: List[PatternMatchResult] = []

    async def add_pattern(self, pattern: Pattern) -> bool:
        """
        Add a pattern to the algorithm's pattern library.

        Args:
            pattern: Pattern to add

        Returns:
            True if pattern was added successfully
        """
        try:
            if pattern.id in self.patterns:
                logger.warning("Pattern {pattern.id} already exists, updating")
            self.patterns[pattern.id] = pattern
            logger.info("Added pattern: {pattern.id} ({pattern.name})")
            return True
        except Exception:
            logger.error("Failed to add pattern {pattern.id}: %(e)s")
            return False

    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a pattern from the library.

        Args:
            pattern_id: ID of pattern to remove

        Returns:
            True if pattern was removed
        """
        if pattern_id in self.patterns:
            del self.patterns[pattern_id]
            logger.info("Removed pattern: %(pattern_id)s")
            return True
        return False

    def get_pattern(self, pattern_id: str) -> Optional[Pattern]:
        """Get a pattern by ID."""
        return self.patterns.get(pattern_id)

    def list_patterns(self) -> List[Dict[str, Any]]:
        """List all patterns in the library."""
        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "category": p.category,
                "length": len(p.sequence),
                "min_confidence": p.min_confidence,
            }
            for p in self.patterns.values()
        ]

    @abstractmethod
    async def find_patterns(
        self,
        data: Union[List[float], np.ndarray, pd.Series],
        pattern_ids: Optional[List[str]] = None,
        search_range: Optional[Tuple[int, int]] = None,
        min_confidence: float = 0.8,
    ) -> List[PatternMatchResult]:
        """
        Find patterns in the data.

        Args:
            data: Time series data to search in
            pattern_ids: Specific patterns to search for (None = all patterns)
            search_range: Range of indices to search (None = entire data)
            min_confidence: Minimum confidence threshold for matches

        Returns:
            List of pattern match results
        """

    async def validate_input(self, data: Union[List[float], np.ndarray, pd.Series]) -> bool:
        """Validate input data for pattern matching."""
        if data is None or len(data) == 0:
            return False

        # Convert to numpy array for validation
        if isinstance(data, pd.Series):
            data_array = data.values
        elif isinstance(data, list):
            data_array = np.array(data)
        else:
            data_array = data

        # Check for NaN values
        if np.isnan(data_array).any():
            logger.warning("Input data contains NaN values")
            return False

        # Check minimum length
        if len(data_array) < 3:
            logger.warning("Input data too short for pattern matching")
            return False

        return True

    def _normalize_sequence(self, sequence: Union[List[float], np.ndarray]) -> np.ndarray:
        """Normalize a sequence for comparison."""
        seq_array = np.array(sequence, dtype=np.float64)

        # Remove linear trend
        if len(seq_array) > 1:
            x = np.arange(len(seq_array))
            slope = np.polyfit(x, seq_array, 1)[0]
            trend = slope * x
            seq_array = seq_array - trend

        # Z-score normalization
        if np.std(seq_array) > 0:
            seq_array = (seq_array - np.mean(seq_array)) / np.std(seq_array)

        return seq_array

    def _calculate_similarity(self, seq1: np.ndarray, seq2: np.ndarray) -> float:
        """Calculate similarity between two sequences."""
        if len(seq1) != len(seq2):
            return 0.0

        # Pearson correlation coefficient
        if np.std(seq1) > 0 and np.std(seq2) > 0:
            correlation = np.corrcoef(seq1, seq2)[0, 1]
            return max(0.0, min(1.0, abs(correlation)))
        else:
            # If no variance, check for exact match
            return 1.0 if np.array_equal(seq1, seq2) else 0.0

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the pattern matching algorithm."""
        return {
            "algorithm_type": self.algorithm_type.value,
            "patterns_loaded": len(self.patterns),
            "gpu_enabled": self.gpu_enabled,
            "match_history_length": len(self.match_history),
            "supported_patterns": list(self.patterns.keys()),
            "metadata": self.metadata.__dict__,
        }
