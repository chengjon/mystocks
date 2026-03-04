# 多 CLI Worktree 场景复用：AI Prompt + 人工 SOP

**文档版本**: v1.0  
**最后更新**: 2026-03-05  
**适用范围**: Git Worktree 多 CLI 协作、规则升级、分支/工作树批量同步

---

## 1. 适用场景

当你遇到以下任一情况时，直接复用本文件：

- 需要把协作规则统一升级（如 `main` 协调验收制、`dev-*` 开发制）
- 需要把仓库内 `.worktrees/` 迁移到外部平行目录（如 `/opt/claude`）
- 需要批量同步多个 worktree 到最新 `main`
- 需要给多个 CLI 分配标准化开发分支与 PR 要件

---

## 2. 可直接给 AI 的 Prompt（通用版）

> 将下面整段复制给 AI；仅替换方括号变量。

```text
你是本仓库的主协调工程师。请按“最小破坏、可审计、可回滚”的原则完成以下工作，并直接执行命令与修改文档。

【仓库信息】
- REPO_ROOT: [例如 /opt/claude/mystocks_spec]
- MAIN_BRANCH: main
- WORKTREE_ROOT: [例如 /opt/claude]
- WORKTREE_DIRS: [例如 /opt/claude/mystocks_spec1,/opt/claude/mystocks_spec2,/opt/claude/mystocks_spec3,/opt/claude/mystocks_spec4]
- DEV_BRANCHES: [例如 dev-mystocks-spec1,dev-mystocks-spec2,dev-mystocks-spec3,dev-mystocks-spec4]

【治理规则（强制）】
1. main 只做协调与验收，不直接做功能开发。
2. 新功能统一在 worktree/dev-* 分支开发。
3. 每个 worktree 分支提交 PR 到 main。
4. PR 必须附：变更范围、验证命令与结果、风险/回滚说明。
5. 合并门禁：质量门（TS/Python/tests）+ 安全门（secrets/audit/SAST）+ 审查门（code review）。
6. main 仅保留“干净、可复现、可回滚”版本。

【执行任务】
A. 审计当前状态：分支、upstream、worktree 列表、脏工作区。
B. 如存在仓库内 .worktrees，执行迁移：
   bash scripts/worktree/migrate_worktrees_to_parallel.sh --target-root /opt/claude
C. 更新规则文档与任务模板，统一到上述治理规则。
D. 创建/校验 dev-* 分支并配置 upstream（必要时 push -u）。
E. 同步每个 worktree 到最新 main 基线，并切换到对应 dev-* 分支。
F. 输出最终报告：
   1) 修改了哪些文件
   2) 执行了哪些命令及关键结果
   3) 若因权限无法直接操作某些目录，给出可直接复制的人工接力命令

【执行约束】
- 不得回滚用户已有未提交改动。
- 只暂存/提交本次目标文件。
- 非 destructive：禁止 git reset --hard / 强制覆盖用户工作。
- 每步给出可核验命令结果。
```

---

## 3. 可直接给 AI 的 Prompt（受限权限版）

> 当 AI 不能写平行目录（例如只能写仓库根目录）时使用。

```text
请在仓库内完成所有可写操作；对仓库外 worktree 目录仅做“远端分支对齐 + 本地接力命令输出”。

必须执行：
1. 在 main 推送规则与模板更新。
2. 将 main 快进推送到各远端 worker 分支（如 mystocks_spec1~4）。
3. 输出人工接力命令（for 循环），用于在 /opt/claude/mystocks_spec1~4 本地执行 pull/switch。

输出必须包含：
- 已完成项（含 commit hash）
- 未完成项（受限原因）
- 一键接力命令
```

---

## 4. 人工处理 SOP（全流程）

## 4.1 前置检查

```bash
git -C /opt/claude/mystocks_spec branch --show-current
git -C /opt/claude/mystocks_spec remote -v
git -C /opt/claude/mystocks_spec worktree list
git -C /opt/claude/mystocks_spec status -sb
```

检查点：
- 当前在 `main`
- 远程使用 `origin`
- 知道哪些变更是“本次目标”，哪些是“用户既有脏改动”

## 4.2 路径迁移（如需要）

```bash
cd /opt/claude/mystocks_spec
bash scripts/worktree/migrate_worktrees_to_parallel.sh --target-root /opt/claude
git worktree list
```

## 4.3 分支与基线准备

```bash
cd /opt/claude/mystocks_spec
git fetch origin main

git branch -f dev-mystocks-spec1 origin/main
git branch -f dev-mystocks-spec2 origin/main
git branch -f dev-mystocks-spec3 origin/main
git branch -f dev-mystocks-spec4 origin/main

git push -u origin dev-mystocks-spec1 dev-mystocks-spec2 dev-mystocks-spec3 dev-mystocks-spec4
```

## 4.4 同步 4 个 worktree（人工本机执行）

```bash
for i in 1 2 3 4; do
  wt="/opt/claude/mystocks_spec${i}"
  b="dev-mystocks-spec${i}"
  echo "== $wt -> $b =="
  git -C "$wt" fetch origin
  git -C "$wt" pull --ff-only
  git -C "$wt" switch "$b"
  git -C "$wt" pull --ff-only
  git -C "$wt" status -sb
done
```

## 4.5 PR 创建标准（每个 dev-* 分支）

```bash
gh pr create --base main --head dev-mystocks-spec1 \
  --title "feat(scope): short description" \
  --body "Change Scope: ...\nVerification: ...\nRisk/Rollback: ..."
```

PR 必填项：
- 变更范围
- 验证命令与结果
- 风险/回滚说明

合并门禁：
- 质量门（TS/Python/tests）
- 安全门（secrets/audit/SAST）
- 审查门（code review）

## 4.6 合并与回滚

合并前：
```bash
git fetch origin
git log --oneline origin/main..origin/dev-mystocks-spec1
```

紧急回滚（已合并 PR）：
```bash
git checkout main
git pull --ff-only origin main
git revert <merge_or_feature_commit_sha>
git push origin main
```

---

## 5. 常见异常与处理

### 5.1 `Permission denied`（AI 无法写 `/opt/claude/mystocks_spec1~4`）

处理：
- AI 在仓库内完成文档与分支更新并 push。
- 人工在本机执行“4.4 同步命令”。

### 5.2 `non-fast-forward` 推送失败

```bash
git fetch origin
git rebase origin/main
# 或按团队策略 merge
git push origin <branch>
```

### 5.3 `no upstream` 阻塞

```bash
branch="$(git branch --show-current)"
git push -u origin "$branch"
git rev-parse --abbrev-ref --symbolic-full-name "@{upstream}"
```

---

## 6. 交付检查清单

- [ ] 规则文档已统一到当前治理口径
- [ ] `dev-*` 分支已创建并绑定 upstream
- [ ] worktree 本地已切到对应 `dev-*`
- [ ] PR 模板字段已完整（Scope/Verification/Risk-Rollback）
- [ ] 合并前门禁（质量/安全/审查）具备可审计证据

