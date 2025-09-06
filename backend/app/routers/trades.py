from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.trades import TradeOut
from app.models import Trade
from app.database import get_db
from typing import List

router = APIRouter(prefix='/trades', tags=['Trades'])

@router.get('/', response_model=List[TradeOut])
def list_trades(db: Session = Depends(get_db)):
    return db.query(Trade).all()