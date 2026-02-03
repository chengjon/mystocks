"""
Algorithm Service Layer

This module provides the business logic layer for quantitative trading algorithms,
implementing the factory pattern for algorithm instantiation and integrating with
GPU acceleration framework.

Features:
- Algorithm factory pattern for dynamic instantiation
- GPU acceleration integration
- Comprehensive error handling and logging
- Result formatting for API responses
- Algorithm metadata management
"""

import logging
import traceback
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories import AlgorithmModelRepository
from app.schemas.algorithm_schemas import (  # Add other algorithm-specific imports as needed
    AlgorithmConfig,
    AlgorithmInfoRequest,
    AlgorithmPredictRequest,
    AlgorithmTrainRequest,
    AlgorithmType,
)

# Define logger early for try/except block
logger = logging.getLogger(__name__)

# Import from src/algorithms
try:
    # Import concrete algorithm classes
    from src.algorithms import (  # KMPAlgorithm,  # TODO: Fix indentation; BMHAlgorithm,  # TODO: Fix indentation; AhoCorasickAlgorithm,  # TODO: Fix indentation
        BayesianNetworkAlgorithm,
        BruteForceAlgorithm,
        DecisionTreeAlgorithm,
        HMMAlgorithm,
        NaiveBayesAlgorithm,
        NeuralNetworkAlgorithm,
        NGramAlgorithm,
    )
    from src.algorithms.base import AlgorithmMetadata, BaseAlgorithm
    from src.algorithms.config import AlgorithmConfig as SrcAlgorithmConfig
    from src.algorithms.types import AlgorithmType as SrcAlgorithmType

    ALGORITHMS_AVAILABLE = True
    logger.info("Successfully imported all algorithm implementations")
except ImportError as e:
    logger.error("Failed to import algorithms: %(e)s")
    # Fallback if src/algorithms not available yet
    ALGORITHMS_AVAILABLE = False

    # Define minimal types for now
    class BaseAlgorithm:
        pass

    class AlgorithmMetadata:
        pass

    class SrcAlgorithmType:
        pass

    class SrcAlgorithmConfig:
        pass

    # Define placeholder algorithm classes
    SVMAlgorithm = DecisionTreeAlgorithm = NaiveBayesAlgorithm = None
    BruteForceAlgorithm = KMPAlgorithm = BMHAlgorithm = AhoCorasickAlgorithm = None
    HMMAlgorithm = BayesianNetworkAlgorithm = NGramAlgorithm = NeuralNetworkAlgorithm = None

    class AlgorithmMetadata:
        pass

    class SrcAlgorithmType:
        pass

    class SrcAlgorithmConfig:
        pass


# Import GPU framework if available
try:
    from gpu_api_system.services import GPUBacktestService

    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False


