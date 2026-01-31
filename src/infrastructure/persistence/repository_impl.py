"""
Implementation of Repository Interfaces
使用 SQLAlchemy 实现领域仓储接口
"""

import logging
from typing import List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from src.domain.portfolio.model.portfolio import Portfolio
from src.domain.portfolio.repository import IPortfolioRepository
from src.domain.portfolio.value_objects import PositionInfo
from src.domain.strategy.model.strategy import Strategy
from src.domain.strategy.repository import IStrategyRepository
from src.domain.strategy.value_objects.strategy_id import StrategyId
from src.domain.trading.model.order import Order
from src.domain.trading.model.position import Position as TradingPosition
from src.domain.trading.repository import IOrderRepository, IPositionRepository
from src.domain.trading.value_objects import OrderId, OrderSide, OrderStatus, OrderType, PositionId

from .exceptions import ConcurrencyException, RepositoryException
from .models import OrderModel, PortfolioModel, PositionModel, StrategyModel

logger = logging.getLogger(__name__)


class StrategyRepositoryImpl(IStrategyRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, strategy: Strategy) -> None:
        try:
            model = self.session.query(StrategyModel).filter_by(id=strategy.id.value).first()
            if not model:
                model = StrategyModel(id=strategy.id.value)
                self.session.add(model)

            model.name = strategy.name
            model.description = strategy.description
            model.rules_json = [r.__dict__ for r in strategy.rules] if hasattr(strategy, "rules") else []
            model.is_active = strategy.is_active

            self.session.commit()
        except StaleDataError:
            self.session.rollback()
            raise ConcurrencyException(f"Strategy {strategy.id} was updated by another process")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryException(f"Database error saving strategy: {e}")

    def find_by_id(self, strategy_id: StrategyId) -> Optional[Strategy]:
        model = self.session.query(StrategyModel).filter_by(id=strategy_id.value).first()
        if not model:
            return None

        return Strategy(
            id=StrategyId(model.id), name=model.name, description=model.description, is_active=model.is_active
        )

    def get_by_id(self, strategy_id: str) -> Optional[Strategy]:
        return self.find_by_id(StrategyId(strategy_id))

    def find_by_name(self, name: str) -> Optional[Strategy]:
        model = self.session.query(StrategyModel).filter_by(name=name).first()
        if not model:
            return None
        return self.find_by_id(StrategyId(model.id))

    def find_all_active(self) -> List[Strategy]:
        models = self.session.query(StrategyModel).filter_by(is_active=True).all()
        return [self.find_by_id(StrategyId(m.id)) for m in models]

    def find_all(self) -> List[Strategy]:
        models = self.session.query(StrategyModel).all()
        return [self.find_by_id(StrategyId(m.id)) for m in models]

    def delete(self, strategy_id: StrategyId) -> None:
        try:
            self.session.query(StrategyModel).filter_by(id=strategy_id.value).delete()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryException(f"Error deleting strategy: {e}")

    def exists(self, strategy_id: StrategyId) -> bool:
        return self.session.query(StrategyModel).filter_by(id=strategy_id.value).count() > 0

    def count_active(self) -> int:
        return self.session.query(StrategyModel).filter_by(is_active=True).count()


class OrderRepositoryImpl(IOrderRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, order: Order) -> None:
        try:
            model = self.session.query(OrderModel).filter_by(id=order.id.value).first()
            if not model:
                model = OrderModel(id=order.id.value)
                self.session.add(model)

            model.symbol = order.symbol
            model.quantity = order.quantity
            model.price = order.price
            model.side = order.side.value
            model.order_type = order.order_type.value
            model.status = order.status.value
            model.filled_quantity = order.filled_quantity
            model.average_fill_price = order.average_fill_price
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryException(f"Error saving order: {e}")

    def get_by_id(self, order_id: OrderId) -> Optional[Order]:
        model = self.session.query(OrderModel).filter_by(id=order_id.value).first()
        if not model:
            return None

        return Order(
            id=OrderId(model.id),
            symbol=model.symbol,
            quantity=model.quantity,
            price=model.price,
            side=OrderSide(model.side),
            order_type=OrderType(model.order_type),
            status=OrderStatus(model.status),
            filled_quantity=model.filled_quantity,
            average_fill_price=model.average_fill_price,
        )

    def get_by_symbol(self, symbol: str) -> List[Order]:
        models = self.session.query(OrderModel).filter_by(symbol=symbol).all()
        return [self.get_by_id(OrderId(m.id)) for m in models]

    def get_active_orders(self) -> List[Order]:
        terminal_statuses = [OrderStatus.FILLED.value, OrderStatus.CANCELLED.value, OrderStatus.REJECTED.value]
        models = self.session.query(OrderModel).filter(OrderModel.status.notin_(terminal_statuses)).all()
        return [self.get_by_id(OrderId(m.id)) for m in models]


