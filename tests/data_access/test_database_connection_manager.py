"""
DatabaseConnectionManager测试

测试DatabaseConnectionManager类的所有功能：
- 环境变量验证
- TDengine连接管理
- PostgreSQL连接池管理
- Redis连接管理（已弃用但保留）
- 连接关闭和清理
- 单例模式

创建日期: 2026-01-03
Phase: 2 - Task 2.1.3
"""

import os
import unittest
from unittest.mock import Mock, patch

from src.storage.database.connection_manager import DatabaseConnectionManager, get_connection_manager


class TestDatabaseConnectionManagerInit(unittest.TestCase):
    """测试DatabaseConnectionManager初始化"""

    def setUp(self):
        """测试前准备"""
        # 保存原始环境变量
        self.original_env = dict(os.environ)

    def tearDown(self):
        """测试后清理"""
        # 恢复原始环境变量
        os.environ.clear()
        os.environ.update(self.original_env)

    def test_init_with_all_env_vars(self):
        """测试所有必需环境变量存在时初始化成功"""
        # 设置所有必需的环境变量
        required_vars = {
            "TDENGINE_HOST": "localhost",
            "TDENGINE_PORT": "6030",
            "TDENGINE_USER": "root",
            "TDENGINE_PASSWORD": "taosdata",  # pragma: allowlist secret
            "TDENGINE_DATABASE": "market_data",
            "POSTGRESQL_HOST": "localhost",
            "POSTGRESQL_PORT": "5438",
            "POSTGRESQL_USER": "postgres",
            "POSTGRESQL_PASSWORD": "password",  # pragma: allowlist secret
            "POSTGRESQL_DATABASE": "mystocks",
        }
        os.environ.update(required_vars)

        manager = DatabaseConnectionManager()

        self.assertIsNotNone(manager)
        self.assertEqual(manager._connections, {})

    def test_init_missing_tdengine_vars(self):
        """测试缺少TDengine环境变量时抛出异常"""
        # 只设置PostgreSQL变量
        os.environ.update(
            {
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",  # pragma: allowlist secret
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )

        with self.assertRaises(EnvironmentError) as context:
            DatabaseConnectionManager()

        self.assertIn("缺少必需的环境变量", str(context.exception))
        self.assertIn("TDENGINE_HOST", str(context.exception))

    def test_init_missing_postgresql_vars(self):
        """测试缺少PostgreSQL环境变量时抛出异常"""
        # 只设置TDengine变量
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
            }
        )

        with self.assertRaises(EnvironmentError) as context:
            DatabaseConnectionManager()

        self.assertIn("缺少必需的环境变量", str(context.exception))
        self.assertIn("POSTGRESQL_HOST", str(context.exception))


