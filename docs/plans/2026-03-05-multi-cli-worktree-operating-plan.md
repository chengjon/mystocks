# Multi-CLI Worktree Operating Plan

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在 `mystocks_spec` 主仓库（`main`）下建立稳定的 4 个 Worker worktree 研发体系，并以 v3.1 规则执行长期协作。

**Architecture:** 主仓库 `main` 仅做治理、验收、合并；`dev` 为唯一开发入口；4 个 Worker 分支在独立 worktree 中执行功能开发，统一 PR 到 `dev`，再由主 CLI 合并 `dev -> main`。所有调度与治理工件统一归档在 `.multi-cli-tasks/`。

**Tech Stack:** Git Worktree, Git Branch Workflow (`main/dev/worker`), `.multi-cli-tasks` v3.1 handbook.

### Task 1: Baseline Branch and Worktree Topology

**Files:**
- Modify: `.multi-cli-tasks/README.md`
- Test: `git worktree list` (command verification)

**Step 1: Verify baseline branch state**

Run: `git branch --show-current && git branch --list dev`
Expected: 当前在 `main`，且存在 `dev` 分支。

**Step 2: Verify 4 worker worktrees exist**

Run:

```bash
git worktree list | rg "mystocks_spec1|mystocks_spec2|mystocks_spec3|mystocks_spec4"
```

Expected: 4 条 worktree 记录均存在并绑定同名分支。

**Step 3: Confirm governance entry points**

Run:

```bash
rg -n "v3.1|MAIN_CLI_WORKFLOW|WORKER_CLI_GUIDE" .multi-cli-tasks/README.md
```

Expected: 文档索引显示 v3.1 与主/Worker 指南。

**Step 4: Configure and verify upstream tracking**

Run:

```bash
# main/dev
git branch --set-upstream-to=origin/main main
git branch --set-upstream-to=origin/dev dev

# worker branches
for b in mystocks_spec1 mystocks_spec2 mystocks_spec3 mystocks_spec4; do
  git branch --set-upstream-to="origin/${b}" "${b}"
done

# verify
for b in main dev mystocks_spec1 mystocks_spec2 mystocks_spec3 mystocks_spec4; do
  echo "=== $b ==="
  git rev-parse --abbrev-ref --symbolic-full-name "${b}@{upstream}"
done
```

Expected: 每个分支都显示对应 `origin/<branch>`，无 `(no-upstream)`。

### Task 2: Worktree Responsibility Matrix (Main CLI Owned)

**Files:**
- Create: `.multi-cli-tasks/WORKTREE_ROLE_PLAN_2026-03-05.md`
- Modify: `.FILE_OWNERSHIP`

**Step 1: Draft role plan**

在 `.multi-cli-tasks/WORKTREE_ROLE_PLAN_2026-03-05.md` 定义 4 个工作单元：
- `mystocks_spec1`: 前端/交互类需求
- `mystocks_spec2`: 后端 API / Service 需求
- `mystocks_spec3`: 数据/策略/计算需求
- `mystocks_spec4`: 测试/质量/文档与发布支持

**Step 2: Sync ownership mapping**

在 `.FILE_OWNERSHIP` 写入按目录分配的 CLI ownership，避免并发冲突。

**Step 3: Commit**

Run:

```bash
git add .multi-cli-tasks/WORKTREE_ROLE_PLAN_2026-03-05.md .FILE_OWNERSHIP
git commit -m "docs(multi-cli): add 4-worktree role matrix and ownership mapping"
```

### Task 3: Worker Bootstrap Kit per Worktree

**Files:**
- Create: `.multi-cli-tasks/mystocks_spec1/TASK.md`
- Create: `.multi-cli-tasks/mystocks_spec2/TASK.md`
- Create: `.multi-cli-tasks/mystocks_spec3/TASK.md`
- Create: `.multi-cli-tasks/mystocks_spec4/TASK.md`
- Create: `.multi-cli-tasks/mystocks_spec1/TASK-REPORT.md`
- Create: `.multi-cli-tasks/mystocks_spec2/TASK-REPORT.md`
- Create: `.multi-cli-tasks/mystocks_spec3/TASK-REPORT.md`
- Create: `.multi-cli-tasks/mystocks_spec4/TASK-REPORT.md`

**Step 1: Generate task files from v3.1 template**

参考 `.multi-cli-tasks/guides/templates/TASK_TEMPLATE.md`，每个 worktree 生成：
- `TASK.md`（任务与验收标准）
- `TASK-REPORT.md`（进度与验证证据）

**Step 2: Distribute task files to physical worktrees**

Run:

```bash
cp .multi-cli-tasks/mystocks_spec1/TASK.md .worktrees/mystocks_spec1/TASK.md
cp .multi-cli-tasks/mystocks_spec2/TASK.md .worktrees/mystocks_spec2/TASK.md
cp .multi-cli-tasks/mystocks_spec3/TASK.md .worktrees/mystocks_spec3/TASK.md
cp .multi-cli-tasks/mystocks_spec4/TASK.md .worktrees/mystocks_spec4/TASK.md
```

Expected: 4 个物理 worktree 根目录均有 `TASK.md`。

### Task 4: Daily Governance Loop (Main CLI)

**Files:**
- Create: `.multi-cli-tasks/DAILY_GOVERNANCE_CHECKLIST.md`
- Modify: `scripts/monitoring/check_worker_progress.sh` (optional)

**Step 1: Define daily check cadence**

主 CLI 每日执行三次：
- 检查 `TASK-REPORT.md` 更新时间
- 检查提交信息格式
- 检查 PR base 是否为 `dev`

**Step 2: Define block conditions**

任何一项触发阻塞：
- PR 指向 `main`
- 缺失验证证据
- 24h 无进度心跳

**Step 3: Commit**

Run:

```bash
git add .multi-cli-tasks/DAILY_GOVERNANCE_CHECKLIST.md scripts/monitoring/check_worker_progress.sh
git commit -m "docs(multi-cli): add daily governance loop for 4 worktrees"
```

### Task 5: Integration and Merge Policy (dev -> main)

**Files:**
- Create: `.multi-cli-tasks/INTEGRATION_GATE_POLICY.md`

**Step 1: Define merge gate checklist**

`dev -> main` 合并前必须满足：
- 至少 2 个有效 PR 已入 `dev`
- 本轮变更通过对应验证命令
- 关键风险已在 `TASK-REPORT.md` 关闭或豁免

**Step 2: Add standard merge commands**

Run:

```bash
git switch dev
git pull --ff-only origin dev
git log --oneline main..dev
git switch main
git merge --ff-only dev
```

Expected: 无冲突快进合并；否则退回冲突协调流程。

**Step 3: Commit**

Run:

```bash
git add .multi-cli-tasks/INTEGRATION_GATE_POLICY.md
git commit -m "docs(multi-cli): define dev-to-main integration gate"
```

## Execution Notes

- `mystocks_spec` 主目录固定为 Main CLI 治理位，不承担并行功能开发。
- 4 个 Worker worktree 仅承担分配任务，禁止跨所有权修改。
- 为降低不同 CLI 本地配置冲突，Worker worktree 统一使用主仓库外部平行目录（`/opt/claude/mystocks_spec1` 等）。
- 所有新功能 PR 统一 `base=dev`，禁止直提 `main`。
- 所有分支必须配置 upstream；未配置 upstream 视为阻塞状态，不允许进入 PR 提交流程。

迁移工具（如当前在 `.worktrees/`）：

```bash
bash scripts/worktree/migrate_worktrees_to_parallel.sh --target-root /opt/claude
```
