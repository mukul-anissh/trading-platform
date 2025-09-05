from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.orders import OrderCreate, OrderOut
from app.models import Order, User
from app.database import get_db
from app.utils.security import get_current_user
from typing import List

router = APIRouter(prefix='/orders', tags=['Orders'])

@router.post('/', response_model=OrderOut)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    new_order = Order(
        user_id=current_user.id,
        stock_id=order.stock_id,
        side=order.side,
        quantity=order.quantity,
        status='OPEN'
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get('/', response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()