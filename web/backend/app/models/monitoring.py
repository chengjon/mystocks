"""
监控系统数据模型
Phase 1: ValueCell Migration - Real-time Monitoring System
"""

from datetime import date, datetime
from typing import Dict, List, Optional
from sqlalchemy import (
    Boolean, Column, Date, DateTime, Integer, String, Text,
    DECIMAL, BigInteger, ForeignKey, Index, UniqueConstraint, TIMESTAMP
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class AlertRule(Base):
    """告警规则表"""
    __tablename__ = 'alert_rule'

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), nullable=False, unique=True)
    rule_type = Column(String(50), nullable=False)  # price_change, volume_surge, technical_break, etc.
    description = Column(Text)
    symbol = Column(String(20), index=True)  # NULL表示全市场规则
    stock_name = Column(String(100))

    # 规则参数
    parameters = Column(JSONB, default=dict)
    trigger_conditions = Column(JSONB, default=dict)
    notification_config = Column(JSONB, default=dict)

    # 状态和元数据
    is_active = Column(Boolean, default=True, index=True)
    priority = Column(Integer, default=1)  # 1-5
    created_by = Column(String(50))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    alert_records = relationship("AlertRecord", back_populates="rule")

    def __repr__(self):
        return f"<AlertRule(id={self.id}, name='{self.rule_name}', type='{self.rule_type}')>"


class AlertRecord(Base):
    """告警记录表"""
    __tablename__ = 'alert_record'

    id = Column(Integer, primary_key=True)
    rule_id = Column(Integer, ForeignKey('alert_rule.id', ondelete='SET NULL'))
    rule_name = Column(String(100))

    # 股票信息
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))

    # 告警信息
    alert_time = Column(DateTime, default=datetime.now, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    alert_level = Column(String(20), default='info', index=True)  # info, warning, critical
    alert_title = Column(String(200))
    alert_message = Column(Text)
    alert_details = Column(JSONB)

    # 市场数据快照
    snapshot_data = Column(JSONB)

    # 状态
    is_read = Column(Boolean, default=False, index=True)
    is_handled = Column(Boolean, default=False)
    handled_by = Column(String(50))
    handled_at = Column(DateTime)
    handle_note = Column(Text)

    created_at = Column(DateTime, default=datetime.now)

    # 关系
    rule = relationship("AlertRule", back_populates="alert_records")

    def __repr__(self):
        return f"<AlertRecord(id={self.id}, symbol='{self.symbol}', type='{self.alert_type}', level='{self.alert_level}')>"


class RealtimeMonitoring(Base):
    """实时监控数据表"""
    __tablename__ = 'realtime_monitoring'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))

    # 时间戳
    timestamp = Column(DateTime, nullable=False, index=True)
    trade_date = Column(Date, nullable=False, index=True)

    # 行情数据
    price = Column(DECIMAL(10, 2))
    open_price = Column(DECIMAL(10, 2))
    high_price = Column(DECIMAL(10, 2))
    low_price = Column(DECIMAL(10, 2))
    pre_close = Column(DECIMAL(10, 2))

    # 涨跌信息
    change_amount = Column(DECIMAL(10, 2))
    change_percent = Column(DECIMAL(10, 2))

    # 成交信息
    volume = Column(BigInteger)  # 成交量(手)
    amount = Column(DECIMAL(20, 2))  # 成交额(元)
    turnover_rate = Column(DECIMAL(10, 2))  # 换手率

    # 技术指标
    indicators = Column(JSONB, default=dict)

    # 市场强度
    market_strength = Column(String(20))  # strong, normal, weak

    # 特殊标记
    is_limit_up = Column(Boolean, default=False, index=True)
    is_limit_down = Column(Boolean, default=False, index=True)
    is_st = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        Index('idx_realtime_symbol_time', 'symbol', 'timestamp'),
    )

    def __repr__(self):
        return f"<RealtimeMonitoring(id={self.id}, symbol='{self.symbol}', price={self.price})>"


class DragonTigerList(Base):
    """龙虎榜数据表"""
    __tablename__ = 'dragon_tiger_list'

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))
    trade_date = Column(Date, nullable=False, index=True)

    # 上榜原因
    reason = Column(String(200))
    reason_code = Column(String(50))

    # 买卖数据
    total_buy_amount = Column(DECIMAL(20, 2))
    total_sell_amount = Column(DECIMAL(20, 2))
    net_amount = Column(DECIMAL(20, 2), index=True)  # 净买入额

    # 机构席位
    institution_buy_count = Column(Integer, default=0)
    institution_sell_count = Column(Integer, default=0)
    institution_net_amount = Column(DECIMAL(20, 2))

    # 详细数据
    detail_data = Column(JSONB)

    # 影响评估
    impact_score = Column(Integer)  # 1-10

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('symbol', 'trade_date', name='uq_dragon_tiger_symbol_date'),
    )

    def __repr__(self):
        return f"<DragonTigerList(id={self.id}, symbol='{self.symbol}', date={self.trade_date})>"


