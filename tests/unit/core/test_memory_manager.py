#!/usr/bin/env python3
"""
内存管理模块单元测试 - 源代码覆盖率测试

测试MyStocks系统中完整的内存管理功能，包括监控、资源管理和泄漏检测
"""

import pytest
import sys
import os
import threading
from unittest.mock import Mock, patch
from datetime import datetime

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core.memory_manager import (
    MemoryStats,
    MemoryLimit,
    ResourceManager,
    MemoryMonitor,
    get_resource_manager,
    get_memory_monitor,
    initialize_memory_management,
    shutdown_memory_management,
    register_resource,
    unregister_resource,
    cleanup_all_resources,
    get_memory_stats,
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

    def test_memory_stats_empty_leak_candidates(self):
        """测试空泄漏候选者列表"""
        stats = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=50.0,
            system_memory_percent=60.0,
            active_objects=500,
            total_objects=600,
            leak_candidates=[],
        )

        assert stats.leak_candidates == []


class TestMemoryLimit:
    """测试内存限制管理器"""

    def test_memory_limit_initialization(self):
        """测试内存限制初始化"""
        limit = MemoryLimit(max_memory_mb=1024, warning_threshold=0.8)

        assert limit.max_memory_mb == 1024
        assert limit.warning_threshold == 0.8
        assert limit.warning_threshold_mb == 819.2  # 1024 * 0.8
        assert len(limit._monitors) == 0

    def test_memory_limit_default_values(self):
        """测试内存限制默认值"""
        limit = MemoryLimit()

        assert limit.max_memory_mb == 1024
        assert limit.warning_threshold == 0.8
        assert limit.warning_threshold_mb == 819.2

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
    def test_is_approaching_limit_false(self, mock_process):
        """测试接近内存限制 - 假"""
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 600  # 600MB
        mock_process.return_value = mock_process_instance

        limit = MemoryLimit(max_memory_mb=1024, warning_threshold=0.8)
        assert limit.is_approaching_limit() is False

    @patch("psutil.Process")
    def test_is_over_limit_true(self, mock_process):
        """测试超过内存限制 - 真"""
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = (
            1024 * 1024 * 1200
        )  # 1200MB
        mock_process.return_value = mock_process_instance

        limit = MemoryLimit(max_memory_mb=1024)
        assert limit.is_over_limit() is True

    @patch("psutil.Process")
    def test_is_over_limit_false(self, mock_process):
        """测试超过内存限制 - 假"""
        mock_process_instance = Mock()
        mock_process_instance.memory_info.return_value.rss = 1024 * 1024 * 800  # 800MB
        mock_process.return_value = mock_process_instance

        limit = MemoryLimit(max_memory_mb=1024)
        assert limit.is_over_limit() is False

    def test_register_monitor(self):
        """测试注册内存监控回调"""
        limit = MemoryLimit()
        callback1 = Mock()
        callback2 = Mock()

        limit.register_monitor(callback1)
        limit.register_monitor(callback2)

        assert len(limit._monitors) == 2
        assert callback1 in limit._monitors
        assert callback2 in limit._monitors

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

    def test_notify_monitors_with_exception(self):
        """测试通知监控器 - 有异常"""
        limit = MemoryLimit()
        callback1 = Mock()
        callback2 = Mock(side_effect=Exception("Test error"))
        callback3 = Mock()

        limit.register_monitor(callback1)
        limit.register_monitor(callback2)
        limit.register_monitor(callback3)

        # 不应该抛出异常
        limit.notify_monitors(512.0)

        callback1.assert_called_once_with(512.0)
        callback2.assert_called_once_with(512.0)
        callback3.assert_called_once_with(512.0)

    def test_notify_monitors_empty(self):
        """测试通知空监控器列表"""
        limit = MemoryLimit()
        # 不应该抛出异常
        limit.notify_monitors(512.0)


