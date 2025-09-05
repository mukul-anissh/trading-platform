from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.stocks import StockOut
from app.models import Stock
from app.database import get_db
from typing import List

router = APIRouter(prefix='/stocks', tags=['Stocks'])

@router.get('/', response_model=List[StockOut])
def list_stocks(db: Session = Depends(get_db)):
    return db.query(Stock).all()