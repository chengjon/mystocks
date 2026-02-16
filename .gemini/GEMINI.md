# GEMINI.md - Agent Memory & Guidelines

## 🧠 核心开发准则 (Core Development Guidelines)

### 🚀 推荐开发流程：六步走战略

> **核心理念**：预防问题优于修复问题，每个阶段解决一类特定痛点。

#### 第一阶段：契约先行 (Contract First) —— 避免"接口分裂"

**痛点回顾**：前端调 `/api/data/stocks`，后端写 `/api/v1/market/quotes`，直到上线才发现对不上。

1. **定义 OpenAPI 规范**：不要先写代码，先用 Swagger Editor 或 JSON 定义好 API 的输入输出。
2. **自动生成代码**：
   - 后端：使用 `fastapi-code-generator` 生成 Pydantic Models 和 Router 存根。
   - 前端：使用 `openapi-typescript-codegen` 自动生成 TypeScript 类型定义（interface）和 API Client。
3. **收益**：前端不会拼错字段名，后端修改字段时前端编译可直接报错。

#### 第二阶段：单体骨架 (Monolithic Skeleton) —— 避免"循环依赖"

**痛点回顾**：Router 引用 Component，Component 引用 Service，Service 引用 Router（为了跳 401），导致 Vue 挂载失败。

1. **分层架构强约束**：
   - **Core**：工具类、配置、日志（无依赖）
   - **Domain**：纯 TypeScript/Python 实体定义（无业务逻辑）
   - **Infra**：数据库、API Client、Redis（只依赖 Core 和 Domain）
   - **Application**：业务服务（依赖 Infra）
   - **UI/API**：Vue 组件 / FastAPI 路由（最上层）
2. **禁止反向依赖**：配置 `dependency-cruiser`（JS）或 `import-linter`（Python），在 CI 阶段拦截任何反向引用。

#### 第三阶段：Mock 驱动开发 (Mock Driven) —— 避免"前端等后端"

**痛点回顾**：后端挂了，前端连页面都打不开；后端好了，前端因为没数据不知道显没显示。

1. **MSW（Mock Service Worker）**：在前端网络层拦截请求，返回符合 OpenAPI 契约的假数据。
2. **独立开发**：前端开发时不需要启动后端服务，`npm run dev` 即可查看完整页面状态。
3. **视觉验收**：在后端代码未完成前，前端 UI/UX 可以先行验收。

#### 第四阶段：后端垂直切片 (Vertical Slicing) —— 避免"甚至连不上库"

**痛点回顾**：一次性写了 50 个路由，结果连 `main.py` 都起不来。

1. **做一个 Feature，通一个 Feature**：例如先做“系统健康”，从 DB 表 → ORM → Repository → Service → API → 前端展示，一次只打通一个垂直流程。
2. **日志标准化**：在第一行业务代码前封装好 logger。所有模块统一 `from app.core.logger import logger`，严禁 `print` 或裸 `logging`。

#### 第五阶段：集成与可观测性 (Observability) —— 避免"隐形白屏"

**痛点回顾**：页面白了，控制台没报错，后端没日志，无法快速定位问题。

1. **RequestId 全链路追踪**：Nginx 生成 ID → FastAPI 中间件接收 → 注入 Logger → 传给前端 → 前端报错时携带 ID。
2. **健康检查探针**：
   - `/health/live`：服务是否存活
   - `/health/ready`：数据库/Redis 是否就绪
   - 前端 `App.vue` 启动时优先检查 `ready`，失败时显示“系统维护中”，避免白屏。

#### 第六阶段：自动化防护网 (Safety Net) —— 避免"回归测试"

**痛点回顾**：修好了 A，坏了 B。

1. **E2E 冒烟测试**：每次提交代码，CI 自动拉起前后端并执行核心流程校验。
2. **路径与环境隔离**：
   - 使用 `pnpm` 或 `poetry` 锁定依赖。
   - 使用 Docker 容器化开发环境，避免依赖开发者本机 `PYTHONPATH`。

---

### 🐳 开发环境管理：Docker 一等公民原则

> **核心原则**：`ecosystem.config.js` 及其配套的 Docker 环境是一等公民。

**禁止行为**：
- ❌ 让开发者在命令行中直接执行 `python main.py` 或 `npm run dev`
- ❌ 依赖开发者本机环境配置

**正确做法**：
- ✅ 使用 `docker-compose up` 一键拉起所有依赖
- ✅ 通过容器化解决路径错误、端口占用、依赖缺失等环境一致性问题

---

## 📝 历史任务记录

### 2026-02-15 菜单重构与风险管理升级
- **任务**: 将前端菜单重构为配置驱动，并将"智能监控"升级为"风险管理"。
- **状态**: ✅ 完成
- **合规性检查**:
    - **契约先行**: ✅ 前端重构未涉及后端 API 变更，符合当前阶段。
    - **单体骨架**: ✅ 遵循分层架构，组件与配置分离。
    - **Mock 驱动**: ✅ 测试中使用 Mock，未依赖后端。
    - **自动化防护网**: ✅ 编写并通过了单元测试 `SidebarMenu.spec.ts`。
- **后续建议**: 
    - 随着 V3.1 风险管理功能的深入开发，需严格执行"契约先行"，先定义 `/v31/*` API 的 OpenAPI 规范。
    - 确保新页面的开发遵循"Mock 驱动"原则，使用 MSW 拦截请求。
