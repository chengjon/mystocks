#!/usr/bin/env python3
"""API健康检查模块测试套件
基于Phase 6成功模式：功能→边界→异常→性能→集成测试
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
import src.utils.check_api_health as api_health_module
from src.utils.check_api_health import (
    API_ENDPOINTS,
    BASE_URL,
    TIMEOUT,
    check_backend_running,
    get_auth_token,
    main,
)


class TestConstantsAndConfiguration:
    """常量和配置测试类"""

    def test_base_url_constant(self):
        """测试BASE_URL常量"""
        expected = os.getenv("BACKEND_URL", f"http://localhost:{os.getenv('BACKEND_PORT', '8020')}")
        assert expected == BASE_URL

    def test_timeout_constant(self):
        """测试TIMEOUT常量"""
        assert TIMEOUT == 5

    def test_api_endpoints_structure(self):
        """测试API_ENDPOINTS配置结构"""
        assert isinstance(API_ENDPOINTS, list)
        assert len(API_ENDPOINTS) == 10

        # 验证每个端点的结构
        for endpoint in API_ENDPOINTS:
            required_keys = [
                "name",
                "method",
                "url",
                "data",
                "auth_required",
                "priority",
                "page",
            ]
            for key in required_keys:
                assert key in endpoint, f"端点缺少必需的键: {key}"

            # 验证方法
            assert endpoint["method"] in ["GET", "POST"], f"不支持的方法: {endpoint['method']}"

            # 验证优先级
            assert endpoint["priority"] in ["P1", "P2", "P3"], f"无效优先级: {endpoint['priority']}"

    def test_api_endpoints_content(self):
        """测试API端点内容"""
        # 验证登录端点
        login_endpoint = API_ENDPOINTS[0]
        assert login_endpoint["name"] == "登录认证"
        assert login_endpoint["method"] == "POST"
        assert login_endpoint["url"] == "/api/auth/login"
        assert login_endpoint["auth_required"] == False
        assert login_endpoint["priority"] == "P1"

        # 验证系统健康检查端点
        health_endpoint = API_ENDPOINTS[-1]
        assert health_endpoint["name"] == "系统健康检查"
        assert health_endpoint["method"] == "GET"
        assert health_endpoint["url"] == "/api/system/health"
        assert health_endpoint["auth_required"] == False
        assert health_endpoint["priority"] == "P2"


class TestCheckBackendRunning:
    """后端服务检查测试类"""

    @patch("src.utils.check_api_health.requests.get")
    def test_backend_running_success(self, mock_get):
        """测试后端服务正常运行"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        result = check_backend_running()

        assert result is True
        mock_get.assert_called_once_with(f"{BASE_URL}/api/docs", timeout=2)

    @patch("src.utils.check_api_health.requests.get")
    def test_backend_not_running_404(self, mock_get):
        """测试后端服务返回404"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = check_backend_running()

        assert result is False

    @patch("src.utils.check_api_health.requests.get")
    def test_backend_connection_error(self, mock_get):
        """测试后端服务连接错误"""
        mock_get.side_effect = requests.exceptions.ConnectionError("连接被拒绝")

        result = check_backend_running()

        assert result is False

    @patch("src.utils.check_api_health.requests.get")
    def test_backend_timeout_error(self, mock_get):
        """测试后端服务超时错误"""
        mock_get.side_effect = requests.exceptions.Timeout("超时")

        result = check_backend_running()

        assert result is False

    @patch("src.utils.check_api_health.requests.get")
    def test_backend_general_exception(self, mock_get):
        """测试后端服务一般异常"""
        mock_get.side_effect = Exception("一般错误")

        result = check_backend_running()

        assert result is False


class TestGetAuthToken:
    """认证Token获取测试类"""

    @patch("src.utils.check_api_health.requests.post")
    def test_get_token_success(self, mock_post):
        """测试成功获取Token"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"access_token": "test_token_12345"}
        mock_post.return_value = mock_response

        token = get_auth_token()

        assert token == "test_token_12345"
        mock_post.assert_called_once_with(
            f"{BASE_URL}/api/auth/login",
            data={"username": "admin", "password": "admin123"},
            timeout=TIMEOUT,
        )

    @patch("src.utils.check_api_health.requests.post")
    def test_get_token_no_access_token(self, mock_post):
        """测试响应中没有access_token"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "登录成功"}
        mock_post.return_value = mock_response

        token = get_auth_token()

        assert token is None

    @patch("src.utils.check_api_health.requests.post")
    def test_get_token_401_error(self, mock_post):
        """测试登录认证失败"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_post.return_value = mock_response

        token = get_auth_token()

        assert token is None

    @patch("src.utils.check_api_health.requests.post")
    @patch("builtins.print")
    def test_get_token_connection_error(self, mock_print, mock_post):
        """测试Token获取连接错误"""
        mock_post.side_effect = requests.exceptions.ConnectionError("连接被拒绝")

        token = get_auth_token()

        assert token is None
        # 验证错误消息被打印
        mock_print.assert_called()
        call_args = str(mock_print.call_args)
        assert "警告: 无法获取Token" in call_args

    @patch("src.utils.check_api_health.requests.post")
    @patch("builtins.print")
    def test_get_token_timeout_error(self, mock_print, mock_post):
        """测试Token获取超时"""
        mock_post.side_effect = requests.exceptions.Timeout("超时")

        token = get_auth_token()

        assert token is None
        # 验证错误消息被打印
        mock_print.assert_called()

    @patch("src.utils.check_api_health.requests.post")
    @patch("builtins.print")
    def test_get_token_general_exception(self, mock_print, mock_post):
        """测试Token获取一般异常"""
        mock_post.side_effect = Exception("一般错误")

        token = get_auth_token()

        assert token is None
        # 验证错误消息被打印
        mock_print.assert_called()


