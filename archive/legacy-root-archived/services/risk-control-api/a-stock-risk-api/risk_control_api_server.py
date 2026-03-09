"""
A股风险控制API服务器
复用主项目的风险指标计算模块，提供完整的风险分析和控制服务
"""
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import pandas as pd
import numpy as np

# 添加主项目路径
project_root = Path("/opt/claude/mystocks_spec")
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="A股风险控制API",
    description="量化交易风险分析和控制服务",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ 数据模型 ============

class RiskMetricsRequest(BaseModel):
    """风险指标计算请求"""
    equity_curve: List[float] = Field(..., description="权益曲线数据")
    returns: List[float] = Field(..., description="收益率序列")
    trades: List[Dict[str, Any]] = Field(default=[], description="交易记录")
    total_return: float = Field(..., description="总收益率")
    max_drawdown: float = Field(..., description="最大回撤")
    risk_free_rate: float = Field(0.0, description="无风险利率")

    class Config:
        json_schema_extra = {
            "example": {
                "equity_curve": [100000, 102000, 101000, 103000, 105000],
                "returns": [0.02, -0.01, 0.02, 0.02],
                "trades": [],
                "total_return": 0.05,
                "max_drawdown": -0.02,
                "risk_free_rate": 0.03
            }
        }

class RiskControlConfig(BaseModel):
    """风险控制配置"""
    max_drawdown_threshold: float = Field(0.30, description="最大回撤阈值")
    stop_loss_pct: Optional[float] = Field(None, description="止损百分比")
    take_profit_pct: Optional[float] = Field(None, description="止盈百分比")
    max_position_size: float = Field(0.10, description="单个股票最大仓位")
    daily_loss_limit: float = Field(0.05, description="单日亏损限制")

class PositionRiskRequest(BaseModel):
    """仓位风险评估请求"""
    positions: List[Dict[str, Any]] = Field(..., description="持仓列表")
    total_capital: float = Field(..., description="总资金")
    config: RiskControlConfig = Field(default_factory=RiskControlConfig)

class RiskAlertRequest(BaseModel):
    """风险告警请求"""
    current_drawdown: float = Field(..., description="当前回撤")
    daily_pnl: float = Field(..., description="当日盈亏")
    total_capital: float = Field(..., description="总资金")
    config: RiskControlConfig = Field(default_factory=RiskControlConfig)

# ============ 全局变量 ============

# 尝试导入风险指标计算模块
try:
    from src.ml_strategy.backtest.risk_metrics import RiskMetrics
    RISK_METRICS_AVAILABLE = True
    logger.info("✅ 主项目风险指标模块已加载")
except ImportError as e:
    logger.warning(f"⚠️  主项目风险指标模块不可用: {e}")
    RISK_METRICS_AVAILABLE = False
    RiskMetrics = None

# 风险告警存储
risk_alerts: Dict[str, Dict[str, Any]] = {}
alert_counter = 0

# ============ 辅助函数 ============

def calculate_risk_metrics_fallback(
    equity_curve: List[float],
    returns: List[float],
    trades: List[Dict],
    total_return: float,
    max_drawdown: float,
    risk_free_rate: float = 0.0
) -> Dict[str, Any]:
    """风险指标计算的备用实现（不依赖主项目）"""
    logger.info("使用备用风险指标计算")

    returns_series = pd.Series(returns)
    equity_df = pd.DataFrame({"equity": equity_curve})

    metrics = {}

    # 基础统计指标
    metrics["volatility"] = returns_series.std() * np.sqrt(252)  # 年化波动率
    metrics["downside_deviation"] = returns_series[returns_series < 0].std() * np.sqrt(252)
    metrics["sharpe_ratio"] = (returns_series.mean() * 252) / (returns_series.std() * np.sqrt(252)) if returns_series.std() > 0 else 0

    # 回撤分析
    cummax = equity_df["equity"].cummax()
    drawdown = (equity_df["equity"] - cummax) / cummax
    metrics["max_drawdown"] = drawdown.min()
    metrics["avg_drawdown"] = drawdown[drawdown < 0].mean() if len(drawdown[drawdown < 0]) > 0 else 0
    metrics["ulcer_index"] = np.sqrt((drawdown ** 2).mean())

    # 分布特征
    from scipy import stats
    metrics["skewness"] = stats.skew(returns_series)
    metrics["kurtosis"] = stats.kurtosis(returns_series)

    # 交易风险（如果有交易记录）
    if trades:
        pnls = [t.get("pnl", 0) for t in trades if "pnl" in t]
        if pnls:
            winning_trades = [p for p in pnls if p > 0]
            losing_trades = [p for p in pnls if p < 0]

            if winning_trades and losing_trades:
                avg_win = np.mean(winning_trades)
                avg_loss = abs(np.mean(losing_trades))
                metrics["payoff_ratio"] = avg_win / avg_loss if avg_loss > 0 else 0
            else:
                metrics["payoff_ratio"] = 0

            win_rate = len(winning_trades) / len(pnls) if pnls else 0
            loss_rate = len(losing_trades) / len(pnls) if pnls else 0
            metrics["win_rate"] = win_rate
            metrics["trade_expectancy"] = (win_rate * np.mean(winning_trades)) - (loss_rate * abs(np.mean(losing_trades))) if winning_trades and losing_trades else 0

    return metrics

