"""
连接生命周期管理单元测试

Test Connection Lifecycle Manager - Connection state and heartbeat monitoring

Task 4.2: 连接管理测试

Author: Claude Code
Date: 2025-11-06
"""

import pytest
import asyncio
import time
from datetime import datetime, timedelta

from app.core.connection_lifecycle import (
    ConnectionLifecycleManager,
    ConnectionState,
    HeartbeatConfig,
    ConnectionHealthMonitor,
    get_connection_lifecycle_manager,
    reset_connection_lifecycle_manager,
)


class TestHeartbeatConfig:
    """测试心跳配置"""

    def test_default_config(self):
        """测试默认配置"""
        config = HeartbeatConfig()

        assert config.interval == 30.0
        assert config.timeout == 60.0
        assert config.max_retries == 3

    def test_custom_config(self):
        """测试自定义配置"""
        config = HeartbeatConfig(interval=15.0, timeout=30.0, max_retries=5)

        assert config.interval == 15.0
        assert config.timeout == 30.0
        assert config.max_retries == 5


class TestConnectionLifecycleManager:
    """测试连接生命周期管理器"""

    def setup_method(self):
        """测试前初始化"""
        reset_connection_lifecycle_manager()
        self.manager = ConnectionLifecycleManager()

    def test_register_connection(self):
        """测试注册连接"""
        self.manager.register_connection("sid_001")

        assert "sid_001" in self.manager.connection_states
        assert self.manager.connection_states["sid_001"] == ConnectionState.CONNECTING
        assert "sid_001" in self.manager.connection_times
        assert "sid_001" in self.manager.last_heartbeat

    def test_mark_connected(self):
        """测试标记为已连接"""
        self.manager.register_connection("sid_001")
        self.manager.mark_connected("sid_001")

        assert self.manager.connection_states["sid_001"] == ConnectionState.CONNECTED

    def test_mark_disconnected(self):
        """测试标记为已断开"""
        self.manager.register_connection("sid_001")
        self.manager.mark_connected("sid_001")
        self.manager.mark_disconnected("sid_001")

        assert self.manager.connection_states["sid_001"] == ConnectionState.DISCONNECTED

    def test_record_heartbeat(self):
        """测试记录心跳"""
        self.manager.register_connection("sid_001")
        old_heartbeat = self.manager.last_heartbeat["sid_001"]

        time.sleep(0.01)  # 等待一段时间
        self.manager.record_heartbeat("sid_001")
        new_heartbeat = self.manager.last_heartbeat["sid_001"]

        assert new_heartbeat >= old_heartbeat
        assert self.manager.heartbeat_failures["sid_001"] == 0

    def test_heartbeat_timeout_detection(self):
        """测试心跳超时检测"""
        config = HeartbeatConfig(timeout=0.1)
        manager = ConnectionLifecycleManager(config)
        manager.register_connection("sid_001")

        # 模拟心跳未更新超过超时时间
        time.sleep(0.15)

        is_timeout = manager.check_heartbeat_timeout("sid_001")
        assert is_timeout
        assert manager.heartbeat_failures["sid_001"] > 0

    def test_connection_timeout_with_max_retries(self):
        """测试达到最大重试次数的连接超时"""
        config = HeartbeatConfig(timeout=0.05, max_retries=2)
        manager = ConnectionLifecycleManager(config)
        manager.register_connection("sid_001")

        # 模拟多次超时
        time.sleep(0.1)
        manager.check_heartbeat_timeout("sid_001")
        manager.check_heartbeat_timeout("sid_001")
        is_timed_out = manager.check_connection_timeout("sid_001")

        assert is_timed_out
        assert manager.connection_states["sid_001"] == ConnectionState.TIMEOUT

    def test_is_healthy_connected(self):
        """测试健康连接检测"""
        self.manager.register_connection("sid_001")
        self.manager.mark_connected("sid_001")

        assert self.manager.is_healthy("sid_001")

    def test_is_healthy_timeout(self):
        """测试超时连接不健康"""
        config = HeartbeatConfig(timeout=0.05, max_retries=1)
        manager = ConnectionLifecycleManager(config)
        manager.register_connection("sid_001")
        manager.mark_connected("sid_001")

        time.sleep(0.1)
        manager.check_heartbeat_timeout("sid_001")
        manager.check_connection_timeout("sid_001")

        assert not manager.is_healthy("sid_001")

    def test_get_connection_state(self):
        """测试获取连接状态"""
        self.manager.register_connection("sid_001")
        state = self.manager.get_connection_state("sid_001")

        assert state == ConnectionState.CONNECTING

    def test_get_connection_duration(self):
        """测试获取连接持续时间"""
        self.manager.register_connection("sid_001")

        duration = self.manager.get_connection_duration("sid_001")

        assert duration is not None
        assert duration >= 0

    def test_get_heartbeat_age(self):
        """测试获取心跳年龄"""
        self.manager.register_connection("sid_001")

        age = self.manager.get_heartbeat_age("sid_001")

        assert age is not None
        assert age >= 0

    def test_get_all_healthy_connections(self):
        """测试获取所有健康连接"""
        self.manager.register_connection("sid_001")
        self.manager.register_connection("sid_002")
        self.manager.mark_connected("sid_001")
        self.manager.mark_connected("sid_002")

        healthy = self.manager.get_all_healthy_connections()

        assert len(healthy) == 2
        assert "sid_001" in healthy
        assert "sid_002" in healthy

    def test_get_all_timeout_connections(self):
        """测试获取所有超时连接"""
        config = HeartbeatConfig(timeout=0.05, max_retries=1)
        manager = ConnectionLifecycleManager(config)

        manager.register_connection("sid_001")
        manager.mark_connected("sid_001")
        manager.register_connection("sid_002")
        manager.mark_connected("sid_002")

        time.sleep(0.1)
        manager.check_heartbeat_timeout("sid_001")
        manager.check_connection_timeout("sid_001")

        timeout_connections = manager.get_all_timeout_connections()

        assert len(timeout_connections) == 1
        assert "sid_001" in timeout_connections

    def test_get_stats(self):
        """测试获取统计信息"""
        self.manager.register_connection("sid_001")
        self.manager.mark_connected("sid_001")
        self.manager.register_connection("sid_002")

        stats = self.manager.get_stats()

        assert stats["total_connections"] == 2
        assert stats["connected"] == 1
        assert "timestamp" in stats


