# 多CLI协作 Worktree 管理手册（标准化版）

**文档版本**: v3.0
**更新日期**: 2026-03-04
**变更说明**: 整合《AI-CLI协作开发规范》，新增分支策略、PR管理规则、提交信息规范、违规处理章节，并完成项目无关化标准化。
**适用范围**: 单开发者 + 多 AI CLI（Claude Code/Codex/Gemini/OpenCode 等）协作的 Git Worktree 项目

---

## 使用说明（先读）

### 适用场景

本手册适用于以下场景：
- 需要并行开发多个模块（如 API、前端、测试、文档）
- 需要主 CLI 统一调度，多个 Worker CLI 独立执行
- 需要通过 Git Worktree 降低分支切换成本并隔离开发上下文

### 项目落地时需替换的占位符

请在落地到具体项目时替换以下内容：
- `[项目名]`：替换为真实仓库名
- `[主仓库路径]`：如 `/path/to/[项目名]`
- `[worktree路径]`：如 `/path/to/[项目名]_feature_x`
- `CLI-X / Worker CLI-1`：替换为实际 CLI 标识

---

## 目录

1. [概述](#概述)
2. [核心概念](#核心概念)
3. [角色定义](#角色定义)
4. [分支策略（所有 CLI 必须遵循）](#分支策略所有-cli-必须遵循)
5. [PR 管理规则](#pr-管理规则)
6. [提交信息规范（AI 生成必须遵循）](#提交信息规范ai-生成必须遵循)
7. [主CLI工作流程](#主cli工作流程)
8. [Worker CLI工作流程](#worker-cli工作流程)
9. [任务分配方法](#任务分配方法)
10. [权限管理](#权限管理)
11. [交互规则](#交互规则)
12. [违规处理](#违规处理)
13. [任务管理工具](#任务管理工具)
14. [快速参考](#快速参考)
15. [相关文档](#相关文档)

---

## 概述

多CLI协作的目标是：
- 保持 `dev` 分支稳定迭代
- 保持 `main` 分支可发布
- 保证每一条变更可追溯到具体 Worker CLI 和模块

核心价值：
1. 真正并行开发（多个 worktree 同时推进）
2. 环境隔离（各 CLI 独立目录）
3. 统一治理（主 CLI 管流程、Worker CLI 管实现）
4. 可审计（统一提交格式 + 统一 PR 规则）

---

## 核心概念

- **主CLI（管理者）**：负责任务拆分、进度治理、PR 审核、分支合并。
- **Worker CLI（执行者）**：负责指定模块开发、自测、提交 PR。
- **主仓库**：`[主仓库路径]`，通常在 `dev` 或 `main`。
- **Worktree**：每个 Worker CLI 的独立工作目录，绑定独立分支。

---

## 角色定义

### 主CLI（Manager）

职责：
1. 任务拆分与分配
2. 建立并维护 worktree 结构
3. 审核与合并 PR（先入 `dev`）
4. 控制 `dev -> main` 节奏

### Worker CLI（Executor）

职责：
1. 从 `dev` 创建专属分支
2. 在专属 worktree 完成模块开发
3. 执行验证命令并提交证据
4. 向 `dev` 发起 PR，不得直提 `main`

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

### 3. 基线校验
每次开始工作前必须执行：
```bash
git branch --show-current
git fetch --all
git worktree list
```

---

## PR 管理规则

### 1. PR 创建（Worker CLI 执行）
- 所有 PR 必须目标 `dev` 分支，禁止直接提交到 `main`
- 统一使用 GitHub CLI 创建 PR

```bash
gh pr create --base dev --head [分支名] \
  --title "[type(scope)]: 描述" \
  --body "AI CLI: [CLI名称] | 生成模块: [模块名]"
```

### 2. PR 审核与合并（主 CLI 执行）
- 主 CLI 审核 Worker CLI 的 PR（功能、规范、验证证据）
- 审核通过后合并至 `dev`
- **`dev` 至少累计 2 个有效 PR 后**，主 CLI 方可合并 `dev` 到 `main`

### 3. 合并顺序建议
1. 先合并低风险/基础能力 PR
2. 再合并依赖其输出的 PR
3. 最后执行集成验证后合并 `dev -> main`

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
- 按项目模块定义（如 `payment` / `login` / `user` / `api`）
- Worker CLI 的 scope 必须与主 CLI 分配模块一致

---

## 主CLI工作流程

1. **任务准备**：拆分任务、定义验收标准、建立工作区
2. **执行监控**：基于 TASK-REPORT / Git 提交进行非侵入式跟踪
3. **审查合并**：审核 PR 并合并到 `dev`
4. **发布门禁**：满足条件后合并 `dev -> main`
5. **收尾清理**：移除完成的 worktree，归档报告

---

## Worker CLI工作流程

1. 读取 TASK.md（明确范围、验收标准、依赖）
2. 在专属分支开发并小步提交
3. 执行本模块验证命令并记录结果
4. 更新 TASK-REPORT.md（进度、阻塞、证据）
5. 发起到 `dev` 的 PR，并等待主 CLI 审核

---

## 任务分配方法

建议主 CLI 使用四要素分配：
- **模块边界**（避免重叠）
- **输入依赖**（谁先谁后）
- **验收标准**（可量化）
- **验证命令**（可复现）

---

## 权限管理

- 主 CLI：全局读写、合并、回滚协调
- Worker CLI：本 worktree 读写；跨边界修改需申请
- 共享文件（如 README、根配置）应设定默认 owner

---

## 交互规则

1. Worker CLI 遇阻塞先在 TASK-REPORT 记录
2. 主 CLI 基于记录进行协调而非直接代做
3. 涉及跨模块改动必须先同步 owner CLI
4. 所有决策留痕（提交、PR、报告）

---

## 违规处理

### 1. Worker CLI 提交 PR 到 main 分支
- **处理**: 主 CLI 直接关闭 PR，要求重新基于 `dev` 提交

### 2. 提交信息不符合规范
- **处理**: 主 CLI 驳回 PR，要求修正后重新提交

### 3. AI 生成代码未验证
- **处理**: 主 CLI 要求执行验证命令（如 `tsc` / `pytest`）并附验证结果

---

## 任务管理工具

- Git Worktree：隔离执行上下文
- GitHub CLI：标准化 PR 生命周期
- TASK.md / TASK-REPORT.md：任务与进度双文档机制

---

## 快速参考

```bash
# 查看当前分支
git branch --show-current

# 查看所有 worktree
git worktree list

# 新建 worker worktree
git worktree add ./worker-api -b feat/api-cli-x dev

# 推送分支
git push -u origin feat/api-cli-x

# 发起 PR 到 dev
gh pr create --base dev --head feat/api-cli-x \
  --title "feat(api): add xxx endpoint" \
  --body "AI CLI: CLI-X | 生成模块: api"
```

---

## 相关文档

- `./MAIN_CLI_WORKFLOW_STANDARDS.md`
- `./CLI_WORKFLOW_GUIDE.md`
- `./GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md`
- `./TASK_TEMPLATE.md`
- `./GIT_WORKTREE_MAIN_CLI_MANUAL.md`

---

**维护建议**: 每次多CLI协作结束后，按“问题-原因-修复-规则更新”机制迭代本文档。