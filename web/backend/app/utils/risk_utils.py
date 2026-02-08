"""
风险管理工具模块

存放风险管理相关的辅助函数、类和单例。
拆分自 risk_management.py。

Author: Claude Code
Date: 2026-02-08
"""

import asyncio
import json
import structlog
from typing import Dict, List, Set, Any
from datetime import datetime
from fastapi import WebSocket

from src.monitoring.monitoring_database import MonitoringDatabase

logger = structlog.get_logger(__name__)

# 延迟初始化监控数据库（避免导入时需要完整环境变量）
_monitoring_db = None

def get_monitoring_db():
    """获取监控数据库实例（延迟初始化）"""
    global _monitoring_db
    if _monitoring_db is None:
        try:
            real_monitoring_db = MonitoringDatabase()

            # 创建适配器来匹配Week1 API的参数命名约定
            class MonitoringAdapter:
                def __init__(self, real_db):
                    self.real_db = real_db

                def log_operation(
                    self,
                    operation_type="UNKNOWN",
                    table_name=None,
                    operation_name=None,
                    rows_affected=0,
                    operation_time_ms=0,
                    success=True,
                    details="",
                    **kwargs,
                ):
                    """适配Week1 API的参数命名到MonitoringDatabase的实际参数"""
                    try:
                        return self.real_db.log_operation(
                            operation_type=operation_type,
                            classification="DERIVED_DATA",
                            target_database="PostgreSQL",
                            table_name=table_name,
                            record_count=rows_affected,
                            operation_status="SUCCESS" if success else "FAILED",
                            error_message=None if success else details,
                            execution_time_ms=int(operation_time_ms),
                            additional_info=(
                                {"operation_name": operation_name, "details": details}
                                if operation_name or details
                                else None
                            ),
                        )
                    except Exception as e:
                        logger.debug(f"Monitoring log failed (non-critical): {e}")
                        return False

            _monitoring_db = MonitoringAdapter(real_monitoring_db)

        except Exception as e:
            logger.warning(f"MonitoringDatabase initialization failed, using fallback: {e}")

            # 创建一个简单的fallback对象
            class MonitoringFallback:
                def log_operation(self, *args, **kwargs):
                    return True  # Silent fallback

            _monitoring_db = MonitoringFallback()
    return _monitoring_db


class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: Dict[str, Set[WebSocket]] = {
            "portfolio_risk": set(),
            "stock_risk": set(),
            "alerts": set(),
            "stop_loss": set(),
        }

    async def connect(self, websocket: WebSocket, topics: List[str] = None):
        """建立WebSocket连接"""
        await websocket.accept()
        self.active_connections.append(websocket)

        # 订阅指定主题
        if topics:
            for topic in topics:
                if topic in self.subscriptions:
                    self.subscriptions[topic].add(websocket)

        logger.info(f"WebSocket连接建立，订阅主题: {topics}")

    def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

        # 取消所有订阅
        for topic_connections in self.subscriptions.values():
            topic_connections.discard(websocket)

        logger.info("WebSocket连接断开")

    async def broadcast_to_topic(self, topic: str, message: Dict[str, Any]):
        """向特定主题的订阅者广播消息"""
        if topic not in self.subscriptions:
            return

        disconnected = []
        message_json = json.dumps(message)

        for connection in self.subscriptions[topic]:
            try:
                await connection.send_text(message_json)
            except Exception:
                disconnected.append(connection)

        # 清理断开的连接
        for connection in disconnected:
            self.disconnect(connection)

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """向特定连接发送消息"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.disconnect(websocket)

# 全局连接管理器实例
connection_manager = ConnectionManager()

async def setup_risk_event_broadcasting(enhanced_risk_features_available: bool = False):
    """
    设置风险事件自动广播到WebSocket

    这个函数应该在应用启动时调用，以设置事件监听器。
    """
    try:
        if not enhanced_risk_features_available:
            logger.warning("增强风险功能不可用，跳过WebSocket广播设置")
            return

        # 这里可以设置事件监听器，当风险事件发生时自动广播
        # 例如监听SignalRecorder的事件或直接集成到风险计算函数中

        logger.info("风险事件WebSocket广播设置完成")

    except Exception as e:
        logger.error(f"设置风险事件广播失败: {e}")
