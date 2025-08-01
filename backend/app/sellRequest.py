class sellRequest:
    def __init__(self, symbol: str, quantity: int):
        self.symbol = symbol.upper()
        self.quantity = quantity
        
    def __str__(self):
        return f"SellRequest(symbol='{self.symbol}', quantity={self.quantity})"
        
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'quantity': self.quantity
        }
