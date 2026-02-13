"""
Support Vector Machine (SVM) Algorithm for Quantitative Trading.

This module implements SVM-based classification for trading signal generation,
leveraging cuML for GPU-accelerated training and prediction.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    from cuml.metrics import accuracy_score as gpu_accuracy_score
    from cuml.preprocessing import StandardScaler as GPUStandardScaler
    from cuml.svm import SVC

    CUMl_AVAILABLE = True
except ImportError:
    CUMl_AVAILABLE = False
    logging.warning("cuML not available, SVM will use CPU fallback")

from src.algorithms.base import AlgorithmMetadata, GPUAcceleratedAlgorithm
from src.algorithms.metadata import AlgorithmFingerprint
from src.gpu.core.hardware_abstraction import GPUResourceManager

logger = logging.getLogger(__name__)


class SVMAlgorithm(GPUAcceleratedAlgorithm):
    """
    Support Vector Machine algorithm for trading signal classification.

    Uses SVM to classify market data into buy/sell/hold signals based on
    technical indicators and market features. Supports GPU acceleration
    via cuML for high-performance training and prediction.
    """

    def __init__(self, metadata: AlgorithmMetadata):
        super().__init__(metadata)
        self.model = None
        self.scaler = None
        self.feature_names: List[str] = []
        self.gpu_manager: Optional[GPUResourceManager] = None

        # Default SVM parameters
        self.default_params = {
            "kernel": "rbf",
            "C": 1.0,
            "gamma": "scale",
            "degree": 3,
            "class_weight": "balanced",
            "max_iter": 1000,
            "random_state": 42,
        }

    async def initialize_gpu_context(self):
        """Initialize GPU context for SVM operations."""
        if not self.gpu_enabled:
            return

        try:
            from src.gpu.core.hardware_abstraction import AllocationRequest, GPUResourceManager, StrategyPriority

            self.gpu_manager = GPUResourceManager()

            if not self.gpu_manager.initialize():
                logger.warning("GPU manager initialization failed, falling back to CPU")
                await self.fallback_to_cpu()
                return

            # Allocate GPU memory for model
            gpu_id = await self.gpu_manager.allocate_context(
                request=AllocationRequest(
                    strategy_id=f"svm_{self.metadata.name}",
                    priority=StrategyPriority.MEDIUM,
                    required_memory=self.gpu_memory_limit or 1024,
                    required_compute_streams=1,
                    performance_profile=None,
                ),
            )

            if gpu_id is not None:
                logger.info("SVM algorithm allocated GPU %(gpu_id)s")
            else:
                logger.warning("Failed to allocate GPU, falling back to CPU")
                await self.fallback_to_cpu()

        except Exception:
            logger.error("GPU context initialization failed: %(e)s")
            await self.fallback_to_cpu()

    async def release_gpu_context(self):
        """Release GPU resources."""
        if self.gpu_manager and not self.gpu_enabled:
            try:
                self.gpu_manager.release_context(f"svm_{self.metadata.name}")
                logger.info("SVM GPU resources released")
            except Exception:
                logger.error("GPU resource release failed: %(e)s")

    async def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train SVM model on historical data.

        Args:
            data: Training data with features and target column
            config: Training configuration

        Returns:
            Dictionary containing trained model and training metrics
        """
        try:
            # Validate input data
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")

            # Extract features and target
            feature_cols = config.get("feature_columns", [])
            target_col = config.get("target_column", "target")

            if not feature_cols:
                # Auto-detect numeric columns (excluding target)
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                feature_cols = [col for col in numeric_cols if col != target_col]

            if target_col not in data.columns:
                raise ValueError(f"Target column '{target_col}' not found in data")

            self.feature_names = feature_cols
            X = data[feature_cols].values
            y = data[target_col].values

            # Initialize GPU context if needed
            if self.gpu_enabled and not self.gpu_manager:
                await self.initialize_gpu_context()

            # Prepare SVM parameters
            svm_params = self.default_params.copy()
            svm_params.update(config.get("svm_params", {}))

            # Feature scaling
            if self.gpu_enabled and CUMl_AVAILABLE:
                # GPU scaling
                self.scaler = GPUStandardScaler()
                X_scaled = self.scaler.fit_transform(X)
            else:
                # CPU scaling
                from sklearn.preprocessing import StandardScaler

                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)

            # Train SVM model
            if self.gpu_enabled and CUMl_AVAILABLE:
                # GPU training
                self.model = SVC(**svm_params)  # pylint: disable=used-before-assignment
                self.model.fit(X_scaled, y)
                logger.info("SVM model trained on GPU")
            else:
                # CPU fallback
                from sklearn.svm import SVC

                self.model = SVC(**svm_params)
                self.model.fit(X_scaled, y)
                logger.info("SVM model trained on CPU")

            # Calculate training metrics
            y_pred = self.model.predict(X_scaled)

            if self.gpu_enabled and CUMl_AVAILABLE:
                accuracy = float(gpu_accuracy_score(y, y_pred))
            else:
                from sklearn.metrics import accuracy_score

                accuracy = accuracy_score(y, y_pred)

            # Create model fingerprint
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
                    "training_time": 0.0,  # TODO: Add timing
                    "gpu_used": self.gpu_enabled,
                },
                "fingerprint": fingerprint,
                "config": config,
                "trained_at": datetime.now(),
            }

            # Update algorithm status
            self.is_trained = True
            self.update_metadata(last_trained=datetime.now())

            logger.info("SVM training completed - Accuracy: %(accuracy)s")
            return training_result

        except Exception:
            logger.error("SVM training failed: %(e)s")
            raise

    async def predict(self, data: pd.DataFrame, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using trained SVM model.

        Args:
            data: Input data for prediction
            model: Trained model from train() method

        Returns:
            Dictionary containing predictions and confidence scores
        """
        try:
            # Load model components
            svm_model = model["model"]
            scaler = model["scaler"]
            feature_names = model["feature_names"]

            # Validate input data
            missing_features = [col for col in feature_names if col not in data.columns]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")

            # Extract features
            X = data[feature_names].values

            # Scale features
            X_scaled = scaler.transform(X)

            # Generate predictions
            predictions = svm_model.predict(X_scaled)

            # Get decision function values (confidence scores)
            if hasattr(svm_model, "decision_function"):
                decision_values = svm_model.decision_function(X_scaled)
                # Convert to confidence scores (0-1 range)
                confidence_scores = 1 / (1 + np.exp(-np.abs(decision_values)))
            else:
                # Fallback for binary classification
                confidence_scores = np.full(len(predictions), 0.5)

            # Prepare results
            results = []
            for i, (pred, conf) in enumerate(zip(predictions, confidence_scores)):
                result = {
                    "prediction": int(pred),
                    "confidence": float(conf),
                    "features_used": {name: float(data.iloc[i][name]) for name in feature_names},
                }
                results.append(result)

            prediction_result = {
                "predictions": results,
                "n_predictions": len(results),
                "feature_names": feature_names,
                "prediction_time": 0.0,  # TODO: Add timing
                "gpu_used": self.gpu_enabled,
            }

            return prediction_result

        except Exception:
            logger.error("SVM prediction failed: %(e)s")
            raise

    def evaluate(self, predictions: Dict[str, Any], actual: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate SVM predictions against actual values.

        Args:
            predictions: Predictions from predict() method
            actual: Actual target values

        Returns:
            Dictionary containing evaluation metrics
        """
        try:
            # Extract predictions and actual values
            pred_values = np.array([p["prediction"] for p in predictions["predictions"]])
            actual_values = actual.values.flatten()

            if len(pred_values) != len(actual_values):
                raise ValueError("Prediction and actual value arrays must have same length")

            # Calculate metrics
            if self.gpu_enabled and CUMl_AVAILABLE:
                # GPU metrics
                accuracy = float(gpu_accuracy_score(actual_values, pred_values))
            else:
                # CPU metrics
                from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

                accuracy = accuracy_score(actual_values, pred_values)
                precision = precision_score(actual_values, pred_values, average="weighted", zero_division=0)
                recall = recall_score(actual_values, pred_values, average="weighted", zero_division=0)
                f1 = f1_score(actual_values, pred_values, average="weighted", zero_division=0)

            metrics = {
                "accuracy": accuracy,
                "precision": precision if not self.gpu_enabled else accuracy,  # pylint: disable=possibly-used-before-assignment
                "recall": recall if not self.gpu_enabled else accuracy,  # pylint: disable=possibly-used-before-assignment
                "f1_score": f1 if not self.gpu_enabled else accuracy,  # pylint: disable=possibly-used-before-assignment
                "n_samples": len(pred_values),
            }

            return metrics

        except Exception:
            logger.error("SVM evaluation failed: %(e)s")
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
            "metadata": self.metadata.__dict__,
        }

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
            logger.info("SVM model saved to %(filepath)s")
            return True

        except Exception:
            logger.error("Failed to save SVM model: %(e)s")
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

            logger.info("SVM model loaded from %(filepath)s")
            return True

        except Exception:
            logger.error("Failed to load SVM model: %(e)s")
            return False
