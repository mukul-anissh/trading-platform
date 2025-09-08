from pydantic import BaseModel, ConfigDict

class StockBase(BaseModel):
    ticker: str
    last_price: float

class StockCreate(StockBase):
    name: str

class StockOut(StockBase):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)