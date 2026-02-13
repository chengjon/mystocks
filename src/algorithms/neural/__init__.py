"""
Neural Network Manager for Advanced Quantitative Trading Algorithms.

This module provides a unified interface for managing and using advanced
neural algorithms (N-gram models and Neural Networks) in the quantitative
trading system. It handles algorithm selection, training, and inference
for complex sequential modeling and deep learning tasks.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pandas as pd
import numpy as np

from src.algorithms.base import AlgorithmMetadata, BaseAlgorithm
from src.algorithms.neural.neural_network_algorithm import NeuralNetworkAlgorithm
from src.algorithms.ngram.ngram_algorithm import NGramAlgorithm
from src.algorithms.types import AlgorithmType

logger = logging.getLogger(__name__)


class NeuralNetworkManager:
    """
    Unified manager for advanced neural algorithms.

    Provides a single interface for sequential modeling and deep learning
    using N-gram models and Neural Networks. Supports automatic algorithm
    selection based on problem characteristics and performance requirements.
    """

    def __init__(self):
        self.algorithms: Dict[str, BaseAlgorithm] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # Algorithm mapping
        self.algorithm_classes = {
            AlgorithmType.N_GRAM: NGramAlgorithm,
            AlgorithmType.NEURAL_NETWORK: NeuralNetworkAlgorithm,
        }

        # Problem type mappings for neural algorithms
        self.problem_mappings = {
            "sequence_prediction": AlgorithmType.N_GRAM,
            "pattern_recognition": AlgorithmType.N_GRAM,
            "time_series_forecasting": AlgorithmType.NEURAL_NETWORK,
            "sequential_modeling": AlgorithmType.NEURAL_NETWORK,
            "complex_feature_learning": AlgorithmType.NEURAL_NETWORK,
            "market_prediction": AlgorithmType.NEURAL_NETWORK,
            "text_sequence_analysis": AlgorithmType.N_GRAM,
        }

    def create_algorithm(
        self, algorithm_type: AlgorithmType, name: str, config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new neural algorithm instance.

        Args:
            algorithm_type: Type of algorithm to create (N-gram or Neural Network)
            name: Unique name for the algorithm
            config: Optional configuration parameters

        Returns:
            Algorithm ID for future reference
        """
        if name in self.algorithms:
            raise ValueError(f"Algorithm with name '{name}' already exists")

        if algorithm_type not in self.algorithm_classes:
            raise ValueError(f"Unsupported algorithm type: {algorithm_type}")

        # Create metadata
        metadata = AlgorithmMetadata(
            algorithm_type=algorithm_type,
            name=name,
            version="1.0.0",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            description=config.get("description") if config else None,
        )

        # Create algorithm instance
        algorithm_class = self.algorithm_classes[algorithm_type]
        algorithm = algorithm_class(metadata)

        self.algorithms[name] = algorithm
        self.performance_history[name] = []

        logger.info("Created {algorithm_type.value} algorithm: %(name)s")
        return name

    async def train_algorithm(
        self, algorithm_name: str, data: Union[List[float], pd.Series, pd.DataFrame], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Train a neural algorithm on provided data.

        Args:
            algorithm_name: Name of the algorithm to train
            data: Training data
            config: Training configuration

        Returns:
            Training results including metrics and model
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        start_time = datetime.now()

        logger.info("Training neural algorithm: %(algorithm_name)s ({algorithm.algorithm_type.value})")

        # Convert data to DataFrame if needed
        if isinstance(data, (list, np.ndarray)):
            if isinstance(data[0], (list, np.ndarray)):
                # Sequence data
                df_data = pd.DataFrame({"sequence": data})
            else:
                # Single sequence
                df_data = pd.DataFrame({"sequence": [data]})
        elif isinstance(data, pd.Series):
            df_data = pd.DataFrame({"sequence": data})
        else:
            df_data = data

        # Train the algorithm
        if algorithm.algorithm_type == AlgorithmType.N_GRAM:
            training_result = await algorithm.train(df_data, config)
        elif algorithm.algorithm_type == AlgorithmType.NEURAL_NETWORK:
            training_result = await algorithm.train(df_data, config)
        else:
            raise ValueError(f"Unsupported algorithm type for training: {algorithm.algorithm_type}")

        # Record performance
        execution_time = (datetime.now() - start_time).total_seconds()
        performance_record = {
            "timestamp": datetime.now(),
            "algorithm_type": algorithm.algorithm_type.value,
            "training_metrics": training_result.get("training_metrics", {}),
            "execution_time": execution_time,
            "config": config,
            "data_size": len(df_data) if hasattr(df_data, "__len__") else "unknown",
        }
        self.performance_history[algorithm_name].append(performance_record)

        logger.info("Algorithm %(algorithm_name)s training completed in {execution_time:.2f}s")
        return training_result

    async def predict_with_algorithm(
        self,
        algorithm_name: str,
        data: Union[List[float], pd.Series, pd.DataFrame],
        model: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate predictions using a trained neural algorithm.

        Args:
            algorithm_name: Name of the algorithm to use
            data: Input data for prediction
            model: Optional specific model to use

        Returns:
            Prediction results
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]

        if not algorithm.is_trained and not model:
            raise ValueError(f"Algorithm '{algorithm_name}' is not trained")

        # Convert data format if needed
        if isinstance(data, (list, np.ndarray)):
            if isinstance(data[0], (list, np.ndarray)):
                df_data = pd.DataFrame({"sequence": data})
            else:
                df_data = pd.DataFrame({"sequence": [data]})
        elif isinstance(data, pd.Series):
            df_data = pd.DataFrame({"sequence": data})
        else:
            df_data = data

        # Use provided model or last trained model
        prediction_model = model or getattr(algorithm, "_last_model", None)

        return await algorithm.predict(df_data, prediction_model)

    def evaluate_algorithm(
        self,
        algorithm_name: str,
        predictions: Dict[str, Any],
        actual: Optional[Union[List[float], pd.Series, pd.DataFrame]] = None,
    ) -> Dict[str, float]:
        """
        Evaluate algorithm predictions.

        Args:
            algorithm_name: Name of the algorithm
            predictions: Predictions from predict method
            actual: Optional actual values for comparison

        Returns:
            Evaluation metrics
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]

        # Convert actual data if provided
        if actual is not None:
            if isinstance(actual, (list, np.ndarray)):
                actual_df = pd.DataFrame({"target": actual})
            elif isinstance(actual, pd.Series):
                actual_df = pd.DataFrame({"target": actual})
            else:
                actual_df = actual
        else:
            actual_df = None

        return algorithm.evaluate(predictions, actual_df)

    def compare_algorithms(
        self, algorithm_names: List[str], data: Union[List[float], pd.Series, pd.DataFrame], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare multiple neural algorithms on the same data.

        Args:
            algorithm_names: List of algorithm names to compare
            data: Test data for analysis
            config: Configuration for comparison

        Returns:
            Comparison results for all algorithms
        """
        import asyncio

        async def run_comparison():
            results = {}
            tasks = []

            for name in algorithm_names:
                if name not in self.algorithms:
                    logger.warning("Algorithm '%(name)s' not found, skipping")
                    continue

                # Create analysis task
                task = self._analyze_algorithm_performance(name, data, config)
                tasks.append((name, task))

            # Execute all analyses concurrently
            for name, task in tasks:
                try:
                    analysis_result = await task
                    results[name] = {
                        "analysis": analysis_result,
                        "algorithm_type": self.algorithms[name].algorithm_type.value,
                        "success": True,
                    }

                except Exception as e:
                    logger.error("Failed to analyze algorithm '%(name)s': %(e)s")
                    results[name] = {"error": str(e), "success": False}

            return results

        return asyncio.run(run_comparison())

    async def _analyze_algorithm_performance(
        self, algorithm_name: str, data: Union[List[float], pd.Series, pd.DataFrame], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze algorithm performance on given data."""
        algorithm = self.algorithms[algorithm_name]

        # Train algorithm
        train_result = await self.train_algorithm(algorithm_name, data, config)

        # Generate predictions
        predictions = await self.predict_with_algorithm(algorithm_name, data)

        # Analyze results
        analysis = self.evaluate_algorithm(algorithm_name, predictions)

        return {
            "training_metrics": train_result.get("training_metrics", {}),
            "prediction_analysis": analysis,
            "model_complexity": self._estimate_model_complexity(algorithm, train_result),
        }

    def _estimate_model_complexity(self, algorithm: BaseAlgorithm, train_result: Dict[str, Any]) -> Dict[str, Any]:
        """Estimate model complexity."""
        if algorithm.algorithm_type == AlgorithmType.N_GRAM:
            n = train_result.get("training_metrics", {}).get("n", 2)
            vocab_size = train_result.get("training_metrics", {}).get("vocab_size", 10)
            return algorithm.estimate_complexity(
                train_result.get("training_metrics", {}).get("n_samples", 1000), vocab_size, n
            )
        elif algorithm.algorithm_type == AlgorithmType.NEURAL_NETWORK:
            seq_length = train_result.get("config", {}).get("sequence_length", 10)
            hidden_units = train_result.get("config", {}).get("neural_network_params", {}).get("hidden_units", [64, 32])
            return algorithm.estimate_complexity(
                train_result.get("training_metrics", {}).get("n_samples", 1000), seq_length, hidden_units
            )
        else:
            return {"complexity": "unknown"}

    def recommend_algorithm(self, problem_characteristics: Dict[str, Any]) -> AlgorithmType:
        """
        Recommend the best neural algorithm based on problem characteristics.

        Args:
            problem_characteristics: Dictionary describing the problem
                (e.g., {'problem_type': 'sequence_prediction', 'data_type': 'symbolic', 'complexity': 'low'})

        Returns:
            Recommended algorithm type
        """
        problem_type = problem_characteristics.get("problem_type", "sequential_modeling")
        data_type = problem_characteristics.get("data_type", "numeric")
        complexity = problem_characteristics.get("complexity", "medium")
        sequence_length = problem_characteristics.get("sequence_length", 10)

        # Direct mapping if problem type is specified
        if problem_type in self.problem_mappings:
            return self.problem_mappings[problem_type]

        # Decision logic based on characteristics
        if data_type == "symbolic" or complexity == "low":
            return AlgorithmType.N_GRAM  # Good for discrete/symbolic sequences
        elif sequence_length > 20 or complexity == "high":
            return AlgorithmType.NEURAL_NETWORK  # Better for long/complex sequences
        elif problem_characteristics.get("temporal_patterns", False):
            return AlgorithmType.NEURAL_NETWORK  # RNN/LSTM for temporal patterns
        elif problem_characteristics.get("probabilistic_output", False):
            return AlgorithmType.N_GRAM  # N-gram gives probabilistic predictions
        else:
            return AlgorithmType.NEURAL_NETWORK  # Default for complex numeric sequences

    def get_algorithm_info(self, algorithm_name: str) -> Dict[str, Any]:
        """Get information about a specific algorithm."""
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        base_info = algorithm.get_algorithm_info()

        # Add manager-specific info
        base_info.update(
            {
                "performance_records": len(self.performance_history[algorithm_name]),
                "last_training": self._get_last_training_time(algorithm_name),
            }
        )

        return base_info

    def _get_last_training_time(self, algorithm_name: str) -> Optional[datetime]:
        """Get the last training time for an algorithm."""
        history = self.performance_history.get(algorithm_name, [])
        if history:
            return history[-1]["timestamp"]
        return None

    def list_algorithms(self) -> List[Dict[str, Any]]:
        """List all created algorithms."""
        return [
            {
                "name": name,
                "type": algorithm.algorithm_type.value,
                "trained": algorithm.is_trained,
                "gpu_enabled": getattr(algorithm, "gpu_enabled", False),
                "created_at": algorithm.metadata.created_at,
                "performance_records": len(self.performance_history[name]),
                "last_training": self._get_last_training_time(name),
            }
            for name, algorithm in self.algorithms.items()
        ]

    def save_algorithm(self, algorithm_name: str, filepath: str) -> bool:
        """Save a trained algorithm to file."""
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        return algorithm.save_model(filepath)

    def load_algorithm(self, algorithm_name: str, filepath: str) -> bool:
        """Load an algorithm from file."""
        if algorithm_name in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' already exists")

        # Try to load and determine algorithm type from file
        try:
            import joblib

            model_data = joblib.load(filepath)

            # Determine algorithm type
            if "ngram_model" in model_data.get("model", {}):
                algorithm_type = AlgorithmType.N_GRAM
            elif "architecture" in model_data:
                algorithm_type = AlgorithmType.NEURAL_NETWORK
            else:
                raise ValueError("Cannot determine algorithm type from saved model")

            # Create algorithm instance
            metadata = model_data.get("metadata")
            if not metadata:
                from src.algorithms.base import AlgorithmMetadata

                metadata = AlgorithmMetadata(
                    algorithm_type=algorithm_type,
                    name=algorithm_name,
                    version="1.0.0",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                )

            algorithm_class = self.algorithm_classes[algorithm_type]
            algorithm = algorithm_class(metadata)

            # Load model data
            success = algorithm.load_model(filepath)
            if success:
                self.algorithms[algorithm_name] = algorithm
                self.performance_history[algorithm_name] = []

            return success

        except Exception:
            logger.error("Failed to load algorithm from %(filepath)s: %(e)s")
            return False

    def get_performance_history(self, algorithm_name: str) -> List[Dict[str, Any]]:
        """Get performance history for an algorithm."""
        return self.performance_history.get(algorithm_name, [])

    def create_ensemble(
        self, algorithm_names: List[str], ensemble_name: str, weights: Optional[Dict[str, float]] = None
    ) -> str:
        """
        Create an ensemble of neural algorithms.

        Args:
            algorithm_names: List of algorithm names to ensemble
            ensemble_name: Name for the ensemble
            weights: Optional weights for each algorithm

        Returns:
            Ensemble algorithm name
        """
        # Validate algorithms exist and are trained
        valid_algorithms = []
        for name in algorithm_names:
            if name not in self.algorithms:
                logger.warning("Algorithm '%(name)s' not found, skipping")
                continue
            if not self.algorithms[name].is_trained:
                logger.warning("Algorithm '%(name)s' is not trained, skipping")
                continue
            valid_algorithms.append(name)

        if len(valid_algorithms) < 2:
            raise ValueError("Need at least 2 valid trained algorithms for ensemble")

        # Create ensemble algorithm (placeholder for future implementation)
        # For now, just store the ensemble configuration
        ensemble_config = {
            "ensemble_name": ensemble_name,
            "algorithms": valid_algorithms,
            "weights": weights or {name: 1.0 / len(valid_algorithms) for name in valid_algorithms},
        }

        # Store in performance history for tracking
        if ensemble_name not in self.performance_history:
            self.performance_history[ensemble_name] = []

        self.performance_history[ensemble_name].append(
            {"timestamp": datetime.now(), "type": "ensemble_created", "config": ensemble_config}
        )

        logger.info("Created ensemble '%(ensemble_name)s' with {len(valid_algorithms)} algorithms")
        return ensemble_name

    def cleanup(self):
        """Clean up resources."""
        for algorithm in self.algorithms.values():
            if hasattr(algorithm, "release_gpu_context"):
                import asyncio

                try:
                    asyncio.create_task(algorithm.release_gpu_context())
                except:
                    pass

        self.algorithms.clear()
        self.performance_history.clear()

        logger.info("NeuralNetworkManager cleaned up")
