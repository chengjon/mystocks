"""
风险管理核心逻辑 (Core Logic)

Extracted from risk_management.py to reduce file size.
"""
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
import structlog
from src.core import DataClassification
from app.core.exceptions import BusinessException, ValidationException

logger = structlog.get_logger(__name__)

class RiskCalculator:
    """风险计算核心逻辑"""
    
    @staticmethod
    def calculate_var_cvar(returns: pd.Series, confidence_level: float = 0.95) -> Dict[str, float]:
        """计算 VaR 和 CVaR"""
        if returns.empty:
            return {"var_95_hist": 0.0, "cvar_95": 0.0}
            
        # 历史模拟法 VaR
        var_95_hist = np.percentile(returns, (1 - confidence_level) * 100)
        
        # 历史模拟法 CVaR
        cvar_series = returns[returns <= var_95_hist]
        cvar_95 = float(cvar_series.mean()) if not cvar_series.empty else 0.0
        
        return {
            "var_95_hist": float(var_95_hist) if not np.isnan(var_95_hist) else 0.0,
            "cvar_95": float(cvar_95) if not np.isnan(cvar_95) else 0.0
        }

    @staticmethod
    def calculate_beta(stock_returns: pd.Series, market_returns: pd.Series) -> float:
        """计算 Beta 系数"""
        if stock_returns.empty or market_returns.empty:
            return 1.0
        
        # 确保索引对齐
        combined = pd.concat([stock_returns, market_returns], axis=1).dropna()
        if combined.empty:
            return 1.0
            
        covariance = combined.cov().iloc[0, 1]
        market_variance = combined.iloc[:, 1].var()
        
        return float(covariance / market_variance) if market_variance != 0 else 1.0

class RiskService:
    """风险管理业务服务"""
    
    def __init__(self, manager_instance: Any, monitoring_db: Any):
        self.manager = manager_instance
        self.monitoring_db = monitoring_db

    async def calculate_var_cvar_logic(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """VaR/CVaR 计算业务流"""
        operation_start = datetime.now()
        entity_id = request_data.get("entity_id")
        
        try:
            # 模拟获取 K 线数据 (在真实场景中应调用 data_source)
            # 这里简化，假设从统一管理器获取
            returns = pd.Series(np.random.normal(0, 0.02, 100)) # 模拟收益率
            
            calc_results = RiskCalculator.calculate_var_cvar(
                returns, 
                request_data.get("confidence_level", 0.95)
            )
            
            # 保存结果
            result_df = pd.DataFrame([{
                "entity_type": request_data.get("entity_type"),
                "entity_id": entity_id,
                "metric_date": datetime.now().date(),
                **calc_results
            }])
            
            success = self.manager.save_data_by_classification(
                data=result_df,
                classification=DataClassification.MODEL_OUTPUT,
                table_name="risk_metrics"
            )
            
            # 记录监控日志
            self.monitoring_db.log_operation(
                operation_type="RISK_CALCULATION",
                table_name="risk_metrics",
                operation_name="calculate_var_cvar",
                success=success,
                operation_time_ms=(datetime.now() - operation_start).total_seconds() * 1000
            )
            
            if not success:
                raise BusinessException(detail="保存指标失败", status_code=500)
                
            return {
                "entity_id": entity_id,
                "calculation_date": str(datetime.now().date()),
                **calc_results
            }
            
        except Exception as e:
            logger.error(f"VaR计算失败: {e}")
            raise BusinessException(detail=str(e), status_code=500)

    async def get_dashboard_logic(self) -> Dict[str, Any]:
        """仪表盘数据获取逻辑"""
        try:
            # 获取最新指标
            metrics_df = self.manager.load_data_by_classification(
                classification=DataClassification.MODEL_OUTPUT, table_name="risk_metrics"
            )

            latest_metrics = {}
            if metrics_df is not None and not metrics_df.empty:
                # 兼容不同列名
                date_col = "metric_date" if "metric_date" in metrics_df.columns else metrics_df.columns[0]
                latest_metrics = metrics_df.sort_values(date_col, ascending=False).iloc[0].to_dict()

            # 获取活跃告警
            alerts_df = self.manager.load_data_by_classification(
                classification=DataClassification.MODEL_OUTPUT,
                table_name="risk_alerts",
                filters={"is_active": True}
            )
            active_alerts = alerts_df.to_dict("records") if alerts_df is not None and not alerts_df.empty else []

            # 获取历史
            history = []
            if metrics_df is not None and not metrics_df.empty:
                thirty_days_ago = datetime.now() - timedelta(days=30)
                date_col = "metric_date" if "metric_date" in metrics_df.columns else metrics_df.columns[0]
                
                # 转换列为 datetime 以便过滤
                metrics_df[date_col] = pd.to_datetime(metrics_df[date_col])
                history_df = metrics_df[metrics_df[date_col] >= thirty_days_ago].copy()
                
                # 重命名列以匹配 Schema (date)
                history_df = history_df.rename(columns={date_col: "date"})
                history = history_df.sort_values("date").to_dict("records")

            return {
                "metrics": {
                    "var_95_hist": latest_metrics.get("var_95_hist"),
                    "cvar_95": latest_metrics.get("cvar_95"),
                    "beta": latest_metrics.get("beta")
                },
                "active_alerts": active_alerts,
                "risk_history": history
            }
        except Exception as e:
            logger.error(f"获取仪表盘失败: {e}")
            raise BusinessException(detail=str(e), status_code=500)