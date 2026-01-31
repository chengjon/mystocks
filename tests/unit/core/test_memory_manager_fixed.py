#!/usr/bin/env python3
"""
内存管理模块单元测试 - 源代码覆盖率测试 (修复版)

测试MyStocks系统中完整的内存管理功能，包括监控、资源管理和泄漏检测
"""

import os
import sys
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.memory_manager import (
    MemoryLimit,
    MemoryMonitor,
    MemoryStats,
    ResourceManager,
    cleanup_all_resources,
    get_memory_monitor,
    get_resource_manager,
    initialize_memory_management,
    register_resource,
    shutdown_memory_management,
)


class TestMemoryStats:
    """测试内存统计信息类"""

    def test_memory_stats_creation(self):
        """测试内存统计信息创建"""
        timestamp = datetime.now()
        stats = MemoryStats(
            timestamp=timestamp,
            process_memory_mb=100.5,
            system_memory_percent=75.2,
            active_objects=1000,
            total_objects=1200,
            leak_candidates=["TestType:1500"],
        )

        assert stats.timestamp == timestamp
        assert stats.process_memory_mb == 100.5
        assert stats.system_memory_percent == 75.2
        assert stats.active_objects == 1000
        assert stats.total_objects == 1200
        assert stats.leak_candidates == ["TestType:1500"]


class TestMemoryLimit:
    """测试内存限制管理器"""

    def test_memory_limit_initialization(self):
        """测试内存限制初始化"""
        limit = MemoryLimit(max_memory_mb=1024, warning_threshold=0.8)

        assert limit.max_memory_mb == 1024
        assert limit.warning_threshold == 0.8
        assert limit.warning_threshold_mb == 819.2  # 1024 * 0.8
        assert len(limit._monitors) == 0

    @patch("psutil.Process")
    def test_check_memory_usage(self, mock_process):
        """测试内存使用检查"""
        # 模拟psutil返回值
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 512  # 512MB
        mock_process.return_value = mock_process_instance

        limit = MemoryLimit()
        memory_mb = limit.check_memory_usage()

        assert memory_mb == 512.0
        mock_process_instance.memory_info.assert_called_once()

    @patch("psutil.Process")
    def test_is_approaching_limit_true(self, mock_process):
        """测试接近内存限制 - 真"""
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 900  # 900MB
        mock_process.return_value = mock_process_instance

        limit = MemoryLimit(max_memory_mb=1024, warning_threshold=0.8)
        assert limit.is_approaching_limit() is True

    @patch("psutil.Process")
    def test_is_over_limit_true(self, mock_process):
        """测试超过内存限制 - 真"""
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 1200  # 1200MB
        mock_process.return_value = mock_process_instance

        limit = MemoryLimit(max_memory_mb=1024)
        assert limit.is_over_limit() is True

    def test_register_monitor(self):
        """测试注册内存监控回调"""
        limit = MemoryLimit()
        callback1 = Mock()
        callback2 = Mock()

        limit.register_monitor(callback1)
        limit.register_monitor(callback2)

        assert len(limit._monitors) == 2

    def test_notify_monitors_success(self):
        """测试通知监控器 - 成功"""
        limit = MemoryLimit()
        callback1 = Mock()
        callback2 = Mock()

        limit.register_monitor(callback1)
        limit.register_monitor(callback2)

        limit.notify_monitors(512.0)

        callback1.assert_called_once_with(512.0)
        callback2.assert_called_once_with(512.0)


