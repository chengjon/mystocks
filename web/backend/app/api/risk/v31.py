import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Set

from fastapi import APIRouter, Body, Path, WebSocket, WebSocketDisconnect

from app.core.exceptions import BusinessException, NotFoundException, ValidationException
from app.openapi_config import COMMON_RESPONSES
from app.api.risk._shared import (
    ENHANCED_RISK_FEATURES_AVAILABLE,
    RISK_MANAGEMENT_V31_AVAILABLE,
    get_risk_management_core,
    logger,
)

RISK_V31_ROUTE_RESPONSES = {
    400: COMMON_RESPONSES[400],
    404: COMMON_RESPONSES[404],
    422: COMMON_RESPONSES[422],
    500: COMMON_RESPONSES[500],
    503: {
        "description": "风险管理增强能力不可用或尚未初始化",
    },
}

router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-V3.1"], responses=RISK_V31_ROUTE_RESPONSES)


def _success_response_spec(description: str, example: Any) -> dict[int, dict[str, Any]]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }

RISK_WS_BROADCAST_EXAMPLES = {
    "broadcast_price_alert": {
        "summary": "广播风险更新消息",
        "description": "向订阅指定 topic 的客户端广播新的风险事件数据。",
        "value": {
            "symbol": "600519",
            "risk_level": "warning",
            "message": "价格波动超过阈值，请关注仓位风险。",
            "metrics": {"drawdown": 0.085, "volatility": 0.23},
        },
    }
}

STOCK_RISK_V31_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "symbol": "600519.SH",
        "risk_metrics": {
            "symbol": "600519.SH",
            "timestamp": "2026-04-08T11:45:00",
            "volatility_20d": 0.24,
            "atr_14": 18.6,
            "volatility_percentile": 72,
            "avg_daily_volume": 3560000.0,
            "bid_ask_spread": 0.02,
            "turnover_rate": 0.018,
            "liquidity_score": 81,
            "ma_trend": "bull",
            "macd_signal": "bullish",
            "rsi": 61.4,
            "bollinger_position": "upper",
            "risk_score": 63,
            "risk_level": "medium",
        },
        "calculated_at": "2026-04-08T11:45:00",
        "version": "3.1",
    },
}

PORTFOLIO_RISK_V31_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "portfolio_id": "hk-a50-portfolio",
        "risk_metrics": {
            "portfolio_id": "hk-a50-portfolio",
            "user_id": "demo-user",
            "timestamp": "2026-04-08T11:45:00",
            "total_value": 1250000.0,
            "cash_value": 210000.0,
            "var_1d_95": 0.026,
            "max_drawdown": 0.082,
            "sharpe_ratio": 1.34,
            "beta": 1.07,
            "hhi": 0.18,
            "top10_ratio": 0.67,
            "max_single_position": 0.14,
            "max_industry_concentration": 0.22,
            "risk_score": 58,
            "risk_level": "medium",
        },
        "calculated_at": "2026-04-08T11:45:00",
        "version": "3.1",
    },
}

RISK_MANAGEMENT_HEALTH_RESPONSE_EXAMPLE = {
    "status": "healthy",
    "version": "3.1",
    "components": {
        "v31_system": {"status": "available", "available": True},
        "core": {"status": "initialized", "available": True},
        "gpu_calculator": {"status": "available", "available": True},
        "stop_loss_engine": {"status": "available", "available": True},
        "alert_service": {"status": "available", "available": True},
    },
    "checked_at": "2026-04-08T11:45:00",
}

RISK_WS_BROADCAST_RESPONSE_EXAMPLE = {
    "status": "success",
    "message": "消息已广播到主题 'alerts'",
    "topic": "alerts",
    "broadcast_at": "2026-04-08T11:45:00",
}

RISK_WS_CONNECTIONS_RESPONSE_EXAMPLE = {
    "status": "success",
    "data": {
        "total_connections": 3,
        "topic_subscriptions": {
            "portfolio_risk": 2,
            "stock_risk": 3,
            "alerts": 3,
            "stop_loss": 1,
        },
        "timestamp": "2026-04-08T11:45:00",
    },
}

STOCK_RISK_V31_RESPONSES = _success_response_spec("V3.1 个股风险评估查询成功。", STOCK_RISK_V31_RESPONSE_EXAMPLE)
PORTFOLIO_RISK_V31_RESPONSES = _success_response_spec(
    "V3.1 组合风险评估查询成功。", PORTFOLIO_RISK_V31_RESPONSE_EXAMPLE
)
RISK_MANAGEMENT_HEALTH_RESPONSES = _success_response_spec(
    "V3.1 风险管理健康检查成功。", RISK_MANAGEMENT_HEALTH_RESPONSE_EXAMPLE
)
RISK_WS_BROADCAST_RESPONSES = _success_response_spec(
    "V3.1 风险广播消息发送成功。", RISK_WS_BROADCAST_RESPONSE_EXAMPLE
)
RISK_WS_CONNECTIONS_RESPONSES = _success_response_spec(
    "V3.1 WebSocket 连接统计查询成功。", RISK_WS_CONNECTIONS_RESPONSE_EXAMPLE
)


