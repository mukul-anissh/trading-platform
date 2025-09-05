import enum
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

base = declarative_base()

class OrderSide(enum.Enum):
    BUY = 'BUY'
    SELL = 'SELL'

class OrderStatus(enum.Enum):
    OPEN = 'OPEN'
    PARTIAL = 'PARTIAL'
    FILLED = 'FILLED'
    CANCELLED = 'CANCELLED'

# table to store user information
class User(base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    balance = Column(Numeric(12, 2), nullable=False, server_default='10000.00')
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship('Order', back_populates='user', cascade='all, delete-orphan')
    positions = relationship('Position', back_populates='user', cascade='all, delete-orphan')

# table to store stock information
class Stock(base):
    __tablename__ = 'stocks'
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100))
    last_price = Column(Numeric(12, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    orders = relationship('Order', back_populates='stock')
    positions = relationship('Position',  back_populates='stock')

# order book
class Order(base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    side = Column(Enum(OrderSide), nullable=False)
    quantity = Column(Integer, nullable=False)
    filled_qty = Column(Integer, nullable=False, server_default='0')
    price = Column(Numeric(12, 2), nullable=False)
    status = Column(Enum(OrderStatus), nullable=False, server_default='OPEN')
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='orders')
    stock = relationship('Stock', back_populates='orders')

# trade records
class Trade(base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, index=True)
    buy_order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    sell_order_id = Column(Integer, ForeignKey('orders.id'), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    traded_at = Column(DateTime(timezone=True), server_default=func.now())

# portfolio of users
class Position(base):
    __tablename__ = 'positions'
    __table_args__ = (UniqueConstraint('user_id', 'stock_id', name='uix_user_stock'),)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    stock_id = Column(Integer, ForeignKey('stocks.id'), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, server_default='0')
    avg_price = Column(Numeric(12, 2))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='positions')
    stock = relationship('Stock', back_populates='positions')