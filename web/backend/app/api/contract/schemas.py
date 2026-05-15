"""
API契约管理 Pydantic模型
用于契约版本管理、差异检测和同步
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# ==================== 契约版本管理 ====================


class ContractVersionCreate(BaseModel):
    """创建契约版本请求"""

    name: str = Field(..., description="契约名称 (如: market-api, trade-api)")
    version: str = Field(..., description="版本号 (如: 1.0.0)")
    spec: Dict[str, Any] = Field(..., description="OpenAPI规范内容")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
    author: Optional[str] = Field(None, description="作者")
    description: Optional[str] = Field(None, description="版本描述")
    tags: List[str] = Field(default_factory=list, description="版本标签")


class ContractVersionUpdate(BaseModel):
    """更新契约版本请求"""

    description: Optional[str] = Field(None, description="版本描述")
    tags: Optional[List[str]] = Field(None, description="版本标签")


class ContractVersionResponse(BaseModel):
    """契约版本响应"""

    id: int = Field(..., description="版本ID")
    name: str = Field(..., description="契约名称")
    version: str = Field(..., description="版本号")
    spec: Dict[str, Any] = Field(..., description="OpenAPI规范内容")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
    author: Optional[str] = Field(None, description="作者")
    description: Optional[str] = Field(None, description="版本描述")
    tags: List[str] = Field(default_factory=list, description="版本标签")
    created_at: datetime = Field(..., description="创建时间")
    is_active: bool = Field(..., description="是否为当前激活版本")


# ==================== 契约差异检测 ====================


class DiffResult(BaseModel):
    """差异检测结果"""

    change_type: str = Field(..., description="变更类型: added|removed|modified")
    path: str = Field(..., description="JSON路径 (如: paths./api/market.get)")
    old_value: Optional[Any] = Field(None, description="旧值")
    new_value: Optional[Any] = Field(None, description="新值")
    is_breaking: bool = Field(default=False, description="是否为破坏性变更")
    description: Optional[str] = Field(None, description="变更描述")


class ContractDiffRequest(BaseModel):
    """契约差异检测请求"""

    from_version_id: int = Field(..., description="源版本ID")
    to_version_id: int = Field(..., description="目标版本ID")


class ContractDiffResponse(BaseModel):
    """契约差异检测响应"""

    from_version: str = Field(..., description="源版本号")
    to_version: str = Field(..., description="目标版本号")
    total_changes: int = Field(..., description="总变更数")
    breaking_changes: int = Field(..., description="破坏性变更数")
    non_breaking_changes: int = Field(..., description="非破坏性变更数")
    diffs: List[DiffResult] = Field(default_factory=list, description="差异列表")
    summary: str = Field(..., description="差异摘要")


# ==================== 契约影响分析 ====================


class ContractImpactRequest(BaseModel):
    """契约影响分析请求"""

    from_version_id: int = Field(..., description="源版本ID")
    to_version_id: int = Field(..., description="目标版本ID")


class ContractImpactItemResponse(BaseModel):
    """单项契约影响结果"""

    category: str = Field(..., description="影响类别: endpoint|schema|contract")
    name: str = Field(..., description="受影响对象名称")
    path: str = Field(..., description="受影响路径")
    change_type: str = Field(..., description="变更类型")
    severity: str = Field(..., description="严重级别")
    is_breaking: bool = Field(..., description="是否为破坏性影响")
    reason: str = Field(..., description="影响原因")


class ContractImpactSummaryResponse(BaseModel):
    """契约影响汇总"""

    total_impacts: int = Field(..., description="总影响项数量")
    breaking_impacts: int = Field(..., description="破坏性影响项数量")
    non_breaking_impacts: int = Field(..., description="非破坏性影响项数量")
    by_category: Dict[str, int] = Field(default_factory=dict, description="按类别统计的影响项数量")


class ContractMigrationEffortResponse(BaseModel):
    """契约迁移工作量估算"""

    level: str = Field(..., description="迁移工作量等级: none|low|medium|high|critical")
    score: int = Field(..., description="迁移工作量评分")
    estimated_hours_min: int = Field(..., description="预估最少迁移工时")
    estimated_hours_max: int = Field(..., description="预估最多迁移工时")
    drivers: List[str] = Field(default_factory=list, description="迁移工作量驱动因素")


class ContractImpactAnalysisResponse(BaseModel):
    """契约影响分析响应"""

    from_version: str = Field(..., description="源版本号")
    to_version: str = Field(..., description="目标版本号")
    risk_level: str = Field(..., description="综合风险等级")
    summary: ContractImpactSummaryResponse = Field(..., description="影响汇总")
    impacts: List[ContractImpactItemResponse] = Field(default_factory=list, description="影响明细")
    affected_endpoints: List[str] = Field(default_factory=list, description="受影响端点")
    affected_schemas: List[str] = Field(default_factory=list, description="受影响 Schema")
    affected_clients: List[str] = Field(default_factory=list, description="受影响客户端域")
    recommendations: List[str] = Field(default_factory=list, description="治理建议")
    migration_effort: ContractMigrationEffortResponse = Field(..., description="迁移工作量估算")


# ==================== 契约验证 ====================


class ValidationResult(BaseModel):
    """验证结果"""

    valid: bool = Field(..., description="是否通过验证")
    category: str = Field(..., description="问题类别: error|warning|info")
    path: Optional[str] = Field(None, description="问题路径")
    message: str = Field(..., description="问题描述")
    suggestion: Optional[str] = Field(None, description="修复建议")


class ContractValidateRequest(BaseModel):
    """契约验证请求"""

    spec: Dict[str, Any] = Field(..., description="待验证的OpenAPI规范")
    check_breaking_changes: bool = Field(default=True, description="是否检查破坏性变更")
    compare_to_version_id: Optional[int] = Field(None, description="对比的版本ID")


class ContractValidateResponse(BaseModel):
    """契约验证响应"""

    valid: bool = Field(..., description="是否通过验证")
    error_count: int = Field(..., description="错误数")
    warning_count: int = Field(..., description="警告数")
    results: List[ValidationResult] = Field(default_factory=list, description="验证结果列表")


# ==================== 契约同步 ====================


class SyncDirection(BaseModel):
    """同步方向"""

    code_to_contract: bool = Field(default=True, description="从代码生成契约")
    contract_to_typescript: bool = Field(default=False, description="从契约生成TypeScript")


class ContractSyncRequest(BaseModel):
    """契约同步请求"""

    name: str = Field(..., description="契约名称")
    direction: str = Field(default="code_to_db", description="同步方向: code_to_db | db_to_code")
    commit_hash: Optional[str] = Field(None, description="Git commit hash")
    author: Optional[str] = Field(None, description="作者")
    description: Optional[str] = Field(None, description="版本描述")


class SyncResult(BaseModel):
    """同步结果"""

    success: bool = Field(..., description="是否成功")
    version_id: Optional[int] = Field(None, description="版本ID")
    version: Optional[str] = Field(None, description="版本号")
    direction: str = Field(..., description="同步方向: code_to_db | db_to_code")
    changes: Dict[str, Any] = Field(default_factory=dict, description="变更详情")
    message: str = Field(..., description="结果消息")


class ContractSyncResponse(BaseModel):
    """契约同步响应"""

    sync_id: str = Field(..., description="同步任务ID")
    status: str = Field(..., description="状态: running|completed|failed")
    results: List[SyncResult] = Field(default_factory=list, description="同步结果列表")
    started_at: datetime = Field(..., description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")


# ==================== 契约列表 ====================


class ContractMetadata(BaseModel):
    """契约元数据"""

    name: str = Field(..., description="契约名称")
    latest_version: str = Field(..., description="最新版本")
    total_versions: int = Field(..., description="版本总数")
    last_updated: datetime = Field(..., description="最后更新时间")
    description: Optional[str] = Field(None, description="契约描述")
    tags: List[str] = Field(default_factory=list, description="标签")


class ContractListResponse(BaseModel):
    """契约列表响应"""

    contracts: List[ContractMetadata] = Field(default_factory=list, description="契约列表")
    total: int = Field(..., description="总数")
