"""
LightGBM Model - Adapter for LGBMRegressor

Wraps LightGBM's regressor to conform to BaseModel interface.

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
import os
from .base_model import BaseModel

try:
    from lightgbm import LGBMRegressor
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
    import joblib
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False


class LightGBMModel(BaseModel):
    """
    LightGBM Model (Regression)

    Wraps LightGBM's LGBMRegressor with BaseModel interface.

    Example:
        >>> model = LightGBMModel()
        >>> metrics = model.fit(X_train, y_train)
        >>> predictions = model.predict(X_test)
    """

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize LightGBM model

        Args:
            config: LightGBM configuration dict (optional)
        """
        super().__init__()

        if not LIGHTGBM_AVAILABLE:
            raise ImportError("LightGBM not installed. Run: pip install lightgbm scikit-learn")

        self.config = config or self._default_config()
        self.model = LGBMRegressor(**self.config)

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        """Default LightGBM configuration"""
        return {
            'boosting_type': 'gbdt',
            'objective': 'regression',
            'num_leaves': 25,
            'learning_rate': 0.2,
            'n_estimators': 70,
            'max_depth': 15,
            'metric': 'rmse',
            'bagging_fraction': 0.8,
            'feature_fraction': 0.8,
            'reg_lambda': 0.9,
            'random_state': 42,
            'verbose': -1
        }

    def fit(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, **kwargs) -> Dict[str, Any]:
        """
        Train LightGBM model

        Args:
            X: Feature matrix
            y: Target variable (continuous)
            test_size: Test set ratio (default 0.2)

        Returns:
            Dict: Training metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )

        # Train model
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric='rmse'
        )
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test)

        metrics = {
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2_score': r2_score(y_test, y_pred),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

        # MAPE
        mask = y_test != 0
        if mask.sum() > 0:
            mape = np.mean(np.abs((y_test[mask] - y_pred[mask]) / y_test[mask])) * 100
            metrics['mape'] = mape

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict continuous values

        Args:
            X: Feature matrix

        Returns:
            np.ndarray: Predicted values
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call fit() first.")

        return self.model.predict(X)

    def save_model(self, file_path: str) -> None:
        """Save model to file"""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Cannot save.")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        model_data = {
            'model': self.model,
            'config': self.config
        }

        joblib.dump(model_data, file_path)

    def load_model(self, file_path: str) -> None:
        """Load model from file"""
        model_data = joblib.load(file_path)

        self.model = model_data['model']
        self.config = model_data['config']
        self.is_trained = True
