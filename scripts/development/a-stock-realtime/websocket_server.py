"""
A股实时行情WebSocket服务器
使用FastAPI + WebSocket实现实时数据推送
"""
import json
import asyncio
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from market_data_simulator import MarketDataSimulator


app = FastAPI(title="MyStocks A股实时行情API", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
simulator = MarketDataSimulator()
active_connections: Set[WebSocket] = set()


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"[{datetime.now()}] 新客户端连接，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"[{datetime.now()}] 客户端断开，当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        """向所有连接的客户端广播消息"""
        if not self.active_connections:
            return

        message_str = json.dumps(message, ensure_ascii=False)
        disconnected = set()

        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                print(f"[{datetime.now()}] 广播失败: {e}")
                disconnected.add(connection)

        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)


manager = ConnectionManager()


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "MyStocks A股实时行情WebSocket API",
        "version": "1.0.0",
        "endpoints": {
            "websocket": "/ws/market",
            "health": "/health"
        },
        "websocket_usage": {
            "endpoint": "ws://localhost:8000/ws/market",
            "initial_message": "发送 'start' 开始接收实时数据",
            "stop_message": "发送 'stop' 停止接收数据"
        }
    }


@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "connections": len(manager.active_connections)
    }


@app.websocket("/ws/market")
async def websocket_market_data(websocket: WebSocket):
    """WebSocket行情数据推送端点"""
    await manager.connect(websocket)

    try:
        # 发送初始完整快照
        snapshot = simulator.get_full_snapshot()
        await manager.send_personal_message(json.dumps({
            "type": "init",
            "data": snapshot
        }, ensure_ascii=False), websocket)

        # 启动增量更新推送
        push_task = asyncio.create_task(market_data_push(websocket))

        # 处理客户端消息
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("action") == "start":
                await manager.send_personal_message(json.dumps({
                    "type": "info",
                    "message": "开始接收实时行情数据..."
                }, ensure_ascii=False), websocket)

            elif message.get("action") == "stop":
                await manager.send_personal_message(json.dumps({
                    "type": "info",
                    "message": "已停止接收实时数据"
                }, ensure_ascii=False), websocket)
                push_task.cancel()

            elif message.get("action") == "snapshot":
                snapshot = simulator.get_full_snapshot()
                await manager.send_personal_message(json.dumps({
                    "type": "snapshot",
                    "data": snapshot
                }, ensure_ascii=False), websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print(f"[{datetime.now()}] WebSocket客户端正常断开")
    except Exception as e:
        manager.disconnect(websocket)
        print(f"[{datetime.now()}] WebSocket错误: {e}")


async def market_data_push(websocket: WebSocket):
    """推送市场数据的异步任务"""
    try:
        while True:
            # 每1秒推送一次增量更新
            update = simulator.get_incremental_update()
            await manager.send_personal_message(json.dumps(update, ensure_ascii=False), websocket)

            # 等待1秒
            await asyncio.sleep(1)

    except (asyncio.CancelledError, RuntimeError, WebSocketDisconnect):
        print(f"[{datetime.now()}] 数据推送任务已停止")
    except Exception as e:
        print(f"[{datetime.now()}] 数据推送错误: {e}")


if __name__ == "__main__":
    import uvicorn

    print("=" * 60)
    print("🚀 MyStocks A股实时行情WebSocket服务器")
    print("=" * 60)
    print("📡 WebSocket端点: ws://localhost:8001/ws/market")
    print("🏥 健康检查: http://localhost:8001/health")
    print("📚 API文档: http://localhost:8001/docs")
    print("=" * 60)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
