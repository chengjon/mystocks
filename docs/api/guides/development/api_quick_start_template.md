# API端点开发快速开始模板

## 🚀 5分钟创建新API端点

### 步骤1: 创建API文件

```bash
# 在 web/backend/app/api/ 目录下创建新文件
touch web/backend/app/api/mymodule.py
```

### 步骤2: 复制基础模板

```python
"""
我的模块 API

功能描述: [在此填写功能描述]

作者: [Your Name]
创建时间: 2025-12-02
版本: 1.0.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from app.core.responses import (
    APIResponse,
    PaginatedResponse,
    create_success_response,
)
from app.core.security import get_current_user, User

# 创建路由器
router = APIRouter(
    prefix="/api/v1/mymodule",
    tags=["我的模块"],
)


# 请求模型
class MyModuleCreateRequest(BaseModel):
    """创建我的模块请求"""
    name: str = Field(..., min_length=1, max_length=100, description="模块名称")
    description: Optional[str] = Field(None, max_length=500, description="模块描述")

    class Config:
        schema_extra = {
            "example": {
                "name": "示例模块",
                "description": "这是示例模块描述",
            }
        }


# 响应模型
class MyModuleResponse(BaseModel):
    """我的模块响应"""
    id: int = Field(..., description="模块ID")
    name: str = Field(..., description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "name": "示例模块",
                "description": "这是示例模块描述",
                "created_at": "2025-12-02T10:00:00Z",
            }
        }


# GET端点示例
@router.get("/", response_model=APIResponse)
async def get_my_modules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取我的模块列表

    Args:
        page: 页码
        size: 每页大小
        current_user: 当前用户

    Returns:
        模块列表
    """
    try:
        # TODO: 实现业务逻辑
        mock_data = [
            {
                "id": 1,
                "name": "示例模块1",
                "description": "这是示例模块1的描述",
                "created_at": datetime.now().isoformat(),
            },
            {
                "id": 2,
                "name": "示例模块2",
                "description": "这是示例模块2的描述",
                "created_at": datetime.now().isoformat(),
            },
        ]

        return PaginatedResponse.create(
            data=mock_data,
            page=page,
            size=size,
            total=len(mock_data),
            message="获取模块列表成功"
        )

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取模块列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取模块列表失败")


# POST端点示例
@router.post("/", response_model=APIResponse, status_code=201)
async def create_my_module(
    request: MyModuleCreateRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    创建我的模块

    Args:
        request: 创建请求数据
        current_user: 当前用户

    Returns:
        创建的模块信息
    """
    try:
        # TODO: 实现业务逻辑
        new_module = {
            "id": 999,
            "name": request.name,
            "description": request.description,
            "created_at": datetime.now().isoformat(),
        }

        return create_success_response(
            data=new_module,
            message="模块创建成功"
        )

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"创建模块失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="创建模块失败")


# GET单条记录示例
@router.get("/{module_id}", response_model=APIResponse)
async def get_my_module(
    module_id: int = Path(..., ge=1, description="模块ID"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取指定模块详情

    Args:
        module_id: 模块ID
        current_user: 当前用户

    Returns:
        模块详细信息
    """
    try:
        # TODO: 实现业务逻辑
        if module_id not in [1, 2]:
            raise HTTPException(status_code=404, detail="模块不存在")

        module_data = {
            "id": module_id,
            "name": f"示例模块{module_id}",
            "description": f"这是示例模块{module_id}的详细信息",
            "created_at": datetime.now().isoformat(),
        }

        return create_success_response(
            data=module_data,
            message="获取模块详情成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"获取模块详情失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取模块详情失败")


# DELETE端点示例
@router.delete("/{module_id}", status_code=204)
async def delete_my_module(
    module_id: int = Path(..., ge=1, description="模块ID"),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    删除指定模块

    Args:
        module_id: 模块ID
        current_user: 当前用户
    """
    try:
        # TODO: 实现业务逻辑
        if module_id not in [1, 2]:
            raise HTTPException(status_code=404, detail="模块不存在")

        # 删除逻辑（实际项目中调用服务层）
        pass

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"删除模块失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="删除模块失败")
```

### 步骤3: 注册路由

在 `web/backend/app/main.py` 中注册新路由：

```python
# 在 main.py 中添加导入
from app.api.mymodule import router as mymodule_router

# 在路由注册部分添加
app.include_router(mymodule_router)
```

