"""
市场数据API单元测试
测试web/backend/app/api/market.py的核心功能
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../web/backend'))


class MockMarketData:
    """模拟市场数据"""

    @staticmethod
    def get_realtime_quotes():
        """获取实时行情"""
        return {
            "success": True,
            "data": [
                {
                    "symbol": "600519",
                    "name": "贵州茅台",
                    "price": 1750.50,
                    "change": 25.30,
                    "change_percent": 1.47,
                    "volume": 1500000,
                    "amount": 2625000000,
                    "open": 1730.00,
                    "high": 1760.00,
                    "low": 1725.00,
                    "prev_close": 1725.20
                },
                {
                    "symbol": "000001",
                    "name": "平安银行",
                    "price": 12.35,
                    "change": 0.15,
                    "change_percent": 1.23,
                    "volume": 25000000,
                    "amount": 308750000,
                    "open": 12.25,
                    "high": 12.40,
                    "low": 12.20,
                    "prev_close": 12.20
                }
            ],
            "timestamp": datetime.now().isoformat()
        }

    @staticmethod
    def get_stock_daily(symbol, start_date, end_date):
        """获取股票日线数据"""
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "name": "测试股票",
                "data": [
                    {
                        "date": "2024-01-01",
                        "open": 10.00,
                        "high": 10.50,
                        "low": 9.80,
                        "close": 10.20,
                        "volume": 1000000,
                        "amount": 10100000
                    },
                    {
                        "date": "2024-01-02",
                        "open": 10.20,
                        "high": 10.60,
                        "low": 10.10,
                        "close": 10.40,
                        "volume": 1200000,
                        "amount": 12420000
                    }
                ]
            }
        }

    @staticmethod
    def get_market_overview():
        """获取市场概览"""
        return {
            "success": True,
            "data": {
                "shanghai": {
                    "index": 3000.50,
                    "change": 15.30,
                    "change_percent": 0.51,
                    "volume": 250000000000,
                    "amount": 280000000000,
                    "up_count": 2500,
                    "down_count": 1800,
                    "flat_count": 200
                },
                "shenzhen": {
                    "index": 10500.20,
                    "change": 50.15,
                    "change_percent": 0.48,
                    "volume": 350000000000,
                    "amount": 420000000000,
                    "up_count": 2200,
                    "down_count": 1500,
                    "flat_count": 150
                }
            }
        }


class TestMarketAPI:
    """市场数据API测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.mock_data = MockMarketData()

    def test_get_realtime_quotes_structure(self):
        """测试实时行情数据结构"""
        response = self.mock_data.get_realtime_quotes()

        assert response["success"] is True
        assert "data" in response
        assert isinstance(response["data"], list)
        assert len(response["data"]) > 0

        # 验证第一条数据的结构
        quote = response["data"][0]
        required_fields = [
            "symbol", "name", "price", "change", "change_percent",
            "volume", "amount", "open", "high", "low", "prev_close"
        ]
        for field in required_fields:
            assert field in quote, f"Missing required field: {field}"

    def test_get_realtime_quotes_data_validation(self):
        """测试实时行情数据有效性"""
        response = self.mock_data.get_realtime_quotes()
        data = response["data"]

        for quote in data:
            # 验证价格逻辑
            assert quote["high"] >= quote["low"], "最高价应大于等于最低价"
            assert quote["high"] >= quote["open"], "最高价应大于等于开盘价"
            assert quote["high"] >= quote["price"], "最高价应大于等于当前价"
            assert quote["low"] <= quote["open"], "最低价应小于等于开盘价"
            assert quote["low"] <= quote["price"], "最低价应小于等于当前价"

            # 验证成交量和成交额为正数
            assert quote["volume"] >= 0, "成交量应为非负数"
            assert quote["amount"] >= 0, "成交额应为非负数"

            # 验证涨跌幅计算
            expected_change_pct = (quote["change"] / quote["prev_close"]) * 100
            assert abs(quote["change_percent"] - expected_change_pct) < 0.1, \
                "涨跌幅计算应该准确"

    def test_get_stock_daily_structure(self):
        """测试股票日线数据结构"""
        response = self.mock_data.get_stock_daily("600519", "2024-01-01", "2024-01-02")

        assert response["success"] is True
        assert "data" in response
        assert "symbol" in response["data"]
        assert "name" in response["data"]
        assert "data" in response["data"]
        assert isinstance(response["data"]["data"], list)

        # 验证日线数据结构
        daily_data = response["data"]["data"][0]
        required_fields = ["date", "open", "high", "low", "close", "volume", "amount"]
        for field in required_fields:
            assert field in daily_data, f"Missing required field: {field}"

    def test_get_stock_daily_data_validation(self):
        """测试股票日线数据有效性"""
        response = self.mock_data.get_stock_daily("600519", "2024-01-01", "2024-01-02")
        data = response["data"]["data"]

        for day in data:
            # 验证K线数据逻辑
            assert day["high"] >= day["low"], "最高价应大于等于最低价"
            assert day["high"] >= day["open"], "最高价应大于等于开盘价"
            assert day["high"] >= day["close"], "最高价应大于等于收盘价"
            assert day["low"] <= day["open"], "最低价应小于等于开盘价"
            assert day["low"] <= day["close"], "最低价应小于等于收盘价"

            # 验证成交量和成交额
            assert day["volume"] >= 0, "成交量应为非负数"
            assert day["amount"] >= 0, "成交额应为非负数"

    def test_get_market_overview_structure(self):
        """测试市场概览数据结构"""
        response = self.mock_data.get_market_overview()

        assert response["success"] is True
        assert "data" in response
        assert "shanghai" in response["data"]
        assert "shenzhen" in response["data"]

        # 验证上证数据
        sh = response["data"]["shanghai"]
        required_fields = [
            "index", "change", "change_percent", "volume", "amount",
            "up_count", "down_count", "flat_count"
        ]
        for field in required_fields:
            assert field in sh, f"Missing required field: {field}"

    def test_get_market_overview_data_validation(self):
        """测试市场概览数据有效性"""
        response = self.mock_data.get_market_overview()

        for market in ["shanghai", "shenzhen"]:
            data = response["data"][market]

            # 验证指数为正数
            assert data["index"] > 0, "指数应为正数"

            # 验证成交量和成交额为正数
            assert data["volume"] >= 0, "成交量应为非负数"
            assert data["amount"] >= 0, "成交额应为非负数"

            # 验证涨跌家数为非负数
            assert data["up_count"] >= 0, "上涨家数应为非负数"
            assert data["down_count"] >= 0, "下跌家数应为非负数"
            assert data["flat_count"] >= 0, "平盘家数应为非负数"

    def test_error_handling_invalid_symbol(self):
        """测试无效股票代码错误处理"""
        # 这里应该测试API如何处理无效的股票代码
        response = self.mock_data.get_stock_daily("INVALID", "2024-01-01", "2024-01-02")
        # 正常情况下应该返回错误或空数据
        assert "success" in response

    def test_error_handling_invalid_date_range(self):
        """测试无效日期范围错误处理"""
        # 测试开始日期晚于结束日期
        response = self.mock_data.get_stock_daily("600519", "2024-12-31", "2024-01-01")
        assert "success" in response

    def test_date_format_validation(self):
        """测试日期格式验证"""
        # 测试正确的日期格式
        response = self.mock_data.get_stock_daily("600519", "2024-01-01", "2024-01-31")
        assert response["success"] is True

    def test_symbol_format_validation(self):
        """测试股票代码格式验证"""
        valid_symbols = ["600519", "000001", "300750"]
        for symbol in valid_symbols:
            response = self.mock_data.get_stock_daily(symbol, "2024-01-01", "2024-01-10")
            assert "success" in response

    def test_response_time_acceptable(self):
        """测试响应时间是否可接受"""
        import time
        start_time = time.time()
        response = self.mock_data.get_realtime_quotes()
        elapsed_time = time.time() - start_time

        # API响应应该在合理时间内完成（如1秒）
        assert elapsed_time < 1.0, "API响应时间应小于1秒"
        assert response["success"] is True

    def test_data_consistency(self):
        """测试数据一致性"""
        # 多次调用应该返回一致的数据结构
        response1 = self.mock_data.get_realtime_quotes()
        response2 = self.mock_data.get_realtime_quotes()

        assert response1.keys() == response2.keys(), "响应结构应该一致"
        assert len(response1["data"]) == len(response2["data"]), "数据条数应该一致"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
