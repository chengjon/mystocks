#!/usr/bin/env python3
"""
投资组合优化器
提供组合健康度分析、再平衡建议和风险预警

功能：
- 组合整体健康度评分（加权平均）
- 风险分布分析
- 再平衡建议算法
- 三级风险预警（紧急/提醒/提示）

作者: Claude Code
创建日期: 2026-01-07
"""

import logging
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """预警级别"""

    CRITICAL = "critical"  # 🔴 紧急
    WARNING = "warning"  # 🟡 提醒
    INFO = "info"  # 🟢 提示


class RebalanceReason(Enum):
    """再平衡原因"""

    DRIFT_THRESHOLD = "weight_drift"  # 权重偏离
    RISK_THRESHOLD = "risk_exceeded"  # 风险超限
    PROFIT_TARGET = "profit_target"  # 止盈目标
    STOP_LOSS = "stop_loss"  # 止损触发
    REGIME_CHANGE = "regime_change"  # 市场体制变化


@dataclass
class PortfolioPosition:
    """组合持仓"""

    stock_code: str
    weight: float
    entry_price: float
    current_price: float
    target_weight: float = 0.0
    stop_loss_price: float = 0.0
    target_price: float = 0.0

    @property
def unrealized_pnl(self) -> float:
        """未实现盈亏"""
        return (self.current_price - self.entry_price) / self.entry_price

    @property
def drift(self) -> float:
        """权重偏离"""
        return self.weight - self.target_weight

    @property
def is_stop_loss_triggered(self) -> bool:
        """是否触发止损"""
        if self.stop_loss_price <= 0:
            return False
        return self.current_price <= self.stop_loss_price

    @property
def is_profit_target_reached(self) -> bool:
        """是否达到止盈"""
        if self.target_price <= 0:
            return False
        return self.current_price >= self.target_price


@dataclass
class PortfolioAnalysis:
    """组合分析结果"""

    watchlist_id: int
    watchlist_name: str
    analysis_date: datetime

    total_score: float
    radar_averages: Dict[str, float]
    risk_score: float

    positions: List[PortfolioPosition]
    sector_allocation: Dict[str, float]

    alerts: List[Dict[str, Any]] = field(default_factory=list)
    rebalance_suggestions: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PortfolioOptimizerConfig:
    """组合优化器配置"""

    rebalance_threshold: float = 0.05  # 再平衡阈值 5%
    stop_loss_buffer: float = 0.02  # 止损缓冲 2%
    profit_target_buffer: float = 0.03  # 止盈缓冲 3%
    max_weight: float = 0.40  # 单只股票最大权重
    min_weight: float = 0.02  # 单只股票最小权重

    risk_warning_threshold: float = 0.70  # 风险评分警告阈值
    risk_critical_threshold: float = 0.85  # 风险评分紧急阈值


class PortfolioOptimizer:
    """
    投资组合优化器
    """

def __init__(self, config: Optional[PortfolioOptimizerConfig] = None):
        self.config = config or PortfolioOptimizerConfig()

def analyze_portfolio(
        self,
        watchlist_id: int,
        watchlist_name: str,
        positions: List[Dict[str, Any]],
        health_scores: List[Dict[str, Any]],
    ) -> PortfolioAnalysis:
        """
        分析组合健康度

        Args:
            watchlist_id: 清单ID
            watchlist_name: 清单名称
            positions: 持仓列表
            health_scores: 健康度评分列表

        Returns:
            PortfolioAnalysis: 分析结果
        """
        portfolio_positions = self._build_positions(positions)

        radar_averages = self._calculate_radar_averages(health_scores)

        total_score = self._calculate_total_score(radar_averages)

        sector_allocation = self._calculate_sector_allocation(positions)

        alerts = self._generate_alerts(portfolio_positions)

        rebalance_suggestions = self._generate_rebalance_suggestions(portfolio_positions, health_scores)

        risk_score = self._calculate_risk_score(portfolio_positions, radar_averages)

        return PortfolioAnalysis(
            watchlist_id=watchlist_id,
            watchlist_name=watchlist_name,
            analysis_date=datetime.now(),
            total_score=total_score,
            radar_averages=radar_averages,
            risk_score=risk_score,
            positions=portfolio_positions,
            sector_allocation=sector_allocation,
            alerts=alerts,
            rebalance_suggestions=rebalance_suggestions,
        )

