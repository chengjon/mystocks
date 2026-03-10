from __future__ import annotations

import importlib
import importlib.util
import sys
from pathlib import Path
from types import ModuleType

LINE_LIMIT = 850


def _line_count(path: str) -> int:
    with open(path, "r", encoding="utf-8") as file:
        return sum(1 for _ in file)


def _load_api_package_module(dotted_name: str):
    package_paths = {
        "app": Path("web/backend/app"),
        "app.api": Path("web/backend/app/api"),
    }
    previous = {name: sys.modules.get(name) for name in package_paths}
    previous[dotted_name] = sys.modules.get(dotted_name)
    original_keys = set(sys.modules)

    for package_name, package_path in package_paths.items():
        fake_package = ModuleType(package_name)
        fake_package.__path__ = [str(package_path.resolve())]
        sys.modules[package_name] = fake_package

    module = importlib.import_module(dotted_name)
    new_keys = {name for name in sys.modules if name not in original_keys}

    for name in new_keys:
        sys.modules.pop(name, None)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def _load_stock_search_package_module(dotted_name: str):
    package_paths = {
        "app": Path("web/backend/app"),
        "app.services": Path("web/backend/app/services"),
        "app.services.stock_search_service": Path("web/backend/app/services/stock_search_service"),
    }
    previous = {name: sys.modules.get(name) for name in package_paths}
    previous[dotted_name] = sys.modules.get(dotted_name)
    original_keys = set(sys.modules)

    for package_name, package_path in package_paths.items():
        fake_package = ModuleType(package_name)
        fake_package.__path__ = [str(package_path.resolve())]
        sys.modules[package_name] = fake_package

    module = importlib.import_module(dotted_name)
    new_keys = {name for name in sys.modules if name not in original_keys}

    for name in new_keys:
        sys.modules.pop(name, None)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def _load_backup_security_support_module():
    module_path = Path("web/backend/app/api/backup_recovery_secure/backup_security_support.py")
    module_name = "test_backup_security_support_split_regressions_module"

    fake_app = ModuleType("app")
    fake_core = ModuleType("app.core")
    fake_security = ModuleType("app.core.security")
    fake_models = ModuleType("app.models")
    fake_backup_schemas = ModuleType("app.models.backup_schemas")

    class FakeUser:
        id = 1
        username = "tester"
        role = "admin"

    fake_security.User = FakeUser
    fake_backup_schemas.require_admin_role = lambda role: role == "admin"
    fake_backup_schemas.require_backup_permission = lambda role: role in {"admin", "operator"}
    fake_backup_schemas.require_recovery_permission = lambda role: role == "admin"

    previous = {
        "app": sys.modules.get("app"),
        "app.core": sys.modules.get("app.core"),
        "app.core.security": sys.modules.get("app.core.security"),
        "app.models": sys.modules.get("app.models"),
        "app.models.backup_schemas": sys.modules.get("app.models.backup_schemas"),
        module_name: sys.modules.get(module_name),
    }

    sys.modules["app"] = fake_app
    sys.modules["app.core"] = fake_core
    sys.modules["app.core.security"] = fake_security
    sys.modules["app.models"] = fake_models
    sys.modules["app.models.backup_schemas"] = fake_backup_schemas

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def _load_operation_metrics_split_module():
    package_name = "src.monitoring.monitoring_service"
    module_name = "test_operation_metrics_split_regressions_module"
    module_paths = {
        "src.monitoring.monitoring_service._operation_metric_models": Path(
            "src/monitoring/monitoring_service/_operation_metric_models.py"
        ),
        "src.monitoring.monitoring_service._monitoring_database": Path(
            "src/monitoring/monitoring_service/_monitoring_database.py"
        ),
        "src.monitoring.monitoring_service._data_quality_monitor": Path(
            "src/monitoring/monitoring_service/_data_quality_monitor.py"
        ),
        "src.monitoring.monitoring_service._performance_monitor": Path(
            "src/monitoring/monitoring_service/_performance_monitor.py"
        ),
    }

    fake_package = ModuleType(package_name)
    fake_package.__path__ = []

    previous = {
        package_name: sys.modules.get(package_name),
        module_name: sys.modules.get(module_name),
    }
    for dotted_name in module_paths:
        previous[dotted_name] = sys.modules.get(dotted_name)

    sys.modules[package_name] = fake_package

    for dotted_name, module_path in module_paths.items():
        spec = importlib.util.spec_from_file_location(dotted_name, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        sys.modules[dotted_name] = module
        spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, Path("src/monitoring/monitoring_service/operation_metrics.py"))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def _load_turning_point_split_module():
    package_name = "src.advanced_analysis.timeseries_analyzer"
    module_name = "src.advanced_analysis.timeseries_analyzer.turning_point"
    module_paths = {
        "src.advanced_analysis.timeseries_analyzer._turning_point_models": Path(
            "src/advanced_analysis/timeseries_analyzer/_turning_point_models.py"
        ),
        "src.advanced_analysis.timeseries_analyzer._turning_point_detection": Path(
            "src/advanced_analysis/timeseries_analyzer/_turning_point_detection.py"
        ),
        "src.advanced_analysis.timeseries_analyzer._turning_point_pattern_analysis": Path(
            "src/advanced_analysis/timeseries_analyzer/_turning_point_pattern_analysis.py"
        ),
        "src.advanced_analysis.timeseries_analyzer._turning_point_reporting": Path(
            "src/advanced_analysis/timeseries_analyzer/_turning_point_reporting.py"
        ),
        "src.advanced_analysis.timeseries_analyzer._assess_ts_risk": Path(
            "src/advanced_analysis/timeseries_analyzer/_assess_ts_risk.py"
        ),
    }

    fake_src = ModuleType("src")
    fake_src.__path__ = []
    fake_advanced_analysis = ModuleType("src.advanced_analysis")
    fake_advanced_analysis.__path__ = []
    fake_package = ModuleType(package_name)
    fake_package.__path__ = []

    class FakeAnalysisResult:
        pass

    class FakeAnalysisType:
        TIME_SERIES = "time_series"

    class FakeBaseAnalyzer:
        pass

    fake_advanced_analysis.AnalysisResult = FakeAnalysisResult
    fake_advanced_analysis.AnalysisType = FakeAnalysisType
    fake_advanced_analysis.BaseAnalyzer = FakeBaseAnalyzer
    fake_src.advanced_analysis = fake_advanced_analysis
    fake_advanced_analysis.timeseries_analyzer = fake_package

    previous = {
        "src": sys.modules.get("src"),
        "src.advanced_analysis": sys.modules.get("src.advanced_analysis"),
        package_name: sys.modules.get(package_name),
        module_name: sys.modules.get(module_name),
    }
    for dotted_name in module_paths:
        previous[dotted_name] = sys.modules.get(dotted_name)

    sys.modules["src"] = fake_src
    sys.modules["src.advanced_analysis"] = fake_advanced_analysis
    sys.modules[package_name] = fake_package

    for dotted_name, module_path in module_paths.items():
        spec = importlib.util.spec_from_file_location(dotted_name, module_path)
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        sys.modules[dotted_name] = module
        spec.loader.exec_module(module)

    spec = importlib.util.spec_from_file_location(module_name, Path("src/advanced_analysis/timeseries_analyzer/turning_point.py"))
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    for name, previous_module in previous.items():
        if previous_module is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous_module

    return module


