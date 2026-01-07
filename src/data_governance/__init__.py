"""
Data Governance Module

Provides data quality metrics, lineage tracking, and asset management
capabilities for comprehensive data governance.
"""

from .quality import (
    DataQualityChecker,
    QualityScore,
    QualityReport,
    QualityDimension,
)

from .lineage import (
    LineageTracker,
    LineageStorage,
    LineageNode,
    LineageEdge,
    LineageGraph,
    NodeType,
    OperationType,
)

from .asset import DataAssetRegistry, AssetStorage, DataAsset, AssetType

__all__ = [
    "DataQualityChecker",
    "QualityScore",
    "QualityReport",
    "QualityDimension",
    "LineageTracker",
    "LineageStorage",
    "LineageNode",
    "LineageEdge",
    "LineageGraph",
    "NodeType",
    "OperationType",
    "DataAssetRegistry",
    "AssetStorage",
    "DataAsset",
    "AssetType",
]

# Alias for backward compatibility
QualityChecker = DataQualityChecker
