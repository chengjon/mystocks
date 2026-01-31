"""
Algorithm metadata and versioning support.

This module provides classes and utilities for managing algorithm
metadata, versioning, and lifecycle management.
"""

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class AlgorithmVersion:
    """Algorithm version information."""

    major: int
    minor: int
    patch: int
    pre_release: Optional[str] = None
    build: Optional[str] = None

    def __str__(self) -> str:
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre_release:
            version += f"-{self.pre_release}"
        if self.build:
            version += f"+{self.build}"
        return version

    @classmethod
    def from_string(cls, version_str: str) -> "AlgorithmVersion":
        """Parse version from string."""
        # Simple parsing - could be enhanced with proper semver parsing
        parts = version_str.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version format: {version_str}")

        major, minor, patch = map(int, parts)
        return cls(major=major, minor=minor, patch=patch)

    def bump_major(self) -> "AlgorithmVersion":
        """Increment major version."""
        return AlgorithmVersion(self.major + 1, 0, 0)

    def bump_minor(self) -> "AlgorithmVersion":
        """Increment minor version."""
        return AlgorithmVersion(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "AlgorithmVersion":
        """Increment patch version."""
        return AlgorithmVersion(self.major, self.minor, self.patch + 1)


@dataclass
class AlgorithmFingerprint:
    """Algorithm fingerprint for change detection."""

    config_hash: str
    code_hash: str
    data_hash: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "AlgorithmFingerprint":
        """Create fingerprint from configuration."""
        config_str = json.dumps(config, sort_keys=True, default=str)
        config_hash = hashlib.sha256(config_str.encode()).hexdigest()
        return cls(config_hash=config_hash, code_hash="")

    def update_code_hash(self, code_content: str):
        """Update code hash."""
        self.code_hash = hashlib.sha256(code_content.encode()).hexdigest()

    def update_data_hash(self, data_content: str):
        """Update data hash."""
        self.data_hash = hashlib.sha256(data_content.encode()).hexdigest()


@dataclass
class AlgorithmHistory:
    """Algorithm execution and training history."""

    algorithm_id: str
    executions: List[Dict[str, Any]] = field(default_factory=list)
    training_sessions: List[Dict[str, Any]] = field(default_factory=list)
    performance_trends: List[Dict[str, Any]] = field(default_factory=list)

    def add_execution(self, execution_result: Dict[str, Any]):
        """Add execution result to history."""
        execution = {"timestamp": datetime.now(), "result": execution_result}
        self.executions.append(execution)

    def add_training_session(self, training_result: Dict[str, Any]):
        """Add training session to history."""
        session = {"timestamp": datetime.now(), "result": training_result}
        self.training_sessions.append(session)

    def get_recent_executions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent executions."""
        return self.executions[-limit:] if self.executions else []

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary from history."""
        if not self.executions:
            return {}

        accuracies = [
            e["result"].get("metrics", {}).get("accuracy", 0)
            for e in self.executions
            if "metrics" in e.get("result", {})
        ]
        execution_times = [e["result"].get("execution_time_seconds", 0) for e in self.executions]

        return {
            "total_executions": len(self.executions),
            "average_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
            "average_execution_time": sum(execution_times) / len(execution_times) if execution_times else 0,
            "last_execution": self.executions[-1]["timestamp"] if self.executions else None,
        }


class AlgorithmRegistry:
    """Registry for managing algorithm metadata."""

    def __init__(self):
        self.algorithms: Dict[str, Dict[str, Any]] = {}

    def register_algorithm(self, algorithm_id: str, metadata: Dict[str, Any]):
        """Register an algorithm."""
        self.algorithms[algorithm_id] = {
            "metadata": metadata,
            "registered_at": datetime.now(),
            "last_updated": datetime.now(),
        }

    def get_algorithm(self, algorithm_id: str) -> Optional[Dict[str, Any]]:
        """Get algorithm metadata."""
        return self.algorithms.get(algorithm_id)

    def update_algorithm(self, algorithm_id: str, updates: Dict[str, Any]):
        """Update algorithm metadata."""
        if algorithm_id in self.algorithms:
            self.algorithms[algorithm_id].update(updates)
            self.algorithms[algorithm_id]["last_updated"] = datetime.now()

    def list_algorithms(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """List algorithms with optional filtering."""
        algorithms = list(self.algorithms.values())

        if filters:
            filtered = []
            for algo in algorithms:
                metadata = algo["metadata"]
                if all(metadata.get(k) == v for k, v in filters.items()):
                    filtered.append(algo)
            return filtered

        return algorithms

    def remove_algorithm(self, algorithm_id: str) -> bool:
        """Remove algorithm from registry."""
        if algorithm_id in self.algorithms:
            del self.algorithms[algorithm_id]
            return True
        return False


# Global registry instance
algorithm_registry = AlgorithmRegistry()
