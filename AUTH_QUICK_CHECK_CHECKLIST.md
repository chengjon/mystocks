# 登录 API 改进 - 快速检查清单

**用途**: 部署前的最后检查
**所需时间**: 5-10 分钟
**执行人**: 开发工程师 + 代码审查员

---

## Pre-Review 检查清单（5 分钟）

### 代码结构检查

```
[ ] 1. 全局计数器已移除
    位置：web/backend/app/api/auth.py
    检查：不应该有 _mfa_query_failure_count = 0

[ ] 2. MFAFailureRecord 模型已创建
    位置：web/backend/app/models/monitoring.py
    检查：
      [ ] 有 id 字段
      [ ] 有 timestamp 字段
      [ ] 有 error_type 字段
      [ ] 有 request_id 字段
      [ ] 有 alert_sent 字段

[ ] 3. 监控函数已实现
    位置：web/backend/app/monitoring/mfa_monitor.py
    检查：
      [ ] record_mfa_failure() 函数存在
      [ ] get_mfa_failure_stats() 函数存在
      [ ] 使用了时间窗口（timedelta）

[ ] 4. 异常处理已分离
    位置：web/backend/app/api/auth.py, login_for_access_token()
    检查：
      [ ] 有 3 个独立的 try-except 块
      [ ] 步骤 1: 用户验证 (authenticate_user)
      [ ] 步骤 2: MFA 检查 (db.execute, MFA lookup)
      [ ] 步骤 3: 返回响应

[ ] 5. 配置已更新
    位置：web/backend/app/core/config.py
    检查：
      [ ] mfa_failure_check_threshold (默认 3)
      [ ] mfa_failure_check_window_minutes (默认 5)
```

---

## 日志安全检查（3 分钟）

### 日志字段审计

检查所有 logger 调用，确保：

```
[ ] 不使用 username 字段
    ✓ 应该用 request_id 代替
    ✗ 错误: logger.warning(..., username=username)

[ ] 不使用 str(e) 或 str(exception)
    ✓ 应该用 error_type=type(e).__name__
    ✗ 错误: logger.error(..., error=str(e))

[ ] 不记录原始 traceback
    ✓ 应该用 exc_info=False
    ✗ 错误: logger.error(..., exc_info=True)

[ ] 所有日志中使用的字段都不包含敏感信息
    检查清单：
    [ ] 没有密码哈希
    [ ] 没有 API key
    [ ] 没有数据库连接字符串
    [ ] 没有完整的用户邮箱（除非是日志脱敏后）
```

---

## 异常类型检查（2 分钟）

### MFAErrorType 枚举验证

```
[ ] 所有可能的异常都被映射到对应的 error_type

检查：
[ ] DatabaseError
    └─ SQLAlchemyError 异常时触发
    └─ logger.warning() 记录
    └─ await record_mfa_failure() 调用

[ ] TimeoutError
    └─ 数据库查询超时时触发
    └─ logger.warning() 记录
    └─ await record_mfa_failure() 调用

[ ] UnexpectedError
    └─ 其他异常时触发
    └─ logger.error() 记录
    └─ await record_mfa_failure() 调用

[ ] 异常处理的顺序正确
    ✓ 先 SQLAlchemyError （更具体）
    ✓ 再 Exception （通用）
    ✗ 错误顺序会导致 SQLAlchemy 异常被通用 handler 捕获
```

---

## Performance 检查（2 分钟）

### 性能基准验证

```
[ ] 单个登录请求延迟
    目标: < 100ms (不含网络往返)
    测试命令:
    ```bash
    time curl -X POST http://localhost:8000/api/auth/login \
      -d "username=user&password=user123"
    ```
    预期：Real < 0.1s

[ ] 100 并发登录请求
    目标: 无死锁，全部成功
    测试命令:
    ```bash
    ab -c 100 -n 100 \
      -p payload.txt \
      -T application/x-www-form-urlencoded \
      http://localhost:8000/api/auth/login
    ```
    预期：所有请求成功

[ ] 内存泄漏检查
    目标: 无内存泄漏
    检查：全局变量已移除，不应有增长
    工具: memory_profiler
    ```bash
    python -m memory_profiler test_auth_memory.py
    ```

[ ] 数据库查询性能
    目标: MFA 查询 < 50ms (normal) 或 < 10s (timeout)
    查看数据库慢查询日志
```

---

## 数据库检查（2 分钟）

### 表结构验证

