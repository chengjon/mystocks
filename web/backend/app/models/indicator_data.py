"""
Indicator Data Models
=====================

SQLAlchemy models for storing indicator calculation results and task history.
Designed for PostgreSQL/TimescaleDB.
"""

from sqlalchemy import Column, String, Float, DateTime, JSON, Integer, Text
from sqlalchemy.sql import func
from app.core.database import Base

class IndicatorData(Base):
    """
    指标数据表 (Time-series)
    
    Stores calculated indicator values.
    Designed to be a TimescaleDB hypertable partitioned by timestamp.
    """
    __tablename__ = "indicator_data"
    
    # Composite Primary Key: (timestamp, stock_code, indicator_code)
    # Note: For TimescaleDB, time column is usually the partition key.
    timestamp = Column(DateTime(timezone=True), primary_key=True, nullable=False, index=True)
    stock_code = Column(String(20), primary_key=True, nullable=False)
    indicator_code = Column(String(50), primary_key=True, nullable=False)
    
    # Values
    value = Column(Float, nullable=True)        # Single value (e.g., RSI)
    complex_value = Column(JSON, nullable=True) # Complex value (e.g., BBANDS: {upper, middle, lower})
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<IndicatorData(code={self.stock_code}, ind={self.indicator_code}, time={self.timestamp})>"


class IndicatorTaskModel(Base):
    """
    指标计算任务表
    
    Tracks the execution status of calculation tasks.
    """
    __tablename__ = "indicator_tasks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String(50), unique=True, index=True, nullable=False)  # UUID
    task_type = Column(String(50), nullable=False)  # batch, single, realtime
    
    # Status
    status = Column(String(20), default="pending", index=True)  # pending, running, success, failed
    progress = Column(Float, default=0.0)
    
    # Details
    params = Column(JSON, nullable=True)        # Calculation parameters
    result_summary = Column(JSON, nullable=True) # Brief result stats
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<IndicatorTask(id={self.task_id}, status={self.status})>"
