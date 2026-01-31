"""
风险指标核心 API - V3.1

提供基础风险指标计算功能:
- VaR (Value at Risk) 计算
- CVaR (Conditional Value at Risk) 计算
- Beta 系数计算
- 风险仪表盘数据

Author: Claude Code
Version: 3.1.0
Date: 2026-01-10
"""

import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

import numpy as np
import pandas as pd
import structlog
from fastapi import APIRouter, HTTPException

logger = structlog.get_logger(__name__)

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.core import DataClassification  # noqa: E402
from src.monitoring.monitoring_database import MonitoringDatabase  # noqa: E402
from unified_manager import MyStocksUnifiedManager as UM  # noqa: E402,F401

try:
    from src.ml_strategy.backtest.risk_metrics import RiskMetrics

    RISK_METRICS_AVAILABLE = True
except ImportError:
    RISK_METRICS_AVAILABLE = False
    RiskMetrics = None

router = APIRouter(prefix="/api/v1/risk/core", tags=["风险指标核心"])

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
                    except Exception as e:
                        logger.debug("Monitoring log failed: %(e)s"")
                        return False

            monitoring_db = MonitoringAdapter(real_monitoring_db)
        except Exception as e:
            logger.warning("MonitoringDB init failed: %(e)s"")

            class MonitoringFallback:
                def log_operation(self, *args, **kwargs):
                    return True

            monitoring_db = MonitoringFallback()
    return monitoring_db


class RiskCalculator:
    @staticmethod
    def calculate_all(returns: pd.Series, confidence_level: float = 0.95) -> Dict[str, float]:
        if returns.empty:
            return {
                "var_95_hist": 0.0,
                "var_95_param": 0.0,
                "var_99_hist": 0.0,
                "cvar_95": 0.0,
                "cvar_99": 0.0,
            }

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


from app.schemas.risk_schemas import (  # noqa: E402
    BetaRequest,
    BetaResult,
    RiskDashboardResponse,
    VaRCVaRRequest,
    VaRCVaRResult,
)


@router.post("/var-cvar", response_model=VaRCVaRResult)
async def calculate_var_cvar(request: VaRCVaRRequest) -> VaRCVaRResult:
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()  # noqa: F821
        entity_type = request.entity_type
        entity_id = request.entity_id
        confidence_level = request.confidence_level

        from src.data_sources.factory import get_timeseries_source

        ts_source = get_timeseries_source(source_type="mock")
        ts_source.set_random_seed(42)

        start = datetime.now() - timedelta(days=365)
        end = datetime.now()
        kline = ts_source.get_kline_data(symbol="sh600000", start_time=start, end_time=end, interval="1d")
        if kline is not None and len(kline) > 1:
            returns = kline["close"].pct_change().dropna()
        else:
            returns = pd.Series(np.random.normal(0.001, 0.02, 252))

        metrics = RiskCalculator.calculate_all(returns)

        risk_data = pd.DataFrame(
            [
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "metric_date": datetime.now().date(),
                    "var_95_hist": metrics["var_95_hist"],
                    "var_95_param": metrics["var_95_param"],
                    "var_99_hist": metrics["var_99_hist"],
                    "cvar_95": metrics["cvar_95"],
                    "cvar_99": metrics["cvar_99"],
                    "created_at": datetime.now(),
                }
            ]
        )

        result = manager.save_data_by_classification(
            data=risk_data,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_metrics",
        )

        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="RISK_CALCULATION",
            table_name="risk_metrics",
            operation_name="calculate_var_cvar",
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result,
            details=f"entity_type={entity_type}, entity_id={entity_id}",
        )

        if not result:
            raise HTTPException(status_code=500, detail="保存风险指标失败")

        return VaRCVaRResult(
            var_95_hist=metrics["var_95_hist"],
            var_95_param=metrics["var_95_param"],
            var_99_hist=metrics["var_99_hist"],
            cvar_95=metrics["cvar_95"],
            cvar_99=metrics["cvar_99"],
            entity_type=entity_type,
            entity_id=entity_id,
            confidence_level=confidence_level,
        )

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="RISK_CALCULATION",
            table_name="risk_metrics",
            operation_name="calculate_var_cvar",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=f"计算VaR/CVaR失败: {str(e)}")


@router.post("/beta", response_model=BetaResult)
async def calculate_beta(request: BetaRequest) -> BetaResult:
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()  # noqa: F821
        entity_type = request.entity_type
        entity_id = request.entity_id
        market_index = request.market_index

        from src.data_sources.factory import get_timeseries_source

        ts_source = get_timeseries_source(source_type="mock")
        ts_source.set_random_seed(42)

        start = datetime.now() - timedelta(days=365)
        end = datetime.now()
        asset_kline = ts_source.get_kline_data(symbol="sh600000", start_time=start, end_time=end, interval="1d")
        if market_index == "000001":
            market_symbol = "sh000001"
        else:
            market_symbol = f"sz{market_index}" if len(market_index) == 6 else market_symbol
        market_kline = ts_source.get_kline_data(symbol=market_symbol, start_time=start, end_time=end, interval="1d")

        if asset_kline is not None and market_kline is not None and len(asset_kline) > 1 and len(market_kline) > 1:
            asset_returns = asset_kline["close"].pct_change().dropna()
            market_returns = market_kline["close"].pct_change().dropna()
        else:
            np.random.seed(42)
            asset_returns = pd.Series(np.random.normal(0.001, 0.02, 252))
            market_returns = pd.Series(np.random.normal(0.0008, 0.015, 252))

        beta = RiskCalculator.beta(asset_returns, market_returns)
        correlation = float(asset_returns.corr(market_returns))

        risk_data = pd.DataFrame(
            [
                {
                    "entity_type": entity_type,
                    "entity_id": entity_id,
                    "metric_date": datetime.now().date(),
                    "beta": beta,
                    "created_at": datetime.now(),
                }
            ]
        )

        result = manager.save_data_by_classification(
            data=risk_data,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_metrics",
            upsert=True,
        )

        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="RISK_CALCULATION",
            table_name="risk_metrics",
            operation_name="calculate_beta",
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result,
        )

        return BetaResult(
            beta=beta,
            correlation=correlation,
            entity_type=entity_type,
            entity_id=entity_id,
            market_index=market_index,
        )

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="RISK_CALCULATION",
            table_name="risk_metrics",
            operation_name="calculate_beta",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=f"计算Beta失败: {str(e)}")