class TestResourceManager:
    """测试资源管理器"""

    def test_resource_manager_initialization(self):
        """测试资源管理器初始化"""
        manager = ResourceManager()

        assert len(manager._resources) == 0
        assert len(manager._weak_refs) == 0
        assert len(manager._cleanup_callbacks) == 0
        assert len(manager._memory_stats) == 0

    def test_register_resource_basic(self):
        """测试注册资源 - 基本功能"""
        manager = ResourceManager()
        resource = {"data": "test"}
        cleanup_callback = Mock()

        manager.register_resource("test_resource", resource, cleanup_callback)

        assert manager.get_resource("test_resource") == resource
        assert "test_resource" in manager._cleanup_callbacks

    def test_register_resource_replace_existing(self):
        """测试注册资源 - 替换已存在资源"""
        manager = ResourceManager()
        resource1 = {"data": "test1"}
        resource2 = {"data": "test2"}

        manager.register_resource("test_resource", resource1)
        manager.register_resource("test_resource", resource2)

        assert manager.get_resource("test_resource") == resource2

    def test_register_resource_with_weak_ref(self):
        """测试注册资源 - 使用弱引用"""
        manager = ResourceManager()
        resource = {"data": "test"}

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
        assert "test_resource" not in manager._cleanup_callbacks

    def test_unregister_nonexistent_resource(self):
        """测试注销不存在的资源"""
        manager = ResourceManager()
        # 不应该抛出异常
        manager.unregister_resource("nonexistent_resource")

    def test_cleanup_resource_with_callback(self):
        """测试清理资源 - 有回调函数"""
        manager = ResourceManager()
        cleanup_callback = Mock()

        manager._cleanup_callbacks["test_resource"] = cleanup_callback
        manager._cleanup_resource("test_resource")

        cleanup_callback.assert_called_once()
        assert "test_resource" not in manager._cleanup_callbacks

    def test_cleanup_resource_without_callback(self):
        """测试清理资源 - 无回调函数"""
        manager = ResourceManager()
        # 不应该抛出异常
        manager._cleanup_resource("test_resource")

    def test_cleanup_resource_callback_exception(self):
        """测试清理资源 - 回调函数异常"""
        manager = ResourceManager()
        cleanup_callback = Mock(side_effect=Exception("Cleanup failed"))

        manager._cleanup_callbacks["test_resource"] = cleanup_callback
        # 不应该抛出异常
        manager._cleanup_resource("test_resource")

        cleanup_callback.assert_called_once()

    def test_auto_cleanup(self):
        """测试自动清理"""
        manager = ResourceManager()
        manager.unregister_resource = Mock()

        manager._auto_cleanup("test_resource")

        manager.unregister_resource.assert_called_once_with("test_resource")

    def test_get_resource_existing(self):
        """测试获取资源 - 存在"""
        manager = ResourceManager()
        resource = {"data": "test"}

        manager._resources["test_resource"] = resource
        result = manager.get_resource("test_resource")

        assert result == resource

    def test_get_resource_nonexistent(self):
        """测试获取资源 - 不存在"""
        manager = ResourceManager()
        result = manager.get_resource("nonexistent_resource")

        assert result is None

    def test_cleanup_all(self):
        """测试清理所有资源"""
        manager = ResourceManager()
        resource1 = {"data": "test1"}
        resource2 = {"data": "test2"}
        cleanup_callback1 = Mock()
        cleanup_callback2 = Mock()

        manager.register_resource("resource1", resource1, cleanup_callback1)
        manager.register_resource("resource2", resource2, cleanup_callback2)

        manager.cleanup_all()

        assert len(manager._resources) == 0
        assert len(manager._cleanup_callbacks) == 0
        assert len(manager._weak_refs) == 0
        cleanup_callback1.assert_called_once()
        cleanup_callback2.assert_called_once()

    def test_cleanup_all_empty(self):
        """测试清理所有资源 - 空列表"""
        manager = ResourceManager()
        # 不应该抛出异常
        manager.cleanup_all()

    def test_get_stats(self):
        """测试获取资源统计信息"""
        manager = ResourceManager()
        resource1 = {"data": "test1"}
        resource2 = {"data": "test2"}
        cleanup_callback = Mock()

        manager.register_resource("resource1", resource1)
        manager.register_resource("resource2", resource2, cleanup_callback)
        manager.register_resource("resource3", None, weak_ref=True)

        stats = manager.get_stats()

        assert stats["total_resources"] == 3
        assert stats["total_cleanup_callbacks"] == 1
        assert stats["weak_refs"] == 1
        assert set(stats["resource_ids"]) == {"resource1", "resource2", "resource3"}

    def test_get_stats_empty(self):
        """测试获取资源统计信息 - 空资源"""
        manager = ResourceManager()
        stats = manager.get_stats()

        assert stats["total_resources"] == 0
        assert stats["total_cleanup_callbacks"] == 0
        assert stats["weak_refs"] == 0
        assert stats["resource_ids"] == []