def _build_positions(self, positions: List[Dict[str, Any]]) -> List[PortfolioPosition]:
        """构建持仓对象列表"""
        return [
            PortfolioPosition(
                stock_code=p["stock_code"],
                weight=p.get("weight", 0),
                entry_price=p.get("entry_price", 0),
                current_price=p.get("current_price", p.get("entry_price", 0)),
                target_weight=p.get("target_weight", p.get("weight", 0)),
                stop_loss_price=p.get("stop_loss_price", 0),
                target_price=p.get("target_price", 0),
            )
            for p in positions
        ]

def _calculate_radar_averages(self, health_scores: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算五维平均分"""
        if not health_scores:
            return {
                "trend": 50.0,
                "technical": 50.0,
                "momentum": 50.0,
                "volatility": 50.0,
                "risk": 50.0,
            }

        scores: Dict[str, List[float]] = {
            "trend": [],
            "technical": [],
            "momentum": [],
            "volatility": [],
            "risk": [],
        }

        for hs in health_scores:
            radar = hs.get("radar_scores", {})
            for dim in scores:
                if dim in radar:
                    # Convert Decimal to float to avoid type errors
                    scores[dim].append(float(radar[dim]))

        return {k: float(np.mean(v)) if v else 50.0 for k, v in scores.items()}

def _calculate_total_score(self, radar_averages: Dict[str, float]) -> float:
        """计算总分"""
        weights = {"trend": 0.25, "technical": 0.25, "momentum": 0.20, "volatility": 0.15, "risk": 0.15}
        return sum(float(radar_averages.get(k, 50)) * v for k, v in weights.items())

def _calculate_sector_allocation(self, positions: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算行业配置"""
        sector_weights: Dict[str, float] = {}
        total_weight = sum(p.get("weight", 0) for p in positions)

        for p in positions:
            sector = p.get("sector", "Unknown")
            weight = p.get("weight", 0)
            sector_weights[sector] = sector_weights.get(sector, 0) + weight

        if total_weight > 0:
            sector_weights = {k: v / total_weight for k, v in sector_weights.items()}

        return sector_weights

def _calculate_risk_score(self, positions: List[PortfolioPosition], radar_averages: Dict[str, float]) -> float:
        """计算风险评分"""
        if not positions:
            return 50.0

        concentration_risk = max(p.weight for p in positions)

        volatility_penalty = max(0, float(radar_averages.get("volatility", 50)) - 50.0) / 50.0

        risk_score = (
            0.4 * (1 - concentration_risk) * 100
            + 0.3 * (100 - float(radar_averages.get("risk", 50)))
            + 0.3 * (1 - volatility_penalty) * 100
        )

        return float(np.clip(risk_score, 0, 100))

def _generate_alerts(self, positions: List[PortfolioPosition]) -> List[Dict[str, Any]]:
        """生成预警列表"""
        alerts = []

        for pos in positions:
            if pos.is_stop_loss_triggered:
                alerts.append(
                    {
                        "level": AlertLevel.CRITICAL.value,
                        "type": "stop_loss",
                        "stock_code": pos.stock_code,
                        "message": f"🔴 {pos.stock_code} 触发止损",
                        "details": {
                            "current_price": pos.current_price,
                            "stop_loss_price": pos.stop_loss_price,
                            "unrealized_pnl": pos.unrealized_pnl,
                        },
                    }
                )

            elif pos.is_profit_target_reached:
                alerts.append(
                    {
                        "level": AlertLevel.WARNING.value,
                        "type": "profit_target",
                        "stock_code": pos.stock_code,
                        "message": f"🟡 {pos.stock_code} 达到止盈目标",
                        "details": {
                            "current_price": pos.current_price,
                            "target_price": pos.target_price,
                            "unrealized_pnl": pos.unrealized_pnl,
                        },
                    }
                )

            if abs(pos.drift) > self.config.rebalance_threshold:
                alerts.append(
                    {
                        "level": AlertLevel.INFO.value,
                        "type": "weight_drift",
                        "stock_code": pos.stock_code,
                        "message": f"🟢 {pos.stock_code} 权重偏离 {(pos.drift * 100):.1f}%",
                        "details": {
                            "current_weight": pos.weight,
                            "target_weight": pos.target_weight,
                            "drift": pos.drift,
                        },
                    }
                )

        return sorted(alerts, key=lambda x: ["info", "warning", "critical"].index(x["level"]))

def _generate_rebalance_suggestions(
        self, positions: List[PortfolioPosition], health_scores: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成再平衡建议"""
        suggestions = []

        score_map = {hs["stock_code"]: hs for hs in health_scores}

        for pos in positions:
            stock_code = pos.stock_code
            health = score_map.get(stock_code, {})
            total_score = health.get("total_score", 50)

            if abs(pos.drift) > self.config.rebalance_threshold:
                drift_action = "减仓" if pos.drift > 0 else "加仓"
                suggestions.append(
                    {
                        "reason": RebalanceReason.DRIFT_THRESHOLD.value,
                        "priority": "high" if abs(pos.drift) > 0.1 else "medium",
                        "stock_code": stock_code,
                        "action": drift_action,
                        "current_weight": pos.weight,
                        "target_weight": pos.target_weight,
                        "message": f"{stock_code} 权重偏离 {(pos.drift * 100):.1f}%，建议{drift_action}",
                        "estimated_cost": abs(pos.drift) * 0.001,
                    }
                )

            if total_score < 40:
                suggestions.append(
                    {
                        "reason": RebalanceReason.RISK_THRESHOLD.value,
                        "priority": "high",
                        "stock_code": stock_code,
                        "action": "减仓/清仓",
                        "current_weight": pos.weight,
                        "target_weight": max(0, pos.weight - 0.1),
                        "message": f"{stock_code} 健康度评分过低 ({total_score:.1f})，建议减仓",
                        "estimated_cost": pos.weight * 0.001,
                    }
                )

            if pos.is_stop_loss_triggered:
                suggestions.append(
                    {
                        "reason": RebalanceReason.STOP_LOSS.value,
                        "priority": "critical",
                        "stock_code": stock_code,
                        "action": "清仓",
                        "current_weight": pos.weight,
                        "target_weight": 0,
                        "message": f"{stock_code} 触发止损，建议清仓",
                        "estimated_cost": pos.weight * 0.001,
                    }
                )

        suggestions.sort(key=lambda x: ["info", "medium", "high", "critical"].index(str(x.get("priority", "info"))))

        return suggestions

def get_portfolio_summary(self, analysis: PortfolioAnalysis) -> Dict[str, Any]:
        """获取组合摘要"""
        return {
            "watchlist_id": analysis.watchlist_id,
            "watchlist_name": analysis.watchlist_name,
            "analysis_date": analysis.analysis_date.isoformat(),
            "total_score": {
                "average": round(analysis.total_score, 2),
            },
            "radar_averages": analysis.radar_averages,
            "risk_score": round(analysis.risk_score, 2),
            "position_count": len(analysis.positions),
            "sector_allocation": analysis.sector_allocation,
            "alert_summary": {
                "critical": len([a for a in analysis.alerts if a["level"] == "critical"]),
                "warning": len([a for a in analysis.alerts if a["level"] == "warning"]),
                "info": len([a for a in analysis.alerts if a["level"] == "info"]),
            },
            "rebalance_count": len(analysis.rebalance_suggestions),
        }


def get_portfolio_optimizer(config: Optional[PortfolioOptimizerConfig] = None) -> PortfolioOptimizer:
    """获取组合优化器实例"""
    return PortfolioOptimizer(config)