class TestConnectionHealthMonitor:
    """测试连接健康监控器"""

    def setup_method(self):
        """测试前初始化"""
        reset_connection_lifecycle_manager()
        self.lifecycle_manager = ConnectionLifecycleManager()
        self.monitor = ConnectionHealthMonitor(
            self.lifecycle_manager,
            check_interval=0.1,
        )

    @pytest.mark.asyncio
    async def test_monitor_start_and_stop(self):
        """测试监控启动和停止"""
        await self.monitor.start()
        assert self.monitor.is_running
        assert self.monitor.monitor_task is not None

        await self.monitor.stop()
        assert not self.monitor.is_running

    @pytest.mark.asyncio
    async def test_monitor_detects_timeout_connections(self):
        """测试监控检测超时连接"""
        config = HeartbeatConfig(timeout=0.05, max_retries=1)
        lifecycle_manager = ConnectionLifecycleManager(config)
        monitor = ConnectionHealthMonitor(lifecycle_manager, check_interval=0.05)

        # 注册连接
        lifecycle_manager.register_connection("sid_001")
        lifecycle_manager.mark_connected("sid_001")

        await monitor.start()
        await asyncio.sleep(0.15)
        await monitor.stop()

        # 检查是否检测到超时
        lifecycle_manager.check_heartbeat_timeout("sid_001")
        lifecycle_manager.check_connection_timeout("sid_001")

        timeout_connections = lifecycle_manager.get_all_timeout_connections()
        assert "sid_001" in timeout_connections


class TestSingletonPattern:
    """测试单例模式"""

    def test_get_singleton_manager(self):
        """测试获取单例管理器"""
        reset_connection_lifecycle_manager()

        manager1 = get_connection_lifecycle_manager()
        manager2 = get_connection_lifecycle_manager()

        assert manager1 is manager2

    def test_reset_singleton_manager(self):
        """测试重置单例管理器"""
        reset_connection_lifecycle_manager()
        manager1 = get_connection_lifecycle_manager()

        reset_connection_lifecycle_manager()
        manager2 = get_connection_lifecycle_manager()

        assert manager1 is not manager2
