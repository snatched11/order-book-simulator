"""
Tests for Order class.
Run with: pytest -v
"""

import pytest
from src.order import (
    Order,
    Side,
    OrderType,
    OrderStatus,
    OrderIDGenerator,
    create_limit_order,
    create_market_order,
    id_generator
)

class TestOrderCreation:
    def setup_method(self):
        id_generator.reset()

    def test_create_limit_buy_order(self):
        order = Order(side=Side.BUY, order_type=OrderType.LIMIT, quantity=100, price=150.50)
        assert order.side == Side.BUY
        assert order.order_type == OrderType.LIMIT
        assert order.quantity == 100
        assert order.price == 150.50
        assert order.status == OrderStatus.PENDING
        assert order.filled_quantity == 0
        assert order.remaining_quantity == 100

    def test_create_market_order(self):
        order = Order(side=Side.SELL, order_type=OrderType.MARKET, quantity=50)
        assert order.order_type == OrderType.MARKET
        assert order.price is None

    def test_limit_order_without_price_raises(self):
        with pytest.raises(ValueError, match="must have a price"):
            Order(side=Side.BUY, order_type=OrderType.LIMIT, quantity=100, price=None)

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="must be positive"):
            Order(side=Side.BUY, order_type=OrderType.LIMIT, quantity=100, price=-10.0)

class TestOrderFill:
    def setup_method(self):
        id_generator.reset()

    def test_partial_fill(self):
        order = create_limit_order(Side.BUY, 100, 150.0)
        order.fill(30)
        assert order.filled_quantity == 30
        assert order.remaining_quantity == 70
        assert order.status == OrderStatus.PARTIALLY_FILLED

    def test_complete_fill(self):
        order = create_limit_order(Side.BUY, 100, 150.0)
        order.fill(100)
        assert order.filled_quantity == 100
        assert order.remaining_quantity == 0
        assert order.status == OrderStatus.FILLED
        assert order.is_filled

class TestOrderCancel:
    def setup_method(self):
        id_generator.reset()

    def test_cancel_pending_order(self):
        order = create_limit_order(Side.BUY, 100, 150.0)
        result = order.cancel()
        assert result is True
        assert order.status == OrderStatus.CANCELLED