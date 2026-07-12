import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.risk._shared import (
    ENHANCED_RISK_FEATURES_AVAILABLE,
    RISK_MANAGEMENT_V31_AVAILABLE,
    get_risk_management_core,
    logger,
)
from app.core.exceptions import BusinessException, NotFoundException, ValidationException


router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-V3.1"])


@router.get("/v31/stock/{symbol}")
async def get_stock_risk_v31(symbol: str) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED",
            )

        core = get_risk_management_core()
        if not core:
            raise BusinessException(
                detail="风险管理核心不可用", status_code=503, error_code="RISK_MANAGEMENT_CORE_UNAVAILABLE",
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
            detail=f"个股风险计算失败: {e!s}", status_code=500, error_code="INDIVIDUAL_STOCK_RISK_CALCULATION_FAILED",
        )


@router.get("/v31/portfolio/{portfolio_id}")
async def get_portfolio_risk_v31(portfolio_id: str) -> Dict[str, Any]:
    try:
        if not RISK_MANAGEMENT_V31_AVAILABLE:
            raise BusinessException(
                detail="V3.1风险管理系统未初始化", status_code=503, error_code="RISK_MANAGEMENT_SYSTEM_NOT_INITIALIZED",
            )

        core = get_risk_management_core()
        if not core:
            raise BusinessException(
                detail="风险管理核心不可用", status_code=503, error_code="RISK_MANAGEMENT_CORE_UNAVAILABLE",
            )

        risk_metrics = await core.calculate_portfolio_risk(portfolio_id)
        await core._publish_risk_event(
            "portfolio_risk_calculated", {"portfolio_id": portfolio_id, "metrics": risk_metrics.__dict__},
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
            detail=f"组合风险计算失败: {e!s}", status_code=500, error_code="PORTFOLIO_RISK_CALCULATION_FAILED",
        )


@router.get("/v31/health")
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
                            {"type": "pong", "timestamp": datetime.now().isoformat()}, websocket,
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


@router.post("/v31/ws/broadcast/{topic}")
async def broadcast_risk_update(topic: str, message: Dict[str, Any]):
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
        raise BusinessException(detail=f"广播失败: {e!s}", status_code=500, error_code="BROADCAST_FAILED")


@router.get("/v31/ws/connections")
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
            detail=f"获取统计失败: {e!s}", status_code=500, error_code="STATISTICS_RETRIEVAL_FAILED",
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
