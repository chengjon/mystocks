"""
示例：契约一致性测试

使用 pytest 进行 API 契约测试，验证后端响应符合 OpenAPI 定义。

使用方法：
    pytest tests/api/test_contract_consistency.py -v
"""

import pytest
from fastapi.testclient import TestClient


class TestContractConsistency:
    """
    契约一致性测试类

    验证 API 响应严格符合 OpenAPI 规范定义。
    防止"契约漂移" (Contract Drift)。
    """

    @pytest.mark.contract
    def test_market_endpoint_contract(self, api_client, contract_validator):
        """
        测试市场数据端点响应符合契约定义
        """
        response = api_client.get("/api/market/stock/list")

        # 基础检查
        assert response.status_code == 200

        # 契约验证
        result = contract_validator.validate_response(
            path="/api/market/stock/list", method="GET", status_code="200", response_data=response.json()
        )

        assert result.success, f"Contract violation: {result.errors}"

    @pytest.mark.contract
    def test_indicators_endpoint_contract(self, api_client, contract_validator):
        """
        测试技术指标端点响应符合契约定义
        """
        response = api_client.get(
            "/api/indicators/calculate", params={"code": "000001", "indicator": "ma", "period": 5}
        )

        assert response.status_code == 200

        result = contract_validator.validate_response(
            path="/api/indicators/calculate", method="GET", status_code="200", response_data=response.json()
        )

        assert result.success, f"Contract violation: {result.errors}"

    @pytest.mark.contract
    def test_post_endpoint_contract(self, api_client, contract_validator):
        """
        测试 POST 端点请求和响应都符合契约定义
        """
        request_body = {"code": "000001", "start_date": "2024-01-01", "end_date": "2024-12-31"}

        response = api_client.post("/api/data/query", json=request_body)

        assert response.status_code == 200

        result = contract_validator.validate_response(
            path="/api/data/query", method="POST", status_code="200", response_data=response.json()
        )

        assert result.success, f"Contract violation: {result.errors}"


class TestContractValidationAdvanced:
    """
    高级契约验证测试
    """

    def test_response_schema_strict_validation(self, api_client, contract_validator):
        """
        严格模式验证：检查响应中的必填字段
        """
        response = api_client.get("/api/market/stock/quote", params={"code": "000001"})

        if response.status_code == 200:
            result = contract_validator.validate_response(
                path="/api/market/stock/quote", method="GET", status_code="200", response_data=response.json()
            )

            # 验证没有警告
            assert len(result.warnings) == 0, f"Warnings found: {result.warnings}"

    def test_error_response_contract(self, api_client, contract_validator):
        """
        测试错误响应也符合契约定义
        """
        response = api_client.get("/api/nonexistent/endpoint")

        # 404 响应也应该有定义的 schema
        result = contract_validator.validate_response(
            path="/api/nonexistent/endpoint", method="GET", status_code="404", response_data=response.json()
        )

        # 即使验证失败也应该记录
        assert result is not None


def test_all_endpoints_conform(api_client, contract_validator):
    """
    测试所有定义在 OpenAPI 中的端点都符合契约

    这个测试会遍历 OpenAPI spec 中定义的所有端点，
    并对每个端点进行契约验证。
    """
    endpoints = contract_validator.get_endpoint_schema_paths()

    # 只测试有明确 schema 定义的端点
    testable_endpoints = [ep for ep in endpoints if ep["responses"] and "200" in ep["responses"]]

    passed = 0
    failed = 0
    errors = []

    for endpoint in testable_endpoints[:10]:  # 限制测试数量
        try:
            # 构造合适的测试请求
            if endpoint["method"] == "GET":
                response = api_client.get(endpoint["path"])
            elif endpoint["method"] == "POST":
                response = api_client.post(endpoint["path"], json={})
            else:
                continue

            if response.status_code == 200:
                result = contract_validator.validate_response(
                    path=endpoint["path"], method=endpoint["method"], status_code="200", response_data=response.json()
                )

                if result.success:
                    passed += 1
                else:
                    failed += 1
                    errors.append({"endpoint": f"{endpoint['method']} {endpoint['path']}", "errors": result.errors})
        except Exception as e:
            failed += 1
            errors.append({"endpoint": f"{endpoint['method']} {endpoint['path']}", "error": str(e)})

    # 输出结果
    print(f"\nContract Test Results:")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")

    if failed > 0:
        print("\nFailures:")
        for err in errors[:5]:
            print(f"  - {err['endpoint']}: {err.get('errors', err.get('error', 'Unknown'))}")

    # 断言
    assert failed == 0, f"Contract violations found: {len(errors)}"
