import os
import sys
from typing import Dict

import numpy as np
import pandas as pd
import structlog


logger = structlog.get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.schemas.risk_schemas import (
    BetaRequest,
    BetaResult,
    NotificationTestRequest,
    NotificationTestResponse,
    RiskAlertCreate,
    RiskAlertResponse,
    RiskAlertUpdate,
    RiskDashboardResponse,
    VaRCVaRRequest,
    VaRCVaRResult,
)
from src.core import DataClassification, MyStocksUnifiedManager
from src.monitoring.monitoring_database import MonitoringDatabase

try:
    from src.ml_strategy.automation.notification_manager import (
        NotificationChannel,
        NotificationLevel,
        NotificationManager,
    )
except ImportError:
    NotificationManager = None
    NotificationChannel = None
    NotificationLevel = None

try:
    from src.governance.risk_management import (
        get_risk_management_core,
        initialize_risk_management_system,
    )

    RISK_MANAGEMENT_V31_AVAILABLE = True
except ImportError:
    RISK_MANAGEMENT_V31_AVAILABLE = False
    get_risk_management_core = None
    initialize_risk_management_system = None

try:
    from src.governance.risk_management.services.alert_rule_engine import (
        AlertContext,
        get_alert_rule_engine,
    )
    from src.governance.risk_management.services.risk_alert_notification_manager import (
        get_risk_alert_notification_manager,
    )
    from src.governance.risk_management.services.stop_loss_execution_service import (
        get_stop_loss_execution_service,
    )
    from src.governance.risk_management.services.stop_loss_history_service import (
        get_stop_loss_history_service,
    )

    ENHANCED_RISK_FEATURES_AVAILABLE = True
except ImportError:
    ENHANCED_RISK_FEATURES_AVAILABLE = False
    get_stop_loss_execution_service = None
    get_stop_loss_history_service = None
    get_risk_alert_notification_manager = None
    get_alert_rule_engine = None
    AlertContext = None


class RiskCalculator:
    """VaR, CVaR, Beta calculation utilities."""

    @staticmethod
    def calculate_all(returns: pd.Series, confidence_level: float = 0.95) -> Dict[str, float]:
        if returns.empty:
            return {"var_95_hist": 0.0, "var_95_param": 0.0, "var_99_hist": 0.0, "cvar_95": 0.0, "cvar_99": 0.0}

        var_95_hist = float(np.percentile(returns, (1 - confidence_level) * 100))
        var_99_hist = float(np.percentile(returns, 1))
        mean = returns.mean()
        std = returns.std()
        var_95_param = float(mean - 1.645 * std)
        cvar_95 = float(returns[returns <= var_95_hist].mean())
        cvar_99 = float(returns[returns <= var_99_hist].mean())

        return {
            "var_95_hist": var_95_hist,
            "var_95_param": var_95_param,
            "var_99_hist": var_99_hist,
            "cvar_95": cvar_95 if not np.isnan(cvar_95) else 0.0,
            "cvar_99": cvar_99 if not np.isnan(cvar_99) else 0.0,
        }

    @staticmethod
    def beta(asset_returns: pd.Series, market_returns: pd.Series) -> float:
        if asset_returns.empty or market_returns.empty:
            return 0.0
        min_len = min(len(asset_returns), len(market_returns))
        asset = asset_returns.iloc[:min_len]
        market = market_returns.iloc[:min_len]
        covariance = np.cov(asset, market)[0][1]
        market_variance = np.var(market)
        if market_variance == 0:
            return 0.0
        return float(covariance / market_variance)


try:
    from src.ml_strategy.backtest.risk_metrics import RiskMetrics

    RISK_METRICS_AVAILABLE = True
except ImportError:
    RISK_METRICS_AVAILABLE = False
    RiskMetrics = None

monitoring_db = None


def get_monitoring_db():
    global monitoring_db
    if monitoring_db is None:
        try:
            real_monitoring_db = MonitoringDatabase()

            class MonitoringAdapter:
                def __init__(self, real_db):
                    self.real_db = real_db

                def log_operation(
                    self,
                    operation_type="UNKNOWN",
                    table_name=None,
                    operation_name=None,
                    rows_affected=0,
                    operation_time_ms=0,
                    success=True,
                    details="",
                    **kwargs,
                ):
                    try:
                        return self.real_db.log_operation(
                            operation_type=operation_type,
                            classification="DERIVED_DATA",
                            target_database="PostgreSQL",
                            table_name=table_name,
                            record_count=rows_affected,
                            operation_status="SUCCESS" if success else "FAILED",
                            error_message=None if success else details,
                            execution_time_ms=int(operation_time_ms),
                            additional_info=(
                                {"operation_name": operation_name, "details": details}
                                if operation_name or details
                                else None
                            ),
                        )
                    except Exception:
                        logger.debug("Monitoring log failed (non-critical)")
                        return False

            monitoring_db = MonitoringAdapter(real_monitoring_db)

        except Exception:
            logger.warning("MonitoringDatabase initialization failed, using fallback")

            class MonitoringFallback:
                def log_operation(self, *args, **kwargs):
                    return True

            monitoring_db = MonitoringFallback()
    return monitoring_db


__all__ = [
    "AlertContext",
    "BetaRequest",
    "BetaResult",
    "DataClassification",
    "ENHANCED_RISK_FEATURES_AVAILABLE",
    "MyStocksUnifiedManager",
    "NotificationManager",
    "NotificationTestRequest",
    "NotificationTestResponse",
    "RISK_MANAGEMENT_V31_AVAILABLE",
    "RISK_METRICS_AVAILABLE",
    "RiskAlertCreate",
    "RiskAlertResponse",
    "RiskAlertUpdate",
    "RiskCalculator",
    "RiskDashboardResponse",
    "RiskMetrics",
    "VaRCVaRRequest",
    "VaRCVaRResult",
    "get_alert_rule_engine",
    "get_monitoring_db",
    "get_risk_alert_notification_manager",
    "get_risk_management_core",
    "get_stop_loss_execution_service",
    "get_stop_loss_history_service",
    "logger",
]
