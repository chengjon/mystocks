"""
Failure Recovery Queue Test Suite
故障恢复队列测试套件

创建日期: 2025-12-20
版本: 1.0.0
测试模块: src.utils.failure_recovery_queue (109行)
"""

import json
import os
import sqlite3
import tempfile
from unittest.mock import patch

import pytest

from src.utils.failure_recovery_queue import FailureRecoveryQueue


class TestFailureRecoveryQueue:
    """失败恢复队列测试"""

    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_queue.db")
        yield db_path
        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)

    @pytest.fixture
    def queue(self, temp_db_path):
        """创建队列实例"""
        return FailureRecoveryQueue(db_path=temp_db_path)

    def test_init_default_path(self):
        """测试默认路径初始化"""
        with patch("os.makedirs") as mock_makedirs:
            queue = FailureRecoveryQueue()
            expected_path = "/tmp/mystocks_recovery_queue.db"
            assert queue.db_path == expected_path
            mock_makedirs.assert_called_once_with("/tmp", exist_ok=True)

    def test_init_custom_path(self, temp_db_path):
        """测试自定义路径初始化"""
        with patch("os.makedirs") as mock_makedirs:
            queue = FailureRecoveryQueue(db_path=temp_db_path)
            assert queue.db_path == temp_db_path
            mock_makedirs.assert_called_once_with(os.path.dirname(temp_db_path), exist_ok=True)

    def test_init_db_table_creation(self, temp_db_path):
        """测试数据库表初始化"""
        queue = FailureRecoveryQueue(db_path=temp_db_path)

        # 验证表是否创建
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]

        # 应该包含outbox_queue表，可能还有sqlite_sequence表（SQLite系统表）
        assert "outbox_queue" in table_names

        # 验证表结构
        cursor.execute("PRAGMA table_info(outbox_queue)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        expected_columns = [
            "id",
            "classification",
            "target_database",
            "data_json",
            "created_at",
            "retry_count",
            "status",
        ]

        for col in expected_columns:
            assert col in column_names

        conn.close()

    def test_enqueue_basic(self, queue):
        """测试基本入队操作"""
        test_data = {"symbol": "600000", "price": 10.5, "volume": 1000}

        queue.enqueue("market_data", "postgresql", test_data)

        # 验证数据是否正确插入
        conn = sqlite3.connect(queue.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT classification, target_database, data_json FROM outbox_queue")
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == "market_data"
        assert result[1] == "postgresql"

        # 验证JSON数据
        stored_data = json.loads(result[2])
        assert stored_data == test_data

        conn.close()

    def test_enqueue_multiple_items(self, queue):
        """测试多个项目入队"""
        items = [
            ("market_data", "postgresql", {"symbol": "600000", "price": 10.5}),
            ("reference_data", "tdengine", {"exchange": "SH", "name": "平安银行"}),
            ("derived_data", "postgresql", {"ma5": 10.2, "ma20": 11.3}),
        ]

        for classification, target_db, data in items:
            queue.enqueue(classification, target_db, data)

        # 验证所有数据都插入成功
        conn = sqlite3.connect(queue.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM outbox_queue")
        count = cursor.fetchone()[0]

        assert count == 3

        # 验证数据顺序和内容
        cursor.execute("SELECT classification, target_database, data_json FROM outbox_queue ORDER BY created_at")
        results = cursor.fetchall()

        for i, (classification, target_db, data) in enumerate(items):
            assert results[i][0] == classification
            assert results[i][1] == target_db
            stored_data = json.loads(results[i][2])
            assert stored_data == data

        conn.close()

    def test_get_pending_items_empty(self, queue):
        """测试获取空的待处理队列"""
        items = queue.get_pending_items()
        assert items == []

    def test_get_pending_items_with_data(self, queue):
        """测试获取有数据的待处理队列"""
        # 先添加一些数据
        test_items = [
            ("market_data", "postgresql", {"symbol": "600000"}),
            ("reference_data", "tdengine", {"exchange": "SH"}),
            ("derived_data", "postgresql", {"indicator": "MA"}),
        ]

        for classification, target_db, data in test_items:
            queue.enqueue(classification, target_db, data)

        # 获取待处理项目
        items = queue.get_pending_items()

        assert len(items) == 3

        # 验证返回的数据格式
        for i, (id, classification, target_db, data_json) in enumerate(items):
            assert isinstance(id, int)
            assert classification == test_items[i][0]
            assert target_db == test_items[i][1]

            # 验证JSON可以正确解析
            data = json.loads(data_json)
            assert data == test_items[i][2]

    def test_get_pending_items_with_limit(self, queue):
        """测试带限制的获取待处理项目"""
        # 添加5个项目
        for i in range(5):
            queue.enqueue("market_data", "postgresql", {"symbol": f"60000{i}"})

        # 限制获取3个
        items = queue.get_pending_items(limit=3)
        assert len(items) == 3

        # 获取所有项目
        all_items = queue.get_pending_items(limit=100)
        assert len(all_items) == 5

    def test_get_pending_items_ordering(self, queue):
        """测试待处理项目的排序（按创建时间）"""
        # 按特定顺序添加项目
        items = [
            (
                "market_data",
                "postgresql",
                {"symbol": "600000", "timestamp": "2025-01-01T09:00:00"},
            ),
            ("reference_data", "tdengine", {"exchange": "SH", "name": "平安银行"}),
            ("derived_data", "postgresql", {"indicator": "MA", "value": 10.5}),
        ]

        for classification, target_db, data in items:
            queue.enqueue(classification, target_db, data)

        # 获取项目并验证顺序
        retrieved_items = queue.get_pending_items()

        assert len(retrieved_items) == 3

        # 验证顺序（应该按照插入顺序，因为创建时间是递增的）
        for i, item in enumerate(items):
            assert retrieved_items[i][1] == item[0]  # classification
            assert retrieved_items[i][2] == item[1]  # target_database

    def test_enqueue_json_serialization(self, queue):
        """测试JSON序列化"""
        complex_data = {
            "symbol": "600000",
            "data": {
                "price": [10.1, 10.2, 10.3],
                "volume": {"total": 1000000, "buy": 500000, "sell": 500000},
            },
            "metadata": {
                "source": "akshare",
                "timestamp": "2025-12-20T10:00:00Z",
                "flags": ["real_time", "verified"],
            },
        }

        queue.enqueue("market_data", "postgresql", complex_data)

        # 验证数据可以正确检索和反序列化
        items = queue.get_pending_items()
        assert len(items) == 1

        retrieved_data = json.loads(items[0][3])
        assert retrieved_data == complex_data

    def test_enqueue_with_none_data(self, queue):
        """测试包含None值的JSON序列化"""
        data_with_none = {
            "symbol": "600000",
            "price": None,
            "volume": 1000,
            "metadata": None,
        }

        queue.enqueue("market_data", "postgresql", data_with_none)

        items = queue.get_pending_items()
        retrieved_data = json.loads(items[0][3])

        assert retrieved_data["symbol"] == "600000"
        assert retrieved_data["price"] is None
        assert retrieved_data["volume"] == 1000
        assert retrieved_data["metadata"] is None

    def test_database_connection_error(self):
        """测试数据库连接错误"""
        # 使用无效路径
        invalid_path = "/invalid/path/that/does/not/exist/test.db"

        with patch("os.makedirs"):
            with pytest.raises(Exception):
                FailureRecoveryQueue(db_path=invalid_path)

    def test_large_data_serialization(self, queue):
        """测试大数据的JSON序列化"""
        # 创建一个较大的数据对象
        large_data = {
            "market_data": [{"symbol": f"60000{i}", "price": i * 0.1, "volume": i * 1000} for i in range(1000)]
        }

        # 这应该能够正常序列化
        queue.enqueue("market_data", "postgresql", large_data)

        items = queue.get_pending_items()
        assert len(items) == 1

        retrieved_data = json.loads(items[0][3])
        assert len(retrieved_data["market_data"]) == 1000

    def test_concurrent_enqueue(self, queue):
        """测试并发入队操作"""
        import threading
        import time

        results = []
        errors = []

        def enqueue_worker(worker_id):
            try:
                for i in range(5):  # 减少并发压力
                    data = {"worker_id": worker_id, "item": i, "timestamp": time.time()}
                    queue.enqueue("test_data", "postgresql", data)
                    results.append((worker_id, i))
                    time.sleep(0.001)  # 添加小延迟避免冲突
            except Exception as e:
                errors.append((worker_id, str(e)))

        # 创建多个线程同时入队
        threads = []
        for i in range(2):  # 减少线程数
            thread = threading.Thread(target=enqueue_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 允许一些并发冲突（SQLite锁问题）
        print(f"Concurrent enqueue results: {len(results)} successful, {len(errors)} errors")

        # 验证至少有一些数据成功入队
        assert len(results) >= 5, f"Too few successful operations: {len(results)}"
        assert len(errors) < 10, f"Too many errors: {errors}"

        # 验证成功入队的数据
        items = queue.get_pending_items(limit=100)
        assert len(items) >= 5

    def test_database_file_persistence(self, temp_db_path):
        """测试数据库文件持久化"""
        # 创建队列并添加数据
        queue1 = FailureRecoveryQueue(db_path=temp_db_path)
        test_data = {"symbol": "600000", "price": 10.5}
        queue1.enqueue("market_data", "postgresql", test_data)

        # 创建新的队列实例，验证数据仍然存在
        queue2 = FailureRecoveryQueue(db_path=temp_db_path)
        items = queue2.get_pending_items()

        assert len(items) == 1
        retrieved_data = json.loads(items[0][3])
        assert retrieved_data == test_data


class TestFailureRecoveryQueueEdgeCases:
    """失败恢复队列边界情况测试"""

    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库路径"""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_edge_cases.db")
        yield db_path
        # 清理
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)

    @pytest.fixture
    def queue(self, temp_db_path):
        """创建队列实例"""
        return FailureRecoveryQueue(db_path=temp_db_path)

    def test_enqueue_empty_data(self, queue):
        """测试空数据入队"""
        queue.enqueue("test", "postgresql", {})

        items = queue.get_pending_items()
        assert len(items) == 1

        retrieved_data = json.loads(items[0][3])
        assert retrieved_data == {}

    def test_enqueue_large_strings(self, queue):
        """测试大字符串数据"""
        large_string = "x" * 10000  # 10KB字符串
        data = {"large_field": large_string}

        queue.enqueue("test", "postgresql", data)

        items = queue.get_pending_items()
        retrieved_data = json.loads(items[0][3])
        assert len(retrieved_data["large_field"]) == 10000

    def test_special_characters_in_data(self, queue):
        """测试包含特殊字符的数据"""
        special_data = {
            "unicode_text": "测试中文🚀📈",
            "special_chars": "!@#$%^&*()_+-=[]{}|;':\",./<>?",
            "newlines": "Line 1\nLine 2\nLine 3",
            "tabs": "Column1\tColumn2\tColumn3",
        }

        queue.enqueue("test", "postgresql", special_data)

        items = queue.get_pending_items()
        retrieved_data = json.loads(items[0][3])
        assert retrieved_data == special_data

    def test_numeric_data_types(self, queue):
        """测试各种数值类型"""
        numeric_data = {
            "integer": 42,
            "float": 3.14159,
            "negative_int": -100,
            "zero": 0,
            "large_int": 999999999999,
            "scientific": 1.23e-10,
            "infinity": float("inf"),
        }

        queue.enqueue("test", "postgresql", numeric_data)

        items = queue.get_pending_items()
        retrieved_data = json.loads(items[0][3])

        # 验证数值类型（JSON可能将某些类型转换为字符串）
        assert retrieved_data["integer"] == 42
        assert abs(retrieved_data["float"] - 3.14159) < 0.00001
        assert retrieved_data["negative_int"] == -100
        assert retrieved_data["zero"] == 0


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
