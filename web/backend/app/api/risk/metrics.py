from datetime import datetime, timedelta
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from fastapi import APIRouter

from app.api.risk._shared import (
    RISK_METRICS_AVAILABLE,
    BetaRequest,
    BetaResult,
    DataClassification,
    MyStocksUnifiedManager,
    RiskCalculator,
    RiskDashboardResponse,
    RiskMetrics,
    VaRCVaRRequest,
    VaRCVaRResult,
    get_monitoring_db,
    logger,
)
from app.core.exceptions import BusinessException


router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-指标计算"])


@router.post("/var-cvar", response_model=VaRCVaRResult)
async def calculate_var_cvar(request: VaRCVaRRequest) -> VaRCVaRResult:
    operation_start = datetime.now()
    try:
        manager = MyStocksUnifiedManager()
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
                },
            ],
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
            raise BusinessException(detail="保存风险指标失败", status_code=500, error_code="RISK_METRICS_SAVE_FAILED")

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
        raise BusinessException(
            detail=f"计算VaR/CVaR失败: {e!s}",
            status_code=500,
            error_code="VAR_CALCULATION_FAILED",
        )


@router.post("/beta", response_model=BetaResult)
async def calculate_beta(request: BetaRequest) -> BetaResult:
    operation_start = datetime.now()
    try:
        manager = MyStocksUnifiedManager()
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
            market_symbol = f"sz{market_index}" if len(market_index) == 6 else market_index
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
                },
            ],
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
        raise BusinessException(detail=f"计算Beta失败: {e!s}", status_code=500, error_code="BETA_CALCULATION_FAILED")


@router.get("/dashboard", response_model=RiskDashboardResponse)
async def get_risk_dashboard() -> RiskDashboardResponse:
    try:
        manager = MyStocksUnifiedManager()

        metrics_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_metrics",
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
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_metrics",
        )
        risk_history = []
        if history_df is not None:
            history_df = history_df[history_df["metric_date"] >= pd.Timestamp(thirty_days_ago)]
            risk_history = history_df.sort_values("metric_date").to_dict("records")

        return {
            "metrics": {
                "var_95_hist": latest_metrics.get("var_95_hist") if latest_metrics else None,
                "cvar_95": latest_metrics.get("cvar_95") if latest_metrics else None,
                "beta": latest_metrics.get("beta") if latest_metrics else None,
            },
            "active_alerts": [
                {
                    "id": a["id"],
                    "name": a["name"],
                    "metric_type": a["metric_type"],
                    "threshold_value": a["threshold_value"],
                }
                for a in active_alerts
            ],
            "risk_history": [
                {
                    "date": m["metric_date"],
                    "var_95_hist": m.get("var_95_hist"),
                    "cvar_95": m.get("cvar_95"),
                    "beta": m.get("beta"),
                }
                for m in risk_history
            ],
        }

    except Exception as e:
        raise BusinessException(
            detail=f"获取仪表盘数据失败: {e!s}",
            status_code=500,
            error_code="DASHBOARD_DATA_RETRIEVAL_FAILED",
        )


@router.get("/metrics/history", response_model=List[Dict[str, Any]])
async def get_risk_metrics_history(
    entity_type: str,
    entity_id: int,
    start_date: str,
    end_date: str,
) -> List[Dict[str, Any]]:
    try:
        manager = MyStocksUnifiedManager()
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
                "date": m["metric_date"],
                "var_95_hist": m.get("var_95_hist"),
                "var_95_param": m.get("var_95_param"),
                "cvar_95": m.get("cvar_95"),
                "beta": m.get("beta"),
            }
            for m in metrics_df.sort_values("metric_date").to_dict("records")
        ]

    except Exception as e:
        raise BusinessException(
            detail=f"获取历史数据失败: {e!s}",
            status_code=500,
            error_code="HISTORICAL_DATA_RETRIEVAL_FAILED",
        )


@router.post("/metrics/calculate")
async def calculate_risk_metrics(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if RISK_METRICS_AVAILABLE and RiskMetrics:
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
        returns_series = pd.Series(request.get("returns", []))
        metrics = {
            "volatility": float(returns_series.std() * np.sqrt(252)) if len(returns_series) > 0 else 0,
            "sharpe_ratio": float((returns_series.mean() * 252) / (returns_series.std() * np.sqrt(252)))
            if returns_series.std() > 0
            else 0,
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
        raise BusinessException(
            detail=f"计算风险指标失败: {e!s}",
            status_code=500,
            error_code="RISK_METRICS_CALCULATION_FAILED",
        )


@router.post("/position/assess")
async def assess_position_risk(request: Dict[str, Any]) -> Dict[str, Any]:
    try:
        positions = request.get("positions", [])
        total_capital = request.get("total_capital", 1000000)
        config = request.get("config", {})
        max_position_size = config.get("max_position_size", 0.10)

        total_position_value = sum(p.get("value", 0) for p in positions)
        position_ratio = total_position_value / total_capital if total_capital > 0 else 0
        cash_ratio = 1 - position_ratio

        position_concentration = []
        exceeded_positions = []
        sector_concentration = {}

        for pos in positions:
            symbol = pos.get("symbol", "UNKNOWN")
            value = pos.get("value", 0)
            sector = pos.get("sector", "UNKNOWN")
            concentration = value / total_capital if total_capital > 0 else 0
            exceeds_limit = concentration > max_position_size

            position_concentration.append(
                {"symbol": symbol, "concentration": concentration, "exceeds_limit": exceeds_limit},
            )
            if exceeds_limit:
                exceeded_positions.append({"symbol": symbol, "concentration": concentration})
            sector_concentration.setdefault(sector, 0)
            sector_concentration[sector] += value

        # Herfindahl index for portfolio concentration
        position_sizes = [p["value"] / total_capital for p in positions if total_capital > 0]
        herfindahl_index = sum(p**2 for p in position_sizes) if position_sizes else 0

        if len(exceeded_positions) > 0 or herfindahl_index > 0.5:
            risk_level = "HIGH"
        elif herfindahl_index > 0.25:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            "status": "success",
            "risk_assessment": {
                "total_position_value": total_position_value,
                "position_ratio": position_ratio,
                "cash_ratio": cash_ratio,
                "position_concentration": position_concentration,
                "exceeded_positions": exceeded_positions,
                "high_concentration_risk": len(exceeded_positions) > 0,
                "sector_concentration": {
                    s: v / total_capital if total_capital > 0 else 0 for s, v in sector_concentration.items()
                },
                "herfindahl_index": herfindahl_index,
                "risk_level": risk_level,
            },
            "assessed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error("评估仓位风险失败: {e}", exc_info=True)
        raise BusinessException(
            detail=f"评估仓位风险失败: {e!s}",
            status_code=500,
            error_code="POSITION_RISK_ASSESSMENT_FAILED",
        )
