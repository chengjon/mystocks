# 错误码与异常处理

> **版本**: 1.0 | **更新日期**: 2026-07-12
> **维护者**: 后端架构
> **合并来源**: `ERROR_CODES.md`（参考表）+ `ERROR_CODE_GUIDE.md`（error_codes.py 使用）+ `EXCEPTION_HANDLER_GUIDE.md`（异常处理器）
> **核心模块**: `app.core.error_codes`、`app.core.exception_handler`、`app.core.validation_messages`

---

## 概览

MyStocks 采用统一错误码体系：HTTP 状态码表达协议层语义，业务码（`code` 字段）表达具体错误类型，中文消息（`msg` 字段）面向终端用户。

```python
from app.core.error_codes import (
    ErrorCode,          # 枚举：所有业务错误码
    HTTPStatus,         # HTTP 状态码常量
    ErrorCategory,      # 分类：CLIENT_ERROR / SERVER_ERROR
    get_http_status,    # ErrorCode → int (400/401/500...)
    get_error_message,  # ErrorCode → str (中文消息)
    get_error_category, # ErrorCode → ErrorCategory
    is_success, is_client_error, is_server_error,
)
from app.core.exception_handler import register_exception_handlers
```

---

## 错误码参考表

### 全局概览

| HTTP | 业务码 | 说明 | 处理建议 |
|------|--------|------|----------|
| 200 | 0 | 成功 | 无需处理 |
| 400 | 400 | 请求参数错误 | 检查请求参数 |
| 401 | 401 | 未认证 | 登录后重试 |
| 403 | 403 | 权限不足 | 联系管理员 |
| 404 | 404 | 资源不存在 | 检查资源 ID |
| 422 | 422 | 数据验证错误 | 检查字段格式 |
| 429 | 429 | 请求过于频繁 | 稍后重试 |
| 500 | 500 | 服务器内部错误 | 联系技术支持 |
| 503 | 503 | 服务不可用 | 稍后重试 |

### 认证模块 (1xxx)

| 业务码 | HTTP | 说明 | 原因 | 解决方案 |
|--------|------|------|------|----------|
| 1001 | 401 | 用户名或密码错误 | 凭据无效 | 检查用户名密码 |
| 1002 | 401 | Token 已过期 | Token 过期 | 刷新 Token |
| 1003 | 401 | Token 无效 | Token 格式错误 | 重新登录 |
| 1004 | 401 | Refresh Token 无效 | Refresh Token 过期 | 重新登录 |
| 1005 | 403 | 用户已禁用 | 账户状态异常 | 联系管理员 |
| 1006 | 400 | 验证码错误 | 验证码不匹配 | 重新获取验证码 |
| 1007 | 400 | 用户名已存在 | 注册时用户名重复 | 使用其他用户名 |
| 1008 | 400 | 邮箱格式错误 | 邮箱格式不正确 | 检查邮箱格式 |
| 1009 | 400 | 密码强度不足 | 密码不符合要求 | 使用更强密码 |

### 市场数据模块 (2xxx)

| 业务码 | HTTP | 说明 | 原因 | 解决方案 |
|--------|------|------|------|----------|
| 2001 | 400 | 股票代码无效 | 代码格式错误 | 检查代码格式，如 `000001.SZ` |
| 2002 | 404 | 股票不存在 | 代码不在数据库 | 确认股票代码 |
| 2003 | 400 | 日期范围错误 | 开始日期晚于结束日期 | 调整日期范围 |
| 2004 | 400 | 日期格式错误 | 格式不为 YYYY-MM-DD | 使用正确格式 |
| 2005 | 400 | 周期参数无效 | interval 值不支持 | 使用: daily/weekly/monthly |
| 2006 | 429 | 请求过于频繁 | 超过 API 调用限制 | 降低请求频率 |
| 2007 | 503 | 数据源不可用 | 第三方服务异常 | 稍后重试 |
| 2008 | 500 | 数据处理错误 | 服务器内部错误 | 联系技术支持 |

### 策略模块 (3xxx)