@router.get("/dashboard", response_model=RiskDashboardResponse)
async def get_risk_dashboard() -> RiskDashboardResponse:
    try:
        manager = MyStocksUnifiedManager()  # noqa: F821

        metrics_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT, table_name="risk_metrics"
        )

        latest_metrics = None
        if metrics_df is not None and len(metrics_df) > 0:
            latest_metrics = metrics_df.sort_values("metric_date", ascending=False).iloc[0].to_dict()

        alerts_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            filters={"is_active": True},
        )

        active_alerts = alerts_df.to_dict("records") if alerts_df is not None else []

        thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
        history_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT, table_name="risk_metrics"
        )

        risk_history = []
        if history_df is not None:
            history_df = history_df[history_df["metric_date"] >= pd.Timestamp(thirty_days_ago)]
            risk_history = history_df.sort_values("metric_date").to_dict("records")

        return {
            "metrics": {
                "var_95_hist": (latest_metrics.get("var_95_hist") if latest_metrics else None),
                "cvar_95": latest_metrics.get("cvar_95") if latest_metrics else None,
                "beta": latest_metrics.get("beta") if latest_metrics else None,
            },
            "active_alerts": [
                {
                    "id": alert["id"],
                    "name": alert["name"],
                    "metric_type": alert["metric_type"],
                    "threshold_value": alert["threshold_value"],
                }
                for alert in active_alerts
            ],
            "risk_history": [
                {
                    "date": (metric["metric_date"]),
                    "var_95_hist": metric.get("var_95_hist"),
                    "cvar_95": metric.get("cvar_95"),
                    "beta": metric.get("beta"),
                }
                for metric in risk_history
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")


@router.get("/metrics/history")
async def get_risk_metrics_history(entity_type: str, entity_id: int, start_date: str, end_date: str):
    try:
        manager = MyStocksUnifiedManager()  # noqa: F821

        metrics_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_metrics",
            filters={"entity_type": entity_type, "entity_id": entity_id},
        )

        if metrics_df is None or len(metrics_df) == 0:
            return []

        metrics_df = metrics_df[
            (metrics_df["metric_date"] >= pd.Timestamp(start_date))
            & (metrics_df["metric_date"] <= pd.Timestamp(end_date))
        ]

        return [
            {
                "date": (metric["metric_date"]),
                "var_95_hist": metric.get("var_95_hist"),
                "var_95_param": metric.get("var_95_param"),
                "cvar_95": metric.get("cvar_95"),
                "beta": metric.get("beta"),
            }
            for metric in metrics_df.sort_values("metric_date").to_dict("records")
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取历史数据失败: {str(e)}")


@router.post("/metrics/calculate")
async def calculate_risk_metrics(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if RISK_METRICS_AVAILABLE and RiskMetrics:
            logger.info("使用主项目风险指标计算模块")

            equity_df = pd.DataFrame({"equity": request.get("equity_curve", [])})
            returns_series = pd.Series(request.get("returns", []))
            trades = request.get("trades", [])

            risk_calculator = RiskMetrics()
            metrics = risk_calculator.calculate_all_risk_metrics(
                equity_curve=equity_df,
                returns=returns_series,
                trades=trades,
                total_return=request.get("total_return", 0),
                max_drawdown=request.get("max_drawdown", 0),
                risk_free_rate=request.get("risk_free_rate", 0.03),
            )

            return {
                "status": "success",
                "metrics": metrics,
                "calculated_at": datetime.now().isoformat(),
                "module": "RiskMetrics (main project)",
            }
        else:
            logger.info("主项目风险指标模块不可用，返回简化指标")
            returns_series = pd.Series(request.get("returns", []))

            metrics = {
                "volatility": float(returns_series.std() * np.sqrt(252)) if len(returns_series) > 0 else 0,
                "sharpe_ratio": (
                    float((returns_series.mean() * 252) / (returns_series.std() * np.sqrt(252)))
                    if returns_series.std() > 0
                    else 0
                ),
                "max_drawdown": request.get("max_drawdown", 0),
                "skewness": float(returns_series.skew()) if len(returns_series) > 0 else 0,
                "kurtosis": float(returns_series.kurtosis()) if len(returns_series) > 0 else 0,
            }

            return {
                "status": "success",
                "metrics": metrics,
                "calculated_at": datetime.now().isoformat(),
                "module": "Simplified (fallback)",
            }

    except Exception as e:
        logger.error("计算风险指标失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"计算风险指标失败: {str(e)}")
