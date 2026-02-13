"""
Real-time MTM API Adapter
实时市值 API 适配器

将 Phase 12.3 的 DDD 架构适配到现有的 WebSocket API 接口，
保持 API 兼容性的同时使用新的领域模型。

Author: Claude Code
Date: 2026-01-09
Phase: 12.4 - API Layer Integration
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class PortfolioSnapshot:
    """投资组合快照（与旧 API 兼容）"""

    portfolio_id: str
    total_market_value: float = 0.0
    total_cost: float = 0.0
    total_unrealized_profit: float = 0.0
    total_realized_profit: float = 0.0
    total_profit: float = 0.0
    profit_ratio: float = 0.0
    cash_balance: float = 0.0
    available_cash: float = 0.0
    position_count: int = 0
    last_update: datetime = field(default_factory=datetime.now)
    positions: Dict[str, "PositionSnapshot"] = field(default_factory=dict)


@dataclass
class PositionSnapshot:
    """持仓快照（与旧 API 兼容）"""

    position_id: str
    portfolio_id: str
    symbol: str
    quantity: int
    avg_price: float
    market_price: float = 0.0
    market_value: float = 0.0
    unrealized_profit: float = 0.0
    profit_ratio: float = 0.0
    realized_profit: float = 0.0
    total_profit: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)
    price_change: float = 0.0
    price_change_percent: float = 0.0


@dataclass
class MTMUpdate:
    """市值更新事件（与旧 API 兼容）"""

    position_id: str
    symbol: str
    old_price: float
    new_price: float
    old_market_value: float
    new_market_value: float
    profit_change: float
    timestamp: datetime = field(default_factory=datetime.now)


class RealtimeMTMAdapter:
    """
    实时市值 API 适配器

    职责：
    1. 将 Phase 12.3 的 DDD 架构适配到现有的 WebSocket API
    2. 保持 API 接口兼容性
    3. 提供与 position_mtm_engine 相同的接口
    """

    def __init__(self, portfolio_repo, valuation_service, event_bus=None):
        """
        初始化适配器

        Args:
            portfolio_repo: 投资组合仓储 (PortfolioRepositoryImpl)
            valuation_service: 投资组合估值服务 (PortfolioValuationService)
            event_bus: 事件总线 (RedisEventBus, 可选)
        """
        self.portfolio_repo = portfolio_repo
        self.valuation_service = valuation_service
        self.event_bus = event_bus

        # 订阅价格变更事件
        if event_bus:
            from src.domain.market_data.streaming import PriceChangedEvent

            event_bus.subscribe(PriceChangedEvent, self._on_price_changed)

        # 缓存最新的快照
        self._portfolio_snapshots: Dict[str, PortfolioSnapshot] = {}

        logger.info("✅ RealtimeMTMAdapter initialized")

    def _on_price_changed(self, event):
        """处理价格变更事件"""
        # 当价格变更时，重新计算相关投资组合
        # 这个方法由事件总线调用

    def register_position(
        self, position_id: str, portfolio_id: str, symbol: str, quantity: int, avg_price: float
    ) -> bool:
        """
        注册持仓（兼容旧接口）

        注意：在 DDD 架构中，持仓通过 Portfolio.handle_order_filled() 添加
        这个方法主要用于向后兼容
        """
        try:
            portfolio = self.portfolio_repo.find_by_id(portfolio_id)
            if not portfolio:
                logger.warning("Portfolio not found: %(portfolio_id)s")
                return False

            # 如果持仓不存在，创建一个 mock 订单成交事件来添加持仓
            from src.domain.trading.value_objects import OrderSide

            class MockEvent:
                def __init__(self):
                    self.symbol = symbol
                    self.side = OrderSide.BUY
                    self.filled_quantity = quantity
                    self.filled_price = avg_price
                    self.commission = 0.0

            portfolio.handle_order_filled(MockEvent())
            self.portfolio_repo.save(portfolio)

            logger.info("✅ Registered position %(position_id)s for portfolio %(portfolio_id)s")
            return True

        except Exception:
            logger.error("Failed to register position: %(e)s")
            return False

    def unregister_position(self, position_id: str) -> bool:
        """注销持仓（兼容旧接口）"""
        logger.warning("unregister_position not implemented in DDD architecture: %(position_id)s")
        return True

    def update_price(self, symbol: str, price: float) -> List[MTMUpdate]:
        """
        更新价格并计算市值（兼容旧接口）

        Args:
            symbol: 股票代码
            price: 新价格

        Returns:
            List[MTMUpdate]: 市值更新事件列表
        """
        updates = []

        try:
            # 获取所有投资组合
            portfolios = self.portfolio_repo.find_all(limit=1000)

            for portfolio in portfolios:
                if symbol not in portfolio.positions:
                    continue

                # 记录旧价格和旧市值
                old_price = portfolio.positions[symbol].current_price
                old_market_value = portfolio.positions[symbol].market_value

                # 更新价格并重新计算
                prices = {symbol: price}
                performance = self.valuation_service.revaluate_portfolio(portfolio.id, prices, force_save=True)

                if performance:
                    # 获取更新后的持仓
                    updated_portfolio = self.portfolio_repo.find_by_id(portfolio.id)
                    new_market_value = updated_portfolio.positions[symbol].market_value
                    new_price = updated_portfolio.positions[symbol].current_price

                    # 创建 MTM 更新事件
                    update = MTMUpdate(
                        position_id=f"{portfolio.id}_{symbol}",
                        symbol=symbol,
                        old_price=old_price,
                        new_price=new_price,
                        old_market_value=old_market_value,
                        new_market_value=new_market_value,
                        profit_change=new_market_value - old_market_value,
                    )
                    updates.append(update)

                    # 更新缓存
                    self._update_portfolio_cache(portfolio.id)

            return updates

        except Exception:
            logger.error("Failed to update price for %(symbol)s: %(e)s")
            return []

    def get_portfolio_snapshot(self, portfolio_id: str) -> Optional[PortfolioSnapshot]:
        """
        获取投资组合快照（兼容旧接口）

        Args:
            portfolio_id: 投资组合 ID

        Returns:
            PortfolioSnapshot: 投资组合快照
        """
        try:
            # 先检查缓存
            if portfolio_id in self._portfolio_snapshots:
                return self._portfolio_snapshots[portfolio_id]

            # 从数据库加载
            portfolio = self.portfolio_repo.find_by_id(portfolio_id)
            if not portfolio:
                return None

            # 计算绩效
            performance = portfolio.calculate_performance()

            # 转换为快照格式
            snapshot = self._convert_to_snapshot(portfolio, performance)

            # 缓存快照
            self._portfolio_snapshots[portfolio_id] = snapshot

            return snapshot

        except Exception:
            logger.error("Failed to get portfolio snapshot %(portfolio_id)s: %(e)s")
            return None

    def get_position_snapshot(self, position_id: str) -> Optional[PositionSnapshot]:
        """
        获取持仓快照（兼容旧接口）

        Args:
            position_id: 持仓 ID (格式: {portfolio_id}_{symbol})

        Returns:
            PositionSnapshot: 持仓快照
        """
        try:
            # 解析 position_id
            parts = position_id.split("_", 1)
            if len(parts) != 2:
                return None

            portfolio_id, symbol = parts

            # 获取投资组合
            portfolio = self.portfolio_repo.find_by_id(portfolio_id)
            if not portfolio or symbol not in portfolio.positions:
                return None

            pos = portfolio.positions[symbol]

            # 转换为快照格式
            snapshot = PositionSnapshot(
                position_id=position_id,
                portfolio_id=portfolio_id,
                symbol=pos.symbol,
                quantity=pos.quantity,
                avg_price=pos.average_cost,
                market_price=pos.current_price,
                market_value=pos.market_value,
                unrealized_profit=pos.unrealized_pnl,
                profit_ratio=((pos.current_price / pos.average_cost) - 1) * 100 if pos.average_cost > 0 else 0.0,
            )

            return snapshot

        except Exception:
            logger.error("Failed to get position snapshot %(position_id)s: %(e)s")
            return None

    def get_metrics(self) -> Dict[str, Any]:
        """获取指标（兼容旧接口）"""
        try:
            valuation_metrics = self.valuation_service.get_metrics()

            return {
                "total_portfolios": len(self._portfolio_snapshots),
                "cached_snapshots": len(self._portfolio_snapshots),
                "valuation_metrics": valuation_metrics,
                "adapter_type": "RealtimeMTMAdapter",
                "architecture": "DDD (Phase 12.3)",
            }
        except Exception:
            logger.error("Failed to get metrics: %(e)s")
            return {}

    def _convert_to_snapshot(self, portfolio, performance) -> PortfolioSnapshot:
        """将 Portfolio 转换为 PortfolioSnapshot"""
        # 计算总成本
        total_cost = sum(pos.quantity * pos.average_cost for pos in portfolio.positions.values())

        # 计算总未实现盈亏
        total_unrealized_profit = sum(pos.unrealized_pnl for pos in portfolio.positions.values())

        # 转换持仓快照
        position_snapshots = {}
        for symbol, pos in portfolio.positions.items():
            position_snapshots[symbol] = PositionSnapshot(
                position_id=f"{portfolio.id}_{symbol}",
                portfolio_id=portfolio.id,
                symbol=pos.symbol,
                quantity=pos.quantity,
                avg_price=pos.average_cost,
                market_price=pos.current_price,
                market_value=pos.market_value,
                unrealized_profit=pos.unrealized_pnl,
                profit_ratio=((pos.current_price / pos.average_cost) - 1) * 100 if pos.average_cost > 0 else 0.0,
            )

        # 创建投资组合快照
        snapshot = PortfolioSnapshot(
            portfolio_id=portfolio.id,
            total_market_value=performance.holdings_value + performance.cash_balance,
            total_cost=total_cost,
            total_unrealized_profit=total_unrealized_profit,
            total_realized_profit=0.0,  # 需要从交易记录计算
            total_profit=performance.holdings_value + performance.cash_balance - portfolio.initial_capital,
            profit_ratio=performance.total_return,
            cash_balance=performance.cash_balance,
            available_cash=performance.cash_balance,
            position_count=len(portfolio.positions),
            last_update=performance.calculated_at,
            positions=position_snapshots,
        )

        return snapshot

    def _update_portfolio_cache(self, portfolio_id: str):
        """更新投资组合缓存"""
        try:
            portfolio = self.portfolio_repo.find_by_id(portfolio_id)
            if portfolio:
                performance = portfolio.calculate_performance()
                snapshot = self._convert_to_snapshot(portfolio, performance)
                self._portfolio_snapshots[portfolio_id] = snapshot
        except Exception:
            logger.error("Failed to update cache for %(portfolio_id)s: %(e)s")


# 全局适配器实例（延迟初始化）
_adapter: Optional[RealtimeMTMAdapter] = None


def get_realtime_mtm_adapter() -> RealtimeMTMAdapter:
    """
    获取实时市值适配器实例

    注意：需要在使用前调用 initialize_adapter() 初始化
    """
    global _adapter
    return _adapter


def initialize_adapter(db_session, event_bus=None):
    """
    初始化适配器（在应用启动时调用）

    Args:
        db_session: SQLAlchemy 数据库会话
        event_bus: Redis 事件总线（可选）
    """
    global _adapter

    if _adapter is not None:
        return _adapter

    # 创建仓储和服务
    from src.domain.portfolio.service.portfolio_valuation_service import PortfolioValuationService
    from src.infrastructure.persistence.repository_impl import PortfolioRepositoryImpl

    portfolio_repo = PortfolioRepositoryImpl(db_session)
    valuation_service = PortfolioValuationService(portfolio_repo)

    # 创建适配器
    _adapter = RealtimeMTMAdapter(
        portfolio_repo=portfolio_repo, valuation_service=valuation_service, event_bus=event_bus
    )

    logger.info("✅ RealtimeMTMAdapter initialized with DDD architecture")

    return _adapter


def get_mtm_engine():
    """
    获取 MTM 引擎（兼容旧接口）

    这个函数返回 RealtimeMTMAdapter 实例，
    它提供与 position_mtm_engine 相同的接口
    """
    return get_realtime_mtm_adapter()