class TestResourceManager:
    """测试资源管理器"""

    def test_resource_manager_initialization(self):
        """测试资源管理器初始化"""
        manager = ResourceManager()

        assert len(manager._resources) == 0
        assert len(manager._weak_refs) == 0
        assert len(manager._cleanup_callbacks) == 0

    def test_register_resource_basic(self):
        """测试注册资源 - 基本功能"""
        manager = ResourceManager()
        resource = {"data": "test"}
        cleanup_callback = Mock()

        manager.register_resource("test_resource", resource, cleanup_callback)

        assert manager.get_resource("test_resource") == resource
        assert "test_resource" in manager._cleanup_callbacks

    def test_register_resource_with_weak_ref_valid(self):
        """测试注册资源 - 使用弱引用（有效对象）"""
        manager = ResourceManager()

        # 创建一个可以被弱引用的对象
        class TestResource:
            def __init__(self):
                self.data = "test"

        resource = TestResource()
        manager.register_resource("test_resource", resource, weak_ref=True)

        assert "test_resource" in manager._weak_refs

    def test_unregister_resource(self):
        """测试注销资源"""
        manager = ResourceManager()
        resource = {"data": "test"}
        cleanup_callback = Mock()

        manager.register_resource("test_resource", resource, cleanup_callback)
        manager.unregister_resource("test_resource")

        assert manager.get_resource("test_resource") is None

    def test_cleanup_resource_with_callback(self):
        """测试清理资源 - 有回调函数"""
        manager = ResourceManager()
        cleanup_callback = Mock()

        manager._cleanup_callbacks["test_resource"] = cleanup_callback
        manager._cleanup_resource("test_resource")

        cleanup_callback.assert_called_once()

    def test_get_stats(self):
        """测试获取资源统计信息"""
        manager = ResourceManager()

        # 创建可以被弱引用的对象
        class TestResource:
            pass

        resource1 = TestResource()
        resource2 = {"data": "test2"}
        cleanup_callback = Mock()

        manager.register_resource("resource1", resource1)
        manager.register_resource("resource2", resource2, cleanup_callback)

        stats = manager.get_stats()

        assert stats["total_resources"] == 2
        assert stats["total_cleanup_callbacks"] == 1
        assert stats["weak_refs"] == 1


class TestMemoryMonitor:
    """测试内存监控器"""

    def test_memory_monitor_initialization(self):
        """测试内存监控器初始化"""
        monitor = MemoryMonitor(check_interval=30, max_history=500)

        assert monitor.check_interval == 30
        assert monitor.max_history == 500
        assert monitor._running is False

    def test_start_already_running(self):
        """测试启动内存监控 - 已在运行"""
        monitor = MemoryMonitor()
        monitor._running = True

        monitor.start()
        assert monitor._running is True

    def test_stop_not_running(self):
        """测试停止内存监控 - 未运行"""
        monitor = MemoryMonitor()
        monitor._running = False

        monitor.stop()
        assert monitor._running is False

    @patch("src.core.memory_manager.psutil.Process")
    @patch("src.core.memory_manager.gc.get_objects")
    def test_collect_stats(self, mock_get_objects, mock_process):
        """测试收集内存统计信息"""
        # 模拟psutil返回值
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 512  # 512MB
        mock_process.return_value = mock_process_instance

        # 模拟gc返回值
        mock_get_objects.return_value = ["obj1", "obj2", "obj3", None]

        # 模拟系统内存
        with patch("src.core.memory_manager.psutil.virtual_memory") as mock_virtual_memory:
            mock_virtual_memory.return_value.percent = 75.0

            monitor = MemoryMonitor()
            monitor._detect_leak_candidates = Mock(return_value=[])

            stats = monitor._collect_stats()

            assert stats.process_memory_mb == 512.0
            assert stats.system_memory_percent == 75.0
            assert stats.active_objects == 3  # 排除None

    def test_update_stats_history(self):
        """测试更新统计历史"""
        monitor = MemoryMonitor(max_history=3)
        stats1 = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=100,
            system_memory_percent=50,
            active_objects=100,
            total_objects=120,
            leak_candidates=[],
        )
        stats2 = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=200,
            system_memory_percent=60,
            active_objects=200,
            total_objects=220,
            leak_candidates=[],
        )

        monitor._update_stats_history(stats1)
        monitor._update_stats_history(stats2)

        assert len(monitor._stats_history) == 2

    @patch("src.core.memory_manager.gc.get_objects")
    def test_detect_leak_candidates_above_threshold(self, mock_get_objects):
        """测试检测内存泄漏候选者 - 超过阈值"""

        # 创建模拟对象类型
        class TestClass:
            pass

        obj1 = TestClass()
        obj2 = TestClass()

        # 创建超过1000个对象
        objects = [obj1, obj2] * 501  # 1002个对象
        mock_get_objects.return_value = objects

        monitor = MemoryMonitor()
        candidates = monitor._detect_leak_candidates()

        assert len(candidates) <= 5

    @patch("src.core.memory_manager.gc.get_objects")
    def test_detect_leak_candidates_below_threshold(self, mock_get_objects):
        """测试检测内存泄漏候选者 - 低于阈值"""
        mock_get_objects.return_value = ["obj"] * 500  # 低于阈值

        monitor = MemoryMonitor()
        candidates = monitor._detect_leak_candidates()

        assert len(candidates) == 0

    @patch("src.core.memory_manager.gc.collect")
    def test_emergency_cleanup(self, mock_gc_collect):
        """测试紧急清理"""
        mock_gc_collect.return_value = 50

        # 模拟全局resource_manager
        with patch("src.core.memory_manager._resource_manager") as mock_resource_manager:
            mock_resource_manager.cleanup_all = Mock()

            monitor = MemoryMonitor()
            monitor._emergency_cleanup()

            mock_gc_collect.assert_called_once()
            mock_resource_manager.cleanup_all.assert_called_once()

    def test_get_current_stats_empty_history(self):
        """测试获取当前统计信息 - 空历史"""
        monitor = MemoryMonitor()

        current = monitor.get_current_stats()

        assert current.process_memory_mb == 0
        assert current.system_memory_percent == 0
        assert current.active_objects == 0


