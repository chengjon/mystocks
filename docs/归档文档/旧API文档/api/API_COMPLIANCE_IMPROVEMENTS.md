# MyStocks API 合规性改进建议

## 高优先级修复 (1-2周内)

### 修复 1: 统一响应格式

**当前问题**: API 返回格式不一致，混合使用多种响应模式

**解决方案**: 强制使用 `app.core.responses` 中定义的标准响应格式

```python
# 需要更新的文件: auth.py, dashboard.py, data.py, market.py, strategy.py

# ❌ 当前实现 (多种格式)
return {"users": users, "total": len(users)}                           # 格式1
return {"success": True, "data": result}                             # 格式2
return {"message": "登出成功", "success": True}                       # 格式3

# ✅ 统一改进 (使用标准格式)
from app.core.responses import create_success_response, create_error_response, ErrorCodes

# 成功响应
return create_success_response(
    data={"users": users, "total": len(users)},
    message="获取用户列表成功"
)

# 错误响应
except Exception as e:
    return create_error_response(
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        message="获取用户列表失败",
        details={"original_error": str(e)}
    )
```

### 修复 2: 添加认证覆盖

**当前问题**: 多个端点缺少认证保护

**解决方案**: 为所有需要认证的端点添加 `get_current_user` 依赖

```python
# 需要更新的文件: health.py, data.py, market.py

# ❌ 当前实现 (无认证)
@router.get("/health")
async def check_system_health(request: Request):

@router.get("/markets/overview")
async def get_market_overview(current_user: User = Depends(get_current_user)):

# ✅ 统一改进 (添加认证)
from app.api.auth import get_current_user, User

@router.get("/health")
async def check_system_health(
    request: Request,
    current_user: User = Depends(get_current_user)  # 添加认证
):

# 对于公开的健康检查端点，创建单独的公开版本
@router.get("/health/public")
async def public_health_check():
    # 公开健康检查，无需认证
    pass
```

### 修复 3: 完善参数验证

**当前问题**: Pydantic 模型验证规则不完整

**解决方案**: 增强字段验证规则和自定义验证器

```python
# 需要更新的文件: 所有包含请求模型的文件

# ❌ 当前实现 (基础验证)
class AddWatchlistRequest(BaseModel):
    symbol: str = Field(..., description="股票代码")
    notes: str = Field(None, description="备注")

# ✅ 改进实现 (完整验证)
from pydantic import BaseModel, Field, validator
import re
from datetime import datetime

class AddWatchlistRequest(BaseModel):
    symbol: str = Field(
        ...,
        min_length=6,
        max_length=10,
        regex=r'^[0-9]{6}$',
        description="股票代码 (6位数字，如: 000001)"
    )
    display_name: str = Field(
        None,
        max_length=100,
        description="显示名称 (最多100字符)"
    )
    notes: str = Field(
        None,
        max_length=500,
        description="备注内容 (最多500字符)"
    )
    group_name: str = Field(
        None,
        max_length=50,
        description="分组名称 (最多50字符)"
    )

    @validator('symbol')
    def validate_symbol(cls, v):
        """验证股票代码格式"""
        if not v.isdigit():
            raise ValueError('股票代码必须为6位数字')
        return v

    @validator('group_name')
    def validate_group_name(cls, v):
        """验证分组名称"""
        if v and len(v.strip()) == 0:
            raise ValueError('分组名称不能为空')
        return v.strip() if v else v
```

### 修复 4: RESTful 路径设计

**当前问题**: 非RESTful路径设计，资源命名不规范

**解决方案**: 重构端点路径，遵循REST原则

```python
# 需要更新的文件: market.py, data.py

# ❌ 当前实现 (非RESTful)
@router.post("/fund-flow/refresh")
@router.post("/etf/refresh")
@router.post("/lhb/refresh")
@router.get("/stocks/intraday")  # 应该用路径参数

# ✅ RESTful改进
# 1. 刷新操作使用 PUT 方法
@router.put("/market/fund-flow/{symbol}/refresh")
@router.put("/market/etf/refresh")
@router.put("/market/lhb/{date}/refresh")

# 2. 资源使用路径参数
@router.get("/stocks/{symbol}/intraday")
@router.get("/stocks/{symbol}/kline")
@router.get("/stocks/{symbol}/detail")
@router.get("/stocks/{symbol}/trading-summary")

# 3. 统一资源路径前缀
# 而不是混合使用 /api/market 和 /api/data
# 统一为 /api/market/xxx 或 /api/stocks/xxx
```

## 中优先级修复 (2-4周内)

### 修复 5: 完善 Swagger 文档

**当前问题**: 缺少完整的响应模型和示例

**解决方案**: 添加完整的 response_model 和示例

```python
# 需要更新的文件: 所有API文件

# ❌ 当前实现 (缺少响应模型)
@router.get("/stocks/basic")
async def get_stocks_basic(...):

# ✅ 完整改进
from app.schemas.responses import StockListResponse, StockItem
from app.schemas.requests import StockListRequest

@router.get(
    "/stocks/basic",
    response_model=StockListResponse,
    summary="获取股票基本信息列表",
    description="获取股票基本信息，支持分页、搜索和行业筛选",
    responses={
        200: {"model": StockListResponse, "description": "成功获取股票列表"},
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未授权访问"},
        500: {"model": ErrorResponse, "description": "服务器内部错误"},
    }
)
async def get_stocks_basic(
    request: StockListRequest = Depends(),
    current_user: User = Depends(get_current_user)
) -> StockListResponse:
    """
    获取股票基本信息列表

    Args:
        request: 股票列表请求参数
        current_user: 当前认证用户

    Returns:
        StockListResponse: 包含股票列表和分页信息的响应

    Raises:
        HTTPException: 当参数验证失败或服务器错误时
    """
```

