# MyStocks API端点开发标准指南

> **使用说明**:
> 本文件是 API 相关的参考文档或专题说明，不是当前 API 契约、当前实施基线或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`；若涉及 API 契约事实源，再以实际的 FastAPI 路由 + Pydantic Schema + `/openapi.json` 为准。
>
> 文内端点、命令、统计值和示例如未重新复核，应视为参考或历史材料，不得直接当作当前事实。


## 概述

本文档定义了MyStocks项目中新增API端点时必须遵循的标准和规范，确保所有API保持一致性、可维护性和RESTful设计原则。

**版本**: 2.0.0
**最后更新**: 2025-12-02
**适用范围**: 所有新增API端点开发

---

## 🏗️ REST API设计原则

### 1. 资源导向设计
- 使用名词而非动词：`/users` 而非 `/getUsers`
- 复数形式表示集合：`/stocks`, `/strategies`
- 单数形式表示单个资源：`/stocks/{symbol}`, `/strategies/{id}`

### 2. HTTP方法语义
| 方法 | 用途 | 示例 |
|------|------|------|
| **GET** | 获取资源（安全、幂等） | `GET /stocks` |
| **POST** | 创建资源 | `POST /strategies` |
| **PUT** | 完整更新资源（幂等） | `PUT /strategies/{id}` |
| **PATCH** | 部分更新资源 | `PATCH /strategies/{id}` |
| **DELETE** | 删除资源（幂等） | `DELETE /strategies/{id}` |

### 3. 状态码规范
| 状态码 | 含义 | 使用场景 |
|---------|------|----------|
| **200** | 成功 | GET, PUT, DELETE 成功 |
| **201** | 创建成功 | POST 创建资源成功 |
| **204** | 无内容 | DELETE 成功无返回内容 |
| **400** | 请求错误 | 参数验证失败 |
| **401** | 未认证 | 缺少或无效令牌 |
| **403** | 无权限 | 权限不足 |
| **404** | 资源不存在 | 资源ID不存在 |
| **409** | 冲突 | 资源已存在 |
| **422** | 语义错误 | 业务逻辑错误 |
| **500** | 服务器错误 | 内部服务器错误 |

---

## 📝 API端点开发模板

### 1. 文件结构规范

```bash
web/backend/app/api/
├── module_name.py          # 主要模块文件
├── module_name_v2.py       # 版本化API（可选）
└── __init__.py             # 包初始化文件
```

### 2. 基础代码模板

```python
"""
模块功能描述

提供XXX相关的API端点，遵循REST API设计原则。

作者: [Your Name]
创建时间: YYYY-MM-DD
版本: 1.0.0
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel, Field

from app.core.responses import (
    APIResponse,
    ErrorResponse,
    PaginatedResponse,
    create_success_response,
    create_error_response,
    ErrorCodes,
)
from app.core.security import get_current_user, User
from app.services.module_service import ModuleService

# 创建路由器
router = APIRouter(
    prefix="/api/v1/module-name",  # 统一前缀
    tags=["模块名称"],                # Swagger文档标签
    responses={404: {"model": ErrorResponse, "description": "资源不存在"}},
)

# 依赖注入
module_service = ModuleService()


# 请求/响应模型
class ModuleCreateRequest(BaseModel):
    """创建模块请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="模块名称")
    description: Optional[str] = Field(None, max_length=500, description="模块描述")
    # 其他字段...

    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "name": "示例模块",
                "description": "这是一个示例模块",
            }
        }


class ModuleResponse(BaseModel):
    """模块响应模型"""
    id: int = Field(..., description="模块ID")
    name: str = Field(..., description="模块名称")
    description: Optional[str] = Field(None, description="模块描述")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        """Pydantic配置"""
        schema_extra = {
            "example": {
                "id": 1,
                "name": "示例模块",
                "description": "这是一个示例模块",
                "created_at": "2025-12-02T10:00:00Z",
                "updated_at": "2025-12-02T10:00:00Z",
            }
        }