class TestGlobalFunctions:
    """测试全局函数"""

    def test_get_resource_manager(self):
        """测试获取全局资源管理器"""
        manager1 = get_resource_manager()
        manager2 = get_resource_manager()

        assert isinstance(manager1, ResourceManager)
        assert manager1 is manager2  # 应该是同一个实例

    def test_get_memory_monitor(self):
        """测试获取全局内存监控器"""
        monitor1 = get_memory_monitor()
        monitor2 = get_memory_monitor()

        assert isinstance(monitor1, MemoryMonitor)
        assert monitor1 is monitor2  # 应该是同一个实例

    def test_register_resource(self):
        """测试注册资源便利函数"""
        resource = {"data": "test"}

        # 清理现有资源
        cleanup_all_resources()

        register_resource("test_resource", resource)

        manager = get_resource_manager()
        assert manager.get_resource("test_resource") == resource

    def test_cleanup_all_resources(self):
        """测试清理所有资源便利函数"""
        resource1 = {"data": "test1"}
        resource2 = {"data": "test2"}
        register_resource("resource1", resource1)
        register_resource("resource2", resource2)

        cleanup_all_resources()

        manager = get_resource_manager()
        assert manager.get_resource("resource1") is None
        assert manager.get_resource("resource2") is None


class TestMemoryManagementLifecycle:
    """测试内存管理生命周期"""

    @patch("atexit.register")
    def test_initialize_memory_management(self, mock_atexit_register):
        """测试初始化内存管理"""
        monitor = Mock()
        with patch("src.core.memory_manager.get_memory_monitor", return_value=monitor):
            initialize_memory_management()

            monitor.start.assert_called_once()
            mock_atexit_register.assert_called_once()

    def test_shutdown_memory_management(self):
        """测试关闭内存管理"""
        monitor = Mock()
        manager = Mock()
        with patch("src.core.memory_manager.get_memory_monitor", return_value=monitor):
            with patch("src.core.memory_manager.get_resource_manager", return_value=manager):
                with patch("src.core.memory_manager.gc.collect") as mock_gc_collect:
                    shutdown_memory_management()

                    manager.cleanup_all.assert_called_once()
                    mock_gc_collect.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
