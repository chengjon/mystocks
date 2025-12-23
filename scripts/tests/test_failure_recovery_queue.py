#!/usr/bin/env python3
"""
故障恢复队列测试套件
完整测试failure_recovery_queue模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import sys
import os
import tempfile
import shutil
import time
from pathlib import Path
from unittest.mock import patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
import sqlite3
import json

# 导入被测试的模块
from src.utils.failure_recovery_queue import FailureRecoveryQueue


class TestFailureRecoveryQueue:
    """故障恢复队列核心功能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        # 创建临时目录用于测试
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_queue.db")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        # 清理临时目录
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_initialization_with_default_path(self):
        """测试使用默认路径初始化"""
        with patch("os.makedirs") as mock_makedirs:
            # 创建实例
            queue = FailureRecoveryQueue()

            # 验证目录创建被调用
            mock_makedirs.assert_called_once()
            args, kwargs = mock_makedirs.call_args
            assert args[0] == "/tmp"  # 默认路径的目录部分
            assert kwargs["exist_ok"] is True

            # 验证属性设置
            assert queue.db_path == "/tmp/mystocks_recovery_queue.db"

    def test_initialization_with_custom_path(self):
        """测试使用自定义路径初始化"""
        import tempfile

        custom_path = tempfile.mktemp(suffix=".db")

        with patch("os.makedirs") as mock_makedirs:
            queue = FailureRecoveryQueue(custom_path)

            mock_makedirs.assert_called_once()
            assert queue.db_path == custom_path

    def test_initialization_creates_directory(self):
        """测试初始化时创建目录"""
        nested_path = os.path.join(self.temp_dir, "nested", "path", "test.db")

        # 确保目录不存在
        assert not os.path.exists(os.path.dirname(nested_path))

        # 初始化队列
        queue = FailureRecoveryQueue(nested_path)

        # 验证目录被创建
        assert os.path.exists(os.path.dirname(nested_path))
        assert queue.db_path == nested_path

    def test_database_initialization(self):
        """测试数据库初始化"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 验证数据库文件被创建
        assert os.path.exists(self.test_db_path)

        # 验证表结构（排除SQLite系统表）
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
        tables = cursor.fetchall()
        conn.close()

        assert len(tables) == 1
        assert tables[0][0] == "outbox_queue"

    def test_table_structure(self):
        """测试表结构正确性"""
        queue = FailureRecoveryQueue(self.test_db_path)

        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()

        cursor.execute("PRAGMA table_info(outbox_queue)")
        columns = cursor.fetchall()
        conn.close()

        # 验证列存在和类型（基于实际PRAGMA输出格式）
        expected_columns = {
            "id": (
                "INTEGER",
                0,
                None,
                1,
            ),  # cid=0, name=id, type=INTEGER, notnull=0, dflt_value=None, pk=1
            "classification": (
                "TEXT",
                1,
                None,
                0,
            ),  # cid=1, name=classification, type=TEXT, notnull=1, dflt_value=None, pk=0
            "target_database": (
                "TEXT",
                1,
                None,
                0,
            ),  # cid=2, name=target_database, type=TEXT, notnull=1, dflt_value=None, pk=0
            "data_json": (
                "TEXT",
                1,
                None,
                0,
            ),  # cid=3, name=data_json, type=TEXT, notnull=1, dflt_value=None, pk=0
            "created_at": (
                "TIMESTAMP",
                0,
                "CURRENT_TIMESTAMP",
                0,
            ),  # cid=4, 默认值是字符串'CURRENT_TIMESTAMP'
            "retry_count": ("INTEGER", 0, "0", 0),  # cid=5, 默认值是字符串'0'
            "status": ("TEXT", 0, "'pending'", 0),  # cid=6, 默认值是字符串"'pending'"
        }

        assert len(columns) == len(expected_columns)

        for col in columns:
            cid, col_name, col_type, notnull, dflt_value, pk = col
            assert col_name in expected_columns
            expected_type, expected_notnull, expected_default, expected_pk = (
                expected_columns[col_name]
            )
            assert col_type == expected_type  # 数据类型
            assert notnull == expected_notnull  # 是否非空
            assert dflt_value == expected_default  # 默认值
            assert pk == expected_pk  # 是否主键

    def test_enqueue_basic(self):
        """测试基本入队操作"""
        queue = FailureRecoveryQueue(self.test_db_path)

        test_data = {"symbol": "000001", "price": 10.5, "volume": 1000}
        queue.enqueue("test_classification", "test_db", test_data)

        # 验证数据被插入
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM outbox_queue")
        rows = cursor.fetchall()
        conn.close()

        assert len(rows) == 1
        row = rows[0]
        assert row[1] == "test_classification"  # classification
        assert row[2] == "test_db"  # target_database
        assert json.loads(row[3]) == test_data  # data_json
        assert row[5] == 0  # retry_count
        assert row[6] == "pending"  # status

    def test_enqueue_multiple_items(self):
        """测试多个项目入队"""
        queue = FailureRecoveryQueue(self.test_db_path)

        items = [
            {"symbol": "000001", "price": 10.5},
            {"symbol": "000002", "price": 20.3},
            {"symbol": "600000", "price": 15.7},
        ]

        for i, item in enumerate(items):
            queue.enqueue(f"classification_{i}", f"db_{i}", item)

        # 验证所有数据被插入
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM outbox_queue")
        count = cursor.fetchone()[0]
        conn.close()

        assert count == len(items)

    def test_enqueue_with_complex_data(self):
        """测试复杂数据结构的入队"""
        queue = FailureRecoveryQueue(self.test_db_path)

        complex_data = {
            "symbol": "000001",
            "price": 10.5,
            "metadata": {
                "source": "test",
                "timestamp": "2024-01-01T12:00:00",
                "tags": ["stock", "test"],
            },
            "nested": {"level1": {"level2": "deep_value"}},
            "array_data": [1, 2, 3, {"key": "value"}],
        }

        queue.enqueue("complex", "production", complex_data)

        # 验证复杂数据被正确序列化和存储
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM outbox_queue")
        stored_json = cursor.fetchone()[0]
        conn.close()

        # 验证JSON序列化和反序列化
        loaded_data = json.loads(stored_json)
        assert loaded_data == complex_data

    def test_get_pending_items_default_limit(self):
        """测试获取待处理项目（默认限制）"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加一些测试数据
        for i in range(5):
            queue.enqueue(f"class_{i}", f"db_{i}", {"id": i})

        # 获取待处理项目
        items = queue.get_pending_items()

        assert len(items) == 5
        for i, item in enumerate(items):
            assert item[0] == i + 1  # id
            assert item[1] == f"class_{i}"
            assert item[2] == f"db_{i}"
            assert json.loads(item[3])["id"] == i

    def test_get_pending_items_with_limit(self):
        """测试获取待处理项目（指定限制）"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加测试数据
        for i in range(10):
            queue.enqueue(f"class_{i}", f"db_{i}", {"id": i})

        # 获取限制数量的项目
        items = queue.get_pending_items(limit=3)

        assert len(items) == 3
        # 验证按时间排序（ASC）
        for i, item in enumerate(items):
            assert json.loads(item[3])["id"] == i

    def test_get_pending_items_empty_queue(self):
        """测试从空队列获取项目"""
        queue = FailureRecoveryQueue(self.test_db_path)

        items = queue.get_pending_items()

        assert items == []

    def test_get_pending_items_filtering(self):
        """测试获取待处理项目的过滤"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加一些项目
        queue.enqueue("pending", "db1", {"id": 1})

        # 手动插入一个已完成的项目来测试过滤
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO outbox_queue (classification, target_database, data_json, status) VALUES (?, ?, ?, ?)",
            ("completed", "db2", json.dumps({"id": 2}), "completed"),
        )
        conn.commit()
        conn.close()

        # 获取待处理项目应该只返回pending状态的项目
        items = queue.get_pending_items()

        assert len(items) == 1
        assert items[0][1] == "pending"