# API端点定义
@router.post("/", response_model=APIResponse, status_code=201)
async def create_module(
    request: ModuleCreateRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    创建新模块

    Args:
        request: 模块创建请求数据
        current_user: 当前认证用户

    Returns:
        创建成功的模块信息

    Raises:
        HTTPException: 当创建失败时
    """
    try:
        # 参数验证
        if not request.name.strip():
            raise HTTPException(status_code=400, detail="模块名称不能为空")

        # 调用服务层
        result = await module_service.create_module(
            name=request.name,
            description=request.description,
            user_id=current_user.id,
        )

        # 返回统一响应格式
        return create_success_response(
            data=result,
            message="模块创建成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        # 记录错误日志
        logger.error(f"创建模块失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="创建模块失败，请稍后重试"
        )


@router.get("/", response_model=APIResponse)
async def get_modules(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(20, ge=1, le=100, description="每页大小"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取模块列表（支持分页和搜索）

    Args:
        page: 页码
        size: 每页大小
        search: 搜索关键词
        current_user: 当前认证用户

    Returns:
        模块列表和分页信息
    """
    try:
        # 参数验证
        if size > 100:
            raise HTTPException(status_code=400, detail="每页大小不能超过100")

        # 调用服务层
        result = await module_service.get_modules(
            user_id=current_user.id,
            page=page,
            size=size,
            search=search,
        )

        # 构建分页响应
        return PaginatedResponse.create(
            data=result["items"],
            page=page,
            size=size,
            total=result["total"],
            message="获取模块列表成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模块列表失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取模块列表失败，请稍后重试"
        )


@router.get("/{module_id}", response_model=APIResponse)
async def get_module(
    module_id: int = Path(..., ge=1, description="模块ID"),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    获取指定模块详情

    Args:
        module_id: 模块ID
        current_user: 当前认证用户

    Returns:
        模块详细信息

    Raises:
        HTTPException: 当模块不存在时返回404
    """
    try:
        # 调用服务层
        result = await module_service.get_module_by_id(
            module_id=module_id,
            user_id=current_user.id,
        )

        if not result:
            raise HTTPException(
                status_code=404,
                detail="模块不存在"
            )

        return create_success_response(
            data=result,
            message="获取模块详情成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模块详情失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="获取模块详情失败，请稍后重试"
        )


@router.put("/{module_id}", response_model=APIResponse)
async def update_module(
    module_id: int = Path(..., ge=1, description="模块ID"),
    request: ModuleCreateRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    更新指定模块

    Args:
        module_id: 模块ID
        request: 更新请求数据
        current_user: 当前认证用户

    Returns:
        更新后的模块信息

    Raises:
        HTTPException: 当模块不存在或更新失败时
    """
    try:
        # 检查模块是否存在
        existing = await module_service.get_module_by_id(
            module_id=module_id,
            user_id=current_user.id,
        )

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="模块不存在"
            )

        # 调用服务层更新
        result = await module_service.update_module(
            module_id=module_id,
            name=request.name,
            description=request.description,
            user_id=current_user.id,
        )

        return create_success_response(
            data=result,
            message="模块更新成功"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模块失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="更新模块失败，请稍后重试"
        )


@router.delete("/{module_id}", status_code=204)
async def delete_module(
    module_id: int = Path(..., ge=1, description="模块ID"),
    current_user: User = Depends(get_current_user),
) -> None:
    """
    删除指定模块

    Args:
        module_id: 模块ID
        current_user: 当前认证用户

    Raises:
        HTTPException: 当模块不存在或删除失败时
    """
    try:
        # 检查模块是否存在
        existing = await module_service.get_module_by_id(
            module_id=module_id,
            user_id=current_user.id,
        )

        if not existing:
            raise HTTPException(
                status_code=404,
                detail="模块不存在"
            )

        # 调用服务层删除
        success = await module_service.delete_module(
            module_id=module_id,
            user_id=current_user.id,
        )

        if not success:
            raise HTTPException(
                status_code=500,
                detail="删除模块失败"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模块失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="删除模块失败，请稍后重试"
        )
```

### 3. 服务层模板

```python
"""
模块服务层

提供模块相关的业务逻辑处理。

作者: [Your Name]
创建时间: YYYY-MM-DD
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from app.models.module import Module
from app.core.database import get_db_connection


class ModuleService:
    """模块服务类"""

    def __init__(self):
        """初始化服务"""
        self.db = get_db_connection()

    async def create_module(
        self,
        name: str,
        description: Optional[str] = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """创建模块"""
        # 实现创建逻辑
        pass

    async def get_modules(
        self,
        user_id: int,
        page: int = 1,
        size: int = 20,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """获取模块列表"""
        # 实现分页查询逻辑
        pass

    async def get_module_by_id(
        self,
        module_id: int,
        user_id: int
    ) -> Optional[Dict[str, Any]]:
        """根据ID获取模块"""
        # 实现详情查询逻辑
        pass

    async def update_module(
        self,
        module_id: int,
        name: str,
        description: Optional[str] = None,
        user_id: int = None
    ) -> Dict[str, Any]:
        """更新模块"""
        # 实现更新逻辑
        pass

    async def delete_module(
        self,
        module_id: int,
        user_id: int
    ) -> bool:
        """删除模块"""
        # 实现删除逻辑
        pass
```

---

## 🔍 开发检查清单

### ✅ 开发前检查

- [ ] **需求分析明确**
  - [ ] 业务需求文档完整
  - [ ] 数据模型已定义
  - [ ] 权限要求明确

- [ ] **技术方案设计**
  - [ ] API接口设计完成
  - [ ] 数据库表结构设计
  - [ ] 错误处理策略制定

- [ ] **开发环境准备**
  - [ ] 开发分支创建
  - [ ] 依赖包已安装
  - [ ] 数据库迁移脚本准备

### ✅ 开发过程中检查

- [ ] **代码规范遵循**
  - [ ] 使用统一代码模板
  - [ ] 命名规范符合项目标准
  - [ ] 类型注解完整
  - [ ] 文档字符串规范

- [ ] **RESTful设计**
  - [ ] HTTP方法语义正确
  - [ ] URL路径设计合理
  - [ ] 状态码使用正确
  - [ ] 资源命名规范

- [ ] **安全性实现**
  - [ ] 认证依赖注入正确
  - [ ] 权限检查完整
  - [ ] 输入验证充分
  - [ ] SQL注入防护

- [ ] **错误处理**
  - [ ] 异常捕获完整
  - [ ] 错误日志记录
  - [ ] 用户友好的错误消息
  - [ ] 统一错误响应格式

### ✅ 开发后检查

- [ ] **代码质量**
  - [ ] 代码审查通过
  - [ ] 单元测试编写
  - [ ] 集成测试通过
  - [ ] 性能测试完成

- [ ] **文档完善**
  - [ ] API文档更新
  - [ ] 代码注释充分
  - [ ] 使用示例提供
  - [ ] 部署文档更新

- [ ] **测试验证**
  - [ ] 功能测试通过
  - [ ] 边界条件测试
  - [ ] 安全测试验证
  - [ ] 性能基准测试

---

## 📚 最佳实践

### 1. 响应格式标准化

```python
# 成功响应
{
    "success": true,
    "data": {
        // 实际数据
    },
    "message": "操作成功",
    "timestamp": "2025-12-02T10:00:00Z"
}

# 分页响应
{
    "success": true,
    "data": [
        // 数据项列表
    ],
    "pagination": {
        "page": 1,
        "size": 20,
        "total": 100,
        "pages": 5
    },
    "message": "获取成功",
    "timestamp": "2025-12-02T10:00:00Z"
}

# 错误响应
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "参数验证失败",
        "details": {
            "field": "name",
            "reason": "名称不能为空"
        }
    },
    "message": "参数验证失败",
    "timestamp": "2025-12-02T10:00:00Z"
}
```

### 2. 参数验证

```python
from pydantic import BaseModel, Field, validator
from typing import Optional
import re

class UserCreateRequest(BaseModel):
    """用户创建请求模型"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        regex=r'^[a-zA-Z0-9_]+$',
        description="用户名（3-50字符，只能包含字母、数字和下划线）"
    )
    email: str = Field(
        ...,
        regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        description="邮箱地址"
    )
    age: Optional[int] = Field(
        None,
        ge=18,
        le=100,
        description="年龄（18-100岁）"
    )

    @validator('username')
    def validate_username(cls, v):
        """自定义验证器"""
        if v.lower() in ['admin', 'root', 'system']:
            raise ValueError('用户名不能使用保留词')
        return v