class TestDatabaseConnectionManagerTDengine(unittest.TestCase):
    """测试TDengine连接管理"""

    def setUp(self):
        """测试前准备"""
        # 设置所有必需的环境变量
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )
        self.manager = DatabaseConnectionManager()

    @patch("taosws.connect")
    def test_get_tdengine_connection_first_time(self, mock_connect):
        """测试首次获取TDengine连接"""
        mock_conn = Mock()
        mock_taosws.connect.return_value = mock_conn

        result = self.manager.get_tdengine_connection()

        self.assertEqual(result, mock_conn)
        mock_taosws.connect.assert_called_once_with(
            host="localhost",
            port=6030,
            user="root",
            password="taosdata",
            database="market_data",
        )
        self.assertIn("tdengine", self.manager._connections)

    @patch("src.storage.database.connection_manager.taosws")
    def test_get_tdengine_connection_cached(self, mock_taosws):
        """测试从缓存获取TDengine连接"""
        mock_conn = Mock()
        mock_taosws.connect.return_value = mock_conn

        # 第一次调用
        result1 = self.manager.get_tdengine_connection()
        # 第二次调用
        result2 = self.manager.get_tdengine_connection()

        self.assertEqual(result1, result2)
        self.assertEqual(result1, mock_conn)
        # 验证只创建了一次连接
        mock_taosws.connect.assert_called_once()

    @patch("src.storage.database.connection_manager.taosws")
    def test_get_tdengine_connection_with_rest_port(self, mock_taosws):
        """测试使用REST端口获取TDengine连接"""
        os.environ["TDENGINE_REST_PORT"] = "6041"
        mock_conn = Mock()
        mock_taosws.connect.return_value = mock_conn

        result = self.manager.get_tdengine_connection()

        mock_taosws.connect.assert_called_once_with(
            host="localhost",
            port=6041,  # 应该使用REST端口
            user="root",
            password="taosdata",
            database="market_data",
        )

    def test_get_tdengine_connection_import_error(self):
        """测试TDengine驱动未安装时抛出ImportError"""
        with patch("src.storage.database.connection_manager.taosws", side_effect=ImportError):
            with self.assertRaises(ImportError) as context:
                self.manager.get_tdengine_connection()

            self.assertIn("TDengine驱动未安装", str(context.exception))

    @patch("src.storage.database.connection_manager.taosws")
    def test_get_tdengine_connection_error(self, mock_taosws):
        """测试TDengine连接失败时抛出ConnectionError"""
        mock_taosws.connect.side_effect = Exception("Connection refused")

        with self.assertRaises(ConnectionError) as context:
            self.manager.get_tdengine_connection()

        self.assertIn("TDengine连接失败", str(context.exception))


class TestDatabaseConnectionManagerPostgreSQL(unittest.TestCase):
    """测试PostgreSQL连接管理"""

    def setUp(self):
        """测试前准备"""
        # 设置所有必需的环境变量
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )
        self.manager = DatabaseConnectionManager()

    @patch("src.storage.database.connection_manager.pool")
    def test_get_postgresql_connection_first_time(self, mock_pool):
        """测试首次获取PostgreSQL连接池"""
        mock_connection_pool = Mock()
        mock_pool.SimpleConnectionPool.return_value = mock_connection_pool

        result = self.manager.get_postgresql_connection()

        self.assertEqual(result, mock_connection_pool)
        mock_pool.SimpleConnectionPool.assert_called_once()
        self.assertIn("postgresql", self.manager._connections)

    @patch("src.storage.database.connection_manager.pool")
    def test_get_postgresql_connection_cached(self, mock_pool):
        """测试从缓存获取PostgreSQL连接池"""
        mock_connection_pool = Mock()
        mock_pool.SimpleConnectionPool.return_value = mock_connection_pool

        # 第一次调用
        result1 = self.manager.get_postgresql_connection()
        # 第二次调用
        result2 = self.manager.get_postgresql_connection()

        self.assertEqual(result1, result2)
        # 验证只创建了一次连接池
        mock_pool.SimpleConnectionPool.assert_called_once()

    @patch("src.storage.database.connection_manager.pool")
    def test_get_postgresql_connection_default_values(self, mock_pool):
        """测试使用默认值创建PostgreSQL连接"""
        # 删除端口和用户名，测试默认值
        del os.environ["POSTGRESQL_PORT"]
        del os.environ["POSTGRESQL_USER"]
        del os.environ["POSTGRESQL_PASSWORD"]
        del os.environ["POSTGRESQL_DATABASE"]

        mock_connection_pool = Mock()
        mock_pool.SimpleConnectionPool.return_value = mock_connection_pool

        self.manager.get_postgresql_connection()

        # 验证调用参数包含默认值
        call_args = mock_pool.SimpleConnectionPool.call_args
        self.assertEqual(call_args[1]["port"], 5438)  # 默认端口
        self.assertEqual(call_args[1]["user"], "postgres")  # 默认用户
        self.assertEqual(call_args[1]["password"], "")  # 默认空密码
        self.assertEqual(call_args[1]["database"], "mystocks")  # 默认数据库

    def test_get_postgresql_connection_import_error(self):
        """测试PostgreSQL驱动未安装时抛出ImportError"""
        with patch("src.storage.database.connection_manager.pool", side_effect=ImportError):
            with self.assertRaises(ImportError) as context:
                self.manager.get_postgresql_connection()

            self.assertIn("PostgreSQL驱动未安装", str(context.exception))

    @patch("src.storage.database.connection_manager.pool")
    def test_get_postgresql_connection_error(self, mock_pool):
        """测试PostgreSQL连接失败时抛出ConnectionError"""
        mock_pool.SimpleConnectionPool.side_effect = Exception("Connection refused")

        with self.assertRaises(ConnectionError) as context:
            self.manager.get_postgresql_connection()

        self.assertIn("PostgreSQL连接失败", str(context.exception))

    @patch("src.storage.database.connection_manager.pool")
    def test_return_postgresql_connection(self, mock_pool):
        """测试归还PostgreSQL连接到连接池"""
        mock_connection_pool = Mock()
        mock_pool.SimpleConnectionPool.return_value = mock_connection_pool

        # 首先获取连接池
        self.manager.get_postgresql_connection()

        # 归还连接
        mock_conn = Mock()
        self.manager._return_postgresql_connection(mock_conn)

        # 验证调用了putconn
        mock_connection_pool.putconn.assert_called_once_with(mock_conn)


