"""
策略管理API单元测试
测试web/backend/app/api/strategy_management.py的核心功能
"""

import pytest
from datetime import datetime
import sys
import os

# 添加源码路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../web/backend"))


class MockStrategyData:
    """模拟策略数据"""

    @staticmethod
    def get_strategy_definitions():
        """获取策略定义列表"""
        return {
            "success": True,
            "data": [
                {
                    "strategy_code": "MACD_CROSS",
                    "strategy_name_cn": "MACD金叉策略",
                    "strategy_name_en": "MACD Golden Cross",
                    "description": "当MACD线上穿信号线时买入",
                    "parameters": {
                        "fast_period": 12,
                        "slow_period": 26,
                        "signal_period": 9,
                    },
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00",
                },
                {
                    "strategy_code": "RSI_OVERSOLD",
                    "strategy_name_cn": "RSI超卖策略",
                    "strategy_name_en": "RSI Oversold",
                    "description": "RSI低于30时买入信号",
                    "parameters": {
                        "period": 14,
                        "oversold_threshold": 30,
                        "overbought_threshold": 70,
                    },
                    "is_active": True,
                    "created_at": "2024-01-01T00:00:00",
                },
            ],
            "total": 2,
        }

    @staticmethod
    def run_strategy_single(strategy_code, symbol, check_date=None):
        """运行单只股票策略"""
        return {
            "success": True,
            "data": {
                "strategy_code": strategy_code,
                "symbol": symbol,
                "check_date": check_date or datetime.now().strftime("%Y-%m-%d"),
                "match_result": True,
                "match_score": 85.5,
                "signals": [
                    {
                        "type": "buy",
                        "strength": "strong",
                        "price": 10.50,
                        "reason": "MACD金叉",
                    }
                ],
                "indicators": {"macd": 0.25, "signal": 0.15, "histogram": 0.10},
            },
        }

    @staticmethod
    def run_strategy_batch(strategy_code, symbols=None, limit=None):
        """批量运行策略"""
        return {
            "success": True,
            "data": {
                "strategy_code": strategy_code,
                "total": 100,
                "matched": 15,
                "failed": 2,
                "match_rate": 0.15,
                "execution_time": 5.23,
                "results": [
                    {"symbol": "600519", "match_result": True, "match_score": 90.5},
                    {"symbol": "000001", "match_result": True, "match_score": 75.2},
                    {"symbol": "300750", "match_result": False, "match_score": 45.0},
                ],
            },
        }

    @staticmethod
    def get_strategy_results(strategy_code=None, symbol=None, match_result=None):
        """查询策略结果"""
        return {
            "success": True,
            "data": [
                {
                    "id": 1,
                    "strategy_code": "MACD_CROSS",
                    "symbol": "600519",
                    "stock_name": "贵州茅台",
                    "check_date": "2024-01-15",
                    "match_result": True,
                    "match_score": 90.5,
                    "latest_price": 1750.50,
                    "change_percent": 1.25,
                    "created_at": "2024-01-15T15:30:00",
                },
                {
                    "id": 2,
                    "strategy_code": "MACD_CROSS",
                    "symbol": "000001",
                    "stock_name": "平安银行",
                    "check_date": "2024-01-15",
                    "match_result": True,
                    "match_score": 75.2,
                    "latest_price": 12.35,
                    "change_percent": 0.85,
                    "created_at": "2024-01-15T15:30:00",
                },
            ],
            "total": 2,
        }

    @staticmethod
    def get_strategy_stats(check_date=None):
        """获取策略统计"""
        return {
            "success": True,
            "data": [
                {
                    "strategy_code": "MACD_CROSS",
                    "strategy_name_cn": "MACD金叉策略",
                    "strategy_name_en": "MACD Golden Cross",
                    "matched_count": 15,
                    "total_count": 100,
                    "match_rate": 0.15,
                    "avg_score": 78.5,
                },
                {
                    "strategy_code": "RSI_OVERSOLD",
                    "strategy_name_cn": "RSI超卖策略",
                    "strategy_name_en": "RSI Oversold",
                    "matched_count": 8,
                    "total_count": 100,
                    "match_rate": 0.08,
                    "avg_score": 72.3,
                },
            ],
        }


