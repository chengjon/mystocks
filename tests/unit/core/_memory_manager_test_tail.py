#!/usr/bin/env python3
"""Support tests extracted from `tests/unit/core/test_memory_manager.py`."""

import threading
from unittest.mock import Mock, patch

from src.core.memory_manager import (
    MemoryLimit,
    ResourceManager,
    get_memory_monitor,
    get_resource_manager,
    initialize_memory_management,
    shutdown_memory_management,
)


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
            with patch("src.core.memory_manager.get_resource_manager", return_value=manager):
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
            except Exception as error:
                errors.append((worker_id, str(error)))

        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

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

        for _ in range(3):
            limit.register_monitor(callback)

        def worker(worker_id):
            limit.notify_monitors(100 + worker_id)

        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 15
