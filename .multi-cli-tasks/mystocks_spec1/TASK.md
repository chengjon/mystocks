# mystocks_spec1 任务文档

**Worker CLI**: mystocks_spec1
**Branch**: `dev-mystocks-spec1`
**Base Branch**: `main`
**PR Base**: `main`
**提交信息模板**: `type(scope): short description`
**Worktree**: `/opt/claude/mystocks_spec1`
**Upstream**: `origin/dev-mystocks-spec1`
**当前状态**: 已规划，等待 `dev-api-availability-gemini` 提交后激活

---

## 🎯 核心职责

- 按主 CLI 分配范围进行开发
- 仅修改所有权范围内文件
- 提交前执行验证并记录证据

---

## 📋 本轮任务

### 任务标题

`API 路由注册与版本前缀治理`

### 目标

- 收敛 API 注册入口与版本前缀规则
- 修复报告中已核实的非 `/api` / 非版本化前缀问题
- 增加回归检查，避免新旧路由规则继续漂移

### 范围

- `web/backend/app/router_registry.py`
- `web/backend/app/api/register_routers.py`
- `web/backend/app/api/VERSION_MAPPING.py`
- `web/backend/app/api/technical/routes.py`
- `web/backend/app/api/monitoring_analysis.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/multi_source/routes.py`
- `web/backend/app/api/market_v2.py`
- `web/backend/tests/` 下新增 focused tests

### 禁止触碰

- `web/backend/app/api/market/**`
- `web/backend/app/api/signal_monitoring/**`
- `web/backend/app/api/strategy_management/get_monitoring_db.py`
- `web/backend/app/api/health.py`
- 当前 `dev-api-availability-gemini` 已在推进的页面/API 真值修正工作

### 验收标准

- 明确单一主注册入口，或把双注册职责差异写清并固化
- 处理本任务范围内非 `/api` / 非版本前缀路由
- 新增回归测试，证明 scoped 路由前缀符合预期
- 在 `TASK-REPORT.md` 写清：改动文件、验证命令、风险与回滚方式

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
