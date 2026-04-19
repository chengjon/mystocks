from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

import pytest

from app.api import realtime_mtm_init
from app.services.adapters.dashboard_adapter import DashboardDataSourceAdapter
from app.services.adapters.strategy_adapter import StrategyDataSourceAdapter
from app.services.adapters.watchlist_adapter import WatchlistDataSourceAdapter
from app.services.task_manager import TaskManager
from app.services.tdx_service import TdxService
from app.services.data_quality_monitor import AlertSeverity, DataQualityAlert, DataQualityMetric, DataQualityMonitor
from app.services.data_source_factory.data_source_factory import _log_unhealthy_data_source
from web.backend.tests._test_data_source_factory_support import HealthStatus, HealthStatusEnum


@pytest.mark.asyncio
async def test_data_quality_alert_logs_resolved_message(caplog):
    monitor = DataQualityMonitor()
    alert = DataQualityAlert(
        id="alert-1",
        metric_name="response_time",
        severity=AlertSeverity.ERROR,
        message="Response time breached 2000ms threshold",
        source="market",
    )

    with caplog.at_level("WARNING"):
        await monitor._trigger_alert(alert)

    assert "Response time breached 2000ms threshold" in caplog.text
    assert "{alert.message}" not in caplog.text


def test_log_unhealthy_data_source_expands_status_and_message():
    health = HealthStatus(
        status=HealthStatusEnum.DEGRADED,
        response_time=12.0,
        message="Fallback active",
        timestamp=datetime.now(),
    )

    with patch("app.services.data_source_factory.data_source_factory.logger.warning") as warning_mock:
        _log_unhealthy_data_source("market", health)

    warning_mock.assert_called_once_with("Data source '%s' is %s: %s", "market", "degraded", "Fallback active")


def test_data_quality_metric_treats_healthy_success_rate_as_info():
    metric = DataQualityMetric(
        name="success_rate",
        value=100.0,
        threshold_warning=95.0,
        threshold_error=90.0,
        threshold_critical=85.0,
        unit="%",
        description="请求成功率",
        higher_is_better=True,
    )

    assert metric.get_severity() == AlertSeverity.INFO


def test_data_quality_metric_treats_high_response_time_as_critical():
    metric = DataQualityMetric(
        name="response_time",
        value=2500.0,
        threshold_warning=500.0,
        threshold_error=1000.0,
        threshold_critical=2000.0,
        unit="ms",
        description="平均响应时间",
        higher_is_better=False,
    )

    assert metric.get_severity() == AlertSeverity.CRITICAL


def test_task_manager_register_function_logs_real_name(tmp_path):
    manager = TaskManager(log_dir=str(tmp_path))

    with patch("app.services.task_manager.logger.info") as info_mock:
        manager.register_function("sync_quotes", lambda _: None)

    info_mock.assert_called_once_with("Function registered: %s", "sync_quotes")


def test_tdx_service_logs_real_index_symbol():
    service = TdxService.__new__(TdxService)
    service.tdx_adapter = type(
        "StubAdapter",
        (),
        {"get_real_time_data": lambda self, symbol: {"price": 10.0, "pre_close": 9.5, "name": "指数"}},
    )()

    with patch("app.services.tdx_service.logger.info") as info_mock:
        result = service.get_index_quote("000001")

    assert result["symbol"] == "000001"
    info_mock.assert_called_once_with("获取指数行情成功: %s", "000001")


def test_realtime_mtm_database_session_logs_resolved_url():
    realtime_mtm_init._db_session = None
    realtime_mtm_init._engine = None

    fake_session = object()

    class FakeSettings:
        DATABASE_URL = "postgresql://user:pass@localhost/testdb"

    with (
        patch("web.backend.app.core.config.settings", FakeSettings()),
        patch("app.api.realtime_mtm_init.create_engine", return_value=object()),
        patch("app.api.realtime_mtm_init.sessionmaker", return_value=lambda: fake_session),
        patch("app.api.realtime_mtm_init.logger.info") as info_mock,
    ):
        session = realtime_mtm_init.get_database_session()

    assert session is fake_session
    info_mock.assert_called_once_with(
        "✅ Database session created",
        database_url="postgresql+psycopg2://user:pass@localhost/testdb",
    )


@pytest.mark.asyncio
async def test_watchlist_health_check_uses_lazy_service_getter():
    adapter = WatchlistDataSourceAdapter({"name": "watchlist", "mode": "real"})

    with (
        patch.object(adapter, "_get_watchlist_service") as get_service_mock,
        patch.object(adapter, "_get_mock_manager", return_value=None),
    ):
        get_service_mock.return_value = type(
            "WatchlistServiceStub",
            (),
            {"get_user_watchlist": lambda self, user_id: [{"symbol": "000001"}]},
        )()

        health = await adapter.health_check()

    assert health.status == HealthStatusEnum.HEALTHY
    assert "Watchlist data source is healthy" == health.message


@pytest.mark.asyncio
async def test_strategy_health_check_uses_lazy_service_getter():
    adapter = StrategyDataSourceAdapter({"name": "strategy", "mode": "real"})

    with (
        patch.object(adapter, "_get_strategy_service") as get_service_mock,
        patch.object(adapter, "_get_mock_manager", return_value=None),
    ):
        get_service_mock.return_value = type(
            "StrategyServiceStub",
            (),
            {"get_strategy_definitions": lambda self: [{"code": "demo"}]},
        )()

        health = await adapter.health_check()

    assert health.status == HealthStatusEnum.HEALTHY
    assert "Strategy data source is healthy" == health.message


@pytest.mark.asyncio
async def test_dashboard_health_check_treats_cold_start_as_healthy():
    adapter = DashboardDataSourceAdapter({"name": "dashboard"})

    health = await adapter.health_check()

    assert health.status == HealthStatusEnum.HEALTHY
    assert health.message == "Dashboard service is healthy (cold start)"
