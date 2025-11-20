"""
公告系统数据模型
Multi-data Source Support
"""

from datetime import date, datetime
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
    Text,
    DECIMAL,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.orm import declarative_base
from pydantic import BaseModel, Field

# 使用与monitoring.py相同的Base
from app.models.monitoring import Base


# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================


class Announcement(Base):
    """公告数据表"""

    __tablename__ = "announcement"

    id = Column(Integer, primary_key=True)
    stock_code = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100))
    announcement_title = Column(Text, nullable=False)
    announcement_type = Column(String(100), index=True)
    publish_date = Column(Date, nullable=False, index=True)
    publish_time = Column(DateTime)
    url = Column(Text)
    content = Column(Text)
    summary = Column(Text)
    keywords = Column(JSONB, default=list)
    importance_level = Column(Integer, default=0, index=True)  # 0-5

    # 多数据源字段
    data_source = Column(String(50), nullable=False, index=True)
    source_id = Column(String(200))

    # 分析字段
    is_analyzed = Column(Boolean, default=False)
    sentiment = Column(String(20))  # positive, negative, neutral
    impact_score = Column(DECIMAL(5, 2))

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    monitor_records = relationship(
        "AnnouncementMonitorRecord", back_populates="announcement"
    )

    __table_args__ = (
        UniqueConstraint(
            "stock_code", "source_id", "data_source", name="uq_announcement_source"
        ),
    )

    def __repr__(self):
        return f"<Announcement(id={self.id}, code='{self.stock_code}', title='{self.announcement_title[:30]}...')>"


class AnnouncementMonitorRule(Base):
    """公告监控规则表"""

    __tablename__ = "announcement_monitor_rule"

    id = Column(Integer, primary_key=True)
    rule_name = Column(String(100), nullable=False, unique=True)
    keywords = Column(JSONB, default=list)
    announcement_types = Column(JSONB, default=list)
    stock_codes = Column(JSONB, default=list)
    min_importance_level = Column(Integer, default=0)

    # 通知设置
    notify_enabled = Column(Boolean, default=True)
    notify_channels = Column(JSONB, default=list)

    is_active = Column(Boolean, default=True, index=True)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # 关系
    monitor_records = relationship("AnnouncementMonitorRecord", back_populates="rule")

    def __repr__(self):
        return f"<AnnouncementMonitorRule(id={self.id}, name='{self.rule_name}')>"


class AnnouncementMonitorRecord(Base):
    """公告监控记录表"""

    __tablename__ = "announcement_monitor_record"

    id = Column(Integer, primary_key=True)
    rule_id = Column(
        Integer,
        ForeignKey("announcement_monitor_rule.id", ondelete="CASCADE"),
        index=True,
    )
    announcement_id = Column(
        Integer, ForeignKey("announcement.id", ondelete="CASCADE"), index=True
    )
    matched_keywords = Column(JSONB, default=list)
    triggered_at = Column(DateTime, default=datetime.now, index=True)
    notified = Column(Boolean, default=False)
    notified_at = Column(DateTime)
    notification_result = Column(Text)

    # 关系
    rule = relationship("AnnouncementMonitorRule", back_populates="monitor_records")
    announcement = relationship("Announcement", back_populates="monitor_records")

    def __repr__(self):
        return f"<AnnouncementMonitorRecord(id={self.id}, rule_id={self.rule_id}, announcement_id={self.announcement_id})>"


# ============================================================================
# Pydantic Schemas (for API)
# ============================================================================


class AnnouncementBase(BaseModel):
    """公告基础模型"""

    stock_code: str
    stock_name: Optional[str] = None
    announcement_title: str
    announcement_type: Optional[str] = None
    publish_date: date
    publish_time: Optional[datetime] = None
    url: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    keywords: list = Field(default_factory=list)
    importance_level: int = 0
    data_source: str
    source_id: Optional[str] = None
    sentiment: Optional[str] = None
    impact_score: Optional[float] = None


class AnnouncementCreate(AnnouncementBase):
    """创建公告请求"""

    pass


class AnnouncementResponse(AnnouncementBase):
    """公告响应"""

    id: int
    is_analyzed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnouncementMonitorRuleBase(BaseModel):
    """公告监控规则基础模型"""

    rule_name: str
    keywords: list = Field(default_factory=list)
    announcement_types: list = Field(default_factory=list)
    stock_codes: list = Field(default_factory=list)
    min_importance_level: int = 0
    notify_enabled: bool = True
    notify_channels: list = Field(default_factory=lambda: ["email"])


class AnnouncementMonitorRuleCreate(AnnouncementMonitorRuleBase):
    """创建监控规则请求"""

    pass


class AnnouncementMonitorRuleUpdate(BaseModel):
    """更新监控规则请求"""

    rule_name: Optional[str] = None
    keywords: Optional[list] = None
    announcement_types: Optional[list] = None
    stock_codes: Optional[list] = None
    min_importance_level: Optional[int] = None
    notify_enabled: Optional[bool] = None
    notify_channels: Optional[list] = None
    is_active: Optional[bool] = None


class AnnouncementMonitorRuleResponse(AnnouncementMonitorRuleBase):
    """监控规则响应"""

    id: int
    is_active: bool
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AnnouncementMonitorRecordResponse(BaseModel):
    """监控记录响应"""

    id: int
    rule_id: int
    announcement_id: int
    matched_keywords: list
    triggered_at: datetime
    notified: bool
    notified_at: Optional[datetime]
    notification_result: Optional[str]

    # 关联数据
    rule_name: Optional[str] = None
    announcement_title: Optional[str] = None

    class Config:
        from_attributes = True


class AnnouncementSearchRequest(BaseModel):
    """公告搜索请求"""

    keywords: Optional[str] = None
    stock_code: Optional[str] = None
    announcement_type: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    min_importance_level: Optional[int] = None
    data_source: Optional[str] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class AnnouncementStatsResponse(BaseModel):
    """公告统计响应"""

    total_count: int
    today_count: int
    important_count: int
    by_source: dict
    by_type: dict
    by_sentiment: dict
