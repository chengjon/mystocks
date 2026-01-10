"""
Portfolio Application Service
组合管理应用服务

提供投资组合管理的应用层接口。
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.application.portfolio.model import Portfolio, Holding, Transaction
from src.application.portfolio.repository import IPortfolioRepository
from src.domain.portfolio.value_objects import PerformanceMetrics

logger = logging.getLogger(__name__)


class PortfolioApplicationService:
    """
    组合管理应用服务

    职责：
    - 组合CRUD操作
    - 持仓管理
    - 绩效分析
    - 风控监控
    """

    def __init__(self, portfolio_repo: IPortfolioRepository, data_source_manager=None):
        self.portfolio_repo = portfolio_repo
        self.data_source_manager = data_source_manager

    def create_portfolio(
        self,
        name: str,
        portfolio_type: str,
        initial_capital: float,
        description: str = "",
        benchmark_index: str = "000300",
    ) -> Dict[str, Any]:
        """创建投资组合"""
        portfolio = Portfolio.create(
            name=name,
            portfolio_type=portfolio_type,
            initial_capital=initial_capital,
            description=description,
            benchmark_index=benchmark_index,
        )
        self.portfolio_repo.save(portfolio)
        logger.info(f"Created portfolio: {portfolio.id}")
        return portfolio.to_dict()

    def get_portfolio(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """获取投资组合"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            return None
        return portfolio.to_dict()

    def list_portfolios(self, portfolio_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """列出投资组合"""
        portfolios = self.portfolio_repo.find_all(limit)
        if portfolio_type:
            portfolios = [p for p in portfolios if p.portfolio_type == portfolio_type]
        return [p.to_dict() for p in portfolios]

    def delete_portfolio(self, portfolio_id: str) -> bool:
        """删除投资组合"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            return False
        self.portfolio_repo.delete(portfolio_id)
        logger.info(f"Deleted portfolio: {portfolio_id}")
        return True

    def add_position(
        self, portfolio_id: str, symbol: str, quantity: int, price: float, side: str = "LONG"
    ) -> Dict[str, Any]:
        """添加持仓"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"组合不存在: {portfolio_id}")

        holding = portfolio.add_holding(symbol, quantity, price, side)
        self.portfolio_repo.save(portfolio)

        self._record_transaction(portfolio, symbol, side, quantity, price)

        logger.info(f"Added position {symbol} to portfolio {portfolio_id}")
        return holding.to_dict()

    def adjust_position(
        self, portfolio_id: str, symbol: str, quantity_change: int, price: float, side: str = "LONG"
    ) -> Optional[Dict[str, Any]]:
        """调整持仓"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"组合不存在: {portfolio_id}")

        holding = portfolio.update_holding(symbol, quantity_change, price, side)
        if holding:
            self.portfolio_repo.save(portfolio)
            self._record_transaction(
                portfolio, symbol, side if quantity_change > 0 else "SELL", abs(quantity_change), price
            )
            logger.info(f"Adjusted position {symbol} in portfolio {portfolio_id}")
        return holding.to_dict() if holding else None

    def close_position(self, portfolio_id: str, symbol: str, price: float) -> bool:
        """清仓持仓"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"组合不存在: {portfolio_id}")

        holding = portfolio.get_holding(symbol)
        if not holding:
            return False

        self._record_transaction(portfolio, symbol, "SELL", holding.quantity, price)
        portfolio.remove_holding(symbol)
        self.portfolio_repo.save(portfolio)
        logger.info(f"Closed position {symbol} in portfolio {portfolio_id}")
        return True

    def update_prices(self, portfolio_id: str, prices: Dict[str, float]) -> None:
        """更新持仓价格"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"组合不存在: {portfolio_id}")

        for symbol, price in prices.items():
            holding = portfolio.get_holding(symbol)
            if holding:
                holding.update_price(price)

        self.portfolio_repo.save(portfolio)
        logger.info(f"Updated prices for portfolio {portfolio_id}")

    def get_performance(self, portfolio_id: str) -> Optional[Dict[str, Any]]:
        """获取绩效指标"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            return None

        metrics = portfolio.get_performance_metrics()
        return {
            "portfolio_id": portfolio_id,
            "portfolio_name": portfolio.name,
            "total_return": round(metrics.total_return, 2),
            "holdings_value": round(metrics.holdings_value, 2),
            "cash_balance": round(metrics.cash_balance, 2),
            "win_rate": round(metrics.win_rate, 2),
            "trade_count": metrics.trade_count,
            "current_value": portfolio.current_value,
        }

    def get_allocation(self, portfolio_id: str) -> Dict[str, Any]:
        """获取配置分析"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"组合不存在: {portfolio_id}")

        return {
            "portfolio_id": portfolio_id,
            "sector_allocation": portfolio.get_sector_allocation(),
            "position_concentration": portfolio.get_position_concentration(),
            "holdings": [h.to_dict() for h in portfolio.get_all_holdings()],
        }

    def get_holdings(self, portfolio_id: str) -> List[Dict[str, Any]]:
        """获取持仓列表"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            return []
        return [h.to_dict() for h in portfolio.get_all_holdings()]

    def get_transactions(self, portfolio_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取交易记录"""
        portfolio = self.portfolio_repo.find_by_id(portfolio_id)
        if not portfolio:
            return []
        transactions = sorted(portfolio.transactions, key=lambda t: t.timestamp, reverse=True)
        return [t.to_dict() for t in transactions[:limit]]

    def _record_transaction(self, portfolio: Portfolio, symbol: str, side: str, quantity: int, price: float) -> None:
        """记录交易"""
        txn = Transaction.create(portfolio_id=portfolio.id, symbol=symbol, side=side, quantity=quantity, price=price)
        portfolio.transactions.append(txn)


def create_portfolio_service(
    portfolio_repo: IPortfolioRepository, data_source_manager=None
) -> PortfolioApplicationService:
    """工厂方法：创建组合管理服务"""
    return PortfolioApplicationService(portfolio_repo=portfolio_repo, data_source_manager=data_source_manager)
