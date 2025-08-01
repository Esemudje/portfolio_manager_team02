class BuyRequest:
    def __init__(self, symbol: str, quantity: int):
        self.symbol = symbol
        self.quantity = quantity

    def __repr__(self):
        return f"BuyRequest(symbol={self.symbol}, quantity={self.quantity})"


