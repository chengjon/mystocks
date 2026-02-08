"""
风险管理核心逻辑模块 (Refactored)

拆分自 risk_management.py，负责核心计算和业务逻辑处理。
遵循单一职责原则。

Author: Claude Code
Date: 2026-02-08
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import structlog

from app.core.exceptions import BusinessException
from src.core import DataClassification
from app.schemas.risk_schemas import VaRCVaRResult, BetaResult

logger = structlog.get_logger(__name__)

class RiskCalculator:
    """提供基础风险指标计算 (VaR, CVaR, Beta)"""

    @staticmethod
    def calculate_all(returns: pd.Series, confidence_level: float = 0.95) -> Dict[str, float]:
        """计算 VaR 和 CVaR"""
        if returns.empty:
            return {"var_95_hist": 0.0, "var_95_param": 0.0, "var_99_hist": 0.0, "cvar_95": 0.0, "cvar_99": 0.0}

        # 历史模拟法
        var_95_hist = float(np.percentile(returns, (1 - confidence_level) * 100))
        var_99_hist = float(np.percentile(returns, 1))  # Fixed 99% for compatibility

        # 参数法 (假设正态分布)
        mean = returns.mean()
        std = returns.std()
        var_95_param = float(mean - 1.645 * std)

        # CVaR (Expected Shortfall)
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
        """计算 Beta 系数"""
        if asset_returns.empty or market_returns.empty:
            return 0.0

        # 确保长度一致
        min_len = min(len(asset_returns), len(market_returns))
        asset = asset_returns.iloc[:min_len]
        market = market_returns.iloc[:min_len]

        covariance = np.cov(asset, market)[0][1]
        market_variance = np.var(market)

        if market_variance == 0:
            return 0.0

        return float(covariance / market_variance)

class RiskService:
    """风险管理业务服务"""
    
    @staticmethod
    async def calculate_var_cvar_logic(
        entity_type: str, 
        entity_id: int, 
        confidence_level: float,
        unified_manager: Any,
        monitoring_db: Any,
        ts_source_factory: Any
    ) -> VaRCVaRResult:
        """业务逻辑：计算并保存VaR/CVaR"""
        operation_start = datetime.now()
        
        try:
            # 获取收益率数据 (Mock逻辑保留)
            ts_source = ts_source_factory(source_type="mock")
            ts_source.set_random_seed(42)

            start = datetime.now() - timedelta(days=365)
            end = datetime.now()
            kline = ts_source.get_kline_data(symbol="sh600000", start_time=start, end_time=end, interval="1d")
            if kline is not None and len(kline) > 1:
                returns = kline["close"].pct_change().dropna()
            else:
                returns = pd.Series(np.random.normal(0.001, 0.02, 252))

            # 计算风险指标
            metrics = RiskCalculator.calculate_all(returns, confidence_level)

            # 保存到数据库
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

            result = unified_manager.save_data_by_classification(
                data=risk_data,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="risk_metrics",
            )

            # 记录操作
            operation_time = (datetime.now() - operation_start).total_seconds() * 1000
            monitoring_db.log_operation(
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
            monitoring_db.log_operation(
                operation_type="RISK_CALCULATION",
                table_name="risk_metrics",
                operation_name="calculate_var_cvar",
                rows_affected=0,
                operation_time_ms=operation_time,
                success=False,
                error_message=str(e),
            )
            if isinstance(e, BusinessException):
                raise e
            raise BusinessException(
                detail=f"计算VaR/CVaR失败: {str(e)}", status_code=500, error_code="VAR_CALCULATION_FAILED"
            )

    @staticmethod
    async def calculate_beta_logic(
        entity_type: str,
        entity_id: int,
        market_index: str,
        unified_manager: Any,
        monitoring_db: Any,
        ts_source_factory: Any
    ) -> BetaResult:
        """业务逻辑：计算并保存Beta"""
        operation_start = datetime.now()

        try:
            ts_source = ts_source_factory(source_type="mock")
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
                    }
                ]
            )

            result = unified_manager.save_data_by_classification(
                data=risk_data,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="risk_metrics",
                upsert=True,
            )

            operation_time = (datetime.now() - operation_start).total_seconds() * 1000
            monitoring_db.log_operation(
                operation_type="RISK_CALCULATION",
                table_name="risk_metrics",
                operation_name="calculate_beta",
                rows_affected=1,
                operation_time_ms=operation_time,
                success=result,
            )

            return BetaResult(
                beta=beta, correlation=correlation, entity_type=entity_type, entity_id=entity_id, market_index=market_index
            )

        except Exception as e:
            operation_time = (datetime.now() - operation_start).total_seconds() * 1000
            monitoring_db.log_operation(
                operation_type="RISK_CALCULATION",
                table_name="risk_metrics",
                operation_name="calculate_beta",
                rows_affected=0,
                operation_time_ms=operation_time,
                success=False,
                error_message=str(e),
            )
            if isinstance(e, BusinessException):
                raise e
            raise BusinessException(detail=f"计算Beta失败: {str(e)}", status_code=500, error_code="BETA_CALCULATION_FAILED")