class TestErrorHandling:
    """错误处理测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_queue.db")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_database_connection_failure(self):
        """测试数据库连接失败"""
        # 模拟sqlite3.connect抛出异常的情况
        with patch(
            "sqlite3.connect",
            side_effect=sqlite3.OperationalError("unable to open database file"),
        ):
            # 创建队列应该因为连接失败而抛出异常
            with pytest.raises(sqlite3.OperationalError):
                FailureRecoveryQueue(self.test_db_path)

    def test_enqueue_invalid_data_type(self):
        """测试入队无效数据类型"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 尝试入队不可序列化的数据
        invalid_data = {
            "function": lambda x: x,  # 函数对象无法JSON序列化
            "binary": b"bytes",  # 二进制数据
        }

        # 这应该因为JSON序列化失败而抛出异常
        with pytest.raises(TypeError):
            queue.enqueue("test", "test_db", invalid_data)

    def test_get_pending_items_database_error(self):
        """测试获取项目时数据库错误"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 删除数据库文件来模拟数据库错误
        os.remove(self.test_db_path)

        # 这应该抛出数据库错误
        with pytest.raises(sqlite3.OperationalError):
            queue.get_pending_items()


class TestEdgeCases:
    """边界情况测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_queue.db")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_enqueue_empty_data(self):
        """测试入队空数据"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 测试空字典
        queue.enqueue("empty", "test_db", {})

        # 验证空数据被正确存储
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM outbox_queue")
        stored_json = cursor.fetchone()[0]
        conn.close()

        assert json.loads(stored_json) == {}

    def test_enqueue_large_data(self):
        """测试入队大量数据"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 创建大量数据
        large_data = {
            "large_array": list(range(1000)),
            "large_string": "x" * 10000,
            "nested": {},
        }

        # 嵌套结构
        for i in range(100):
            large_data["nested"][f"key_{i}"] = f"value_{i}" * 100

        # 这应该能正常处理
        queue.enqueue("large", "test_db", large_data)

        # 验证数据被正确存储
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT data_json FROM outbox_queue")
        stored_json = cursor.fetchone()[0]
        conn.close()

        loaded_data = json.loads(stored_json)
        assert len(loaded_data["large_array"]) == 1000
        assert len(loaded_data["large_string"]) == 10000
        assert len(loaded_data["nested"]) == 100

    def test_get_pending_items_zero_limit(self):
        """测试获取零个待处理项目"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加一些数据
        queue.enqueue("test", "test_db", {"id": 1})

        # 获取零个项目
        items = queue.get_pending_items(limit=0)

        assert items == []

    def test_get_pending_items_negative_limit(self):
        """测试获取负数个待处理项目"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加一些数据
        queue.enqueue("test", "test_db", {"id": 1})

        # SQLite中LIMIT -1意味着返回所有行，而不是空列表
        items = queue.get_pending_items(limit=-1)

        # 应该返回所有项目（SQLite中LIMIT -1 = 无限制）
        assert len(items) == 1
        assert items[0][1] == "test"  # classification
        assert items[0][2] == "test_db"  # target_database

    def test_concurrent_operations(self):
        """测试并发操作"""
        import threading

        queue = FailureRecoveryQueue(self.test_db_path)
        results = []
        errors = []

        def producer():
            try:
                for i in range(10):
                    queue.enqueue(f"producer_{i}", "test_db", {"id": i})
                    results.append(f"producer_{i}")
            except Exception as e:
                errors.append(f"Producer error: {e}")

        def consumer():
            try:
                time.sleep(0.1)  # 等待生产者产生一些数据
                items = queue.get_pending_items(limit=50)
                results.append(f"consumer_got_{len(items)}")
            except Exception as e:
                errors.append(f"Consumer error: {e}")

        # 创建并启动线程
        producer_thread = threading.Thread(target=producer)
        consumer_thread = threading.Thread(target=consumer)

        producer_thread.start()
        consumer_thread.start()

        # 等待线程完成
        producer_thread.join()
        consumer_thread.join()

        # 验证没有错误发生
        assert len(errors) == 0
        assert "producer_9" in results

    def test_unicode_handling(self):
        """测试Unicode字符处理"""
        queue = FailureRecoveryQueue(self.test_db_path)

        unicode_data = {
            "chinese": "测试中文数据",
            "emoji": "🚀🌟💎",
            "special": "Café résumé naïve",
            "math": "∑∏∫∆∇∂",
        }

        queue.enqueue("unicode", "test_db", unicode_data)

        # 验证Unicode数据被正确存储和检索
        items = queue.get_pending_items()
        assert len(items) == 1

        stored_data = json.loads(items[0][3])
        assert stored_data == unicode_data


