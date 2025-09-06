from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Optional
from app.models import User, Stock, Trade, Order, Position, OrderSide, OrderStatus
from decimal import Decimal, ROUND_DOWN

def _get_remaining(order: Order) -> int:
    return int(order.quantity - order.filled_qty)

def _ensure_position(session: Session, user_id: int, stock_id: int) -> Position:
    pos = session.query(Position).filter_by(user_id=user_id, stock_id=stock_id).with_for_update().first()
    if not pos:
        pos = Position(user_id=user_id, stock_id=stock_id, quantity=0, avg_price=None)
        session.add(pos)
        session.flush()
    return pos

def _update_buyer_position_on_buy(pos: Position, qty: int, price: float):
    old_qty = int(pos.quantity or 0)
    if old_qty <= 0 or pos.avg_price is None:
        pos.avg_price = price
    else:
        old_total = pos.avg_price*old_qty
        new_total = qty*price+old_total
        new_qty = old_qty+qty
        pos.avg_price = (new_total)/(new_qty)
    pos.quantity = old_qty+qty

def _update_seller_position_on_sell(pos: Position, qty: int):
    old_qty = int(pos.quantity or 0)
    new_qty = old_qty-qty
    if new_qty < 0:
        raise ValueError('Seller does not have enough shares')
    pos.quantity = new_qty
    if new_qty == 0:
        pos.avg_price = None

def process_order_match(session: Session, incoming_order_id: int):
    incoming = session.query(Order).filter(Order.id == incoming_order_id).with_for_update(skip_locked=True).first()
    if not incoming:
        raise ValueError("Order not found")
    
    if incoming.status not in (OrderStatus.OPEN, OrderStatus.PARTIAL):
        return
    
    remaining = _get_remaining(incoming)
    if remaining <= 0:
        return
    
    opposite_side = OrderSide.SELL if incoming.side == OrderSide.BUY else OrderSide.BUY
    opposite_q = session.query(Order).filter(
        Order.stock_id == incoming.stock_id,
        Order.side == opposite_side,
        Order.status.in_([OrderStatus.OPEN, OrderStatus.PARTIAL])
    ).order_by(Order.created_at.asc()).with_for_update(skip_locked=True)

    incoming_user = session.query(User).filter(User.id == incoming.user_id).with_for_update(skip_locked=True).first()

    for resting in opposite_q:
        if remaining <= 0:
            break

        resting_remaining = _get_remaining(resting)
        if resting_remaining <= 0:
            continue

        match_qty = int(min(resting_remaining, remaining))
        exec_price = float(resting.price)
        total_cost = match_qty*exec_price

        if incoming.side == OrderSide.BUY:
            buy_order = incoming
            sell_order = resting
            buyer = incoming_user
            seller = session.query(User).filter(User.id == resting.user_id).with_for_update(skip_locked=True).first()
        else:
            sell_order = incoming
            buy_order = resting
            seller = incoming_user
            buyer = session.query(User).filter(User.id == resting.user_id).with_for_update(skip_locked=True).first()
        
        if buyer.id == seller.id:
            continue

        if buyer.balance < total_cost:
            affordable_qty = int(buyer.balance//exec_price)
            if affordable_qty <= 0:
                continue
            match_qty = int(affordable_qty)
            total_cost = match_qty*exec_price
        
        seller_pos = _ensure_position(session, seller.id, incoming.stock_id)
        if int(seller_pos.quantity or 0) < match_qty:
            available_qty = int(seller_pos.quantity or 0)
            if available_qty <= 0:
                continue
            match_qty = int(available_qty)
            total_cost = match_qty*exec_price

        if match_qty <= 0:
            continue

        trade = Trade(
            buy_order_id=buy_order.id,
            sell_order_id=sell_order.id,
            stock_id=incoming.stock_id,
            quantity=match_qty,
            price=exec_price
        )
        session.add(trade)
        session.flush()

        resting.filled_qty = int(resting.filled_qty) + match_qty
        resting_remaining_after = int(resting.quantity) - resting.filled_qty
        resting.status = OrderStatus.FILLED if resting_remaining_after == 0 else OrderStatus.PARTIAL
        resting.updated_at = func.now()

        incoming.filled_qty = int(incoming.filled_qty) + match_qty
        remaining = int(incoming.quantity) - incoming.filled_qty
        incoming.status = OrderStatus.FILLED if remaining == 0 else OrderStatus.PARTIAL
        incoming.updated_at = func.now()

        buyer.balance = float(buyer.balance) - total_cost
        seller.balance = float(seller.balance) + total_cost

        buyer_pos = _ensure_position(session, buyer.id, incoming.stock_id)
        _update_buyer_position_on_buy(buyer_pos, match_qty, exec_price)

        _update_seller_position_on_sell(seller_pos, match_qty)

        session.flush()
    return