class TestApiEndpointTesting:
    """API端点测试函数测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.sample_endpoint = {
            "name": "测试端点",
            "method": "GET",
            "url": "/api/test",
            "data": None,
            "auth_required": False,
            "priority": "P1",
            "page": "测试页面",
        }

    @patch("src.utils.check_api_health.requests.get")
    def test_get_endpoint_success(self, mock_get):
        """测试GET端点成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is True
        assert message == "成功"
        assert status_code == 200
        mock_get.assert_called_once_with(
            f"{BASE_URL}/api/test",
            headers={},
            timeout=TIMEOUT,
        )

    @patch("src.utils.check_api_health.requests.post")
    def test_post_endpoint_success(self, mock_post):
        """测试POST端点成功"""
        endpoint = {
            "name": "POST测试端点",
            "method": "POST",
            "url": "/api/test",
            "data": {"key": "value"},
            "auth_required": False,
            "priority": "P1",
            "page": "测试页面",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            endpoint,
            None,
        )

        assert success is True
        assert message == "成功"
        assert status_code == 200
        expected_headers = {"Content-Type": "application/json"}
        mock_post.assert_called_once_with(
            f"{BASE_URL}/api/test",
            json={"key": "value"},
            headers=expected_headers,
            timeout=TIMEOUT,
        )

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_with_auth(self, mock_get):
        """测试需要认证的端点"""
        endpoint = {**self.sample_endpoint, "auth_required": True}
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            endpoint,
            "test_token",
        )

        assert success is True
        expected_headers = {"Authorization": "Bearer test_token"}
        mock_get.assert_called_once_with(
            f"{BASE_URL}/api/test",
            headers=expected_headers,
            timeout=TIMEOUT,
        )

    def test_endpoint_with_auth_no_token(self):
        """测试需要认证但没有Token的端点"""
        endpoint = {**self.sample_endpoint, "auth_required": True}

        success, message, status_code = api_health_module.test_api_endpoint(
            endpoint,
            None,
        )

        # 没有token时，会直接发送请求（不带Authorization头）
        # 由于没有mock请求，这里应该会失败
        assert success is False
        assert "Backend未启动" in message or "连接被拒绝" in message

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_401_error(self, mock_get):
        """测试401认证错误"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "认证失败 (Token无效或过期)"
        assert status_code == 401

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_404_error(self, mock_get):
        """测试404端点不存在错误"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "端点不存在"
        assert status_code == 404

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_500_error(self, mock_get):
        """测试500服务器内部错误"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "服务器内部错误"
        assert status_code == 500

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_503_error(self, mock_get):
        """测试503服务不可用错误"""
        mock_response = Mock()
        mock_response.status_code = 503
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "服务不可用 (可能数据库连接失败)"
        assert status_code == 503

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_other_http_error(self, mock_get):
        """测试其他HTTP错误码"""
        mock_response = Mock()
        mock_response.status_code = 422
        mock_get.return_value = mock_response

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "HTTP 422"
        assert status_code == 422

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_connection_error(self, mock_get):
        """测试连接错误"""
        mock_get.side_effect = requests.exceptions.ConnectionError("连接被拒绝")

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "连接被拒绝 (Backend未启动?)"
        assert status_code is None

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_timeout_error(self, mock_get):
        """测试请求超时错误"""
        mock_get.side_effect = requests.exceptions.Timeout("超时")

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == f"请求超时 (>{TIMEOUT}s)"
        assert status_code is None

    @patch("src.utils.check_api_health.requests.get")
    def test_endpoint_general_exception(self, mock_get):
        """测试一般异常"""
        mock_get.side_effect = Exception("一般错误")

        success, message, status_code = api_health_module.test_api_endpoint(
            self.sample_endpoint,
            None,
        )

        assert success is False
        assert message == "异常: 一般错误"
        assert status_code is None

    def test_endpoint_unsupported_method(self):
        """测试不支持的HTTP方法"""
        endpoint = {**self.sample_endpoint, "method": "DELETE"}

        success, message, status_code = api_health_module.test_api_endpoint(
            endpoint,
            None,
        )

        assert success is False
        assert message == "不支持的方法: DELETE"
        assert status_code is None


class TestMainFunction:
    """主函数测试类"""

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_backend_not_running(
        self,
        mock_print,
        mock_check,
        mock_token,
        mock_test,
    ):
        """测试后端服务未运行的情况"""
        mock_check.return_value = False

        exit_code = main()

        assert exit_code == 1
        mock_print.assert_called()
        # 验证错误消息
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Backend服务未运行" in call for call in print_calls)

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_successful_run_100_percent(
        self,
        mock_print,
        mock_check,
        mock_token,
        mock_test,
    ):
        """测试100%通过的成功运行"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"
        # 模拟所有API测试都成功
        mock_test.return_value = (True, "成功", 200)

        exit_code = main()

        assert exit_code == 0
        # 验证所有API都被测试
        assert mock_test.call_count == len(API_ENDPOINTS)

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_partial_success_above_80_percent(
        self,
        mock_print,
        mock_check,
        mock_token,
        mock_test,
    ):
        """测试80%以上的部分成功"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"

        # 模拟9/10的API成功（90%通过率）
        def side_effect_func(endpoint, token):
            if endpoint["name"] == "系统健康检查":  # 让最后一个失败
                return (False, "模拟失败", 500)
            return (True, "成功", 200)

        mock_test.side_effect = side_effect_func

        exit_code = main()

        assert exit_code == 0  # 90% > 80%，应该返回0

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_partial_success_below_80_percent(
        self,
        mock_print,
        mock_check,
        mock_token,
        mock_test,
    ):
        """测试低于80%的部分成功"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"

        # 模拟只有7/10的API成功（70%通过率）
        def side_effect_func(endpoint, token):
            if endpoint["priority"] in ["P2", "P3"]:  # 让所有P2和P3失败
                return (False, "模拟失败", 500)
            return (True, "成功", 200)

        mock_test.side_effect = side_effect_func

        exit_code = main()

        assert exit_code == 1  # 70% < 80%，应该返回1

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_no_token(self, mock_print, mock_check, mock_token, mock_test):
        """测试无法获取Token的情况"""
        mock_check.return_value = True
        mock_token.return_value = None  # 无Token
        mock_test.return_value = (True, "成功", 200)

        exit_code = main()

        # 验证警告消息
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("Token获取失败" in call for call in print_calls)

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_result_statistics(
        self,
        mock_print,
        mock_check,
        mock_token,
        mock_test,
    ):
        """测试结果统计功能"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"

        # 模拟不同优先级的不同结果
        def side_effect_func(endpoint, token):
            if endpoint["priority"] == "P1":
                return (True, "成功", 200)  # 所有P1成功
            if endpoint["priority"] == "P2":
                if endpoint["name"] == "技术指标":  # 让P2中1个失败
                    return (False, "模拟失败", 500)
                return (True, "成功", 200)
            # P3失败
            return (False, "模拟失败", 404)

        mock_test.side_effect = side_effect_func

        exit_code = main()

        # 验证统计输出
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("P1: 4/4" in call for call in print_calls)
        assert any("P2: 4/5" in call for call in print_calls)
        assert any("P3: 0/1" in call for call in print_calls)

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_failed_items_details(
        self,
        mock_print,
        mock_check,
        mock_token,
        mock_test,
    ):
        """测试失败项详情输出"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"

        # 模拟2个API失败
        def side_effect_func(endpoint, token):
            if endpoint["name"] in ["财务数据", "数据源管理"]:
                return (False, "模拟错误消息", 500)
            return (True, "成功", 200)

        mock_test.side_effect = side_effect_func

        exit_code = main()

        # 验证失败项详情输出
        print_calls = [str(call) for call in mock_print.call_args_list]
        assert any("失败项详情" in call for call in print_calls)
        assert any("财务数据" in call for call in print_calls)
        assert any("数据源管理" in call for call in print_calls)

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_fix_suggestions(self, mock_print, mock_check, mock_token, mock_test):
        """测试修复建议功能"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"

        # 模拟不同类型的错误
        def side_effect_func(endpoint, token):
            if "连接被拒绝" in endpoint["name"]:
                return (False, "连接被拒绝 (Backend未启动?)", None)
            if "端点不存在" in endpoint["name"]:
                return (False, "端点不存在", 404)
            if "认证失败" in endpoint["name"]:
                return (False, "认证失败 (Token无效或过期)", 401)
            if "服务器内部错误" in endpoint["name"]:
                return (False, "服务器内部错误", 500)
            if "服务不可用" in endpoint["name"]:
                return (False, "服务不可用 (可能数据库连接失败)", 503)
            return (True, "成功", 200)

        # 临时修改API_ENDPOINTS以包含各种错误
        original_endpoints = API_ENDPOINTS[:]
        try:
            API_ENDPOINTS.clear()
            API_ENDPOINTS.extend(
                [
                    {
                        "name": "连接被拒绝测试",
                        "method": "GET",
                        "url": "/api/test1",
                        "data": None,
                        "auth_required": False,
                        "priority": "P1",
                        "page": "测试",
                    },
                    {
                        "name": "端点不存在测试",
                        "method": "GET",
                        "url": "/api/test2",
                        "data": None,
                        "auth_required": False,
                        "priority": "P1",
                        "page": "测试",
                    },
                    {
                        "name": "认证失败测试",
                        "method": "GET",
                        "url": "/api/test3",
                        "data": None,
                        "auth_required": False,
                        "priority": "P1",
                        "page": "测试",
                    },
                    {
                        "name": "服务器内部错误测试",
                        "method": "GET",
                        "url": "/api/test4",
                        "data": None,
                        "auth_required": False,
                        "priority": "P1",
                        "page": "测试",
                    },
                    {
                        "name": "服务不可用测试",
                        "method": "GET",
                        "url": "/api/test5",
                        "data": None,
                        "auth_required": False,
                        "priority": "P1",
                        "page": "测试",
                    },
                ],
            )

            mock_test.side_effect = side_effect_func
            exit_code = main()

            # 验证修复建议输出
            print_calls = [str(call) for call in mock_print.call_args_list]
            assert any("修复建议" in call for call in print_calls)
            assert any("启动Backend服务" in call for call in print_calls)
            assert any("检查路由注册" in call for call in print_calls)
            assert any("检查JWT配置" in call for call in print_calls)
            assert any("查看Backend日志" in call for call in print_calls)
            assert any("检查数据库连接" in call for call in print_calls)

        finally:
            # 恢复原始配置
            API_ENDPOINTS.clear()
            API_ENDPOINTS.extend(original_endpoints)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
