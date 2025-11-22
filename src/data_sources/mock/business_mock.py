"""
Mock业务数据源实现

本模块实现IBusinessDataSource接口的Mock版本。
业务数据源协调时序和关系数据源，提供复合查询和业务聚合功能。

作者: MyStocks Backend Team
创建日期: 2025-11-21
版本: 1.0.0
"""

import random
from typing import List, Dict, Optional, Any
from datetime import date, datetime, timedelta
import pandas as pd
from faker import Faker

from src.interfaces.business_data_source import IBusinessDataSource
from src.interfaces.timeseries_data_source import ITimeSeriesDataSource
from src.interfaces.relational_data_source import IRelationalDataSource


class MockBusinessDataSource(IBusinessDataSource):
    """Mock业务数据源实现"""

    def __init__(
        self,
        timeseries_source: Optional[ITimeSeriesDataSource] = None,
        relational_source: Optional[IRelationalDataSource] = None,
        seed: Optional[int] = None
    ):
        """
        初始化Mock业务数据源

        Args:
            timeseries_source: 时序数据源实例
            relational_source: 关系数据源实例
            seed: 随机种子
        """
        self.fake = Faker('zh_CN')
        if seed is not None:
            Faker.seed(seed)
            random.seed(seed)

        # 如果未提供数据源，创建Mock实例
        if timeseries_source is None:
            from src.data_sources.mock.timeseries_mock import MockTimeSeriesDataSource
            timeseries_source = MockTimeSeriesDataSource(seed=seed)

        if relational_source is None:
            from src.data_sources.mock.relational_mock import MockRelationalDataSource
            relational_source = MockRelationalDataSource(seed=seed)

        self.ts = timeseries_source
        self.rel = relational_source

        # 内存存储回测结果
        self._backtest_results: Dict[str, Dict] = {}

    def get_dashboard_summary(
        self,
        user_id: int,
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取仪表盘汇总数据"""
        # 获取市场概览
        market_overview = self.ts.get_market_overview()

        # 获取用户自选股
        watchlist = self.rel.get_watchlist(user_id)

        # 计算自选股表现（简化版）
        watchlist_performance = []
        if watchlist:
            symbols = [item["symbol"] for item in watchlist[:10]]
            quotes = self.ts.get_realtime_quotes(symbols=symbols)
            for quote in quotes:
                watchlist_performance.append({
                    "symbol": quote["symbol"],
                    "name": quote["name"],
                    "price": quote["price"],
                    "change_percent": quote["change_percent"]
                })

        # 获取资金流向排名
        top_fund_flow = self.ts.get_top_fund_flow_stocks(limit=10)

        # 数据状态
        data_status = {
            "last_update": datetime.now().isoformat(),
            "market_status": "trading" if datetime.now().hour < 15 else "closed",
            "data_freshness": "real-time"
        }

        return {
            "market_overview": market_overview,
            "watchlist_performance": watchlist_performance,
            "top_fund_flow": top_fund_flow[:10],
            "data_status": data_status,
            "user_stats": {
                "watchlist_count": len(watchlist),
                "strategy_count": len(self.rel.get_strategy_configs(user_id)),
                "alert_count": len(self.rel.get_risk_alerts(user_id))
            }
        }

    def get_sector_performance(
        self,
        sector_type: str = "industry",
        trade_date: Optional[date] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """获取板块表现"""
        if trade_date is None:
            trade_date = date.today()

        if sector_type == "industry":
            sectors = self.rel.get_industry_list()
        else:  # concept
            sectors = self.rel.get_concept_list()

        # 为每个板块生成模拟表现数据
        sector_performance = []
        for sector in sectors[:limit]:
            # 获取板块内的股票
            if sector_type == "industry":
                stocks = self.rel.get_stocks_by_industry(sector["code"], limit=5)
            else:
                stocks = self.rel.get_stocks_by_concept(sector["code"], limit=5)

            # 生成板块统计
            avg_change = round(random.uniform(-5.0, 5.0), 2)
            sector_performance.append({
                "sector_code": sector["code"],
                "sector_name": sector["name"],
                "avg_change_percent": avg_change,
                "up_stocks": random.randint(0, len(stocks)),
                "down_stocks": random.randint(0, len(stocks)),
                "total_stocks": len(stocks),
                "top_stocks": stocks[:3],
                "leader_symbol": stocks[0]["symbol"] if stocks else None,
                "total_amount": round(random.uniform(1000000000, 50000000000), 2)
            })

        # 排序
        sector_performance.sort(key=lambda x: x["avg_change_percent"], reverse=True)

        return {
            "trade_date": trade_date.isoformat(),
            "sector_type": sector_type,
            "sectors": sector_performance,
            "summary": {
                "up_sectors": sum(1 for s in sector_performance if s["avg_change_percent"] > 0),
                "down_sectors": sum(1 for s in sector_performance if s["avg_change_percent"] < 0)
            }
        }

    def execute_backtest(
        self,
        user_id: int,
        strategy_config: Dict[str, Any],
        symbols: List[str],
        start_date: date,
        end_date: date,
        initial_capital: float = 1000000.0
    ) -> Dict[str, Any]:
        """执行策略回测"""
        # 生成回测ID
        backtest_id = f"BT_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}"

        # 简化的回测模拟
        days = (end_date - start_date).days

        # 生成交易记录
        trades = []
        num_trades = random.randint(10, 50)
        for i in range(num_trades):
            trade_date = start_date + timedelta(days=random.randint(0, days))
            symbol = random.choice(symbols)
            trades.append({
                "trade_id": i + 1,
                "symbol": symbol,
                "action": random.choice(["buy", "sell"]),
                "price": round(random.uniform(10.0, 100.0), 2),
                "quantity": random.randint(100, 10000),
                "trade_date": trade_date.isoformat(),
                "commission": round(random.uniform(5.0, 50.0), 2)
            })

        # 生成持仓记录
        positions = []
        for symbol in symbols[:5]:
            positions.append({
                "symbol": symbol,
                "quantity": random.randint(100, 5000),
                "avg_cost": round(random.uniform(10.0, 50.0), 2),
                "current_price": round(random.uniform(10.0, 50.0), 2),
                "profit_loss": round(random.uniform(-10000, 50000), 2),
                "profit_loss_percent": round(random.uniform(-20.0, 50.0), 2)
            })

        # 生成权益曲线
        equity_curve = []
        current_equity = initial_capital
        for i in range(0, days, 7):  # 每周一个数据点
            date_point = start_date + timedelta(days=i)
            change = random.uniform(-0.02, 0.03)  # ±2-3%波动
            current_equity *= (1 + change)
            equity_curve.append({
                "date": date_point.isoformat(),
                "equity": round(current_equity, 2),
                "cumulative_return": round(((current_equity / initial_capital) - 1) * 100, 2)
            })

        # 生成回测结果
        final_equity = equity_curve[-1]["equity"] if equity_curve else initial_capital
        total_return = ((final_equity / initial_capital) - 1) * 100

        result = {
            "backtest_id": backtest_id,
            "user_id": user_id,
            "strategy_config": strategy_config,
            "symbols": symbols,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "initial_capital": initial_capital,
            "final_equity": round(final_equity, 2),
            "total_return": round(total_return, 2),
            "annual_return": round(total_return / (days / 365), 2),
            "max_drawdown": round(random.uniform(-15.0, -5.0), 2),
            "sharpe_ratio": round(random.uniform(0.5, 2.5), 2),
            "win_rate": round(random.uniform(0.45, 0.65), 2),
            "total_trades": len(trades),
            "trades": trades,
            "positions": positions,
            "equity_curve": equity_curve,
            "create_time": datetime.now().isoformat()
        }

        # 保存回测结果
        self._backtest_results[backtest_id] = result

        return result

    def get_backtest_results(
        self,
        user_id: int,
        backtest_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """获取回测结果"""
        if backtest_id:
            result = self._backtest_results.get(backtest_id)
            return [result] if result and result["user_id"] == user_id else []

        # 返回用户的所有回测结果
        user_results = [
            r for r in self._backtest_results.values()
            if r["user_id"] == user_id
        ]

        # 按创建时间排序
        user_results.sort(key=lambda x: x["create_time"], reverse=True)

        return user_results[:limit]

    def calculate_risk_metrics(
        self,
        user_id: int,
        portfolio: List[Dict[str, Any]],
        confidence_level: float = 0.95
    ) -> Dict[str, Any]:
        """计算风险指标"""
        # 简化的风险计算
        total_value = sum(p["quantity"] * p["price"] for p in portfolio)

        # 计算各类风险指标
        risk_metrics = {
            "var_1day": round(total_value * random.uniform(0.01, 0.03), 2),
            "var_5day": round(total_value * random.uniform(0.02, 0.05), 2),
            "cvar_1day": round(total_value * random.uniform(0.015, 0.04), 2),
            "volatility_annual": round(random.uniform(0.15, 0.35), 2),
            "beta": round(random.uniform(0.8, 1.2), 2),
            "concentration_risk": {
                "top1_weight": round(random.uniform(0.15, 0.30), 2),
                "top3_weight": round(random.uniform(0.35, 0.60), 2),
                "top5_weight": round(random.uniform(0.50, 0.80), 2)
            },
            "industry_exposure": {
                "银行": round(random.uniform(0.0, 0.20), 2),
                "证券": round(random.uniform(0.0, 0.15), 2),
                "医药": round(random.uniform(0.0, 0.10), 2),
                "电子": round(random.uniform(0.0, 0.15), 2),
                "其他": round(random.uniform(0.40, 0.60), 2)
            },
            "stress_test": {
                "market_crash_10pct": round(-total_value * 0.10, 2),
                "market_crash_20pct": round(-total_value * 0.20, 2),
                "sector_rotation": round(random.uniform(-0.05, 0.05) * total_value, 2)
            }
        }

        return risk_metrics

    def check_risk_alerts(
        self,
        user_id: int,
        portfolio: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """检查风险预警"""
        # 获取用户配置的预警
        alerts = self.rel.get_risk_alerts(user_id, is_active=True)

        triggered_alerts = []
        for alert in alerts:
            # 简化的预警检查
            is_triggered = random.choice([True, False, False])  # 33%触发概率

            if is_triggered:
                triggered_alerts.append({
                    "alert_id": alert["id"],
                    "alert_name": alert["alert_name"],
                    "alert_type": alert["alert_type"],
                    "trigger_value": round(random.uniform(0.0, 100.0), 2),
                    "threshold": alert["condition"].get("threshold", 0),
                    "message": f"{alert['alert_name']} 触发预警",
                    "severity": random.choice(["low", "medium", "high"]),
                    "trigger_time": datetime.now().isoformat()
                })

        return triggered_alerts

    def analyze_trading_signals(
        self,
        user_id: int,
        strategy_ids: List[str],
        symbols: Optional[List[str]] = None,
        trade_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """分析交易信号"""
        if trade_date is None:
            trade_date = date.today()

        # 获取策略配置
        strategies = self.rel.get_strategy_configs(user_id, status="active")
        active_strategies = [s for s in strategies if s["id"] in strategy_ids]

        # 生成交易信号
        signals = []
        for strategy in active_strategies:
            # 为每个策略生成几个信号
            num_signals = random.randint(0, 5)
            for _ in range(num_signals):
                symbol = random.choice(symbols) if symbols else f"60{random.randint(0, 9999):04d}"
                signals.append({
                    "signal_id": f"SIG_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
                    "strategy_id": strategy["id"],
                    "strategy_name": strategy["strategy_name"],
                    "symbol": symbol,
                    "signal_type": random.choice(["buy", "sell", "hold"]),
                    "signal_strength": round(random.uniform(0.5, 1.0), 2),
                    "target_price": round(random.uniform(10.0, 100.0), 2),
                    "stop_loss": round(random.uniform(8.0, 15.0), 2),
                    "take_profit": round(random.uniform(12.0, 120.0), 2),
                    "reason": self.fake.sentence(),
                    "confidence": round(random.uniform(0.6, 0.95), 2),
                    "generate_time": datetime.now().isoformat()
                })

        return signals

    def get_portfolio_analysis(
        self,
        user_id: int,
        portfolio: List[Dict[str, Any]],
        benchmark: str = "sh000001"
    ) -> Dict[str, Any]:
        """获取组合分析"""
        # 计算组合总值
        total_value = sum(p["quantity"] * p["price"] for p in portfolio)
        total_cost = sum(p["quantity"] * p["avg_cost"] for p in portfolio)
        total_profit = total_value - total_cost
        total_return = ((total_value / total_cost) - 1) * 100 if total_cost > 0 else 0

        # 持仓分析
        holdings = []
        for p in portfolio:
            value = p["quantity"] * p["price"]
            cost = p["quantity"] * p["avg_cost"]
            holdings.append({
                **p,
                "value": round(value, 2),
                "cost": round(cost, 2),
                "weight": round((value / total_value) * 100, 2) if total_value > 0 else 0,
                "profit_loss": round(value - cost, 2),
                "profit_loss_percent": round(((value / cost) - 1) * 100, 2) if cost > 0 else 0
            })

        # 排序
        holdings.sort(key=lambda x: x["value"], reverse=True)

        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "total_return": round(total_return, 2),
            "holdings": holdings,
            "performance": {
                "1day_return": round(random.uniform(-3.0, 3.0), 2),
                "1week_return": round(random.uniform(-5.0, 5.0), 2),
                "1month_return": round(random.uniform(-10.0, 10.0), 2),
                "ytd_return": round(random.uniform(-15.0, 25.0), 2)
            },
            "benchmark_comparison": {
                "benchmark_code": benchmark,
                "portfolio_return": round(total_return, 2),
                "benchmark_return": round(random.uniform(-5.0, 15.0), 2),
                "alpha": round(random.uniform(-2.0, 5.0), 2),
                "tracking_error": round(random.uniform(2.0, 8.0), 2)
            }
        }

    def perform_attribution_analysis(
        self,
        user_id: int,
        portfolio: List[Dict[str, Any]],
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """执行归因分析"""
        # 简化的归因分析
        total_return = round(random.uniform(-10.0, 20.0), 2)

        attribution = {
            "total_return": total_return,
            "sector_attribution": {
                "银行": round(random.uniform(-2.0, 3.0), 2),
                "证券": round(random.uniform(-1.0, 4.0), 2),
                "医药": round(random.uniform(-1.5, 2.5), 2),
                "电子": round(random.uniform(-2.0, 5.0), 2),
                "其他": round(random.uniform(-3.0, 3.0), 2)
            },
            "stock_attribution": [],
            "allocation_effect": round(random.uniform(-2.0, 2.0), 2),
            "selection_effect": round(random.uniform(-3.0, 5.0), 2),
            "interaction_effect": round(random.uniform(-1.0, 1.0), 2)
        }

        # 为每只股票生成归因
        for p in portfolio[:10]:
            attribution["stock_attribution"].append({
                "symbol": p["symbol"],
                "contribution": round(random.uniform(-2.0, 5.0), 2),
                "weight_effect": round(random.uniform(-1.0, 1.0), 2),
                "return_effect": round(random.uniform(-2.0, 4.0), 2)
            })

        return attribution

    def execute_stock_screener(
        self,
        criteria: Dict[str, Any],
        sort_by: str = "market_cap",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """执行股票筛选"""
        # 获取所有股票
        all_stocks = []
        industries = self.rel.get_industry_list()
        for industry in industries:
            stocks = self.rel.get_stocks_by_industry(industry["code"], limit=50)
            all_stocks.extend(stocks)

        # 简化的筛选逻辑（实际应根据criteria过滤）
        filtered_stocks = all_stocks[:limit]

        # 为每只股票添加评分和指标
        results = []
        for stock in filtered_stocks:
            results.append({
                "symbol": stock["symbol"],
                "name": stock["name"],
                "industry": stock["industry"],
                "market_cap": round(random.uniform(1000000000, 500000000000), 2),
                "pe_ratio": round(random.uniform(5.0, 50.0), 2),
                "pb_ratio": round(random.uniform(0.5, 10.0), 2),
                "roe": round(random.uniform(0.05, 0.30), 2),
                "revenue_growth": round(random.uniform(-0.10, 0.50), 2),
                "profit_margin": round(random.uniform(0.02, 0.30), 2),
                "score": round(random.uniform(60.0, 95.0), 2)
            })

        # 排序
        if sort_by == "market_cap":
            results.sort(key=lambda x: x["market_cap"], reverse=True)
        elif sort_by == "score":
            results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def health_check(self) -> Dict[str, Any]:
        """业务数据源健康检查"""
        ts_health = self.ts.health_check()
        rel_health = self.rel.health_check()

        return {
            "status": "healthy" if ts_health["status"] == "healthy" and rel_health["status"] == "healthy" else "degraded",
            "data_source_type": "mock_composite",
            "components": {
                "timeseries": ts_health,
                "relational": rel_health
            },
            "business_metrics": {
                "total_backtests": len(self._backtest_results)
            }
        }
