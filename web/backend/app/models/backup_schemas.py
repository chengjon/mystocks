"""
备份和恢复数据模型

提供安全的 Pydantic 模型用于备份和恢复操作的请求验证
包含输入验证、路径安全检查和权限控制

版本: 1.0.0
日期: 2025-12-01
"""

import re
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, validator

# 安全正则表达式模式
SAFE_BACKUP_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
SAFE_TABLE_NAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]*$")
SAFE_DATABASE_TYPE_PATTERN = re.compile(r"^(tdengine|postgresql)$")
SAFE_BACKUP_TYPE_PATTERN = re.compile(r"^(full|incremental)$")
SAFE_STATUS_PATTERN = re.compile(r"^(success|failed|pending)$")


class BackupRequestBase(BaseModel):
    """备份请求基础模型"""

    class Config:
        str_strip_whitespace = True
        validate_assignment = True


class TDengineFullBackupRequest(BackupRequestBase):
    """TDengine 全量备份请求模型"""

    description: Optional[str] = Field(None, description="备份描述信息", max_length=500)

    tags: Optional[List[str]] = Field(None, description="备份标签", max_items=10)

    @validator("tags")
    def validate_tags(cls, v):
        if v:
            for tag in v:
                if not tag or len(tag.strip()) == 0:
                    raise ValueError("标签不能为空")
                if len(tag) > 50:
                    raise ValueError("单个标签长度不能超过50字符")
        return v


class TDengineIncrementalBackupRequest(BackupRequestBase):
    """TDengine 增量备份请求模型"""

    since_backup_id: str = Field(..., description="基准备份ID", min_length=3, max_length=100)

    description: Optional[str] = Field(None, description="备份描述信息", max_length=500)

    @validator("since_backup_id")
    def validate_backup_id(cls, v):
        if not SAFE_BACKUP_ID_PATTERN.match(v):
            raise ValueError("备份ID只能包含字母、数字、下划线和连字符")
        return v


class PostgreSQLFullBackupRequest(BackupRequestBase):
    """PostgreSQL 全量备份请求模型"""

    exclude_tables: Optional[List[str]] = Field(None, description="要排除的表名列表", max_items=50)

    include_tables: Optional[List[str]] = Field(None, description="要包含的表名列表（空则备份所有表）", max_items=200)

    compression_level: int = Field(6, description="压缩级别 (1-9)", ge=1, le=9)

    description: Optional[str] = Field(None, description="备份描述信息", max_length=500)

    @validator("exclude_tables", "include_tables")
    def validate_table_names(cls, v):
        if v:
            for table_name in v:
                if not table_name or len(table_name.strip()) == 0:
                    raise ValueError("表名不能为空")
                if len(table_name) > 63:
                    raise ValueError("表名长度不能超过63字符")
                if not SAFE_TABLE_NAME_PATTERN.match(table_name):
                    raise ValueError("表名只能以字母开头，包含字母、数字和下划线")
        return v


class RecoveryRequestBase(BaseModel):
    """恢复请求基础模型"""

    dry_run: bool = Field(False, description="测试运行模式，不实际执行恢复")

    force: bool = Field(False, description="强制覆盖现有数据")

    backup_id: str = Field(..., description="备份文件ID", min_length=3, max_length=100)

    @validator("backup_id")
    def validate_backup_id(cls, v):
        if not SAFE_BACKUP_ID_PATTERN.match(v):
            raise ValueError("备份ID只能包含字母、数字、下划线和连字符")
        return v


class TDengineFullRecoveryRequest(RecoveryRequestBase):
    """TDengine 全量恢复请求模型"""

    target_tables: Optional[List[str]] = Field(None, description="要恢复的指定表列表", max_items=200)

    restore_to_database: Optional[str] = Field(None, description="恢复到目标数据库名", min_length=1, max_length=63)

    @validator("target_tables")
    def validate_table_names(cls, v):
        if v:
            for table_name in v:
                if not table_name or len(table_name.strip()) == 0:
                    raise ValueError("表名不能为空")
                if len(table_name) > 191:  # TDengine 表名长度限制
                    raise ValueError("TDengine表名长度不能超过191字符")
                if not SAFE_TABLE_NAME_PATTERN.match(table_name):
                    raise ValueError("表名只能以字母开头，包含字母、数字和下划线")
        return v


class PostgreSQLFullRecoveryRequest(RecoveryRequestBase):
    """PostgreSQL 全量恢复请求模型"""

    target_tables: Optional[List[str]] = Field(None, description="要恢复的指定表列表", max_items=200)

    restore_to_database: Optional[str] = Field(None, description="恢复到目标数据库名", min_length=1, max_length=63)

    drop_existing: bool = Field(False, description="恢复前删除现有表/数据库")

    @validator("target_tables")
    def validate_table_names(cls, v):
        if v:
            for table_name in v:
                if not table_name or len(table_name.strip()) == 0:
                    raise ValueError("表名不能为空")
                if len(table_name) > 63:
                    raise ValueError("PostgreSQL表名长度不能超过63字符")
                if not SAFE_TABLE_NAME_PATTERN.match(table_name):
                    raise ValueError("表名只能以字母开头，包含字母、数字和下划线")
        return v


