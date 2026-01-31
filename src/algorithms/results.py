"""
Algorithm result models using Pydantic.

This module defines the data models for algorithm results, predictions,
and evaluation metrics. All models use Pydantic for validation and
structured data handling.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class AlgorithmMetrics(BaseModel):
    """Metrics for algorithm evaluation."""

    # Classification metrics
    accuracy: Optional[float] = Field(None, ge=0, le=1)
    precision: Optional[float] = Field(None, ge=0, le=1)
    recall: Optional[float] = Field(None, ge=0, le=1)
    f1_score: Optional[float] = Field(None, ge=0, le=1)

    # Regression metrics
    mse: Optional[float] = Field(None, ge=0)
    rmse: Optional[float] = Field(None, ge=0)
    mae: Optional[float] = Field(None, ge=0)
    r2_score: Optional[float] = Field(None, ge=-float("inf"), le=1)

    # Pattern matching metrics
    pattern_matches: Optional[int] = Field(None, ge=0)
    match_accuracy: Optional[float] = Field(None, ge=0, le=1)
    false_positives: Optional[int] = Field(None, ge=0)
    false_negatives: Optional[int] = Field(None, ge=0)

    # General metrics
    training_time: Optional[float] = Field(None, ge=0)
    prediction_time: Optional[float] = Field(None, ge=0)
    memory_usage_mb: Optional[float] = Field(None, ge=0)

    # Custom metrics
    custom_metrics: Optional[Dict[str, Union[float, int]]] = Field(default_factory=dict)


class PredictionResult(BaseModel):
    """Result of a single prediction."""

    timestamp: datetime
    prediction: Union[str, float, int]
    confidence: Optional[float] = Field(None, ge=0, le=1)
    probability_distribution: Optional[Dict[str, float]] = Field(default_factory=dict)
    features_used: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True


class AlgorithmResult(BaseModel):
    """Complete result from algorithm execution."""

    algorithm_id: str
    algorithm_type: str
    algorithm_name: str
    execution_timestamp: datetime
    execution_time_seconds: float

    # Predictions
    predictions: List[PredictionResult] = Field(default_factory=list)

    # Evaluation metrics
    metrics: AlgorithmMetrics

    # Model information
    model_version: Optional[str] = None
    model_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    # Execution context
    input_data_shape: Optional[tuple] = None
    gpu_used: bool = Field(default=False)
    gpu_memory_used_mb: Optional[float] = None

    # Error handling
    success: bool = Field(default=True)
    error_message: Optional[str] = None
    warnings: Optional[List[str]] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True


class BatchAlgorithmResult(BaseModel):
    """Result from batch algorithm execution."""

    batch_id: str
    total_executions: int
    successful_executions: int
    failed_executions: int

    results: List[AlgorithmResult] = Field(default_factory=list)
    errors: List[Dict[str, Any]] = Field(default_factory=list)

    # Batch statistics
    total_execution_time: float
    average_execution_time: float
    gpu_utilization_percent: Optional[float] = None

    # Summary metrics
    aggregated_metrics: Optional[AlgorithmMetrics] = None


class ModelArtifact(BaseModel):
    """Serialized algorithm model artifact."""

    algorithm_type: str
    algorithm_name: str
    version: str
    created_at: datetime

    # Model data (serialized)
    model_data: bytes
    model_format: str = Field(default="pickle")  # pickle, joblib, onnx, etc.

    # Metadata
    training_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    feature_names: Optional[List[str]] = Field(default_factory=list)
    target_names: Optional[List[str]] = Field(default_factory=list)

    # Performance
    training_metrics: Optional[AlgorithmMetrics] = None
    validation_metrics: Optional[AlgorithmMetrics] = None

    # Size and checksums
    model_size_bytes: int
    checksum_sha256: str

    class Config:
        arbitrary_types_allowed = True


class AlgorithmStatus(BaseModel):
    """Current status of an algorithm."""

    algorithm_id: str
    status: str = Field(pattern=r"^(idle|training|predicting|error|maintenance)$")
    current_operation: Optional[str] = None
    progress_percent: Optional[float] = Field(None, ge=0, le=100)
    last_updated: datetime

    # Resource usage
    gpu_memory_used_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None

    # Error information
    last_error: Optional[str] = None
    error_count: int = Field(default=0)


class AlgorithmRegistryEntry(BaseModel):
    """Entry in the algorithm registry."""

    algorithm_type: str
    name: str
    version: str
    description: Optional[str] = None

    # Capabilities
    supported_features: List[str] = Field(default_factory=list)
    gpu_accelerated: bool = Field(default=True)
    max_data_size: Optional[int] = None  # Maximum data points

    # Status
    is_active: bool = Field(default=True)
    is_deprecated: bool = Field(default=False)
    deprecated_since: Optional[str] = None

    # Metadata
    author: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    tags: List[str] = Field(default_factory=list)