class TestDatabaseConnectionManagerRedis(unittest.TestCase):
    """测试Redis连接管理（已弃用但保留）"""

    def setUp(self):
        """测试前准备"""
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )
        self.manager = DatabaseConnectionManager()

    @patch("src.storage.database.connection_manager.redis")
    def test_get_redis_connection_first_time(self, mock_redis):
        """测试首次获取Redis连接"""
        os.environ.update(
            {
                "REDIS_HOST": "localhost",
                "REDIS_PORT": "6379",
                "REDIS_DB": "1",
            }
        )

        mock_conn = Mock()
        mock_redis.Redis.return_value = mock_conn

        result = self.manager.get_redis_connection()

        self.assertEqual(result, mock_conn)
        mock_conn.ping.assert_called_once()  # 验证测试连接
        self.assertIn("redis", self.manager._connections)

    def test_get_redis_connection_import_error(self):
        """测试Redis驱动未安装时抛出ImportError"""
        with patch("src.storage.database.connection_manager.redis", side_effect=ImportError):
            with self.assertRaises(ImportError) as context:
                self.manager.get_redis_connection()

            self.assertIn("Redis驱动未安装", str(context.exception))


class TestDatabaseConnectionManagerClose(unittest.TestCase):
    """测试连接关闭功能"""

    def setUp(self):
        """测试前准备"""
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )
        self.manager = DatabaseConnectionManager()

    def test_close_tdengine_connection(self):
        """测试关闭TDengine连接"""
        mock_tdengine_conn = Mock()
        self.manager._connections["tdengine"] = mock_tdengine_conn

        self.manager.close_all_connections()

        mock_tdengine_conn.close.assert_called_once()
        self.assertNotIn("tdengine", self.manager._connections)

    def test_close_postgresql_connection(self):
        """测试关闭PostgreSQL连接"""
        mock_postgresql_pool = Mock()
        self.manager._connections["postgresql"] = mock_postgresql_pool

        self.manager.close_all_connections()

        mock_postgresql_pool.closeall.assert_called_once()
        self.assertNotIn("postgresql", self.manager._connections)

    def test_close_redis_connection(self):
        """测试关闭Redis连接"""
        mock_redis_conn = Mock()
        self.manager._connections["redis"] = mock_redis_conn

        self.manager.close_all_connections()

        mock_redis_conn.close.assert_called_once()
        self.assertNotIn("redis", self.manager._connections)

    def test_close_all_connections(self):
        """测试关闭所有连接"""
        # 模拟所有类型的连接
        self.manager._connections.update(
            {
                "tdengine": Mock(close=Mock()),
                "postgresql": Mock(closeall=Mock()),
                "redis": Mock(close=Mock()),
            }
        )

        self.manager.close_all_connections()

        # 验证所有连接都被关闭
        self.assertEqual(len(self.manager._connections), 0)

    def test_close_connection_with_error(self):
        """测试关闭连接时发生错误"""
        # 创建一个关闭时会抛出异常的连接
        mock_conn_error = Mock(close=Mock(side_effect=Exception("Close error")))
        mock_conn_ok = Mock(close=Mock())

        self.manager._connections.update(
            {
                "tdengine": mock_conn_error,
                "postgresql": mock_conn_ok,
            }
        )

        # 应该不会抛出异常，而是打印警告
        self.manager.close_all_connections()

        # 验证两个close方法都被调用了
        mock_conn_error.close.assert_called_once()
        mock_conn_ok.closeall.assert_called_once()
        # 连接应该被清空
        self.assertEqual(len(self.manager._connections), 0)


