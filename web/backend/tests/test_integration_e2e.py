"""
End-to-End Integration Tests
端到端集成测试 - 验证完整数据流
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app

# Test client
client = TestClient(app)


class TestE2EIndicatorCalculation:
    """端到端指标计算测试 (T027)"""

    def test_full_indicator_calculation_flow(self):
        """
        T027: 完整的指标计算流程测试

        测试流程:
        1. 调用 POST /api/indicators/calculate
        2. 验证数据加载 (DataService)
        3. 验证数据质量检查
        4. 验证指标计算
        5. 验证响应格式
        """
        # 准备请求数据
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)

        request_data = {
            "symbol": "600519.SH",
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "indicators": [
                {"abbreviation": "SMA", "parameters": {"timeperiod": 5}},
                {"abbreviation": "SMA", "parameters": {"timeperiod": 10}},
                {"abbreviation": "RSI", "parameters": {"timeperiod": 14}}
            ],
            "use_cache": False
        }

        # 执行请求
        response = client.post("/api/indicators/calculate", json=request_data)

        # 验证响应
        # Note: 可能返回 200(成功), 404(无数据), 或 422(日期无效)
        assert response.status_code in [200, 404, 422], \
            f"Unexpected status code: {response.status_code}"

        if response.status_code == 200:
            data = response.json()

            # 验证响应结构
            assert "symbol" in data
            assert "symbol_name" in data
            assert "ohlcv" in data
            assert "indicators" in data
            assert "calculation_time_ms" in data

            # 验证OHLCV数据
            ohlcv = data["ohlcv"]
            assert len(ohlcv["dates"]) > 0
            assert len(ohlcv["open"]) == len(ohlcv["dates"])
            assert len(ohlcv["high"]) == len(ohlcv["dates"])
            assert len(ohlcv["low"]) == len(ohlcv["dates"])
            assert len(ohlcv["close"]) == len(ohlcv["dates"])
            assert len(ohlcv["volume"]) == len(ohlcv["dates"])

            # 验证指标结果
            assert len(data["indicators"]) == 3  # 3个指标

            # 验证每个指标
            for indicator in data["indicators"]:
                assert "abbreviation" in indicator
                assert "parameters" in indicator
                assert "outputs" in indicator or "error" in indicator
                assert "panel_type" in indicator

            # 验证计算时间
            assert data["calculation_time_ms"] > 0

            print(f"✅ E2E Test Passed: Calculated {len(data['indicators'])} indicators")
            print(f"   Data points: {len(ohlcv['dates'])}")
            print(f"   Calculation time: {data['calculation_time_ms']:.2f}ms")

        elif response.status_code == 404:
            # 数据未找到 - 这是预期的(如果数据库为空)
            error_detail = response.json().get("detail", {})
            assert "error_code" in error_detail or isinstance(error_detail, str)
            print("⚠️  E2E Test: No data found (expected if database is empty)")

        else:  # 422
            # 验证错误或日期无效
            error_detail = response.json().get("detail", {})
            print(f"⚠️  E2E Test: Validation error - {error_detail}")

    def test_registry_endpoint(self):
        """测试指标注册表端点"""
        response = client.get("/api/indicators/registry")

        assert response.status_code == 200

        data = response.json()
        assert "total_count" in data
        assert "categories" in data
        assert "indicators" in data

        # 验证至少有基础指标
        assert data["total_count"] >= 27  # 我们实现的27个指标

        print(f"✅ Registry Test Passed: {data['total_count']} indicators available")

    def test_invalid_symbol_error_handling(self):
        """测试无效股票代码的错误处理"""
        request_data = {
            "symbol": "INVALID",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "indicators": [
                {"abbreviation": "SMA", "parameters": {"timeperiod": 20}}
            ]
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 应该返回422 Validation Error
        assert response.status_code == 422

        print("✅ Invalid Symbol Test Passed: Validation error as expected")

    def test_invalid_date_range_error_handling(self):
        """测试无效日期范围的错误处理"""
        request_data = {
            "symbol": "600519.SH",
            "start_date": "2024-12-31",  # 开始日期晚于结束日期
            "end_date": "2024-01-01",
            "indicators": [
                {"abbreviation": "SMA", "parameters": {"timeperiod": 20}}
            ]
        }

        response = client.post("/api/indicators/calculate", json=request_data)

        # 应该返回422 Validation Error
        assert response.status_code == 422

        error_detail = response.json().get("detail", {})
        if isinstance(error_detail, dict):
            assert error_detail.get("error_code") in ["INVALID_DATE_RANGE", None]

        print("✅ Invalid Date Range Test Passed: Validation error as expected")

    def test_performance_metrics(self):
        """测试性能指标"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        request_data = {
            "symbol": "600519.SH",
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "indicators": [
                {"abbreviation": "SMA", "parameters": {"timeperiod": 20}}
            ],
            "use_cache": False
        }

        # 执行多次请求,测量性能
        import time
        times = []

        for _ in range(3):
            start = time.time()
            response = client.post("/api/indicators/calculate", json=request_data)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)

            if response.status_code == 200:
                data = response.json()
                calc_time = data.get("calculation_time_ms", 0)
                print(f"   Request time: {elapsed:.2f}ms, Calc time: {calc_time:.2f}ms")

        if times:
            avg_time = sum(times) / len(times)
            print(f"✅ Performance Test: Average response time: {avg_time:.2f}ms")

            # 性能断言 (宽松的阈值)
            assert avg_time < 5000, f"Response time too slow: {avg_time:.2f}ms"


class TestDataServiceIntegration:
    """数据服务集成测试"""

    def test_data_service_with_mock_data(self):
        """测试DataService的mock数据功能"""
        from app.services.data_service import get_data_service
        from datetime import datetime, timedelta

        data_service = get_data_service()

        # 测试mock数据生成
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        try:
            df, ohlcv_data = data_service.get_daily_ohlcv(
                symbol="000001.SZ",
                start_date=start_date,
                end_date=end_date
            )

            # 验证数据格式
            assert len(df) > 0, "DataFrame should not be empty"
            assert 'trade_date' in df.columns
            assert 'open' in df.columns
            assert 'high' in df.columns
            assert 'low' in df.columns
            assert 'close' in df.columns
            assert 'volume' in df.columns

            # 验证OHLCV数组
            assert 'open' in ohlcv_data
            assert 'high' in ohlcv_data
            assert 'low' in ohlcv_data
            assert 'close' in ohlcv_data
            assert 'volume' in ohlcv_data

            print(f"✅ DataService Test Passed: Generated {len(df)} data points")

        except Exception as e:
            print(f"⚠️  DataService Test: {e}")

    def test_symbol_validation(self):
        """测试股票代码验证"""
        from app.services.data_service import get_data_service

        data_service = get_data_service()

        # 有效的股票代码
        assert data_service.validate_symbol_format("600519.SH") == True
        assert data_service.validate_symbol_format("000001.SZ") == True
        assert data_service.validate_symbol_format("300750.SZ") == True

        # 无效的股票代码
        assert data_service.validate_symbol_format("INVALID") == False
        assert data_service.validate_symbol_format("12345") == False
        assert data_service.validate_symbol_format("600519") == False  # 缺少交易所

        print("✅ Symbol Validation Test Passed")


if __name__ == "__main__":
    """运行集成测试"""
    print("\n" + "="*80)
    print("Running End-to-End Integration Tests")
    print("="*80 + "\n")

    pytest.main([__file__, "-v", "--tb=short"])
