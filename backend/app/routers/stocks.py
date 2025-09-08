from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.stocks import StockOut, StockCreate
from app.models import Stock
from app.database import get_db
from typing import List

router = APIRouter(prefix='/stocks', tags=['Stocks'])

@router.post('/', response_model=StockOut)
def create_stock(stock: StockCreate, db: Session = Depends(get_db)):
    existing = db.query(Stock).filter(Stock.ticker == stock.ticker).first()
    if existing:
        raise HTTPException(status_code=409, detail='Ticker already exists!')

    new_stock = Stock(
        ticker=stock.ticker,
        name=stock.name,
        last_price=stock.last_price
    )

    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock

@router.get('/', response_model=List[StockOut])
def list_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()