| 业务码 | HTTP | 说明 | 原因 | 解决方案 |
|--------|------|------|------|----------|
| 3001 | 404 | 策略不存在 | ID 无效 | 确认策略 ID |
| 3002 | 400 | 参数验证失败 | 参数不符合要求 | 检查参数范围 |
| 3003 | 400 | 策略名称为空 | 缺少必填字段 | 提供策略名称 |
| 3004 | 403 | 无操作权限 | 不是策略所有者 | 确认所有权 |
| 3005 | 400 | 策略类型不存在 | type 值无效 | 使用支持的类型 |
| 3006 | 400 | JSON 格式错误 | parameters 非有效 JSON | 检查 JSON 格式 |

### 回测模块 (4xxx)

| 业务码 | HTTP | 说明 | 原因 | 解决方案 |
|--------|------|------|------|----------|
| 4001 | 404 | 回测不存在 | ID 无效 | 确认回测 ID |
| 4002 | 400 | 初始资金无效 | 资金 <= 0 | 设置正数资金 |
| 4003 | 400 | 日期范围无效 | 范围超过 5 年 | 缩短日期范围 |
| 4004 | 409 | 回测已在运行 | 同一策略不能重复运行 | 等待完成或取消 |
| 4005 | 500 | 回测执行失败 | 策略逻辑错误 | 检查策略参数 |
| 4006 | 403 | 无查看权限 | 不是回测所有者 | 确认所有权 |
| 4007 | 400 | 回测结果不存在 | 结果已删除 | 重新运行回测 |

### 交易模块 (5xxx)

| 业务码 | HTTP | 说明 | 原因 | 解决方案 |
|--------|------|------|------|----------|
| 5001 | 400 | 订单参数错误 | 参数不符合要求 | 检查参数 |
| 5002 | 400 | 股票代码无效 | 代码格式错误 | 使用正确格式 |
| 5003 | 400 | 订单类型无效 | type 值不支持 | 使用 market/limit/stop |
| 5004 | 400 | 价格无效 | 价格 <= 0 或非数字 | 检查价格 |
| 5005 | 400 | 数量无效 | 数量 <= 0 或非整数 | 检查数量 |
| 5006 | 403 | 余额不足 | 可用资金不足 | 充值或减少数量 |
| 5007 | 403 | 持仓不足 | 平仓数量超过持仓 | 减少平仓数量 |
| 5008 | 404 | 订单不存在 | order_id 无效 | 确认订单 ID |
| 5009 | 409 | 订单状态错误 | 订单已成交或已取消 | 不能重复操作 |
| 5010 | 429 | 下单过于频繁 | 超过交易频率限制 | 降低频率 |

### 系统错误码 (9xxx)

| 业务码 | HTTP | 说明 | 原因 | 解决方案 |
|--------|------|------|------|----------|
| 9001 | 500 | 数据库连接失败 | 数据库服务异常 | 检查数据库连接 |
| 9002 | 500 | Redis 连接失败 | 缓存服务异常 | 检查 Redis |
| 9003 | 503 | 服务维护中 | 系统维护中 | 等待维护完成 |
| 9004 | 500 | 内部错误 | 未预期的异常 | 联系技术支持 |
| 9005 | 429 | 限流触发 | 超过 API 限制 | 降低请求频率 |
| 9006 | 502 | 网关错误 | 上游服务异常 | 稍后重试 |

---

## 错误响应格式

### 成功响应

```json
{
  "code": 200,
  "data": { /* 业务数据 */ },
  "msg": "success"
}
```

### 错误响应

