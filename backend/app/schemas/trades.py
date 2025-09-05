from pydantic import BaseModel, ConfigDict
from datetime import datetime

class TradeOut(BaseModel):
    id: int
    buy_order_id: int
    sell_order_id: int
    stock_id: int
    quantity: int
    price: float
    traded_at: datetime

    model_config = ConfigDict(from_attributes=True)