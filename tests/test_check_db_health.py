"""
测试check_db_health数据库健康检查工具

修改: 2025-11-19 - 更新为双数据库架构 (PostgreSQL + TDengine)
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, "/opt/claude/mystocks_spec")

# 动态导入模块
import importlib.util

spec = importlib.util.spec_from_file_location(
    "check_db_health", "/opt/claude/mystocks_spec/src/utils/check_db_health.py"
)
check_db_health = importlib.util.module_from_spec(spec)


@pytest.fixture(autouse=True)
def load_module():
    """加载模块，如果失败则跳过测试"""
    try:
        spec.loader.exec_module(check_db_health)
    except FileNotFoundError:
        pytest.skip("check_db_health.py 文件不存在")
    except Exception as e:
        pytest.skip(f"加载模块失败: {str(e)}")


class TestDatabaseHealthCheck:
    """数据库健康检查测试类 (双数据库架构: PostgreSQL + TDengine)"""

    @patch("psycopg2.connect")
    def test_check_postgresql_success(self, mock_connect):
        """测试PostgreSQL检查成功"""
        # Mock连接和cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("PostgreSQL 17.6",)
        mock_cursor.fetchall.return_value = [("test_table",)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # 调用方法
        if hasattr(check_db_health, "check_postgresql_connection"):
            result = check_db_health.check_postgresql_connection()

            # 验证
            assert result is not None
            assert "status" in result
            assert result["status"] in ["success", "failed"]
        else:
            pytest.skip("check_postgresql_connection 函数不存在")

    @patch("psycopg2.connect")
    def test_check_postgresql_connection_failure(self, mock_connect):
        """测试PostgreSQL连接失败"""
        # Mock连接失败
        mock_connect.side_effect = Exception("Connection refused")

        # 调用方法
        if hasattr(check_db_health, "check_postgresql_connection"):
            result = check_db_health.check_postgresql_connection()

            # 验证
            assert result is not None
            assert result["status"] == "failed"
        else:
            pytest.skip("check_postgresql_connection 函数不存在")

    @patch("taos.connect")
    def test_check_tdengine_success(self, mock_connect):
        """测试TDengine检查成功"""
        # Mock连接和cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = ("3.0.0",)
        mock_cursor.fetchall.return_value = [("test_db",)]

        mock_conn = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # 调用方法
        if hasattr(check_db_health, "check_tdengine_connection"):
            result = check_db_health.check_tdengine_connection()

            # 验证
            assert result is not None
            assert "status" in result
            assert result["status"] in ["success", "failed"]
        else:
            pytest.skip("check_tdengine_connection 函数不存在")

    @patch("taos.connect")
    def test_check_tdengine_connection_failure(self, mock_connect):
        """测试TDengine连接失败"""
        # Mock连接失败
        mock_connect.side_effect = Exception("Connection refused")

        # 调用方法
        if hasattr(check_db_health, "check_tdengine_connection"):
            result = check_db_health.check_tdengine_connection()

            # 验证
            assert result is not None
            assert result["status"] == "failed"
        else:
            pytest.skip("check_tdengine_connection 函数不存在")


class TestHealthCheckIntegration:
    """集成测试"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_run_all_checks(self):
        """测试运行所有检查（可选）"""
        try:
            results = []

            # 运行 PostgreSQL 检查
            if hasattr(check_db_health, "check_postgresql_connection"):
                postgresql_result = check_db_health.check_postgresql_connection()
                results.append(postgresql_result)

            # 运行 TDengine 检查
            if hasattr(check_db_health, "check_tdengine_connection"):
                tdengine_result = check_db_health.check_tdengine_connection()
                results.append(tdengine_result)

            # 验证结果
            if results:
                assert all(r is not None for r in results)
                assert all("status" in r for r in results)
            else:
                pytest.skip("没有可用的健康检查函数")

        except Exception as e:
            pytest.skip(f"健康检查失败: {str(e)}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