def assess_position_risk(
    positions: List[Dict[str, Any]],
    total_capital: float,
    config: RiskControlConfig
) -> Dict[str, Any]:
    """评估仓位风险"""

    total_position_value = sum(p.get("value", 0) for p in positions)
    total_market_value = sum(p.get("market_value", p.get("value", 0)) for p in positions)

    # 计算风险指标
    position_concentration = []
    sector_concentration = {}

    for pos in positions:
        symbol = pos.get("symbol", "UNKNOWN")
        value = pos.get("value", 0)
        sector = pos.get("sector", "UNKNOWN")

        # 个股集中度
        concentration = value / total_capital if total_capital > 0 else 0
        position_concentration.append({
            "symbol": symbol,
            "concentration": concentration,
            "exceeds_limit": concentration > config.max_position_size
        })

        # 行业集中度
        if sector not in sector_concentration:
            sector_concentration[sector] = 0
        sector_concentration[sector] += value

    # 风险评估
    exceeded_positions = [p for p in position_concentration if p["exceeds_limit"]]
    high_concentration_risk = len(exceeded_positions) > 0

    # 仓位分布
    position_sizes = [p["value"] / total_capital for p in positions if total_capital > 0]
    herfindahl_index = sum(p**2 for p in position_sizes) if position_sizes else 0

    return {
        "total_position_value": total_position_value,
        "total_market_value": total_market_value,
        "position_ratio": total_position_value / total_capital if total_capital > 0 else 0,
        "cash_ratio": 1 - (total_position_value / total_capital) if total_capital > 0 else 0,
        "position_concentration": position_concentration,
        "exceeded_positions": exceeded_positions,
        "high_concentration_risk": high_concentration_risk,
        "sector_concentration": {
            sector: value / total_capital if total_capital > 0 else 0
            for sector, value in sector_concentration.items()
        },
        "herfindahl_index": herfindahl_index,
        "risk_level": "HIGH" if high_concentration_risk else "MEDIUM" if herfindahl_index > 0.25 else "LOW"
    }

def generate_risk_alerts(
    current_drawdown: float,
    daily_pnl: float,
    total_capital: float,
    config: RiskControlConfig
) -> List[Dict[str, Any]]:
    """生成风险告警"""

    alerts = []
    alert_time = datetime.now().isoformat()

    # 回撤告警
    if abs(current_drawdown) > config.max_drawdown_threshold:
        alerts.append({
            "type": "max_drawdown_exceeded",
            "severity": "CRITICAL",
            "message": f"最大回撤超限: {abs(current_drawdown)*100:.2f}% > {config.max_drawdown_threshold*100:.2f}%",
            "timestamp": alert_time,
            "suggestion": "立即减仓或平仓，控制风险敞口"
        })

    # 单日亏损告警
    daily_loss_pct = daily_pnl / total_capital if total_capital > 0 else 0
    if daily_loss_pct < -config.daily_loss_limit:
        alerts.append({
            "type": "daily_loss_limit_exceeded",
            "severity": "WARNING",
            "message": f"单日亏损超限: {daily_loss_pct*100:.2f}% < -{config.daily_loss_limit*100:.2f}%",
            "timestamp": alert_time,
            "suggestion": "暂停新开仓，评估当前持仓风险"
        })

    return alerts

# ============ API端点 ============

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "A股风险控制API",
        "version": "1.0.0",
        "risk_metrics_available": RISK_METRICS_AVAILABLE,
        "endpoints": {
            "POST /api/risk/metrics": "计算风险指标",
            "POST /api/risk/position": "评估仓位风险",
            "POST /api/risk/alerts": "生成风险告警",
            "GET /api/risk/alerts/list": "列出所有告警",
            "GET /health": "健康检查"
        }
    }

@app.get("/health")
async def health():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "risk_metrics_available": RISK_METRICS_AVAILABLE,
        "active_alerts": len([a for a in risk_alerts.values() if a.get("active", False)])
    }

