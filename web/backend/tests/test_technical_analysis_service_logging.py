import pandas as pd

from app.services.technical_analysis_service import (
    TechnicalAnalysisService,
    _normalize_history_period,
)


def test_get_stock_history_logs_real_symbol_and_error(monkeypatch, caplog):
    service = TechnicalAnalysisService()

    class _BrokenAkshare:
        @staticmethod
        def stock_zh_a_hist(**_kwargs):
            raise RuntimeError("upstream unavailable")

    monkeypatch.setattr("app.services.technical_analysis_service._get_akshare_module", lambda _feature: _BrokenAkshare)

    with caplog.at_level("ERROR"):
        result = service.get_stock_history("600519")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert "600519" in caplog.text
    assert "upstream unavailable" in caplog.text


def test_get_stock_history_logs_transient_upstream_disconnect_as_warning(monkeypatch, caplog):
    service = TechnicalAnalysisService()

    class _TransientAkshare:
        @staticmethod
        def stock_zh_a_hist(**_kwargs):
            raise ConnectionError("Connection aborted. Remote end closed connection without response")

    monkeypatch.setattr(
        "app.services.technical_analysis_service._get_akshare_module",
        lambda _feature: _TransientAkshare,
    )

    with caplog.at_level("WARNING"):
        result = service.get_stock_history("000001")

    assert isinstance(result, pd.DataFrame)
    assert result.empty
    assert "000001" in caplog.text
    assert "Remote end closed connection" in caplog.text
    assert not [record for record in caplog.records if record.levelname == "ERROR"]


def test_normalize_history_period_maps_window_alias_to_daily_range():
    normalized_period, start_date, end_date = _normalize_history_period("1y", None, "2026-04-17")

    assert normalized_period == "daily"
    assert start_date == "2025-04-17"
    assert end_date == "2026-04-17"


def test_get_stock_history_uses_normalized_period_and_dates(monkeypatch):
    service = TechnicalAnalysisService()
    captured: dict[str, str] = {}

    class _AkshareRecorder:
        @staticmethod
        def stock_zh_a_hist(**kwargs):
            captured.update(kwargs)
            return pd.DataFrame(
                {
                    "日期": ["2026-04-16", "2026-04-17"],
                    "开盘": [10.0, 10.5],
                    "收盘": [10.2, 10.8],
                    "最高": [10.4, 10.9],
                    "最低": [9.9, 10.2],
                    "成交量": [1000, 1200],
                    "成交额": [10000, 12000],
                }
            )

    monkeypatch.setattr(
        "app.services.technical_analysis_service._get_akshare_module",
        lambda _feature: _AkshareRecorder,
    )

    service._cache.clear()
    result = service.get_stock_history("600519", period="3m", end_date="2026-04-17")

    assert not result.empty
    assert captured["period"] == "daily"
    assert captured["start_date"] == "20260117"
    assert captured["end_date"] == "20260417"


def test_calculate_trend_indicators_skips_warning_for_empty_dataframe(caplog):
    service = TechnicalAnalysisService()

    with caplog.at_level("WARNING"):
        result = service.calculate_trend_indicators(pd.DataFrame())

    assert result == {}
    assert "Insufficient data for trend indicators" not in caplog.text