### 步骤4: 测试API

```bash
# 重启后端服务
python -m uvicorn web.backend.app.main:app --reload

# 测试API端点
curl -X GET "http://localhost:8000/api/v1/mymodule/" \
  -H "Authorization: Bearer YOUR_TOKEN"

curl -X POST "http://localhost:8000/api/v1/mymodule/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "新模块", "description": "新模块描述"}'
```

### 步骤5: 查看API文档

访问 Swagger 文档：
```
http://localhost:8000/api/docs
```

---

## 🔧 常用代码片段

### 1. 数据库操作

```python
from app.core.database import get_db_connection

async def get_data_from_db():
    """从数据库获取数据"""
    db = get_db_connection()

    try:
        # 查询数据
        query = "SELECT * FROM my_table WHERE user_id = %s"
        results = await db.fetch_all(query, (current_user.id,))

        return results
    finally:
        await db.close()
```

### 2. 缓存使用

```python
from app.core.cache import cache_manager

async def get_cached_data(cache_key: str):
    """获取缓存数据"""
    # 尝试从缓存获取
    cached_data = await cache_manager.get(cache_key)
    if cached_data:
        return cached_data

    # 从数据库获取
    data = await get_data_from_db()

    # 设置缓存
    await cache_manager.set(cache_key, data, ttl=3600)

    return data
```

### 3. 参数验证

```python
from pydantic import BaseModel, Field, validator
from datetime import datetime

class AdvancedRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., regex=r'^[^@]+@[^@]+\.[^@]+$')
    age: int = Field(..., ge=18, le=100)
    tags: List[str] = Field(default=[], max_items=10)

    @validator('name')
    def name_must_not_contain_spaces(cls, v):
        if ' ' in v:
            raise ValueError('名称不能包含空格')
        return v

    @validator('tags')
    def tags_must_be_unique(cls, v):
        if len(v) != len(set(v)):
            raise ValueError('标签不能重复')
        return v
```

### 4. 错误处理

```python
class BusinessException(Exception):
    """业务异常"""
    def __init__(self, message: str, error_code: str = "BUSINESS_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

@router.get("/example")
async def example_endpoint():
    """示例端点"""
    try:
        # 业务逻辑
        if some_condition:
            raise BusinessException("业务逻辑错误", "INVALID_CONDITION")

        return create_success_response(data={"result": "success"})

    except BusinessException as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error_code": e.error_code,
                "message": e.message
            }
        )
    except Exception as e:
        import logging
        logger.error(f"未知错误: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="服务器内部错误")
```

### 5. 分页查询

```python
from fastapi import Query

@router.get("/items")
async def get_items(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
):
    """分页获取项目列表"""
    try:
        # 计算偏移量
        offset = (page - 1) * size

        # 构建查询条件
        where_conditions = []
        params = []

        if search:
            where_conditions.append("name LIKE %s")
            params.append(f"%{search}%")

        # 构建SQL
        query = f"""
            SELECT * FROM items
            {'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
        """

        params.extend([size, offset])

        # 执行查询
        db = get_db_connection()
        items = await db.fetch_all(query, params)

        # 获取总数
        count_query = f"""
            SELECT COUNT(*) FROM items
            {'WHERE ' + ' AND '.join(where_conditions) if where_conditions else ''}
        """
        total = await db.fetch_one(count_query, params[:len(params)-2])

        await db.close()

        return PaginatedResponse.create(
            data=items,
            page=page,
            size=size,
            total=total['count'],
            message="获取项目列表成功"
        )

    except Exception as e:
        import logging
        logger.error(f"获取项目列表失败: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="获取项目列表失败")
```

---

## 📚 扩展资源

- **完整开发指南**: `/docs/api/API_DEVELOPMENT_GUIDELINES.md`
- **检查清单**: `/docs/api/API_DEVELOPMENT_CHECKLIST.md`
- **API端点列表**: `/docs/api/API_ENDPOINT_DOCUMENTATION.md`
- **项目文档结构**: `/docs/`

---

## 🆘 获取帮助

如果在开发过程中遇到问题：

1. **查看现有代码**: 参考 `/web/backend/app/api/` 中的其他模块
2. **阅读文档**: 查看完整开发指南和检查清单
3. **咨询团队**: 联系 dev-team@mystocks.com
4. **创建Issue**: 在GitHub仓库创建技术问题

---

*模板会根据项目发展和最佳实践持续更新*
