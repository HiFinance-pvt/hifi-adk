from pydantic import BaseModel


class StockActionSchema(BaseModel):
    action: str  # 'buy' or 'sell'
    symbol: str
    exchange: str = "BSE"  # Default to BSE, can be made configurable
    quantity: int
    order_type: str = "MARKET"  # Default to MARKET order
    product: str = "CNC"  # Cash and Carry for delivery trades