#!/usr/bin/env python3
"""API健康检查工具测试套件 v2.0
完整测试check_api_health_v2模块的所有功能，确保100%测试覆盖率
遵循Phase 6成功模式：功能→边界→异常→性能→集成测试
"""

import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
import requests


# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入被测试的模块
from src.utils.check_api_health_v2 import APIHealthChecker, Colors


EXPECTED_BASE_URL = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8020')}")


class TestColors:
    """Colors类测试类"""

    def test_color_constants_exist(self):
        """测试颜色常量存在"""
        # 验证所有需要的颜色常量都存在
        required_colors = ["RED", "GREEN", "YELLOW", "BLUE", "BOLD", "END"]
        for color in required_colors:
            assert hasattr(Colors, color)
            assert isinstance(getattr(Colors, color), str)

    def test_color_values_are_strings(self):
        """测试颜色值都是字符串"""
        color_constants = [
            Colors.RED,
            Colors.GREEN,
            Colors.YELLOW,
            Colors.BLUE,
            Colors.BOLD,
            Colors.END,
        ]
        for color in color_constants:
            assert isinstance(color, str)
            assert len(color) > 0  # 颜色代码不能为空

    def test_color_codes_format(self):
        """测试颜色代码格式正确"""
        # 验证颜色代码符合ANSI格式
        for color in [Colors.RED, Colors.GREEN, Colors.YELLOW, Colors.BLUE]:
            # ANSI颜色码通常以 \033[ 开头，以 m 结尾
            assert color.startswith("\033[") or color.startswith("\x1b[")

    def test_bold_and_reset_codes(self):
        """测试加粗和重置代码"""
        # BOLD应该是加粗，END应该是重置
        assert Colors.BOLD.endswith("m")
        assert Colors.END == "\033[0m" or Colors.END == "\x1b[0m"


