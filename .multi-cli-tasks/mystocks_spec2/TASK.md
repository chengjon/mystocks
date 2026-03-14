# mystocks_spec2 任务文档

**Worker CLI**: mystocks_spec2
**Branch**: `mystocks_spec2`
**Base Branch**: `main`
**PR Base**: `main`
**提交信息模板**: `type(scope): short description`
**Worktree**: `/opt/claude/mystocks_spec2`
**Upstream**: `origin/dev-mystocks-spec2`
**当前状态**: 已激活，待同步最新 `main` 后执行

---

## 🎯 核心职责

- 按主 CLI 分配范围进行开发
- 仅修改所有权范围内文件
- 提交前执行验证并记录证据

---

## 📋 本轮任务

### 任务标题

`历史遗留文件与损坏文件治理`

### 目标

- 核实并清理 active repo 内仍残留的 `.backup` / `.broken` / `.old` / `.new` 文件
- 严格遵守功能树判定与代码路径判定，避免误删兼容层

### 启动前步骤

- `git fetch origin`
- `git rebase main`
- 确认当前 worktree 已对齐 `main@4ec63902` 之后再开始修改

### 范围

- `web/frontend/src/views/RiskMonitor.vue.broken`
- `web/frontend/src/views/BacktestAnalysis.vue.broken`
- `web/frontend/src/router/index.ts.broken`
- `web/frontend/src/router/index.ts.bak.20260214`
- `web/frontend/src/main.js.old`
- `web/frontend/src/App.vue.old`
- `web/backend/app/api/risk_management.py.backup.20260130`
- `web/backend/app/api/data.py.backup.20260130`
- `web/backend/app/api/technical_analysis.py.new`
- `src/database/database_service.py.backup.20260130`
- `src/advanced_analysis/decision_models_analyzer.py.backup.20260130`
- `src/monitoring/alert_manager.py.backup_complex_20251108`

### 禁止触碰

- `.claude/worktrees/**`
- `.config/**`
- `.omc/**`
- `src/adapters/legacy_adapter.py`
- 任何未能证明为“重复冗余 / 正式下线”的文件

### 验收标准

- 为每个目标文件写出状态判定：`有效` / `兼容保留` / `重复冗余` / `待判定`
- 只删除已证明可安全移除的文件
- 对保留文件写清保留原因
- 在 `TASK-REPORT.md` 记录清理对象、依据与未删原因

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
