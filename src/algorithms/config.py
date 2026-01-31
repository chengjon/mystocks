"""
Algorithm configuration models using Pydantic.

This module defines the configuration models for algorithm training,
prediction, and evaluation parameters. All configurations use Pydantic
for validation and type safety.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .types import AlgorithmType


class AlgorithmConfig(BaseModel):
    """Base configuration for all algorithms."""

    algorithm_type: AlgorithmType
    algorithm_name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")
    description: Optional[str] = Field(None, max_length=500)

    # Common training parameters
    random_seed: Optional[int] = Field(None, ge=0, le=2**32 - 1)
    enable_gpu: bool = Field(default=True)
    gpu_memory_limit_mb: Optional[int] = Field(None, gt=0)
    enable_validation: bool = Field(default=True)

    class Config:
        validate_assignment = True


class ClassificationConfig(AlgorithmConfig):
    """Configuration for classification algorithms."""

    # SVM specific
    kernel: Optional[str] = Field(None, pattern=r"^(linear|rbf|poly|sigmoid)$")
    C: Optional[float] = Field(None, gt=0)
    gamma: Optional[Union[str, float]] = Field(None)
    degree: Optional[int] = Field(None, ge=1, le=10)

    # Decision Tree specific
    max_depth: Optional[int] = Field(None, gt=0)
    min_samples_split: Optional[int] = Field(None, gt=1)
    min_samples_leaf: Optional[int] = Field(None, gt=0)
    max_features: Optional[Union[str, int, float]] = Field(None)

    # Naive Bayes specific
    alpha: Optional[float] = Field(None, ge=0)  # Laplace smoothing

    # Common classification parameters
    class_weight: Optional[Union[str, Dict[str, float]]] = Field(None)
    max_iter: Optional[int] = Field(None, gt=0)


class PatternMatchingConfig(AlgorithmConfig):
    """Configuration for pattern matching algorithms."""

    # Common parameters
    case_sensitive: bool = Field(default=False)
    max_pattern_length: Optional[int] = Field(None, gt=0, le=10000)
    max_text_length: Optional[int] = Field(None, gt=0, le=1000000)

    # Aho-Corasick specific
    enable_failure_links: bool = Field(default=True)

    # GPU acceleration parameters
    gpu_block_size: Optional[int] = Field(None, gt=0)
    gpu_thread_count: Optional[int] = Field(None, gt=0)


class MarkovConfig(AlgorithmConfig):
    """Configuration for Hidden Markov Model algorithms."""

    n_states: int = Field(..., gt=1, le=100)
    n_features: Optional[int] = Field(None, gt=0)
    covariance_type: str = Field(default="full", pattern=r"^(full|diag|spherical|tied)$")

    # Training parameters
    max_iter: int = Field(default=100, gt=0)
    tol: float = Field(default=1e-3, gt=0)
    n_init: int = Field(default=10, gt=0)

    # Initialization method
    init_method: str = Field(default="kmeans", pattern=r"^(random|kmeans)$")


class BayesianConfig(AlgorithmConfig):
    """Configuration for Bayesian Network algorithms."""

    structure_learning: str = Field(default="hill_climb", pattern=r"^(hill_climb|exact|chow_liu)$")
    parameter_learning: str = Field(default="mle", pattern=r"^(mle|bayesian)$")

    # Structure learning parameters
    max_parents: Optional[int] = Field(None, gt=0)
    significance_level: float = Field(default=0.05, gt=0, le=1)

    # Inference parameters
    inference_method: str = Field(default="exact", pattern=r"^(exact|approximate)$")
    sampling_method: Optional[str] = Field(None, pattern=r"^(gibbs|rejection)$")


class NGramConfig(AlgorithmConfig):
    """Configuration for N-gram model algorithms."""

    n: int = Field(..., gt=0, le=10)  # N-gram size
    smoothing: str = Field(default="laplace", pattern=r"^(laplace|good_turing|kneser_ney)$")

    # Smoothing parameters
    alpha: float = Field(default=1.0, ge=0)  # Laplace smoothing parameter
    discount: Optional[float] = Field(None, gt=0, lt=1)  # Kneser-Ney discount

    # Model parameters
    min_frequency: int = Field(default=1, ge=0)
    max_vocabulary_size: Optional[int] = Field(None, gt=0)


class NeuralNetworkConfig(AlgorithmConfig):
    """Configuration for neural network algorithms."""

    architecture: str = Field(default="lstm", pattern=r"^(lstm|gru|rnn|cnn)$")
    hidden_units: List[int] = Field(default_factory=lambda: [64, 32])
    dropout_rate: float = Field(default=0.2, ge=0, le=1)

    # Training parameters
    epochs: int = Field(default=100, gt=0)
    batch_size: int = Field(default=32, gt=0)
    learning_rate: float = Field(default=0.001, gt=0)
    optimizer: str = Field(default="adam", pattern=r"^(adam|rmsprop|sgd)$")

    # Architecture specific parameters
    num_layers: int = Field(default=2, gt=0)
    bidirectional: bool = Field(default=False)
    attention: bool = Field(default=False)


class TrainingConfig(BaseModel):
    """Configuration for algorithm training."""

    start_date: datetime
    end_date: datetime
    symbol: str
    features: List[str] = Field(default_factory=list)
    target_column: str = Field(default="close")
    train_split: float = Field(default=0.7, gt=0, lt=1)

    # Validation parameters
    enable_cross_validation: bool = Field(default=True)
    cv_folds: int = Field(default=5, gt=1)
    validation_metric: str = Field(default="accuracy")

    # Data preprocessing
    enable_scaling: bool = Field(default=True)
    enable_missing_value_handling: bool = Field(default=True)
    outlier_threshold: Optional[float] = Field(None, gt=0)


class PredictionConfig(BaseModel):
    """Configuration for algorithm prediction."""

    prediction_horizon: int = Field(default=1, gt=0)
    confidence_threshold: float = Field(default=0.5, ge=0, le=1)
    enable_probability_output: bool = Field(default=True)

    # Rolling prediction parameters
    rolling_window_size: Optional[int] = Field(None, gt=0)
    step_size: int = Field(default=1, gt=0)


class EvaluationConfig(BaseModel):
    """Configuration for algorithm evaluation."""

    metrics: List[str] = Field(default_factory=lambda: ["accuracy", "precision", "recall", "f1"])
    enable_confusion_matrix: bool = Field(default=True)
    enable_roc_curve: bool = Field(default=True)
    enable_feature_importance: bool = Field(default=True)