class TestMemoryMonitor:
    """测试内存监控器"""

    def test_memory_monitor_initialization(self):
        """测试内存监控器初始化"""
        monitor = MemoryMonitor(check_interval=30, max_history=500)

        assert monitor.check_interval == 30
        assert monitor.max_history == 500
        assert monitor._running is False
        assert monitor._thread is None
        assert len(monitor._stats_history) == 0

    def test_memory_monitor_default_initialization(self):
        """测试内存监控器默认初始化"""
        monitor = MemoryMonitor()

        assert monitor.check_interval == 60
        assert monitor.max_history == 1000

    @patch("threading.Thread")
    def test_start_success(self, mock_thread):
        """测试启动内存监控 - 成功"""
        monitor = MemoryMonitor()
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance

        monitor.start()

        assert monitor._running is True
        mock_thread.assert_called_once_with(target=monitor._monitor_loop, daemon=True)
        mock_thread_instance.start.assert_called_once()

    def test_start_already_running(self):
        """测试启动内存监控 - 已在运行"""
        monitor = MemoryMonitor()
        monitor._running = True

        monitor.start()

        # 状态不应该改变
        assert monitor._running is True

    @patch("threading.Thread")
    def test_stop_success(self, mock_thread):
        """测试停止内存监控 - 成功"""
        monitor = MemoryMonitor()
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        monitor._thread = mock_thread_instance

        monitor.start()
        assert monitor._running is True

        monitor.stop()
        assert monitor._running is False
        mock_thread_instance.join.assert_called_once_with(timeout=5)

    def test_stop_not_running(self):
        """测试停止内存监控 - 未运行"""
        monitor = MemoryMonitor()
        monitor._running = False

        monitor.stop()
        # 不应该抛出异常
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
        with patch(
            "src.core.memory_manager.psutil.virtual_memory"
        ) as mock_virtual_memory:
            mock_virtual_memory.return_value.percent = 75.0

            monitor = MemoryMonitor()
            monitor._detect_leak_candidates = Mock(return_value=["TestType:100"])

            stats = monitor._collect_stats()

            assert stats.process_memory_mb == 512.0
            assert stats.system_memory_percent == 75.0
            assert stats.active_objects == 3  # 排除None
            assert stats.total_objects == 4
            assert stats.leak_candidates == ["TestType:100"]

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
        stats3 = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=300,
            system_memory_percent=70,
            active_objects=300,
            total_objects=320,
            leak_candidates=[],
        )
        stats4 = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=400,
            system_memory_percent=80,
            active_objects=400,
            total_objects=420,
            leak_candidates=[],
        )

        # 添加3个统计
        monitor._update_stats_history(stats1)
        monitor._update_stats_history(stats2)
        monitor._update_stats_history(stats3)

        assert len(monitor._stats_history) == 3

        # 添加第4个，应该移除第一个
        monitor._update_stats_history(stats4)

        assert len(monitor._stats_history) == 3
        assert monitor._stats_history[0] == stats2
        assert monitor._stats_history[1] == stats3
        assert monitor._stats_history[2] == stats4

    @patch("src.core.memory_manager.gc.get_objects")
    def test_detect_leak_candidates(self, mock_get_objects):
        """测试检测内存泄漏候选者"""

        # 创建模拟对象
        class TestClass:
            pass

        class OtherClass:
            pass

        obj1 = TestClass()
        obj2 = TestClass()
        obj3 = OtherClass()
        obj4 = TestClass()

        mock_get_objects.return_value = [
            obj1,
            obj2,
            obj3,
            obj4,
            None,
        ] * 300  # 超过1000个对象

        monitor = MemoryMonitor()
        candidates = monitor._detect_leak_candidates()

        # 应该包含数量超过1000的类型
        assert any("TestClass" in candidate for candidate in candidates)

    def test_detect_leak_candidates_below_threshold(self):
        """测试检测内存泄漏候选者 - 低于阈值"""
        with patch("src.core.memory_manager.gc.get_objects") as mock_get_objects:
            mock_get_objects.return_value = ["obj"] * 500  # 低于阈值

            monitor = MemoryMonitor()
            candidates = monitor._detect_leak_candidates()

            assert len(candidates) <= 5  # 最多返回5个

    @patch("src.core.memory_manager.gc.collect")
    def test_emergency_cleanup(self, mock_gc_collect):
        """测试紧急清理"""
        mock_gc_collect.return_value = 50

        # 模拟resource_manager
        with patch("src.core.memory_manager.get_resource_manager") as mock_get_manager:
            mock_manager = Mock()
            mock_get_manager.return_value = mock_manager

            monitor = MemoryMonitor()
            monitor._emergency_cleanup()

            mock_gc_collect.assert_called_once()
            mock_manager.cleanup_all.assert_called_once()

    def test_get_current_stats_with_history(self):
        """测试获取当前统计信息 - 有历史"""
        monitor = MemoryMonitor()
        stats = MemoryStats(
            timestamp=datetime.now(),
            process_memory_mb=100,
            system_memory_percent=50,
            active_objects=100,
            total_objects=120,
            leak_candidates=[],
        )
        monitor._stats_history = [stats]

        current = monitor.get_current_stats()

        assert current.process_memory_mb == 100
        assert current.system_memory_percent == 50
        assert current.active_objects == 100
        assert current.total_objects == 120

    def test_get_current_stats_empty_history(self):
        """测试获取当前统计信息 - 空历史"""
        monitor = MemoryMonitor()

        current = monitor.get_current_stats()

        assert current.process_memory_mb == 0
        assert current.system_memory_percent == 0
        assert current.active_objects == 0
        assert current.total_objects == 0
        assert current.leak_candidates == []

    def test_get_history(self):
        """测试获取历史统计"""
        monitor = MemoryMonitor()
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
        monitor._stats_history = [stats1, stats2]

        history = monitor.get_history()

        assert len(history) == 2
        assert history[0] == stats1
        assert history[1] == stats2

        # 确保返回的是副本
        history.append(stats1)
        assert len(monitor._stats_history) == 2


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
        cleanup_callback = Mock()

        # 清理现有资源
        cleanup_all_resources()

        register_resource("test_resource", resource, cleanup_callback)

        manager = get_resource_manager()
        assert manager.get_resource("test_resource") == resource

    def test_unregister_resource(self):
        """测试注销资源便利函数"""
        resource = {"data": "test"}
        register_resource("test_resource", resource)
        unregister_resource("test_resource")

        manager = get_resource_manager()
        assert manager.get_resource("test_resource") is None

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

    @patch("src.core.memory_manager._memory_monitor.get_current_stats")
    @patch("src.core.memory_manager._resource_manager.get_stats")
    @patch("src.core.memory_manager._memory_monitor.get_history")
    def test_get_memory_stats(
        self, mock_history, mock_resource_stats, mock_current_stats
    ):
        """测试获取内存统计信息"""
        # 模拟返回值
        mock_stats = MemoryStats(
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            process_memory_mb=100,
            system_memory_percent=50,
            active_objects=100,
            total_objects=120,
            leak_candidates=["TestType:100"],
        )
        mock_current_stats.return_value = mock_stats
        mock_history.return_value = [mock_stats]
        mock_resource_stats.return_value = {
            "total_resources": 5,
            "total_cleanup_callbacks": 2,
            "weak_refs": 1,
            "resource_ids": ["res1", "res2"],
        }

        stats = get_memory_stats()

        assert "current" in stats
        assert "resource_manager" in stats
        assert "history_length" in stats

        current = stats["current"]
        assert current["timestamp"] == "2025-01-01T12:00:00"
        assert current["process_memory_mb"] == 100
        assert current["system_memory_percent"] == 50
        assert current["active_objects"] == 100
        assert current["total_objects"] == 120
        assert current["leak_candidates"] == ["TestType:100"]

        assert stats["resource_manager"]["total_resources"] == 5
        assert stats["history_length"] == 1


