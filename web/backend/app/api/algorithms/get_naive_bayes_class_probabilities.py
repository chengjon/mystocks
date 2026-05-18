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


import structlog
from fastapi import APIRouter, Depends

from app.core.exceptions import BusinessException

from app.core.responses import (
    UnifiedResponse,
    ok,
    server_error,
)
from app.core.security import User, get_current_user
from app.services.algorithm_service import algorithm_service

# 延迟导入算法模块，避免循环依赖
algorithms = None
AlgorithmType = None

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/api/v1/algorithms", tags=["量化交易算法"])

async def get_naive_bayes_class_probabilities(
    model_id: str, current_user: User = Depends(get_current_user)
) -> UnifiedResponse:
    """
    获取朴素贝叶斯模型的类别概率分布

    Args:
        model_id: 模型ID

    Returns:
        各类别的先验概率和条件概率信息
    """
    try:
        logger.info("获取朴素贝叶斯类别概率", user=current_user.username, model_id=model_id)

        # 使用服务层获取模型统计信息
        result = await algorithm_service.get_model_statistics(model_id)

        return ok(data=result, message="获取类别概率成功")

    except BusinessException:
        raise
    except Exception as e:
        logger.error("获取类别概率失败", model_id=model_id, error=str(e))
        return server_error(message="获取类别概率失败")


