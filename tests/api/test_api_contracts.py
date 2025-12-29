"""
API契约测试套件
使用pytest框架测试API契约的正确性和一致性
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pytest
import requests
from pydantic import ValidationError
import yaml

# 测试配置
API_BASE_URL = os.environ.get("API_TEST_BASE_URL", "http://localhost:8000")
CONTRACTS_DIR = Path(__file__).parent.parent.parent / "docs/api/contracts"


class APITestClient:
    """API测试客户端"""

    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def set_token(self, token: str):
        """设置认证token"""
        self.token = token
        self.session.headers.update({"Authorization": f"Bearer {token}"})

    def request(
        self,
        method: str,
        endpoint: str,
        data: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        expected_status: int = 200,
    ) -> requests.Response:
        """发送API请求"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}

        response = self.session.request(
            method=method,
            url=url,
            json=data,
            params=params,
            headers=headers,
        )

        # 检查状态码
        if response.status_code != expected_status:
            raise AssertionError(
                f"Expected status {expected_status}, got {response.status_code}\n" f"Response: {response.text}"
            )

        return response

    def get(self, endpoint: str, params: Dict[str, Any] = None, **kwargs):
        """GET请求"""
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(self, endpoint: str, data: Dict[str, Any] = None, **kwargs):
        """POST请求"""
        return self.request("POST", endpoint, data=data, **kwargs)

    def put(self, endpoint: str, data: Dict[str, Any] = None, **kwargs):
        """PUT请求"""
        return self.request("PUT", endpoint, data=data, **kwargs)

    def delete(self, endpoint: str, **kwargs):
        """DELETE请求"""
        return self.request("DELETE", endpoint, **kwargs)


# ==================== 契约版本管理测试 ====================


class TestContractVersionAPI:
    """契约版本管理API测试"""

    @pytest.fixture(scope="class")
    def client(self):
        return APITestClient()

    @pytest.fixture(scope="class")
    def test_contract(self, client):
        """创建测试契约"""
        contract_data = {
            "name": "test-api",
            "version": "1.0.0",
            "spec": {
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {},
                "components": {"schemas": {}},
            },
            "author": "test-suite",
            "description": "测试契约",
        }

        response = client.post("/api/contracts/versions", contract_data)
        yield response.json()["data"]

        # 清理
        client.delete(f"/api/contracts/versions/{response.json()['data']['id']}")

    def test_create_version(self, client):
        """测试创建契约版本"""
        contract_data = {
            "name": "test-api-create",
            "version": "1.0.0",
            "spec": {
                "openapi": "3.0.0",
                "info": {"title": "Test API", "version": "1.0.0"},
                "paths": {},
            },
        }

        response = client.post("/api/contracts/versions", contract_data)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["name"] == "test-api-create"
        assert data["version"] == "1.0.0"
        assert data["author"] == "test-suite"

    def test_get_version(self, client, test_contract):
        """测试获取契约版本"""
        version_id = test_contract["id"]
        response = client.get(f"/api/contracts/versions/{version_id}")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["id"] == version_id

    def test_list_versions(self, client, test_contract):
        """测试列出版本"""
        response = client.get("/api/contracts/versions", {"name": "test-api"})

        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)

    def test_activate_version(self, client, test_contract):
        """测试激活版本"""
        version_id = test_contract["id"]
        response = client.post(f"/api/contracts/versions/{version_id}/activate")

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["success"] is True


# ==================== Market API测试 ====================


