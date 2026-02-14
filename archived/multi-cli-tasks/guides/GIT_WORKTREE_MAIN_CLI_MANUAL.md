# Git Worktree 命令参考手册

**版本**: v2.1
**创建日期**: 2025-12-28
**最后更新**: 2026-02-13
**维护者**: Main CLI
**目标读者**: 主CLI、需要查询Git命令的Worker CLI

---

## 📚 目录

1. [核心概念](#核心概念)
2. [命令速查](#命令速查)
3. [详细命令说明](#详细命令说明)
4. [Git别名系统](#git别名系统)
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
git worktree add [-f] [--detach] [--checkout] [--lock [--reason <string>]]
               [--orphan] [(-b | -B) <new-branch>] <path> [<commit-ish>]

# 创建新分支并签出
git worktree add -b <新分支名> <路径>

# 创建孤儿分支 (Git 2.42+)
git worktree add --orphan <新分支名> <路径>

# 使用相对路径链接 (提高便携性, Git 2.41+)
git worktree add --relative-paths <路径> <分支名>

# 从现有分支创建
git worktree add <路径> <分支名>
```

### 列出 Worktree

```bash
# 基本列表
git worktree list

# 详细模式 (包含锁定/可清理状态)
git worktree list -v

# 脚本友好格式 (Porcelain)
git worktree list --porcelain

# 以 NUL 分隔的 Porcelain 格式 (处理特殊字符路径)
git worktree list --porcelain -z
```

### 删除 Worktree

```bash
# 删除干净的 worktree (无未追踪文件及未提交修改)
git worktree remove <worktree>

# 强制删除 (即使有修改或包含子模块)
git worktree remove -f <worktree>
```

### 移动 Worktree

```bash
# 移动 worktree 到新位置
git worktree move <worktree> <new-path>

# 注意：主工作树或包含子模块的链接工作树不能直接使用此命令移动。
```

### Prune（清理）

```bash
# 预览将要删除什么
git worktree prune -n

# 实际清理过期的元数据
git worktree prune

# 仅清理过期超过指定时间的
git worktree prune --expire <time>
```

### 锁定/解锁

```bash
# 锁定 worktree (防止元数据被 prune，防止被移动或删除)
git worktree lock [--reason <reason>] <worktree>

# 解锁
git worktree unlock <worktree>
```

### Repair（修复）

```bash
# 修复主仓库与链接 worktree 的双向连接
git worktree repair [<path>...]

# 典型场景：手动移动了主仓库或链接工作树后导致链接断开。
```

---

## 核心机制：Refs 共享规则

在多工作树环境中，某些引用是**全局共享**的，而某些是**每个工作树独立**的。

- **共享引用**: 所有以 `refs/` 开头的引用（如 `refs/heads/`, `refs/tags/`, `refs/remotes/`）。
- **独立引用**: 伪引用（Pseudo refs）如 `HEAD`, `FETCH_HEAD`, `ORIG_HEAD`, `CHERRY_PICK_HEAD` 等。
- **例外**: `refs/bisect/`, `refs/worktree/`, `refs/rewritten/` 是每工作树独立的。

### 跨工作树访问 Refs
可以通过特殊路径访问其他工作树的独立引用：
- `main-worktree/HEAD`: 访问主工作树的 HEAD。
- `worktrees/<id>/HEAD`: 访问特定 ID 链接工作树的 HEAD。

---

## 配置收敛建议

为了在多工作树间保持配置一致性：
- **全局配置**: 修改 `.git/config`（默认共享）。
- **特定工作树配置**: 开启 `extensions.worktreeConfig` 后，可使用 `git config --worktree` 修改独立配置（如 `core.sparseCheckout`）。

---

## 详细命令说明

### 1. git worktree add

**语法**:
```bash
git worktree add [-f] [--detach] [--checkout] [--lock [--reason <string>]]
               [--orphan] [(-b | -B) <new-branch>] <path> [<commit-ish>]
```

**高级参数说明**:
- `--orphan`: 创建一个空的工作树和索引，关联到一个全新的无提交分支。适用于全新的开始。
- `--relative-paths`: 使用相对路径链接工作树。这在工作树和主仓库可能整体移动的环境中非常有用。可以通过 `worktree.useRelativePaths = true` 全局开启。
- `--guess-remote`: 如果未指定分支且本地不存在，尝试匹配远程追踪分支。
- `-f` / `--force`: 强制创建，即使目标目录已存在或分支已被检出。
- `--detach`: 创建分离式 HEAD（不在任何分支上），适合临时实验。

**使用场景**:

**场景1: 从现有分支创建**
```bash
git worktree add /opt/claude/mystocks_phase6_cache phase6-cache-optimization
```

**场景2: 创建新分支**
```bash
git worktree add -b phase6-new-feature /opt/claude/mystocks_new_feature
```

**场景3: 创建孤儿分支 (全新开始)**
```bash
git worktree add --orphan phase6-clean-slate /opt/claude/mystocks_clean
```

### 2. git worktree list

**语法**:
```bash
git worktree list [-v | --porcelain [-z]]
```

**参数说明**:
- `-v`: 显示详细信息（包括 HEAD 提交哈希、是否锁定、是否可清理）。
- `--porcelain`: 脚本友好格式（便于解析）。
- `-z`: 以 NUL 分隔的 Porcelain 格式 (处理特殊字符路径)。

**Porcelain 输出示例**:
```
worktree /path/to/bare-source
bare

worktree /path/to/linked-worktree
HEAD abcd1234...
branch refs/heads/master
```

### 3. git worktree repair

**语法**:
```bash
git worktree repair [<path>...]
```

**功能**:
修复工作树管理文件，如果它们因外部因素（如手动移动目录）而损坏或过时。

**何时需要 repair**:
- **主仓库移动**: 链接工作树将无法找到主仓库。**解决方案**: 在主仓库运行 `git worktree repair`。
- **链接工作树手动移动**: 未使用 `move` 命令而是手动 `mv` 目录。**解决方案**: 在移动后的工作树内运行 `git worktree repair`。
- **双向损坏**: 两者都手动移动了。**解决方案**: 在主仓库运行 `repair` 并提供所有链接工作树的新路径作为参数：`git worktree repair /new/path/to/worktree1 /new/path/to/worktree2`。

### 4. git worktree remove & prune

**Remove**:
- `git worktree remove <worktree>`: 删除工作树。
- `-f`: 强制删除（即使有未提交的修改或未追踪的文件）。

**Prune**:
- `git worktree prune`: 清理 `$GIT_DIR/worktrees` 中指向不存在目录的过期元数据。
- `--expire <time>`: 仅清理过期超过指定时间的记录。

### 5. git worktree lock & unlock

**Lock**:
- `git worktree lock <worktree>`: 防止 Worktree 被清理或移动。
- `--reason <string>`: 锁定原因（如“在移动硬盘上”）。

**Unlock**:
- `git worktree unlock <worktree>`: 解除锁定。

---

## 🔧 配置 (Configuration)

为了在多工作树间保持配置的灵活性，Git 提供了 `extensions.worktreeConfig`。

### 启用独立配置
```bash
git config extensions.worktreeConfig true
```

启用后，特定工作树的配置将存储在 `.git/worktrees/<id>/config.worktree` 中，而不是全局的 `.git/config`。

**使用场景**:
- **Sparse Checkout**: 某些 Worktree 只需要仓库的一部分。
- **特定 Email**: 在某个 Worktree 使用不同的提交邮箱。

**设置命令**:
```bash
# 在特定工作树下执行
git config --worktree user.email "worker-cli-1@example.com"
```

---

## Git别名系统

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
- `../../.FILE_OWNERSHIP` - 文件归属权映射（所有worktree的权威来源）
- [多 CLI 协作管理手册 (Master Guide)](../README.md) - 体系总纲
- [主CLI工作规范](./MAIN_CLI_WORKFLOW.md) - 主CLI工作流程
- [Worker CLI工作流程](./WORKER_CLI_GUIDE.md) - Worker CLI工作流程
- [协作冲突预防](./CONFLICT_PREVENTION.md) - 冲突处理

### 任务管理文档
- [任务文档模板](./templates/TASK_TEMPLATE.md) - 任务文档命名规范：TASK.md → TASK-REPORT.md → TASK-*-REPORT.md

### 其他配置
- [Git远程名称标准](./GIT_REMOTE_NAME_STANDARD.md) - 远程配置规范（统一使用origin）

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

**版本**: v2.1
**最后更新**: 2026-02-13
**维护者**: Main CLI