```
[ ] mfa_failure_records 表已创建
    检查命令：
    ```sql
    \dt mfa_failure_records  -- PostgreSQL
    ```

[ ] 表结构正确
    检查：
    [ ] id SERIAL PRIMARY KEY
    [ ] timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    [ ] error_type VARCHAR NOT NULL
    [ ] request_id VARCHAR
    [ ] alert_sent INTEGER DEFAULT 0

[ ] 索引已创建
    检查：
    [ ] INDEX on timestamp
    [ ] INDEX on error_type

[ ] 初始数据为空
    检查命令：
    ```sql
    SELECT COUNT(*) FROM mfa_failure_records;
    ```
    预期：0 行

[ ] 可以成功插入和查询
    测试：
    ```sql
    INSERT INTO mfa_failure_records (error_type, request_id, alert_sent)
    VALUES ('database_error', 'test-123', 0);

    SELECT * FROM mfa_failure_records
    WHERE request_id = 'test-123';
    ```
```

---

## 功能测试检查（5 分钟）

### 核心功能验证

```
[ ] 无 MFA 用户的登录流程
    操作：
    1. POST /api/auth/login with username="user", password="user123"
    2. 检查响应

    预期：
    {
      "access_token": "eyJ...",
      "token_type": "bearer",
      "mfa_required": false,
      "user": {...}
    }

    [ ] 响应状态码: 200
    [ ] mfa_required: false
    [ ] access_token 有效

[ ] 错误密码的登录
    操作：
    1. POST /api/auth/login with username="user", password="wrong"

    预期：
    [ ] 状态码: 401
    [ ] detail: "用户名或密码错误"

[ ] 数据库故障时的优雅降级
    操作：
    1. 停止数据库（或 mock 数据库异常）
    2. POST /api/auth/login with username="user", password="user123"

    预期：
    [ ] 返回 200（不返回 500）
    [ ] mfa_required: false（跳过 MFA 检查）
    [ ] 日志中有 "mfa_check_database_error" 记录
    [ ] mfa_failure_records 表中有新记录

[ ] 监控端点访问权限
    操作：
    1. 无 token 访问 GET /api/auth/monitor/mfa-health

    预期：
    [ ] 状态码: 403 （未授权）

    操作：
    2. 使用 user token 访问

    预期：
    [ ] 状态码: 403 （权限不足，仅管理员）

    操作：
    3. 使用 admin token 访问

    预期：
    [ ] 状态码: 200
    [ ] 返回 JSON，包含 status, last_hour, last_24h 字段
```

---

## 日志审计检查（3 分钟）

### 日志输出验证

运行以下命令并检查日志输出：

```bash
# 1. 正常登录的日志
tail -f logs/app.log &
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=user&password=user123"

检查日志：
[ ] 没有 username 字段
[ ] 有 request_id 字段
[ ] 有 "login_success" 或 "login_requires_mfa"
[ ] 没有密码哈希

# 2. 错误登录的日志
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=user&password=wrong"

检查日志：
[ ] 没有 username 字段
[ ] 有 "authentication_failed"
[ ] 状态码: 401

# 3. MFA 查询失败的日志
# (需要 mock 数据库故障或停止数据库)

检查日志：
[ ] "mfa_check_database_error" 事件
[ ] 没有完整的异常栈
[ ] 有 error_type 字段（例如 "SQLAlchemyError"）
[ ] 有 request_id 字段
```

---

## 安全审计检查（3 分钟）

### 信息泄露检查

```
[ ] 搜索 "username" 在 logger 调用中
    命令：grep -n "logger\.*username" web/backend/app/api/auth.py
    结果：应该为空

[ ] 搜索 "str(e)" 在 logger 调用中
    命令：grep -n "logger\.*str(e)" web/backend/app/api/auth.py
    结果：应该为空

[ ] 搜索"密码"相关的日志
    命令：grep -n "password" web/backend/app/api/auth.py
    结果：应该为空

[ ] 检查是否有硬编码的敏感信息
    命令：grep -rn "password\|api_key\|secret" web/backend/app/api/auth.py
    结果：应该只在配置文件中，不在代码中
```

---

## 导入检查（2 分钟）

### Import 语句验证

```
web/backend/app/api/auth.py 应该有：

[ ] from sqlalchemy.exc import SQLAlchemyError
[ ] from app.models.monitoring import MFAErrorType
[ ] from app.monitoring.mfa_monitor import record_mfa_failure
[ ] from app.core.config import settings

不应该有：
[ ] import logging (改用 structlog)
[ ] from app.api.auth import _mfa_query_failure_count (全局变量)
```

---

## 测试执行检查（5 分钟）

### Unit Tests

```bash
# 1. 运行登录测试
pytest tests/test_auth_refactor.py::TestLoginWithoutMFA -v

检查：
[ ] test_login_success: PASSED
[ ] test_login_invalid_credentials: PASSED
[ ] test_login_nonexistent_user: PASSED

# 2. 运行 MFA 故障处理测试
pytest tests/test_auth_refactor.py::TestMFAFailureHandling -v

检查：
[ ] test_mfa_failure_recorded: PASSED
[ ] test_alert_triggered_on_threshold: PASSED

# 3. 运行监控端点测试
pytest tests/test_auth_refactor.py::TestMFAHealthEndpoint -v

检查：
[ ] test_get_mfa_health_requires_auth: PASSED
[ ] test_get_mfa_health_admin_only: PASSED

# 4. 运行所有认证测试
pytest tests/test_auth_refactor.py -v

检查：
[ ] 所有测试通过
[ ] 代码覆盖率 > 80%
```