### 修复 6: 权限系统标准化

**当前问题**: 权限检查不一致，缺少装饰器

**解决方案**: 实现基于装饰器的权限系统

```python
# 创建文件: app/decorators/permissions.py

from functools import wraps
from enum import Enum
from typing import List
from fastapi import HTTPException, status

class Permission(Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

def require_permissions(required_permissions: List[Permission]):
    """权限验证装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="未认证"
                )

            user_permissions = get_user_permissions(current_user.id)

            for permission in required_permissions:
                if permission.value not in user_permissions:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
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
    pass
```

### 修复 7: 错误处理标准化

**当前问题**: 错误处理模式不统一

**解决方案**: 实现统一的错误处理装饰器

```python
# 创建文件: app/decorators/error_handling.py

from functools import wraps
import logging
from fastapi import HTTPException
from app.core.responses import create_error_response, ErrorCodes

logger = logging.getLogger(__name__)

def handle_api_errors(func):
    """API错误处理装饰器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except HTTPException:
            raise
        except ValueError as e:
            logger.error(f"参数验证错误: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    error_code=ErrorCodes.VALIDATION_ERROR,
                    message="参数验证失败",
                    details={"validation_error": str(e)}
                )
            )
        except Exception as e:
            logger.error(f"API错误: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
                    message="服务器内部错误"
                )
            )
    return wrapper

# 使用示例
@router.get("/stocks/basic")
@handle_api_errors
async def get_stocks_basic(
    request: StockListRequest = Depends(),
    current_user: User = Depends(get_current_user)
):
    # 业务逻辑，异常会被装饰器自动处理
    pass
```

## 低优先级修复 (4-8周内)

### 修复 8: 缓存策略标准化

**当前问题**: 缓存使用不一致，缺少统一策略

**解决方案**: 实现统一的缓存装饰器

```python
# 创建文件: app/decorators/caching.py

from functools import wraps
import hashlib
import json
from typing import Any, Optional
from app.core.cache import cache_manager

def cache_response(ttl: int = 300, key_prefix: str = ""):
    """缓存响应装饰器"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = _generate_cache_key(func.__name__, args, kwargs, key_prefix)

            # 尝试从缓存获取
            cached_result = await cache_manager.get(cache_key)
            if cached_result:
                return cached_result

            # 执行函数并缓存结果
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator

def _generate_cache_key(func_name: str, args: tuple, kwargs: dict, prefix: str) -> str:
    """生成缓存键"""
    key_data = {
        'func': func_name,
        'args': args,
        'kwargs': {k: v for k, v in kwargs.items() if k != 'current_user'}
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return f"{prefix}:{hashlib.md5(key_str.encode()).hexdigest()}"

# 使用示例
@router.get("/stocks/basic")
@cache_response(ttl=600, key_prefix="stocks")
async def get_stocks_basic(
    request: StockListRequest = Depends(),
    current_user: User = Depends(get_current_user)
):
    pass
```

### 修复 9: API 版本控制

**当前问题**: 缺少版本控制策略

**解决方案**: 实现API版本控制

```python
# 创建版本化路由
from fastapi import APIRouter

# v1 API
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])

@v1_router.get("/stocks/basic")
async def get_stocks_basic_v1():
    """v1版本的股票基础信息接口"""
    pass

# v2 API (未来扩展)
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v2_router.get("/stocks/basic")
async def get_stocks_basic_v2():
    """v2版本的股票基础信息接口（向后兼容）"""
    pass

# 在main.py中注册
app.include_router(v1_router)
app.include_router(v2_router)
```

### 修复 10: 性能监控集成

**当前问题**: 缺少API性能监控

**解决方案**: 添加性能监控装饰器

```python
# 创建文件: app/decorators/monitoring.py

from functools import wraps
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

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

            # 慢查询警告
            if execution_time > 2.0:
                logger.warning(f"慢查询检测: {func.__name__} 执行时间 {execution_time:.3f}s")

            return result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"API错误: {func.__name__} 执行时间 {execution_time:.3f}s, 错误: {str(e)}")
            raise

    return wrapper

# 使用示例
@router.get("/stocks/basic")
@monitor_performance
async def get_stocks_basic(
    request: StockListRequest = Depends(),
    current_user: User = Depends(get_current_user)
):
    pass
```

## 实施计划

### 第一阶段 (1-2周): 高优先级修复
- [ ] 统一所有API响应格式
- [ ] 添加缺失的认证保护
- [ ] 完善参数验证规则
- [ ] 重构RESTful路径设计

### 第二阶段 (2-4周): 中优先级修复
- [ ] 完善Swagger文档
- [ ] 实现权限系统标准化
- [ ] 统一错误处理模式

### 第三阶段 (4-8周): 低优先级修复
- [ ] 实现缓存策略标准化
- [ ] 添加API版本控制
- [ ] 集成性能监控

### 验收标准
1. **合规性达到 90%+**
2. **所有API都有完整的Swagger文档**
3. **统一的响应格式和错误处理**
4. **完整的认证和权限控制**
5. **RESTful设计原则遵循**

### 工具和脚本
创建自动化脚本来验证合规性:

```python
# scripts/api_compliance_check.py
"""API合规性检查脚本"""

def check_response_format(api_function):
    """检查响应格式是否符合标准"""
    pass

def check_authentication(api_function):
    """检查是否有适当的认证"""
    pass

def check_documentation(api_function):
    """检查文档完整性"""
    pass

def generate_compliance_report():
    """生成合规性报告"""
    pass
```

这些改进将显著提升MyStocks API的规范性、可维护性和用户体验。
