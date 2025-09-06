from pydantic import BaseModel, ConfigDict
from app.models import OrderSide, OrderStatus
from datetime import datetime

class OrderBase(BaseModel):
    stock_id: int
    quantity: int
    side: OrderSide

class OrderCreate(OrderBase):
    pass

class OrderOut(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)