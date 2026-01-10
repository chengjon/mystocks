"""
Hidden Markov Model (HMM) Algorithm for Quantitative Trading.

This module implements Hidden Markov Model for market regime detection,
leveraging cuML for GPU-accelerated training and prediction. HMMs are
particularly effective for identifying different market states (bull,
bear, sideways) and predicting regime transitions.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
import numpy as np
import pandas as pd

from src.algorithms.base import GPUAcceleratedAlgorithm
from src.algorithms.types import AlgorithmType
from src.algorithms.metadata import AlgorithmFingerprint
from src.gpu.core.hardware_abstraction import GPUResourceManager

logger = logging.getLogger(__name__)


class HMMAlgorithm(GPUAcceleratedAlgorithm):
    """
    Hidden Markov Model algorithm for market regime detection.

    HMMs model market behavior as a sequence of hidden states (regimes) that
    generate observable outputs (price movements, volatility, etc.). This
    algorithm is particularly effective for:
    - Market regime classification (bull/bear/sideways)
    - Volatility regime detection
    - Trend transition prediction
    - Risk management based on regime changes
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.model = None
        self.scaler = None
        self.n_states = 3  # Default: bull, bear, sideways
        self.gpu_manager: Optional[GPUResourceManager] = None

        # Default HMM parameters
        self.default_params = {
            "n_components": 3,  # Number of hidden states
            "covariance_type": "full",
            "min_covar": 1e-3,
            "startprob_prior": 1.0,
            "transmat_prior": 1.0,
            "algorithm": "viterbi",
            "random_state": 42,
            "n_iter": 100,
            "tol": 1e-2,
            "verbose": False,
            "params": "stmc",
            "init_params": "stmc",
        }

        # Regime labels
        self.regime_labels = {
            0: "bear_market",  # State 0: Bear market
            1: "sideways",  # State 1: Sideways/range-bound
            2: "bull_market",  # State 2: Bull market
        }

    async def initialize_gpu_context(self):
        """Initialize GPU context for HMM operations."""
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
                task_id=f"hmm_{self.metadata.name}",
                priority="medium",
                memory_required=self.gpu_memory_limit or 2048,  # 2GB default for HMM
            )

            if gpu_id is not None:
                logger.info(f"HMM algorithm allocated GPU {gpu_id}")
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
                self.gpu_manager.release_gpu(f"hmm_{self.metadata.name}")
                logger.info("HMM GPU resources released")
            except Exception as e:
                logger.error(f"GPU resource release failed: {e}")

    async def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train HMM model on historical data.

        Args:
            data: Training data with features for regime detection
            config: Training configuration

        Returns:
            Dictionary containing trained model and training metrics
        """
        try:
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")

            # Extract features
            feature_cols = config.get("feature_columns", ["returns", "volume", "volatility"])
            if not all(col in data.columns for col in feature_cols):
                raise ValueError(f"Missing required features: {feature_cols}")

            X = data[feature_cols].values
            self.n_states = config.get("n_states", 3)

            if self.gpu_enabled and not self.gpu_manager:
                await self.initialize_gpu_context()

            # Prepare HMM parameters
            hmm_params = self.default_params.copy()
            hmm_params["n_components"] = self.n_states
            hmm_params.update(config.get("hmm_params", {}))

            # Feature scaling
            if self.gpu_enabled:
                try:
                    from cuml.preprocessing import StandardScaler as GPUStandardScaler

                    self.scaler = GPUStandardScaler()
                    X_scaled = self.scaler.fit_transform(X)
                except ImportError:
                    # Fallback to CPU scaling
                    from sklearn.preprocessing import StandardScaler

                    self.scaler = StandardScaler()
                    X_scaled = self.scaler.fit_transform(X)
            else:
                from sklearn.preprocessing import StandardScaler

                self.scaler = StandardScaler()
                X_scaled = self.scaler.fit_transform(X)

            # Train HMM model
            if self.gpu_enabled:
                # Try GPU implementation first
                try:
                    from cuml.cluster import GaussianMixture as GPUHMM

                    # Use GMM as approximation for HMM on GPU
                    self.model = GPUHMM(n_components=self.n_states, random_state=42)
                    self.model.fit(X_scaled)
                    logger.info("HMM approximated with GPU GMM")
                except (ImportError, AttributeError):
                    # Fallback to CPU HMM
                    await self._train_cpu_hmm(X_scaled, hmm_params)
            else:
                await self._train_cpu_hmm(X_scaled, hmm_params)

            # Calculate training metrics
            y_pred = self.model.predict(X_scaled)
            n_regime_changes = self._count_regime_changes(y_pred)

            fingerprint = AlgorithmFingerprint.from_config(config)
            fingerprint.update_code_hash(str(self.__class__.__module__))

            training_result = {
                "model": self.model,
                "scaler": self.scaler,
                "feature_names": feature_cols,
                "n_states": self.n_states,
                "regime_labels": self.regime_labels,
                "training_metrics": {
                    "n_samples": len(X),
                    "n_features": len(feature_cols),
                    "n_regime_changes": n_regime_changes,
                    "regime_distribution": self._get_regime_distribution(y_pred),
                    "training_time": 0.0,
                    "gpu_used": self.gpu_enabled,
                },
                "fingerprint": fingerprint,
                "config": config,
                "trained_at": pd.Timestamp.now(),
            }

            self.is_trained = True
            self.update_metadata(last_trained=pd.Timestamp.now())

            logger.info(f"HMM training completed - {self.n_states} states, {n_regime_changes} regime changes")
            return training_result

        except Exception as e:
            logger.error(f"HMM training failed: {e}")
            raise

    async def _train_cpu_hmm(self, X: np.ndarray, params: Dict[str, Any]):
        """Train HMM using CPU implementation."""
        try:
            from hmmlearn import hmm

            self.model = hmm.GaussianHMM(**params)
            self.model.fit(X)
            logger.info("HMM trained on CPU using hmmlearn")
        except ImportError:
            # Fallback to simple Markov chain approximation
            logger.warning("hmmlearn not available, using simplified Markov chain")
            self.model = self._create_simple_markov_chain(X, params)

    def _create_simple_markov_chain(self, X: np.ndarray, params: Dict[str, Any]):
        """Create a simple Markov chain as HMM approximation."""
        from sklearn.cluster import KMeans

        # Use K-means to approximate states
        kmeans = KMeans(n_clusters=self.n_states, random_state=42)
        states = kmeans.fit_predict(X)

        # Calculate transition probabilities
        n_samples = len(states)
        transmat = np.zeros((self.n_states, self.n_states))

        for i in range(n_samples - 1):
            transmat[states[i], states[i + 1]] += 1

        # Normalize rows
        transmat = transmat / transmat.sum(axis=1, keepdims=True)

        # Simple mock HMM object
        class SimpleHMM:
            def __init__(self, transmat, n_states):
                self.transmat_ = transmat
                self.n_components = n_states
                self.means_ = kmeans.cluster_centers_
                self.covars_ = np.array([np.cov(X[states == i].T) for i in range(n_states)])

            def predict(self, X):
                return kmeans.predict(X)

            def score(self, X):
                return kmeans.score(X)

        return SimpleHMM(transmat, self.n_states)

    async def predict(self, data: pd.DataFrame, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict market regimes using trained HMM.

        Args:
            data: Input data for regime prediction
            model: Trained model from train() method

        Returns:
            Dictionary containing regime predictions
        """
        try:
            hmm_model = model["model"]
            scaler = model["scaler"]
            feature_names = model["feature_names"]

            # Validate input
            missing_features = [col for col in feature_names if col not in data.columns]
            if missing_features:
                raise ValueError(f"Missing required features: {missing_features}")

            X = data[feature_names].values

            # Scale features
            if scaler:
                X_scaled = scaler.transform(X)
            else:
                X_scaled = X

            # Predict regimes
            regimes = hmm_model.predict(X_scaled)

            # Convert to regime labels
            regime_labels = [self.regime_labels.get(r, f"state_{r}") for r in regimes]

            # Calculate regime probabilities if available
            try:
                regime_probs = hmm_model.predict_proba(X_scaled)
                probabilities = regime_probs.tolist()
            except AttributeError:
                # Fallback: equal probability for predicted state
                probabilities = []
                for r in regimes:
                    prob = [0.0] * self.n_states
                    prob[r] = 1.0
                    probabilities.append(prob)

            results = []
            for i, (regime, label, probs) in enumerate(zip(regimes, regime_labels, probabilities)):
                result = {
                    "regime": int(regime),
                    "regime_label": label,
                    "confidence": float(max(probs)),
                    "probabilities": {f"state_{j}": float(p) for j, p in enumerate(probs)},
                    "features_used": {name: float(data.iloc[i][name]) for name in feature_names},
                }
                results.append(result)

            return {
                "predictions": results,
                "n_predictions": len(results),
                "n_states": self.n_states,
                "regime_labels": self.regime_labels,
                "feature_names": feature_names,
                "prediction_time": 0.0,
                "gpu_used": self.gpu_enabled,
            }

        except Exception as e:
            logger.error(f"HMM prediction failed: {e}")
            raise

    def evaluate(self, predictions: Dict[str, Any], actual: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate HMM regime predictions.

        For HMM, evaluation focuses on regime stability and transition patterns
        rather than traditional classification metrics.
        """
        try:
            pred_regimes = np.array([p["regime"] for p in predictions["predictions"]])

            # Calculate regime metrics
            n_regime_changes = self._count_regime_changes(pred_regimes)
            regime_stability = self._calculate_regime_stability(pred_regimes)
            regime_distribution = self._get_regime_distribution(pred_regimes)

            metrics = {
                "n_regime_changes": n_regime_changes,
                "regime_stability": regime_stability,
                "regime_distribution": regime_distribution,
                "n_predictions": len(pred_regimes),
                "n_states": self.n_states,
            }

            return metrics

        except Exception as e:
            logger.error(f"HMM evaluation failed: {e}")
            raise

    def _count_regime_changes(self, regimes: np.ndarray) -> int:
        """Count the number of regime changes."""
        if len(regimes) <= 1:
            return 0
        return np.sum(regimes[:-1] != regimes[1:])

    def _calculate_regime_stability(self, regimes: np.ndarray) -> float:
        """Calculate regime stability (lower values = more stable)."""
        if len(regimes) <= 1:
            return 1.0

        changes = self._count_regime_changes(regimes)
        stability = 1.0 - (changes / len(regimes))
        return max(0.0, min(1.0, stability))

    def _get_regime_distribution(self, regimes: np.ndarray) -> Dict[str, float]:
        """Get the distribution of regimes."""
        unique, counts = np.unique(regimes, return_counts=True)
        total = len(regimes)

        distribution = {}
        for regime, count in zip(unique, counts):
            label = self.regime_labels.get(regime, f"state_{regime}")
            distribution[label] = count / total

        return distribution

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the HMM algorithm."""
        base_info = super().get_algorithm_info()
        base_info.update(
            {
                "algorithm_variant": "hidden_markov_model",
                "complexity": "O(n * k^2)",  # n=samples, k=states
                "n_states": self.n_states,
                "regime_labels": self.regime_labels,
                "strengths": ["Regime detection", "Temporal dependencies", "Probabilistic transitions"],
                "weaknesses": ["Computational complexity", "Parameter sensitivity", "Convergence issues"],
                "best_use_case": "Market regime analysis, volatility modeling, trend transition detection",
            }
        )
        return base_info

    def estimate_complexity(self, data_length: int, n_states: int = 3) -> Dict[str, Any]:
        """Estimate computational complexity."""
        operations = data_length * n_states * n_states

        return {
            "estimated_operations": operations,
            "estimated_time_seconds": operations / 1e7,
            "memory_usage_mb": (data_length * n_states * 8) / 1e6,
            "complexity_class": f"O(n * k^2) where k={n_states}",
            "recommendation": f"Excellent for regime detection with {n_states} market states",
        }

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the HMM algorithm."""
        return {
            "algorithm_type": self.algorithm_type.value,
            "is_trained": self.is_trained,
            "n_states": self.n_states,
            "regime_labels": self.regime_labels,
            "gpu_enabled": self.gpu_enabled,
            "model_params": self.default_params,
            "metadata": self.metadata.__dict__,
        }

    # Required abstract method implementations
    async def train(self, data, config):
        """HMM training is handled by the specialized train method."""
        return await self.train(data, config)

    async def predict(self, data, model):
        """HMM prediction is handled by the specialized predict method."""
        return await self.predict(data, model)

    def evaluate(self, predictions, actual):
        """HMM evaluation is handled by the specialized evaluate method."""
        return self.evaluate(predictions, actual)
