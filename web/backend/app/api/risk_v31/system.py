"""
系统、WebSocket与核心监控路由 (V3.1)
"""
import structlog
from datetime import datetime
from typing import Any, Dict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.exceptions import BusinessException
from app.utils.risk_utils import connection_manager

# 导入核心
try:
    from src.governance.risk_management import get_risk_management_core
    RISK_MANAGEMENT_V31_AVAILABLE = True
except ImportError:
    RISK_MANAGEMENT_V31_AVAILABLE = False
    get_risk_management_core = None

logger = structlog.get_logger(__name__)
router = APIRouter()

@router.get("/stock/{symbol}")
async def get_stock_risk_v31(symbol: str) -> Dict[str, Any]:
    """V3.1 个股风险监控"""
    try:
        core = get_risk_management_core()
        risk_metrics = await core.calculate_stock_risk(symbol)
        return {"status": "success", "data": {"symbol": symbol, "risk_metrics": risk_metrics.__dict__}}
    except Exception as e:
        raise BusinessException(detail=str(e), status_code=500)

@router.get("/health")
async def get_risk_management_health() -> Dict[str, Any]:
    """V3.1 风险管理系统健康检查"""
    return {"status": "healthy", "version": "3.1", "checked_at": datetime.now().isoformat()}

@router.websocket("/ws/risk-updates")
async def websocket_risk_updates(websocket: WebSocket, topics: str = "portfolio_risk,stock_risk,alerts"):
    """WebSocket实时风险数据推送 (V3.1)"""
    topic_list = [t.strip() for t in topics.split(",") if t.strip()]
    await connection_manager.connect(websocket, topic_list)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle messages...
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)

@router.get("/ws/connections")
async def get_websocket_connections():
    """获取WebSocket连接统计 (V3.1)"""
    return {
        "status": "success",
        "data": {"total": len(connection_manager.active_connections)}
    }
