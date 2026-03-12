from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd


def test_health_check_reads_nested_registry_config_fields() -> None:
    with patch("dotenv.load_dotenv", return_value=True):
        from src.core.data_source.base import DataSourceManagerV2

    manager = DataSourceManagerV2.__new__(DataSourceManagerV2)
    manager.registry = {
        "demo.endpoint": {
            "config": {
                "status": "active",
                "success_rate": 88.0,
                "health_status": "unknown",
            },
            "handler": None,
            "cache": None,
            "last_call": None,
            "call_count": 0,
        }
    }

    result = manager.health_check()

    assert result["total"] == 1
    assert result["healthy"] == 1
    assert result["unhealthy"] == 0
    assert result["details"]["demo.endpoint"]["enabled"] is True
    assert result["details"]["demo.endpoint"]["health_score"] == 88.0
    assert result["details"]["demo.endpoint"]["healthy"] is True


def test_tdx_data_source_can_initialize_and_delegate_market_calendar(
) -> None:
    with patch("dotenv.load_dotenv", return_value=True):
        from src.adapters.tdx.tdx_data_source import TdxDataSource

    expected = pd.DataFrame({"date": ["2024-01-02"], "is_trading_day": [True], "market": ["CN"]})

    with patch("src.adapters.tdx.tdx_data_source.BaseTdxAdapter.__init__", return_value=None), patch(
        "src.adapters.tdx.tdx_data_source.KlineDataService"
    ) as mock_kline_service, patch("src.adapters.tdx.tdx_data_source.RealtimeService") as mock_realtime_service:
        mock_kline_service.return_value.get_market_calendar.return_value = expected

        adapter = TdxDataSource()
        adapter._connection = None
        result = adapter.get_market_calendar("2024-01-01", "2024-01-31")

        assert adapter.kline_service is mock_kline_service.return_value
        assert adapter.realtime_service is mock_realtime_service.return_value
        mock_kline_service.return_value.get_market_calendar.assert_called_once_with("2024-01-01", "2024-01-31")
        pd.testing.assert_frame_equal(result, expected)


@patch("src.adapters.financial.financial_data_source.FinancialReportAdapter")
@patch("src.adapters.financial.financial_data_source.StockDailyAdapter")
def test_financial_data_source_keeps_availability_flags_after_init(
    mock_stock_daily_adapter: MagicMock,
    mock_financial_report_adapter: MagicMock,
) -> None:
    stock_daily = MagicMock()
    financial_report = MagicMock()
    mock_stock_daily_adapter.return_value = stock_daily
    mock_financial_report_adapter.return_value = financial_report

    with patch("dotenv.load_dotenv", return_value=True):
        from src.adapters.financial.financial_data_source import FinancialDataSource

    adapter = FinancialDataSource()
    status = adapter.get_data_source_status()

    stock_daily._check_dependency_availability.assert_called_once_with()
    financial_report._check_dependency_availability.assert_called_once_with()
    assert adapter._stock_daily_available is True
    assert adapter._financial_reports_available is True
    assert status["stock_daily_adapter"]["available"] is True
    assert status["financial_report_adapter"]["available"] is True



def test_load_from_yaml_uses_endpoint_name_as_canonical_key(tmp_path) -> None:
    with patch("dotenv.load_dotenv", return_value=True):
        from src.core.data_source.registry import _load_from_yaml

    yaml_path = tmp_path / "registry.yaml"
    yaml_path.write_text(
        """
        data_sources:
          alias_name:
            endpoint_name: canonical.endpoint
            source_name: demo
            status: active
        """
    )

    class Dummy:
        yaml_config_path = str(yaml_path)

    result = _load_from_yaml(Dummy())

    assert "canonical.endpoint" in result
    assert "alias_name" not in result
    assert result["canonical.endpoint"]["endpoint_name"] == "canonical.endpoint"
    assert result["canonical.endpoint"]["_loaded_from"] == "yaml"


def test_merge_sources_does_not_duplicate_yaml_alias_endpoint() -> None:
    with patch("dotenv.load_dotenv", return_value=True):
        from src.core.data_source.registry import _merge_sources

    db_sources = {
        "canonical.endpoint": {
            "endpoint_name": "canonical.endpoint",
            "status": "active",
            "description": "db version",
            "_loaded_from": "database",
        }
    }
    yaml_sources = {
        "alias_name": {
            "endpoint_name": "canonical.endpoint",
            "status": "active",
            "description": "yaml version",
            "test_parameters": {"symbol": "000001"},
            "_loaded_from": "yaml",
        }
    }

    class Dummy:
        pass

    result = _merge_sources(Dummy(), db_sources, yaml_sources)

    assert list(result.keys()) == ["canonical.endpoint"]
    assert result["canonical.endpoint"]["description"] == "yaml version"
    assert result["canonical.endpoint"]["test_parameters"] == {"symbol": "000001"}
