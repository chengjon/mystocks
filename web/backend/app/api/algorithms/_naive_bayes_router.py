"""Naive Bayes endpoints for algorithm API."""

import structlog
from fastapi import APIRouter, Depends, HTTPException

from app.core.responses import UnifiedResponse, bad_request, ok, server_error
from app.core.security import User, get_current_user
from app.schemas.algorithm_schemas import AlgorithmPredictRequest, AlgorithmTrainRequest
from app.services.algorithm_service import algorithm_service

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/classification/naive-bayes/train", response_model=UnifiedResponse)
async def train_naive_bayes_algorithm(
    request: AlgorithmTrainRequest,
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """训练朴素贝叶斯分类算法。"""
    try:
        logger.info(
            "收到朴素贝叶斯算法训练请求",
            user=current_user.username,
            data_points=len(request.training_data),
        )

        train_request = request.copy()
        train_request.algorithm_type = "naive_bayes"
        train_request.algorithm_name = "classification"

        if not train_request.config:
            train_request.config = {}
        train_request.config.update(
            {
                "enable_gpu": train_request.config.get("enable_gpu", False),
                "gpu_memory_limit_mb": 1024,
            }
        )

        result = await algorithm_service.train_algorithm(train_request)
        logger.info(
            "朴素贝叶斯算法训练完成",
            model_id=result.get("model_id"),
            accuracy=result.get("accuracy"),
        )
        return ok(data=result, message="朴素贝叶斯算法训练成功")

    except HTTPException:
        raise
    except Exception as error:
        logger.error("朴素贝叶斯算法训练失败", error=str(error))
        return server_error(message="朴素贝叶斯算法训练失败")


@router.post("/classification/naive-bayes/predict", response_model=UnifiedResponse)
async def predict_naive_bayes_algorithm(
    request: AlgorithmPredictRequest,
    current_user: User = Depends(get_current_user),
) -> UnifiedResponse:
    """使用训练好的朴素贝叶斯模型进行预测。"""
    try:
        logger.info(
            "收到朴素贝叶斯预测请求",
            user=current_user.username,
            model_id=request.model_id,
        )

        model_info = await algorithm_service.get_model_info(request.model_id)
        if model_info["algorithm_name"] != "naive_bayes":
            return bad_request(message="指定的模型不是朴素贝叶斯模型")

        result = await algorithm_service.predict_with_algorithm(request)
        logger.info("朴素贝叶斯预测完成", model_id=request.model_id)
        return ok(data=result, message="朴素贝叶斯预测成功")

    except HTTPException:
        raise
    except Exception as error:
        logger.error("朴素贝叶斯预测失败", model_id=request.model_id, error=str(error))
        return server_error(message="朴素贝叶斯预测失败")