@app.post("/api/risk/metrics")
async def calculate_risk_metrics(request: RiskMetricsRequest):
    """
    计算风险指标

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

    ## 响应示例
    ```json
    {
      "metrics": {
        "volatility": 0.15,
        "sharpe_ratio": 1.5,
        "max_drawdown": -0.05,
        "ulcer_index": 2.3
      }
    }
    ```
    """
    try:
        if RISK_METRICS_AVAILABLE and RiskMetrics:
            logger.info("📊 使用主项目风险指标模块")
            risk_calculator = RiskMetrics()

            # 转换数据格式
            equity_df = pd.DataFrame({"equity": request.equity_curve})
            returns_series = pd.Series(request.returns)

            # 计算所有风险指标
            metrics = risk_calculator.calculate_all_risk_metrics(
                equity_curve=equity_df,
                returns=returns_series,
                trades=request.trades,
                total_return=request.total_return,
                max_drawdown=request.max_drawdown,
                risk_free_rate=request.risk_free_rate
            )
        else:
            logger.info("📊 使用备用风险指标计算")
            metrics = calculate_risk_metrics_fallback(
                equity_curve=request.equity_curve,
                returns=request.returns,
                trades=request.trades,
                total_return=request.total_return,
                max_drawdown=request.max_drawdown,
                risk_free_rate=request.risk_free_rate
            )

        return {
            "status": "success",
            "metrics": metrics,
            "calculated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"计算风险指标失败: {e}")
        raise HTTPException(status_code=500, detail=f"计算风险指标失败: {str(e)}")

@app.post("/api/risk/position")
async def assess_position_risk_endpoint(request: PositionRiskRequest):
    """
    评估仓位风险

    ## 请求示例
    ```json
    {
      "positions": [
        {"symbol": "sh600000", "value": 100000, "sector": "金融"},
        {"symbol": "sh600036", "value": 150000, "sector": "金融"}
      ],
      "total_capital": 1000000,
      "config": {
        "max_position_size": 0.10,
        "daily_loss_limit": 0.05
      }
    }
    ```

    ## 响应示例
    ```json
    {
      "risk_assessment": {
        "total_position_value": 250000,
        "position_ratio": 0.25,
        "risk_level": "MEDIUM",
        "exceeded_positions": [...]
      }
    }
    ```
    """
    try:
        assessment = assess_position_risk(
            positions=request.positions,
            total_capital=request.total_capital,
            config=request.config
        )

        return {
            "status": "success",
            "risk_assessment": assessment,
            "assessed_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"评估仓位风险失败: {e}")
        raise HTTPException(status_code=500, detail=f"评估仓位风险失败: {str(e)}")

@app.post("/api/risk/alerts")
async def generate_risk_alerts_endpoint(request: RiskAlertRequest):
    """
    生成风险告警

    ## 请求示例
    ```json
    {
      "current_drawdown": -0.15,
      "daily_pnl": -50000,
      "total_capital": 1000000,
      "config": {
        "max_drawdown_threshold": 0.30,
        "daily_loss_limit": 0.05
      }
    }
    ```

    ## 响应示例
    ```json
    {
      "alerts": [
        {
          "type": "daily_loss_limit_exceeded",
          "severity": "WARNING",
          "message": "单日亏损超限: -5.00%",
          "timestamp": "2025-12-26T11:30:00",
          "suggestion": "暂停新开仓"
        }
      ]
    }
    ```
    """
    global alert_counter, risk_alerts

    try:
        alerts = generate_risk_alerts(
            current_drawdown=request.current_drawdown,
            daily_pnl=request.daily_pnl,
            total_capital=request.total_capital,
            config=request.config
        )

        # 保存告警记录
        alert_counter += 1
        alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{alert_counter}"

        alert_record = {
            "alert_id": alert_id,
            "alerts": alerts,
            "created_at": datetime.now().isoformat(),
            "active": True
        }

        risk_alerts[alert_id] = alert_record

        return {
            "status": "success",
            "alert_id": alert_id,
            "alerts": alerts,
            "alert_count": len(alerts),
            "created_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"生成风险告警失败: {e}")
        raise HTTPException(status_code=500, detail=f"生成风险告警失败: {str(e)}")

@app.get("/api/risk/alerts/list")
async def list_alerts():
    """列出所有告警"""
    return {
        "total": len(risk_alerts),
        "active": len([a for a in risk_alerts.values() if a.get("active", False)]),
        "items": [
            {
                "alert_id": alert_id,
                "created_at": alert["created_at"],
                "active": alert.get("active", False),
                "alert_count": len(alert.get("alerts", []))
            }
            for alert_id, alert in risk_alerts.items()
        ]
    }

# ============ 主程序 ============

if __name__ == "__main__":
    print("=" * 70)
    print("🛡️  A股风险控制API服务器")
    print("=" * 70)
    print("📡 API地址: http://localhost:8003")
    print("🏥 健康检查: http://localhost:8003/health")
    print("📚 API文档: http://localhost:8003/docs")
    print(f"🎯 风险指标: {'✅ 主模块已加载' if RISK_METRICS_AVAILABLE else '⚠️  使用备用实现'}")
    print("=" * 70)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8003,
        log_level="info"
    )
