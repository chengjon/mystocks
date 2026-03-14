# mystocks_spec4 任务文档

**Worker CLI**: mystocks_spec4
**Branch**: `dev-mystocks-spec4`
**Base Branch**: `main`
**PR Base**: `main`
**提交信息模板**: `type(scope): short description`
**Worktree**: `/opt/claude/mystocks_spec4`
**Upstream**: `origin/dev-mystocks-spec4`
**当前状态**: 已规划，等待 `dev-api-availability-gemini` 提交后激活

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
