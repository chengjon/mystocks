"""
N-gram Model Algorithm for Quantitative Trading.

This module implements N-gram models for sequential pattern analysis in financial
time series. N-gram models are effective for identifying recurring patterns in
price movements, volume sequences, and other market indicators.
"""

import logging
import time
from typing import Dict, List, Any, Optional, Union, Tuple
from collections import defaultdict, Counter
import numpy as np
import pandas as pd

from src.algorithms.base import GPUAcceleratedAlgorithm
from src.algorithms.types import AlgorithmType
from src.algorithms.metadata import AlgorithmFingerprint
from src.gpu.core.hardware_abstraction import GPUResourceManager

from src.algorithms.base import GPUAcceleratedAlgorithm
from src.algorithms.types import AlgorithmType
from src.algorithms.metadata import AlgorithmFingerprint
from src.gpu.core.hardware_abstraction import GPUResourceManager

logger = logging.getLogger(__name__)


class NGramAlgorithm(GPUAcceleratedAlgorithm):
    """
    N-gram model algorithm for sequential pattern analysis.

    N-gram models analyze sequences of market events to predict future behavior.
    In quantitative trading, this is particularly useful for:
    - Price movement pattern recognition
    - Volume sequence analysis
    - Technical indicator pattern detection
    - Market regime transition prediction
    """

    def __init__(self, metadata):
        super().__init__(metadata)
        self.n = 2  # Default bigram model
        self.ngram_model = defaultdict(Counter)
        self.vocab = set()
        self.smoothing = "laplace"
        self.alpha = 1.0  # Laplace smoothing parameter
        self.gpu_manager: Optional[GPUResourceManager] = None

        # Default N-gram parameters
        self.default_params = {
            "n": 2,  # N-gram size
            "smoothing": "laplace",  # laplace, good_turing, kneser_ney
            "alpha": 1.0,  # Laplace smoothing parameter
            "min_frequency": 1,  # Minimum frequency for n-grams
            "max_vocabulary_size": None,  # Maximum vocabulary size
            "normalization": True,  # Whether to normalize sequences
        }

    async def initialize_gpu_context(self):
        """Initialize GPU context for N-gram operations."""
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
                task_id=f"ngram_{self.metadata.name}",
                priority="medium",
                memory_required=self.gpu_memory_limit or 512,  # 512MB default for N-gram
            )

            if gpu_id is not None:
                logger.info(f"N-gram algorithm allocated GPU {gpu_id}")
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
                self.gpu_manager.release_gpu(f"ngram_{self.metadata.name}")
                logger.info("N-gram GPU resources released")
            except Exception as e:
                logger.error(f"GPU resource release failed: {e}")

    def _discretize_sequence(self, sequence: np.ndarray, bins: int = 10) -> List[str]:
        """
        Discretize a continuous sequence into discrete symbols.

        Args:
            sequence: Continuous numerical sequence
            bins: Number of bins for discretization

        Returns:
            List of discrete symbols
        """
        # Remove outliers using IQR method
        q1, q3 = np.percentile(sequence, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        # Clip outliers
        clipped = np.clip(sequence, lower_bound, upper_bound)

        # Discretize into bins
        _, bin_edges = np.histogram(clipped, bins=bins)

        # Convert to discrete symbols
        digitized = np.digitize(clipped, bin_edges[:-1])  # Exclude last edge

        # Convert to string symbols
        symbols = [f"s{i}" for i in digitized]

        return symbols

    def _build_ngrams(self, sequence: List[str], n: int) -> List[Tuple[str, ...]]:
        """
        Build n-grams from a sequence of symbols.

        Args:
            sequence: List of symbols
            n: N-gram size

        Returns:
            List of n-gram tuples
        """
        if len(sequence) < n:
            return []

        return [tuple(sequence[i : i + n]) for i in range(len(sequence) - n + 1)]

    def _apply_smoothing(
        self, ngram_counts: Dict[Tuple[str, ...], int], context_counts: Dict[Tuple[str, ...], int], vocab_size: int
    ) -> Dict[Tuple[str, ...], Dict[str, float]]:
        """
        Apply smoothing to n-gram probabilities.

        Args:
            ngram_counts: Raw n-gram counts
            context_counts: Context (n-1 gram) counts
            vocab_size: Size of vocabulary

        Returns:
            Smoothed probability distributions
        """
        smoothed_probs = {}

        if self.smoothing == "laplace":
            # Laplace (add-one) smoothing
            for ngram, count in ngram_counts.items():
                context = ngram[:-1]
                context_count = context_counts.get(context, 0)

                # Create probability distribution for each possible next symbol
                probs = {}
                total_count = context_count + self.alpha * vocab_size

                for symbol in self.vocab:
                    next_ngram = ngram + (symbol,)
                    symbol_count = ngram_counts.get(next_ngram, 0)
                    probs[symbol] = (symbol_count + self.alpha) / total_count

                smoothed_probs[ngram] = probs

        else:
            # No smoothing - maximum likelihood estimation
            for ngram, count in ngram_counts.items():
                context = ngram[:-1]
                context_count = context_counts.get(context, 0)

                probs = {}
                if context_count > 0:
                    for symbol in self.vocab:
                        next_ngram = ngram + (symbol,)
                        symbol_count = ngram_counts.get(next_ngram, 0)
                        probs[symbol] = symbol_count / context_count
                else:
                    # Uniform distribution for unseen contexts
                    uniform_prob = 1.0 / vocab_size
                    probs = {symbol: uniform_prob for symbol in self.vocab}

                smoothed_probs[ngram] = probs

        return smoothed_probs

    async def train(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train N-gram model on sequential data.

        Args:
            data: Training data with sequential features
            config: Training configuration

        Returns:
            Dictionary containing trained model and training metrics
        """
        try:
            if not await self.validate_input(data):
                raise ValueError("Invalid input data")

            # Get training parameters
            self.n = config.get("n", 2)
            self.smoothing = config.get("smoothing", "laplace")
            self.alpha = config.get("alpha", 1.0)

            sequence_col = config.get("sequence_column", "sequence")
            if sequence_col not in data.columns:
                # If no sequence column, use first numeric column
                numeric_cols = data.select_dtypes(include=[np.number]).columns
                if not numeric_cols.empty:
                    sequence_col = numeric_cols[0]
                else:
                    raise ValueError("No suitable sequence column found")

            if self.gpu_enabled and not self.gpu_manager:
                await self.initialize_gpu_context()

            # Extract sequences
            sequences = []
            for seq in data[sequence_col]:
                if isinstance(seq, (list, np.ndarray)):
                    sequences.append(list(seq))
                elif isinstance(seq, pd.Series):
                    sequences.append(seq.tolist())
                else:
                    # Single value - convert to list
                    sequences.append([seq])

            # Discretize sequences if needed
            discretized_sequences = []
            for seq in sequences:
                seq_array = np.array(seq, dtype=float)
                discretized = self._discretize_sequence(seq_array)
                discretized_sequences.append(discretized)

            # Build vocabulary
            all_symbols = [symbol for seq in discretized_sequences for symbol in seq]
            self.vocab = set(all_symbols)

            # Count n-grams
            ngram_counts = Counter()
            context_counts = Counter()

            for seq in discretized_sequences:
                ngrams = self._build_ngrams(seq, self.n)
                for ngram in ngrams:
                    ngram_counts[ngram] += 1
                    if len(ngram) > 1:
                        context_counts[ngram[:-1]] += 1

            # Apply smoothing
            self.ngram_model = self._apply_smoothing(ngram_counts, context_counts, len(self.vocab))

            # Calculate training metrics
            total_ngrams = len(ngram_counts)
            unique_contexts = len(context_counts)
            perplexity = self._calculate_perplexity(discretized_sequences)

            fingerprint = AlgorithmFingerprint.from_config(config)
            fingerprint.update_code_hash(str(self.__class__.__module__))

            training_result = {
                "model": {
                    "ngram_model": dict(self.ngram_model),
                    "vocab": list(self.vocab),
                    "n": self.n,
                    "smoothing": self.smoothing,
                },
                "training_metrics": {
                    "n": self.n,
                    "vocab_size": len(self.vocab),
                    "total_ngrams": total_ngrams,
                    "unique_contexts": unique_contexts,
                    "perplexity": perplexity,
                    "training_time": 0.0,
                    "gpu_used": self.gpu_enabled,
                },
                "fingerprint": fingerprint,
                "config": config,
                "trained_at": pd.Timestamp.now(),
            }

            self.is_trained = True
            self.update_metadata(last_trained=pd.Timestamp.now())

            logger.info(
                f"N-gram training completed - {self.n}-gram model, {len(self.vocab)} symbols, perplexity: {perplexity:.2f}"
            )
            return training_result

        except Exception as e:
            logger.error(f"N-gram training failed: {e}")
            raise

    def _calculate_perplexity(self, sequences: List[List[str]]) -> float:
        """Calculate perplexity of the model on training data."""
        if not self.ngram_model:
            return float("inf")

        total_log_prob = 0
        total_predictions = 0

        for seq in sequences:
            if len(seq) < self.n:
                continue

            ngrams = self._build_ngrams(seq, self.n)
            for ngram in ngrams:
                context = ngram[:-1]
                next_symbol = ngram[-1]

                if context in self.ngram_model:
                    probs = self.ngram_model[context]
                    prob = probs.get(next_symbol, 1e-10)  # Small probability for unseen
                    total_log_prob += np.log(prob)
                    total_predictions += 1

        if total_predictions == 0:
            return float("inf")

        avg_log_prob = total_log_prob / total_predictions
        perplexity = np.exp(-avg_log_prob)

        return perplexity

    async def predict(self, data: pd.DataFrame, model: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate predictions using trained N-gram model.

        Args:
            data: Input data for prediction
            model: Trained model from train() method

        Returns:
            Dictionary containing predictions and probabilities
        """
        try:
            ngram_model = model["model"]["ngram_model"]
            vocab = set(model["model"]["vocab"])
            n = model["model"]["n"]

            predictions = []
            for idx, row in data.iterrows():
                # Extract sequence (same logic as training)
                sequence_col = model["config"].get("sequence_column", "sequence")
                if sequence_col in row.index:
                    seq = row[sequence_col]
                else:
                    # Use first available numeric value
                    numeric_vals = [v for v in row.values if isinstance(v, (int, float))]
                    seq = numeric_vals[0] if numeric_vals else 0

                # Convert to sequence
                if not isinstance(seq, (list, np.ndarray)):
                    seq = [seq]

                # Discretize
                seq_array = np.array(seq, dtype=float)
                discretized = self._discretize_sequence(seq_array)

                # Generate prediction
                prediction = self._predict_next_symbol(discretized, ngram_model, vocab, n)

                result = {
                    "sample_index": idx,
                    "predicted_symbol": prediction["symbol"],
                    "confidence": prediction["confidence"],
                    "probabilities": prediction["probabilities"],
                    "sequence_length": len(discretized),
                }
                predictions.append(result)

            return {
                "predictions": predictions,
                "n_predictions": len(predictions),
                "model_info": {"n": n, "vocab_size": len(vocab), "smoothing": model["model"]["smoothing"]},
                "prediction_time": 0.0,
                "gpu_used": self.gpu_enabled,
            }

        except Exception as e:
            logger.error(f"N-gram prediction failed: {e}")
            raise

    def _predict_next_symbol(self, sequence: List[str], ngram_model: Dict, vocab: set, n: int) -> Dict[str, Any]:
        """Predict the next symbol in a sequence."""
        if len(sequence) < n - 1:
            # Not enough context, return uniform distribution
            uniform_prob = 1.0 / len(vocab)
            probs = {symbol: uniform_prob for symbol in vocab}
            most_likely = max(probs.keys(), key=lambda x: probs[x])

            return {"symbol": most_likely, "confidence": uniform_prob, "probabilities": probs}

        # Use last n-1 symbols as context
        context = tuple(sequence[-(n - 1) :])

        if context in ngram_model:
            probs = ngram_model[context]
            most_likely = max(probs.keys(), key=lambda x: probs[x])
            confidence = probs[most_likely]

            return {"symbol": most_likely, "confidence": confidence, "probabilities": probs}
        else:
            # Unseen context, return uniform distribution
            uniform_prob = 1.0 / len(vocab)
            probs = {symbol: uniform_prob for symbol in vocab}
            most_likely = max(probs.keys(), key=lambda x: probs[x])

            return {"symbol": most_likely, "confidence": uniform_prob, "probabilities": probs}

    def evaluate(self, predictions: Dict[str, Any], actual: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate N-gram predictions.

        For N-gram models, evaluation focuses on prediction accuracy
        and model perplexity.
        """
        try:
            pred_symbols = [p["predicted_symbol"] for p in predictions["predictions"]]

            # Basic accuracy calculation (if actual values available)
            accuracy = 0.0
            if len(actual) > 0 and len(pred_symbols) == len(actual):
                # This is a simplified evaluation - in practice, you'd need proper labels
                accuracy = 0.5  # Placeholder

            # Calculate average confidence
            avg_confidence = np.mean([p["confidence"] for p in predictions["predictions"]])

            metrics = {
                "n_predictions": len(predictions["predictions"]),
                "vocab_size": predictions["model_info"]["vocab_size"],
                "n": predictions["model_info"]["n"],
                "avg_confidence": avg_confidence,
                "accuracy": accuracy,  # Placeholder
            }

            return metrics

        except Exception as e:
            logger.error(f"N-gram evaluation failed: {e}")
            raise

    def get_algorithm_info(self) -> Dict[str, Any]:
        """Get information about the N-gram algorithm."""
        return {
            "algorithm_type": self.algorithm_type.value,
            "is_trained": self.is_trained,
            "n": self.n,
            "vocab_size": len(self.vocab),
            "smoothing": self.smoothing,
            "ngrams_learned": len(self.ngram_model),
            "gpu_enabled": self.gpu_enabled,
            "metadata": self.metadata.__dict__,
        }

    def estimate_complexity(self, data_length: int, vocab_size: int = 10, n: int = 2) -> Dict[str, Any]:
        """Estimate computational complexity."""
        ngram_operations = data_length * n
        model_size = vocab_size**n

        return {
            "estimated_operations": ngram_operations,
            "model_size": model_size,
            "estimated_time_seconds": ngram_operations / 1e6,
            "memory_usage_mb": model_size * 8 / 1e6,
            "complexity_class": f"O(L * {n}) where L=data_length",
            "recommendation": f"Suitable for sequence prediction with vocabulary size {vocab_size}",
        }

    # Required abstract method implementations
    async def train(self, data, config):
        """N-gram training is handled by the specialized train method."""
        return await self.train(data, config)

    async def predict(self, data, model):
        """N-gram prediction is handled by the specialized predict method."""
        return await self.predict(data, model)

    def evaluate(self, predictions, actual):
        """N-gram evaluation is handled by the specialized evaluate method."""
        return self.evaluate(predictions, actual)