def test_dashboard_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/dashboard.py") < LINE_LIMIT


def test_notification_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/notification.py") < LINE_LIMIT


def test_advanced_backtest_engine_stays_below_850_lines():
    assert _line_count("src/backtesting/advanced_backtest_engine.py") < LINE_LIMIT


def test_market_panorama_analyzer_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/market_panorama_analyzer.py") < LINE_LIMIT


def test_capital_flow_cluster_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/capital_flow_analyzer/capital_flow_cluster.py") < LINE_LIMIT


def test_sentiment_score_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/sentiment_analyzer/sentiment_score.py") < LINE_LIMIT


def test_technical_signal_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/technical_analyzer/technical_signal.py") < LINE_LIMIT


def test_trading_signal_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/trading_signals_analyzer/trading_signal.py") < LINE_LIMIT


def test_chip_concentration_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/chip_distribution_analyzer/chip_concentration.py") < LINE_LIMIT


def test_fundamental_analyzer_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/fundamental_analyzer.py") < LINE_LIMIT


def test_efinance_data_source_stays_below_850_lines():
    assert _line_count("src/interfaces/adapters/efinance_adapter/efinance_data_source.py") < LINE_LIMIT


def test_check_use_mock_data_stays_below_850_lines():
    assert _line_count("src/routes/stocks_routes/check_use_mock_data.py") < LINE_LIMIT


def test_tdengine_access_module_stays_below_300_lines():
    assert _line_count("src/data_access/tdengine_access.py") < 300


def test_tdengine_access_split_helpers_remain_importable():
    importlib.import_module("src.data_access._tdengine_validation")
    importlib.import_module("src.data_access._tdengine_write_operations")
    importlib.import_module("src.data_access._tdengine_query_operations")
    module = importlib.import_module("src.data_access.tdengine_access")

    assert callable(module.TDengineDataAccess)
    assert callable(module.validate_identifier)
    assert callable(module.validate_symbol)
    assert callable(module.TDengineDataAccess.save_data)
    assert callable(module.TDengineDataAccess.query_latest)
    assert callable(module.TDengineDataAccess.create_stable)


def test_backup_security_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/backup_recovery_secure/log_security_event.py") < LINE_LIMIT


def test_stock_search_service_module_stays_below_850_lines():
    assert _line_count("web/backend/app/services/stock_search_service/stock_search_service.py") < LINE_LIMIT