class TestDatabaseConnectionManagerTestAll(unittest.TestCase):
    """测试test_all_connections方法"""

    def setUp(self):
        """测试前准备"""
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )
        self.manager = DatabaseConnectionManager()

    @patch("src.storage.database.connection_manager.taosws")
    @patch("src.storage.database.connection_manager.pool")
    def test_all_connections_success(self, mock_pool, mock_taosws):
        """测试所有连接成功"""
        mock_tdengine_conn = Mock()
        mock_taosws.connect.return_value = mock_tdengine_conn

        mock_pg_pool = Mock()
        mock_pg_conn = Mock()
        mock_pool.SimpleConnectionPool.return_value = mock_pg_pool
        mock_pg_pool.getconn.return_value = mock_pg_conn

        results = self.manager.test_all_connections()

        self.assertTrue(results.get("tdengine"))
        self.assertTrue(results.get("postgresql"))

    @patch("src.storage.database.connection_manager.taosws")
    def test_tdengine_connection_failure(self, mock_taosws):
        """测试TDengine连接失败"""
        mock_taosws.connect.side_effect = Exception("Connection failed")

        results = self.manager.test_all_connections()

        self.assertFalse(results.get("tdengine"))

    @patch("src.storage.database.connection_manager.pool")
    def test_postgresql_connection_failure(self, mock_pool):
        """测试PostgreSQL连接失败"""
        mock_pool.SimpleConnectionPool.side_effect = Exception("Connection failed")

        results = self.manager.test_all_connections()

        self.assertFalse(results.get("postgresql"))


class TestDatabaseConnectionManagerSingleton(unittest.TestCase):
    """测试单例模式"""

    def setUp(self):
        """测试前准备"""
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )

    def test_get_connection_manager_singleton(self):
        """测试get_connection_manager返回单例"""
        manager1 = get_connection_manager()
        manager2 = get_connection_manager()

        self.assertIs(manager1, manager2)

    def test_get_connection_manager_initialization(self):
        """测试get_connection_manager首次调用时初始化"""
        manager = get_connection_manager()

        self.assertIsInstance(manager, DatabaseConnectionManager)


class TestDatabaseConnectionManagerEdgeCases(unittest.TestCase):
    """测试边界情况"""

    def setUp(self):
        """测试前准备"""
        os.environ.update(
            {
                "TDENGINE_HOST": "localhost",
                "TDENGINE_PORT": "6030",
                "TDENGINE_USER": "root",
                "TDENGINE_PASSWORD": "taosdata",
                "TDENGINE_DATABASE": "market_data",
                "POSTGRESQL_HOST": "localhost",
                "POSTGRESQL_PORT": "5438",
                "POSTGRESQL_USER": "postgres",
                "POSTGRESQL_PASSWORD": "password",
                "POSTGRESQL_DATABASE": "mystocks",
            }
        )
        self.manager = DatabaseConnectionManager()

    def test_close_empty_connections(self):
        """测试关闭空的连接字典"""
        self.manager._connections.clear()

        # 应该不会抛出异常
        self.manager.close_all_connections()
        self.assertEqual(len(self.manager._connections), 0)

    def test_return_postgresql_connection_without_pool(self):
        """测试在没有连接池时归还连接"""
        mock_conn = Mock()

        # 应该不会抛出异常
        self.manager._return_postgresql_connection(mock_conn)


if __name__ == "__main__":
    unittest.main(verbosity=2)
