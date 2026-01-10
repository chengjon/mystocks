"""
Decision Tree Algorithm for Quantitative Trading.

This module implements Decision Tree-based classification for trading signal generation,
leveraging cuML for GPU-accelerated training and prediction. Includes Random Forest
ensemble methods for improved accuracy and robustness.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Union

try:
    from cuml.ensemble import RandomForestClassifier
    from cuml.tree import DecisionTreeClassifier
    from cuml.preprocessing import StandardScaler as GPUStandardScaler
    from cuml.metrics import accuracy_score as gpu_accuracy_score

    CUMl_AVAILABLE = True
except ImportError:
    CUMl_AVAILABLE = False
    logging.warning("cuML not available, Decision Tree will use CPU fallback")

from src.algorithms.base import GPUAcceleratedAlgorithm
from src.algorithms.types import AlgorithmType
from src.algorithms.metadata import AlgorithmFingerprint
from src.gpu.core.hardware_abstraction import GPUResourceManager

logger = logging.getLogger(__name__)


class DecisionTreeAlgorithm(GPUAcceleratedAlgorithm):
    """
    Decision Tree algorithm for trading signal classification.

    Uses Decision Tree and Random Forest algorithms to classify market data into
    buy/sell/hold signals based on technical indicators and market features.
    Supports GPU acceleration via cuML for high-performance training and prediction.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.model = None
        self.scaler = None
        self.feature_names: List[str] = []
        self.gpu_manager: Optional[GPUResourceManager] = None

        # Default Decision Tree parameters
        self.default_params = {
            "max_depth": None,
            "min_samples_split": 2,
            "min_samples_leaf": 1,
            "max_features": None,
            "criterion": "gini",
            "random_state": 42,
            "class_weight": "balanced",
        }

        # Random Forest specific parameters
        self.rf_params = {
            "n_estimators": 100,
            "bootstrap": True,
            "oob_score": False,
            "n_jobs": None,
            "warm_start": False,
        }

    async def initialize_gpu_context(self):
        """Initialize GPU context for Decision Tree operations."""
        if not self.gpu_enabled:
            return

        try:
            from src.gpu.core.hardware_abstraction import GPUResourceManager

            self.gpu_manager = GPUResourceManager()

            if not self.gpu_manager.initialize():
                logger.warning("GPU manager initialization failed, falling back to CPU")
                await self.fallback_to_cpu()
                return

            gpu_id = self.gpu_manager.allocate_gpu(
                task_id=f"dt_{self.metadata.name}", priority="medium", memory_required=self.gpu_memory_limit or 1024
            )

            if gpu_id is not None:
                logger.info(f"Decision Tree algorithm allocated GPU {gpu_id}")
            else:
                logger.warning("Failed to allocate GPU, falling back to CPU")
                await self.fallback_to_cpu()

        except Exception as e:
            logger.error(f"GPU context initialization failed: {e}")
            await self.fallback_to_cpu()

    async def release_gpu_context(self):
        """Release GPU resources."""
        if self.gpu_manager and not self.gpu_enabled:
            try:
                self.gpu_manager.release_gpu(f"dt_{self.metadata.name}")
                logger.info("Decision Tree GPU resources released")
            except Exception as e:
                logger.error(f"GPU resource release failed: {e}")

    async def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train Decision Tree/Random Forest model on historical data.

        Args:
            data: Training data with features and target column
            config: Training configuration

        Returns:
            Dictionary containing trained model and training metrics
        """
        try:
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")

            feature_cols = config.get("feature_columns", [])
            target_col = config.get("target_column", "target")
            use_random_forest = config.get("use_random_forest", True)

            if not feature_cols:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                feature_cols = [col for col in numeric_cols if col != target_col]

            if target_col not in data.columns:
                raise ValueError(f"Target column '{target_col}' not found in data")

            self.feature_names = feature_cols
            X = data[feature_cols].values
            y = data[target_col].values

            if self.gpu_enabled and not self.gpu_manager:
                await self.initialize_gpu_context()

            dt_params = self.default_params.copy()
            dt_params.update(config.get("decision_tree_params", {}))

            if self.gpu_enabled and CUMl_AVAILABLE:
                self.scaler = GPUStandardScaler()
                X_scaled = self.scaler.fit_transform(X)

                if use_random_forest:
                    rf_params = self.rf_params.copy()
                    rf_params.update(config.get("random_forest_params", {}))
                    combined_params = {**dt_params, **rf_params}
                    self.model = RandomForestClassifier(**combined_params)
                    logger.info("Training Random Forest on GPU")
                else:
                    self.model = DecisionTreeClassifier(**dt_params)
                    logger.info("Training Decision Tree on GPU")

                self.model.fit(X_scaled, y)

            else:
                from sklearn.preprocessing import StandardScaler
                from sklearn.ensemble import RandomForestClassifier
                from sklearn.tree import DecisionTreeClassifier

                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)

                if use_random_forest:
                    rf_params = self.rf_params.copy()
                    rf_params.update(config.get("random_forest_params", {}))
                    combined_params = {**dt_params, **rf_params}
                    self.model = RandomForestClassifier(**combined_params)
                    logger.info("Training Random Forest on CPU")
                else:
                    self.model = DecisionTreeClassifier(**dt_params)
                    logger.info("Training Decision Tree on CPU")

                self.model.fit(X_scaled, y)

            y_pred = self.model.predict(X_scaled)

            if self.gpu_enabled and CUMl_AVAILABLE:
                accuracy = float(gpu_accuracy_score(y, y_pred))
            else:
                from sklearn.metrics import accuracy_score

                accuracy = accuracy_score(y, y_pred)

            fingerprint = AlgorithmFingerprint.from_config(config)
            fingerprint.update_code_hash(str(self.__class__.__module__))

            training_result = {
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": self.feature_names,
                "training_metrics": {
                    "accuracy": accuracy,
                    "n_samples": len(X),
                    "n_features": len(feature_cols),
                    "algorithm_type": "random_forest" if use_random_forest else "decision_tree",
                    "training_time": 0.0,
                    "gpu_used": self.gpu_enabled,
                },
                "fingerprint": fingerprint,
                "config": config,
                "trained_at": pd.Timestamp.now(),
            }

            self.is_trained = True
            self.update_metadata(last_trained=pd.Timestamp.now())

            algorithm_name = "Random Forest" if use_random_forest else "Decision Tree"
            logger.info(f"{algorithm_name} training completed - Accuracy: {accuracy:.4f}")
            return training_result

        except Exception as e:
            logger.error(f"Decision Tree training failed: {e}")
            raise

    async def predict(self, data: pd.DataFrame, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using trained Decision Tree model.

        Args:
            data: Input data for prediction
            model: Trained model from train() method

        Returns:
            Dictionary containing predictions and confidence scores
        """
        try:
            svm_model = model["model"]
            scaler = model["scaler"]
            feature_names = model["feature_names"]

            missing_features = [col for col in feature_names if col not in data.columns]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")

            X = data[feature_names].values
            X_scaled = scaler.transform(X)

            predictions = svm_model.predict(X_scaled)

            if hasattr(svm_model, "predict_proba"):
                probabilities = svm_model.predict_proba(X_scaled)
                confidence_scores = np.max(probabilities, axis=1)
            else:
                confidence_scores = np.full(len(predictions), 0.5)

            results = []
            for i, (pred, conf) in enumerate(zip(predictions, confidence_scores)):
                result = {
                    "prediction": int(pred),
                    "confidence": float(conf),
                    "features_used": {name: float(data.iloc[i][name]) for name in feature_names},
                }
                results.append(result)

            return {
                "predictions": results,
                "n_predictions": len(results),
                "feature_names": feature_names,
                "prediction_time": 0.0,
                "gpu_used": self.gpu_enabled,
            }

        except Exception as e:
            logger.error(f"Decision Tree prediction failed: {e}")
            raise

    def evaluate(self, predictions: Dict[str, Any], actual: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate Decision Tree predictions against actual values.

        Args:
            predictions: Predictions from predict() method
            actual: Actual target values

        Returns:
            Dictionary containing evaluation metrics
        """
        try:
            pred_values = np.array([p["prediction"] for p in predictions["predictions"]])
            actual_values = actual.values.flatten()

            if len(pred_values) != len(actual_values):
                raise ValueError("Prediction and actual value arrays must have same length")

            if self.gpu_enabled and CUMl_AVAILABLE:
                accuracy = float(gpu_accuracy_score(actual_values, pred_values))
            else:
                from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

                accuracy = accuracy_score(actual_values, pred_values)
                precision = precision_score(actual_values, pred_values, average="weighted", zero_division=0)
                recall = recall_score(actual_values, pred_values, average="weighted", zero_division=0)
                f1 = f1_score(actual_values, pred_values, average="weighted", zero_division=0)

            metrics = {
                "accuracy": accuracy,
                "precision": precision if not self.gpu_enabled else accuracy,
                "recall": recall if not self.gpu_enabled else accuracy,
                "f1_score": f1 if not self.gpu_enabled else accuracy,
                "n_samples": len(pred_values),
            }

            return metrics

        except Exception as e:
            logger.error(f"Decision Tree evaluation failed: {e}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model."""
        if not self.is_trained or not self.model:
            return {"status": "not_trained"}

        return {
            "algorithm_type": self.algorithm_type.value,
            "is_trained": self.is_trained,
            "feature_names": self.feature_names,
            "gpu_enabled": self.gpu_enabled,
            "model_params": self.model.get_params() if hasattr(self.model, "get_params") else {},
            "feature_importance": self._get_feature_importance(),
            "metadata": self.metadata.__dict__,
        }

    def _get_feature_importance(self) -> Optional[Dict[str, float]]:
        """Get feature importance scores."""
        if not self.model or not hasattr(self.model, "feature_importances_"):
            return None

        return dict(zip(self.feature_names, self.model.feature_importances_))

    def save_model(self, filepath: str) -> bool:
        """Save trained model to file."""
        try:
            if not self.is_trained:
                raise ValueError("Model must be trained before saving")

            import joblib

            model_data = {
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": self.feature_names,
                "metadata": self.metadata,
                "gpu_enabled": self.gpu_enabled,
            }

            joblib.dump(model_data, filepath)
            logger.info(f"Decision Tree model saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to save Decision Tree model: {e}")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load trained model from file."""
        try:
            import joblib

            model_data = joblib.load(filepath)

            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.feature_names = model_data["feature_names"]
            self.metadata = model_data["metadata"]
            self.gpu_enabled = model_data.get("gpu_enabled", False)
            self.is_trained = True

            logger.info(f"Decision Tree model loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"Failed to load Decision Tree model: {e}")
            return False
