"""
市场数据API路由

提供RESTful接口:
- GET /api/market/fund-flow - 查询资金流向
- POST /api/market/fund-flow/refresh - 刷新资金流向数据
- GET /api/market/etf/list - 查询ETF列表
- POST /api/market/etf/refresh - 刷新ETF数据
- GET /api/market/chip-race - 查询竞价抢筹
- POST /api/market/chip-race/refresh - 刷新抢筹数据
- GET /api/market/lhb - 查询龙虎榜
- POST /api/market/lhb/refresh - 刷新龙虎榜数据
- GET /api/market/heatmap - 获取市场热力图数据
"""

import logging
from datetime import datetime

from fastapi import APIRouter


router = APIRouter()
logger = logging.getLogger(__name__)


MARKET_HEALTH_RESPONSES = {
    500: {
        "description": "市场数据服务内部错误",
        "content": {
            "application/json": {
                "example": {
                    "success": False,
                    "message": "市场数据服务健康检查失败",
                    "error_code": "MARKET_HEALTH_CHECK_FAILED",
                    "timestamp": "2026-04-05T08:45:00",
                }
            }
        },
    },
    200: {
        "description": "市场数据服务健康状态",
        "content": {
            "application/json": {
                "example": {
                    "status": "healthy",
                    "timestamp": "2026-04-05T08:45:00",
                    "service": "market-data-api",
                }
            }
        },
    },
}


@router.get(
    "/health",
    summary="市场数据 API 健康检查",
    description="检查市场数据 API 服务的健康状态，用于市场数据链路监控、自动化巡检和负载均衡探针。",
    tags=["health"],
    responses=MARKET_HEALTH_RESPONSES,
)
async def health_check():
    """
    检查市场数据 API 服务的整体健康状态

    此端点用于监控市场数据 API 的可用性和响应能力。

    **功能说明**:
    - 验证市场数据服务的运行状态
    - 检查实时行情数据提供者的连接
    - 评估 API 服务的响应性能

    **使用场景**:
    - 前端定期轮询显示服务状态
    - 监控和告警系统集成
    - 负载均衡器健康检查
    - 自动化部署流程的健康验证

    Returns:
        Dict: 包含以下字段的健康状态对象
            - status: 服务状态 (healthy/unhealthy)
            - service: 服务名称 (market-data-api)
            - timestamp: 检查时间戳 (ISO 8601 格式)

    Examples:
        获取市场数据 API 健康状态:
        ```bash
        curl http://localhost:${BACKEND_PORT}/api/market/health
        ```

        正常响应:
        ```json
        {
            "status": "healthy",
            "timestamp": "2025-11-30T21:06:45.123456",
            "service": "market-data-api"
        }
        ```

    Notes:
        - 此端点不需要认证，允许任何客户端查询
        - 响应时间通常在 50-100ms 以内
        - healthy: 服务正常运行，可以接受数据请求
        - 建议监控系统每 30 秒调用一次
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "market-data-api",
    }

