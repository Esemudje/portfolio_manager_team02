from enum import Enum
from dataclasses import dataclass

class OrderType(Enum):
    MARKET = "MARKET"

class OrderSide(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    EXPIRED = "EXPIRED"

@dataclass
class OrderRequest:
    """Simplified order request for market orders only"""
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = OrderType.MARKET
    user_id: str = 'default_user'

    def __post_init__(self):
        """Validate order parameters"""
        self.symbol = self.symbol.upper()
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")

    def to_dict(self):
        """Convert to dictionary for database storage"""
        return {
            'user_id': self.user_id,
            'stock_symbol': self.symbol,
            'order_type': self.order_type.value,
            'side': self.side.value,
            'quantity': self.quantity
        }

    def __repr__(self):
        return f"OrderRequest(symbol={self.symbol}, side={self.side.value}, quantity={self.quantity}, type={self.order_type.value})"


# Helper function for creating market orders

def create_market_order(symbol: str, side: OrderSide, quantity: int, user_id: str = 'default_user') -> OrderRequest:
    """Create a market order"""
    return OrderRequest(
        symbol=symbol,
        side=side,
        quantity=quantity,
        order_type=OrderType.MARKET,
        user_id=user_id
    )
