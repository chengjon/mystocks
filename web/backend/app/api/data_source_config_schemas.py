"""
数据源配置 CRUD API 的请求模型定义。
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class DataSourceCreate(BaseModel):
    """创建数据源配置请求"""

    endpoint_name: str = Field(
        ..., description="端点名称（唯一标识）", min_length=1, max_length=255, example="akshare.stock_zh_a_hist"
    )
    source_name: str = Field(..., description="数据源名称", min_length=1, max_length=100, example="akshare")
    source_type: str = Field(..., description="数据源类型", min_length=1, max_length=50, example="http")
    data_category: str = Field(
        ...,
        description="数据分类",
        min_length=1,
        max_length=50,
        example="DAILY_KLINE",
    )
    parameters: Dict[str, Any] = Field(..., description="参数定义")
    test_parameters: Dict[str, Any] = Field(..., description="测试参数")
    priority: int = Field(default=5, description="优先级（1-10）", ge=1, le=10, example=5)
    description: str = Field(default="", description="描述信息", example="A股日线数据")

    @validator("data_category")
    def validate_data_category(cls, value: str) -> str:
        """验证数据分类"""
        valid_categories = ["DAILY_KLINE", "MINUTE_KLINE", "REALTIME_QUOTE", "FINANCIAL_DATA", "REFERENCE_DATA"]
        if value not in valid_categories:
            raise ValueError(f"Invalid data_category. Must be one of: {', '.join(valid_categories)}")
        return value


class DataSourceUpdate(BaseModel):
    """更新数据源配置请求"""

    priority: Optional[int] = Field(None, description="优先级（1-10）", ge=1, le=10)
    data_quality_score: Optional[float] = Field(None, description="质量评分（0-10）", ge=0, le=10)
    status: Optional[str] = Field(None, description="状态（active, maintenance, deprecated）")
    description: Optional[str] = Field(None, description="描述信息")
    parameters: Optional[Dict[str, Any]] = Field(None, description="参数定义")
    test_parameters: Optional[Dict[str, Any]] = Field(None, description="测试参数")


class BatchOperationItem(BaseModel):
    """单个批量操作项"""

    action: str = Field(..., description="操作类型: create, update, delete")
    endpoint_name: Optional[str] = Field(None, description="端点名称（update/delete时需要）")
    config: Optional[DataSourceCreate] = Field(None, description="配置信息（create时需要）")
    updates: Optional[DataSourceUpdate] = Field(None, description="更新信息（update时需要）")


class BatchOperationRequest(BaseModel):
    """批量操作请求"""

    operations: List[BatchOperationItem] = Field(..., description="操作列表", min_items=1, max_items=50)

    @validator("operations")
    def validate_operations(cls, value: List[BatchOperationItem]) -> List[BatchOperationItem]:
        """验证操作列表"""
        if not value:
            raise ValueError("Operations list cannot be empty")
        if len(value) > 50:
            raise ValueError("Maximum 50 operations allowed")
        return value


class RollbackRequest(BaseModel):
    """回滚请求"""

    changed_by: str = Field(default="system", description="变更人")


class ReloadRequest(BaseModel):
    """热重载请求"""

    changed_by: str = Field(default="system", description="变更人")