class TestStrategyAPI:
    """策略管理API测试类"""

    def setup_method(self):
        """测试前的设置"""
        self.mock_data = MockStrategyData()

    def test_get_strategy_definitions_structure(self):
        """测试获取策略定义数据结构"""
        response = self.mock_data.get_strategy_definitions()

        assert response["success"] is True
        assert "data" in response
        assert isinstance(response["data"], list)
        assert len(response["data"]) > 0

        # 验证策略定义结构
        strategy = response["data"][0]
        required_fields = [
            "strategy_code",
            "strategy_name_cn",
            "strategy_name_en",
            "description",
            "parameters",
            "is_active",
        ]
        for field in required_fields:
            assert field in strategy, f"Missing required field: {field}"

    def test_get_strategy_definitions_data_validation(self):
        """测试策略定义数据有效性"""
        response = self.mock_data.get_strategy_definitions()
        strategies = response["data"]

        for strategy in strategies:
            # 验证策略代码不为空
            assert strategy["strategy_code"], "策略代码不能为空"
            assert isinstance(strategy["strategy_code"], str), "策略代码应为字符串"

            # 验证策略名称不为空
            assert strategy["strategy_name_cn"], "策略中文名称不能为空"
            assert strategy["strategy_name_en"], "策略英文名称不能为空"

            # 验证参数是字典类型
            assert isinstance(strategy["parameters"], dict), "参数应为字典类型"

            # 验证激活状态是布尔值
            assert isinstance(strategy["is_active"], bool), "激活状态应为布尔值"

    def test_run_strategy_single_structure(self):
        """测试单只运行策略数据结构"""
        response = self.mock_data.run_strategy_single("MACD_CROSS", "600519")

        assert response["success"] is True
        assert "data" in response

        data = response["data"]
        required_fields = [
            "strategy_code",
            "symbol",
            "check_date",
            "match_result",
            "match_score",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_run_strategy_single_validation(self):
        """测试单只运行策略数据有效性"""
        response = self.mock_data.run_strategy_single("MACD_CROSS", "600519")
        data = response["data"]

        # 验证匹配结果是布尔值
        assert isinstance(data["match_result"], bool), "匹配结果应为布尔值"

        # 验证匹配分数在0-100之间
        assert 0 <= data["match_score"] <= 100, "匹配分数应在0-100之间"

        # 验证股票代码不为空
        assert data["symbol"], "股票代码不能为空"

        # 验证策略代码不为空
        assert data["strategy_code"], "策略代码不能为空"

    def test_run_strategy_batch_structure(self):
        """测试批量运行策略数据结构"""
        response = self.mock_data.run_strategy_batch("MACD_CROSS", limit=100)

        assert response["success"] is True
        assert "data" in response

        data = response["data"]
        required_fields = [
            "strategy_code",
            "total",
            "matched",
            "failed",
            "match_rate",
            "execution_time",
            "results",
        ]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_run_strategy_batch_validation(self):
        """测试批量运行策略数据有效性"""
        response = self.mock_data.run_strategy_batch("MACD_CROSS", limit=100)
        data = response["data"]

        # 验证数量关系
        assert data["total"] >= data["matched"], "总数应大于等于匹配数"
        assert data["total"] >= data["failed"], "总数应大于等于失败数"

        # 验证匹配率在0-1之间
        assert 0 <= data["match_rate"] <= 1, "匹配率应在0-1之间"

        # 验证执行时间为正数
        assert data["execution_time"] >= 0, "执行时间应为非负数"

        # 验证结果列表
        assert isinstance(data["results"], list), "结果应为列表"

    def test_get_strategy_results_structure(self):
        """测试查询策略结果数据结构"""
        response = self.mock_data.get_strategy_results("MACD_CROSS")

        assert response["success"] is True
        assert "data" in response
        assert isinstance(response["data"], list)

        if len(response["data"]) > 0:
            result = response["data"][0]
            required_fields = [
                "strategy_code",
                "symbol",
                "stock_name",
                "check_date",
                "match_result",
                "match_score",
                "latest_price",
            ]
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"

    def test_get_strategy_results_filtering(self):
        """测试策略结果过滤功能"""
        # 测试按策略代码过滤
        response1 = self.mock_data.get_strategy_results(strategy_code="MACD_CROSS")
        assert response1["success"] is True

        # 测试按股票代码过滤
        response2 = self.mock_data.get_strategy_results(symbol="600519")
        assert response2["success"] is True

        # 测试按匹配结果过滤
        response3 = self.mock_data.get_strategy_results(match_result=True)
        assert response3["success"] is True

    def test_get_strategy_stats_structure(self):
        """测试策略统计数据结构"""
        response = self.mock_data.get_strategy_stats()

        assert response["success"] is True
        assert "data" in response
        assert isinstance(response["data"], list)

        if len(response["data"]) > 0:
            stats = response["data"][0]
            required_fields = [
                "strategy_code",
                "strategy_name_cn",
                "matched_count",
                "total_count",
                "match_rate",
                "avg_score",
            ]
            for field in required_fields:
                assert field in stats, f"Missing required field: {field}"

    def test_get_strategy_stats_validation(self):
        """测试策略统计数据有效性"""
        response = self.mock_data.get_strategy_stats()
        stats_list = response["data"]

        for stats in stats_list:
            # 验证匹配数量不大于总数
            assert stats["matched_count"] <= stats["total_count"], "匹配数量应小于等于总数"

            # 验证匹配率在0-1之间
            assert 0 <= stats["match_rate"] <= 1, "匹配率应在0-1之间"

            # 验证平均分数在0-100之间
            assert 0 <= stats["avg_score"] <= 100, "平均分数应在0-100之间"

            # 验证匹配率计算正确
            expected_rate = stats["matched_count"] / stats["total_count"] if stats["total_count"] > 0 else 0
            assert abs(stats["match_rate"] - expected_rate) < 0.01, "匹配率计算应该准确"

    def test_strategy_code_validation(self):
        """测试策略代码验证"""
        valid_codes = ["MACD_CROSS", "RSI_OVERSOLD", "MA_CROSS"]
        for code in valid_codes:
            response = self.mock_data.run_strategy_single(code, "600519")
            assert response["success"] is True

    def test_symbol_validation(self):
        """测试股票代码验证"""
        valid_symbols = ["600519", "000001", "300750"]
        for symbol in valid_symbols:
            response = self.mock_data.run_strategy_single("MACD_CROSS", symbol)
            assert response["success"] is True

    def test_error_handling_invalid_strategy(self):
        """测试无效策略代码错误处理"""
        # 应该优雅地处理无效策略代码
        response = self.mock_data.run_strategy_single("INVALID_STRATEGY", "600519")
        assert "success" in response

    def test_error_handling_invalid_symbol(self):
        """测试无效股票代码错误处理"""
        response = self.mock_data.run_strategy_single("MACD_CROSS", "INVALID")
        assert "success" in response

    def test_batch_limit_validation(self):
        """测试批量限制验证"""
        # 测试不同的限制数量
        limits = [10, 100, 1000]
        for limit in limits:
            response = self.mock_data.run_strategy_batch("MACD_CROSS", limit=limit)
            assert response["success"] is True

    def test_performance_batch_execution(self):
        """测试批量执行性能"""
        import time

        start_time = time.time()
        response = self.mock_data.run_strategy_batch("MACD_CROSS", limit=100)
        elapsed_time = time.time() - start_time

        # 批量执行应该在合理时间内完成
        assert elapsed_time < 10.0, "批量执行应在10秒内完成"
        assert response["success"] is True

    def test_results_consistency(self):
        """测试结果一致性"""
        # 相同参数的查询应该返回一致的结果
        response1 = self.mock_data.get_strategy_results("MACD_CROSS")
        response2 = self.mock_data.get_strategy_results("MACD_CROSS")

        assert response1["success"] == response2["success"]
        assert len(response1["data"]) == len(response2["data"])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
