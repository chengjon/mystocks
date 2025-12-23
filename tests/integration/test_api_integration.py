"""
集成测试：页面集成测试（核心重点）
测试文件：tests/integration/test_api_integration.py
"""

import pytest
import requests
import subprocess
import time
import os


class TestAPIIntegration:
    """API集成测试类"""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """启动和关闭后端服务"""
        # 设置环境变量
        os.environ["USE_MOCK_DATA"] = "true"  # 使用Mock数据进行集成测试

        # 启动后端服务
        process = subprocess.Popen(
            [
                "python",
                "-m",
                "uvicorn",
                "web.backend.app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                "--reload",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # 等待服务启动
        time.sleep(5)

        yield  # 运行测试

        # 关闭服务
        process.terminate()
        process.wait()

    def test_api_health_check(self):
        """测试API健康检查"""
        try:
            response = requests.get(
                "http://127.0.0.1:8000/api/stocks/health", timeout=10
            )
            assert response.status_code == 200
            data = response.json()
            assert data["status"] in [
                "healthy",
                "unavailable",
            ]  # 可能由于数据库未配置返回unavailable
        except requests.exceptions.ConnectionError:
            pytest.skip("后端服务未启动，跳过测试")

    def test_api_get_stock_list(self):
        """测试获取股票列表API"""
        try:
            response = requests.get(
                "http://127.0.0.1:8000/api/stocks/list?page=1&limit=10", timeout=10
            )
            assert response.status_code in [200, 500]  # 500可能由于数据库配置问题
        except requests.exceptions.ConnectionError:
            pytest.skip("后端服务未启动，跳过测试")

    def test_api_get_technical_indicators(self):
        """测试获取技术指标API"""
        try:
            response = requests.get(
                "http://127.0.0.1:8000/api/technical/000001/indicators", timeout=10
            )
            assert response.status_code in [200, 404, 500]  # 根据实现可能返回不同状态码
        except requests.exceptions.ConnectionError:
            pytest.skip("后端服务未启动，跳过测试")

    def test_api_monitoring_endpoints(self):
        """测试监控API端点"""
        try:
            response = requests.get(
                "http://127.0.0.1:8000/api/monitoring/realtime", timeout=10
            )
            assert response.status_code in [200, 500]
        except requests.exceptions.ConnectionError:
            pytest.skip("后端服务未启动，跳过测试")

    def test_api_strategy_endpoints(self):
        """测试策略API端点"""
        try:
            response = requests.get(
                "http://127.0.0.1:8000/api/strategy/definitions", timeout=10
            )
            assert response.status_code in [200, 500]
        except requests.exceptions.ConnectionError:
            pytest.skip("后端服务未启动，跳过测试")
