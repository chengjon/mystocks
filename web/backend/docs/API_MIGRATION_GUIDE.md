# API 统一响应格式迁移指南 (增强版 - 中间件方案)

## 版本信息

| 项目 | 版本 |
|------|------|
| 文档版本 | 2.0.0 |
| 最后更新 | 2025-12-24 |
| 作者 | MyStocks Team |

---

## 概述

本文档描述了 MyStocks 后端 API 从自定义响应格式迁移到**统一响应格式**的完整方案。

### 核心策略：中间件自动包装

采用**非侵入式**的设计理念，通过 FastAPI 中间件自动包装所有响应，无需修改现有 API 代码。

**优势：**
- ✅ **零侵入** - 不需要修改现有 API 代码
- ✅ **向后兼容** - 自动转换旧格式响应
- ✅ **统一格式** - 所有响应自动包装为统一格式
- ✅ **错误处理** - 集中式错误处理器

---

## 统一响应格式 (增强版)

### 标准 API 响应结构

```json
{
  "success": true,           // 布尔值，表示请求是否成功处理
  "code": 200,               // 整数，业务状态码 (与HTTP状态码区分开)
  "message": "操作成功",     // 字符串，给前端展示的消息
  "data": {...},             // 任意类型，实际的业务数据
  "timestamp": "2025-12-24T10:30:00Z", // 字符串，响应生成的时间戳
  "request_id": "req-123",   // 字符串，可选，请求ID，用于追踪
  "errors": [                // 数组，可选，详细错误信息
    {
      "field": "username",   // 字符串，可选，错误发生的字段
      "code": "INVALID_FORMAT", // 字符串，具体的错误代码
      "message": "用户名格式不正确" // 字符串，具体的错误描述
    }
  ]
}
```

### 业务状态码映射

| 业务码 | HTTP 状态码 | 说明 |
|--------|------------|------|
| 200 | 200 | 成功 |
| 201 | 201 | 创建成功 |
| 400 | 400 | 请求参数错误 |
| 401 | 401 | 未认证 |
| 403 | 403 | 禁止访问 |
| 404 | 404 | 资源未找到 |
| 422 | 422 | 参数验证失败 |
| 429 | 429 | 请求过于频繁 |
| 500 | 500 | 服务器内部错误 |
| 502 | 502 | 外部服务错误 |
| 503 | 503 | 服务暂不可用 |

---

## 实施方案

### 阶段一：中间件自动包装 (推荐，零侵入)

这是**最推荐**的方案，通过中间件自动处理所有响应格式：

#### 1. 注册中间件

在 `app/app_factory.py` 或应用初始化代码中：

```python
from app.middleware.response_format import ResponseFormatMiddleware
from app.core.global_exception_handlers import register_global_exception_handlers

def create_app():
    app = FastAPI()

    # 注册全局异常处理器
    register_global_exception_handlers(app)

    # 注册响应格式中间件
    app.add_middleware(ResponseFormatMiddleware)

    return app
```

#### 2. 中间件自动处理的格式

**自动包装的格式：**

| 输入格式 | 输出格式 |
|---------|----------|
| `{"data": [...]}` | 统一格式，success=true, code=200 |
| `{"success": true, "data": {...}}` | 转换为统一格式，添加 code |
| `{"status": "ok", "result": [...]}` | 统一格式，自动提取数据 |
| Pydantic 模型 | 统一格式，自动序列化 |
| HTTPException | 统一错误格式，带 errors 数组 |

#### 3. 便捷函数

新的响应格式提供了便捷的快捷函数：

```python
from app.core.responses import ok, not_found, validation_error, bad_request, unauthorized, forbidden

# 成功响应 (code=200)
return ok(data={"items": [...]})

# 创建成功 (code=201)
return created(data={"id": 123})

# 资源未找到 (code=404)
return not_found(resource="用户")

# 参数验证失败 (code=422)
errors = [
    ErrorDetail(field="email", code="INVALID_FORMAT", message="邮箱格式错误"),
    ErrorDetail(field="age", code="OUT_OF_RANGE", message="年龄必须大于0"),
]
return validation_error(errors=errors)

# 请求错误 (code=400)
return bad_request(message="参数无效")

# 未授权 (code=401)
return unauthorized()

# 禁止访问 (code=403)
return forbidden()
```

---

### 阶段二：逐步迁移 (可选)

如果需要更精细的控制，可以逐步迁移 API 端点：

#### 迁移前的代码

```python
@router.get("/items")
async def get_items():
    items = fetch_items()
    return {"data": items, "status": "ok"}
```

#### 迁移后的代码

```python
from app.core.responses import ok, create_unified_success_response

@router.get("/items")
async def get_items():
    items = fetch_items()
    return ok(data={"items": items, "total": len(items)})
    # 或者使用完整函数
    # return create_unified_success_response(
    #     data={"items": items},
    #     message="获取列表成功",
    #     code=200
    # )
```

