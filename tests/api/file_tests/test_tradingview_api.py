"""
File-level route and model contract tests for tradingview.py.

这里对齐当前真实的 TradingView 配置端点与请求模型，
替换掉生成式占位断言。
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = ROOT / "web" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))


@pytest.fixture
def tradingview_module(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("POSTGRESQL_HOST", "localhost")
    monkeypatch.setenv("POSTGRESQL_USER", "postgres")
    monkeypatch.setenv("POSTGRESQL_PASSWORD", "password")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-secret-key")
    monkeypatch.setenv("BACKEND_PORT", "8020")
    monkeypatch.setenv("BACKEND_BACKUP_PORT", "8021")
    return importlib.import_module("app.api.tradingview")


class TestTradingviewAPIFile:
    @pytest.mark.file_test
    def test_router_registers_expected_tradingview_routes(self, tradingview_module):
        route_methods = {(route.path, tuple(sorted(route.methods or []))) for route in tradingview_module.router.routes}

        assert ("/chart/config", ("POST",)) in route_methods
        assert ("/mini-chart/config", ("POST",)) in route_methods
        assert ("/ticker-tape/config", ("POST",)) in route_methods
        assert ("/market-overview/config", ("GET",)) in route_methods
        assert ("/screener/config", ("GET",)) in route_methods
        assert ("/symbol/convert", ("GET",)) in route_methods

    @pytest.mark.file_test
    def test_router_contains_expected_number_of_routes(self, tradingview_module):
        route_pairs = [(route.path, tuple(sorted(route.methods or []))) for route in tradingview_module.router.routes]

        assert len(route_pairs) == 6
        assert len(route_pairs) == len(set(route_pairs))

    @pytest.mark.file_test
    def test_all_routes_use_plain_dict_response_model(self, tradingview_module):
        for route in tradingview_module.router.routes:
            assert route.response_model == tradingview_module.Dict

    @pytest.mark.file_test
    def test_route_names_remain_stable_for_core_operations(self, tradingview_module):
        route_names = {(route.path, tuple(sorted(route.methods or []))): route.name for route in tradingview_module.router.routes}

        assert route_names[("/chart/config", ("POST",))] == "get_chart_config"
        assert route_names[("/mini-chart/config", ("POST",))] == "get_mini_chart_config"
        assert route_names[("/ticker-tape/config", ("POST",))] == "get_ticker_tape_config"
        assert route_names[("/symbol/convert", ("GET",))] == "convert_symbol"

    @pytest.mark.file_test
    def test_chart_config_request_fields_and_defaults_are_stable(self, tradingview_module):
        fields = tradingview_module.ChartConfigRequest.model_fields

        assert set(fields) == {"symbol", "market", "interval", "theme", "locale", "container_id"}
        assert fields["market"].default == "CN"
        assert fields["interval"].default == "D"
        assert fields["theme"].default == "dark"
        assert fields["locale"].default == "zh_CN"
        assert fields["container_id"].default == "tradingview_chart"

    @pytest.mark.file_test
    def test_symbol_item_and_ticker_tape_models_expose_expected_fields(self, tradingview_module):
        symbol_fields = set(tradingview_module.SymbolItem.model_fields)
        tape_fields = tradingview_module.TickerTapeConfigRequest.model_fields

        assert symbol_fields == {"proName", "title"}
        assert set(tape_fields) == {"symbols", "theme", "locale", "container_id"}
        assert tape_fields["theme"].default == "dark"
        assert tape_fields["locale"].default == "zh_CN"
        assert tape_fields["container_id"].default == "tradingview_ticker_tape"

    @pytest.mark.file_test
    def test_router_exposes_three_post_and_three_get_routes(self, tradingview_module):
        methods = [tuple(sorted(route.methods or [])) for route in tradingview_module.router.routes]

        assert methods.count(("POST",)) == 3
        assert methods.count(("GET",)) == 3

    @pytest.mark.file_test
    def test_module_docstring_mentions_widgets_and_chart_config(self, tradingview_module):
        doc = tradingview_module.__doc__ or ""

        assert "TradingView Widget API" in doc
        assert "widgets" in doc

    @pytest.mark.file_test
    def test_docstrings_cover_chart_ticker_and_symbol_conversion(self, tradingview_module):
        assert "获取 TradingView 图表配置" in (tradingview_module.get_chart_config.__doc__ or "")
        assert "获取 TradingView Ticker Tape 配置" in (tradingview_module.get_ticker_tape_config.__doc__ or "")
        assert "将股票代码转换为 TradingView 格式" in (tradingview_module.convert_symbol.__doc__ or "")

    @pytest.mark.file_test
    def test_tradingview_routes_stay_under_single_namespace(self, tradingview_module):
        assert all(route.path.startswith("/") and "config" in route.path or route.path == "/symbol/convert" for route in tradingview_module.router.routes)
