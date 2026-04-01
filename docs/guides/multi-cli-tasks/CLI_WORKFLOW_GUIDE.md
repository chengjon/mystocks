# Worker CLI 工作流程指南（标准化版）

**文档版本**: v3.0
**更新日期**: 2026-03-04
**变更说明**: 整合《AI-CLI协作开发规范》，新增分支策略、PR管理规则、提交信息规范、违规处理；完成项目无关化。
**适用于**: 所有 Worker CLI（CLI-X、Worker CLI-1 等）

---

## 使用说明

- 本文档是 Worker CLI 的执行手册。
- 原则：按任务边界执行、按规范提交、按证据交付。
- 项目落地时替换：`[项目名]`、`[worktree路径]`、`[模块名]`。

---

## 目录

1. [工作流程总览](#工作流程总览)
2. [分支策略（所有 CLI 必须遵循）](#分支策略所有-cli-必须遵循)
3. [PR 管理规则](#pr-管理规则)
4. [提交信息规范（AI 生成必须遵循）](#提交信息规范ai-生成必须遵循)
5. [阶段1：任务启动](#阶段1任务启动)
6. [阶段2：开发实现](#阶段2开发实现)
7. [阶段3：自测验证](#阶段3自测验证)
8. [阶段4：Git提交](#阶段4git提交)
9. [阶段5：更新TASK-REPORT](#阶段5更新task-report)
10. [阶段6：完成确认](#阶段6完成确认)
11. [常见问题处理](#常见问题处理)
12. [违规处理](#违规处理)
13. [快速参考](#快速参考)
14. [相关文档](#相关文档)

---

## 工作流程总览

```text
1) 任务启动 -> 2) 开发实现 -> 3) 自测验证 -> 4) Git提交 -> 5) 更新TASK-REPORT -> 6) 完成确认
```

关键要求：
- 不在共享 README 记录个人任务进度
- 统一使用 `TASK.md + TASK-REPORT.md`

---

## 分支策略（所有 CLI 必须遵循）

### 1. 分支基础规则
- 基准分支：`dev`
- 生产分支：`main`（禁止直提）
- Worker 分支：`feat/[模块名]-[cli标识]` 或 `fix/[模块名]-[cli标识]`

### 2. 工作区创建（Git Worktree）
```bash
# 主CLI初始化（仅首次执行）
git worktree add ./ai-workspace -b dev origin/dev

# 子CLI创建专属工作区
git worktree add ./worker-module -b feat/module-cli-x dev
```

### 3. 开工前检查
```bash
git branch --show-current
git status
git pull --rebase origin dev
```

---

## PR 管理规则

### 1. PR 创建（Worker CLI 执行）
- 目标分支必须是 `dev`
- 使用统一模板：

```bash
gh pr create --base dev --head [分支名] \
  --title "[type(scope)]: 描述" \
  --body "AI CLI: [CLI名称] | 生成模块: [模块名]"
```

### 2. PR 审核与合并（主 CLI 执行）
- 主 CLI 审核通过后合并
- Worker CLI 不执行 `dev -> main` 合并

---

## 提交信息规范（AI 生成必须遵循）

### 1. 格式要求
- `type(scope): short description`（英文）
- 描述必须具体，不得使用空泛语句

### 2. 类型（type）枚举
| 类型 | 适用场景 | 示例 |
|------|---------|------|
| `feat` | 新功能开发 | `feat(payment): add amount calc` |
| `fix` | 修复 bug | `fix(login): resolve token expire` |
| `docs` | 文档更新 | `docs(readme): update workflow` |
| `refactor` | 代码重构 | `refactor(user): optimize model` |
| `chore` | 构建/配置变更 | `chore(ci): add test step` |

### 3. 范围（scope）枚举
- scope 必须等于主 CLI 分配模块（如 `payment`、`api`、`user`）

---

## 阶段1：任务启动

收到主 CLI 指令：

```text
请按你当前 worktree 的 TASK.md 开工。
```

默认按以下顺序执行：

1. 阅读 `TASK.md`（目标、范围、验收标准）
2. 阅读：
   - `docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
   - `docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md`
3. 在 Mongo control plane 中记录开工：
   - `work mark --status in_progress`
4. 创建或更新 `TASK-REPORT.md`
5. 识别依赖与风险，并记录到报告

补充规则：

- 需要任务状态、owner、plan 进度时，查 Mongo
- 需要历史 handoff、架构事实、审核结论时，查 Graphiti

---

## 阶段2：开发实现

执行原则：
- 仅修改分配范围文件
- 小步提交，避免大批量不可回滚改动
- 涉及跨模块文件，先申请主 CLI 协调

---

## 阶段3：自测验证

提交前至少完成：
- 功能验证（对照验收标准）
- 质量验证（lint/type/test）
- 结果写入 `TASK-REPORT.md`

常见验证命令（示例）：
```bash
# TypeScript
pnpm tsc --noEmit

# Python
pytest -q
```

---

## 阶段4：Git提交

建议流程：
```bash
git status
git add [受影响文件]
git commit -m "feat(module): implement xxx"
git push -u origin [分支名]
```

要求：
- 提交信息必须符合规范
- 每次提交聚焦单一逻辑改动

---

## 阶段5：更新TASK-REPORT

每次关键进展后更新：
- 已完成项
- 进行中项
- 阻塞项
- 验证结果与证据

建议节点：25% / 50% / 75% / 100%。

如果该批次存在后续复用价值，还应补一条 Graphiti 记忆摘要，但这不能替代 Mongo 状态流转。

---

## 阶段6：完成确认

交付前检查：
- 所有验收标准打勾
- 所有验证命令通过
- 代码已推送到远程分支
- PR 已创建（base=dev）
- `TASK-*-REPORT.md` 已生成（如阶段性任务）
- Mongo control plane 已执行 `update add --status ready_for_review` 与 `work transition --to ready_for_review`

---

## 常见问题处理

### Q1: 被阻塞怎么办？
先在 `TASK-REPORT.md` 记录阻塞原因和影响，再请求主 CLI 协调。

### Q2: 发现需求不清怎么办？
记录具体疑问与建议方案，等待主 CLI 澄清后继续。

### Q3: 提交被拒怎么办？
按主 CLI 评论修复后重新提交，不要跳过验证。

---

## 违规处理

### 1. Worker CLI 提交 PR 到 main 分支
- **处理**: 主 CLI 直接关闭 PR，要求重新基于 `dev` 提交

### 2. 提交信息不符合规范
- **处理**: 主 CLI 驳回 PR，要求修正后重新提交

### 3. AI 生成代码未验证
- **处理**: 主 CLI 要求执行验证命令（如 `tsc`/`pytest`）并附验证结果

---

## 快速参考

```bash
# 开工前
git branch --show-current
git pull --rebase origin dev

# 提交
git add [files]
git commit -m "fix(api): handle null response"
git push -u origin fix/api-cli-x

# 提PR到dev
gh pr create --base dev --head fix/api-cli-x \
  --title "fix(api): handle null response" \
  --body "AI CLI: CLI-X | 生成模块: api"
```

---

## 相关文档

- `./MAIN_CLI_WORKFLOW_STANDARDS.md`
- `./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md`
- `./TASK_TEMPLATE.md`
- `./MULTI_CLI_WORKTREE_MANAGEMENT.md`

---

**维护建议**: 每个 Worker CLI 在交付后补充“本轮经验总结”，供主 CLI 更新治理规范。
