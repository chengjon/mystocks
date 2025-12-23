"""
Socket.IO服务器管理器单元测试

Test Socket.IO Manager - WebSocket connection and event handling

Task 4.1: Socket.IO服务器实现测试

Author: Claude Code
Date: 2025-11-06
"""

import pytest
import asyncio

from app.core.socketio_manager import (
    ConnectionManager,
    get_socketio_manager,
    reset_socketio_manager,
)
from app.models.websocket_message import (
    create_request_message,
    create_response_message,
    create_error_message,
)


class TestConnectionManager:
    """测试连接管理器"""

    def setup_method(self):
        """测试前初始化"""
        self.manager = ConnectionManager()

    def test_add_connection(self):
        """测试添加连接"""
        self.manager.add_connection("sid_001", user_id="user_001")

        assert "sid_001" in self.manager.active_connections
        assert self.manager.active_connections["sid_001"]["user_id"] == "user_001"
        assert self.manager.active_connections["sid_001"]["message_count"] == 0

    def test_add_connection_without_user(self):
        """测试添加无用户ID的连接"""
        self.manager.add_connection("sid_002")

        assert "sid_002" in self.manager.active_connections
        assert self.manager.active_connections["sid_002"]["user_id"] is None

    def test_remove_connection(self):
        """测试移除连接"""
        self.manager.add_connection("sid_001", user_id="user_001")
        user_id = self.manager.remove_connection("sid_001")

        assert user_id == "user_001"
        assert "sid_001" not in self.manager.active_connections
        assert "user_001" not in self.manager.user_connections

    def test_remove_nonexistent_connection(self):
        """测试移除不存在的连接"""
        user_id = self.manager.remove_connection("nonexistent")

        assert user_id is None

    def test_get_connection(self):
        """测试获取连接信息"""
        self.manager.add_connection("sid_001", user_id="user_001")
        conn = self.manager.get_connection("sid_001")

        assert conn is not None
        assert conn["user_id"] == "user_001"
        assert conn["sid"] == "sid_001"

    def test_is_connected(self):
        """测试检查连接状态"""
        self.manager.add_connection("sid_001", user_id="user_001")

        assert self.manager.is_connected("sid_001")
        assert not self.manager.is_connected("nonexistent")

    def test_subscribe_to_room(self):
        """测试订阅房间"""
        self.manager.add_connection("sid_001")
        success = self.manager.subscribe_to_room("sid_001", "room_001")

        assert success
        assert "room_001" in self.manager.active_connections["sid_001"]["rooms"]
        assert "sid_001" in self.manager.room_members["room_001"]

    def test_subscribe_to_room_nonexistent_connection(self):
        """测试订阅房间时连接不存在"""
        success = self.manager.subscribe_to_room("nonexistent", "room_001")

        assert not success

    def test_unsubscribe_from_room(self):
        """测试取消订阅房间"""
        self.manager.add_connection("sid_001")
        self.manager.subscribe_to_room("sid_001", "room_001")
        success = self.manager.unsubscribe_from_room("sid_001", "room_001")

        assert success
        assert "room_001" not in self.manager.active_connections["sid_001"]["rooms"]
        assert "room_001" not in self.manager.room_members

    def test_get_room_members(self):
        """测试获取房间成员"""
        self.manager.add_connection("sid_001")
        self.manager.add_connection("sid_002")
        self.manager.subscribe_to_room("sid_001", "room_001")
        self.manager.subscribe_to_room("sid_002", "room_001")

        members = self.manager.get_room_members("room_001")

        assert len(members) == 2
        assert "sid_001" in members
        assert "sid_002" in members

    def test_get_user_connections(self):
        """测试获取用户所有连接"""
        self.manager.add_connection("sid_001", user_id="user_001")
        self.manager.add_connection("sid_002", user_id="user_001")

        sids = self.manager.get_user_connections("user_001")

        assert len(sids) == 2
        assert "sid_001" in sids
        assert "sid_002" in sids

    def test_update_activity(self):
        """测试更新活动时间"""
        self.manager.add_connection("sid_001")
        old_time = self.manager.active_connections["sid_001"]["last_activity"]

        asyncio.sleep(0.01)  # 等待一段时间
        self.manager.update_activity("sid_001")
        new_time = self.manager.active_connections["sid_001"]["last_activity"]

        assert new_time >= old_time

    def test_increment_message_count(self):
        """测试增加消息计数"""
        self.manager.add_connection("sid_001")

        self.manager.increment_message_count("sid_001")
        assert self.manager.active_connections["sid_001"]["message_count"] == 1

        self.manager.increment_message_count("sid_001")
        assert self.manager.active_connections["sid_001"]["message_count"] == 2

    def test_get_stats(self):
        """测试获取统计信息"""
        self.manager.add_connection("sid_001", user_id="user_001")
        self.manager.add_connection("sid_002", user_id="user_002")
        self.manager.subscribe_to_room("sid_001", "room_001")

        stats = self.manager.get_stats()

        assert stats["total_connections"] == 2
        assert stats["total_users"] == 2
        assert stats["total_rooms"] == 1
        assert "timestamp" in stats