```json
{
  "code": 1001,
  "msg": "用户名或密码错误",
  "details": {
    "field": "password",
    "reason": "密码错误"
  },
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 验证错误响应

```json
{
  "code": 422,
  "msg": "Validation error",
  "details": [
    { "field": "username", "error": "field required" },
    { "field": "password", "error": "string too short" }
  ],
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

## error_codes.py 使用

### 在 API 端点中使用

```python
from fastapi import HTTPException, status
from app.core.error_codes import ErrorCode, get_http_status, get_error_message

@router.post("/trade/orders")
async def create_order(order: OrderRequest):
    if order.quantity % 100 != 0:
        error_code = ErrorCode.QUANTITY_INVALID
        raise HTTPException(
            status_code=get_http_status(error_code),
            detail={
                "code": error_code.value,
                "message": get_error_message(error_code)
            }
        )
```

### 判断错误类型

```python
if is_success(error_code):
    pass
elif is_client_error(error_code):
    # 客户端错误 — 需要用户修正输入
    pass
elif is_server_error(error_code):
    # 服务器错误 — 需要运维介入
    pass
```

### HTTP 状态码映射规则

| HTTP | 错误码示例 | 场景 |
|------|-----------|------|
| 400 | 1000 (BAD_REQUEST) | 请求参数错误 |
| 401 | 6000 (AUTHENTICATION_FAILED) | 身份验证失败 |
| 403 | 4402 (RISK_LEVEL_HIGH) | 风险等级过高 |
| 404 | 4000 (ORDER_NOT_FOUND) | 资源不存在 |
| 409 | 4200 (INSUFFICIENT_CASH) | 业务冲突(资金不足) |
| 422 | 1001 (VALIDATION_ERROR) | 参数验证失败 |
| 429 | 6005 (RATE_LIMIT_EXCEEDED) | 请求过于频繁 |
| 500 | 9000 (INTERNAL_SERVER_ERROR) | 服务器内部错误 |
| 503 | 9002 (SERVICE_UNAVAILABLE) | 服务暂不可用 |

---

## 全局异常处理器

### 自动注册

```python
# main.py
from app.core.exception_handler import register_exception_handlers

app = FastAPI(...)
register_exception_handlers(app)  # 自动注册所有异常处理器
```

注册后**无需手动处理异常**，系统自动捕获并转换为标准 `APIResponse`。

### 异常类型到错误码映射

```python
# ValueError → 业务错误码（根据消息自动推断）
raise ValueError("股票代码格式不正确")  # → ErrorCode.SYMBOL_INVALID (1100)
raise ValueError("可用资金不足")          # → ErrorCode.INSUFFICIENT_CASH (4200)

# HTTPException → 错误码映射
# HTTP 401 → 6000 (AUTHENTICATION_FAILED)
# HTTP 404 → 4000 (ORDER_NOT_FOUND)
```

### 环境差异

| 特性 | 开发环境 | 生产环境 |
|------|---------|---------|
| 堆栈跟踪 | ✅ 包含在响应中 | ❌ 不包含 |
| 请求信息 | ✅ 包含在响应中 | ❌ 不包含 |
| 详细错误消息 | ✅ 暴露原始错误 | ❌ 仅通用消息 |
| 数据库错误详情 | ✅ 包含完整错误 | ❌ 仅错误类型 |

### 日志记录

- 客户端错误 (4xx) → `WARNING` 级别
- 服务器错误 (5xx) → `ERROR` 级别（含堆栈追踪）

---

## 最佳实践

1. **使用验证器而非手动验证**：使用 `TradingValidator` / `StockSymbolValidator` 统一校验入口
2. **统一错误抛出方式**：业务层 `raise ValueError(msg)` 或 `raise HTTPException`，禁止返回 None + 错误字符串
3. **前端统一拦截**：根据 `code` 字段跳转登录（6000）、提示用户（4xxx）、告警运维（5xxx/9xxx）
4. **错误消息优先从 `validation_messages.py` 获取**：所有业务错误消息保持中文

---

## 调试技巧

1. 每个错误响应都包含 `request_id`，用于追踪问题
2. 根据 `request_id` 查找日志：
   ```bash
   grep "<request_id>" /var/log/mystocks/api.log
   ```
3. 开启调试模式：
   ```bash
   export MYSTOCKS_DEBUG=true
   export MYSTOCKS_LOG_LEVEL=debug
   ```
4. 联系技术支持时提供：Request ID + 完整 URL + 方法 + 请求体 + 期望结果

---

## 相关文档

- [API 契约源文件](contracts/)
- [架构红线](../architecture/STANDARDS.md)
- [API 集成指南](integration.md)