class AlgorithmFactory:
    """
    Factory class for creating algorithm instances.

    This factory handles the instantiation of different algorithm types
    and integrates with GPU acceleration when available.
    """

    def __init__(self):
        self._algorithm_cache = {}
        self._gpu_service = None

        if GPU_AVAILABLE:
            try:
                self._gpu_service = GPUBacktestService()
                logger.info("GPU acceleration service initialized")
            except Exception as e:
                logger.warning("Failed to initialize GPU service: %(e)s")

    async def create_algorithm(self, algorithm_type: AlgorithmType, config: AlgorithmConfig) -> BaseAlgorithm:
        """
        Create an algorithm instance based on type and configuration.

        Args:
            algorithm_type: Type of algorithm to create
            config: Algorithm configuration

        Returns:
            Initialized algorithm instance

        Raises:
            ValueError: If algorithm type is not supported
            RuntimeError: If algorithm creation fails
        """
        try:
            # Convert API enum to src enum if needed
            if ALGORITHMS_AVAILABLE:
                src_algorithm_type = SrcAlgorithmType(algorithm_type.value)

                # Create metadata
                metadata = AlgorithmMetadata(
                    algorithm_type=src_algorithm_type,
                    name=f"{algorithm_type.value}_algorithm",
                    version="1.0.0",
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    description=f"{algorithm_type.value.upper()} algorithm instance",
                )

                # Import and instantiate the specific algorithm class
                algorithm_class = await self._get_algorithm_class(algorithm_type)

                # Create algorithm instance
                algorithm = algorithm_class(metadata)

                # Configure GPU if available and requested
                if config.enable_gpu and GPU_AVAILABLE and hasattr(algorithm, "gpu_enabled"):
                    await self._configure_gpu_algorithm(algorithm, config)

                logger.info("Created algorithm: {algorithm_type.value}")
                return algorithm

            else:
                raise RuntimeError("Algorithm framework not available")

        except Exception as e:
            logger.error("Failed to create algorithm {algorithm_type.value}: %(e)s")
            raise RuntimeError(f"Algorithm creation failed: {str(e)}")

    async def _get_algorithm_class(self, algorithm_type: AlgorithmType):
        """Get the algorithm class for the given type."""

        # Mapping of algorithm types to their implementation classes
        algorithm_mapping = {
            # Classification algorithms
            AlgorithmType.SVM: SVMAlgorithm,
            AlgorithmType.DECISION_TREE: DecisionTreeAlgorithm,
            AlgorithmType.NAIVE_BAYES: NaiveBayesAlgorithm,
            # Pattern matching algorithms
            AlgorithmType.BRUTE_FORCE: BruteForceAlgorithm,
            AlgorithmType.KNUTH_MORRIS_PRATT: KMPAlgorithm,
            AlgorithmType.BOYER_MOORE_HORSPOOL: BMHAlgorithm,
            AlgorithmType.AHO_CORASICK: AhoCorasickAlgorithm,
            # Advanced algorithms
            AlgorithmType.HIDDEN_MARKOV_MODEL: HMMAlgorithm,
            AlgorithmType.BAYESIAN_NETWORK: BayesianNetworkAlgorithm,
            AlgorithmType.N_GRAM: NGramAlgorithm,
            AlgorithmType.NEURAL_NETWORK: NeuralNetworkAlgorithm,
        }

        if algorithm_type not in algorithm_mapping:
            raise ValueError(f"Unsupported algorithm type: {algorithm_type.value}")

        return algorithm_mapping[algorithm_type]

    async def _configure_gpu_algorithm(self, algorithm, config: AlgorithmConfig):
        """Configure GPU settings for the algorithm."""
        try:
            if hasattr(algorithm, "set_gpu_memory_limit") and config.gpu_memory_limit_mb:
                algorithm.set_gpu_memory_limit(config.gpu_memory_limit_mb)

            await algorithm.initialize_gpu_context()
            logger.info("GPU context initialized for algorithm")

        except Exception as e:
            logger.warning("GPU configuration failed, falling back to CPU: %(e)s")
            await algorithm.fallback_to_cpu()


class AlgorithmResultFormatter:
    """
    Utility class for formatting algorithm results for API responses.
    """

    @staticmethod
    def format_training_result(result: Dict[str, Any], algorithm_type: AlgorithmType) -> Dict[str, Any]:
        """Format training result for API response."""
        return {
            "algorithm_type": algorithm_type.value,
            "status": "completed",
            "model_id": result.get("model_id", ""),
            "training_metrics": result.get("training_metrics", {}),
            "created_at": datetime.now().isoformat(),
            "gpu_used": result.get("gpu_used", False),
        }

    @staticmethod
    def format_prediction_result(result: Dict[str, Any], algorithm_type: AlgorithmType) -> Dict[str, Any]:
        """Format prediction result for API response."""
        return {
            "algorithm_type": algorithm_type.value,
            "status": "completed",
            "predictions": result.get("predictions", []),
            "confidence_scores": result.get("confidence_scores", []),
            "processing_time_ms": result.get("processing_time_ms", 0),
            "gpu_used": result.get("gpu_used", False),
        }

    @staticmethod
    def format_error_result(error: Exception, algorithm_type: AlgorithmType) -> Dict[str, Any]:
        """Format error result for API response."""
        return {
            "algorithm_type": algorithm_type.value,
            "status": "error",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
        }