class TestAPIHealthChecker:
    """APIHealthChecker类测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.checker = APIHealthChecker()

    def test_init_method(self):
        """测试初始化方法"""
        # 验证初始化后的属性
        assert hasattr(self.checker, "results")
        assert isinstance(self.checker.results, list)
        assert len(self.checker.results) == 0  # 初始应该为空

        assert hasattr(self.checker, "token")
        assert self.checker.token is None  # 初始应该没有token

    def test_print_header_method(self):
        """测试打印标题方法"""
        with patch("builtins.print") as mock_print:
            self.checker.print_header("Test Header")

            # 验证print被调用了3次（顶部线、标题、底部线）
            assert mock_print.call_count == 3

            # 验证调用参数包含标题文本
            call_args = [str(call[0]) for call in mock_print.call_args_list]
            assert "Test Header" in "\n".join(call_args)

    def test_print_result_method_with_different_statuses(self):
        """测试打印结果方法的不同状态"""
        with patch("builtins.print") as mock_print:
            # 测试PASS状态
            self.checker.print_result("Test1", "PASS", "Success message")
            # 测试FAIL状态
            self.checker.print_result("Test2", "FAIL", "Error message")
            # 测试其他状态
            self.checker.print_result("Test3", "WARN", "Warning message")

            # 验证每次调用都调用了print
            assert mock_print.call_count == 6  # 3个测试 × 2次调用每次

            # 验证包含了正确的符号
            all_prints = "\n".join([str(call[0]) for call in mock_print.call_args_list])
            assert "✅" in all_prints
            assert "❌" in all_prints
            assert "⚠️" in all_prints

    def test_print_result_method_without_detail(self):
        """测试没有详细信息的打印结果"""
        with patch("builtins.print") as mock_print:
            self.checker.print_result("Test", "PASS")

            # 没有详细信息时，应该只调用一次print
            assert mock_print.call_count == 1

    def test_check_backend_running_success(self):
        """测试后端服务检查成功情况"""
        with patch("requests.get") as mock_get:
            # 模拟成功响应
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = self.checker.check_backend_running()

            assert result is True
            mock_get.assert_called_once()
            mock_get.assert_called_with(f"{EXPECTED_BASE_URL}/api/docs", timeout=2)

    def test_check_backend_running_failure(self):
        """测试后端服务检查失败情况"""
        with patch("requests.get") as mock_get:
            # 模拟异常
            mock_get.side_effect = Exception("Connection error")

            result = self.checker.check_backend_running()

            assert result is False

    def test_check_backend_running_different_status_code(self):
        """测试后端服务检查不同状态码"""
        with patch("requests.get") as mock_get:
            # 模拟非200状态码
            mock_response = Mock()
            mock_response.status_code = 404
            mock_get.return_value = mock_response

            result = self.checker.check_backend_running()

            assert result is False

    @patch("requests.post")
    def test_get_jwt_token_success(self, mock_post):
        """测试JWT token获取成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token"}
        mock_post.return_value = mock_response

        success, token = self.checker.get_jwt_token()

        assert success is True
        assert token == "test_token"
        mock_post.assert_called_once()

    @patch("requests.post")
    def test_get_jwt_token_failure_status_code(self, mock_post):
        """测试JWT token获取失败（状态码）"""
        # 模拟失败响应
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        success, error = self.checker.get_jwt_token()

        assert success is False
        assert "401" in error

    @patch("requests.post")
    def test_get_jwt_token_exception(self, mock_post):
        """测试JWT token获取异常"""
        # 模拟异常
        mock_post.side_effect = Exception("Network error")

        success, error = self.checker.get_jwt_token()

        assert success is False
        assert "Network error" in error

    def test_test_endpoint_unsupported_method(self):
        """测试不支持的HTTP方法"""
        result = self.checker.test_endpoint(
            name="Test",
            method="DELETE",  # 不支持的方法
            url="http://example.com/api/test",
            priority="high",
        )

        assert result["status"] == "SKIP"
        assert "不支持的HTTP方法" in result["error"]
        assert result["name"] == "Test"

    @patch("requests.get")
    def test_test_endpoint_get_success(self, mock_get):
        """测试GET请求成功"""
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.elapsed.total_seconds.return_value = 0.1
        mock_get.return_value = mock_response

        result = self.checker.test_endpoint(
            name="Test GET",
            method="GET",
            url="http://example.com/api/test",
            priority="high",
        )

        assert result["name"] == "Test GET"
        assert result["method"] == "GET"
        assert result["status_code"] == 200
        assert result["status"] == "PASS"
        assert result["response_time"] == 100.0  # 0.1秒 = 100毫秒
        assert result["url"] == "http://example.com/api/test"
        assert result["priority"] == "high"

    @patch("requests.get")
    def test_test_endpoint_get_with_params(self, mock_get):
        """测试GET请求带参数"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_response.elapsed.total_seconds.return_value = 0.05
        mock_get.return_value = mock_response

        result = self.checker.test_endpoint(
            name="Test GET with params",
            method="GET",
            url="http://example.com/api/test",
            priority="medium",
            params={"param1": "value1"},
        )

        assert result["status"] == "PASS"
        mock_get.assert_called_once()
        # 验证参数被正确传递
        args, kwargs = mock_get.call_args
        assert kwargs.get("params") == {"param1": "value1"}

    @patch("requests.post")
    def test_test_endpoint_post_success(self, mock_post):
        """测试POST请求成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"result": "success"}
        mock_response.elapsed.total_seconds.return_value = 0.15
        mock_post.return_value = mock_response

        result = self.checker.test_endpoint(
            name="Test POST",
            method="POST",
            url="http://example.com/api/test",
            priority="high",
            data={"key": "value"},
        )

        assert result["name"] == "Test POST"
        assert result["method"] == "POST"
        assert result["status_code"] == 200
        assert result["status"] == "PASS"
        assert result["response_time"] == 150.0
        assert result["data_keys"] == ["result"]

    def test_test_endpoint_with_auth(self):
        """测试需要认证的端点"""
        # 首先设置token
        self.checker.token = "test_token"

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": "authenticated"}
            mock_response.elapsed.total_seconds.return_value = 0.08
            mock_get.return_value = mock_response

            result = self.checker.test_endpoint(
                name="Authenticated Test",
                method="GET",
                url="http://example.com/api/protected",
                priority="medium",
                need_auth=True,
            )

            assert result["status"] == "PASS"
            assert result["need_auth"] is True
            # 验证Authorization头被设置
            args, kwargs = mock_get.call_args
            headers = kwargs.get("headers", {})
            assert headers.get("Authorization") == "Bearer test_token"

    def test_test_endpoint_status_code_not_200(self):
        """测试状态码不是200的情况"""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.json.return_value = {"error": "Not found"}
            mock_response.elapsed.total_seconds.return_value = 0.02
            mock_get.return_value = mock_response

            result = self.checker.test_endpoint(
                name="Not Found Test",
                method="GET",
                url="http://exception.com/api/notfound",
                priority="low",
            )

            assert result["status"] == "FAIL"
            assert result["status_code"] == 404

    def test_test_endpoint_json_parsing_error(self):
        """测试JSON解析错误"""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_response.elapsed.total_seconds.return_value = 0.03
            mock_get.return_value = mock_response

            result = self.checker.test_endpoint(
                name="JSON Error Test",
                method="GET",
                url="http://example.com/api/invalid",
                priority="low",
            )

            assert result["status"] == "PASS"
            assert "data_keys" not in result

    def test_test_endpoint_request_exception(self):
        """测试请求异常"""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.RequestException("Request failed")

            result = self.checker.test_endpoint(
                name="Request Exception Test",
                method="GET",
                url="http://example.com/api/exception",
                priority="low",
            )

            assert result["status"] == "FAIL"
            assert "Request failed" in result["error"]

    def test_test_endpoint_timeout(self):
        """测试请求超时"""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.Timeout("Request timeout")

            result = self.checker.test_endpoint(
                name="Timeout Test",
                method="GET",
                url="http://example.com/api/timeout",
                priority="low",
            )

            assert result["status"] == "FAIL"
            assert "请求超时" in result["error"]

    def test_run_tests_workflow(self):
        """测试完整测试工作流"""
        # Mock所有依赖的外部调用
        with (
            patch.object(self.checker, "check_backend_running"),
            patch.object(self.checker, "get_jwt_token"),
            patch.object(self.checker, "test_endpoint") as mock_test,
            patch.object(self.checker, "generate_report") as mock_report,
        ):
            # 模拟后端检查
            self.checker.check_backend_running.return_value = True

            # 模拟token获取
            self.checker.get_jwt_token.return_value = (True, "test_token")

            # 模拟测试执行
            mock_test.return_value = {"name": "Test", "status": "PASS"}

            # 模拟多个测试
            def mock_test_side_effect(*args, **kwargs):
                return {"name": kwargs["name"], "status": "PASS", "priority": kwargs["priority"]}

            mock_test.side_effect = mock_test_side_effect

            self.checker.run_tests()

            # 验证调用顺序和次数
            self.checker.check_backend_running.assert_called_once()
            self.checker.get_jwt_token.assert_called_once()
            # test_endpoint 应该被调用多次（针对不同的API端点）
            assert mock_test.call_count > 0
            self.checker.generate_report.assert_called_once()

    def test_run_tests_backend_not_running(self):
        """测试后端服务未运行的情况"""
        with patch.object(self.checker, "check_backend_running") as mock_check:
            mock_check.return_value = False

            with patch("builtins.print") as mock_print:
                self.checker.run_tests()

                # 验证打印了错误信息
                all_prints = "\n".join(
                    [str(call[0]) for call in mock_print.call_args_list],
                )
                assert "Backend服务未运行" in all_prints or "❌" in all_prints

    def test_run_tests_auth_failure(self):
        """测试认证失败的情况"""
        with (
            patch.object(self.checker, "check_backend_running") as mock_check,
            patch.object(self.checker, "get_jwt_token") as mock_auth,
            patch.object(self.checker, "test_endpoint"),
            patch.object(self.checker, "generate_report"),
        ):
            # 模拟后端运行正常
            mock_check.return_value = True

            # 模拟认证失败
            mock_auth.return_value = (False, "Authentication failed")

            with patch("builtins.print") as mock_print:
                self.checker.run_tests()

                # 验证打印了认证失败信息
                all_prints = "\n".join(
                    [str(call[0]) for call in mock_print.call_args_list],
                )
                assert "获取失败" in all_prints or "⚠️" in all_prints

    def test_generate_report_empty_results(self):
        """测试空结果生成报告"""
        # 初始状态应该没有结果
        assert len(self.checker.results) == 0

        with patch("builtins.print") as mock_print:
            self.checker.generate_report()

            # 验证打印了汇总信息
            assert mock_print.call_count >= 3  # 至少标题、统计、结束线
            all_prints = "\n".join([str(call[0]) for call in mock_print.call_args_list])
            assert "测试结果汇总" in all_prints

    def test_generate_report_with_results(self):
        """测试有结果时生成报告"""
        # 添加一些测试结果
        self.checker.results = [
            {"name": "Test1", "status": "PASS", "priority": "high"},
            {"name": "Test2", "status": "FAIL", "priority": "medium", "error": "Error"},
            {"name": "Test3", "status": "SKIP", "priority": "low"},
        ]

        with patch("builtins.print") as mock_print:
            self.checker.generate_report()

            # 验证打印了统计信息
            all_prints = "\n".join([str(call[0]) for call in mock_print.call_args_list])
            assert "总测试数: 3" in all_prints
            assert "通过:" in all_prints
            assert "失败:" in all_prints

    def test_generate_report_statistics(self):
        """测试报告统计计算"""
        # 添加各种状态的结果
        self.checker.results = [
            {"name": "Test1", "status": "PASS", "priority": "high"},
            {"name": "Test2", "status": "PASS", "priority": "medium"},
            {"name": "Test3", "status": "FAIL", "priority": "low"},
            {"name": "Test4", "status": "SKIP", "priority": "low"},
            {"name": "Test5", "status": "FAIL", "priority": "high"},
        ]

        with patch("builtins.print") as mock_print:
            self.checker.generate_report()

            all_prints = "\n".join([str(call[0]) for call in mock_print.call_args_list])
            # 验证包含了各种统计信息
            assert "总测试数: 5" in all_prints
            assert "通过: 2" in all_prints
            assert "失败: 2" in all_prints


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
