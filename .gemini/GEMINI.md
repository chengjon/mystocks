# GEMINI.md - Agent Memory & Guidelines

## 🧠 核心开发准则 (Core Development Guidelines)

> **⚠️ 顶层约束 (Master Guideline)**:
> 遵循 [architecture/STANDARDS.md](../architecture/STANDARDS.md) 定义的工程红线。任何违反准则的代码均为不可接受交付。

### 统一共享规则（引用 STANDARDS）

以下规则统一以 [architecture/STANDARDS.md](../architecture/STANDARDS.md) 为准，避免多文档重复：

- `方案先行准则 (Proposal-First Rule)`：见“零、统一治理与审批门禁”
- `推荐开发流程：六步走战略`：见“一、推荐开发流程：六步走战略”
- `Docker 一等公民原则`：见“二、技术工程红线 -> 3. 环境一致性”

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
