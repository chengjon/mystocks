"""
风险管理 API - Week 1 Architecture Compliant

提供VaR/CVaR计算、Beta分析、风险预警等接口
使用 MyStocksUnifiedManager 统一数据访问 + MonitoringDatabase 监控集成

Author: JohnC & Claude
Version: 2.0.0 (Architecture Compliant)
Date: 2025-10-24
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import sys
import os
import structlog

logger = structlog.get_logger(__name__)

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 使用 MyStocksUnifiedManager 作为统一入口点
from unified_manager import MyStocksUnifiedManager
from src.core import DataClassification
from src.monitoring.monitoring_database import MonitoringDatabase

# 导入 NotificationManager
try:
    from src.ml_strategy.automation.notification_manager import (
        NotificationManager,
        NotificationChannel,
        NotificationLevel,
    )
except ImportError:
    NotificationManager = None
    NotificationChannel = None
    NotificationLevel = None


# 本地实现的风险计算器 (替代 ExtendedRiskMetrics)
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


# 风险指标计算模块（新功能 - 2025-12-26）
try:
    from src.ml_strategy.backtest.risk_metrics import RiskMetrics

    RISK_METRICS_AVAILABLE = True
except ImportError:
    RISK_METRICS_AVAILABLE = False
    RiskMetrics = None

router = APIRouter(prefix="/api/v1/risk", tags=["风险管理-Week1"])

# 延迟初始化监控数据库（避免导入时需要完整环境变量）
monitoring_db = None


def get_monitoring_db():
    """获取监控数据库实例（延迟初始化）"""
    global monitoring_db
    if monitoring_db is None:
        try:
            real_monitoring_db = MonitoringDatabase()

            # 创建适配器来匹配Week1 API的参数命名约定
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
                    """适配Week1 API的参数命名到MonitoringDatabase的实际参数"""
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
                        logger.debug(f"Monitoring log failed (non-critical): {e}")
                        return False

            monitoring_db = MonitoringAdapter(real_monitoring_db)

        except Exception as e:
            logger.warning(f"MonitoringDatabase initialization failed, using fallback: {e}")

            # 创建一个简单的fallback对象
            class MonitoringFallback:
                def log_operation(self, *args, **kwargs):
                    return True  # Silent fallback

            monitoring_db = MonitoringFallback()
    return monitoring_db


from app.schemas.risk_schemas import (
    VaRCVaRRequest,
    VaRCVaRResult,
    BetaRequest,
    BetaResult,
    RiskAlertCreate,
    RiskAlertUpdate,
    RiskAlertResponse,
    NotificationTestRequest,
    NotificationTestResponse,
    RiskDashboardResponse,
)

# ============ 风险指标计算 ============


@router.post("/var-cvar", response_model=VaRCVaRResult)
async def calculate_var_cvar(request: VaRCVaRRequest) -> VaRCVaRResult:
    """
    计算VaR和CVaR

    Args:
        request: 请求参数

    Returns:
        VaRCVaRResult
    """
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()
        entity_type = request.entity_type
        entity_id = request.entity_id
        confidence_level = request.confidence_level

        # 获取收益率数据
        # 使用 Mock 数据源生成模拟数据
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

        # 计算风险指标
        metrics = RiskCalculator.calculate_all(returns)

        # 保存到数据库（使用 UnifiedManager）
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

        # 记录操作到监控数据库
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
        # 记录失败操作
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
    """
    计算Beta系数

    Args:
        request: 请求参数

    Returns:
        BetaResult
    """
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()
        entity_type = request.entity_type
        entity_id = request.entity_id
        market_index = request.market_index

        # 获取资产和市场收益率数据
        # 使用 Mock 数据源生成模拟数据
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

        # 计算Beta
        beta = RiskCalculator.beta(asset_returns, market_returns)

        # 计算相关系数
        correlation = float(asset_returns.corr(market_returns))

        # 更新或创建风险指标记录
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

        # 记录操作到监控数据库
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
            beta=beta, correlation=correlation, entity_type=entity_type, entity_id=entity_id, market_index=market_index
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
    """
    获取风险仪表盘数据

    Returns:
        RiskDashboardResponse
    """
    try:
        manager = MyStocksUnifiedManager()

        # 获取最新风险指标
        metrics_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT, table_name="risk_metrics"
        )

        latest_metrics = None
        if metrics_df is not None and len(metrics_df) > 0:
            latest_metrics = metrics_df.sort_values("metric_date", ascending=False).iloc[0].to_dict()

        # 获取活跃预警规则
        alerts_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            filters={"is_active": True},
        )

        active_alerts = alerts_df.to_dict("records") if alerts_df is not None else []

        # 获取风险历史（最近30天）
        thirty_days_ago = (datetime.now() - timedelta(days=30)).date()
        # 注意：这里简化了过滤逻辑，实际应该支持日期范围过滤
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


@router.get("/metrics/history", response_model=List[Dict[str, Any]])
async def get_risk_metrics_history(
    entity_type: str, entity_id: int, start_date: str, end_date: str
) -> List[Dict[str, Any]]:
    """获取风险指标历史数据"""
    try:
        manager = MyStocksUnifiedManager()

        # 获取风险指标数据
        metrics_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_metrics",
            filters={"entity_type": entity_type, "entity_id": entity_id},
        )

        if metrics_df is None or len(metrics_df) == 0:
            return []

        # 日期过滤
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


# ============ 风险预警管理 ============


@router.get("/alerts")
async def list_risk_alerts(is_active: Optional[bool] = None) -> List[Dict[str, Any]]:
    """获取风险预警规则列表"""
    try:
        manager = MyStocksUnifiedManager()

        filters = {}
        if is_active is not None:
            filters["is_active"] = is_active

        alerts_df = manager.load_data_by_classification(
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            filters=filters,
        )

        return alerts_df.to_dict("records") if alerts_df is not None else []

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取预警列表失败: {str(e)}")


@router.post("/alerts", response_model=RiskAlertResponse)
async def create_risk_alert(alert_data: RiskAlertCreate) -> RiskAlertResponse:
    """创建风险预警规则"""
    operation_start = datetime.now()

    try:
        manager = MyStocksUnifiedManager()

        # 转换为字典
        data_dict = alert_data.dict()
        data_dict["created_at"] = datetime.now()
        data_dict["updated_at"] = datetime.now()

        alert_df = pd.DataFrame([data_dict])

        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
        )

        # 记录操作
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="risk_alerts",
            operation_name="create_risk_alert",
            rows_affected=1,
            operation_time_ms=operation_time,
            success=result,
        )

        if result:
            # 获取 ID (模拟，实际应该从数据库返回)
            data_dict["id"] = int(datetime.now().timestamp())
            return RiskAlertResponse(**data_dict)
        else:
            raise HTTPException(status_code=500, detail="创建预警规则失败")

    except Exception as e:
        operation_time = (datetime.now() - operation_start).total_seconds() * 1000
        get_monitoring_db().log_operation(
            operation_type="INSERT",
            table_name="risk_alerts",
            operation_name="create_risk_alert",
            rows_affected=0,
            operation_time_ms=operation_time,
            success=False,
            error_message=str(e),
        )
        raise HTTPException(status_code=500, detail=f"创建预警规则失败: {str(e)}")


@router.put("/alerts/{alert_id}")
async def update_risk_alert(alert_id: int, alert_update: RiskAlertUpdate) -> Dict[str, str]:
    """更新风险预警规则"""
    try:
        manager = MyStocksUnifiedManager()

        update_data = alert_update.dict(exclude_unset=True)
        update_data["id"] = alert_id
        update_data["updated_at"] = datetime.now()

        alert_df = pd.DataFrame([update_data])

        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            upsert=True,
        )

        if result:
            return {"message": "预警规则已更新"}
        else:
            raise HTTPException(status_code=500, detail="更新预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新预警规则失败: {str(e)}")


@router.delete("/alerts/{alert_id}")
async def delete_risk_alert(alert_id: int) -> Dict[str, str]:
    """删除风险预警规则（软删除：设置为非活跃）"""
    try:
        manager = MyStocksUnifiedManager()

        # 软删除：更新is_active为False
        alert_df = pd.DataFrame([{"id": alert_id, "is_active": False}])

        result = manager.save_data_by_classification(
            data=alert_df,
            classification=DataClassification.MODEL_OUTPUT,
            table_name="risk_alerts",
            upsert=True,
        )

        if result:
            return {"message": "预警规则已禁用"}
        else:
            raise HTTPException(status_code=500, detail="删除预警规则失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除预警规则失败: {str(e)}")


# ============ 通知管理 ============


@router.post("/notifications/test", response_model=NotificationTestResponse)
async def test_notification(request: NotificationTestRequest) -> NotificationTestResponse:
    """发送测试通知"""
    try:
        notifier = NotificationManager()

        if request.notification_type == "email":
            result = notifier.send_email(
                to_addrs=[request.config_data.get("email")],
                subject="MyStocks 测试通知",
                message="这是一封测试邮件，您的邮件配置正常工作！",
            )
        elif request.notification_type == "webhook":
            result = notifier.send_webhook(message="MyStocks 测试通知", test=True)
        else:
            raise HTTPException(status_code=400, detail="不支持的通知类型")

        if result:
            return NotificationTestResponse(success=True, message="测试通知发送成功")
        else:
            return NotificationTestResponse(success=False, message="测试通知发送失败")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发送失败: {str(e)}")


# ============ 风险指标计算（新功能 - 2025-12-26）============


@router.post("/metrics/calculate")
async def calculate_risk_metrics(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    计算完整的风险指标（使用主项目RiskMetrics类）

    ## 请求示例
    ```json
    {
      "equity_curve": [100000, 102000, 101000, 103000, 105000],
      "returns": [0.02, -0.01, 0.02, 0.02],
      "trades": [],
      "total_return": 0.05,
      "max_drawdown": -0.02,
      "risk_free_rate": 0.03
    }
    ```
    """
    try:
        if RISK_METRICS_AVAILABLE and RiskMetrics:
            logger.info("📊 使用主项目风险指标计算模块")

            # 转换数据格式
            equity_df = pd.DataFrame({"equity": request.get("equity_curve", [])})
            returns_series = pd.Series(request.get("returns", []))
            trades = request.get("trades", [])

            # 计算所有风险指标
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
            logger.info("📊 主项目风险指标模块不可用，返回简化指标")
            # 简化版计算
            returns_series = pd.Series(request.get("returns", []))
            # equity_curve = request.get("equity_curve", [])

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
        logger.error(f"计算风险指标失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"计算风险指标失败: {str(e)}")


@router.post("/position/assess")
async def assess_position_risk(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    评估仓位风险

    ## 请求示例
    ```json
    {
      "positions": [
        {"symbol": "sh600000", "value": 150000, "sector": "金融"},
        {"symbol": "sh600036", "value": 120000, "sector": "金融"}
      ],
      "total_capital": 1000000,
      "config": {
        "max_position_size": 0.10,
        "daily_loss_limit": 0.05
      }
    }
    ```
    """
    try:
        positions = request.get("positions", [])
        total_capital = request.get("total_capital", 1000000)
        config = request.get("config", {})

        max_position_size = config.get("max_position_size", 0.10)

        # 计算总仓位
        total_position_value = sum(p.get("value", 0) for p in positions)
        position_ratio = total_position_value / total_capital if total_capital > 0 else 0
        cash_ratio = 1 - position_ratio

        # 个股集中度分析
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
                {"symbol": symbol, "concentration": concentration, "exceeds_limit": exceeds_limit}
            )

            if exceeds_limit:
                exceeded_positions.append({"symbol": symbol, "concentration": concentration})

            # 行业集中度
            if sector not in sector_concentration:
                sector_concentration[sector] = 0
            sector_concentration[sector] += value

        # Herfindahl指数（持仓集中度）
        position_sizes = [p["value"] / total_capital for p in positions if total_capital > 0]
        herfindahl_index = sum(p**2 for p in position_sizes) if position_sizes else 0

        # 风险等级评估
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
                    sector: value / total_capital if total_capital > 0 else 0
                    for sector, value in sector_concentration.items()
                },
                "herfindahl_index": herfindahl_index,
                "risk_level": risk_level,
            },
            "assessed_at": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"评估仓位风险失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"评估仓位风险失败: {str(e)}")


@router.post("/alerts/generate")
async def generate_risk_alerts(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    生成风险告警

    ## 请求示例
    ```json
    {
      "current_drawdown": -0.25,
      "daily_pnl": -60000,
      "total_capital": 1000000,
      "config": {
        "max_drawdown_threshold": 0.30,
        "daily_loss_limit": 0.05
      }
    }
    ```
    """
    try:
        current_drawdown = request.get("current_drawdown", 0)
        daily_pnl = request.get("daily_pnl", 0)
        total_capital = request.get("total_capital", 1000000)
        config = request.get("config", {})

        max_drawdown_threshold = config.get("max_drawdown_threshold", 0.30)
        daily_loss_limit = config.get("daily_loss_limit", 0.05)

        alerts = []
        alert_time = datetime.now().isoformat()

        # 回撤告警
        if abs(current_drawdown) > max_drawdown_threshold:
            alerts.append(
                {
                    "type": "max_drawdown_exceeded",
                    "severity": "CRITICAL",
                    "message": (
                        f"最大回撤超限: {abs(current_drawdown) * 100:.2f}% > " f"{max_drawdown_threshold * 100:.2f}%"
                    ),
                    "timestamp": alert_time,
                    "suggestion": "立即减仓或平仓，控制风险敞口",
                }
            )

        # 单日亏损告警
        daily_loss_pct = daily_pnl / total_capital if total_capital > 0 else 0
        if daily_loss_pct < -daily_loss_limit:
            alerts.append(
                {
                    "type": "daily_loss_limit_exceeded",
                    "severity": "WARNING",
                    "message": f"单日亏损超限: {daily_loss_pct * 100:.2f}% < -{daily_loss_limit * 100:.2f}%",
                    "timestamp": alert_time,
                    "suggestion": "暂停新开仓，评估当前持仓风险",
                }
            )

        return {"status": "success", "alerts": alerts, "alert_count": len(alerts), "generated_at": alert_time}

    except Exception as e:
        logger.error(f"生成风险告警失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"生成风险告警失败: {str(e)}")
