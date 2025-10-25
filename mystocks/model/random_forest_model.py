"""
Random Forest Model - Adapter for RandomForestClassifier

Wraps sklearn's RandomForestClassifier to conform to BaseModel interface.

Author: JohnC & Claude
Version: 3.1.0 (Simplified MVP)
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
import pickle
import os
from .base_model import BaseModel

try:
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class RandomForestModel(BaseModel):
    """
    Random Forest Model (Classification)

    Wraps sklearn's RandomForestClassifier with BaseModel interface.

    Example:
        >>> model = RandomForestModel()
        >>> metrics = model.fit(X_train, y_train)
        >>> predictions = model.predict(X_test)
    """

    def __init__(self, n_estimators: int = 100, max_depth: int = 10, **kwargs):
        """
        Initialize Random Forest model

        Args:
            n_estimators: Number of trees (default 100)
            max_depth: Maximum tree depth (default 10)
            **kwargs: Additional sklearn parameters
        """
        super().__init__()

        if not SKLEARN_AVAILABLE:
            raise ImportError("sklearn not installed. Run: pip install scikit-learn")

        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.kwargs = kwargs

        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            **kwargs
        )

    def fit(self, X: pd.DataFrame, y: pd.Series, test_size: float = 0.2, **kwargs) -> Dict[str, Any]:
        """
        Train Random Forest model

        Args:
            X: Feature matrix
            y: Target variable (binary: 0/1)
            test_size: Test set ratio (default 0.2)

        Returns:
            Dict: Training metrics
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )

        # Train model
        self.model.fit(X_train, y_train)
        self.is_trained = True

        # Evaluate
        y_pred = self.model.predict(X_test)

        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, zero_division=0),
            'recall': recall_score(y_test, y_pred, zero_division=0),
            'f1_score': f1_score(y_test, y_pred, zero_division=0),
            'train_samples': len(X_train),
            'test_samples': len(X_test)
        }

        return metrics

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict class labels

        Args:
            X: Feature matrix

        Returns:
            np.ndarray: Predicted labels (0/1)
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call fit() first.")

        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict class probabilities

        Args:
            X: Feature matrix

        Returns:
            np.ndarray: Probability for positive class
        """
        if not self.is_trained:
            raise RuntimeError("Model not trained. Call fit() first.")

        return self.model.predict_proba(X)[:, 1]

    def save_model(self, file_path: str) -> None:
        """Save model to file"""
        if not self.is_trained:
            raise RuntimeError("Model not trained. Cannot save.")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        model_data = {
            'model': self.model,
            'n_estimators': self.n_estimators,
            'max_depth': self.max_depth,
            'kwargs': self.kwargs
        }

        with open(file_path, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, file_path: str) -> None:
        """Load model from file"""
        with open(file_path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.n_estimators = model_data['n_estimators']
        self.max_depth = model_data['max_depth']
        self.kwargs = model_data.get('kwargs', {})
        self.is_trained = True
