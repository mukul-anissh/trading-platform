from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.orders import OrderCreate, OrderOut
from app.models import Order, User, Stock, OrderSide, OrderStatus
from app.database import get_db
from app.utils.security import get_current_user
from app.services.matching import process_order_match
from typing import List

router = APIRouter(prefix='/orders', tags=['Orders'])

@router.post('/', response_model=OrderOut)
def create_order(order: OrderCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if order.quantity <= 0 :
        raise HTTPException(status_code=400, detail='Quantity must be greater than 0')
    
    stock = db.query(Stock).filter(Stock.id == order.stock_id).first()
    if not stock:
        raise HTTPException(status_code=404, detail='Stock not found')
    
    price = float(stock.last_price) if stock.last_price else 0.0
    new_order = Order(
        user_id=current_user.id,
        stock_id=order.stock_id,
        side=OrderSide(order.side.upper()),
        quantity=order.quantity,
        price=price,
        status=OrderStatus('OPEN')
    )

    try:
        with db.begin():
            db.add(new_order)
            db.flush()
            process_order_match(db, new_order.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    db.refresh(new_order)
    return new_order

@router.get('/', response_model=List[OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()