---

## 中间件配置

### 排除路径

某些路径可以排除自动包装：

```python
class ResponseFormatMiddleware(BaseHTTPMiddleware):
    # 不需要包装的路径前缀
    EXCLUDE_PATHS = {
        "/docs",      # Swagger UI
        "/redoc",     # ReDoc
        "/openapi.json",
        "/static",
        "/favicon",
    }

    # 完全跳过的路径
    SKIP_PATHS = {
        "/health",    # 健康检查端点
    }
```

### 自定义排除

使用装饰器排除特定端点：

```python
from app.middleware.response_format import exclude_response_wrapper

@router.get("/custom")
@exclude_response_wrapper()
async def custom_endpoint():
    return {"custom": "format", "unchanged": True}
```

---

## 错误处理

### 验证错误自动转换

Pydantic 验证错误会自动转换为 `errors` 数组：

**请求：**
```json
{
  "email": "invalid-email",
  "age": -5
}
```

**响应 (422)：**
```json
{
  "success": false,
  "code": 422,
  "message": "参数验证失败: email, age",
  "errors": [
    {
      "field": "email",
      "code": "INVALID_FORMAT",
      "message": "value is not a valid email address"
    },
    {
      "field": "age",
      "code": "OUT_OF_RANGE",
      "message": "ensure this value is greater than 0"
    }
  ],
  "request_id": "req-xxx"
}
```

### HTTPException 自动转换

```python
from fastapi import HTTPException

@router.get("/item/{id}")
async def get_item(id: int):
    if id < 1:
        raise HTTPException(
            status_code=404,
            detail="项目未找到"
        )
    return {"id": id, "name": "Item"}
```

**自动转换为：**
```json
{
  "success": false,
  "code": 404,
  "message": "项目未找到",
  "errors": [
    {
      "code": "NOT_FOUND",
      "message": "项目未找到"
    }
  ],
  "request_id": "req-xxx"
}
```

---

## 前端适配指南

### 统一响应处理

前端可以使用统一的响应处理逻辑：

```typescript
interface ApiResponse<T = any> {
  success: boolean;
  code: number;
  message: string;
  data?: T;
  timestamp: string;
  request_id?: string;
  errors?: ErrorDetail[];
}

interface ErrorDetail {
  field?: string;
  code: string;
  message: string;
}

// 统一 API 调用处理
async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  const apiResponse: ApiResponse<T> = await response.json();

  if (!apiResponse.success) {
    // 显示错误信息
    if (apiResponse.errors) {
      // 显示字段级别的错误
      apiResponse.errors.forEach(err => {
        console.error(`${err.field}: ${err.message}`);
      });
    } else {
      // 显示通用错误
      console.error(apiResponse.message);
    }
    throw new Error(apiResponse.message);
  }

  return apiResponse.data!;
}
```

---

## 迁移状态

### 已完成迁移 (32个模块)

| 模块 | 文件路径 | 状态 |
|------|----------|------|
| Auth | `app/api/auth.py` | ✅ |
| Watchlist | `app/api/watchlist.py` | ✅ |
| Indicators | `app/api/indicators.py` | ✅ |
| ... | ... | ... |

**注意：** 使用中间件方案后，所有现有 API 端点**自动返回统一格式**，无需修改代码。

---

## 检查清单

部署前确认：

- [ ] 中间件已注册到 FastAPI 应用
- [ ] 全局异常处理器已注册
- [ ] 测试验证错误响应格式正确
- [ ] 前端已适配新响应格式
- [ ] 文档已更新

---

## 相关文档

- 统一响应格式定义: `app/core/responses.py`
- 响应格式中间件: `app/middleware/response_format.py`
- 全局异常处理器: `app/core/global_exception_handlers.py`
- API 文档: http://localhost:8000/docs

---

## 示例对比

### 迁移前 (旧格式)

```python
@router.get("/user/{id}")
async def get_user(id: int):
    user = db.get_user(id)
    if not user:
        return {"error": "not_found", "message": "用户未找到"}, 404
    return {"status": "success", "data": user}
```

### 迁移后 (中间件自动处理)

```python
@router.get("/user/{id}")
async def get_user(id: int):
    user = db.get_user(id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user  # 中间件自动包装
```

**响应 (自动包装)：**
```json
{
  "success": false,
  "code": 404,
  "message": "用户未找到",
  "errors": [{"code": "NOT_FOUND", "message": "用户未找到"}],
  "request_id": "req-xxx"
}
```

---

## 变更历史

| 日期 | 版本 | 变更内容 |
|------|------|----------|
| 2025-12-24 | 2.0.0 | 增加中间件自动包装方案，添加 code 和 errors 字段 |
| 2025-12-24 | 1.0.0 | 初始版本，手动迁移方案 |