class MonitoringStatistics(Base):
    """监控统计表"""
    __tablename__ = 'monitoring_statistics'

    id = Column(Integer, primary_key=True)
    stat_date = Column(Date, nullable=False, index=True)
    stat_hour = Column(Integer)  # 0-23

    # 监控覆盖
    total_monitored_stocks = Column(Integer)
    active_alerts = Column(Integer)

    # 告警统计
    total_alerts_triggered = Column(Integer)
    alerts_by_type = Column(JSONB)
    alerts_by_level = Column(JSONB)

    # 市场统计
    limit_up_count = Column(Integer)
    limit_down_count = Column(Integer)
    dragon_tiger_count = Column(Integer)

    # 性能指标
    avg_response_time_ms = Column(Integer)
    data_update_frequency = Column(Integer)

    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint('stat_date', 'stat_hour', name='uq_monitoring_stat_date_hour'),
    )

    def __repr__(self):
        return f"<MonitoringStatistics(date={self.stat_date}, hour={self.stat_hour})>"


# ============================================================================
# Pydantic schemas for API request/response
# ============================================================================

from pydantic import BaseModel, Field, validator
from enum import Enum


class AlertRuleType(str, Enum):
    """告警规则类型枚举"""
    PRICE_CHANGE = "price_change"
    VOLUME_SURGE = "volume_surge"
    TECHNICAL_BREAK = "technical_break"
    LIMIT_UP = "limit_up"
    LIMIT_DOWN = "limit_down"
    DRAGON_TIGER = "dragon_tiger"


class AlertLevel(str, Enum):
    """告警级别枚举"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertRuleCreate(BaseModel):
    """创建告警规则请求"""
    rule_name: str = Field(..., min_length=1, max_length=100)
    rule_type: AlertRuleType
    description: Optional[str] = None
    symbol: Optional[str] = None
    stock_name: Optional[str] = None
    parameters: Dict = Field(default_factory=dict)
    trigger_conditions: Dict = Field(default_factory=dict)
    notification_config: Dict = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)
    is_active: bool = True

    @validator('rule_name')
    def validate_rule_name(cls, v):
        if not v or not v.strip():
            raise ValueError('规则名称不能为空')
        return v.strip()


class AlertRuleUpdate(BaseModel):
    """更新告警规则请求"""
    rule_name: Optional[str] = None
    description: Optional[str] = None
    parameters: Optional[Dict] = None
    trigger_conditions: Optional[Dict] = None
    notification_config: Optional[Dict] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    is_active: Optional[bool] = None


class AlertRuleResponse(BaseModel):
    """告警规则响应"""
    id: int
    rule_name: str
    rule_type: str
    description: Optional[str]
    symbol: Optional[str]
    stock_name: Optional[str]
    parameters: Dict
    trigger_conditions: Dict
    notification_config: Dict
    is_active: bool
    priority: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertRecordResponse(BaseModel):
    """告警记录响应"""
    id: int
    rule_id: Optional[int]
    rule_name: Optional[str]
    symbol: str
    stock_name: Optional[str]
    alert_time: datetime
    alert_type: str
    alert_level: str
    alert_title: Optional[str]
    alert_message: Optional[str]
    alert_details: Optional[Dict]
    snapshot_data: Optional[Dict]
    is_read: bool
    is_handled: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RealtimeMonitoringResponse(BaseModel):
    """实时监控数据响应"""
    id: int
    symbol: str
    stock_name: Optional[str]
    timestamp: datetime
    trade_date: date
    price: Optional[float]
    change_percent: Optional[float]
    volume: Optional[int]
    amount: Optional[float]
    indicators: Optional[Dict]
    market_strength: Optional[str]
    is_limit_up: bool
    is_limit_down: bool

    class Config:
        from_attributes = True


class DragonTigerListResponse(BaseModel):
    """龙虎榜响应"""
    id: int
    symbol: str
    stock_name: Optional[str]
    trade_date: date
    reason: Optional[str]
    total_buy_amount: Optional[float]
    total_sell_amount: Optional[float]
    net_amount: Optional[float]
    institution_buy_count: int
    institution_sell_count: int
    institution_net_amount: Optional[float]
    detail_data: Optional[Dict]
    impact_score: Optional[int]

    class Config:
        from_attributes = True


class MonitoringSummaryResponse(BaseModel):
    """监控摘要响应"""
    total_stocks: int = 0
    limit_up_count: int = 0
    limit_down_count: int = 0
    strong_up_count: int = 0
    strong_down_count: int = 0
    avg_change_percent: Optional[float] = None
    total_amount: Optional[float] = None
    active_alerts: int = 0
    unread_alerts: int = 0
