"""
Pattern Matching Manager for Quantitative Trading Algorithms.

This module provides a unified interface for managing and using all
pattern matching algorithms (BF, KMP, BMH, AC) in the quantitative
trading system. It handles algorithm selection, pattern management,
and performance evaluation for time series pattern detection.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd

from src.algorithms.base import AlgorithmMetadata
from src.algorithms.types import AlgorithmType

from .ac_algorithm import AhoCorasickAlgorithm
from .base import Pattern, PatternMatchingAlgorithm, PatternMatchResult
from .bmh_algorithm import BMHAlgorithm
from .brute_force_algorithm import BruteForceAlgorithm
from .kmp_algorithm import KMPAlgorithm

logger = logging.getLogger(__name__)


class PatternMatchingManager:
    """
    Unified manager for pattern matching algorithms in quantitative trading.

    Provides a single interface for pattern detection using multiple algorithms.
    Supports automatic algorithm selection based on data characteristics and
    performance requirements. Includes comprehensive pattern library management.
    """

    def __init__(self):
        self.algorithms: Dict[str, PatternMatchingAlgorithm] = {}
        self.pattern_library: Dict[str, Pattern] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # Algorithm mapping
        self.algorithm_classes = {
            AlgorithmType.BRUTE_FORCE: BruteForceAlgorithm,
            AlgorithmType.KNUTH_MORRIS_PRATT: KMPAlgorithm,
            AlgorithmType.BOYER_MOORE_HORSPOOL: BMHAlgorithm,
            AlgorithmType.AHO_CORASICK: AhoCorasickAlgorithm,
        }

    def create_algorithm(
        self, algorithm_type: AlgorithmType, name: str, config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new pattern matching algorithm instance.

        Args:
            algorithm_type: Type of algorithm to create
            name: Unique name for the algorithm
            config: Optional configuration parameters

        Returns:
            Algorithm ID for future reference
        """
        if name in self.algorithms:
            raise ValueError(f"Algorithm with name '{name}' already exists")

        if algorithm_type not in self.algorithm_classes:
            raise ValueError(f"Unsupported algorithm type: {algorithm_type}")

        # Create metadata
        metadata = AlgorithmMetadata(
            algorithm_type=algorithm_type,
            name=name,
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            description=config.get("description") if config else None,
        )

        # Create algorithm instance
        algorithm_class = self.algorithm_classes[algorithm_type]
        algorithm = algorithm_class(metadata)

        self.algorithms[name] = algorithm
        self.performance_history[name] = []

        logger.info("Created {algorithm_type.value} algorithm: %(name)s")
        return name

    def add_pattern_to_library(self, pattern: Pattern) -> bool:
        """
        Add a pattern to the global pattern library.

        Args:
            pattern: Pattern to add

        Returns:
            True if pattern was added successfully
        """
        if pattern.id in self.pattern_library:
            logger.warning("Pattern {pattern.id} already exists, updating")
        self.pattern_library[pattern.id] = pattern
        logger.info("Added pattern to library: {pattern.id")
        return True

    def remove_pattern_from_library(self, pattern_id: str) -> bool:
        """
        Remove a pattern from the global library.

        Args:
            pattern_id: ID of pattern to remove

        Returns:
            True if pattern was removed
        """
        if pattern_id in self.pattern_library:
            del self.pattern_library[pattern_id]
            logger.info("Removed pattern from library: %(pattern_id)s")
            return True
        return False

    def load_patterns_to_algorithm(self, algorithm_name: str, pattern_ids: List[str]) -> int:
        """
        Load patterns from library to a specific algorithm.

        Args:
            algorithm_name: Name of the algorithm
            pattern_ids: IDs of patterns to load

        Returns:
            Number of patterns successfully loaded
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        loaded_count = 0

        for pattern_id in pattern_ids:
            if pattern_id in self.pattern_library:
                import asyncio

                success = asyncio.run(algorithm.add_pattern(self.pattern_library[pattern_id]))
                if success:
                    loaded_count += 1
            else:
                logger.warning("Pattern %(pattern_id)s not found in library")

        logger.info("Loaded %(loaded_count)s patterns to algorithm %(algorithm_name)s")
        return loaded_count

    async def find_patterns(
        self,
        algorithm_name: str,
        data: Union[List[float], pd.Series, pd.DataFrame],
        pattern_ids: Optional[List[str]] = None,
        search_range: Optional[Tuple[int, int]] = None,
        min_confidence: float = 0.8,
    ) -> List[PatternMatchResult]:
        """
        Find patterns using a specific algorithm.

        Args:
            algorithm_name: Name of the algorithm to use
            data: Time series data to search in
            pattern_ids: Specific patterns to search for (None = all loaded patterns)
            search_range: Range of indices to search (None = entire data)
            min_confidence: Minimum confidence threshold for matches

        Returns:
            List of pattern match results
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        start_time = datetime.now()

        # Perform pattern matching
        results = await algorithm.find_patterns(data, pattern_ids, search_range, min_confidence)

        # Record performance
        execution_time = (datetime.now() - start_time).total_seconds()
        performance_record = {
            "timestamp": datetime.now(),
            "data_length": len(data) if hasattr(data, "__len__") else "unknown",
            "patterns_searched": len(pattern_ids) if pattern_ids else len(algorithm.patterns),
            "matches_found": sum(len(r.matches) for r in results),
            "execution_time": execution_time,
            "algorithm_type": algorithm.algorithm_type.value,
        }
        self.performance_history[algorithm_name].append(performance_record)

        return results

    def compare_algorithms(
        self,
        algorithm_names: List[str],
        data: Union[List[float], pd.Series, pd.DataFrame],
        pattern_ids: Optional[List[str]] = None,
        min_confidence: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Compare multiple algorithms on the same data and patterns.

        Args:
            algorithm_names: List of algorithm names to compare
            data: Test data for pattern matching
            pattern_ids: Patterns to search for
            min_confidence: Minimum confidence threshold

        Returns:
            Comparison results for all algorithms
        """
        import asyncio

        async def run_comparison():
            results = {}
            tasks = []

            for name in algorithm_names:
                if name not in self.algorithms:
                    logger.warning("Algorithm '%(name)s' not found, skipping")
                    continue

                # Load patterns if specified
                if pattern_ids:
                    self.load_patterns_to_algorithm(name, pattern_ids)

                # Create search task
                task = self.find_patterns(name, data, pattern_ids, None, min_confidence)
                tasks.append((name, task))

            # Execute all searches concurrently
            for name, task in tasks:
                try:
                    search_results = await task
                    total_matches = sum(len(r.matches) for r in search_results)

                    results[name] = {
                        "results": search_results,
                        "total_matches": total_matches,
                        "success": True,
                        "algorithm_type": self.algorithms[name].algorithm_type.value,
                    }

                except Exception as e:
                    logger.error("Failed to run algorithm '%(name)s': %(e)s")
                    results[name] = {"error": str(e), "success": False}

            return results

        return asyncio.run(run_comparison())

    def get_algorithm_info(self, algorithm_name: str) -> Dict[str, Any]:
        """Get information about a specific algorithm."""
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        base_info = algorithm.get_algorithm_info()

        # Add manager-specific info
        base_info.update(
            {
                "patterns_loaded": len(algorithm.patterns),
                "library_patterns_available": len(self.pattern_library),
                "performance_records": len(self.performance_history[algorithm_name]),
            }
        )

        return base_info

    def list_algorithms(self) -> List[Dict[str, Any]]:
        """List all created algorithms."""
        return [
            {
                "name": name,
                "type": algorithm.algorithm_type.value,
                "patterns_loaded": len(algorithm.patterns),
                "gpu_enabled": getattr(algorithm, "gpu_enabled", False),
                "created_at": algorithm.metadata.created_at,
                "performance_records": len(self.performance_history[name]),
            }
            for name, algorithm in self.algorithms.items()
        ]

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
            for p in self.pattern_library.values()
        ]

    def get_performance_history(self, algorithm_name: str) -> List[Dict[str, Any]]:
        """Get performance history for an algorithm."""
        return self.performance_history.get(algorithm_name, [])

    def recommend_algorithm(self, requirements: Dict[str, Any]) -> AlgorithmType:
        """
        Recommend the best algorithm based on requirements.

        Args:
            requirements: Dictionary describing requirements
                (e.g., {'data_length': 10000, 'patterns_count': 5, 'real_time': True})

        Returns:
            Recommended algorithm type
        """
        data_length = requirements.get("data_length", 1000)
        patterns_count = requirements.get("patterns_count", 1)
        real_time = requirements.get("real_time", False)
        exact_matching = requirements.get("exact_matching", True)

        # Decision logic based on requirements
        if patterns_count > 10:
            return AlgorithmType.AHO_CORASICK  # Multi-pattern efficiency
        elif real_time and data_length > 10000:
            return AlgorithmType.BOYER_MOORE_HORSPOOL  # Fast for large data
        elif data_length < 1000:
            return AlgorithmType.BRUTE_FORCE  # Simple for small data
        elif exact_matching and patterns_count <= 5:
            return AlgorithmType.KNUTH_MORRIS_PRATT  # Good all-around
        else:
            return AlgorithmType.AHO_CORASICK  # Default for complex scenarios

    def export_patterns(self, filepath: str) -> bool:
        """Export pattern library to file."""
        try:
            import json

            patterns_data = {
                "exported_at": datetime.now().isoformat(),
                "patterns": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "sequence": p.sequence,
                        "description": p.description,
                        "category": p.category,
                        "min_confidence": p.min_confidence,
                        "metadata": p.metadata,
                    }
                    for p in self.pattern_library.values()
                ],
            }

            with open(filepath, "w") as f:
                json.dump(patterns_data, f, indent=2, default=str)

            logger.info("Exported {len(self.pattern_library)} patterns to %(filepath)s")
            return True

        except Exception as e:
            logger.error("Failed to export patterns: %(e)s")
            return False

    def import_patterns(self, filepath: str) -> int:
        """Import pattern library from file."""
        try:
            import json

            with open(filepath, "r") as f:
                data = json.load(f)

            imported_count = 0
            for pattern_data in data.get("patterns", []):
                pattern = Pattern(**pattern_data)
                if self.add_pattern_to_library(pattern):
                    imported_count += 1

            logger.info("Imported %(imported_count)s patterns from %(filepath)s")
            return imported_count

        except Exception as e:
            logger.error("Failed to import patterns: %(e)s")
            return 0

    def cleanup(self):
        """Clean up resources."""
        self.algorithms.clear()
        self.pattern_library.clear()
        self.performance_history.clear()

        logger.info("PatternMatchingManager cleaned up")
