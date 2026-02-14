# API CLI 任务清单

**角色**: 后端开发工程师
**职责**: FastAPI后端开发、认证授权、API设计

## 🔴 高优先级任务 (立即开始)

### 1. 实现JWT认证系统
- **任务ID**: task-3.1
- **预计工时**: 16小时
- **技术栈**: FastAPI, JWT, Pydantic, security
- **描述**:
  - 实现用户注册API (POST /api/auth/register)
  - 实现用户登录API (POST /api/auth/login)
  - 实现JWT token生成和验证
  - 实现token刷新机制 (POST /api/auth/refresh)
  - 实现密码重置功能 (POST /api/auth/reset-password)
  - 使用Pydantic进行请求验证
  - 确保API安全性（密码加密、token过期）

### 2. 开发股票数据API端点
- **任务ID**: task-3.2
- **预计工时**: 20小时
- **技术栈**: FastAPI, PostgreSQL, TDengine, API-design
- **描述**:
  - 实现股票行情查询API (GET /api/market/quote)
  - 实现K线数据查询API (GET /api/market/kline)
  - 实现技术指标查询API (GET /api/market/indicators)
  - 支持分页参数 (page, page_size)
  - 支持过滤参数 (symbol, start_date, end_date)
  - 支持排序参数 (sort_by, order)
  - 集成TDengine（高频数据）和PostgreSQL（日线数据）
  - 编写API文档（OpenAPI/Swagger）

## 🟡 中优先级任务

### 3. 实现用户权限管理
- **任务ID**: task-3.3
- **预计工时**: 12小时
- **技术栈**: FastAPI, RBAC, middleware
- **描述**:
  - 定义用户角色（admin, user, guest）
  - 实现基于角色的访问控制(RBAC)
  - 创建权限验证中间件
  - 实现API访问权限管理
  - 编写权限检查装饰器

## 📋 任务依赖关系

```
task-3.1 (JWT认证) ← 必须首先完成
    ↓
task-3.2 (API端点) ← 依赖认证系统
    ↓
task-3.3 (权限管理) ← 完善认证系统
```

## 📝 工作流程

1. ✅ **Phase 1**: 完成JWT认证系统 (task-3.1)
   - 创建用户模型和数据库表
   - 实现认证端点
   - 编写单元测试

2. ✅ **Phase 2**: 开发数据API端点 (task-3.2)
   - 设计API接口规范
   - 实现端点逻辑
   - 集成数据库查询
   - 性能优化

3. ✅ **Phase 3**: 实现权限管理 (task-3.3)
   - 设计权限模型
   - 实现中间件
   - 应用权限控制

## 🔗 相关文档

- FastAPI文档: `docs/api/FASTAPI_GUIDE.md`
- 认证规范: `docs/security/AUTHENTICATION_SPEC.md`
- API设计指南: `docs/api/API_DESIGN_GUIDE.md`

## 💬 协作要求

- 与**DB CLI**协作: 确认数据库表结构
- 与**WEB CLI**协作: 确认API接口规范
- 向**main**汇报: 每日更新进度，遇到阻塞及时报告

---

**最后更新**: 2026-01-01 20:55
**分配者**: Main CLI
