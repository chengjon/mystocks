# mystocks_spec3 任务文档

**Worker CLI**: mystocks_spec3
**Branch**: `dev-mystocks-spec3`
**Base Branch**: `main`
**PR Base**: `main`
**提交信息模板**: `type(scope): short description`
**Worktree**: `/opt/claude/mystocks_spec3`
**Upstream**: `origin/dev-mystocks-spec3`
**当前状态**: 待主 CLI 分配具体模块任务

---

## 🎯 核心职责

- 按主 CLI 分配范围进行开发
- 仅修改所有权范围内文件
- 提交前执行验证并记录证据

---

## 📋 初始任务清单

- [ ] 阅读 `.multi-cli-tasks/guides/WORKER_CLI_GUIDE.md`
- [ ] 与主 CLI 确认本轮任务范围
- [ ] 切换到开发分支：`git switch dev-mystocks-spec3`
- [ ] 更新 `TASK-REPORT.md` 并开始开发

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
