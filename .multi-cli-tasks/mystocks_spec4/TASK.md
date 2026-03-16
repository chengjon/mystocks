# mystocks_spec4 任务文档

**Worker CLI**: mystocks_spec4
**Branch**: `mystocks_spec4`
**Base Branch**: `main`
**PR Base**: `main`
**提交信息模板**: `type(scope): short description`
**Worktree**: `/opt/claude/mystocks_spec4`
**Upstream**: `origin/dev-mystocks-spec4`
**当前状态**: 已激活，待同步最新 `main` 后执行

---

## 🎯 核心职责

- 按主 CLI 分配范围进行开发
- 仅修改所有权范围内文件
- 提交前执行验证并记录证据

---

## 📋 本轮任务

### 任务标题

`数据源配置双轨收敛与回归保护`

### 目标

- 核实 YAML/JSON 双配置入口的真实使用边界
- 先建立 source-of-truth 矩阵与回归保护，再推进收敛

### 启动前步骤

- `git fetch origin`
- `git rebase main`
- 确认当前 worktree 已对齐 `main@4ec63902` 之后再开始修改
- 阅读 `docs/guides/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
- 阅读 `docs/guides/GRAPHITI_MCP_WORKFLOW.md`
- 在 Mongo control plane 中先执行 `work claim`
- 如需历史 source-of-truth / review 事实，再使用 Graphiti 查询

### Checklist 对齐项

**参考清单**:
- `/opt/claude/GitNexus/docs/plans/2026-03-17-mystocks-spec-task-checklist.md`

**主对齐条目**:
- `3. Mongo ready_for_review control-plane unblock`
- `5. Code Simplification Phase A Baseline Inventory`

**补充要求**:
- 如果 `ready_for_review` 仍写不进去，必须留下精确 blocker：
  - 缺失凭证
  - 失败命令
  - 配置位置
- source-of-truth 矩阵之外，还要补一份只读 inventory，说明哪些配置入口仍是兼容层、哪些是 canonical entrypoint
- 不做静默行为变化，不在本轮直接删除尚未判定的入口

**建议命令**:
- `rg -n "coordctl|ready_for_review|createIndexes|Mongo" . docs scripts src`
- `sed -n '108,125p' docs/reports/plans/code-simplification-optimization-plan.md`
- `rg -n "compat|legacy|\\.old|\\.bak|\\.backup|apiClient|services/api-client" src web/frontend/src web/backend/app`

**Done when**:
- `ready_for_review` 成功写入，或 blocker note 足够精确可交接
- YAML/JSON / compatibility entrypoint 的 inventory 与 canonical destination 已写清

### 范围

- `config/data_sources_registry.yaml`
- `config/data_sources.json`
- `config/data_sources_loader.py`
- `src/core/data_source/base.py`
- `src/core/data_source/config_manager.py`
- `web/backend/app/core/data_source_manager.py`
- `web/backend/app/services/data_source_factory/data_source_factory.py`
- `web/backend/app/api/data_source_config.py`
- 相关测试：`tests/` 与 `web/backend/tests/`

### 禁止触碰

- `web/backend/config/data_sources.json`（除非先证明它是本任务必需输入，并记录原因）
- `web/backend/app/api/market/**`
- 与 `dev-api-availability-gemini` 当前分支直接冲突的文件

### 验收标准

- 产出 YAML/JSON source-of-truth 矩阵
- 为关键入口补充回归测试或断言
- 收敛 ambiguity，但不引入静默行为变化
- 若无法一次性统一，分阶段写清迁移方案与剩余风险
- 补充 Mongo 提审阻塞状态与 baseline inventory 证据

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
