"""
Classification Manager for Quantitative Trading Algorithms.

This module provides a unified interface for managing and using all
classification algorithms (SVM, Decision Trees, Naive Bayes) in the
quantitative trading system. It handles algorithm selection, training,
prediction, and performance evaluation.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from src.algorithms.base import AlgorithmMetadata, BaseAlgorithm
from src.algorithms.classification.decision_tree_algorithm import DecisionTreeAlgorithm
from src.algorithms.classification.naive_bayes_algorithm import NaiveBayesAlgorithm
from src.algorithms.classification.svm_algorithm import SVMAlgorithm
from src.algorithms.types import AlgorithmType

logger = logging.getLogger(__name__)


class ClassificationManager:
    """
    Unified manager for classification algorithms in quantitative trading.

    Provides a single interface for training, prediction, and evaluation
    of multiple classification algorithms. Supports automatic algorithm
    selection based on data characteristics and performance metrics.
    """

    def __init__(self):
        self.algorithms: Dict[str, BaseAlgorithm] = {}
        self.trained_models: Dict[str, Dict[str, Any]] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # Algorithm mapping
        self.algorithm_classes = {
            AlgorithmType.SVM: SVMAlgorithm,
            AlgorithmType.DECISION_TREE: DecisionTreeAlgorithm,
            AlgorithmType.NAIVE_BAYES: NaiveBayesAlgorithm,
        }

    def create_algorithm(
        self, algorithm_type: AlgorithmType, name: str, config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new algorithm instance.

        Args:
            algorithm_type: Type of algorithm to create
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

        # Apply configuration if provided
        if config:
            if hasattr(algorithm, "default_params"):
                algorithm.default_params.update(config.get("params", {}))

        self.algorithms[name] = algorithm
        self.performance_history[name] = []

        logger.info("Created {algorithm_type.value} algorithm: %(name)s")
        return name

    async def train_algorithm(self, algorithm_name: str, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train a specific algorithm on provided data.

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
        logger.info("Training algorithm: %(algorithm_name)s")

        # Train the algorithm
        training_result = await algorithm.train(data, config)

        # Store the trained model
        self.trained_models[algorithm_name] = training_result

        # Record performance
        performance_record = {
            "timestamp": datetime.now(),
            "algorithm_type": algorithm.algorithm_type.value,
            "training_metrics": training_result["training_metrics"],
            "config": config,
        }
        self.performance_history[algorithm_name].append(performance_record)

        logger.info("Algorithm %(algorithm_name)s training completed")
        return training_result

    async def predict_with_algorithm(
        self, algorithm_name: str, data: pd.DataFrame, model: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate predictions using a trained algorithm.

        Args:
            algorithm_name: Name of the algorithm to use
            data: Input data for prediction
            model: Optional specific model to use (defaults to last trained)

        Returns:
            Prediction results
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]

        if not algorithm.is_trained and not model:
            raise ValueError(f"Algorithm '{algorithm_name}' is not trained")

        # Use provided model or last trained model
        prediction_model = model or self.trained_models.get(algorithm_name)
        if not prediction_model:
            raise ValueError(f"No trained model available for '{algorithm_name}'")

        return await algorithm.predict(data, prediction_model)

    def evaluate_algorithm(
        self, algorithm_name: str, predictions: Dict[str, Any], actual: pd.DataFrame
    ) -> Dict[str, float]:
        """
        Evaluate algorithm predictions against actual values.

        Args:
            algorithm_name: Name of the algorithm
            predictions: Predictions from predict method
            actual: Actual target values

        Returns:
            Evaluation metrics
        """
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        return algorithm.evaluate(predictions, actual)

    async def compare_algorithms(
        self, algorithm_names: List[str], test_data: pd.DataFrame, test_labels: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Compare multiple algorithms on the same test data.

        Args:
            algorithm_names: List of algorithm names to compare
            test_data: Test input data
            test_labels: Actual labels for evaluation

        Returns:
            Comparison results for all algorithms
        """
        results = {}

        for name in algorithm_names:
            if name not in self.algorithms:
                logger.warning("Algorithm '%(name)s' not found, skipping")
                continue

            try:
                # Generate predictions
                predictions = await self.predict_with_algorithm(name, test_data)

                # Evaluate performance
                metrics = self.evaluate_algorithm(name, predictions, test_labels)

                results[name] = {
                    "predictions": predictions,
                    "metrics": metrics,
                    "algorithm_type": self.algorithms[name].algorithm_type.value,
                    "trained": self.algorithms[name].is_trained,
                }

            except Exception as e:
                logger.error("Failed to evaluate algorithm '%(name)s': %(e)s")
                results[name] = {"error": str(e)}

        return results

    def get_algorithm_info(self, algorithm_name: str) -> Dict[str, Any]:
        """Get information about a specific algorithm."""
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm '{algorithm_name}' not found")

        algorithm = self.algorithms[algorithm_name]
        return algorithm.get_model_info()

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

        # Try to load and determine algorithm type
        try:
            import joblib

            model_data = joblib.load(filepath)

            # Determine algorithm type from loaded data
            if "model" in model_data:
                model = model_data["model"]
                if hasattr(model, "_impl") and "svm" in str(type(model)).lower():
                    algorithm_type = AlgorithmType.SVM
                elif hasattr(model, "n_estimators"):
                    algorithm_type = AlgorithmType.DECISION_TREE
                elif hasattr(model, "class_count_"):
                    algorithm_type = AlgorithmType.NAIVE_BAYES
                else:
                    raise ValueError("Cannot determine algorithm type from saved model")

                # Create algorithm instance
                metadata = model_data.get("metadata")
                if not metadata:
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

        except Exception as e:
            logger.error("Failed to load algorithm from %(filepath)s: %(e)s")
            return False

    def get_performance_history(self, algorithm_name: str) -> List[Dict[str, Any]]:
        """Get performance history for an algorithm."""
        return self.performance_history.get(algorithm_name, [])

    def recommend_algorithm(self, data_characteristics: Dict[str, Any]) -> AlgorithmType:
        """
        Recommend the best algorithm based on data characteristics.

        Args:
            data_characteristics: Dictionary describing the data
                (e.g., {'n_samples': 1000, 'n_features': 10, 'data_type': 'continuous'})

        Returns:
            Recommended algorithm type
        """
        n_samples = data_characteristics.get("n_samples", 1000)
        n_features = data_characteristics.get("n_features", 10)
        data_type = data_characteristics.get("data_type", "mixed")

        # Simple recommendation logic
        if n_samples < 1000:
            return AlgorithmType.NAIVE_BAYES  # Works well with small datasets
        elif n_features > 50:
            return AlgorithmType.SVM  # Good with high-dimensional data
        elif data_type == "categorical" or n_features < 10:
            return AlgorithmType.DECISION_TREE  # Interpretable, handles mixed data
        else:
            return AlgorithmType.SVM  # Default choice

    def cleanup(self):
        """Clean up resources and GPU contexts."""
        for algorithm in self.algorithms.values():
            if hasattr(algorithm, "release_gpu_context"):
                try:
                    import asyncio

                    asyncio.create_task(algorithm.release_gpu_context())
                except:
                    pass

        self.algorithms.clear()
        self.trained_models.clear()
        self.performance_history.clear()

        logger.info("ClassificationManager cleaned up")
