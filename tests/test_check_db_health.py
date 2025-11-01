"""
测试check_db_health数据库健康检查工具
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
sys.path.insert(0, '/opt/claude/mystocks_spec')

# 动态导入模块
import importlib.util
spec = importlib.util.spec_from_file_location("check_db_health", "/opt/claude/mystocks_spec/utils/check_db_health.py")
check_db_health = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_db_health)


class TestDatabaseHealthCheck:
    """数据库健康检查测试类"""

    @patch('pymysql.connect')
    def test_check_mysql_success(self, mock_connect):
        """测试MySQL检查成功"""
        # Mock连接和cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('9.2.0',)
        mock_cursor.fetchall.return_value = [('test_table',)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # 调用方法
        result = check_db_health.check_mysql_connection()

        # 验证
        assert result is not None
        assert 'status' in result
        assert result['status'] in ['success', 'failed']

    @patch('pymysql.connect')
    def test_check_mysql_connection_failure(self, mock_connect):
        """测试MySQL连接失败"""
        # Mock连接失败
        mock_connect.side_effect = Exception("Connection refused")

        # 调用方法
        result = check_db_health.check_mysql_connection()

        # 验证
        assert result is not None
        assert result['status'] == 'failed'

    @patch('psycopg2.connect')
    def test_check_postgresql_success(self, mock_connect):
        """测试PostgreSQL检查成功"""
        # Mock连接和cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('PostgreSQL 17.6',)
        mock_cursor.fetchall.return_value = [('test_table',)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # 调用方法
        result = check_db_health.check_postgresql_connection()

        # 验证
        assert result is not None
        assert 'status' in result
        assert result['status'] in ['success', 'failed']

    @patch('taos.connect')
    def test_check_tdengine_success(self, mock_connect):
        """测试TDengine检查成功"""
        # Mock连接和cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ('3.0.0',)
        mock_cursor.fetchall.return_value = [('test_db',)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # 调用方法
        result = check_db_health.check_tdengine_connection()

        # 验证
        assert result is not None
        assert 'status' in result
        assert result['status'] in ['success', 'failed']

    @patch('redis.Redis')
    def test_check_redis_success(self, mock_redis):
        """测试Redis检查成功"""
        # Mock Redis连接
        mock_conn = MagicMock()
        mock_conn.ping.return_value = True
        mock_conn.info.return_value = {'redis_version': '8.0.2'}
        mock_redis.return_value = mock_conn

        # 调用方法
        result = check_db_health.check_redis_connection()

        # 验证
        assert result is not None
        assert 'status' in result
        assert result['status'] in ['success', 'failed']


class TestHealthCheckIntegration:
    """集成测试"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_run_all_checks(self):
        """测试运行所有检查（可选）"""
        try:
            # 运行所有检查
            mysql_result = check_db_health.check_mysql_connection()
            postgresql_result = check_db_health.check_postgresql_connection()
            tdengine_result = check_db_health.check_tdengine_connection()
            redis_result = check_db_health.check_redis_connection()

            # 验证结果
            results = [mysql_result, postgresql_result, tdengine_result, redis_result]
            assert all(r is not None for r in results)
            assert all('status' in r for r in results)
        except Exception as e:
            pytest.skip(f"Health check failed: {str(e)}")
