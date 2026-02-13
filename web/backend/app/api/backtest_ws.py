"""
WebSocket endpoints for backtest progress

回测进度 WebSocket 推送
"""

import json
import logging
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.celery_app import register_progress_callback, unregister_progress_callback

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ws", tags=["WebSocket"])

# 存储活跃的 WebSocket 连接
active_connections: Dict[str, Set[WebSocket]] = {}


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        self.connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, backtest_id: str):
        """接受新的 WebSocket 连接"""
        await websocket.accept()

        if backtest_id not in self.connections:
            self.connections[backtest_id] = set()
        self.connections[backtest_id].add(websocket)

        # 注册进度回调
        register_progress_callback(backtest_id, lambda data: self._sync_broadcast(backtest_id, data))

        logger.info("WebSocket连接建立: backtest_id=%(backtest_id)s")

    def disconnect(self, websocket: WebSocket, backtest_id: str):
        """断开 WebSocket 连接"""
        if backtest_id in self.connections:
            self.connections[backtest_id].discard(websocket)

            # 如果没有更多连接，注销回调
            if not self.connections[backtest_id]:
                del self.connections[backtest_id]
                unregister_progress_callback(backtest_id)

        logger.info("WebSocket连接断开: backtest_id=%(backtest_id)s")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_text(message)
        except Exception:
            logger.error("发送WebSocket消息失败: %(e)s")

    async def broadcast(self, backtest_id: str, message: dict):
        """向所有订阅该 backtest_id 的连接广播消息"""
        if backtest_id not in self.connections:
            return

        disconnected = set()
        message_json = json.dumps(message)

        for connection in self.connections[backtest_id]:
            try:
                await connection.send_text(message_json)
            except Exception:
                logger.warning("广播消息失败: %(e)s")
                disconnected.add(connection)

        # 清理断开的连接
        for conn in disconnected:
            self.connections[backtest_id].discard(conn)

    def _sync_broadcast(self, backtest_id: str, message: dict):
        """同步版本的广播（供 Celery 回调使用）"""
        import asyncio

        if backtest_id not in self.connections:
            return

        message_json = json.dumps(message)

        for connection in list(self.connections[backtest_id]):
            try:
                # 在事件循环中发送
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(connection.send_text(message_json))
                else:
                    asyncio.run(connection.send_text(message_json))
            except Exception:
                logger.warning("同步广播失败: %(e)s")


# 创建全局连接管理器
manager = ConnectionManager()


@router.websocket("/backtest/{backtest_id}")
async def websocket_backtest_progress(websocket: WebSocket, backtest_id: str):
    """
    WebSocket endpoint for backtest progress updates

    订阅指定回测任务的进度更新
    """
    await manager.connect(websocket, backtest_id)

    try:
        # 发送连接确认
        await manager.send_personal_message(
            json.dumps({"type": "connected", "backtest_id": backtest_id, "message": "已连接到回测进度推送"}), websocket
        )

        # 保持连接，等待消息
        while True:
            try:
                # 接收客户端消息（心跳或取消请求）
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "ping":
                    # 心跳响应
                    await manager.send_personal_message(json.dumps({"type": "pong"}), websocket)
                elif message.get("type") == "cancel":
                    # 取消回测请求
                    # TODO: 实现取消逻辑
                    await manager.send_personal_message(
                        json.dumps({"type": "cancelled", "message": "回测已取消"}), websocket
                    )
                    break

            except json.JSONDecodeError:
                logger.warning("收到无效的JSON消息")

    except WebSocketDisconnect:
        logger.info("WebSocket客户端断开: backtest_id=%(backtest_id)s")
    except Exception:
        logger.error("WebSocket错误: %(e)s")
    finally:
        manager.disconnect(websocket, backtest_id)


@router.get("/status")
async def get_websocket_status():
    """
    获取 WebSocket 连接状态

    Returns:
        当前活跃连接数
    """
    total_connections = sum(len(conns) for conns in manager.connections.values())

    return {
        "status": "ok",
        "total_connections": total_connections,
        "backtest_subscriptions": len(manager.connections),
        "details": {backtest_id: len(conns) for backtest_id, conns in manager.connections.items()},
    }
