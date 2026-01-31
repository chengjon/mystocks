"""
Naive Bayes Algorithm for Quantitative Trading.

This module implements Naive Bayes classification for trading signal generation,
leveraging cuML for GPU-accelerated training and prediction. Suitable for
market regime detection and probabilistic signal generation.
"""

import logging
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    from cuml.metrics import accuracy_score as gpu_accuracy_score
    from cuml.naive_bayes import ComplementNB, GaussianNB, MultinomialNB
            # type: ignore[E0601]  # Pylint false positive - imports available in all code paths
    from cuml.preprocessing import StandardScaler as GPUStandardScaler

    CUMl_AVAILABLE = True
except ImportError:
    CUMl_AVAILABLE = False
    logging.warning("cuML not available, Naive Bayes will use CPU fallback")

from src.algorithms.base import GPUAcceleratedAlgorithm
from src.algorithms.metadata import AlgorithmFingerprint
from src.gpu.core.hardware_abstraction import AllocationRequest, GPUResourceManager, StrategyPriority

logger = logging.getLogger(__name__)


class NaiveBayesAlgorithm(GPUAcceleratedAlgorithm):
    """
    Naive Bayes algorithm for trading signal classification.

    Uses probabilistic Naive Bayes algorithms to classify market data into
    buy/sell/hold signals based on feature independence assumptions.
            # type: ignore[E0601]  # Pylint false positive - imports available in all code paths
    Supports multiple variants: Gaussian, Multinomial, and Complement NB.
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.model = None
        self.scaler = None
        self.feature_names: List[str] = []
        self.gpu_manager: Optional[GPUResourceManager] = None
        self.variant = "gaussian"

        # Default parameters for different variants
        self.default_params = {
            "gaussian": {"var_smoothing": 1e-9},
            "multinomial": {"alpha": 1.0, "fit_prior": True, "class_prior": None},
            "complement": {"alpha": 1.0, "fit_prior": True, "norm": False},
        }

    async def initialize_gpu_context(self):
        """Initialize GPU context for Naive Bayes operations."""
        if not self.gpu_enabled:
            return

        try:
            from src.gpu.core.hardware_abstraction import GPUResourceManager

            self.gpu_manager = GPUResourceManager()

            if not self.gpu_manager.initialize():
                logger.warning("GPU manager initialization failed, falling back to CPU")
                await self.fallback_to_cpu()
                return

            from src.gpu.core.hardware_abstraction import AllocationRequest, StrategyPriority
            gpu_id = await self.gpu_manager.allocate_context(
                request=AllocationRequest(
                    strategy_id=f"nb_{self.metadata.name}",
                    priority=StrategyPriority.MEDIUM,
                    required_memory=self.gpu_memory_limit or 1024,
                    required_compute_streams=1,
                    performance_profile=None,
                ),
            )
            if gpu_id is not None:  # pylint: disable=possibly-used-before-assignment
                logger.info("Naive Bayes algorithm allocated GPU %(gpu_id)s")
            else:
                logger.warning("Failed to allocate GPU, falling back to CPU")
                await self.fallback_to_cpu()

        except Exception as e:
            logger.error("GPU context initialization failed: %(e)s")
            await self.fallback_to_cpu()

    async def release_gpu_context(self):
        """Release GPU resources."""
        if self.gpu_manager and not self.gpu_enabled:
            try:
                self.gpu_manager.release_context(f"nb_{self.metadata.name}")
                logger.info("Naive Bayes GPU resources released")
            except Exception as e:
                logger.error("GPU resource release failed: %(e)s")

    async def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train Naive Bayes model on historical data.

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
            self.variant = config.get("variant", "gaussian").lower()

            if self.variant not in ["gaussian", "multinomial", "complement"]:
                raise ValueError(f"Unsupported Naive Bayes variant: {self.variant}")

            if not feature_cols:
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                feature_cols = [col for col in numeric_cols if col != target_col]

            if target_col not in data.columns:
                raise ValueError(f"Target column '{target_col}' not found in data")

            self.feature_names = feature_cols
            X = data[feature_cols].values
            y = data[target_col].values

            if self.gpu_enabled and not self.gpu_manager:
                X_scaled = X  # Initialize to default value
                await self.initialize_gpu_context()

            nb_params = self.default_params[self.variant].copy()
            nb_params.update(config.get("naive_bayes_params", {}))

            if self.gpu_enabled and CUMl_AVAILABLE:
                if self.variant == "gaussian":
                    self.scaler = GPUStandardScaler()
                    X_scaled = self.scaler.fit_transform(X)
                    self.model = GaussianNB(**nb_params)  # pylint: disable=used-before-assignment
                elif self.variant == "multinomial":
                    # Multinomial NB works with raw counts/frequencies
                    X_scaled = X
                    self.scaler = None
                    self.model = MultinomialNB(**nb_params)  # pylint: disable=used-before-assignment
                elif self.variant == "complement":
                    X_scaled = X
                    self.scaler = None
                    self.model = ComplementNB(**nb_params)  # pylint: disable=used-before-assignment

                self.model.fit(X_scaled, y)  # pylint: disable=possibly-used-before-assignment
                logger.info("Training {self.variant} Naive Bayes on GPU")

            else:
                from sklearn.naive_bayes import ComplementNB, GaussianNB, MultinomialNB
                from sklearn.preprocessing import StandardScaler

                if self.variant == "gaussian":
                    self.scaler = StandardScaler()
                    X_scaled = self.scaler.fit_transform(X)
                    self.model = GaussianNB(**nb_params)
                elif self.variant == "multinomial":
                    X_scaled = X
                    self.scaler = None
                    self.model = MultinomialNB(**nb_params)
                elif self.variant == "complement":
                    X_scaled = X
                    self.scaler = None
                    self.model = ComplementNB(**nb_params)

                self.model.fit(X_scaled, y)
                logger.info("Training {self.variant} Naive Bayes on CPU")

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
                    "variant": self.variant,
                    "training_time": 0.0,
                    "gpu_used": self.gpu_enabled,
                },
                "fingerprint": fingerprint,
                "config": config,
                "trained_at": pd.Timestamp.now(),
            }

            self.is_trained = True
            self.update_metadata(last_trained=pd.Timestamp.now())

            logger.info("Naive Bayes ({self.variant}) training completed - Accuracy: %(accuracy)s")
            return training_result

        except Exception as e:
            logger.error("Naive Bayes training failed: %(e)s")
            raise

    async def predict(self, data: pd.DataFrame, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using trained Naive Bayes model.

        Args:
            data: Input data for prediction
            model: Trained model from train() method

        Returns:
            Dictionary containing predictions and confidence scores
        """
        try:
            nb_model = model["model"]
            scaler = model["scaler"]
            feature_names = model["feature_names"]

            missing_features = [col for col in feature_names if col not in data.columns]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")

            X = data[feature_names].values

            if scaler:
                X_scaled = scaler.transform(X)
            else:
                X_scaled = X

            predictions = nb_model.predict(X_scaled)
            probabilities = nb_model.predict_proba(X_scaled)
            confidence_scores = np.max(probabilities, axis=1)

            results = []
            for i, (pred, conf) in enumerate(zip(predictions, confidence_scores)):
                result = {
                    "prediction": int(pred),
                    "confidence": float(conf),
                    "probabilities": {f"class_{j}": float(prob) for j, prob in enumerate(probabilities[i])},
                    "features_used": {name: float(data.iloc[i][name]) for name in feature_names},
                }
                results.append(result)

            return {
                "predictions": results,
                "n_predictions": len(results),
                "feature_names": feature_names,
                "variant": self.variant,
                "prediction_time": 0.0,
                "gpu_used": self.gpu_enabled,
            }

        except Exception as e:
            logger.error("Naive Bayes prediction failed: %(e)s")
            raise

    def evaluate(self, predictions: Dict[str, Any], actual: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate Naive Bayes predictions against actual values.

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
                # Initialize metrics to avoid E0606 errors
                precision = recall = f1 = 0.0
                from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
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

        except Exception as e:
            logger.error("Naive Bayes evaluation failed: %(e)s")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the trained model."""
        if not self.is_trained or not self.model:
            return {"status": "not_trained"}

        return {
            "algorithm_type": self.algorithm_type.value,
            "is_trained": self.is_trained,
            "feature_names": self.feature_names,
            "variant": self.variant,
            "gpu_enabled": self.gpu_enabled,
            "model_params": self.model.get_params() if hasattr(self.model, "get_params") else {},
            "class_priors": self._get_class_priors(),
            "metadata": self.metadata.__dict__,
        }

    def _get_class_priors(self) -> Optional[Dict[str, float]]:
        """Get class prior probabilities."""
        if not self.model or not hasattr(self.model, "class_count_"):
            return None

        try:
            total_samples = np.sum(self.model.class_count_)
            priors = self.model.class_count_ / total_samples
            return {f"class_{i}": float(prior) for i, prior in enumerate(priors)}
        except:
            return None

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
                "variant": self.variant,
                "metadata": self.metadata,
                "gpu_enabled": self.gpu_enabled,
            }

            joblib.dump(model_data, filepath)
            logger.info("Naive Bayes model saved to %(filepath)s")
            return True

        except Exception as e:
            logger.error("Failed to save Naive Bayes model: %(e)s")
            return False

    def load_model(self, filepath: str) -> bool:
        """Load trained model from file."""
        try:
            import joblib

            model_data = joblib.load(filepath)

            self.model = model_data["model"]
            self.scaler = model_data["scaler"]
            self.feature_names = model_data["feature_names"]
            self.variant = model_data.get("variant", "gaussian")
            self.metadata = model_data["metadata"]
            self.gpu_enabled = model_data.get("gpu_enabled", False)
            self.is_trained = True

            logger.info("Naive Bayes model loaded from %(filepath)s")
            return True

        except Exception as e:
            logger.error("Failed to load Naive Bayes model: %(e)s")
            return False
