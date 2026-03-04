# V3 Placeholder Pages Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 消除前端优化清单中首批 4 个 `placeholder` 页面状态（#29/#30/#33/#34），将页面升级为可用的监控/公告/系统管理视图并更新清单状态。

**Architecture:** 遵循 V3“能力提取而非删除”策略：复用既有监控与公告能力（API + 组件范式），在 ArtDeco 路由页面中做轻量聚合视图。优先保证真实接口数据可见、可刷新、可追踪（REQ_ID）。

**Tech Stack:** Vue 3 + TypeScript + Element Plus + 现有 `useArtDecoApi`/`monitoringApi`。

### Task 1: 实现 Risk Alerts 页面（#29）

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue`
- Test: `web/frontend/tests/e2e/comprehensive-all-pages.spec.ts`

**Step 1: 写失败验证（页面结构）**
- 在 E2E 关键选择器中确保 `/risk/alerts` 页有至少一个核心可见元素（统计卡/表格）。

**Step 2: 运行失败验证（如失败才继续）**
- Run: `npm --prefix web/frontend run test -- tests/e2e/comprehensive-all-pages.spec.ts --list`

**Step 3: 实现最小可用功能**
- 用 `monitoringApi.getAlertRules/getAlerts` 拉取规则和告警。
- 增加统计卡、告警表、规则表、刷新按钮、REQ_ID 展示。
- 保留 ArtDeco 样式变量，移除纯占位文本。

**Step 4: 运行通过验证**
- Run: `npm --prefix web/frontend run type-check`

**Step 5: Commit**
- `git add web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue`

### Task 2: 实现 Risk News 页面（#30）

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue`

**Step 1: 写失败验证（页面结构）**
- 页面需呈现公告统计、公告列表、刷新操作。

**Step 2: 运行失败验证（如失败才继续）**
- Run: `npm --prefix web/frontend run test -- tests/e2e/comprehensive-all-pages.spec.ts --list`

**Step 3: 实现最小可用功能**
- 用 `monitoringApi.getAnnouncements` 拉取数据并归一化。
- 增加统计卡（总数/今日/重要），列表表格（标题、代码、类型、时间、操作）。
- 支持打开原文链接与 REQ_ID 展示。

**Step 4: 运行通过验证**
- Run: `npm --prefix web/frontend run type-check`

**Step 5: Commit**
- `git add web/frontend/src/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue`

### Task 3: 清单状态回写（#29/#30/#33/#34）

**Files:**
- Modify: `docs/plans/frontend-page-optimization-list.md`

**Step 1: 更新状态字段**
- 将 #29/#30 从 `placeholder` 更新为 `mixed`。
- 结合实际实现，将 #33/#34 从 `placeholder` 更新为 `mixed`。

**Step 2: 更新执行顺序与备注**
- 将“先消除 placeholder 页面”改为“placeholder 已完成，继续 mock-debt 治理”。
- 在审批备注追加本轮完成与验证结果。

**Step 3: 验证文档一致性**
- Run: `python scripts/dev/frontend_optimization_audit.py --repo-root . --strict --report-file reports/analysis/frontend-page-optimization-audit-report.md`

**Step 4: Commit**
- `git add docs/plans/frontend-page-optimization-list.md`

### Task 4: 回归与门禁验证

**Files:**
- Verify only

**Step 1: 类型检查**
- Run: `npm --prefix web/frontend run type-check`

**Step 2: 关键门禁**
- Run: `bash scripts/run_e2e_pm2.sh`

**Step 3: 报告运行真值**
- Run: `pm2 list`
- Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3020`
- Run: `curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8020/health`

