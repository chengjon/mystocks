#!/usr/bin/env python3
"""Support tests extracted from `scripts/tests/test_check_api_health.py`."""

from unittest.mock import Mock, patch

import requests

import src.utils.check_api_health as api_health_module
from src.utils.check_api_health import API_ENDPOINTS, BASE_URL, TIMEOUT, main


class TestEdgeCasesAndErrorHandling:
    """边界条件和错误处理测试类"""

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_zero_endpoints(self, mock_print, mock_check, mock_token, mock_test):
        """测试零端点的情况"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"

        original_endpoints = API_ENDPOINTS[:]
        try:
            API_ENDPOINTS.clear()
            exit_code = main()
            assert exit_code == 1
        finally:
            API_ENDPOINTS.extend(original_endpoints)

    @patch("src.utils.check_api_health.test_api_endpoint")
    @patch("src.utils.check_api_health.get_auth_token")
    @patch("src.utils.check_api_health.check_backend_running")
    @patch("builtins.print")
    def test_main_all_endpoints_fail(self, mock_print, mock_check, mock_token, mock_test):
        """测试所有端点都失败的情况"""
        mock_check.return_value = True
        mock_token.return_value = "test_token"
        mock_test.return_value = (False, "全部失败", 500)

        exit_code = main()

        assert exit_code == 1

    @patch("src.utils.check_api_health.test_api_endpoint")
    def test_endpoint_with_empty_response_data(self, mock_test):
        """测试空响应数据的端点"""
        endpoint = {
            "name": "空数据测试",
            "method": "POST",
            "url": "/api/test",
            "data": {},
            "auth_required": False,
            "priority": "P1",
            "page": "测试页面",
        }

        mock_response = Mock()
        mock_response.status_code = 200
        mock_test.return_value = (True, "成功", 200)

        with patch("requests.post", return_value=mock_response):
            success, message, status_code = api_health_module.test_api_endpoint(endpoint, None)
            assert success is True

    def test_endpoint_with_none_data(self):
        """测试data为None的端点"""
        endpoint = {
            "name": "None数据测试",
            "method": "GET",
            "url": "/api/test",
            "data": None,
            "auth_required": False,
            "priority": "P1",
            "page": "测试页面",
        }

        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            success, message, status_code = api_health_module.test_api_endpoint(endpoint, None)
            assert success is True


class TestIntegrationScenarios:
    """集成场景测试类"""

    @patch("builtins.print")
    def test_real_workflow_simulation(self, mock_print):
        """模拟真实工作流程"""
        with patch("src.utils.check_api_health.check_backend_running") as mock_check:
            with patch("src.utils.check_api_health.get_auth_token") as mock_token:
                with patch("src.utils.check_api_health.test_api_endpoint") as mock_test:
                    mock_check.return_value = True
                    mock_token.return_value = "real_token_12345"

                    def realistic_side_effect(endpoint, token):
                        if endpoint["priority"] == "P1":
                            if endpoint["name"] == "登录认证":
                                return (True, "成功", 200)
                            if endpoint["name"] == "TDX实时行情":
                                return (True, "成功", 200)
                            return (False, "数据源连接失败", 503)

                        return (
                            (True, "成功", 200)
                            if "系统" in endpoint["name"]
                            else (False, "功能未实现", 404)
                        )

                    mock_test.side_effect = realistic_side_effect

                    exit_code = main()

                    mock_check.assert_called_once()
                    mock_token.assert_called_once()
                    assert mock_test.call_count == len(API_ENDPOINTS)
                    assert exit_code == 1

                    print_calls = [str(call) for call in mock_print.call_args_list]
                    assert any("MyStocks Web API 健康检查" in call for call in print_calls)
                    assert any("测试结果汇总" in call for call in print_calls)

    def test_constants_consistency(self):
        """测试常量一致性"""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout("超时")

            endpoint = {
                "name": "超时测试",
                "method": "GET",
                "url": "/api/test",
                "data": None,
                "auth_required": False,
                "priority": "P1",
                "page": "测试页面",
            }

            success, message, status_code = api_health_module.test_api_endpoint(endpoint, None)

            assert success is False
            assert f">{TIMEOUT}s" in message
            mock_get.assert_called_once_with(f"{BASE_URL}/api/test", headers={}, timeout=TIMEOUT)
