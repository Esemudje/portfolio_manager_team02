from enum import Enum
from typing import Optional
from dataclasses import dataclass

class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

class TimeInForce(Enum):
    DAY = "DAY"
    GTC = "GTC"  # Good Till Cancelled

@dataclass
class OrderRequest:
    """Enhanced order request supporting different order types"""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType
    price: Optional[float] = None  # For limit orders
    stop_price: Optional[float] = None  # For stop and stop-limit orders
    limit_price: Optional[float] = None  # For stop-limit orders (limit price after stop triggers)
    time_in_force: TimeInForce = TimeInForce.DAY
    user_id: str = 'default_user'

    def __post_init__(self):
        """Validate order parameters"""
        self.symbol = self.symbol.upper()
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        
        if self.order_type == OrderType.LIMIT and self.price is None:
            raise ValueError("Limit orders require a price")
        
        if self.order_type == OrderType.STOP and self.stop_price is None:
            raise ValueError("Stop orders require a stop price")
        
        if self.order_type == OrderType.STOP_LIMIT:
            if self.stop_price is None or self.limit_price is None:
                raise ValueError("Stop-limit orders require both stop price and limit price")

    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            'user_id': self.user_id,
            'stock_symbol': self.symbol,
            'order_type': self.order_type.value,
            'side': self.side.value,
            'quantity': self.quantity,
            'price': self.price,
            'stop_price': self.stop_price,
            'limit_price': self.limit_price,
            'time_in_force': self.time_in_force.value
        }

    def __repr__(self):
        return f"OrderRequest(symbol={self.symbol}, side={self.side.value}, quantity={self.quantity}, type={self.order_type.value})"


# Helper functions for creating specific order types

def create_market_order(symbol: str, side: OrderSide, quantity: int, user_id: str = 'default_user') -> OrderRequest:
    """Create a market order"""
    return OrderRequest(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=OrderType.MARKET,
        user_id=user_id
    )

def create_limit_order(symbol: str, side: OrderSide, quantity: int, price: float, user_id: str = 'default_user') -> OrderRequest:
    """Create a limit order"""
    return OrderRequest(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=OrderType.LIMIT,
        price=price,
        user_id=user_id
    )

def create_stop_order(symbol: str, side: OrderSide, quantity: int, stop_price: float, user_id: str = 'default_user') -> OrderRequest:
    """Create a stop order (stop-loss)"""
    return OrderRequest(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=OrderType.STOP,
        stop_price=stop_price,
        user_id=user_id
    )

def create_stop_limit_order(symbol: str, side: OrderSide, quantity: int, stop_price: float, limit_price: float, user_id: str = 'default_user') -> OrderRequest:
    """Create a stop-limit order"""
    return OrderRequest(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=OrderType.STOP_LIMIT,
        stop_price=stop_price,
        limit_price=limit_price,
        user_id=user_id
    )
