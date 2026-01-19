"""
Phase 8: Infrastructure Layer 验证测试
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.storage.database.database_manager import Base
from src.infrastructure.persistence.models import StrategyModel, OrderModel, PortfolioModel
from src.infrastructure.persistence.repository_impl import OrderRepositoryImpl
from src.domain.trading.model.order import Order
from src.domain.trading.value_objects import OrderSide, OrderType, OrderId, OrderStatus
from src.infrastructure.messaging.local_event_bus import LocalEventBus
from src.domain.shared.event import DomainEvent


class TestInfrastructure:

    @pytest.fixture
    def db_session(self):
        # 使用 SQLite 内存数据库进行测试
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_order_repository_save_and_load(self, db_session):
        repo = OrderRepositoryImpl(db_session)

        # 1. 创建订单
        order = Order.create(symbol="000001", quantity=100, side=OrderSide.BUY, order_type=OrderType.LIMIT, price=10.5)

        # 2. 保存
        repo.save(order)

        # 3. 加载
        loaded_order = repo.get_by_id(order.id)

        assert loaded_order is not None
        assert loaded_order.symbol == "000001"
        assert loaded_order.quantity == 100
        assert loaded_order.price == 10.5
        assert loaded_order.status == OrderStatus.CREATED

    def test_local_event_bus(self):
        bus = LocalEventBus()
        mock_handler = MagicMock()

        @dataclass
        class TestEvent(DomainEvent):
            data: str

        bus.subscribe(TestEvent, mock_handler)

        event = TestEvent(data="hello")
        bus.publish(event)

        assert mock_handler.called
        args, _ = mock_handler.call_args
        assert args[0].data == "hello"


from unittest.mock import MagicMock
from dataclasses import dataclass

if __name__ == "__main__":
    pytest.main([__file__])
