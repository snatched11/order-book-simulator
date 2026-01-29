"""
Order module for the Order Book Simulator.

This version works on Python 3.9+ (no slots=True).
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional
import time

# ------------------------
# Enums
# ------------------------
class Side(Enum):
    BUY = 1
    SELL = -1

class OrderType(Enum):
    LIMIT = 1
    MARKET = 2

class OrderStatus(Enum):
    PENDING = 0
    PARTIALLY_FILLED = 1
    FILLED = 2
    CANCELLED = 3

# ------------------------
# Order ID generator
# ------------------------
class OrderIDGenerator:
    def __init__(self, start: int = 1):
        self._current = start

    def next(self) -> int:
        order_id = self._current
        self._current += 1
        return order_id

    def reset(self):
        self._current = 1

# Global generator
id_generator = OrderIDGenerator()

# ------------------------
# Order class
# ------------------------
@dataclass
class Order:
    side: Side
    order_type: OrderType
    quantity: int
    price: Optional[float] = None
    order_id: int = field(default_factory=lambda: id_generator.next())
    timestamp: float = field(default_factory=time.time)
    filled_quantity: int = 0
    status: OrderStatus = OrderStatus.PENDING

    def __post_init__(self):
        self._validate()

    def _validate(self):
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise ValueError("Limit order must have a price")
        if self.order_type == OrderType.LIMIT and self.price <= 0:
            raise ValueError("Price must be positive")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if not isinstance(self.quantity, int):
            raise ValueError("Quantity must be an integer")

    @property
    def remaining_quantity(self) -> int:
        return self.quantity - self.filled_quantity

    @property
    def is_filled(self) -> bool:
        return self.remaining_quantity == 0

    @property
    def is_active(self) -> bool:
        return self.status in (OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED)

    def fill(self, quantity: int) -> int:
        if quantity <= 0:
            raise ValueError("Fill quantity must be positive")
        if quantity > self.remaining_quantity:
            raise ValueError(f"Cannot fill {quantity}, only {self.remaining_quantity} remaining")
        self.filled_quantity += quantity
        if self.is_filled:
            self.status = OrderStatus.FILLED
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
        return quantity

    def cancel(self) -> bool:
        if self.status == OrderStatus.FILLED:
            return False
        self.status = OrderStatus.CANCELLED
        return True

    def __repr__(self) -> str:
        price_str = f"${self.price:.2f}" if self.price else "MARKET"
        return (
            f"Order({self.order_id}: {self.side.name} {self.quantity} "
            f"@ {price_str} | Filled: {self.filled_quantity} | {self.status.name})"
        )

    def __hash__(self) -> int:
        return hash(self.order_id)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

# ------------------------
# Factory functions
# ------------------------
def create_limit_order(side: Side, quantity: int, price: float) -> Order:
    return Order(side=side, order_type=OrderType.LIMIT, quantity=quantity, price=price)

def create_market_order(side: Side, quantity: int) -> Order:
    return Order(side=side, order_type=OrderType.MARKET, quantity=quantity, price=None)