"""
Phase 7: Application Layer 验证测试
"""

from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.application.dto.trading_dto import CreateOrderRequest
from src.application.trading.order_mgmt_service import OrderManagementService
from src.domain.trading.value_objects import OrderId, OrderSide, OrderStatus


class TestOrderManagementService:
    def test_place_order_flow(self):
        # Setup mocks
        mock_repo = MagicMock()
        service = OrderManagementService(order_repo=mock_repo)

        request = CreateOrderRequest(symbol="000001", quantity=100, side="BUY", order_type="LIMIT", price=10.5)

        # Execute
        response = service.place_order(request)

        # Verify
        assert response.symbol == "000001"
        assert response.status == OrderStatus.SUBMITTED.value
        assert mock_repo.save.called

    def test_handle_execution_report(self):
        # Setup mocks
        mock_repo = MagicMock()

        # 构造一个真实的 Order 对象而不是 MagicMock，以满足 Pydantic 校验
        # 因为 Pydantic 期待属性是字符串/枚举/日期等，而不是 Mock 对象
        from src.domain.trading.model.order import Order
        from src.domain.trading.value_objects import OrderType

        order = Order.create(symbol="000001", quantity=100, side=OrderSide.BUY, order_type=OrderType.LIMIT, price=10.0)
        order.submit()

        mock_repo.get_by_id.return_value = order
        service = OrderManagementService(order_repo=mock_repo)

        # Execute
        response = service.handle_execution_report(order.id.value, 100, 10.6)

        # Verify
        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == 100
        assert mock_repo.save.called
        assert response.status == OrderStatus.FILLED.value
        assert response.symbol == "000001"


if __name__ == "__main__":
    pytest.main([__file__])
