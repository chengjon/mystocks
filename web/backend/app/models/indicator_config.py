"""
SQLAlchemy Model for Indicator Configurations
指标配置的数据库模型
"""

from sqlalchemy import JSON, TIMESTAMP, Column, Index, Integer, String, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class IndicatorConfiguration(Base):
    """
    用户指标配置表

    对应 table_config.yaml 中的 indicator_configurations 表
    """

    __tablename__ = "indicator_configurations"
    __table_args__ = (
        Index("uk_user_name", "user_id", "name", unique=True),
        Index("idx_user_id", "user_id"),
        Index("idx_last_used", "last_used_at"),
        {"mysql_engine": "InnoDB", "mysql_charset": "utf8mb4"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True, comment="配置ID")

    user_id = Column(Integer, nullable=False, comment="用户ID")

    name = Column(String(100), nullable=False, comment="配置名称")

    indicators = Column(JSON, nullable=False, comment="指标数组JSON")

    created_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        comment="创建时间",
    )

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        comment="更新时间",
    )

    last_used_at = Column(TIMESTAMP, nullable=True, comment="最后使用时间")

    def __repr__(self):
        return (
            f"<IndicatorConfiguration(id={self.id}, user_id={self.user_id}, "
            f"name='{self.name}', indicator_count={len(self.indicators) if self.indicators else 0})>"
        )

    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "indicators": self.indicators,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_used_at": (self.last_used_at.isoformat() if self.last_used_at else None),
        }
