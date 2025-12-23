"""
测试数据库服务模块

作者: Claude Code
创建时间: 2025-11-15
"""

import pytest
import unittest
from unittest.mock import Mock, patch
import pandas as pd
from src.database.database_service import DatabaseService


class TestDatabaseService(unittest.TestCase):
    """测试数据库服务类"""

    def setUp(self):
        """设置测试环境"""
        self.mock_postgresql_access = Mock()
        with patch(
            "src.database.database_service.PostgreSQLDataAccess"
        ) as MockPostgreSQLAccess:
            MockPostgreSQLAccess.return_value = self.mock_postgresql_access
            self.db_service = DatabaseService()

    def test_get_stock_list_empty_params(self):
        """测试获取股票列表 - 空参数"""
        # 模拟数据库返回空DataFrame
        mock_df_empty = pd.DataFrame(
            columns=["symbol", "name", "industry", "area", "market", "list_date"]
        )
        self.mock_postgresql_access.query.return_value = mock_df_empty

        result = self.db_service.get_stock_list()
        assert result == []

    def test_get_stock_list_with_data(self):
        """测试获取股票列表 - 有数据"""
        # 模拟数据库返回
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001", "600000"],
                "name": ["平安银行", "浦发银行"],
                "industry": ["银行", "银行"],
                "area": ["深圳", "上海"],
                "market": ["深交所", "上交所"],
                "list_date": [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-02")],
            }
        )

        # 模拟总数量查询
        mock_total_df = pd.DataFrame({"total": [2]})

        # 修复两次调用query方法
        def side_effect(table_name, **kwargs):
            if (
                "columns" in kwargs
                and kwargs["columns"]
                and "COUNT(*)" in kwargs["columns"][0]
            ):
                return mock_total_df
            else:
                return mock_df

        self.mock_postgresql_access.query.side_effect = side_effect

        result = self.db_service.get_stock_list({"limit": 20, "offset": 0})

        assert len(result) == 2
        assert result[0]["symbol"] == "000001"
        assert result[0]["name"] == "平安银行"
        assert result[0]["market"] == "深交所"
        assert result[0]["total"] == 2  # 每个结果都应该包含总数

    def test_get_stock_detail_with_code(self):
        """测试获取股票详情 - 有股票代码"""
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001"],
                "name": ["平安银行"],
                "industry": ["银行"],
                "area": ["深圳"],
                "market": ["深交所"],
                "list_date": [pd.Timestamp("2020-01-01")],
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        result = self.db_service.get_stock_detail("000001")
        assert result["symbol"] == "000001"
        assert result["name"] == "平安银行"

    def test_get_stock_detail_empty_code(self):
        """测试获取股票详情 - 空股票代码"""
        result = self.db_service.get_stock_detail("")
        assert result == {}

    def test_get_realtime_quotes_with_symbols(self):
        """测试获取实时行情 - 有股票列表"""
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001", "600000"],
                "name": ["平安银行", "浦发银行"],
                "price": [15.5, 12.3],
                "change": 0.5,
                "change_percent": 3.3,
                "volume": [1000000, 2000000],
                "amount": [15500000.0, 24600000.0],
                "open": [15.0, 12.0],
                "high": [15.8, 12.5],
                "low": [14.9, 11.9],
                "pre_close": [15.0, 12.0],
                "timestamp": [
                    pd.Timestamp("2025-01-01 10:00:00"),
                    pd.Timestamp("2025-01-01 10:00:00"),
                ],
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        result = self.db_service.get_realtime_quotes(["000001", "600000"])
        assert len(result) == 2
        assert result[0]["symbol"] == "000001"
        assert result[0]["price"] == 15.5

    def test_get_realtime_quotes_empty_symbols(self):
        """测试获取实时行情 - 空股票列表"""
        result = self.db_service.get_realtime_quotes([])
        assert result == []

    def test_execute_wencai_query(self):
        """测试执行问财查询"""
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001", "600000"],
                "name": ["平安银行", "浦发银行"],
                "price": [15.5, 12.3],
                "change_percent": [3.3, -1.2],
                "volume": [1000000, 2000000],
                "market_value": [1000000000.0, 2000000000.0],
                "pe_ratio": [8.5, 7.2],
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        query_params = {"query_name": "high_volume", "pages": 1}
        result = self.db_service.execute_wencai_query(query_params)

        assert result["query_name"] == "high_volume"
        assert result["total_records"] == 2
        assert len(result["records"]) == 2
        assert result["records"][0]["symbol"] == "000001"

    def test_get_technical_indicators_with_symbol(self):
        """测试获取技术指标 - 有股票代码"""
        mock_df = pd.DataFrame(
            {
                "date": [pd.Timestamp("2025-01-01")],
                "ma5": [15.5],
                "ma10": [15.2],
                "ma20": [15.0],
                "macd": [0.1],
                "rsi": [65.0],
                "kdj_k": [70.0],
                "atr": [0.5],
                "obv": [1000000.0],
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        result = self.db_service.get_technical_indicators("000001")
        assert result["symbol"] == "000001"
        assert "trend" in result
        assert "momentum" in result
        assert "volatility" in result
        assert "volume" in result

    def test_get_technical_indicators_empty_symbol(self):
        """测试获取技术指标 - 空股票代码"""
        result = self.db_service.get_technical_indicators("")
        assert result == {}

    def test_get_monitoring_alerts(self):
        """测试获取监控告警"""
        mock_df = pd.DataFrame(
            {
                "id": [1, 2],
                "symbol": ["000001", "600000"],
                "stock_name": ["平安银行", "浦发银行"],
                "alert_type": ["price_breakthrough", "volume_spike"],
                "level": ["high", "medium"],
                "message": ["价格突破", "成交量激增"],
                "timestamp": [
                    pd.Timestamp("2025-01-01 10:00:00"),
                    pd.Timestamp("2025-01-01 10:05:00"),
                ],
                "is_read": [False, True],
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        result = self.db_service.get_monitoring_alerts()
        assert len(result) == 2
        assert result[0]["symbol"] == "000001"
        assert result[0]["alert_type"] == "price_breakthrough"

    def test_get_monitoring_summary(self):
        """测试获取监控摘要"""
        result = self.db_service.get_monitoring_summary()
        assert "total_stocks" in result
        assert "limit_up_count" in result
        assert "limit_down_count" in result
        assert "strong_up_count" in result
        assert "strong_down_count" in result
        assert "avg_change_percent" in result
        assert "total_amount" in result
        assert "active_alerts" in result
        assert "unread_alerts" in result

    def test_get_trend_indicators(self):
        """测试获取趋势指标"""
        with patch.object(self.db_service, "get_technical_indicators") as mock_method:
            mock_method.return_value = {"symbol": "000001", "trend": {"ma5": 15.5}}
            result = self.db_service.get_trend_indicators("000001")
            assert result["symbol"] == "000001"
            mock_method.assert_called_once_with(
                {"symbol": "000001", "indicator_type": "trend"}
            )

    def test_get_momentum_indicators(self):
        """测试获取动量指标"""
        with patch.object(self.db_service, "get_technical_indicators") as mock_method:
            mock_method.return_value = {"symbol": "000001", "momentum": {"rsi": 65.0}}
            result = self.db_service.get_momentum_indicators("000001")
            assert result["symbol"] == "000001"
            mock_method.assert_called_once_with(
                {"symbol": "000001", "indicator_type": "momentum"}
            )

    def test_get_volatility_indicators(self):
        """测试获取波动率指标"""
        with patch.object(self.db_service, "get_technical_indicators") as mock_method:
            mock_method.return_value = {"symbol": "000001", "volatility": {"atr": 0.5}}
            result = self.db_service.get_volatility_indicators("000001")
            assert result["symbol"] == "000001"
            mock_method.assert_called_once_with(
                {"symbol": "000001", "indicator_type": "volatility"}
            )

    def test_get_volume_indicators(self):
        """测试获取成交量指标"""
        with patch.object(self.db_service, "get_technical_indicators") as mock_method:
            mock_method.return_value = {
                "symbol": "000001",
                "volume": {"obv": 1000000.0},
            }
            result = self.db_service.get_volume_indicators("000001")
            assert result["symbol"] == "000001"
            mock_method.assert_called_once_with(
                {"symbol": "000001", "indicator_type": "volume"}
            )

    def test_get_trading_signals(self):
        """测试获取交易信号"""
        mock_df = pd.DataFrame(
            {
                "symbol": ["000001"],
                "signal_type": ["buy"],
                "signal": "RSI_Oversold",
                "strength": 0.8,
                "created_at": [pd.Timestamp("2025-01-01 10:00:00")],
                "indicator": "RSI",
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        result = self.db_service.get_trading_signals("000001")
        assert result["symbol"] == "000001"
        assert result["signal_type"] == "buy"

    def test_get_stock_history(self):
        """测试获取股票历史数据"""
        mock_df = pd.DataFrame(
            {
                "date": [pd.Timestamp("2025-01-01"), pd.Timestamp("2025-01-02")],
                "open": [15.0, 15.5],
                "close": [15.5, 16.0],
                "high": [15.8, 16.2],
                "low": [14.9, 15.4],
                "volume": [1000000, 1200000],
                "change_percent": [3.3, 3.2],
            }
        )
        self.mock_postgresql_access.query.return_value = mock_df

        params = {"symbol": "000001", "period": "daily", "limit": 100}
        result = self.db_service.get_stock_history(params)
        assert result["symbol"] == "000001"
        assert result["period"] == "daily"
        assert len(result["dates"]) == 2
        assert len(result["data"]) == 2
        assert "change_percent" in result

    def test_get_batch_indicators(self):
        """测试批量获取技术指标"""
        with patch.object(self.db_service, "get_technical_indicators") as mock_method:
            mock_method.return_value = {"symbol": "000001", "trend": {"ma5": 15.5}}
            result = self.db_service.get_batch_indicators(["000001", "600000"])
            assert result["success"] is True
            assert result["count"] == 2
            assert len(result["data"]) == 2
            assert mock_method.call_count == 2  # 被调用两次，一次为每个股票


if __name__ == "__main__":
    pytest.main([__file__])
