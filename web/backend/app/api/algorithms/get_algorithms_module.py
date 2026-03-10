"""
量化交易算法 API 端点

提供完整的量化交易算法API接口，基于现有的11种算法实现：
- 分类算法: SVM, 决策树, 朴素贝叶斯
- 模式匹配: BF, KMP, BMH, Aho-Corasick
- 高级算法: HMM, 贝叶斯网络, N-gram, 神经网络

支持GPU加速、实时处理和批量操作。

作者: Claude Code
版本: 1.0.0
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.algorithms._naive_bayes_router import router as naive_bayes_router
from app.api.algorithms.algorithm_metadata import (
    get_algorithm_description,
    get_algorithm_parameters,
    get_algorithm_performance,
    get_algorithm_use_cases,
)
from app.core.responses import (
    UnifiedResponse,
    bad_request,
    not_found,
    ok,
    server_error,
)
from app.core.security import User, get_current_user
from app.schemas.algorithm_schemas import (
    AlgorithmPredictRequest,
    AlgorithmTrainRequest,
    DecisionTreeTrainRequest,
)
from app.services.algorithm_service import algorithm_service

# 延迟导入算法模块，避免循环依赖
algorithms = None
AlgorithmType = None

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/algorithms", tags=["量化交易算法"])
router.include_router(naive_bayes_router)

def get_algorithms_module():
    """延迟加载算法模块"""
    global algorithms, AlgorithmType
    if algorithms is None:
        try:
            from src.algorithms import algorithms as alg_module
            from src.algorithms.types import AlgorithmType as AlgType

            algorithms = alg_module
            AlgorithmType = AlgType
        except ImportError as e:
            logger.error("Failed to import algorithms module", error=str(e))
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="算法服务暂不可用",
            )
    return algorithms, AlgorithmType


@router.get("/health", response_model=UnifiedResponse)
async def health_check(
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    算法API健康检查

    检查算法服务的整体健康状态，包括：
    - 算法模块导入状态
    - GPU资源可用性
    - 数据库连接状态
    """
    try:
        # 检查算法模块
        alg_module, alg_type = get_algorithms_module()

        # 检查GPU状态
        gpu_available = False
        try:
            from src.gpu.core.hardware_abstraction import GPUResourceManager

            gpu_manager = GPUResourceManager()
            gpu_available = True
        except ImportError:
            gpu_available = False

        health_data = {
            "service": "algorithms-api",
            "status": "healthy",
            "algorithms_loaded": True,
            "gpu_available": gpu_available,
            "supported_algorithms": len(alg_type.get_all_algorithms()) if alg_type else 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return ok(data=health_data, message="算法服务运行正常")

    except Exception as e:
        logger.error("算法健康检查失败", error=str(e))
        return server_error(message="算法服务健康检查失败")


@router.get("/", response_model=UnifiedResponse)
async def list_algorithms(
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    获取所有可用算法列表

    返回系统中支持的所有量化交易算法，按类别分组。
    """
    try:
        alg_module, alg_type = get_algorithms_module()

        algorithms_list = {
            "classification": [alg.value for alg in alg_type.get_classification_algorithms()],
            "pattern_matching": [alg.value for alg in alg_type.get_pattern_matching_algorithms()],
            "advanced": [alg.value for alg in alg_type.get_advanced_algorithms()],
        }

        return ok(data=algorithms_list, message="获取算法列表成功")

    except Exception as e:
        logger.error("获取算法列表失败", error=str(e))
        return server_error(message="获取算法列表失败")


@router.get("/{algorithm_type}/info", response_model=UnifiedResponse)
async def get_algorithm_info(algorithm_type: str, current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    获取算法详细信息

    Args:
        algorithm_type: 算法类型 (svm, decision_tree, hmm, etc.)

    Returns:
        算法的详细信息，包括用途、参数要求、性能特征等
    """
    try:
        alg_module, alg_type = get_algorithms_module()

        # 验证算法类型
        try:
            alg_enum = alg_type(algorithm_type)
        except ValueError:
            return not_found(message=f"不支持的算法类型: {algorithm_type}")

        # 获取算法信息
        algorithm_info = {
            "type": algorithm_type,
            "category": alg_enum.get_category(),
            "description": get_algorithm_description(alg_enum),
            "parameters": get_algorithm_parameters(alg_enum),
            "use_cases": get_algorithm_use_cases(alg_enum),
            "performance": get_algorithm_performance(alg_enum),
        }

        return ok(data=algorithm_info, message="获取算法信息成功")

    except Exception as e:
        logger.error("获取算法信息失败", algorithm_type=algorithm_type, error=str(e))
        return server_error(message="获取算法信息失败")


@router.post("/train", response_model=UnifiedResponse)
async def train_algorithm(
    request: AlgorithmTrainRequest, current_user: User = Depends(get_current_user)
) -> UnifiedResponse:
    """
    训练量化交易算法

    使用指定的算法类型和训练数据训练模型。

    Args:
        request: 训练请求，包含算法类型、特征数据、配置等

    Returns:
        训练结果，包括模型ID、训练指标等
    """
    try:
        logger.info(
            "收到算法训练请求",
            user=current_user.username,
            algorithm=request.algorithm_type.value,
        )

        # 使用服务层进行训练
        result = await algorithm_service.train_algorithm(request)

        logger.info(
            "算法训练完成",
            algorithm=request.algorithm_type.value,
            model_id=result.get("model_id"),
        )

        return ok(data=result, message=f"{request.algorithm_type.value.upper()}算法训练成功")

    except HTTPException:
        # 服务层已抛出HTTPException，直接重新抛出
        raise
    except Exception as e:
        logger.error("算法训练失败", algorithm=request.algorithm_type.value, error=str(e))
        return server_error(message="算法训练过程中发生错误")


@router.post("/predict", response_model=UnifiedResponse)
async def predict_with_algorithm(
    request: AlgorithmPredictRequest, current_user: User = Depends(get_current_user)
) -> UnifiedResponse:
    """
    使用训练好的算法进行预测

    Args:
        request: 预测请求，包含模型ID和预测数据

    Returns:
        预测结果，包括预测值和置信度
    """
    try:
        logger.info("收到算法预测请求", user=current_user.username, model_id=request.model_id)

        # 使用服务层进行预测
        result = await algorithm_service.predict_with_algorithm(request)

        logger.info("算法预测完成", model_id=request.model_id)

        return ok(data=result, message="算法预测成功")

    except HTTPException:
        # 服务层已抛出HTTPException，直接重新抛出
        raise
    except Exception as e:
        logger.error("算法预测失败", model_id=request.model_id, error=str(e))
        return server_error(message="算法预测过程中发生错误")


@router.get("/models", response_model=UnifiedResponse)
async def list_active_models(
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    获取当前活跃的算法模型列表

    Returns:
        当前加载的模型列表
    """
    try:
        logger.info("获取活跃模型列表", user=current_user.username)

        models = await algorithm_service.list_active_models()

        return ok(
            data={"models": models, "count": len(models)},
            message="获取活跃模型列表成功",
        )

    except Exception as e:
        logger.error("获取活跃模型列表失败", error=str(e))
        return server_error(message="获取活跃模型列表失败")


@router.delete("/models/{model_id}", response_model=UnifiedResponse)
async def unload_model(model_id: str, current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    卸载指定的算法模型

    Args:
        model_id: 要卸载的模型ID

    Returns:
        卸载结果
    """
    try:
        logger.info("卸载模型", user=current_user.username, model_id=model_id)

        result = await algorithm_service.unload_model(model_id)

        return ok(data=result, message="模型卸载成功")

    except HTTPException:
        # 服务层已抛出HTTPException，直接重新抛出
        raise
    except Exception as e:
        logger.error("卸载模型失败", model_id=model_id, error=str(e))
        return server_error(message="卸载模型失败")


@router.get("/training-history", response_model=UnifiedResponse)
async def get_training_history(
    model_id: Optional[str] = None,
    algorithm_type: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    获取算法训练历史记录 (Phase 1.4)

    Args:
        model_id: 模型ID过滤 (可选)
        algorithm_type: 算法类型过滤 (可选)
        limit: 返回记录数量限制 (默认50，最大100)

    Returns:
        训练历史记录列表
    """
    try:
        logger.info(
            "获取训练历史",
            user=current_user.username,
            model_id=model_id,
            algorithm_type=algorithm_type,
        )

        # 验证参数
        if limit > 100:
            limit = 100
        elif limit <= 0:
            limit = 50

        # 获取训练历史
        history = await algorithm_service.get_training_history(
            model_id=model_id, algorithm_type=algorithm_type, limit=limit
        )

        return ok(
            data={"training_history": history, "count": len(history)},
            message="获取训练历史成功",
        )

    except Exception as e:
        logger.error("获取训练历史失败", error=str(e))
        return server_error(message="获取训练历史失败")


@router.get("/prediction-history", response_model=UnifiedResponse)
async def get_prediction_history(
    model_id: Optional[str] = None,
    algorithm_type: Optional[str] = None,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    获取算法预测历史记录 (Phase 1.4)

    Args:
        model_id: 模型ID过滤 (可选)
        algorithm_type: 算法类型过滤 (可选)
        limit: 返回记录数量限制 (默认100，最大500)

    Returns:
        预测历史记录列表
    """
    try:
        logger.info(
            "获取预测历史",
            user=current_user.username,
            model_id=model_id,
            algorithm_type=algorithm_type,
        )

        # 验证参数
        if limit > 500:
            limit = 500
        elif limit <= 0:
            limit = 100

        # 获取预测历史
        history = await algorithm_service.get_prediction_history(
            model_id=model_id, algorithm_type=algorithm_type, limit=limit
        )

        return ok(
            data={"prediction_history": history, "count": len(history)},
            message="获取预测历史成功",
        )

    except Exception as e:
        logger.error("获取预测历史失败", error=str(e))
        return server_error(message="获取预测历史失败")


@router.get("/models/{model_id}/history", response_model=UnifiedResponse)
async def get_model_history(
    model_id: str,
    history_type: str = "all",  # all, training, prediction
    limit: int = 50,
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    获取指定模型的完整历史记录 (Phase 1.4)

    Args:
        model_id: 模型ID
        history_type: 历史类型 (all/training/prediction)
        limit: 返回记录数量限制 (默认50)

    Returns:
        模型的历史记录
    """
    try:
        logger.info(
            "获取模型历史",
            user=current_user.username,
            model_id=model_id,
            history_type=history_type,
        )

        # 验证参数
        if history_type not in ["all", "training", "prediction"]:
            return bad_request(message="无效的历史类型")

        if limit > 100:
            limit = 100
        elif limit <= 0:
            limit = 50

        result = {}

        # 获取训练历史
        if history_type in ["all", "training"]:
            training_history = await algorithm_service.get_training_history(model_id=model_id, limit=limit)
            result["training_history"] = training_history

        # 获取预测历史
        if history_type in ["all", "prediction"]:
            prediction_history = await algorithm_service.get_prediction_history(model_id=model_id, limit=limit)
            result["prediction_history"] = prediction_history

        return ok(data=result, message="获取模型历史成功")

    except Exception as e:
        logger.error("获取模型历史失败", model_id=model_id, error=str(e))
        return server_error(message="获取模型历史失败")


@router.get("/statistics", response_model=UnifiedResponse)
async def get_algorithm_statistics(
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """
    获取算法系统的统计信息 (Phase 1.4)

    Returns:
        系统统计数据
    """
    try:
        logger.info("获取算法统计", user=current_user.username)

        # 获取统计信息
        stats = await algorithm_service.get_model_statistics()

        return ok(data=stats, message="获取算法统计成功")

    except Exception as e:
        logger.error("获取算法统计失败", error=str(e))
        return server_error(message="获取算法统计失败")


@router.get("/models/{model_id}", response_model=UnifiedResponse)
async def get_model_details(model_id: str, current_user: User = Depends(get_current_user)) -> UnifiedResponse:
    """
    获取指定模型的详细信息 (Phase 1.4)

    Args:
        model_id: 模型ID

    Returns:
        模型详细信息
    """
    try:
        logger.info("获取模型详情", user=current_user.username, model_id=model_id)

        # 从算法服务获取模型详情
        # 注意：这里可能需要从repository直接查询，因为服务层的模型可能不在内存中
        if hasattr(algorithm_service, "repository") and algorithm_service.repository:
            model_data = await algorithm_service.repository.get_model(model_id)
            if model_data:
                return ok(data=model_data, message="获取模型详情成功")
            else:
                return not_found(message="模型不存在")
        else:
            return server_error(message="数据库服务不可用")

    except Exception as e:
        logger.error("获取模型详情失败", model_id=model_id, error=str(e))
        return server_error(message="获取模型详情失败")


@router.post("/classification/decision-tree/train", response_model=UnifiedResponse)
async def train_decision_tree_algorithm(
    request: DecisionTreeTrainRequest, current_user: User = Depends(get_current_user)
) -> UnifiedResponse:
    """
    训练决策树分类算法

    使用决策树算法对量化交易数据进行分类训练，支持Random Forest扩展。

    Args:
        request: 决策树训练请求，包含训练数据和参数

    Returns:
        训练结果，包括模型ID、准确率、特征重要性等指标
    """
    try:
        logger.info(
            "收到决策树算法训练请求",
            user=current_user.username,
            data_points=len(request.training_data),
        )

        # 构建通用训练请求
        train_request = AlgorithmTrainRequest(
            algorithm_type="decision_tree",
            algorithm_name="classification",
            training_data=request.training_data,
            config={
                "max_depth": request.tree_config.max_depth,
                "min_samples_split": request.tree_config.min_samples_split,
                "min_samples_leaf": request.tree_config.min_samples_leaf,
                "criterion": request.tree_config.criterion,
                "max_features": request.tree_config.max_features,
                "random_state": request.tree_config.random_state,
                "use_random_forest": request.tree_config.use_random_forest,
                "n_estimators": request.tree_config.n_estimators if request.tree_config.use_random_forest else None,
                "enable_gpu": request.tree_config.enable_gpu,
                "gpu_memory_limit_mb": 2048,
            },
            validation_split=request.validation_split,
            random_state=request.random_state,
        )

        # 使用服务层进行训练
        result = await algorithm_service.train_algorithm(train_request)

        logger.info(
            "决策树算法训练完成",
            model_id=result.get("model_id"),
            accuracy=result.get("accuracy"),
        )

        return ok(data=result, message="决策树算法训练成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("决策树算法训练失败", error=str(e))
        return server_error(message="决策树算法训练失败")


@router.post("/classification/decision-tree/predict", response_model=UnifiedResponse)
async def predict_decision_tree_algorithm(
    request: AlgorithmPredictRequest, current_user: User = Depends(get_current_user)
) -> UnifiedResponse:
    """
    使用训练好的决策树模型进行预测

    Args:
        request: 预测请求，包含模型ID和输入数据

    Returns:
        决策树预测结果，包括分类标签、置信度和特征重要性
    """
    try:
        logger.info("收到决策树预测请求", user=current_user.username, model_id=request.model_id)

        # 验证模型是否为决策树
        model_info = await algorithm_service.get_model_info(request.model_id)
        if model_info["algorithm_name"] != "decision_tree":
            return bad_request(message="指定的模型不是决策树模型")

        # 使用服务层进行预测
        result = await algorithm_service.predict_with_algorithm(request)

        logger.info("决策树预测完成", model_id=request.model_id)

        return ok(data=result, message="决策树预测成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("决策树预测失败", model_id=request.model_id, error=str(e))
        return server_error(message="决策树预测失败")


async def get_decision_tree_feature_importance(
    model_id: str, current_user: User = Depends(get_current_user)
) -> UnifiedResponse:
    """
    获取决策树模型的特征重要性

    Args:
        model_id: 模型ID

    Returns:
        特征重要性分析结果
    """
    try:
        logger.info("获取决策树特征重要性", user=current_user.username, model_id=model_id)

        # 使用服务层获取特征重要性
        result = await algorithm_service.get_feature_importance(model_id)

        return ok(data=result, message="获取特征重要性成功")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("获取特征重要性失败", model_id=model_id, error=str(e))
        return server_error(message="获取特征重要性失败")


