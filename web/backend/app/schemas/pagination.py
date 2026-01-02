"""
统一分页和排序模型

提供标准的分页请求/响应模型和排序参数模型，
用于所有列表查询API。
"""

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field, field_validator

T = TypeVar("T")


class PaginationParams(BaseModel):
    """
    统一分页请求参数

    **示例**:
    ```python
    @router.get("/users")
    async def get_users(pagination: PaginationParams = Depends()):
        # pagination.page = 1
        # pagination.page_size = 20
        pass
    ```
    """

    page: int = Field(
        default=1,
        ge=1,
        description="页码（从1开始）",
        examples=[1, 2, 3],
    )
    page_size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="每页数量（1-100）",
        examples=[10, 20, 50],
    )

    @field_validator("page_size")
    @classmethod
    def validate_page_size(cls, v: int) -> int:
        """验证page_size在合理范围内"""
        if v < 1:
            raise ValueError("page_size必须大于0")
        if v > 100:
            raise ValueError("page_size不能超过100")
        return v

    @property
    def offset(self) -> int:
        """计算数据库查询的偏移量"""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """获取数据库查询的limit值"""
        return self.page_size


class PaginatedResponse(BaseModel, Generic[T]):
    """
    统一分页响应模型

    **示例**:
    ```python
    return PaginatedResponse[UserSchema](
        data=users,
        total=100,
        page=1,
        page_size=20
    )
    ```
    """

    data: List[T] = Field(..., description="当前页数据列表")
    total: int = Field(..., ge=0, description="总记录数")
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, description="每页数量")

    @property
    def total_pages(self) -> int:
        """计算总页数"""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """是否有下一页"""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页"""
        return self.page > 1

    def model_dump(self, **kwargs) -> dict:
        """转换为字典（包含计算属性）"""
        return {
            "data": self.data,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "has_next": self.has_next,
            "has_prev": self.has_prev,
        }


class SortParams(BaseModel):
    """
    统一排序参数模型

    **示例**:
    ```python
    @router.get("/users")
    async def get_users(sort: SortParams = Depends()):
        # sort.sort_by = "created_at"
        # sort.order = "desc"
        pass
    ```
    """

    sort_by: str = Field(
        default="id",
        description="排序字段名",
        examples=["id", "created_at", "name"],
    )
    order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="排序方向（asc升序/desc降序）",
        examples=["asc", "desc"],
    )

    @field_validator("sort_by")
    @classmethod
    def validate_sort_by(cls, v: str, values) -> str:
        """
        验证排序字段是否在允许的列表中

        **使用示例**:
        ```python
        class MySortParams(SortParams):
            # 定义允许排序的字段
            _allowed_fields = {"id", "name", "created_at"}

            @field_validator("sort_by")
            def validate_field(cls, v):
                if v not in cls._allowed_fields:
                    raise ValueError(f"排序字段必须是以下之一: {cls._allowed_fields}")
                return v
        ```
        """
        # 基本验证：只允许字母、数字、下划线
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("排序字段只能包含字母、数字、下划线和点")
        return v

    def get_order_by_clause(self) -> str:
        """
        生成SQL ORDER BY子句

        **返回**: "field_name ASC" 或 "field_name DESC"
        """
        return f"{self.sort_by} {self.order.upper()}"

    def get_sort_dict(self) -> dict:
        """
        生成MongoDB/Pydantic排序字典

        **返回**: {"field_name": 1} 或 {"field_name": -1}
        """
        return {self.sort_by: 1 if self.order == "asc" else -1}


class FilterParams(BaseModel):
    """
    通用过滤参数基类

    子类可以扩展特定的过滤字段

    **示例**:
    ```python
    class StockFilterParams(FilterParams):
        symbol: Optional[str] = None
        exchange: Optional[str] = None
        start_date: Optional[date] = None
        end_date: Optional[date] = None
    ```
    """

    def get_where_clauses(self) -> tuple:
        """
        生成SQL WHERE子句

        **返回**: (where_sql, params_dict)
        """
        clauses = []
        params = {}

        for field, value in self.model_dump(exclude_unset=True).items():
            if value is not None:
                clauses.append(f"{field} = :{field}")
                params[field] = value

        where_sql = " AND ".join(clauses) if clauses else "1=1"
        return where_sql, params


# ============================================================================
# 便捷依赖函数
# ============================================================================


def get_pagination_params(
    page: int = 1,
    page_size: int = 20,
) -> PaginationParams:
    """
    从查询参数获取分页参数

    **使用示例**:
    ```python
    @router.get("/items")
    async def get_items(pagination: PaginationParams = Depends(get_pagination_params)):
        return paginated_response(items, pagination, total_count)
    ```
    """
    return PaginationParams(page=page, page_size=page_size)


def get_sort_params(
    sort_by: str = "id",
    order: str = "asc",
) -> SortParams:
    """
    从查询参数获取排序参数

    **使用示例**:
    ```python
    @router.get("/items")
    async def get_items(sort: SortParams = Depends(get_sort_params)):
        order_by = sort.get_order_by_clause()
        ...
    ```
    """
    return SortParams(sort_by=sort_by, order=order)


# ============================================================================
# 辅助函数
# ============================================================================


def create_paginated_response(
    data: List[T],
    total: int,
    pagination: PaginationParams,
) -> PaginatedResponse[T]:
    """
    创建分页响应

    **参数**:
        data: 当前页数据列表
        total: 总记录数
        pagination: 分页参数

    **返回**: PaginatedResponse对象

    **示例**:
    ```python
    users = query.limit(pagination.page_size).offset(pagination.offset).all()
    total = query.count()
    return create_paginated_response(users, total, pagination)
    ```
    """
    return PaginatedResponse[T](
        data=data,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
    )