class TestMySocketIOManager:
    """测试Socket.IO服务器管理器"""

    def setup_method(self):
        """测试前初始化"""
        reset_socketio_manager()
        self.manager = get_socketio_manager()

    def teardown_method(self):
        """测试后清理"""
        reset_socketio_manager()

    def test_manager_initialization(self):
        """测试管理器初始化"""
        assert self.manager is not None
        assert self.manager.connection_manager is not None
        assert self.manager.request_handlers is not None

    def test_singleton_pattern(self):
        """测试单例模式"""
        manager1 = get_socketio_manager()
        manager2 = get_socketio_manager()

        assert manager1 is manager2

    def test_register_request_handler(self):
        """测试注册请求处理器"""

        async def handler(sid: str, request):
            return {"success": True, "data": "test"}

        self.manager.register_request_handler("test_action", handler)

        assert "test_action" in self.manager.request_handlers
        assert self.manager.request_handlers["test_action"] == handler

    def test_get_stats(self):
        """测试获取统计信息"""
        # 添加一些连接
        self.manager.connection_manager.add_connection("sid_001", user_id="user_001")
        self.manager.connection_manager.subscribe_to_room("sid_001", "room_001")

        stats = self.manager.get_stats()

        assert stats["total_connections"] == 1
        assert stats["total_users"] == 1
        assert stats["total_rooms"] == 1
        assert stats["namespace"] == "/"


class TestWebSocketMessageFormats:
    """测试WebSocket消息格式"""

    def test_create_request_message(self):
        """测试创建请求消息"""
        msg = create_request_message(
            request_id="req_001",
            action="get_data",
            payload={"key": "value"},
            user_id="user_001",
        )

        assert msg.request_id == "req_001"
        assert msg.action == "get_data"
        assert msg.payload["key"] == "value"
        assert msg.user_id == "user_001"

    def test_create_response_message(self):
        """测试创建响应消息"""
        msg = create_response_message(
            request_id="req_001",
            data={"result": "success"},
        )

        assert msg.request_id == "req_001"
        assert msg.success is True
        assert msg.data["result"] == "success"

    def test_create_error_message(self):
        """测试创建错误消息"""
        msg = create_error_message(
            error_code="INVALID_ACTION",
            error_message="The action is invalid",
            request_id="req_001",
        )

        assert msg.error_code == "INVALID_ACTION"
        assert msg.error_message == "The action is invalid"
        assert msg.request_id == "req_001"

    def test_message_serialization(self):
        """测试消息序列化"""
        msg = create_response_message(
            request_id="req_001",
            data={"value": 123},
        )

        # 序列化为JSON兼容格式
        serialized = msg.model_dump(mode="json")

        assert serialized["request_id"] == "req_001"
        assert serialized["type"] == "response"
        assert serialized["success"] is True
        assert serialized["data"]["value"] == 123


@pytest.mark.asyncio
class TestSocketIOIntegration:
    """Socket.IO集成测试"""

    def setup_method(self):
        """测试前重置管理器"""
        reset_socketio_manager()

    def teardown_method(self):
        """测试后清理"""
        reset_socketio_manager()

    async def test_connection_lifecycle(self):
        """测试连接生命周期"""
        manager = get_socketio_manager()

        # 模拟连接
        manager.connection_manager.add_connection("sid_001", user_id="user_001")

        # 验证连接已添加
        assert manager.connection_manager.is_connected("sid_001")
        stats = manager.get_stats()
        assert stats["total_connections"] == 1

        # 模拟断开连接
        manager.connection_manager.remove_connection("sid_001")

        # 验证连接已移除
        assert not manager.connection_manager.is_connected("sid_001")
        stats = manager.get_stats()
        assert stats["total_connections"] == 0

    async def test_room_subscription_lifecycle(self):
        """测试房间订阅生命周期"""
        manager = get_socketio_manager()

        # 添加连接
        manager.connection_manager.add_connection("sid_001")

        # 订阅房间
        manager.connection_manager.subscribe_to_room("sid_001", "stock_600519")

        # 验证订阅
        members = manager.connection_manager.get_room_members("stock_600519")
        assert "sid_001" in members

        # 取消订阅
        manager.connection_manager.unsubscribe_from_room("sid_001", "stock_600519")

        # 验证取消订阅
        members = manager.connection_manager.get_room_members("stock_600519")
        assert len(members) == 0

    async def test_multi_room_subscription(self):
        """测试多房间订阅"""
        manager = get_socketio_manager()
        manager.connection_manager.add_connection("sid_001")

        # 订阅多个房间
        manager.connection_manager.subscribe_to_room("sid_001", "room_1")
        manager.connection_manager.subscribe_to_room("sid_001", "room_2")
        manager.connection_manager.subscribe_to_room("sid_001", "room_3")

        # 验证订阅
        rooms = manager.connection_manager.active_connections["sid_001"]["rooms"]
        assert len(rooms) == 3
        assert "room_1" in rooms
        assert "room_2" in rooms
        assert "room_3" in rooms

    async def test_multi_user_same_room(self):
        """测试多用户同一房间"""
        manager = get_socketio_manager()

        # 添加多个连接并订阅同一房间
        manager.connection_manager.add_connection("sid_001", user_id="user_001")
        manager.connection_manager.add_connection("sid_002", user_id="user_002")
        manager.connection_manager.add_connection("sid_003", user_id="user_003")

        manager.connection_manager.subscribe_to_room("sid_001", "market")
        manager.connection_manager.subscribe_to_room("sid_002", "market")
        manager.connection_manager.subscribe_to_room("sid_003", "market")

        # 验证房间成员
        members = manager.connection_manager.get_room_members("market")
        assert len(members) == 3

        # 验证统计信息
        stats = manager.get_stats()
        assert stats["total_users"] == 3
        assert stats["total_rooms"] == 1
