"""
Markov-Bayesian Manager for Advanced Quantitative Trading Algorithms.

This module provides a unified interface for managing and using advanced
algorithms (Hidden Markov Models and Bayesian Networks) in the quantitative
trading system. It handles algorithm selection, training, and inference
for complex probabilistic and sequential modeling.
"""

import logging
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import pandas as pd

from src.algorithms.base import BaseAlgorithm, AlgorithmMetadata
from src.algorithms.types import AlgorithmType
from src.algorithms.markov.hmm_algorithm import HMMAlgorithm
from src.algorithms.bayesian.bayesian_network_algorithm import BayesianNetworkAlgorithm

logger = logging.getLogger(__name__)


class MarkovBayesianManager:
    """
    Unified manager for advanced Markov and Bayesian algorithms.

    Provides a single interface for probabilistic modeling and sequential
    analysis using HMMs and Bayesian Networks. Supports automatic algorithm
    selection based on problem characteristics and performance requirements.
    """

    def __init__(self):
        self.algorithms: Dict[str, BaseAlgorithm] = {}
        self.performance_history: Dict[str, List[Dict[str, Any]]] = {}

        # Algorithm mapping
        self.algorithm_classes = {
            AlgorithmType.HIDDEN_MARKOV_MODEL: HMMAlgorithm,
            AlgorithmType.BAYESIAN_NETWORK: BayesianNetworkAlgorithm,
        }

        # Problem type mappings
        self.problem_mappings = {
            "regime_detection": AlgorithmType.HIDDEN_MARKOV_MODEL,
            "sequential_modeling": AlgorithmType.HIDDEN_MARKOV_MODEL,
            "causal_modeling": AlgorithmType.BAYESIAN_NETWORK,
            "probabilistic_inference": AlgorithmType.BAYESIAN_NETWORK,
            "dependency_analysis": AlgorithmType.BAYESIAN_NETWORK,
            "market_state_modeling": AlgorithmType.HIDDEN_MARKOV_MODEL,
            "factor_relationships": AlgorithmType.BAYESIAN_NETWORK,
        }

    def create_algorithm(
        self, algorithm_type: AlgorithmType, name: str, config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new advanced algorithm instance.

        Args:
            algorithm_type: Type of algorithm to create (HMM or BN)
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

        logger.info(f"Created {algorithm_type.value} algorithm: {name}")
        return name

    async def train_algorithm(self, algorithm_name: str, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Train an advanced algorithm on provided data.

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

        logger.info(f"Training advanced algorithm: {algorithm_name} ({algorithm.algorithm_type.value})")

        # Train the algorithm
        if algorithm.algorithm_type == AlgorithmType.HIDDEN_MARKOV_MODEL:
            training_result = await algorithm.train(data, config)
        elif algorithm.algorithm_type == AlgorithmType.BAYESIAN_NETWORK:
            training_result = await algorithm.train(data, config)
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
        }
        self.performance_history[algorithm_name].append(performance_record)

        logger.info(f"Algorithm {algorithm_name} training completed in {execution_time:.2f}s")
        return training_result

    async def predict_with_algorithm(
        self,
        algorithm_name: str,
        data: Union[List[float], pd.Series, pd.DataFrame],
        model: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate predictions using a trained advanced algorithm.

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

        # Use provided model or last trained model
        prediction_model = model or getattr(algorithm, "_last_model", None)
        if not prediction_model:
            raise ValueError(f"No trained model available for '{algorithm_name}'")

        return await algorithm.predict(data, prediction_model)

    def evaluate_algorithm(
        self, algorithm_name: str, predictions: Dict[str, Any], actual: Optional[pd.DataFrame] = None
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

        # For advanced algorithms, evaluation might not always need actual values
        if actual is not None:
            return algorithm.evaluate(predictions, actual)
        else:
            # Return prediction statistics
            return self._analyze_predictions(predictions, algorithm.algorithm_type)

    def _analyze_predictions(self, predictions: Dict[str, Any], algorithm_type: AlgorithmType) -> Dict[str, Any]:
        """Analyze prediction results without ground truth."""
        if algorithm_type == AlgorithmType.HIDDEN_MARKOV_MODEL:
            return self._analyze_hmm_predictions(predictions)
        elif algorithm_type == AlgorithmType.BAYESIAN_NETWORK:
            return self._analyze_bn_predictions(predictions)
        else:
            return {"analysis_type": "unknown"}

    def _analyze_hmm_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze HMM prediction patterns."""
        pred_list = predictions["predictions"]
        regimes = [p["regime"] for p in pred_list]

        # Calculate regime statistics
        from collections import Counter

        regime_counts = Counter(regimes)

        # Calculate transitions
        transitions = 0
        for i in range(1, len(regimes)):
            if regimes[i] != regimes[i - 1]:
                transitions += 1

        return {
            "regime_distribution": dict(regime_counts),
            "total_regime_changes": transitions,
            "regime_stability": 1 - (transitions / len(regimes)) if regimes else 0,
            "most_common_regime": regime_counts.most_common(1)[0][0] if regime_counts else None,
        }

    def _analyze_bn_predictions(self, predictions: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Bayesian Network prediction patterns."""
        pred_list = predictions["predictions"]

        # Analyze probability distributions
        variable_confidences = {}
        for pred in pred_list:
            for var, probs in pred.get("inferred_probabilities", {}).items():
                if var not in variable_confidences:
                    variable_confidences[var] = []
                # Max probability as confidence
                max_prob = max(probs.values()) if probs else 0
                variable_confidences[var].append(max_prob)

        # Calculate average confidences
        avg_confidences = {}
        for var, confs in variable_confidences.items():
            avg_confidences[var] = sum(confs) / len(confs) if confs else 0

        return {
            "variables_analyzed": len(avg_confidences),
            "average_confidences": avg_confidences,
            "total_predictions": len(pred_list),
        }

    def compare_algorithms(
        self, algorithm_names: List[str], data: Union[List[float], pd.Series, pd.DataFrame], config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare multiple advanced algorithms on the same data.

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
                    logger.warning(f"Algorithm '{name}' not found, skipping")
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
                    logger.error(f"Failed to analyze algorithm '{name}': {e}")
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
        if algorithm.algorithm_type == AlgorithmType.HIDDEN_MARKOV_MODEL:
            n_states = train_result.get("training_metrics", {}).get("n_states", 3)
            return algorithm.estimate_complexity(len(train_result.get("node_names", [])), n_states)
        elif algorithm.algorithm_type == AlgorithmType.BAYESIAN_NETWORK:
            n_vars = len(train_result.get("node_names", []))
            n_edges = len(train_result.get("edge_list", []))
            return algorithm.estimate_complexity(n_vars, n_edges)
        else:
            return {"complexity": "unknown"}

    def recommend_algorithm(self, problem_characteristics: Dict[str, Any]) -> AlgorithmType:
        """
        Recommend the best advanced algorithm based on problem characteristics.

        Args:
            problem_characteristics: Dictionary describing the problem
                (e.g., {'problem_type': 'regime_detection', 'temporal': True, 'causal': False})

        Returns:
            Recommended algorithm type
        """
        problem_type = problem_characteristics.get("problem_type", "sequential_modeling")
        temporal_nature = problem_characteristics.get("temporal", False)
        causal_modeling = problem_characteristics.get("causal", False)
        probabilistic_inference = problem_characteristics.get("probabilistic_inference", False)

        # Direct mapping if problem type is specified
        if problem_type in self.problem_mappings:
            return self.problem_mappings[problem_type]

        # Decision logic based on characteristics
        if temporal_nature and not causal_modeling:
            return AlgorithmType.HIDDEN_MARKOV_MODEL  # Sequential modeling
        elif causal_modeling and probabilistic_inference:
            return AlgorithmType.BAYESIAN_NETWORK  # Causal relationships
        elif problem_characteristics.get("n_variables", 5) > 10:
            return AlgorithmType.BAYESIAN_NETWORK  # Complex dependencies
        else:
            return AlgorithmType.HIDDEN_MARKOV_MODEL  # Default for sequential data

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
            if "regime_labels" in model_data:
                algorithm_type = AlgorithmType.HIDDEN_MARKOV_MODEL
            elif "graph_structure" in model_data:
                algorithm_type = AlgorithmType.BAYESIAN_NETWORK
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

        except Exception as e:
            logger.error(f"Failed to load algorithm from {filepath}: {e}")
            return False

    def get_performance_history(self, algorithm_name: str) -> List[Dict[str, Any]]:
        """Get performance history for an algorithm."""
        return self.performance_history.get(algorithm_name, [])

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

        logger.info("MarkovBayesianManager cleaned up")
