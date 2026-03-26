# Main CLI 工作规范与最佳实践（标准化版）

**文档版本**: v3.0
**更新日期**: 2026-03-04
**变更说明**: 整合《AI-CLI协作开发规范》，新增分支策略、PR管理规则、提交信息规范、违规处理；完成项目无关化。
**适用范围**: 所有使用 Git Worktree 的多 CLI 协作项目（主 CLI 视角）

---

## 使用说明

- 本文档用于主 CLI（管理者）执行“任务拆分-流程治理-PR审查-发布合并”。
- 项目落地时，请替换占位符：`[项目名]`、`[主仓库路径]`、`Worker CLI-X`。
- 若与项目内部规范冲突，以项目强制门禁为准。

---

## 目录

1. [文档目的](#文档目的)
2. [核心原则](#核心原则)
3. [Step -1: Pre-flight检查清单](#step--1-pre-flight检查清单)
4. [分支策略（所有 CLI 必须遵循）](#分支策略所有-cli-必须遵循)
5. [PR 管理规则](#pr-管理规则)
6. [提交信息规范（AI 生成必须遵循）](#提交信息规范ai-生成必须遵循)
7. [Phase 0: 准备阶段工作清单](#phase-0-准备阶段工作清单)
8. [Phase 1: Git Worktree 创建标准流程](#phase-1-git-worktree-创建标准流程)
9. [Phase 2: 监控系统设置](#phase-2-监控系统设置)
10. [Phase 3: 文档组织规范](#phase-3-文档组织规范)
11. [Phase 4: 验收与交付标准](#phase-4-验收与交付标准)
12. [违规处理](#违规处理)
13. [最佳实践总结](#最佳实践总结)
14. [相关文档](#相关文档)
15. [文档维护](#文档维护)

---

## 文档目的

建立主 CLI 的统一执行标准：
- 防止任务分配冲突和分支治理失控
- 保证 Worker CLI 提交可追溯、可验收
- 保证 `dev` 稳定迭代、`main` 可发布

---

## 核心原则

1. **完整优先**：先建规则与模板，再启动 Worker。
2. **文档驱动**：任务边界、验收标准、验证命令必须写清。
3. **非侵入式监控**：主 CLI 以报告和提交记录观察，不代做实现。
4. **标准化复用**：统一命名、统一提交、统一 PR 模板。

## 当前开工口令标准

主 CLI 给 worker 的统一开工口令保持为：

```text
请按你当前 worktree 的 TASK.md 开工。
```

其余上下文不再依赖聊天补充，默认写入：

- `TASK.md`
- `TASK-REPORT.md`
- `docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md`
- `docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md`

边界要求：

- Mongo 负责任务状态、claim、plan、submit、review 生命周期
- Graphiti 负责长期记忆、handoff、历史事实检索
- 主 CLI 不得把 Graphiti 当作任务状态真相源

---

## Step -1: Pre-flight检查清单

主 CLI 在开始任何新工作前，必须执行：

```bash
pwd
git branch --show-current
git worktree list
git fetch --all
git log HEAD..origin/dev --oneline
```

对于 MyStocks 当前的“本地优先 + SQLite tracker + Maestro”工作流，在**正式分配 owner / worker 前**，还应增加一轮 owner suggestion pre-flight：

```bash
python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md \
  --path <可选补充路径1> \
  --path <可选补充路径2>
```

主 CLI 解释输出时遵循：
1. `suggested_owner` 只是建议，不是自动分配结果
2. 若建议 owner 与 `.FILE_OWNERSHIP`、`TASK.md` 路径线索一致，可优先采用
3. 若输出回退到 `main`，通常表示“未知路径较多”或“多个 owner 并列”，应由主 CLI 继续人工拆分/协调
4. 在确定最终 owner 后，先写入 `TASK.md`，再用运行时记录机器态 assignment

建议的落地顺序：

```bash
# 1) 先拿建议
python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md

# 2) 人工确认 owner / worker 后，再持久化 assignment
python scripts/runtime/maestro_collab.py assign <ISSUE-ID> \
  --worker-cli <CLI-NAME> \
  --assigned-by main \
  --acceptance-summary "<验收摘要>"
```

如果发现已完成的 worker 分支：
1. 确认其工作区无未提交变更
2. 审核并合并 PR 至 `dev`
3. 清理对应 worktree
4. 更新进度文档

---

## 分支策略（所有 CLI 必须遵循）

### 1. 分支基础规则
- **基准分支**: `dev`（开发分支，所有代码变更的唯一入口）
- **生产分支**: `main`（仅从 `dev` 合并，禁止直接提交/PR）
- **临时分支**: 子 CLI 基于 `dev` 创建功能分支
  - 命名格式：`feat/[模块名]-[cli标识]` 或 `fix/[模块名]-[cli标识]`
  - 示例：`feat/payment-codex`、`fix/login-gemini`

### 2. 工作区创建（Git Worktree）
```bash
# 主CLI初始化（仅首次执行）
git worktree add ./ai-workspace -b dev origin/dev

# 子CLI创建专属工作区
git worktree add ./worker-payment -b feat/payment-cli-x dev
```

### 3. 主 CLI 审核要点
- Worker 分支是否从 `dev` 分叉
- 分支名是否符合命名规范
- 是否存在直连 `main` 的提交/PR

---

## PR 管理规则

### 1. PR 创建（Worker CLI 执行）
- 所有 PR 必须目标 `dev`，禁止直接到 `main`
- 统一使用 GitHub CLI：

```bash
gh pr create --base dev --head [分支名] \
  --title "[type(scope)]: 描述" \
  --body "AI CLI: [CLI名称] | 生成模块: [模块名]"
```

### 2. PR 审核与合并（主 CLI 执行）
- 主 CLI 负责审查：需求符合性、代码质量、验证证据
- 审核通过后合并到 `dev`
- **`dev` 至少累计 2 个有效 PR 后**，方可合并 `dev -> main`

### 3. 有效 PR 判定标准
- 有明确模块边界
- 有通过的验证命令输出
- 提交信息合规
- 未引入跨模块未审批改动

---

## 提交信息规范（AI 生成必须遵循）

### 1. 格式要求
- 强制英文：`type(scope): short description`（建议 50 字符内）
- 禁止无意义描述（如 `update code`、`fix bug`）

### 2. 类型（type）枚举

| 类型 | 适用场景 | 示例 |
|------|---------|------|
| `feat` | 新功能开发 | `feat(payment): add amount calc` |
| `fix` | 修复 bug | `fix(login): resolve token expire` |
| `docs` | 文档更新 | `docs(readme): update workflow` |
| `refactor` | 代码重构 | `refactor(user): optimize model` |
| `chore` | 构建/配置变更 | `chore(ci): add test step` |

### 3. 范围（scope）枚举
- 按项目模块定义（如 `payment`/`login`/`user`/`api`）
- Worker CLI 必须与主 CLI 分配模块一致

---

## Phase 0: 准备阶段工作清单

主 CLI 启动前必须具备：
1. 任务分配文档（含验收标准）
2. Worker 工作流文档（TASK + TASK-REPORT 机制）
3. 监控机制（定期检查）
4. 文件所有权映射（避免重叠修改）

---

## Phase 1: Git Worktree 创建标准流程

```bash
# 示例
git worktree add [worktree路径] -b feat/module-cli-x dev
```

创建后检查：
- 分支正确
- 任务文档已下发
- hooks 与校验机制可用

---

## Phase 2: 监控系统设置

- 监控数据源：`TASK-REPORT.md` + Git 历史
- 预警阈值建议：24h 黄色、48h 红色
- 主 CLI 在红色预警时必须触发阻塞协调

---

## Phase 3: 文档组织规范

推荐目录：`docs/guides/multi-cli-tasks/`
- `MAIN_CLI_WORKFLOW_STANDARDS.md`
- `CLI_WORKFLOW_GUIDE.md`
- `GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md`
- `TASK_TEMPLATE.md`

任务文档使用：
- `TASK.md`: 任务定义
- `TASK-REPORT.md`: 进度报告
- `TASK-*-REPORT.md`: 阶段完成报告

---

## Phase 4: 验收与交付标准

单个 Worker CLI 完成标准：
- 任务 100% 完成
- 验收项全部通过
- 分支已推送并发起 PR（base=dev）
- 验证证据完整
- 报告文档完整

主 CLI 集成标准：
- 所有必须 PR 合并到 `dev`
- 集成验证通过
- 满足发布条件再合并 `dev -> main`

---

## 违规处理

### 1. Worker CLI 提交 PR 到 main 分支
- **处理**: 主 CLI 直接关闭 PR，要求重新基于 `dev` 提交

### 2. 提交信息不符合规范
- **处理**: 主 CLI 驳回 PR，要求修正后重新提交

### 3. AI 生成代码未验证
- **处理**: 主 CLI 要求执行验证命令（如 `tsc`/`pytest`）并附验证结果

---

## 最佳实践总结

### Do
- 先规范后执行
- 小步提交、频繁同步
- 所有决策和证据留痕

### Don’t
- 允许直连 `main`
- 未验证即合并
- 模块边界不清下并行开发

---

## 相关文档

- `./CLI_WORKFLOW_GUIDE.md`
- `./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md`
- `./TASK_TEMPLATE.md`
- `./MULTI_CLI_WORKTREE_MANAGEMENT.md`

---

## 文档维护

**版本历史**:
- v3.0 (2026-03-04): 标准化改造，整合 AI-CLI 协作规范，新增分支/PR/提交/违规章节。

**维护者**: Main CLI