```

### 3. 错误处理

```python
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class APIError(Exception):
    """自定义API异常"""
    def __init__(self, message: str, error_code: str = "API_ERROR"):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

# 异常处理装饰器
def handle_api_errors(func):
    """API错误处理装饰器"""
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except APIError as e:
            logger.error(f"API错误: {e.message}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error_code": e.error_code,
                    "message": e.message
                }
            )
        except Exception as e:
            logger.error(f"未预期错误: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail="服务器内部错误"
            )
    return wrapper
```

### 4. 缓存策略

```python
from app.core.cache import cache_manager
import hashlib
import json

class CacheMixin:
    """缓存混入类"""

    def get_cache_key(self, prefix: str, **kwargs) -> str:
        """生成缓存键"""
        key_data = {
            'prefix': prefix,
            'params': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()

    async def get_cached_data(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        return await cache_manager.get(key)

    async def set_cached_data(
        self,
        key: str,
        data: Any,
        ttl: int = 3600
    ) -> None:
        """设置缓存数据"""
        await cache_manager.set(key, data, ttl)

    async def invalidate_cache(self, pattern: str) -> None:
        """失效缓存"""
        await cache_manager.delete_pattern(pattern)
```

### 5. 权限控制

```python
from enum import Enum
from typing import List

class Permission(Enum):
    """权限枚举"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

def require_permissions(required_permissions: List[Permission]):
    """权限验证装饰器"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(status_code=401, detail="未认证")

            user_permissions = current_user.get('permissions', [])

            for permission in required_permissions:
                if permission.value not in user_permissions:
                    raise HTTPException(
                        status_code=403,
                        detail=f"缺少权限: {permission.value}"
                    )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@router.post("/admin/users")
@require_permissions([Permission.ADMIN])
async def create_user_admin(
    request: UserCreateRequest,
    current_user: User = Depends(get_current_user),
):
    """管理员创建用户"""
    pass
```

---

## 🚀 部署和监控

### 1. 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        try:
            result = await func(*args, **kwargs)

            # 记录性能指标
            execution_time = time.time() - start_time
            logger.info(f"API性能: {func.__name__} 执行时间: {execution_time:.3f}s")

            # 发送到监控系统
            await send_metrics(
                metric_name="api_execution_time",
                value=execution_time,
                tags={"endpoint": func.__name__}
            )

            return result

        except Exception as e:
            # 记录错误指标
            await send_metrics(
                metric_name="api_error_count",
                value=1,
                tags={"endpoint": func.__name__, "error": str(e)}
            )
            raise

    return wrapper

# 使用示例
@router.get("/stocks")
@monitor_performance
async def get_stocks():
    """获取股票列表"""
    pass
```

### 2. API版本控制

```python
# 版本化路由
from fastapi import APIRouter

v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v1_router.get("/stocks")
async def get_stocks_v1():
    """v1版本的股票接口"""
    pass

@v2_router.get("/stocks")
async def get_stocks_v2():
    """v2版本的股票接口"""
    pass
```

### 3. 文档自动生成

```python
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="MyStocks API",
    description="量化交易平台API文档",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 自定义OpenAPI信息
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="MyStocks API",
        version="2.0.0",
        description="## 认证\n\n所有API都需要JWT认证\n\n```bash\nBearer <token>\n```",
        routes=app.routes,
    )

    # 添加自定义信息
    openapi_schema["info"]["x-logo"] = {
        "url": "https://mystocks.com/logo.png"
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## 📋 开发工作流程

### 1. 需求分析阶段
1. 与产品经理沟通需求
2. 设计API接口规范
3. 评审技术方案
4. 确定开发计划

### 2. 开发阶段
1. 创建开发分支
2. 实现服务层逻辑
3. 实现API端点
4. 编写单元测试
5. 编写集成测试

### 3. 测试阶段
1. 功能测试
2. 性能测试
3. 安全测试
4. 文档验证

### 4. 部署阶段
1. 代码审查
2. 合并到主分支
3. 部署到测试环境
4. 部署到生产环境

### 5. 监控维护
1. 性能监控
2. 错误日志监控
3. 用户反馈收集
4. 持续优化改进

---

## 📞 技术支持

如果在开发过程中遇到问题，请参考以下资源：

- **项目文档**: `/docs/api/`
- **API文档**: `/api/docs`
- **代码规范**: `.claude/skills/backend-dev-guidelines/`
- **问题反馈**: 创建GitHub Issue

**联系方式**: dev-team@mystocks.com

---

*本指南将根据项目发展和团队反馈持续更新和完善。*