class TestPerformance:
    """性能测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_queue.db")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_enqueue_performance(self):
        """测试入队性能"""
        queue = FailureRecoveryQueue(self.test_db_path)

        iterations = 1000
        test_data = {"symbol": "TEST", "data": "x" * 100}

        start_time = time.time()
        for i in range(iterations):
            queue.enqueue(f"perf_test_{i}", "test_db", test_data)
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000  # 毫秒

        # 每次入队操作应该在合理时间内完成（小于10毫秒）
        assert avg_time < 10, f"入队操作平均耗时 {avg_time:.2f} 毫秒，超过预期"

        # 验证所有数据都被正确存储
        items = queue.get_pending_items(limit=iterations * 2)
        assert len(items) == iterations

    def test_get_pending_items_performance(self):
        """测试获取待处理项目性能"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 先添加大量数据
        for i in range(1000):
            queue.enqueue(f"perf_{i}", "test_db", {"id": i})

        iterations = 100

        start_time = time.time()
        for _ in range(iterations):
            items = queue.get_pending_items(limit=100)
        end_time = time.time()

        avg_time = (end_time - start_time) / iterations * 1000  # 毫秒

        # 获取操作应该很快（小于5毫秒）
        assert avg_time < 5, f"获取操作平均耗时 {avg_time:.2f} 毫秒，超过预期"

    def test_database_size_impact(self):
        """测试数据库大小对性能的影响"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加不同大小的数据
        small_data = {"small": "test"}
        medium_data = {"medium": "x" * 1000}
        large_data = {"large": "x" * 10000}

        data_sizes = [small_data, medium_data, large_data]

        for data in data_sizes:
            start_time = time.time()

            # 添加100个这种大小的数据
            for i in range(100):
                queue.enqueue("size_test", "test_db", data)

            end_time = time.time()

            # 测量获取性能
            get_start = time.time()
            items = queue.get_pending_items(limit=200)
            get_end = time.time()

            enqueue_time = (end_time - start_time) * 1000
            get_time = (get_end - get_start) * 1000

            # 验证性能在可接受范围内
            assert enqueue_time < 1000, (
                f"数据大小 {len(str(data))} 入队耗时 {enqueue_time:.2f} 毫秒"
            )
            assert get_time < 50, (
                f"数据大小 {len(str(data))} 获取耗时 {get_time:.2f} 毫秒"
            )


class TestIntegration:
    """集成测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test_queue.db")

    def teardown_method(self):
        """每个测试方法执行后的清理"""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_full_workflow(self):
        """测试完整工作流程"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 1. 模拟数据库故障时的数据入队
        failed_operations = [
            {
                "classification": "stock_data",
                "target": "postgresql",
                "data": {"symbol": "000001", "price": 10.5},
            },
            {
                "classification": "stock_data",
                "target": "postgresql",
                "data": {"symbol": "000002", "price": 20.3},
            },
            {
                "classification": "market_data",
                "target": "tdengine",
                "data": {"symbol": "600000", "volume": 1000},
            },
            {
                "classification": "user_data",
                "target": "postgresql",
                "data": {"user_id": 1, "action": "buy"},
            },
        ]

        # 2. 入队所有失败的操作
        for op in failed_operations:
            queue.enqueue(op["classification"], op["target"], op["data"])

        # 3. 模拟数据库恢复后获取待处理项目
        pending_items = queue.get_pending_items(limit=50)

        # 4. 验证数据完整性
        assert len(pending_items) == len(failed_operations)

        # 5. 模拟处理每个项目
        for i, item in enumerate(pending_items):
            classification, target_db, data_json = item[1], item[2], json.loads(item[3])

            # 验证数据匹配
            original_op = failed_operations[i]
            assert classification == original_op["classification"]
            assert target_db == original_op["target"]
            assert data_json == original_op["data"]

    def test_data_persistence_across_instances(self):
        """测试跨实例的数据持久性"""
        # 第一个实例入队数据
        queue1 = FailureRecoveryQueue(self.test_db_path)
        test_data = {"persistent": True, "timestamp": "2024-01-01"}
        queue1.enqueue("persistence_test", "test_db", test_data)

        # 第二个实例应该能访问相同的数据
        queue2 = FailureRecoveryQueue(self.test_db_path)
        items = queue2.get_pending_items()

        assert len(items) == 1
        stored_data = json.loads(items[0][3])
        assert stored_data == test_data

    def test_multiple_queues_isolation(self):
        """测试多个队列之间的隔离"""
        # 创建两个不同的队列
        queue1_path = os.path.join(self.temp_dir, "queue1.db")
        queue2_path = os.path.join(self.temp_dir, "queue2.db")

        queue1 = FailureRecoveryQueue(queue1_path)
        queue2 = FailureRecoveryQueue(queue2_path)

        # 在不同队列中添加数据
        queue1.enqueue("queue1", "db1", {"source": "first"})
        queue2.enqueue("queue2", "db2", {"source": "second"})

        # 验证隔离性
        items1 = queue1.get_pending_items()
        items2 = queue2.get_pending_items()

        assert len(items1) == 1
        assert len(items2) == 1
        assert json.loads(items1[0][3])["source"] == "first"
        assert json.loads(items2[0][3])["source"] == "second"

    def test_realistic_failure_recovery_scenario(self):
        """测试真实的故障恢复场景"""
        queue = FailureRecoveryQueue(self.test_db_path)

        # 模拟高频交易时的故障
        trade_operations = []

        # 生成1000个交易操作
        for i in range(100):
            trade = {
                "classification": "trade_execution",
                "target_database": "postgresql",
                "data": {
                    "order_id": f"ORDER_{i}_{int(time.time() * 1000)}",
                    "symbol": f"00000{i % 10}",
                    "price": 10.0 + (i % 100) * 0.01,
                    "quantity": 100 + i,
                    "timestamp": time.time(),
                    "side": "buy" if i % 2 == 0 else "sell",
                },
            }
            trade_operations.append(trade)

        # 系统故障时批量入队
        enqueue_start = time.time()
        for trade in trade_operations:
            queue.enqueue(
                trade["classification"], trade["target_database"], trade["data"]
            )
        enqueue_time = time.time() - enqueue_start

        # 模拟系统恢复后批量处理
        recovery_start = time.time()
        batch_size = 50
        processed_count = 0

        while processed_count < len(trade_operations):
            batch = queue.get_pending_items(limit=batch_size)
            if not batch:
                break

            # 模拟处理每个交易
            for item in batch:
                trade_data = json.loads(item[3])
                # 这里会包含实际的业务逻辑处理
                processed_count += 1

            # 模拟处理延迟
            time.sleep(0.001)  # 1ms

        recovery_time = time.time() - recovery_start

        # 验证性能指标
        assert enqueue_time < 10.0, f"入队1000个操作耗时 {enqueue_time:.2f}秒"
        assert recovery_time < 5.0, f"恢复处理耗时 {recovery_time:.2f}秒"
        assert processed_count == len(trade_operations)

    def test_database_schema_migration(self):
        """测试数据库模式迁移场景"""
        # 创建初始队列
        queue = FailureRecoveryQueue(self.test_db_path)

        # 添加一些数据
        queue.enqueue("migration_test", "db", {"version": 1})

        # 验证初始表结构
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(outbox_queue)")
        original_columns = [col[1] for col in cursor.fetchall()]
        conn.close()

        # 模拟添加新列（实际应用中可能需要修改代码）
        conn = sqlite3.connect(self.test_db_path)
        cursor = conn.cursor()
        cursor.execute("ALTER TABLE outbox_queue ADD COLUMN processed_at TIMESTAMP")
        conn.commit()
        conn.close()

        # 创建新实例应该仍能工作
        queue2 = FailureRecoveryQueue(self.test_db_path)

        # 验证数据仍然可访问
        items = queue2.get_pending_items()
        assert len(items) == 1
        assert json.loads(items[0][3])["version"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