@router.get(
    "/v31/stock/{symbol}",
    summary="查询 V3.1 个股风险",
    description="获取指定股票在 V3.1 风险管理引擎下的最新风险评估结果，包含风险指标和计算时间。",
    responses=STOCK_RISK_V31_RESPONSES,
)
async def get_stock_risk_v31(symbol: str = Path(..., description="需要查询风险画像的股票代码。")) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        core = get_risk_management_core()
        if not core:
            raise BusinessException(
                detail="风险管理核心不可用", status_code=503, error_code="RISK_MANAGEMENT_CORE_UNAVAILABLE"
            )

        risk_metrics = await core.calculate_stock_risk(symbol)
        await core._publish_risk_event("stock_risk_calculated", {"symbol": symbol, "metrics": risk_metrics.__dict__})

        return {
            "status": "success",
            "data": {
                "symbol": symbol,
                "risk_metrics": risk_metrics.__dict__,
                "calculated_at": datetime.now().isoformat(),
                "version": "3.1",
            },
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("V3.1个股风险计算失败 %(symbol)s: %(e)s")
        raise BusinessException(
            detail=f"个股风险计算失败: {str(e)}", status_code=500, error_code="INDIVIDUAL_STOCK_RISK_CALCULATION_FAILED"
        )


@router.get(
    "/v31/portfolio/{portfolio_id}",
    summary="查询 V3.1 组合风险",
    description="获取指定投资组合在 V3.1 风险管理引擎下的组合风险评估结果与版本信息。",
    responses=PORTFOLIO_RISK_V31_RESPONSES,
)
async def get_portfolio_risk_v31(
    portfolio_id: str = Path(..., description="需要查询风险概览的投资组合ID。"),
) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED"
            )

        core = get_risk_management_core()
        if not core:
            raise BusinessException(
                detail="风险管理核心不可用", status_code=503, error_code="RISK_MANAGEMENT_CORE_UNAVAILABLE"
            )

        risk_metrics = await core.calculate_portfolio_risk(portfolio_id)
        await core._publish_risk_event(
            "portfolio_risk_calculated", {"portfolio_id": portfolio_id, "metrics": risk_metrics.__dict__}
        )

        return {
            "status": "success",
            "data": {
                "portfolio_id": portfolio_id,
                "risk_metrics": risk_metrics.__dict__,
                "calculated_at": datetime.now().isoformat(),
                "version": "3.1",
            },
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("V3.1组合风险计算失败 %(portfolio_id)s: %(e)s")
        raise BusinessException(
            detail=f"组合风险计算失败: {str(e)}", status_code=500, error_code="PORTFOLIO_RISK_CALCULATION_FAILED"
        )


@router.get(
    "/v31/health",
    summary="检查 V3.1 风险系统健康度",
    description="检查 V3.1 风险管理系统及其核心组件的可用性，返回当前初始化与依赖状态。",
    responses=RISK_MANAGEMENT_HEALTH_RESPONSES,
)
async def get_risk_management_health() -> Dict[str, Any]:
    try:
        health_status = {
            "status": "healthy",
            "version": "3.1",
            "components": {},
            "checked_at": datetime.now().isoformat(),
        }

        health_status["components"]["v31_system"] = {
            "status": "available" if RISK_MANAGEMENT_V31_AVAILABLE else "unavailable",
            "available": RISK_MANAGEMENT_V31_AVAILABLE,
        }

        if RISK_MANAGEMENT_V31_AVAILABLE:
            core = get_risk_management_core()
            health_status["components"]["core"] = {
                "status": "initialized" if core else "uninitialized",
                "available": core is not None,
            }
            if core:
                health_status["components"]["gpu_calculator"] = {
                    "status": "available" if core.risk_calculator else "unavailable",
                    "available": core.risk_calculator is not None,
                }
                health_status["components"]["stop_loss_engine"] = {
                    "status": "available" if core.stop_loss_engine else "unavailable",
                    "available": core.stop_loss_engine is not None,
                }
                health_status["components"]["alert_service"] = {
                    "status": "available" if core.alert_service else "unavailable",
                    "available": core.alert_service is not None,
                }
        else:
            health_status["status"] = "degraded"
            health_status["components"]["core"] = {"status": "unavailable", "available": False}

        return health_status

    except Exception as e:
        logger.error("V3.1健康检查失败: %(e)s")
        return {"status": "unhealthy", "error": str(e), "version": "3.1", "checked_at": datetime.now().isoformat()}


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {
            "portfolio_risk": set(),
            "stock_risk": set(),
            "alerts": set(),
            "stop_loss": set(),
        }

    async def connect(self, websocket: WebSocket, topics: List[str] = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if topics:
            for topic in topics:
                if topic in self.subscriptions:
                    self.subscriptions[topic].add(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        for topic_connections in self.subscriptions.values():
            topic_connections.discard(websocket)

    async def broadcast_to_topic(self, topic: str, message: Dict[str, Any]):
        if topic not in self.subscriptions:
            return
        disconnected = []
        message_json = json.dumps(message)
        for connection in self.subscriptions[topic]:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.append(connection)
        for connection in disconnected:
            self.disconnect(connection)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.disconnect(websocket)


connection_manager = ConnectionManager()


@router.websocket("/v31/ws/risk-updates")
async def websocket_risk_updates(websocket: WebSocket, topics: str = "portfolio_risk,stock_risk,alerts"):
    try:
        topic_list = [t.strip() for t in topics.split(",") if t.strip()]
        await connection_manager.connect(websocket, topic_list)

        try:
            welcome_message = {
                "type": "welcome",
                "message": "已连接到MyStocks风险管理系统实时数据流",
                "subscribed_topics": topic_list,
                "timestamp": datetime.now().isoformat(),
            }
            await connection_manager.send_personal_message(welcome_message, websocket)

            while True:
                data = await websocket.receive_text()
                try:
                    message = json.loads(data)
                    if message.get("type") == "ping":
                        await connection_manager.send_personal_message(
                            {"type": "pong", "timestamp": datetime.now().isoformat()}, websocket
                        )
                    elif message.get("type") == "subscribe":
                        logger.info("客户端请求更新订阅: %(new_topics)s", new_topics=message.get("topics", []))
                    elif message.get("type") == "unsubscribe":
                        logger.info("客户端请求取消订阅: %(remove_topics)s", remove_topics=message.get("topics", []))
                except json.JSONDecodeError:
                    pass

        except WebSocketDisconnect:
            connection_manager.disconnect(websocket)

    except Exception:
        logger.error("WebSocket连接错误")
        if websocket in connection_manager.active_connections:
            connection_manager.disconnect(websocket)


@router.post(
    "/v31/ws/broadcast/{topic}",
    summary="广播 V3.1 风险更新",
    description="向指定 V3.1 风险主题广播更新消息，通知已订阅客户端刷新状态。",
    responses=RISK_WS_BROADCAST_RESPONSES,
)
async def broadcast_risk_update(
    topic: str = Path(..., description="接收广播消息的风险主题名称。"),
    message: Dict[str, Any] = Body(..., openapi_examples=RISK_WS_BROADCAST_EXAMPLES),
):
    try:
        if topic not in connection_manager.subscriptions:
            raise ValidationException(detail=f"不支持的主题: {topic}", field="topic")

        broadcast_message = {"type": "update", "topic": topic, "data": message, "timestamp": datetime.now().isoformat()}
        await connection_manager.broadcast_to_topic(topic, broadcast_message)

        return {
            "status": "success",
            "message": f"消息已广播到主题 '{topic}'",
            "topic": topic,
            "broadcast_at": datetime.now().isoformat(),
        }

    except (BusinessException, ValidationException, NotFoundException):
        raise
    except Exception as e:
        logger.error("广播风险更新失败 %(topic)s: %(e)s")
        raise BusinessException(detail=f"广播失败: {str(e)}", status_code=500, error_code="BROADCAST_FAILED")


@router.get(
    "/v31/ws/connections",
    summary="查询 V3.1 WebSocket 连接统计",
    description="返回当前 V3.1 风险 WebSocket 通道的连接数与各主题订阅分布，用于运行态观测。",
    responses=RISK_WS_CONNECTIONS_RESPONSES,
)
async def get_websocket_connections():
    try:
        return {
            "status": "success",
            "data": {
                "total_connections": len(connection_manager.active_connections),
                "topic_subscriptions": {topic: len(conns) for topic, conns in connection_manager.subscriptions.items()},
                "timestamp": datetime.now().isoformat(),
            },
        }
    except Exception as e:
        logger.error("获取WebSocket连接统计失败: %(e)s")
        raise BusinessException(
            detail=f"获取统计失败: {str(e)}", status_code=500, error_code="STATISTICS_RETRIEVAL_FAILED"
        )


async def setup_risk_event_broadcasting():
    try:
        if not ENHANCED_RISK_FEATURES_AVAILABLE:
            logger.warning("增强风险功能不可用，跳过WebSocket广播设置")
            return
        logger.info("风险事件WebSocket广播设置完成")
    except Exception:
        logger.error("设置风险事件广播失败")


try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = None

if loop is not None:
    loop.create_task(setup_risk_event_broadcasting())
