"""
Machine Learning Strategy Module for MyStocks

This module provides machine learning capabilities for stock price prediction,
feature engineering, and feature selection.

Modules:
    - feature_engineering: Rolling window feature generation
    - price_predictor: LightGBM-based price prediction
    - feature_selector: Multiple feature selection algorithms

Author: MyStocks Development Team
Created: 2025-10-19
"""

__version__ = "1.0.0"
__all__ = [
    "RollingFeatureGenerator",
    "PricePredictorStrategy",
    "FeatureSelector",
]

# Import main classes (will be available after implementation)
try:
    from .feature_engineering import RollingFeatureGenerator
except ImportError:
    pass

try:
    from .price_predictor import PricePredictorStrategy
except ImportError:
    pass

try:
    from .feature_selector import FeatureSelector
except ImportError:
    pass
