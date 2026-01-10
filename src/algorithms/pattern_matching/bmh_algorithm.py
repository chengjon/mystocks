"""
Boyer-Moore-Horspool (BMH) Pattern Matching Algorithm for Quantitative Trading.

This module implements the Boyer-Moore-Horspool pattern matching algorithm,
which uses a bad character heuristic to achieve sub-linear time complexity
by skipping portions of the text that cannot match the pattern.
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


class BMHAlgorithm(PatternMatchingAlgorithm):
    """
    Boyer-Moore-Horspool pattern matching algorithm for trading patterns.

    BMH algorithm uses a bad character heuristic to skip portions of the text
    that cannot possibly match the pattern. It preprocesses the pattern to create
    a shift table that indicates how far to shift the pattern when a mismatch occurs.
    This makes it significantly faster than brute force for large alphabets.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.bad_char_tables: Dict[str, Dict[float, int]] = {}

    def _compute_bad_char_table(self, pattern: np.ndarray) -> Dict[float, int]:
        """
        Compute the bad character shift table for BMH algorithm.

        Args:
            pattern: Normalized pattern sequence

        Returns:
            Bad character table mapping characters to shift distances
        """
        m = len(pattern)
        bad_char_table = {}

        # Initialize all possible values with default shift (pattern length)
        for i in range(m - 1):
            bad_char_table[pattern[i]] = m - i - 1

        return bad_char_table

    def _bmh_search(self, text: np.ndarray, pattern: np.ndarray, bad_char_table: Dict[float, int]) -> List[int]:
        """
        Perform BMH search on the text.

        Args:
            text: Normalized text sequence to search in
            pattern: Normalized pattern sequence to find
            bad_char_table: Precomputed bad character shift table

        Returns:
            List of starting indices where pattern matches were found
        """
        n, m = len(text), len(pattern)
        matches = []

        if m == 0 or n < m:
            return matches

        i = 0  # Starting position in text
        while i <= n - m:
            j = m - 1  # Starting position in pattern (right to left)

            # Compare pattern from right to left
            while j >= 0 and abs(text[i + j] - pattern[j]) < 1e-6:
                j -= 1

            if j < 0:
                # Found a match
                matches.append(i)
                # Shift by 1 for overlapping matches (simplified)
                i += 1
            else:
                # Mismatch occurred, use bad character rule
                bad_char = text[i + j]
                shift = bad_char_table.get(bad_char, m)

                # Ensure we make progress
                i += max(1, shift)

        return matches

    async def add_pattern(self, pattern: Pattern) -> bool:
        """
        Add a pattern and precompute its bad character table.

        Args:
            pattern: Pattern to add

        Returns:
            True if pattern was added successfully
        """
        success = await super().add_pattern(pattern)
        if success:
            # Precompute bad character table for the pattern
            normalized_pattern = self._normalize_sequence(pattern.sequence)
            bad_char_table = self._compute_bad_char_table(normalized_pattern)
            self.bad_char_tables[pattern.id] = bad_char_table

            logger.info(f"Precomputed bad character table for pattern {pattern.id} (size: {len(bad_char_table)})")

        return success

    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a pattern and its bad character table.

        Args:
            pattern_id: ID of pattern to remove

        Returns:
            True if pattern was removed
        """
        success = super().remove_pattern(pattern_id)
        if success and pattern_id in self.bad_char_tables:
            del self.bad_char_tables[pattern_id]
            logger.info(f"Removed bad character table for pattern {pattern_id}")

        return success

    async def find_patterns(
        self,
        data: Union[List[float], np.ndarray, pd.Series],
        pattern_ids: Optional[List[str]] = None,
        search_range: Optional[Tuple[int, int]] = None,
        min_confidence: float = 0.8,
    ) -> List[PatternMatchResult]:
        """
        Find patterns using BMH algorithm.

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
            if pattern_id not in self.patterns or pattern_id not in self.bad_char_tables:
                logger.warning(f"Pattern {pattern_id} not found or not preprocessed")
                continue

            pattern = self.patterns[pattern_id]
            bad_char_table = self.bad_char_tables[pattern_id]
            normalized_pattern = self._normalize_sequence(pattern.sequence)

            # Perform BMH search
            match_indices = self._bmh_search(normalized_data, normalized_pattern, bad_char_table)

            matches = []
            for start_idx in match_indices:
                end_idx = start_idx + len(normalized_pattern) - 1
                confidence = 1.0  # BMH finds exact matches after normalization

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
                    algorithm_used="boyer_moore_horspool",
                    gpu_used=self.gpu_enabled,
                    search_range=(search_start, search_end),
                )
                results.append(result)

                logger.info(f"Found {len(matches)} matches for pattern {pattern_id} using BMH")

        self.match_history.extend(results)
        return results

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the BMH algorithm."""
        base_info = super().get_algorithm_info()
        base_info.update(
            {
                "algorithm_variant": "boyer_moore_horspool",
                "complexity": "O(n*m)",  # Worst case, but often sub-linear
                "preprocessing_complexity": "O(m + σ)",  # σ = alphabet size
                "strengths": [
                    "Sub-linear performance",
                    "Simple bad character heuristic",
                    "Effective for large alphabets",
                ],
                "weaknesses": ["Worst case still O(n*m)", "No good suffix rule", "Memory for shift tables"],
                "best_use_case": "Large alphabets, real-time pattern matching, when patterns are distinct",
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
        # BMH is typically much faster than BF due to skipping
        # Average case is often O(n/m) for distinct patterns
        preprocessing_ops = pattern_count * (avg_pattern_length + 256)  # Rough alphabet size estimate
        search_ops = data_length * pattern_count * 0.5  # Estimated skipping factor

        return {
            "preprocessing_operations": preprocessing_ops,
            "search_operations": search_ops,
            "total_operations": preprocessing_ops + search_ops,
            "estimated_time_seconds": (preprocessing_ops + search_ops) / 5e7,  # Much faster than BF
            "memory_usage_mb": (data_length + pattern_count * avg_pattern_length) * 8 / 1e6,
            "complexity_class": "O(n*m) worst case, often O(n/m) average",
            "recommendation": "Excellent for real-time applications and large datasets",
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