class TradingPositionRepositoryImpl(IPositionRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, position: TradingPosition) -> None:
        try:
            model = self.session.query(PositionModel).filter_by(id=position.id.value).first()
            if not model:
                model = PositionModel(id=position.id.value)
                self.session.add(model)

            model.symbol = position.symbol
            model.quantity = position.quantity
            model.average_cost = position.average_cost

            self.session.commit()
        except StaleDataError:
            self.session.rollback()
            raise ConcurrencyException(f"Position {position.symbol} was updated by another process")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryException(f"Error saving position: {e}")

    def get_by_symbol(self, symbol: str) -> Optional[TradingPosition]:
        model = self.session.query(PositionModel).filter_by(symbol=symbol).first()
        if not model:
            return None

        pos = TradingPosition(
            id=PositionId(model.id), symbol=model.symbol, quantity=model.quantity, average_cost=model.average_cost
        )
        return pos

    def get_all(self) -> List[TradingPosition]:
        models = self.session.query(PositionModel).all()
        return [
            TradingPosition(id=PositionId(m.id), symbol=m.symbol, quantity=m.quantity, average_cost=m.average_cost)
            for m in models
        ]


class PortfolioRepositoryImpl(IPortfolioRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, portfolio: Portfolio) -> None:
        try:
            # 找到模型或创建
            model = self.session.query(PortfolioModel).filter_by(id=portfolio.id).first()
            if not model:
                model = PortfolioModel(id=portfolio.id)
                self.session.add(model)

            model.name = portfolio.name
            model.initial_capital = portfolio.initial_capital
            model.cash = portfolio.cash

            # 先执行一次显式 flush，以便触发版本检查
            self.session.flush()

            # 处理持仓
            self.session.query(PositionModel).filter_by(portfolio_id=portfolio.id).delete()
            for symbol, pos in portfolio.positions.items():
                pos_model = PositionModel(
                    id=f"{portfolio.id}_{symbol}",
                    portfolio_id=portfolio.id,
                    symbol=symbol,
                    quantity=pos.quantity,
                    average_cost=pos.average_cost,
                    current_price=pos.current_price,  # 保存当前价格
                )
                self.session.add(pos_model)

            self.session.commit()
        except StaleDataError:
            self.session.rollback()
            raise ConcurrencyException(f"Portfolio {portfolio.id} was updated by another process")
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryException(f"Database error saving portfolio: {e}")

    def find_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        model = self.session.query(PortfolioModel).filter_by(id=portfolio_id).first()
        if not model:
            return None

        p = Portfolio(
            id=model.id, name=model.name, initial_capital=float(model.initial_capital), cash=float(model.cash)
        )

        for pos_model in model.positions:
            p.positions[pos_model.symbol] = PositionInfo(
                symbol=pos_model.symbol,
                quantity=pos_model.quantity,
                average_cost=pos_model.average_cost,
                current_price=pos_model.current_price,  # 从数据库读取当前价格
            )

        return p

    def get_by_id(self, portfolio_id: str) -> Optional[Portfolio]:
        return self.find_by_id(portfolio_id)

    def find_by_name(self, name: str) -> Optional[Portfolio]:
        model = self.session.query(PortfolioModel).filter_by(name=name).first()
        if not model:
            return None
        return self.find_by_id(model.id)

    def find_all(self, limit: int = 100) -> List[Portfolio]:
        models = self.session.query(PortfolioModel).limit(limit).all()
        return [self.find_by_id(m.id) for m in models]

    def get_all(self) -> List[Portfolio]:
        return self.find_all()

    def delete(self, portfolio_id: str) -> None:
        try:
            self.session.query(PortfolioModel).filter_by(id=portfolio_id).delete()
            self.session.commit()
        except SQLAlchemyError as e:
            self.session.rollback()
            raise RepositoryException(f"Error deleting portfolio: {e}")

    def exists(self, portfolio_id: str) -> bool:
        return self.session.query(PortfolioModel).filter_by(id=portfolio_id).count() > 0

    def count(self) -> int:
        return self.session.query(PortfolioModel).count()
