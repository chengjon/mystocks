# mystocks_spec3 任务文档

> **使用说明**:
> 本文件用于说明多 CLI 协作流程中的当前入口、任务工件或执行方式，服务于协作推进过程中的上下文同步。
> 其中的步骤、状态和局部约束不能脱离 `architecture/STANDARDS.md`、当前协作口径与实际执行结果单独解读为最终事实。


**Worker CLI**: mystocks_spec3
**Branch**: `mystocks_spec3`
**Base Branch**: `main`
**PR Base**: `main`
**提交信息模板**: `type(scope): short description`
**Worktree**: `/opt/claude/mystocks_spec3`
**Upstream**: `origin/dev-mystocks-spec3`
**当前状态**: 已激活，待同步最新 `main` 后执行

---

## 🎯 核心职责

- 按主 CLI 分配范围进行开发
- 仅修改所有权范围内文件
- 提交前执行验证并记录证据

---

## 📋 本轮任务

### 任务标题

`前端大组件/API硬编码/WebSocket收敛`

### 目标

- 处理报告中已核实的 active 前端大组件与硬编码接口问题
- 以小步方式拆分超大页面，并把 scoped 逻辑收敛到 service / config / websocket 工具层

### 启动前步骤

- `git fetch origin`
- `git rebase main`
- 确认当前 worktree 已对齐 `main@4ec63902` 之后再开始修改
- 阅读 `docs/guides/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
- 阅读 `docs/guides/GRAPHITI_MCP_WORKFLOW.md`
- 在 Mongo control plane 中先执行 `work claim`
- 如需历史页面判定或 handoff 事实，再使用 Graphiti 查询

### Checklist 对齐项

**参考清单**:
- `/opt/claude/GitNexus/docs/plans/2026-03-17-mystocks-spec-task-checklist.md`

**主对齐条目**:
- `1. API Pending Truth-Source Verification`
- `2. PM2 Smoke Validation`

**补充要求**:
- 对 scoped 页面补充“已可切换真实 API / backend-blocked / 待评审”三分法
- PM2 smoke 目标不是全仓库救火，而是识别本轮改动后的第一个硬失败点
- 若 PM2 失败与本任务改动无关，也必须把失败点与日志证据写进 `TASK-REPORT.md`

**建议命令**:
- `rg -n "API pending|blocker" web/frontend/src/views`
- `rg -n "mixed -> real|真值复核|API pending" TASK-REPORT.md docs`
- `bash scripts/run_e2e_pm2.sh`

**Done when**:
- scoped 页面状态拆分已写清
- PM2 smoke 的 frontend/backend/script 首个硬失败点已被记录
- 若本轮改动没有引入新失败，已有证据说明这一点

### 范围

- `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue`
- `web/frontend/src/views/artdeco-pages/ArtDecoMarketData.vue`
- `web/frontend/src/views/artdeco-pages/composables/useArtDecoDashboard.ts`
- `web/frontend/src/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue`
- `web/frontend/src/components/realtime/RealtimePositionPanel.vue`
- `web/frontend/src/config/pageConfig.ts`
- `web/frontend/src/composables/useWebSocketWithConfig.ts`
- 相关 `web/frontend/tests/unit/**`

### 禁止触碰

- `web/frontend/src/views/converted.archive/**`
- 不在本任务范围内的 demo / example 页面
- 与 `dev-api-availability-gemini` 正在调整的 API 真值判断逻辑

### 验收标准

- 至少拆分 1 个 active 超大页面为更小的 helper / view-model / subcomponent
- scoped active 页面中的硬编码 API 调用明显减少
- scoped websocket 使用统一到现有 shared composable / utility
- 补充对应单元测试，并在 `TASK-REPORT.md` 报告验证结果
- 补充 scoped 页面真值状态与 PM2 smoke 结果

---

## 📦 PR 必填信息（提交前准备）

- [ ] 变更范围（模块/文件/API/数据结构）
- [ ] 验证命令与结果（TS/Python/tests 对应命令与结论）
- [ ] 风险与回滚说明（触发条件 + 回滚步骤/命令）

---

## ✅ 治理门禁

- PR 目标必须是 `main`
- 提交信息必须符合 `type(scope): short description`
- PR 必须包含：变更范围、验证命令与结果、风险/回滚说明
- 合并前必须通过：质量门（TS/Python/tests）、安全门（secrets/audit/SAST）、审查门（code review）
- `main` 仅接收“干净、可复现、可回滚”的版本
