"""
Quantitative Trading Algorithms Module

This module provides advanced machine learning algorithms for quantitative trading,
leveraging GPU acceleration and existing MyStocks infrastructure.

Algorithms Categories:
- Classification: SVM, Decision Trees, Naive Bayes for signal generation
- Pattern Matching: BF, KMP, BMH, Aho-Corasick for sequence analysis
- Markov: Hidden Markov Models for market regime detection
- Bayesian: Bayesian Networks for probabilistic relationships
- N-gram: N-gram models for sequential pattern analysis
- Neural: Neural networks for time-series forecasting

All algorithms support GPU acceleration via cuML/cuDF and integrate with
existing TDengine/PostgreSQL dual database architecture.
"""

from .base import AlgorithmType, BaseAlgorithm
from .config import AlgorithmConfig
from .results import AlgorithmMetrics, AlgorithmResult

__all__ = [
    "BaseAlgorithm",
    "AlgorithmType",
    "AlgorithmConfig",
    "AlgorithmResult",
    "AlgorithmMetrics",
]