class AlgorithmService:
    """
    Main service class for algorithm operations.

    This service provides high-level methods for training, prediction,
    and management of quantitative trading algorithms.
    """

    def __init__(self, db_session: Optional[Session] = None):
        self.factory = AlgorithmFactory()
        self.formatter = AlgorithmResultFormatter()
        self._active_algorithms = {}
        self.db_session = db_session
        self.repository = AlgorithmModelRepository(db_session) if db_session else None

    async def train_algorithm(self, request: AlgorithmTrainRequest) -> Dict[str, Any]:
        """
        Train an algorithm with the given request.

        Args:
            request: Training request with algorithm type, data, and config

        Returns:
            Formatted training result

        Raises:
            HTTPException: If training fails
        """
        try:
            logger.info("Starting training for algorithm: {request.algorithm_type.value}")

            # Create algorithm instance
            algorithm = await self.factory.create_algorithm(request.algorithm_type, request.config)

            # Prepare training data
            training_data = await self._prepare_training_data(request)

            # Execute training
            start_time = datetime.now()
            result = await algorithm.train(training_data, request.config.dict())
            end_time = datetime.now()

            # Add timing information
            result["processing_time_ms"] = (end_time - start_time).total_seconds() * 1000
            result["gpu_used"] = request.config.enable_gpu and GPU_AVAILABLE

            # Store algorithm for future predictions
            model_id = f"{request.algorithm_type.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self._active_algorithms[model_id] = algorithm
            result["model_id"] = model_id

            # Persist training result to database if repository is available
            if self.repository:
                await self._persist_training_result(model_id, request, result, start_time, end_time)

            logger.info("Training completed for {request.algorithm_type.value}, model_id: %(model_id)s")

            return self.formatter.format_training_result(result, request.algorithm_type)

        except Exception as e:
            logger.error("Training failed for {request.algorithm_type.value}: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Algorithm training failed: {str(e)}")

    async def predict_with_algorithm(self, request: AlgorithmPredictRequest) -> Dict[str, Any]:
        """
        Generate predictions using a trained algorithm.

        Args:
            request: Prediction request with model ID and data

        Returns:
            Formatted prediction result

        Raises:
            HTTPException: If prediction fails
        """
        try:
            logger.info("Starting prediction for model: {request.model_id}")

            # Get algorithm instance
            algorithm = self._active_algorithms.get(request.model_id)
            if not algorithm:
                raise ValueError(f"Model {request.model_id} not found")

            # Prepare prediction data
            prediction_data = await self._prepare_prediction_data(request)

            # Execute prediction
            prediction_start_time = datetime.now()
            result = await algorithm.predict(prediction_data, {})
            prediction_end_time = datetime.now()

            # Add timing information
            result["processing_time_ms"] = (prediction_end_time - prediction_start_time).total_seconds() * 1000

            # Persist prediction result to database if repository is available
            if self.repository:
                await self._persist_prediction_result(
                    request.model_id,
                    request,
                    result,
                    prediction_start_time,
                    prediction_end_time,
                )

            logger.info("Prediction completed for model: {request.model_id}")

            return self.formatter.format_prediction_result(result, algorithm.algorithm_type)

        except Exception as e:
            logger.error("Prediction failed for model {request.model_id}: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Algorithm prediction failed: {str(e)}")

    async def get_algorithm_info(self, request: AlgorithmInfoRequest) -> Dict[str, Any]:
        """
        Get information about an algorithm type.

        Args:
            request: Info request with algorithm type

        Returns:
            Algorithm metadata and capabilities
        """
        try:
            algorithm_type = request.algorithm_type

            # Get algorithm capabilities based on type
            capabilities = await self._get_algorithm_capabilities(algorithm_type)

            return {
                "algorithm_type": algorithm_type.value,
                "capabilities": capabilities,
                "gpu_supported": GPU_AVAILABLE,
                "framework_available": ALGORITHMS_AVAILABLE,
            }

        except Exception as e:
            logger.error("Failed to get algorithm info: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to get algorithm information: {str(e)}")

    async def list_active_models(self) -> List[Dict[str, Any]]:
        """
        List all currently active (loaded) algorithm models.
        Returns models from database if available, otherwise from memory cache.

        Returns:
            List of active model information
        """
        try:
            # Try to get models from database first
            if self.repository:
                db_models = await self.repository.list_models(is_active=True)
                if db_models:
                    return db_models

            # Fallback to memory cache
            models = []
            for model_id, algorithm in self._active_algorithms.items():
                models.append(
                    {
                        "model_id": model_id,
                        "algorithm_type": getattr(algorithm, "algorithm_type", "unknown"),
                        "is_trained": getattr(algorithm, "is_trained", True),
                        "created_at": getattr(algorithm.metadata, "created_at", datetime.now()).isoformat(),
                        "gpu_enabled": getattr(algorithm, "gpu_enabled", False),
                    }
                )

            return models

        except Exception as e:
            logger.error("Failed to list active models: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to list active models: {str(e)}")

            return models

        except Exception as e:
            logger.error("Failed to list active models: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to list active models: {str(e)}")

    async def unload_model(self, model_id: str) -> Dict[str, Any]:
        """
        Unload a specific algorithm model from memory.

        Args:
            model_id: ID of the model to unload

        Returns:
            Unload result
        """
        try:
            if model_id in self._active_algorithms:
                algorithm = self._active_algorithms[model_id]

                # Release GPU resources if applicable
                if hasattr(algorithm, "release_gpu_context"):
                    await algorithm.release_gpu_context()

                del self._active_algorithms[model_id]

                logger.info("Unloaded model: %(model_id)s")
                return {
                    "status": "success",
                    "model_id": model_id,
                    "message": "Model unloaded successfully",
                }
            else:
                raise ValueError(f"Model {model_id} not found")

        except Exception as e:
            logger.error("Failed to unload model %(model_id)s: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Failed to unload model: {str(e)}")

    async def _prepare_training_data(self, request: AlgorithmTrainRequest) -> Any:
        """Prepare training data for algorithm."""
        # This would convert request data to appropriate format
        # For now, return as-is or convert from request.training_data
        if request.training_data:
            return request.training_data

        # Placeholder for data preparation logic
        return {
            "features": request.features,
            "labels": request.labels,
            "symbol": request.symbol,
        }

    async def _prepare_prediction_data(self, request: AlgorithmPredictRequest) -> Any:
        """Prepare prediction data for algorithm."""
        # Convert request data to appropriate format
        return {"features": request.features_data}

    async def _get_algorithm_capabilities(self, algorithm_type: AlgorithmType) -> Dict[str, Any]:
        """Get capabilities for a specific algorithm type."""
        base_capabilities = {
            "supports_training": True,
            "supports_prediction": True,
            "supports_evaluation": True,
            "gpu_accelerated": GPU_AVAILABLE,
        }

        # Add algorithm-specific capabilities
        if algorithm_type == AlgorithmType.SVM:
            base_capabilities.update(
                {
                    "kernels": ["linear", "rbf", "poly", "sigmoid"],
                    "max_iter": "configurable",
                    "probability_support": True,
                }
            )
        elif algorithm_type == AlgorithmType.DECISION_TREE:
            base_capabilities.update(
                {
                    "max_depth": "configurable",
                    "criterion": ["gini", "entropy", "log_loss"],
                    "feature_importance": True,
                }
            )
        elif algorithm_type == AlgorithmType.NAIVE_BAYES:
            base_capabilities.update(
                {
                    "distribution_types": ["gaussian", "multinomial", "bernoulli"],
                    "prior_probabilities": "configurable",
                }
            )

        return base_capabilities

    # ==================== 数据库持久化辅助方法 ====================

    async def _persist_training_result(
        self,
        model_id: str,
        request: AlgorithmTrainRequest,
        result: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
    ):
        """
        持久化训练结果到数据库

        Args:
            model_id: 模型ID
            request: 训练请求
            result: 训练结果
            start_time: 训练开始时间
            end_time: 训练结束时间
        """
        try:
            if not self.repository:
                return

            # 保存算法模型
            model_data = {
                "model_id": model_id,
                "algorithm_type": request.algorithm_type.value,
                "model_name": f"{request.algorithm_type.value} Model {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "model_version": "1.0.0",
                "model_data": result.get("model_data", {}),
                "metadata": {
                    "training_config": request.config.dict() if hasattr(request.config, "dict") else request.config,
                    "features": request.features if hasattr(request, "features") else [],
                    "symbol": getattr(request, "symbol", None),
                    "created_by": "algorithm_service",
                },
                "training_metrics": result.get("training_metrics", {}),
                "symbol": getattr(request, "symbol", None),
                "features": request.features if hasattr(request, "features") else [],
                "is_active": True,
                "gpu_trained": result.get("gpu_used", False),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }

            await self.repository.save_model(model_data)

            # 保存训练历史
            training_history_data = {
                "training_id": f"train_{model_id}_{uuid.uuid4().hex[:8]}",
                "model_id": model_id,
                "algorithm_type": request.algorithm_type.value,
                "training_start_time": start_time,
                "training_end_time": end_time,
                "training_duration_ms": result.get("processing_time_ms", 0),
                "status": "success",
                "symbol": getattr(request, "symbol", None),
                "features": request.features if hasattr(request, "features") else [],
                "training_config": request.config.dict(),
                "training_metrics": result.get("training_metrics", {}),
                "validation_metrics": result.get("validation_metrics", {}),
                "gpu_used": result.get("gpu_used", False),
                "data_sample_count": (
                    len(request.training_data) if hasattr(request, "training_data") and request.training_data else 0
                ),
                "created_at": datetime.now(),
            }

            # 保存训练历史
            training_history_data = {
                "training_id": f"train_{model_id}_{uuid.uuid4().hex[:8]}",
                "model_id": model_id,
                "algorithm_type": request.algorithm_type.value,
                "training_start_time": start_time,
                "training_end_time": end_time,
                "training_duration_ms": result.get("processing_time_ms", 0),
                "status": "success",
                "symbol": getattr(request, "symbol", None),
                "features": request.features if hasattr(request, "features") else [],
                "training_config": request.config.dict() if hasattr(request.config, "dict") else request.config,
                "training_metrics": result.get("training_metrics", {}),
                "validation_metrics": result.get("validation_metrics", {}),
                "gpu_used": result.get("gpu_used", False),
                "data_sample_count": (
                    len(request.training_data) if hasattr(request, "training_data") and request.training_data else 0
                ),
                "created_at": datetime.now(),
            }

            await self.repository.save_training_history(training_history_data)

        except Exception as e:
            logger.error("Failed to persist training result: %(e)s")
            # Don't raise exception to avoid breaking the main flow

    async def _persist_prediction_result(
        self,
        model_id: str,
        request: AlgorithmPredictRequest,
        result: Dict[str, Any],
        start_time: datetime,
        end_time: datetime,
    ):
        """
        持久化预测结果到数据库

        Args:
            model_id: 模型ID
            request: 预测请求
            result: 预测结果
            start_time: 预测开始时间
            end_time: 预测结束时间
        """
        try:
            if not self.repository:
                return

            # 保存预测历史
            prediction_history_data = {
                "prediction_id": f"pred_{model_id}_{uuid.uuid4().hex[:8]}",
                "model_id": model_id,
                "algorithm_type": result.get("algorithm_type", "unknown"),
                "prediction_time": start_time,
                "processing_time_ms": result.get("processing_time_ms", 0),
                "status": "success",
                "input_data": request.features_data if hasattr(request, "features_data") else {},
                "prediction_result": result.get("predictions", []),
                "confidence_score": (
                    result.get("confidence_scores", [None])[0] if result.get("confidence_scores") else None
                ),
                "gpu_used": result.get("gpu_used", False),
                "batch_size": len(request.features_data) if hasattr(request, "features_data") else 1,
                "created_at": datetime.now(),
            }

            await self.repository.save_prediction_history(prediction_history_data)

        except Exception as e:
            logger.error("Failed to persist prediction result: %(e)s")
            # Don't raise exception to avoid breaking the main flow

    # ==================== 历史查询方法 ====================

    async def get_training_history(
        self,
        model_id: Optional[str] = None,
        algorithm_type: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """
        获取训练历史记录

        Args:
            model_id: 模型ID过滤
            algorithm_type: 算法类型过滤
            limit: 返回记录数量限制

        Returns:
            训练历史列表
        """
        if not self.repository:
            return []

        return await self.repository.list_training_history(model_id, algorithm_type, limit)

    async def get_prediction_history(
        self,
        model_id: Optional[str] = None,
        algorithm_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        获取预测历史记录

        Args:
            model_id: 模型ID过滤
            algorithm_type: 算法类型过滤
            limit: 返回记录数量限制

        Returns:
            预测历史列表
        """
        if not self.repository:
            return []

        return await self.repository.list_prediction_history(model_id, algorithm_type, limit)

    async def get_model_statistics(self) -> Dict[str, Any]:
        """
        获取模型统计信息

        Returns:
            统计数据字典
        """
        if not self.repository:
            return {}

        return await self.repository.get_model_statistics()


# Global service instance (without database session - for backward compatibility)
algorithm_service = AlgorithmService()
