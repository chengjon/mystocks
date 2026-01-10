"""
Infrastructure Layer - SQLAlchemy Models
将领域实体映射到数据库表结构
"""
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, DateTime, DECIMAL, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from src.storage.database.database_manager import Base

class StrategyModel(Base):
    """策略模型"""
    __tablename__ = "ddd_strategies"
    
    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(Text)
    rules_json = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class PortfolioModel(Base):
    """投资组合模型"""
    __tablename__ = "ddd_portfolios"
    
    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    initial_capital = Column(DECIMAL(18, 4))
    cash = Column(DECIMAL(18, 4))
    
    # 启用 SQLAlchemy 自动版本号管理 (乐观锁)
    version = Column(Integer, nullable=False)
    __mapper_args__ = {
        "version_id_col": version
    }
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    positions = relationship("PositionModel", back_populates="portfolio", cascade="all, delete-orphan")
    transactions = relationship("TransactionModel", back_populates="portfolio", cascade="all, delete-orphan")

class PositionModel(Base):
    """持仓模型"""
    __tablename__ = "ddd_positions"

    id = Column(String(64), primary_key=True)
    portfolio_id = Column(String(64), ForeignKey("ddd_portfolios.id"), nullable=False)
    symbol = Column(String(16), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=False, default=0.0)  # 当前市场价格

    version = Column(Integer, nullable=False)
    __mapper_args__ = {
        "version_id_col": version
    }

    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    portfolio = relationship("PortfolioModel", back_populates="positions")

class OrderModel(Base):
    """订单模型"""
    __tablename__ = "ddd_orders"
    
    id = Column(String(64), primary_key=True)
    symbol = Column(String(16), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    price = Column(Float)
    side = Column(String(10), nullable=False) # BUY/SELL
    order_type = Column(String(10), nullable=False) # MARKET/LIMIT
    status = Column(String(20), nullable=False)
    filled_quantity = Column(Integer, default=0)
    average_fill_price = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class TransactionModel(Base):
    """交易流水模型"""
    __tablename__ = "ddd_transactions"
    
    id = Column(String(64), primary_key=True)
    portfolio_id = Column(String(64), ForeignKey("ddd_portfolios.id"), nullable=False)
    symbol = Column(String(16), nullable=False)
    side = Column(String(10), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    total_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)
    
    portfolio = relationship("PortfolioModel", back_populates="transactions")
