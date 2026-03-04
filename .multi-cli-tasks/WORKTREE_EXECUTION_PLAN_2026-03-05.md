# 4 Worktree 执行计划（v3.1）

**日期**: 2026-03-05  
**主仓库（Main CLI）**: `/opt/claude/mystocks_spec` (`main`)  
**开发入口分支**: `dev`  
**规则基线**: `.multi-cli-tasks/guides/MULTI_CLI_WORKTREE_MANAGEMENT.md` (v3.1)

---

## 1. 工作单元拓扑

| 工作单元 | 分支 | 物理路径 | 角色定位 |
|---|---|---|---|
| Worker-1 | `mystocks_spec1` | `.worktrees/mystocks_spec1` | 前端功能开发 |
| Worker-2 | `mystocks_spec2` | `.worktrees/mystocks_spec2` | 后端 API/服务开发 |
| Worker-3 | `mystocks_spec3` | `.worktrees/mystocks_spec3` | 数据/策略/计算开发 |
| Worker-4 | `mystocks_spec4` | `.worktrees/mystocks_spec4` | 测试/质量/文档支持 |

---

## 2. 强制治理规则

1. 所有 Worker 分支均从 `dev` 基线派生。  
2. 所有 Worker PR 必须 `base=dev`，禁止直提 `main`。  
3. 提交信息必须符合 `type(scope): short description`。  
4. 提交前必须执行验证，并在 `TASK-REPORT.md` 记录证据。  
5. `main` 仅用于治理、验收与合并 `dev -> main`。  
6. 每个分支必须配置 upstream（`origin/<同名分支>`），未配置不得发起 PR。  

---

## 2.1 Upstream 标准

- `main` -> `origin/main`
- `dev` -> `origin/dev`
- `mystocks_spec1` -> `origin/mystocks_spec1`
- `mystocks_spec2` -> `origin/mystocks_spec2`
- `mystocks_spec3` -> `origin/mystocks_spec3`
- `mystocks_spec4` -> `origin/mystocks_spec4`

首次推送建议命令（自动建立 upstream）：

```bash
git push -u origin "$(git branch --show-current)"
```

修复缺失 upstream：

```bash
branch="$(git branch --show-current)"
git branch --set-upstream-to="origin/${branch}" "${branch}"
```

---

## 3. Main CLI 每日动作

1. 检查 4 个 `TASK-REPORT.md` 更新时间与阻塞状态。  
2. 检查 Worker 最近提交是否符合提交规范。  
3. 检查 PR 目标分支是否为 `dev`。  
4. 汇总问题并写入 `.multi-cli-tasks/` 对应工作单元目录。  

---

## 4. 合并门禁（dev -> main）

- 至少 2 个有效 PR 已合并到 `dev`。  
- 对应测试/检查命令通过并有证据。  
- 无高优先级阻塞问题未关闭。  

标准命令：

```bash
git switch dev
git pull --ff-only origin dev
git log --oneline main..dev
git switch main
git merge --ff-only dev
```

---

## 5. 启动检查命令

```bash
git branch --show-current
git branch --list dev mystocks_spec1 mystocks_spec2 mystocks_spec3 mystocks_spec4
git worktree list | rg "mystocks_spec1|mystocks_spec2|mystocks_spec3|mystocks_spec4"
for b in main dev mystocks_spec1 mystocks_spec2 mystocks_spec3 mystocks_spec4; do
  git rev-parse --abbrev-ref --symbolic-full-name "${b}@{upstream}"
done
```