class TDenginePITRRequest(BaseModel):
    """TDengine 点对点时间恢复请求模型"""

    target_time: str = Field(..., description="目标恢复时间 (ISO 8601格式)")

    target_tables: Optional[List[str]] = Field(None, description="要恢复的指定表列表", max_items=200)

    restore_to_database: Optional[str] = Field(None, description="恢复到目标数据库名", min_length=1, max_length=63)

    @validator("target_time")
    def validate_target_time(cls, v):
        try:
            # 验证 ISO 8601 格式
            datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("时间格式无效，请使用ISO 8601格式 (如: 2025-01-01T12:00:00)")
        return v

    @validator("target_tables")
    def validate_table_names(cls, v):
        if v:
            for table_name in v:
                if not table_name or len(table_name.strip()) == 0:
                    raise ValueError("表名不能为空")
                if len(table_name) > 191:
                    raise ValueError("TDengine表名长度不能超过191字符")
                if not SAFE_TABLE_NAME_PATTERN.match(table_name):
                    raise ValueError("表名只能以字母开头，包含字母、数字和下划线")
        return v


class BackupListQueryParams(BaseModel):
    """备份列表查询参数模型"""

    database: Optional[str] = Field(None, description="数据库类型 (tdengine/postgresql)")

    backup_type: Optional[str] = Field(None, description="备份类型 (full/incremental)")

    status: Optional[str] = Field(None, description="备份状态 (success/failed/pending)")

    limit: int = Field(50, description="返回记录数限制", ge=1, le=1000)

    offset: int = Field(0, description="跳过记录数", ge=0)

    start_date: Optional[str] = Field(None, description="开始日期 (ISO 8601)")

    end_date: Optional[str] = Field(None, description="结束日期 (ISO 8601)")

    @validator("database")
    def validate_database(cls, v):
        if v and not SAFE_DATABASE_TYPE_PATTERN.match(v):
            raise ValueError("数据库类型只能是 tdengine 或 postgresql")
        return v

    @validator("backup_type")
    def validate_backup_type(cls, v):
        if v and not SAFE_BACKUP_TYPE_PATTERN.match(v):
            raise ValueError("备份类型只能是 full 或 incremental")
        return v

    @validator("status")
    def validate_status(cls, v):
        if v and not SAFE_STATUS_PATTERN.match(v):
            raise ValueError("状态只能是 success、failed 或 pending")
        return v

    @validator("start_date", "end_date")
    def validate_date(cls, v):
        if v:
            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError("日期格式无效，请使用ISO 8601格式")
        return v


class CleanupBackupsRequest(BaseModel):
    """清理过期备份请求模型"""

    retention_days: int = Field(30, description="备份保留天数", ge=1, le=3650)  # 最大10年

    database: Optional[str] = Field(None, description="指定数据库类型 (tdengine/postgresql)")

    backup_type: Optional[str] = Field(None, description="指定备份类型 (full/incremental)")

    dry_run: bool = Field(False, description="测试运行，不实际删除文件")

    force: bool = Field(False, description="强制删除，忽略安全警告")

    @validator("database")
    def validate_database(cls, v):
        if v and not SAFE_DATABASE_TYPE_PATTERN.match(v):
            raise ValueError("数据库类型只能是 tdengine 或 postgresql")
        return v

    @validator("backup_type")
    def validate_backup_type(cls, v):
        if v and not SAFE_BACKUP_TYPE_PATTERN.match(v):
            raise ValueError("备份类型只能是 full 或 incremental")
        return v


class SchedulerControlRequest(BaseModel):
    """调度器控制请求模型"""

    action: Literal["start", "stop", "restart", "status"] = Field(..., description="调度器操作")

    force: bool = Field(False, description="强制执行操作")


# ============================================================================
# 响应模型 (基于统一响应格式)
# ============================================================================


class BackupMetadata(BaseModel):
    """备份元数据响应模型"""

    backup_id: str
    backup_type: str
    database: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None
    tables_backed_up: List[str]
    total_rows: int
    backup_size_mb: float
    compression_ratio: Optional[float] = None
    status: str
    error_message: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class RecoveryMetadata(BaseModel):
    """恢复操作元数据"""

    backup_id: str
    recovery_type: str
    target_time: Optional[str] = None
    target_tables: Optional[List[str]] = None
    dry_run: bool
    success: bool
    message: str
    start_time: str
    end_time: Optional[str] = None
    duration_seconds: Optional[float] = None


class IntegrityVerificationResult(BaseModel):
    """完整性验证结果模型"""

    backup_id: str
    is_valid: bool
    verification_details: Dict[str, Any]
    report_file_path: Optional[str] = None
    verification_time: str


class ScheduledJobInfo(BaseModel):
    """计划任务信息模型"""

    job_id: str
    job_type: str
    schedule: str
    next_run: Optional[str] = None
    last_run: Optional[str] = None
    status: str
    description: Optional[str] = None


class CleanupResult(BaseModel):
    """清理操作结果模型"""

    success: bool
    message: str
    deleted_count: int
    freed_space_mb: float
    deleted_files: Optional[List[str]] = None
    retention_days: int
    dry_run: bool


# ============================================================================
# 权限验证辅助函数
# ============================================================================


def require_admin_role(user_role: str) -> bool:
    """检查是否为管理员权限"""
    return user_role.lower() == "admin"


def require_backup_permission(user_role: str) -> bool:
    """检查备份操作权限（管理员和备份操作员）"""
    allowed_roles = ["admin", "backup_operator"]
    return user_role.lower() in allowed_roles


def require_recovery_permission(user_role: str) -> bool:
    """检查恢复操作权限（仅管理员）"""
    return user_role.lower() == "admin"
