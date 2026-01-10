"""
Brute Force Pattern Matching Algorithm for Quantitative Trading.

This module implements the Brute Force (BF) pattern matching algorithm,
which exhaustively searches for patterns in financial time series data.
While simple and straightforward, it's suitable for small datasets and
serves as a baseline for more sophisticated algorithms.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd

from .base import PatternMatchingAlgorithm, Pattern, PatternMatch, PatternMatchResult
from src.algorithms.types import AlgorithmType
from src.algorithms.metadata import AlgorithmFingerprint

logger = logging.getLogger(__name__)


class BruteForceAlgorithm(PatternMatchingAlgorithm):
    """
    Brute Force pattern matching algorithm for trading patterns.

    This algorithm performs exhaustive search by sliding a window over the
    data and comparing each window with the target patterns. It's simple,
    predictable, and serves as a baseline for evaluating more sophisticated
    algorithms. Best suited for small datasets or when exact matching is required.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.window_sizes: Dict[str, int] = {}

    async def find_patterns(
        self,
        data: Union[List[float], np.ndarray, pd.Series],
        pattern_ids: Optional[List[str]] = None,
        search_range: Optional[Tuple[int, int]] = None,
        min_confidence: float = 0.8,
    ) -> List[PatternMatchResult]:
        """
        Find patterns using brute force search.

        Args:
            data: Time series data to search in
            pattern_ids: Specific patterns to search for (None = all patterns)
            search_range: Range of indices to search (None = entire data)
            min_confidence: Minimum confidence threshold for matches

        Returns:
            List of pattern match results
        """
        start_time = time.time()

        if not await self.validate_input(data):
            raise ValueError("Invalid input data")

        # Convert data to numpy array
        if isinstance(data, pd.Series):
            data_array = data.values
        elif isinstance(data, list):
            data_array = np.array(data)
        else:
            data_array = data

        # Set search range
        if search_range is None:
            search_start, search_end = 0, len(data_array)
        else:
            search_start, search_end = search_range

        # Determine which patterns to search for
        target_patterns = pattern_ids or list(self.patterns.keys())
        if not target_patterns:
            logger.warning("No patterns available for matching")
            return []

        results = []

        for pattern_id in target_patterns:
            if pattern_id not in self.patterns:
                logger.warning(f"Pattern {pattern_id} not found")
                continue

            pattern = self.patterns[pattern_id]
            pattern_length = len(pattern.sequence)
            matches = []

            # Slide window over the data
            for i in range(search_start, search_end - pattern_length + 1):
                window = data_array[i : i + pattern_length]

                # Normalize both sequences for comparison
                normalized_window = self._normalize_sequence(window)
                normalized_pattern = self._normalize_sequence(pattern.sequence)

                # Calculate similarity
                confidence = self._calculate_similarity(normalized_window, normalized_pattern)

                if confidence >= max(min_confidence, pattern.min_confidence):
                    match = PatternMatch(
                        start_index=i,
                        end_index=i + pattern_length - 1,
                        pattern_length=pattern_length,
                        confidence=confidence,
                        matched_sequence=window.tolist(),
                        pattern_id=pattern_id,
                    )
                    matches.append(match)

            if matches:
                result = PatternMatchResult(
                    pattern_id=pattern_id,
                    matches=matches,
                    total_matches=len(matches),
                    execution_time=time.time() - start_time,
                    algorithm_used="brute_force",
                    gpu_used=self.gpu_enabled,
                    search_range=(search_start, search_end),
                )
                results.append(result)

                logger.info(f"Found {len(matches)} matches for pattern {pattern_id}")

        self.match_history.extend(results)
        return results

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the Brute Force algorithm."""
        base_info = super().get_algorithm_info()
        base_info.update(
            {
                "algorithm_variant": "brute_force",
                "complexity": "O(n*m*k)",  # n=data length, m=pattern length, k=patterns
                "strengths": ["Simple", "Exact matching", "No preprocessing"],
                "weaknesses": ["Slow for large datasets", "No optimizations", "High computational cost"],
                "best_use_case": "Small datasets, baseline comparison, exact pattern matching",
            }
        )
        return base_info

    def estimate_complexity(self, data_length: int, pattern_count: int, avg_pattern_length: int) -> Dict[str, Any]:
        """
        Estimate computational complexity for given parameters.

        Args:
            data_length: Length of data to search
            pattern_count: Number of patterns
            avg_pattern_length: Average pattern length

        Returns:
            Complexity estimates
        """
        operations = data_length * avg_pattern_length * pattern_count

        return {
            "estimated_operations": operations,
            "estimated_time_seconds": operations / 1e6,  # Rough estimate: 1M ops/sec
            "memory_usage_mb": (data_length + pattern_count * avg_pattern_length) * 8 / 1e6,
            "complexity_class": "O(n*m*k)",
            "recommendation": "Use for data_length < 10000" if data_length < 10000 else "Consider optimized algorithms",
        }

    # Required abstract method implementations from BaseAlgorithm
    async def train(self, data, config):
        """Pattern matching algorithms don't require training."""
        raise NotImplementedError("Pattern matching algorithms don't support training")

    async def predict(self, data, model):
        """Use find_patterns instead."""
        raise NotImplementedError("Use find_patterns method for pattern matching")

    def evaluate(self, predictions, actual):
        """Pattern matching evaluation is handled differently."""
        raise NotImplementedError("Pattern matching uses different evaluation metrics")