def test_stock_search_service_split_module_stays_below_300_lines():
    assert _line_count("web/backend/app/services/stock_search_service/stock_search_service.py") < 300


def test_stock_search_service_split_helpers_remain_importable():
    _load_stock_search_package_module("app.services.stock_search_service._stock_search_finnhub")
    _load_stock_search_package_module("app.services.stock_search_service._stock_search_cn")
    _load_stock_search_package_module("app.services.stock_search_service._stock_search_hk")
    module = _load_stock_search_package_module("app.services.stock_search_service.stock_search_service")

    assert callable(module.StockSearchService)
    assert callable(module.get_stock_search_service)
    assert callable(module.StockSearchService.search_stocks)
    assert callable(module.StockSearchService.get_a_stock_kline)
    assert callable(module.StockSearchService.search_hk_stocks)


def test_tasks_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/tasks.py") < LINE_LIMIT


def test_indicator_cache_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/indicators/indicator_cache.py") < LINE_LIMIT


def test_strategy_management_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/strategy_management/get_monitoring_db.py") < LINE_LIMIT


def test_market_data_request_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/market/market_data_request.py") < LINE_LIMIT


def test_stock_search_result_module_stays_below_850_lines():
    assert _line_count("web/backend/app/api/stock_search/stock_search_result.py") < LINE_LIMIT


def test_cache_api_split_module_stays_below_120_lines():
    assert _line_count("web/backend/app/api/cache.py") < 120


def test_cache_api_split_helpers_remain_importable():
    _load_api_package_module("app.api._cache_basic_routes")
    _load_api_package_module("app.api._cache_eviction_routes")
    _load_api_package_module("app.api._cache_prewarming_routes")
    module = _load_api_package_module("app.api.cache")

    assert module.router is not None


def test_mock_stock_list_module_stays_below_850_lines():
    assert _line_count("src/mock/mock_stocks/get_stock_list.py") < LINE_LIMIT


def test_mock_stock_list_exports_remain_available():
    module = importlib.import_module("src.mock.mock_stocks.get_stock_list")

    assert callable(module.get_stock_list)
    assert callable(module.get_real_time_quote)
    assert callable(module.get_stock_detail)
    assert callable(module.search_stocks)


def test_mock_market_module_stays_below_850_lines():
    assert _line_count("src/mock/mock_market/_generate_realistic_stock_price.py") < LINE_LIMIT


def test_mock_market_exports_remain_available():
    module = importlib.import_module("src.mock.mock_market._generate_realistic_stock_price")

    assert callable(module.get_market_heatmap)
    assert callable(module.get_real_time_quotes)
    assert callable(module.get_fund_flow)
    assert callable(module.get_stock_list)


def test_operation_metrics_module_stays_below_850_lines():
    assert _line_count("src/monitoring/monitoring_service/operation_metrics.py") < LINE_LIMIT


def test_operation_metrics_exports_remain_available():
    module = _load_operation_metrics_split_module()

    assert callable(module.OperationMetrics)
    assert callable(module.MonitoringDatabase)
    assert callable(module.DataQualityMonitor)
    assert callable(module.PerformanceMonitor)


def test_turning_point_module_stays_below_850_lines():
    assert _line_count("src/advanced_analysis/timeseries_analyzer/turning_point.py") < LINE_LIMIT


def test_turning_point_exports_remain_available():
    module = _load_turning_point_split_module()

    assert callable(module.TurningPoint)
    assert callable(module.TimeSeriesSegment)
    assert callable(module.PatternMatch)
    assert callable(module.TimeSeriesAnalyzer)
    assert callable(module._detect_turning_points)
    assert callable(module._perform_pattern_matching)
    assert callable(module._generate_ts_recommendations)


def test_ai_alert_manager_module_stays_below_300_lines():
    assert _line_count("src/monitoring/ai_alert_manager.py") < 300


def test_ai_alert_manager_split_helpers_remain_importable():
    importlib.import_module("src.monitoring._ai_alert_models")
    importlib.import_module("src.monitoring._ai_alert_handlers")
    importlib.import_module("src.monitoring._ai_alert_manager_core")
    module = importlib.import_module("src.monitoring.ai_alert_manager")

    assert callable(module.AIAlertManager)
    assert callable(module.get_ai_alert_manager)
    assert callable(module.AlertRule)
    assert callable(module.Alert)
    assert callable(module.SystemMetrics)


def test_ai_alert_manager_source_contains_no_print_statements():
    source = Path("src/monitoring/ai_alert_manager.py").read_text(encoding="utf-8")

    assert "print(" not in source


def test_dashboard_module_remains_importable():
    module = _load_api_package_module("app.api.dashboard")

    assert module.router is not None


def test_notification_module_remains_importable():
    module = _load_api_package_module("app.api.notification")

    assert module.router is not None


def test_backup_security_support_remains_importable():
    module = _load_backup_security_support_module()

    assert callable(module.log_security_event)