class TestMemoryManagementLifecycle:
    """测试内存管理生命周期"""

    @patch("src.core.memory_manager.atexit.register")
    def test_initialize_memory_management(self, mock_atexit_register):
        """测试初始化内存管理"""
        monitor = Mock()
        with patch("src.core.memory_manager.get_memory_monitor", return_value=monitor):
            initialize_memory_management()

            monitor.start.assert_called_once()
            mock_atexit_register.assert_called_once_with(shutdown_memory_management)

    def test_shutdown_memory_management(self):
        """测试关闭内存管理"""
        monitor = Mock()
        manager = Mock()
        with patch("src.core.memory_manager.get_memory_monitor", return_value=monitor):
            with patch(
                "src.core.memory_manager.get_resource_manager", return_value=manager
            ):
                with patch("src.core.memory_manager.gc.collect") as mock_gc_collect:
                    shutdown_memory_management()

                    monitor.stop.assert_called_once()
                    manager.cleanup_all.assert_called_once()
                    mock_gc_collect.assert_called_once()


class TestThreadSafety:
    """测试线程安全"""

    def test_resource_manager_thread_safety(self):
        """测试资源管理器线程安全"""
        manager = ResourceManager()
        results = []
        errors = []

        def worker(worker_id):
            try:
                resource = {"worker_id": worker_id}
                resource_id = f"resource_{worker_id}"
                manager.register_resource(resource_id, resource)
                retrieved = manager.get_resource(resource_id)
                results.append((worker_id, retrieved))
                manager.unregister_resource(resource_id)
            except Exception as e:
                errors.append((worker_id, str(e)))

        # 创建多个线程
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        assert len(errors) == 0, f"线程安全错误: {errors}"
        assert len(results) == 5

        for worker_id, retrieved in results:
            assert retrieved["worker_id"] == worker_id

    def test_memory_limit_monitor_thread_safety(self):
        """测试内存限制监控器线程安全"""
        limit = MemoryLimit()
        results = []

        def callback(memory_mb):
            results.append(memory_mb)

        # 注册多个监控器
        for i in range(3):
            limit.register_monitor(callback)

        def worker(worker_id):
            limit.notify_monitors(100 + worker_id)

        # 创建多个线程同时通知
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 应该有15个结果（5个worker * 3个monitor）
        assert len(results) == 15


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