---

## 代码审查检查（5 分钟）

### 代码风格和质量

```
[ ] 遵循 PEP 8 规范
    命令：flake8 web/backend/app/api/auth.py
    结果：无错误或仅有可接受的警告

[ ] 类型提示完整
    命令：mypy web/backend/app/api/auth.py
    结果：无类型错误

[ ] 没有未使用的导入
    检查：移除了所有与全局计数器相关的导入

[ ] 函数文档完整
    检查：
    [ ] record_mfa_failure() 有 docstring
    [ ] get_mfa_failure_stats() 有 docstring
    [ ] login_for_access_token() 的 docstring 已更新

[ ] 代码注释清晰
    检查：
    [ ] 步骤 1, 2, 3 的分离清晰标记
    [ ] 异常处理的意图明确
    [ ] 没有过度注释（1 行代码不需要 1 行注释）

[ ] 变量命名清晰
    检查：
    [ ] 没有单字母变量（除了循环）
    [ ] 没有 temp, x, y 等无意义的变量
    [ ] 枚举值清晰：MFAErrorType.DATABASE_ERROR 而非 ERROR_1
```

---

## 部署前最后检查（2 分钟）

```
[ ] 代码已提交到 Git
    命令：git status
    结果：working tree clean

[ ] 提交消息清晰
    检查：提交消息包含以下信息
    [ ] 修复了哪个问题
    [ ] 使用了什么方案
    [ ] 需要的数据库迁移

[ ] 没有调试代码
    搜索：print(), console.log(), debugger
    结果：全部移除

[ ] 没有临时注释
    搜索：TODO, FIXME, HACK, XXX
    结果：如果有，确认是有意的还是遗留

[ ] 生产环境配置已验证
    检查：
    [ ] 数据库连接字符串正确
    [ ] 环境变量已设置
    [ ] 日志级别合适（INFO，不是 DEBUG）
    [ ] 性能参数合理（连接池大小、超时时间等）

[ ] 回滚方案已准备
    文档：
    [ ] 如何回滚代码
    [ ] 如何回滚数据库迁移
    [ ] 应急故障处理流程
```

---

## 绿灯清单

**只有当以下所有项都打勾时，才能部署：**

```
✓ 代码结构完整
✓ 日志安全
✓ 异常处理分离
✓ 配置已更新
✓ 性能基准通过
✓ 数据库表正确
✓ 功能测试通过
✓ 单元测试通过
✓ 日志审计通过
✓ 安全审计通过
✓ 导入检查通过
✓ 代码风格检查通过
✓ 部署前检查完成
```

**所有项都打勾 = 可以部署 ✅**

---

## 故障应急指南

如果部署后出现问题，按以下步骤处理：

### 问题 1: 登录失败

```
症状：所有登录请求返回 500

诊断：
1. 检查 mfa_failure_records 表是否存在
   SELECT COUNT(*) FROM mfa_failure_records;

2. 检查应用日志
   tail -f /var/log/app.log | grep "login"

3. 检查数据库连接
   psql -U postgres -d mystocks -c "SELECT 1"

解决：
- 如果表不存在：运行 alembic upgrade head
- 如果连接失败：检查数据库凭证和网络
- 如果应用崩溃：查看完整的 traceback
```

### 问题 2: 告警频繁触发

```
症状：持续收到 "mfa_persistent_failure_alert"

诊断：
1. 查看最近的失败记录
   SELECT * FROM mfa_failure_records
   WHERE timestamp > NOW() - INTERVAL '1 hour'
   ORDER BY timestamp DESC;

2. 检查 MFA 表是否健康
   SELECT COUNT(*) FROM mfa_secrets;

3. 检查数据库性能
   EXPLAIN ANALYZE SELECT * FROM mfa_secrets LIMIT 1;

解决：
- 如果 MFA 表损坏：修复或重建
- 如果查询慢：添加索引
- 如果数据库过载：优化查询或增加资源
```

### 问题 3: 日志泄露

```
症状：发现日志中包含用户名

诊断：
grep "username" /var/log/app.log

解决：
1. 立即中止：停止应用
2. 查找原因：grep -n "username=" web/backend/app/api/auth.py
3. 修复：移除包含 username 的日志字段
4. 重新部署：等等 5 分钟，部署补丁
5. 审计：查看有多少日志被泄露，是否需要通知用户
```

---

**检查清单完成！** 🎉

如果所有项都通过，你就可以自信地部署这个改进到生产环境了。

