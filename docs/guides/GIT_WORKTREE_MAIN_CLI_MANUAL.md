# Git Worktree 命令参考手册

**版本**: v2.0
**创建日期**: 2025-12-28
**最后更新**: 2025-12-30
**维护者**: Main CLI
**目标读者**: 主CLI、需要查询Git命令的Worker CLI

---

## 📚 目录

1. [核心概念](#核心概念)
2. [命令速查](#命令速查)
3. [详细命令说明](#详细命令说明)
4. [Git别名系统](#git别名系统) ⭐ 新增
5. [故障排查](#故障排查)
6. [相关文档](#相关文档)

---

## 核心概念

### 什么是 Git Worktree？

Git Worktree 允许在**同一个仓库**中创建**多个独立的工作目录**，每个目录可以签出不同的分支。

**官方定义**: > "Git worktree allows you to have multiple working directories attached to same repository."

**关键优势**:
- ✅ **真正的并行开发**: 无需 stash 或频繁切换分支
- ✅ **隔离的工作环境**: 每个 worktree 有独立的文件状态
- ✅ **共享 Git 历史**: 所有 worktree 共享 refs/ 和对象数据库
- ✅ **零上下文切换开销**: 每个 CLI 在独立目录中工作

**架构图**:
```
mystocks_spec/                    # 主仓库 (主 worktree)
├── .git/                        # Git 对象数据库 (共享)
│   ├── worktrees/               # Worktree 元数据
│   │   ├── phase6-monitor/      # CLI-1 的元数据
│   │   ├── phase6-cache/        # CLI-3 的元数据
│   │   ├── phase6-e2e/          # CLI-2 的元数据
│   │   └── phase6-docs/         # CLI-4 的元数据
│   ├── refs/                    # 共享的引用 (分支/标签)
│   └── objects/                 # 共享的 Git 对象
├── src/                         # 主分支代码
└── ...

/opt/claude/mystocks_phase6_monitor/  # CLI-1 worktree
├── .git -> ../mystocks_spec/.git/worktrees/phase6-monitor
└── 监控系统验证代码

/opt/claude/mystocks_phase6_e2e/        # CLI-2 worktree
├── .git -> ../mystocks_spec/.git/worktrees/phase6-e2e
└── E2E 测试代码

... 其他 worktree
```

**共享 vs 独立**:
- **共享**: `refs/`, `objects/`（Git历史和引用）
- **独立**: `HEAD`, `index`, 工作目录文件（每个worktree有自己的状态）

---

## 命令速查

### 创建 Worktree

```bash
# 基本语法
git worktree add <路径> [<分支名>] [<起点>]

# 创建新分支并签出
git worktree add -b <新分支名> <路径>

# 从现有分支创建
git worktree add <路径> <分支名>

# 从指定起点创建
git worktree add <路径> <分支名> <起点>

# 创建分离式 HEAD（用于实验）
git worktree add --detach <路径>

# 创建并锁定（用于便携设备）
git worktree add --lock <路径> <分支名>

# 示例
git worktree add /opt/claude/mystocks_phase6_cache phase6-cache-optimization
git worktree add -b phase6-new-feature /opt/claude/mystocks_new_feature
```

### 列出 Worktree

```bash
# 基本列表
git worktree list

# 详细模式
git worktree list -v

# 脚本友好格式
git worktree list --porcelain

# 仅显示特定 worktree
git worktree list | grep phase6
```

**输出示例**:
```
/opt/claude/mystocks_spec                abcd1234 [main]
/opt/claude/mystocks_phase6_monitor        5678abcd [phase6-monitoring-verification]
/opt/claude/mystocks_phase6_e2e             1234ef56 [phase6-e2e-testing]
/opt/claude/mystocks_phase6_cache           8b33d71 [phase6-cache-optimization]
/opt/claude/mystocks_phase6_docs            9f0e1a2b [phase6-documentation]
```

### 删除 Worktree

```bash
# 删除干净的 worktree
git worktree remove /path/to/worktree

# 强制删除（即使有未提交的修改）
git worktree remove -f /path/to/worktree

# 强制删除锁定的 worktree
git worktree remove --force --force /path/to/locked

# 示例
git worktree remove /opt/claude/mystocks_phase6_cache
git worktree remove -f /opt/claude/mystocks_phase6_e2e
```

### 移动 Worktree

```bash
# 移动 worktree 到新位置
git worktree move /opt/claude/old /opt/claude/new

# 移动并重命名
git worktree move /opt/claude/mystocks_phase6_e2e mystocks_e2e_testing_new

# 示例
git worktree move mystocks_phase6_e2e mystocks_e2e_testing_new
```

### Prune（清理）

```bash
# 预览将要删除什么
git worktree prune -n

# 实际清理
git worktree prune

# 详细输出
git worktree prune -v

# 仅清理过期超过指定时间的
git worktree prune --expire 3.months.ago

# 示例
git worktree prune
git worktree prune -v
```

### 锁定/解锁

```bash
# 锁定 worktree（防止被 prune）
git worktree lock /path/to/worktree

# 锁定并注明原因
git worktree lock --reason "进行重要修复" /path/to/worktree

# 解锁
git worktree unlock /path/to/worktree

# 示例
git worktree lock --reason "存储在便携设备上" /opt/claude/mystocks_portable
git worktree unlock /opt/claude/mystocks_portable
```

### Repair（修复）

```bash
# 修复主仓库与链接 worktree 的连接
git worktree repair

# 修复特定 worktree
git worktree repair /path/to/broken/worktree

# 示例
git worktree repair
git worktree repair /opt/claude/mystocks_phase6_broken
```

---

## 详细命令说明

### 1. git worktree add

**语法**:
```bash
git worktree add [-f] [--detach] [--checkout] [--lock [--reason <reason>]]
               [-b <new-branch>] <path> [<commit-ish>]
```

**参数说明**:
- `-f`: 强制创建，即使目标目录已存在
- `--detach`: 创建分离式 HEAD（不在任何分支上）
- `--checkout`: 创建后不立即切换到该 worktree
- `--lock`: 创建后锁定 worktree
- `--reason <reason>`: 锁定的原因
- `-b <new-branch>`: 创建新分支并签出

**使用场景**:

**场景1: 从现有分支创建**
```bash
git worktree add /opt/claude/mystocks_phase6_cache phase6-cache-optimization
```

**场景2: 创建新分支**
```bash
git worktree add -b phase6-new-feature /opt/claude/mystocks_new_feature
```

**场景3: 从指定起点创建**
```bash
git worktree add /opt/claude/mystocks_experiment phase6-experiment~2
```

**场景4: 创建实验性 worktree**
```bash
git worktree add --detach /opt/claude/mystocks_experiment
```

### 2. git worktree list

**语法**:
```bash
git worktree list [-v | --porcelain]
```

**参数说明**:
- `-v`: 显示详细信息（包括 HEAD 提交哈希）
- `--porcelain`: 脚本友好格式（便于解析）

**输出格式**:
```
<worktree-path> <commit-hash> [<branch-name>]
```

**详细模式示例**:
```
/opt/claude/mystocks_spec                abcd1234 [main]
/worktrees/phase6-monitor/       HEAD (bare)
/opt/claude/mystocks_phase6_monitor        5678abcd [phase6-monitoring-verification]
```

### 3. git worktree remove

**语法**:
```bash
git worktree remove [-f] --force [--force] <path>
```

**参数说明**:
- `-f`: 强制删除有未提交修改的 worktree
- `--force --force`: 强制删除锁定的 worktree

**使用场景**:

**场景1: 删除干净的 worktree**
```bash
# 先确认 worktree 是干净的
cd /opt/claude/mystocks_phase6_cache
git status --short

# 如果没有修改，删除
cd /opt/claude/mystocks_spec
git worktree remove /opt/claude/mystocks_phase6_cache
```

**场景2: 强制删除脏 worktree**
```bash
# worktree 有未提交的修改，强制删除
git worktree remove -f /opt/claude/mystocks_phase6_cache
```

**场景3: 删除锁定的 worktree**
```bash
# worktree 被锁定，强制删除
git worktree remove --force --force /opt/claude/mystocks_locked
```

### 4. git worktree prune

**语法**:
```bash
git worktree prune [-n] [-v] [--expire <time>]
```

**参数说明**:
- `-n`: 预览模式（不实际删除）
- `-v`: 详细输出
- `--expire <time>`: 仅清理过期超过指定时间的 worktree

**使用场景**:

**场景1: 预览将要删除什么**
```bash
git worktree prune -n
```

**场景2: 清理过期的 worktree**
```bash
# 实际清理
git worktree prune

# 查看详细输出
git worktree prune -v
```

**场景3: 清理3个月前的 worktree**
```bash
git worktree prune --expire 3.months.ago
```

**何时需要 prune**:
- 手动删除 worktree 目录（而不是使用 `git worktree remove`）
- 硬盘故障恢复后
- 意外删除 `.git/worktrees` 目录

### 5. git worktree lock/unlock

**语法**:
```bash
git worktree lock [--reason <reason>] <path>
git worktree unlock <path>
```

**使用场景**:

**场景1: 锁定便携设备上的 worktree**
```bash
git worktree lock --reason "存储在便携设备上" /opt/claude/mystocks_portable
```

**场景2: 解锁 worktree**
```bash
git worktree unlock /opt/claude/mystocks_portable
```

**锁定状态检查**:
```bash
git worktree list -v | grep locked
# 输出示例: /opt/claude/mystocks_portable  1234abc [locked]
```

### 6. git worktree repair

**语法**:
```bash
git worktree repair [<path>...]
```

**使用场景**:

**场景1: 修复主仓库与链接 worktree 的连接**
```bash
# 主仓库移动后，修复所有 worktree
cd /opt/claude/mystocks_spec
git worktree repair
```

**场景2: 修复特定 worktree**
```bash
git worktree repair /opt/claude/mystocks_phase6_broken
```

**何时需要 repair**:
- 主仓库目录被移动
- 手动修改 `.git` 文件导致链接断裂
- Git 升升级后 worktree 元数据损坏

---

## Git别名系统 ⭐ 新增

### 配置 Git 别名

在 `~/.gitconfig` 中添加以下别名：

```bash
# Git Worktree 别名
[alias]
  wt = worktree
  wta = worktree add
  wtls = worktree list
  wtrm = worktree remove
  wtmv = worktree move
  wtprune = worktree prune
  wtlock = worktree lock
  wtunlock = worktree unlock
  wtrepair = worktree repair
```

### 配置步骤

**方法1: 手动编辑**
```bash
# 编辑 Git 配置文件
vim ~/.gitconfig

# 添加上述 [alias] 部分

# 保存并退出
```

**方法2: 使用 git config 命令**
```bash
# 添加单个别名
git config --global alias.wt worktree
git config --global alias.wta worktree add
git config --global alias.wtls worktree list
git config --global alias.wtrm worktree remove
git config --global alias.wtmv worktree move
git config --global alias.wtprune worktree prune
git config --global alias.wtlock worktree lock
git config --global alias.wtunlock worktree unlock
git config --global alias.wtrepair worktree repair

# 批量添加所有别名
cat >> ~/.gitconfig << 'EOF'

[alias]
  wt = worktree
  wta = worktree add
  wtls = worktree list
  wtrm = worktree remove
  wtmv = worktree move
  wtprune = worktree prune
  wtlock = worktree lock
  wtunlock = worktree unlock
  wtrepair = worktree repair
EOF
```

### 使用别名

**简化后的命令**:
```bash
# 创建 worktree
git wta /opt/claude/mystocks_phase6_cache phase6-cache-optimization

# 列出 worktree
git wtls

# 删除 worktree
git wtrm /opt/claude/mystocks_phase6_cache

# 移动 worktree
git wtmv /opt/claude/old /opt/claude/new

# 清理过期 worktree
git wtprune -v

# 锁定 worktree
git wtlock /opt/claude/mystocks_portable

# 解锁 worktree
git wtunlock /opt/claude/mystocks_portable

# 修复 worktree
git wtrepair
```

**好处**:
- ✅ 减少输入字符（从 `git worktree` 到 `git wt`）
- ✅ 提高命令效率
- ✅ 减少拼写错误

---

## 故障排查

### 问题 1: Worktree 路径损坏

**症状**:
```bash
$ git worktree list
error: cannot locate worktree '/path/to/worktree'
```

**解决方案**:
```bash
# 方法 1: 使用 repair 修复
git worktree repair /path/to/worktree

# 方法 2: 手动删除元数据
rm -rf .git/worktrees/worktree-name
git worktree prune
```

### 问题 2: Worktree 被锁定

**症状**:
```bash
$ git worktree remove /path/to/worktree
error: cannot remove a locked worktree
```

**解决方案**:
```bash
# 1. 解锁
git worktree unlock /path/to/worktree

# 2. 再次删除
git worktree remove /path/to/worktree
```

### 问题 3: 主仓库移动后链接断裂

**症状**:
- 所有 worktree 的 `.git` 文件指向错误的路径

**解决方案**:
```bash
# 在主仓库中运行 repair
git worktree repair

# 验证所有 worktree
git worktree list -v
```

### 问题 4: Worktree 检测到 "detached HEAD"

**症状**:
```bash
$ git worktree list
/path/to/worktree  abcd1234 (detached HEAD)
```

**原因**: worktree 处于分离式 HEAD 状态（不在任何分支上）

**解决方案**:
```bash
cd /path/to/worktree

# 创建新分支
git switch -c new-branch

# 或检出现有分支
git switch existing-branch
```

### 问题 5: Pre-commit hook 在 worktree 中失败

**症状**:
- 在 worktree 中提交时 pre-commit hook 失败
- 需要禁用特定 worktree 的 hook

**解决方案**:
```bash
cd /path/to/worktree

# 临时跳过 hook
git commit --no-verify -m "message"

# 或永久禁用该 worktree 的 hook
git config core.hooksPath /dev/null
```

### 问题 6: ".git" 文件不存在的错误

**症状**:
```bash
$ cd /path/to/worktree
fatal: Not a git repository (or any of the parent directories): .git
```

**原因**: worktree 的 `.git` 文件损坏或被删除

**解决方案**:
```bash
# 1. 在主仓库中检查 worktree 状态
git worktree list

# 2. 使用 repair 修复
git worktree repair /path/to/worktree

# 3. 验证修复
cd /path/to/worktree
git status
```

### 问题 7: 删除 worktree 时提示 "not a worktree"

**症状**:
```bash
$ git worktree remove /path/to/worktree
fatal: '/path/to/worktree' is not a worktree
```

**原因**: Git 不认为该目录是一个 worktree

**解决方案**:
```bash
# 方法 1: 检查 worktree 列表
git worktree list

# 方法 2: 如果目录存在但不在列表中，手动删除
rm -rf /path/to/worktree

# 方法 3: 使用 prune 清理元数据
git worktree prune
```

---

## 相关文档

### 工作流程文档
- [主CLI工作规范](./multi-cli-tasks/MAIN_CLI_WORKFLOW_STANDARDS.md) - 主CLI工作流程
- [Worker CLI工作流程](./multi-cli-tasks/CLI_WORKFLOW_GUIDE.md) - Worker CLI工作流程
- [协作冲突预防](./multi-cli-tasks/GIT_WORKTREE_COLLABORATION_CONFLICT_PREVENTION.md) - 冲突处理

### 任务管理文档
- [任务文档模板](./multi-cli-tasks/TASK_TEMPLATE.md) - TASK.md和TASK-REPORT.md模板

### 其他配置
- [Git远程名称标准](./multi-cli-tasks/GIT_REMOTE_NAME_STANDARD.md) - 远程配置规范

---

## 附录

### 常用操作流程

**批量创建 worktree**:
```bash
#!/bin/bash
# 批量创建 worktree

MAIN_REPO="/opt/claude/mystocks_spec"
cd "$MAIN_REPO"

declare -A WORKTREES
WORKTREES=(
    ["phase6-monitor"]="phase6-monitoring-verification"
    ["phase6-e2e"]="phase6-e2e-testing"
    ["phase6-cache"]="phase6-cache-optimization"
    ["phase6-docs"]="phase6-documentation"
)

for key in "${!WORKTREES[@]}"; do
    branch="${WORKTREES[$key]}"
    path="/opt/claude/mystocks_$key"

    echo "创建: $key"
    echo "  分支: $branch"
    echo "  路径: $path"

    git worktree add "$path" "$branch"
    echo "  ✅ 创建成功"
    echo ""
done

echo "=== 所有 worktree 创建完成 ==="
git worktree list
```

**批量删除 worktree**:
```bash
#!/bin/bash
# 批量删除 worktree

MAIN_REPO="/opt/claude/mystocks_spec"
cd "$MAIN_REPO"

for worktree in /opt/claude/mystocks_phase6_*; do
    echo "删除: $worktree"
    git worktree remove "$worktree" 2>/dev/null && echo "  ✅ 删除成功" || echo "  ❌ 删除失败"
    echo ""
done

echo "=== 清理元数据 ==="
git worktree prune

echo "=== 剩余 worktree ==="
git worktree list
```

---

**版本**: v2.0
**最后更新**: 2025-12-30
**维护者**: Main CLI
