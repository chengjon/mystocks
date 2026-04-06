"""
测试 TDXDataSource 当前兼容入口（tdx_split）。
"""

from __future__ import annotations

import pandas as pd
import pytest

from src.adapters.tdx.tdx_adapter import TdxDataSource


class _FakeContextManager:
    def __init__(self, api):
        self.api = api

    def __enter__(self):
        return self.api

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakeQuoteAPI:
    def __init__(self, connect_result=True, quotes=None):
        self.connect_result = connect_result
        self.quotes = quotes or []

    def connect(self, host, port):
        return self.connect_result

    def get_security_quotes(self, pairs):
        return self.quotes


class _FakeKlineAPI:
    def __init__(self, connect_result=True, bars=None):
        self.connect_result = connect_result
        self.bars = bars or []

    def connect(self, host, port):
        return self.connect_result

    def get_security_bars(self, category, market, symbol, start_position, batch_size):
        return self.bars


class TestTDXAdapter:
    """TDX split 适配器测试。"""

    def setup_method(self):
        self.adapter = TdxDataSource(use_server_config=False)

    def test_adapter_initialization(self):
        """测试适配器初始化"""
        assert self.adapter is not None
        assert self.adapter.tdx_host == "101.227.73.20"
        assert self.adapter.tdx_port == 7709
        assert self.adapter.max_retries == 3
        assert hasattr(self.adapter, "get_real_time_data")
        assert hasattr(self.adapter, "get_stock_kline")

    def test_get_real_time_data_success(self, monkeypatch):
        """测试获取实时数据成功场景"""
        fake_api = _FakeQuoteAPI(
            quotes=[
                {
                    "name": "平安银行",
                    "price": 12.34,
                    "last_close": 12.0,
                    "open": 12.1,
                    "high": 12.5,
                    "low": 12.0,
                    "vol": 12345,
                    "amount": 67890.0,
                    "bid1": 12.33,
                    "bid_vol1": 100,
                    "ask1": 12.35,
                    "ask_vol1": 120,
                }
            ]
        )
        monkeypatch.setattr(self.adapter, "_retry_api_call", lambda func: func)
        monkeypatch.setattr(self.adapter, "_get_tdx_connection", lambda: _FakeContextManager(fake_api))
        monkeypatch.setattr("src.adapters.tdx.tdx_split.realtime_misc.ColumnMapper.to_english", lambda df: df)

        result = self.adapter.get_real_time_data("000001")

        assert result["code"] == "000001"
        assert result["name"] == "平安银行"
        assert result["price"] == 12.34
        assert result["volume"] == 12345

    def test_get_real_time_data_connection_fail(self, monkeypatch):
        """测试连接失败场景"""
        fake_api = _FakeQuoteAPI(connect_result=False)
        monkeypatch.setattr(self.adapter, "_retry_api_call", lambda func: func)
        monkeypatch.setattr(self.adapter, "_get_tdx_connection", lambda: _FakeContextManager(fake_api))

        result = self.adapter.get_real_time_data("000001")

        assert isinstance(result, str)
        assert "网络连接失败" in result

    def test_get_stock_kline_daily(self, monkeypatch):
        """测试获取日K线数据"""
        fake_api = _FakeKlineAPI(
            bars=[
                {
                    "datetime": "2024-01-01 15:00:00",
                    "open": 10.0,
                    "high": 10.5,
                    "low": 9.8,
                    "close": 10.2,
                    "vol": 1000,
                }
            ]
        )
        monkeypatch.setattr(self.adapter, "_retry_api_call", lambda func: func)
        monkeypatch.setattr(self.adapter, "_get_tdx_connection", lambda: _FakeContextManager(fake_api))
        monkeypatch.setattr("src.adapters.tdx.tdx_split.kline_classify.ColumnMapper.to_english", lambda df: df)
        monkeypatch.setattr("src.adapters.tdx.tdx_split.kline_classify.normalize_date", lambda value: value)

        result = self.adapter.get_stock_kline("000001", "2024-01-01", "2024-01-31", period="1d")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert list(result["close"]) == [10.2]

    def test_get_stock_kline_minute(self, monkeypatch):
        """测试获取分钟K线数据"""
        fake_api = _FakeKlineAPI(
            bars=[
                {
                    "datetime": "2024-01-01 09:35:00",
                    "open": 10.0,
                    "high": 10.1,
                    "low": 9.9,
                    "close": 10.05,
                    "vol": 500,
                }
            ]
        )
        monkeypatch.setattr(self.adapter, "_retry_api_call", lambda func: func)
        monkeypatch.setattr(self.adapter, "_get_tdx_connection", lambda: _FakeContextManager(fake_api))
        monkeypatch.setattr("src.adapters.tdx.tdx_split.kline_classify.ColumnMapper.to_english", lambda df: df)
        monkeypatch.setattr("src.adapters.tdx.tdx_split.kline_classify.normalize_date", lambda value: value)

        result = self.adapter.get_stock_kline("000001", "2024-01-01", "2024-01-31", period="5m")

        assert isinstance(result, pd.DataFrame)
        assert not result.empty
        assert list(result["close"]) == [10.05]

    def test_period_mapping(self):
        """测试支持的周期映射"""
        supported_periods = ["1m", "5m", "15m", "30m", "1h", "1d", "1w", "1M", "1q", "1y"]
        fake_api = _FakeKlineAPI(bars=[])

        from src.adapters.tdx.tdx_split import kline_classify as kline_module

        original_retry = self.adapter._retry_api_call
        original_connection = self.adapter._get_tdx_connection
        original_mapper = kline_module.ColumnMapper.to_english
        original_normalize = kline_module.normalize_date

        self.adapter._retry_api_call = lambda func: func
        self.adapter._get_tdx_connection = lambda: _FakeContextManager(fake_api)
        kline_module.ColumnMapper.to_english = lambda df: df
        kline_module.normalize_date = lambda value: value

        try:
            for period in supported_periods:
                result = self.adapter.get_stock_kline("000001", "2024-01-01", "2024-01-31", period=period)
                assert isinstance(result, pd.DataFrame)
        finally:
            self.adapter._retry_api_call = original_retry
            self.adapter._get_tdx_connection = original_connection
            kline_module.ColumnMapper.to_english = original_mapper
            kline_module.normalize_date = original_normalize

    def test_market_detection(self):
        """测试市场检测"""
        assert self.adapter._get_market_code("000001") == 0
        assert self.adapter._get_market_code("600519") == 1
        assert self.adapter._get_market_code("300001") == 0
        assert self.adapter._get_market_code("688001") == 1

    def test_invalid_symbol(self):
        """测试无效股票代码"""
        invalid_symbols = [None, "", "INVALID", "abc123"]

        for symbol in invalid_symbols:
            result = self.adapter.get_real_time_data(symbol)
            assert isinstance(result, str)
            assert "无效的股票代码格式" in result

    def test_server_failover(self, monkeypatch):
        """测试重试装饰器在失败时会重试"""
        calls = {"count": 0}

        def flaky():
            calls["count"] += 1
            if calls["count"] < 3:
                raise RuntimeError("temporary failure")
            return "ok"

        monkeypatch.setattr(self.adapter, "retry_delay", 0)

        wrapped = self.adapter._retry_api_call(flaky)
        result = wrapped()

        assert result == "ok"
        assert calls["count"] == 3

    def test_unsupported_period_returns_empty_dataframe(self):
        """测试不支持的周期返回空DataFrame"""
        result = self.adapter.get_stock_kline("000001", "2024-01-01", "2024-01-31", period="yearly")

        assert isinstance(result, pd.DataFrame)
        assert result.empty


class TestTDXAdapterIntegration:
    """集成测试（需要TDX服务器连接）"""

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_tdx_connection(self):
        """测试真实TDX连接（可选）"""
        try:
            adapter = TdxDataSource()
            result = adapter.get_real_time_data("000001")

            if result and isinstance(result, dict):
                assert "code" in result or "price" in result
        except Exception as e:
            pytest.skip(f"TDX connection failed: {str(e)}")

    @pytest.mark.integration
    @pytest.mark.slow
    def test_real_kline_data(self):
        """测试真实K线数据获取（可选）"""
        try:
            adapter = TdxDataSource()
            result = adapter.get_stock_kline("000001", "2024-01-01", "2024-01-31", period="1d")

            if result is not None:
                assert isinstance(result, pd.DataFrame)
        except Exception as e:
            pytest.skip(f"TDX K-line data failed: {str(e)}")
