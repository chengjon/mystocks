"""
Aho-Corasick (AC) Multi-Pattern Matching Algorithm for Quantitative Trading.

This module implements the Aho-Corasick pattern matching algorithm, which
constructs a finite automaton that can efficiently search for multiple patterns
simultaneously. This makes it ideal for detecting various trading patterns
in financial time series data.
"""

import logging
import time
from collections import deque
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


from .base import Pattern, PatternMatch, PatternMatchingAlgorithm, PatternMatchResult

logger = logging.getLogger(__name__)


class ACNode:
    """Node in the Aho-Corasick trie."""

    def __init__(self):
        self.children: Dict[float, "ACNode"] = {}
        self.failure_link: Optional["ACNode"] = None
        self.output_link: Optional["ACNode"] = None
        self.pattern_ids: List[str] = []  # Patterns that end at this node
        self.depth: int = 0

    def add_child(self, char: float) -> "ACNode":
        """Add a child node for the given character."""
        if char not in self.children:
            self.children[char] = ACNode()
            self.children[char].depth = self.depth + 1
        return self.children[char]

    def get_child(self, char: float) -> Optional["ACNode"]:
        """Get child node for the given character."""
        return self.children.get(char)


class AhoCorasickAlgorithm(PatternMatchingAlgorithm):
    """
    Aho-Corasick multi-pattern matching algorithm for trading patterns.

    AC algorithm constructs a trie of all patterns and adds failure links
    to enable efficient multi-pattern matching. It can find all occurrences
    of multiple patterns in a single pass through the text, making it
    extremely efficient for detecting various trading patterns simultaneously.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.root: Optional[ACNode] = None
        self.pattern_lengths: Dict[str, int] = {}

    def _build_trie(self, patterns: Dict[str, Pattern]) -> ACNode:
        """
        Build the Aho-Corasick trie from patterns.

        Args:
            patterns: Dictionary of patterns to include

        Returns:
            Root node of the constructed trie
        """
        root = ACNode()

        # Build trie
        for pattern_id, pattern in patterns.items():
            normalized_seq = self._normalize_sequence(pattern.sequence)
            self.pattern_lengths[pattern_id] = len(normalized_seq)

            node = root
            for char in normalized_seq:
                node = node.add_child(char)

            # Mark pattern end
            node.pattern_ids.append(pattern_id)

        return root

    def _build_failure_links(self, root: ACNode):
        """Build failure links for the Aho-Corasick automaton."""
        queue = deque()

        # Initialize root's children failure links
        for node in root.children.values():
            node.failure_link = root
            queue.append(node)

        # BFS to build failure links
        while queue:
            current = queue.popleft()

            for char, child in current.children.items():
                # Find the longest proper suffix that is also a prefix
                failure = current.failure_link

                while failure and char not in failure.children:
                    failure = failure.failure_link

                if failure:
                    child.failure_link = failure.children[char]
                else:
                    child.failure_link = root

                # Set output link for multi-pattern matching
                if child.failure_link.pattern_ids:
                    child.output_link = child.failure_link
                else:
                    child.output_link = child.failure_link.output_link

                queue.append(child)

    def _get_matches_from_node(self, node: ACNode, position: int) -> List[Tuple[str, int]]:
        """
        Get all pattern matches ending at the given node.

        Args:
            node: Current node in the automaton
            position: Current position in the text

        Returns:
            List of (pattern_id, start_position) tuples
        """
        matches = []

        # Check current node
        for pattern_id in node.pattern_ids:
            pattern_length = self.pattern_lengths[pattern_id]
            start_pos = position - pattern_length + 1
            matches.append((pattern_id, start_pos))

        # Follow output link for additional matches
        output_node = node.output_link
        while output_node:
            for pattern_id in output_node.pattern_ids:
                pattern_length = self.pattern_lengths[pattern_id]
                start_pos = position - pattern_length + 1
                matches.append((pattern_id, start_pos))
            output_node = output_node.output_link

        return matches

    def _aho_corasick_search(self, text: np.ndarray, root: ACNode, search_start: int = 0) -> Dict[str, List[int]]:
        """
        Perform Aho-Corasick search on the text.

        Args:
            text: Normalized text sequence to search in
            root: Root of the Aho-Corasick automaton
            search_start: Starting position offset

        Returns:
            Dictionary mapping pattern IDs to lists of match positions
        """
        matches = {}
        node = root
        n = len(text)

        for i in range(n):
            char = text[i]

            # Follow failure links until we find a valid transition
            while node and char not in node.children:
                node = node.failure_link

            if node:
                node = node.children.get(char, root)
            else:
                node = root

            # Check for matches at current position
            if node.pattern_ids or node.output_link:
                current_matches = self._get_matches_from_node(node, i)

                for pattern_id, start_pos in current_matches:
                    # Convert to absolute position
                    abs_start_pos = search_start + start_pos
                    if pattern_id not in matches:
                        matches[pattern_id] = []
                    matches[pattern_id].append(abs_start_pos)

        return matches

    async def add_pattern(self, pattern: Pattern) -> bool:
        """
        Add a pattern to the automaton (requires rebuilding).

        Args:
            pattern: Pattern to add

        Returns:
            True if pattern was added successfully
        """
        success = await super().add_pattern(pattern)
        if success:
            # Rebuild the entire automaton when patterns change
            await self._rebuild_automaton()

            logger.info("Added pattern {pattern.id} and rebuilt automaton")

        return success

    def remove_pattern(self, pattern_id: str) -> bool:
        """
        Remove a pattern from the automaton (requires rebuilding).

        Args:
            pattern_id: ID of pattern to remove

        Returns:
            True if pattern was removed
        """
        success = super().remove_pattern(pattern_id)
        if success:
            if pattern_id in self.pattern_lengths:
                del self.pattern_lengths[pattern_id]

            # Rebuild the entire automaton when patterns change
            import asyncio

            asyncio.create_task(self._rebuild_automaton())

            logger.info("Removed pattern %(pattern_id)s and rebuilt automaton")

        return success

    async def _rebuild_automaton(self):
        """Rebuild the Aho-Corasick automaton from current patterns."""
        if not self.patterns:
            self.root = None
            return

        self.root = self._build_trie(self.patterns)
        self._build_failure_links(self.root)

        logger.info("Rebuilt Aho-Corasick automaton with {len(self.patterns)} patterns")

    async def find_patterns(
        self,
        data: Union[List[float], np.ndarray, pd.Series],
        pattern_ids: Optional[List[str]] = None,
        search_range: Optional[Tuple[int, int]] = None,
        min_confidence: float = 0.8,
    ) -> List[PatternMatchResult]:
        """
        Find patterns using Aho-Corasick algorithm.

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

        # Ensure automaton is built
        if not self.root:
            await self._rebuild_automaton()
            if not self.root:
                logger.warning("No automaton available for matching")
                return []

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

        # Perform Aho-Corasick search
        all_matches = self._aho_corasick_search(normalized_data, self.root, search_start)

        results = []

        for pattern_id in target_patterns:
            if pattern_id not in self.patterns or pattern_id not in all_matches:
                continue

            pattern = self.patterns[pattern_id]
            match_positions = all_matches[pattern_id]

            matches = []
            for start_idx in match_positions:
                end_idx = start_idx + len(pattern.sequence) - 1
                confidence = 1.0  # AC finds exact matches after normalization

                if confidence >= max(min_confidence, pattern.min_confidence):
                    match = PatternMatch(
                        start_index=start_idx,
                        end_index=end_idx,
                        pattern_length=len(pattern.sequence),
                        confidence=confidence,
                        matched_sequence=data_array[start_idx : end_idx + 1].tolist(),
                        pattern_id=pattern_id,
                    )
                    matches.append(match)

            if matches:
                result = PatternMatchResult(
                    pattern_id=pattern_id,
                    matches=matches,
                    total_matches=len(matches),
                    execution_time=time.time() - start_time,
                    algorithm_used="aho_corasick",
                    gpu_used=self.gpu_enabled,
                    search_range=(search_start, search_end),
                )
                results.append(result)

                logger.info("Found {len(matches)} matches for pattern %(pattern_id)s using AC")

        self.match_history.extend(results)
        return results

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the Aho-Corasick algorithm."""
        base_info = super().get_metadata()
        base_info.update(
            {
                "algorithm_variant": "aho_corasick",
                "complexity": "O(n + m + z)",  # n=text, m=patterns, z=matches
                "preprocessing_complexity": "O(m * l)",  # m=patterns, l=avg length
                "strengths": ["Multi-pattern matching", "Linear time guarantee", "Memory efficient", "Scalable"],
                "weaknesses": ["Complex implementation", "Preprocessing overhead", "Memory for automaton"],
                "best_use_case": "Multiple pattern detection, large-scale pattern matching, real-time systems",
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
        # AC preprocessing is O(total characters in patterns)
        preprocessing_ops = pattern_count * avg_pattern_length * 2  # Rough estimate
        search_ops = data_length + (pattern_count * avg_pattern_length)  # Linear search

        return {
            "preprocessing_operations": preprocessing_ops,
            "search_operations": search_ops,
            "total_operations": preprocessing_ops + search_ops,
            "estimated_time_seconds": (preprocessing_ops + search_ops) / 1e8,  # Very fast
            "memory_usage_mb": (data_length + pattern_count * avg_pattern_length * 3) * 8 / 1e6,  # Automaton overhead
            "complexity_class": "O(n + m + z)",  # z = number of matches
            "recommendation": "Ideal for multi-pattern matching and large-scale applications",
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