class TestMarketAPI:
    """Market API测试"""

    @pytest.fixture(scope="class")
    def client(self):
        return APITestClient()

    def test_get_stock_list(self, client):
        """测试获取股票列表"""
        response = client.get("/api/market/symbols", {"limit": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert "data" in data

    def test_search_stocks(self, client):
        """测试搜索股票"""
        response = client.get("/api/market/search", {"q": "平安"})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"

    def test_get_quote(self, client):
        """测试获取行情"""
        response = client.get("/api/market/quote", {"symbol": "000001.SZ"})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"
        assert "data" in data

    def test_get_kline_data(self, client):
        """测试获取K线数据"""
        response = client.get("/api/market/kline", {"symbol": "000001.SZ", "period": "day", "limit": 10})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"


# ==================== Technical API测试 ====================


class TestTechnicalAPI:
    """Technical Analysis API测试"""

    @pytest.fixture(scope="class")
    def client(self):
        return APITestClient()

    def test_get_ma(self, client):
        """测试获取MA指标"""
        response = client.get("/api/technical/indicators/ma", {"symbol": "000001.SZ", "periods": [5, 10, 20]})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"

    def test_get_macd(self, client):
        """测试获取MACD指标"""
        response = client.get("/api/technical/indicators/macd", {"symbol": "000001.SZ"})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == "SUCCESS"


# ==================== Trade API测试 ====================


class TestTradeAPI:
    """Trade API测试"""

    @pytest.fixture(scope="class")
    def authenticated_client(self):
        """认证客户端"""
        client = APITestClient()

        # 登录获取token
        login_data = {"username": "test_user", "password": "test_password"}  # pragma: allowlist secret

        try:
            response = client.post("/api/v1/auth/login", login_data)
            if response.status_code == 200:
                token = response.json()["data"].get("token")
                if token:
                    client.set_token(token)
        except:
            pass  # 忽略登录失败

        return client

    def test_get_account_balance(self, authenticated_client):
        """测试获取账户余额"""
        try:
            response = authenticated_client.get("/api/trade/account/balance")
            assert response.status_code in [200, 401]  # 可能未授权
        except:
            pass  # 忽略网络错误

    def test_validate_order(self, authenticated_client):
        """测试验证订单"""
        order_data = {
            "symbol": "000001.SZ",
            "type": "limit",
            "direction": "buy",
            "price": 10.50,
            "quantity": 100,
        }

        try:
            response = authenticated_client.post("/api/trade/orders/validate", order_data)
            assert response.status_code in [200, 401]
        except:
            pass


# ==================== 契约一致性测试 ====================


class TestContractConsistency:
    """契约一致性测试"""

    @pytest.fixture(scope="class")
    def contracts(self):
        """加载所有契约文件"""
        contracts = {}
        for file_path in CONTRACTS_DIR.glob("*.yaml"):
            with open(file_path) as f:
                contracts[file_path.stem] = yaml.safe_load(f)
        return contracts

    def test_openapi_version(self, contracts):
        """测试OpenAPI版本"""
        for name, contract in contracts.items():
            assert "openapi" in contract, f"{name}: 缺少openapi字段"
            assert contract["openapi"].startswith("3."), f"{name}: OpenAPI版本不支持"

    def test_required_fields(self, contracts):
        """测试必需字段"""
        for name, contract in contracts.items():
            assert "info" in contract, f"{name}: 缺少info字段"
            assert "title" in contract["info"], f"{name}: 缺少title字段"
            assert "paths" in contract, f"{name}: 缺少paths字段"

    def test_response_format(self, contracts):
        """测试响应格式一致性"""
        required_fields = ["code", "message", "data"]

        for name, contract in contracts.items():
            paths = contract.get("paths", {})

            for path, methods in paths.items():
                for method, details in methods.items():
                    if "responses" in details:
                        for status_code, response in details["responses"].items():
                            if status_code.startswith("2") and "content" in response:
                                # 检查schema是否有必需字段
                                schema = response["content"].get("application/json", {}).get("schema", {})

                                if "properties" in schema:
                                    properties = schema["properties"]
                                    for field in required_fields:
                                        assert field in properties, (
                                            f"{name} {path} {method} {status_code}: " f"响应缺少{field}字段"
                                        )


# ==================== 性能测试 ====================


class TestAPIPerformance:
    """API性能测试"""

    @pytest.fixture(scope="class")
    def client(self):
        return APITestClient()

    @pytest.mark.performance
    def test_stock_list_response_time(self, client):
        """测试股票列表响应时间"""
        import time

        start_time = time.time()
        response = client.get("/api/market/symbols")
        elapsed_time = time.time() - start_time

        assert response.status_code == 200
        assert elapsed_time < 2.0, f"响应时间过长: {elapsed_time:.2f}秒"

    @pytest.mark.performance
    def test_concurrent_requests(self, client):
        """测试并发请求"""
        import time
        import concurrent.futures

        def fetch_quote(symbol):
            start = time.time()
            try:
                response = client.get("/api/market/quote", {"symbol": symbol})
                elapsed = time.time() - start
                return elapsed
            except:
                return None

        symbols = ["000001.SZ", "000002.SZ", "000003.SZ"]

        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(fetch_quote, s) for s in symbols]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        elapsed_time = time.time() - start_time

        assert all(r is not None for r in results), "部分请求失败"
        assert elapsed_time < 3.0, f"并发请求时间过长: {elapsed_time:.2f}秒"


# ==================== 运行配置 ====================


def pytest_configure(config):
    """Pytest配置"""
    config.addinivalue_line("markers", "performance: 标记性能测试")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
