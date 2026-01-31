"""
Data Governance Module

Provides data quality metrics, lineage tracking, and asset management
capabilities for comprehensive data governance.
"""

from .asset import AssetStorage, AssetType, DataAsset, DataAssetRegistry
from .lineage import (
    LineageEdge,
    LineageGraph,
    LineageNode,
    LineageStorage,
    LineageTracker,
    NodeType,
    OperationType,
)
from .quality import (
    DataQualityChecker,
    QualityDimension,
    QualityReport,
    QualityScore,
)

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
