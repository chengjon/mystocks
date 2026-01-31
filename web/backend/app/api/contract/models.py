"""
API契约管理 数据库模型
使用PostgreSQL存储契约版本和元数据
"""

from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from app.core.database import Base


class ContractVersion(Base):
    """契约版本表"""

    __tablename__ = "contract_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True, comment="契约名称")
    version = Column(String(50), nullable=False, comment="版本号")
    spec = Column(JSON, nullable=False, comment="OpenAPI规范内容")
    commit_hash = Column(String(100), nullable=True, comment="Git commit hash")
    author = Column(String(100), nullable=True, comment="作者")
    description = Column(Text, nullable=True, comment="版本描述")
    tags = Column(JSON, default=list, comment="版本标签")
    is_active = Column(Boolean, default=False, comment="是否为当前激活版本")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    __table_args__ = ({"comment": "API契约版本表", "schema": "mystocks"},)


class ContractDiff(Base):
    """契约差异记录表"""

    __tablename__ = "contract_diffs"

    id = Column(Integer, primary_key=True, index=True)
    contract_name = Column(String(100), nullable=False, index=True, comment="契约名称")
    from_version_id = Column(Integer, ForeignKey("mystocks.contract_versions.id"), comment="源版本ID")
    to_version_id = Column(Integer, ForeignKey("mystocks.contract_versions.id"), comment="目标版本ID")
    total_changes = Column(Integer, default=0, comment="总变更数")
    breaking_changes = Column(Integer, default=0, comment="破坏性变更数")
    non_breaking_changes = Column(Integer, default=0, comment="非破坏性变更数")
    diffs = Column(JSON, default=list, comment="差异详情")
    summary = Column(Text, nullable=True, comment="差异摘要")
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    __table_args__ = ({"comment": "契约差异记录表", "schema": "mystocks"},)


class ContractValidation(Base):
    """契约验证记录表"""

    __tablename__ = "contract_validations"

    id = Column(Integer, primary_key=True, index=True)
    version_id = Column(Integer, ForeignKey("mystocks.contract_versions.id"), comment="契约版本ID")
    valid = Column(Boolean, nullable=False, comment="是否通过验证")
    error_count = Column(Integer, default=0, comment="错误数")
    warning_count = Column(Integer, default=0, comment="警告数")
    results = Column(JSON, default=list, comment="验证结果详情")
    created_at = Column(DateTime, default=datetime.utcnow, comment="验证时间")

    __table_args__ = ({"comment": "契约验证记录表", "schema": "mystocks"},)
