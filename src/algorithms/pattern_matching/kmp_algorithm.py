"""
Knuth-Morris-Pratt (KMP) Pattern Matching Algorithm for Quantitative Trading.

This module implements the KMP pattern matching algorithm, which achieves
linear time complexity O(n+m) by preprocessing the pattern to create a
prefix table that allows efficient skipping during the search process.
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


class KMPAlgorithm(PatternMatchingAlgorithm):
    """
    Knuth-Morris-Pratt pattern matching algorithm for trading patterns.

    KMP algorithm achieves O(n+m) time complexity by preprocessing the pattern
    to create a prefix table (also called failure function) that indicates how
    much to shift the pattern when a mismatch occurs. This makes it much more
    efficient than brute force for large datasets.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.prefix_tables: Dict[str, List[int]] = {}

    def _compute_prefix_table(self, pattern: np.ndarray) -> List[int]:
        """
        Compute the KMP prefix table (failure function).

        Args:
            pattern: Normalized pattern sequence

        Returns:
            Prefix table for the pattern
        """
        m = len(pattern)
        prefix_table = [0] * m
        j = 0  # Length of previous longest prefix suffix

        i = 1
        while i < m:
            if abs(pattern[i] - pattern[j]) < 1e-6:  # Approximate equality for floats
                j += 1
                prefix_table[i] = j
                i += 1
            else:
                if j != 0:
                    j = prefix_table[j - 1]
                else:
                    prefix_table[i] = 0
                    i += 1

        return prefix_table

    def _kmp_search(self, text: np.ndarray, pattern: np.ndarray, prefix_table: List[int]) -> List[int]:
        """
        Perform KMP search on the text.

        Args:
            text: Normalized text sequence to search in
            pattern: Normalized pattern sequence to find
            prefix_table: Precomputed prefix table for the pattern

        Returns:
            List of starting indices where pattern matches were found
        """
        n, m = len(text), len(pattern)
        matches = []

        i = 0  # Index for text
        j = 0  # Index for pattern

        while i < n:
            if abs(text[i] - pattern[j]) < 1e-6:  # Approximate match
                i += 1
                j += 1

                if j == m:
                    # Found a match
                    matches.append(i - j)
                    j = prefix_table[j - 1]  # Continue searching for overlapping matches
            else:
                if j != 0:
                    j = prefix_table[j - 1]
                else:
                    i += 1

        return matches

    async def add_pattern(self, pattern: Pattern) -> bool:
        """
        Add a pattern and precompute its prefix table.

        Args:
            pattern: Pattern to add

        Returns:
            True if pattern was added successfully
        """
        success = await super().add_pattern(pattern)
        if success:
            # Precompute prefix table for the pattern
            normalized_pattern = self._normalize_sequence(pattern.sequence)
            prefix_table = self._compute_prefix_table(normalized_pattern)
            self.prefix_tables[pattern.id] = prefix_table

            logger.info(f"Precomputed prefix table for pattern {pattern.id} (length: {len(prefix_table)})")

        return success

    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a pattern and its prefix table.

        Args:
            pattern_id: ID of pattern to remove

        Returns:
            True if pattern was removed
        """
        success = super().remove_pattern(pattern_id)
        if success and pattern_id in self.prefix_tables:
            del self.prefix_tables[pattern_id]
            logger.info(f"Removed prefix table for pattern {pattern_id}")

        return success

    async def find_patterns(
        self,
        data: Union[List[float], np.ndarray, pd.Series],
        pattern_ids: Optional[List[str]] = None,
        search_range: Optional[Tuple[int, int]] = None,
        min_confidence: float = 0.8,
    ) -> List[PatternMatchResult]:
        """
        Find patterns using KMP algorithm.

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

        # Normalize the entire data sequence once
        normalized_data = self._normalize_sequence(data_array)

        # Set search range
        if search_range is None:
            search_start, search_end = 0, len(normalized_data)
        else:
            search_start, search_end = search_range
            normalized_data = normalized_data[search_start:search_end]

        # Determine which patterns to search for
        target_patterns = pattern_ids or list(self.patterns.keys())
        if not target_patterns:
            logger.warning("No patterns available for matching")
            return []

        results = []

        for pattern_id in target_patterns:
            if pattern_id not in self.patterns or pattern_id not in self.prefix_tables:
                logger.warning(f"Pattern {pattern_id} not found or not preprocessed")
                continue

            pattern = self.patterns[pattern_id]
            prefix_table = self.prefix_tables[pattern_id]
            normalized_pattern = self._normalize_sequence(pattern.sequence)

            # Perform KMP search
            match_indices = self._kmp_search(normalized_data, normalized_pattern, prefix_table)

            matches = []
            for start_idx in match_indices:
                end_idx = start_idx + len(normalized_pattern) - 1
                confidence = 1.0  # KMP finds exact matches after normalization

                if confidence >= max(min_confidence, pattern.min_confidence):
                    # Convert back to original indices
                    original_start = search_start + start_idx
                    original_end = search_start + end_idx

                    match = PatternMatch(
                        start_index=original_start,
                        end_index=original_end,
                        pattern_length=len(pattern.sequence),
                        confidence=confidence,
                        matched_sequence=data_array[original_start : original_end + 1].tolist(),
                        pattern_id=pattern_id,
                    )
                    matches.append(match)

            if matches:
                result = PatternMatchResult(
                    pattern_id=pattern_id,
                    matches=matches,
                    total_matches=len(matches),
                    execution_time=time.time() - start_time,
                    algorithm_used="knuth_morris_pratt",
                    gpu_used=self.gpu_enabled,
                    search_range=(search_start, search_end),
                )
                results.append(result)

                logger.info(f"Found {len(matches)} matches for pattern {pattern_id} using KMP")

        self.match_history.extend(results)
        return results

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the KMP algorithm."""
        base_info = super().get_algorithm_info()
        base_info.update(
            {
                "algorithm_variant": "knuth_morris_pratt",
                "complexity": "O(n+m)",  # n=text length, m=pattern length
                "preprocessing_complexity": "O(m)",
                "strengths": ["Linear time complexity", "No backtracking", "Efficient for multiple searches"],
                "weaknesses": [
                    "Preprocessing overhead",
                    "Memory usage for prefix tables",
                    "Approximate matching less robust",
                ],
                "best_use_case": "Large datasets, exact pattern matching, multiple pattern searches",
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
        preprocessing_ops = pattern_count * avg_pattern_length
        search_ops = data_length * pattern_count

        return {
            "preprocessing_operations": preprocessing_ops,
            "search_operations": search_ops,
            "total_operations": preprocessing_ops + search_ops,
            "estimated_time_seconds": (preprocessing_ops + search_ops) / 1e7,  # Faster than BF
            "memory_usage_mb": (data_length + pattern_count * avg_pattern_length * 2)
            * 8
            / 1e6,  # Extra space for prefix tables
            "complexity_class": "O(n+m*k)",  # k=patterns, but preprocessing is amortized
            "recommendation": "Excellent for large datasets and multiple pattern searches",
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
