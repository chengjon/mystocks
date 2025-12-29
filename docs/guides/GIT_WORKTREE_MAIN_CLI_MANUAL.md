# Git Worktree 主CLI 参考手册

**版本**: 1.0
**适用场景**: Phase 6 多CLI协作管理
**创建者**: Main CLI (Manager)
**创建时间**: 2025-12-28

---

## 📚 目录

1. [核心概念](#核心概念)
2. [常用命令速查](#常用命令速查)
3. [Phase 6 工作流程](#phase-6-工作流程)
4. [自动化脚本模板](#自动化脚本模板)
5. [故障排查](#故障排查)
6. [最佳实践](#最佳实践)

---

## 核心概念

### 什么是 Git Worktree？

Git Worktree 允许在**同一个仓库**中创建**多个独立的工作目录**，每个目录可以签出不同的分支。

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

**重要文件**:
- 每个链接 worktree 的 `.git` 文件指向元数据目录
- 元数据路径: `$GIT_DIR/worktrees/<worktree-name>/`
- 共享内容: `refs/`, `objects/`
- 独立内容: `HEAD`, `index`, 工作目录文件

---

## 常用命令速查

### 1. 创建 Worktree

```bash
# 基本语法
git worktree add <路径> [<分支名>] [<起点>]

# 常用示例

# 1. 从现有分支创建 worktree
git worktree add /opt/claude/mystocks_phase6_cache phase6-cache-optimization

# 2. 创建新分支并签出
git worktree add -b phase6-new-feature /opt/claude/mystocks_new_feature

# 3. 创建分离式 HEAD (用于实验)
git worktree add --detach /opt/claude/mystocks_experiment

# 4. 从远程分支创建
git worktree add /opt/claude/mystocks_feature origin/feature-branch

# 5. 创建并锁定 (用于便携设备)
git worktree add --lock /opt/claude/mystocks_portable feature-x
```

### 2. 列出 Worktree

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

### 3. 删除 Worktree

```bash
# 删除干净的 worktree
git worktree remove /opt/claude/mystocks_phase6_cache

# 强制删除 (即使有未提交的修改)
git worktree remove -f /opt/claude/mystocks_phase6_e2e

# 强制删除锁定的 worktree
git worktree remove --force --force /opt/claude/mystocks_locked
```

### 4. 移动 Worktree

```bash
# 移动 worktree 到新位置
git worktree move /opt/claude/old /opt/claude/new

# 移动并重命名
git worktree move mystocks_phase6_e2e mystocks_e2e_testing_new
```

### 5. Prune (清理)

```bash
# 预览将要删除什么
git worktree prune -n

# 实际清理
git worktree prune

# 详细输出
git worktree prune -v

# 仅清理过期超过指定时间的
git worktree prune --expire 3.months.ago
```

### 6. 锁定/解锁

```bash
# 锁定 worktree (防止被 prune)
git worktree lock /opt/claude/mystocks_portable

# 锁定并注明原因
git worktree lock --reason "存储在便携设备上" /opt/claude/mystocks_portable

# 解锁
git worktree unlock /opt/claude/mystocks_portable
```

### 7. Repair (修复)

```bash
# 修复主仓库与链接 worktree 的连接
git worktree repair

# 修复特定 worktree
git worktree repair /path/to/broken/worktree
```

---

## Phase 6 工作流程

### 场景：多CLI并行协作

**目标**: 4个 Worker CLI 同时在不同分支工作，互不干扰。

### 步骤 1: 初始化阶段 (T+0h)

```bash
#!/bin/bash
# 主CLI初始化脚本

MAIN_REPO="/opt/claude/mystocks_spec"
cd "$MAIN_REPO"

# 1. 确保在 main 分支
git checkout main
git pull origin main

# 2. 创建 4 个 worktree
git worktree add /opt/claude/mystocks_phase6_monitor phase6-monitoring-verification
git worktree add /opt/claude/mystocks_phase6_e2e phase6-e2e-testing
git worktree add /opt/claude/mystocks_phase6_cache phase6-cache-optimization
git worktree add /opt/claude/mystocks_phase6_docs phase6-documentation

# 3. 验证所有 worktree
git worktree list

# 4. 在每个 worktree 创建 README.md 任务文档
for worktree in /opt/claude/mystocks_phase6_*; do
    cp "$MAIN_REPO/docs/templates/CLI_README.md" "$worktree/README.md"
done
```

### 步骤 2: 监控阶段 (T+0h → T+10h)

```bash
#!/bin/bash
# 主CLI监控脚本

check_cli_progress() {
    local cli_name=$1
    local worktree_path=$2
    local branch=$3

    echo "🔍 检查 $cli_name 进度..."

    # 1. 检查最新提交
    latest_commit=$(cd "$worktree_path" && git log -1 --oneline)
    echo "   最新提交: $latest_commit"

    # 2. 检查未提交的修改
    uncommitted=$(cd "$worktree_path" && git status --short | wc -l)
    echo "   未提交修改: $uncommitted 个文件"

    # 3. 检查分支状态
    branch_status=$(cd "$worktree_path" && git branch --show-current)
    echo "   当前分支: $branch_status"

    # 4. 统计提交数量
    commit_count=$(cd "$worktree_path" && git rev-list --count main ^origin/main)
    echo "   新增提交: $commit_count 个"
}

# 定期检查所有 CLI
while true; do
    echo "=== $(date) ==="

    check_cli_progress "CLI-1 (监控验证)" \
        "/opt/claude/mystocks_phase6_monitor" \
        "phase6-monitoring-verification"

    check_cli_progress "CLI-2 (E2E测试)" \
        "/opt/claude/mystocks_phase6_e2e" \
        "phase6-e2e-testing"

    check_cli_progress "CLI-3 (缓存优化)" \
        "/opt/claude/mystocks_phase6_cache" \
        "phase6-cache-optimization"

    check_cli_progress "CLI-4 (文档)" \
        "/opt/claude/mystocks_phase6_docs" \
        "phase6-documentation"

    echo ""
    sleep 1800  # 每 30 分钟检查一次
done
```

### 步骤 3: 集成阶段 (T+9h)

```bash
#!/bin/bash
# 主CLI集成脚本

# 1. 验证所有 CLI 完成状态
verify_cli_completion() {
    local cli_path=$1
    local branch=$2

    echo "验证 $cli_path..."

    # 检查分支是否合并或可合并
    cd "$cli_path"

    # 检查是否有未提交的修改
    if ! git diff-index --quiet HEAD --; then
        echo "❌ 错误: 有未提交的修改"
        return 1
    fi

    # 检查是否在正确的分支
    current_branch=$(git branch --show-current)
    if [ "$current_branch" != "$branch" ]; then
        echo "⚠️  警告: 当前在 $current_branch，应该在 $branch"
    fi

    echo "✅ 验证通过"
}

# 2. 验证所有 worktree
verify_cli_completion "/opt/claude/mystocks_phase6_monitor" "phase6-monitoring-verification"
verify_cli_completion "/opt/claude/mystocks_phase6_e2e" "phase6-e2e-testing"
verify_cli_completion "/opt/claude/mystocks_phase6_cache" "phase6-cache-optimization"
verify_cli_completion "/opt/claude/mystocks_phase6_docs" "phase6-documentation"

# 3. 合并所有分支到 main
cd /opt/claude/mystocks_spec
git checkout main

# 按顺序合并分支
for branch in \
    phase6-monitoring-verification \
    phase6-e2e-testing \
    phase6-cache-optimization \
    phase6-documentation
do
    echo "合并 $branch..."
    git merge --no-ff -m "Merge $branch into main" $branch
done

# 4. 清理 worktree
git worktree list | awk '/phase6/ {print $1}' | while read path; do
    git worktree remove "$path"
done

echo "✅ 集成完成！"
```

---

## 自动化脚本模板

### 模板 1: Worktree 状态检查

```bash
#!/bin/bash
# check_worktree_status.sh - 检查所有 worktree 状态

WORKTREES=(
    "phase6-monitoring-verification:/opt/claude/mystocks_phase6_monitor"
    "phase6-e2e-testing:/opt/claude/mystocks_phase6_e2e"
    "phase6-cache-optimization:/opt/claude/mystocks_phase6_cache"
    "phase6-documentation:/opt/claude/mystocks_phase6_docs"
)

echo "📊 Git Worktree 状态报告"
echo "======================"

for worktree_info in "${WORKTREES[@]}"; do
    IFS=: read -r branch path <<< "$worktree_info"

    echo ""
    echo "🔷 $branch"
    echo "   路径: $path"

    if [ -d "$path" ]; then
        # 检查工作目录状态
        cd "$path"

        # 当前提交
        commit_hash=$(git rev-parse --short HEAD)
        commit_msg=$(git log -1 --pretty=format:"%s")
        echo "   提交: $commit_hash - $commit_msg"

        # 分支状态
        branch_name=$(git branch --show-current)
        echo "   分支: $branch_name"

        # 文件状态
        status=$(git status --short | wc -l)
        if [ $status -eq 0 ]; then
            echo "   状态: ✅ 干净"
        else
            echo "   状态: ⚠️  有 $status 个未提交文件"
        fi

        # 与主分支的差异
        ahead=$(git rev-list --count main ^origin/main 2>/dev/null || echo "0")
        if [ $ahead -gt 0 ]; then
            echo "   领先主分支: $ahead 个提交"
        fi
    else
        echo "   状态: ❌ Worktree 不存在"
    fi
done

echo ""
echo "======================"
echo "📋 所有 worktree 列表:"
git worktree list
```

### 模板 2: 批量创建 Worktree

```bash
#!/bin/bash
# create_worktrees.sh - 批量创建 worktree

MAIN_REPO="/opt/claude/mystocks_spec"
cd "$MAIN_REPO" || exit 1

# 定义 worktree 配置
declare -A WORKTREES
WORKTREES=(
    ["phase6-monitor"]="phase6-monitoring-verification"
    ["phase6-e2e"]="phase6-e2e-testing"
    ["phase6-cache"]="phase6-cache-optimization"
    ["phase6-docs"]="phase6-documentation"
)

echo "🚀 创建 Phase 6 Worktree"
echo "===================="

# 确保在 main 分支
git checkout main >/dev/null 2>&1
git pull origin main >/dev/null 2>&1

for key in "${!WORKTREES[@]}"; do
    branch="${WORKTREES[$key]}"
    path="/opt/claude/mystocks_$key"

    echo "创建: $key"
    echo "  分支: $branch"
    echo "  路径: $path"

    # 检查是否已存在
    if git worktree list | grep -q "$path"; then
        echo "  ⚠️  Worktree 已存在，跳过"
        continue
    fi

    # 创建 worktree
    if git worktree add "$path" "$branch" 2>/dev/null; then
        echo "  ✅ 创建成功"

        # 在 worktree 中创建 README
        cat > "$path/README.md" <<EOF
# Phase 6: $key

**分支**: \`$branch\`
**Worktree**: \`$path\`
**创建时间**: $(date)

## 任务目标

[待补充]

## 完成标准

- [ ] 任务完成
- [ ] 测试通过
- [ ] 文档更新

## 提交规范

\`\`bash
git commit -m "feat($key): 完成任务描述"
\`\`
EOF
    else
        echo "  ❌ 创建失败"
    fi
    echo ""
done

echo "===================="
echo "✅ Worktree 创建完成"
echo ""
git worktree list
```

### 模板 3: 自动提交监控

```bash
#!/bin/bash
# monitor_commits.sh - 监控各 CLI 的提交活动

LOG_FILE="/tmp/phase6_commit_monitor.log"
check_interval=600  # 10 分钟检查一次

echo "🔍 启动 Phase 6 提交监控" | tee -a "$LOG_FILE"
echo "检查间隔: $check_interval 秒" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"

declare -A last_commits

# 初始化 last_commits
for cli in monitor e2e cache docs; do
    worktree="/opt/claude/mystocks_phase6_$cli"
    if [ -d "$worktree" ]; then
        last_commits[$cli]=$(cd "$worktree" && git rev-parse HEAD)
    fi
done

while true; do
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    for cli in monitor e2e cache docs; do
        worktree="/opt/claude/mystocks_phase6_$cli"

        if [ ! -d "$worktree" ]; then
            continue
        fi

        cd "$worktree"
        current_commit=$(git rev-parse HEAD)

        # 检查是否有新提交
        if [ "${last_commits[$cli]}" != "$current_commit" ]; then
            # 获取提交信息
            commit_hash=$(git rev-parse --short HEAD)
            commit_msg=$(git log -1 --pretty=format:"%s")
            commit_author=$(git log -1 --pretty=format:"%an")
            commit_time=$(git log -1 --pretty=format:"%cr" --date=local)

            # 记录到日志
            {
                echo "[$timestamp] 🆕 新提交检测: $cli"
                echo "   Worktree: $worktree"
                echo "   提交: $commit_hash"
                echo "   作者: $commit_author"
                echo "   消息: $commit_msg"
                echo "   时间: $commit_time"
                echo ""
            } | tee -a "$LOG_FILE"

            # 更新 last_commits
            last_commits[$cli]=$current_commit
        fi
    done

    sleep $check_interval
done
```

### 模板 4: Worktree 清理脚本

```bash
#!/bin/bash
# cleanup_worktrees.sh - 清理已完成的 worktree

DRY_RUN=false
FORCE=false

# 解析参数
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "未知选项: $1"
            exit 1
            ;;
    esac
done

echo "🧹 Phase 6 Worktree 清理工具"
echo "===================="

if [ "$DRY_RUN" = true ]; then
    echo "🔍 预览模式 (不会实际删除)"
fi

# 定义已完成的工作树
COMPLETED_WORKTREES=(
    "/opt/claude/mystocks_phase6_cache"
)

cd /opt/claude/mystocks_spec

for worktree in "${COMPLETED_WORKTREES[@]}"; do
    if ! git worktree list | grep -q "$worktree"; then
        echo "⚠️  Worktree 不存在: $worktree"
        continue
    fi

    echo "检查: $worktree"

    # 检查是否有未提交的修改
    cd "$worktree"
    if ! git diff-index --quiet HEAD --; then
        if [ "$FORCE" = true ]; then
            echo "  ⚠️  强制删除 (有未提交的修改)"
        else
            echo "  ❌ 跳过 (有未提交的修改)"
            continue
        fi
    fi

    # 检查是否有未跟踪的文件
    untracked=$(git ls-files --others --exclude-standard | wc -l)
    if [ $untracked -gt 0 ]; then
        if [ "$FORCE" = true ]; then
            echo "  ⚠️  强制删除 (有 $untracked 个未跟踪文件)"
        else
            echo "  ❌ 跳过 (有 $untracked 个未跟踪文件)"
            continue
        fi
    fi

    # 删除 worktree
    cd /opt/claude/mystocks_spec
    if [ "$DRY_RUN" = true ]; then
        echo "  [预览] 将删除: $worktree"
    else
        echo "  ✅ 删除: $worktree"
        git worktree remove "$worktree"
    fi
    echo ""
done

echo "===================="

# 列出剩余 worktree
echo "📋 剩余 worktree:"
git worktree list

# 建议清理
echo ""
echo "💡 建议: 运行 'git worktree prune' 清理元数据"
```

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

---

## 最佳实践

### ⭐ Phase 6 实践经验 - 关键成功因素

基于 Phase 6 多CLI协作项目（4个CLI，10小时完成，65.5%时间节省），以下是关键成功经验：

#### 🎯 成功经验1: 进度监控的最佳实践

**发现问题**: 早期缺乏系统化监控，CLI-2阻塞3小时才被发现

**解决方案**: 建立自动化进度监控机制

```bash
#!/bin/bash
# 自动化进度监控脚本（每小时运行）

check_cli_progress() {
    local cli_name=$1
    local worktree_path=$2
    local branch=$3

    echo "🔍 检查 $cli_name 进度..."

    # 1. 检查最新提交
    latest_commit=$(cd "$worktree_path" && git log -1 --oneline)
    echo "   最新提交: $latest_commit"

    # 2. 检查未提交的修改
    uncommitted=$(cd "$worktree_path" && git status --short | wc -l)
    echo "   未提交修改: $uncommitted 个文件"

    # 3. 检查分支状态
    branch_status=$(cd "$worktree_path" && git branch --show-current)
    echo "   当前分支: $branch_status"

    # 4. 统计提交数量
    commit_count=$(cd "$worktree_path" && git rev-list --count main ^origin/main)
    echo "   新增提交: $commit_count 个"

    # 5. 检查是否有阻塞问题
    if [ $uncommitted -gt 50 ]; then
        echo "   ⚠️  警告: 大量未提交文件，可能遇到问题"
    fi
}

# 定期检查所有 CLI
while true; do
    echo "=== $(date) ==="

    check_cli_progress "CLI-1 (监控验证)" \
        "/opt/claude/mystocks_phase6_monitor" \
        "phase6-monitoring-verification"

    check_cli_progress "CLI-2 (E2E测试)" \
        "/opt/claude/mystocks_phase6_e2e" \
        "phase6-e2e-testing"

    check_cli_progress "CLI-3 (缓存优化)" \
        "/opt/claude/mystocks_phase6_cache" \
        "phase6-cache-optimization"

    check_cli_progress "CLI-4 (文档)" \
        "/opt/claude/mystocks_phase6_docs" \
        "phase6-documentation"

    echo ""
    sleep 3600  # 每小时检查一次
done
```

**监控频率建议**:
- ✅ 每小时：检查所有worktree状态
- ✅ 每2小时：生成结构化进度报告
- ✅ 里程碑时间点：T+2h, T+6h, T+8h, T+9h

---

#### 🎯 成功经验2: 优先级动态调整策略

**发现问题**: CLI-2初始优先级不合理，导致阻塞

**解决方案**: 建立优先级评估模型

```python
def calculate_priority(task):
    """
    任务优先级计算模型

    Args:
        task: 任务对象

    Returns:
        int: 优先级分数（1-10，10最高）
    """
    score = 0

    # 因素1: 依赖数量（被依赖的任务优先）
    if task.dependents_count > 0:
        score += min(task.dependents_count * 2, 5)

    # 因素2: 预计时间（短任务优先）
    if task.estimated_time < 2:
        score += 3
    elif task.estimated_time < 4:
        score += 2

    # 因素3: 阻塞状态（阻塞任务最高优先级）
    if task.is_blocked:
        score += 5

    # 因素4: 依赖数量（无依赖任务优先）
    if task.dependencies_count == 0:
        score += 2

    return min(score, 10)
```

**优先级评估表**:

| 任务类型 | 依赖数 | 预计时间 | 优先级建议 | 说明 |
|---------|--------|----------|------------|------|
| 无依赖短任务 | 0 | <2h | 9-10 | 最高优先级，快速完成 |
| 无依赖长任务 | 0 | >4h | 7-8 | 并行处理 |
| 被依赖任务 | >0 | - | 10 | 解除阻塞，优先级最高 |
| 阻塞任务 | - | - | 10 | 立即响应 |
| 有依赖任务 | >0 | - | 4-6 | 等待依赖完成 |

**Phase 6优化结果**:
- CLI-2优先级调整（4→5→3）
- 节省时间：63分钟
- 杠杆率：206.7%（投入1.5h，节省3.1h）

---

#### 🎯 成功经验3: Git提交的标准化

**发现问题**: CLI提交信息格式不统一

**解决方案**: 使用HEREDOC格式化，确保多行提交信息正确

```bash
# 标准化的Git提交格式（推荐）
git commit -m "$(cat <<'EOF'
type(scope): description

Detailed explanation...

- Bullet point 1
- Bullet point 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"

# 实际示例（Phase 6使用）
git commit -m "$(cat <<'EOF'
docs: Add Phase 6 final completion report

Phase 6 多CLI并行开发100%完成并成功合并！

核心成就:
- ✅ 4/4 CLIs 100%完成
- ✅ 11次Git提交全部成功
- ✅ ~700+文件修改完成
- ✅ ~30,000+行代码变更
- ✅ 100% E2E测试通过 (18/18)
- ✅ Pylint 9.32/10 (最高评级)
- ✅ 65.5%时间节省 (并行化效率)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>
EOF
)"
```

**提交类型（type）**:
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `chore`: 构建/工具链更新
- `refactor`: 重构
- `test`: 测试相关

**提交范围（scope）**:
- `phase6`: Phase 6相关
- `monitoring`: 监控系统
- `cache`: 缓存优化
- `e2e`: E2E测试
- `docs`: 文档

---

#### 🎯 成功经验4: 合并冲突的预防

**发现问题**: Phase 6合并时出现7个文件冲突

**解决方案**: 建立文件所有权规则

**文件所有权规则**:

| 文件类型 | 所有权优先 | 负责CLI | 冲突解决策略 |
|---------|-----------|---------|-------------|
| `README.md` | 文档专业分支 | CLI-4 | 接受CLI-4版本 |
| 监控配置文件 | 监控专业分支 | CLI-1 | 接受CLI-1版本 |
| 测试代码 | 测试专业分支 | CLI-2 | 接受CLI-2版本 |
| 业务代码 | 最新修复版本 | - | 接受最新修复版本 |
| API文档 | 文档专业分支 | CLI-4 | 接受CLI-4版本 |

**Phase 6实际冲突**:

1. **README.md** (3次冲突) - 通过接受文档专业分支版本解决
2. **monitoring-stack/config/loki-config.yaml** - 接受CLI-1版本
3. **monitoring-stack/config/tempo-config.yaml** - 接受CLI-1版本
4. **tests/e2e/test_architecture_optimization_e2e.py** - 接受CLI-2版本
5. **src/adapters/tdx/kline_data_service.py** - 接受CLI-1版本

**合并策略**:
```bash
# 按顺序合并分支（最小化冲突）
git merge --no-ff --no-edit phase6-cache-optimization  # 先合并CLI-3（最快）
git merge --no-ff --no-edit phase6-documentation        # 再合并CLI-4（文档）
git merge --no-ff --no-edit phase6-e2e-testing          # 再合并CLI-2（测试）
git merge --no-ff --no-edit phase6-monitoring-verification  # 最后合并CLI-1（监控）
```

---

#### 🎯 成功经验5: 问题响应的SLA标准

**发现问题**: CLI-2阻塞3小时才被发现，响应时间过长

**解决方案**: 建立3级问题响应机制

**问题响应SLA标准**:

| 级别 | 定义 | 响应时间 | 处理方式 | 示例 |
|------|------|----------|----------|------|
| 🟢 信息级 | 不影响工作的小问题 | 4h内 | Worker CLI独立处理 | 代码风格问题 |
| 🟡 警告级 | 可能影响进度 | 1h内 | Worker尝试解决，无法解决时报告 | 部分测试失败 |
| 🔴 阻塞级 | 完全无法继续工作 | 15min内 | 立即报告主CLI，请求帮助 | 服务启动失败 |

**问题报告模板**:
```markdown
## 进度更新 (T+Xh)

### ✅ 已完成
- 任务1完成
- 任务2完成

### ⚠️ 阻塞问题
**问题描述**: 后端服务无法启动
**错误信息**: ModuleNotFoundError: No module named 'web.backend.app'
**严重程度**: 🔴 阻塞级
**已尝试**:
- 检查import路径
- 尝试修改为相对导入
**请求帮助**: 需要主CLI提供正确的配置
```

**Phase 6响应时间**:
- 🟢 信息级: 平均2小时响应
- 🟡 警告级: 平均30分钟响应
- 🔴 阻塞级: 平均15分钟响应

---

### 1. Worktree 命名规范

```bash
# 推荐的命名模式
<project>-<purpose>-<type>

# Phase 6 实例
mystocks_phase6_monitor    # ✅ 清晰
mystocks_phase6_e2e        # ✅ 简洁
mystocks_phase6_cache       # ✅ 描述性

# 不推荐
test                       # ❌ 太模糊
w1                         # ❌ 无意义
temp                       # ❌ 不够具体
```

### 2. 分支管理策略

```bash
# 使用功能分支命名
phase6-<cli-name>-<task>

# 实例
phase6-monitor-verification
phase6-e2e-testing
phase6-cache-optimization
phase6-documentation

# 确保分支名唯一，避免冲突
```

### 3. Worktree 卫生

```bash
# 定期清理过期的 worktree
git worktree prune --expire 1.month

# 定期检查 worktree 状态
git worktree list -v

# 定期锁定便携设备上的 worktree
git worktree lock --reason "在便携设备上" /path/to/portable
```

### 4. 并行开发注意事项

```bash
# ❌ 不要做的事

# 1. 不要在多个 worktree 中同时修改同一文件
# 可能导致合并冲突

# 2. 不要忘记切换到正确的 worktree
# 使用 cd 或自动化脚本

# 3. 不要在 worktree 中执行影响其他 worktree 的操作
# 如 git clean -fdx

# ✅ 推荐做的事

# 1. 定期同步主分支
git fetch origin main

# 2. 使用脚本自动化重复任务
# 如创建、删除、监控脚本

# 3. 为每个 worktree 创建独立的 README
# 记录任务目标和完成标准
```

### 5. CI/CD 集成

```bash
# GitHub Actions 示例: 在所有 worktree 中运行测试
name: Test All Worktrees

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        worktree:
          - phase6-monitor
          - phase6-e2e
          - phase6-cache
          - phase6-docs

    steps:
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0

      - name: Test worktree ${{ matrix.worktree }}
        run: |
          git worktree list
          cd /opt/claude/mystocks_${{ matrix.worktree }}
          pytest tests/
```

---

## Phase 6 专用工作流程

### 快速启动 Phase 6

```bash
#!/bin/bash
# Phase 6 快速启动脚本

set -e

echo "🚀 Phase 6 多CLI协作系统"
echo "===================="

# 1. 创建所有 worktree
./scripts/create_phase6_worktrees.sh

# 2. 启动提交监控
./scripts/monitor_commits.sh &

# 3. 通知各 CLI 开始工作
echo "✅ Worktree 已就绪"
echo ""
echo "📋 Worker CLI 任务分配:"
echo "   CLI-1: cd /opt/claude/mystocks_phase6_monitor"
echo "   CLI-2: cd /opt/claude/mystocks_phase6_e2e"
echo "   CLI-3: cd /opt/claude/mystocks_phase6_cache"
echo "   CLI-4: cd /opt/claude/mystocks_phase6_docs"
echo ""
echo "主CLI 监控脚本已启动，日志: /tmp/phase6_commit_monitor.log"
```

### 进度汇总报告

```bash
#!/bin/bash
# 生成进度汇总报告

REPORT_FILE="/tmp/phase6_progress_report.md"

echo "# Phase 6 进度报告" > "$REPORT_FILE"
echo "**生成时间**: $(date)" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

echo "## CLI 完成状态" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

for cli in monitor e2e cache docs; do
    worktree="/opt/claude/mystocks_phase6_$cli"

    echo "### $cli" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"

    if [ -d "$worktree" ]; then
        cd "$worktree"

        # 提交统计
        commits=$(git rev-list --count main ^origin/main 2>/dev/null || echo "0")

        # 最新提交
        latest=$(git log -1 --pretty=format:"%h - %s" 2>/dev/null || echo "无提交")

        echo "- **最新提交**: $latest" >> "$REPORT_FILE"
        echo "- **新增提交**: $commits 个" >> "$REPORT_FILE"
        echo "- **状态**: $(git status --short | wc -l) 个未提交文件" >> "$REPORT_FILE"
    else
        echo "- **状态**: Worktree 不存在" >> "$REPORT_FILE"
    fi

    echo "" >> "$REPORT_FILE"
done

echo "✅ 报告已生成: $REPORT_FILE"
cat "$REPORT_FILE"
```

---

## 参考资料

### 官方文档
- [git-worktree 中文文档](https://git-scm.com/docs/git-worktree/zh_HANS-CN)
- [Git Worktree 官方文档](https://git-scm.com/docs/git-worktree)

### 社区资源
- [Git Worktree：更优雅的多分支开发方式](https://zhengw-tech.com/2025/10/08/git-worktree/)
- [利用Git Worktree 实现无畏并行开发工作流](https://zhuanlan.zhihu.com/p/1957615857908823086)
- [Parallel Development with ClaudeCode and Git Worktrees](https://medium.com/@ooi_yee_fei/parallel-ai-development-with-git-worktrees-f2524afc3e33)
- [如何在 Claude Code 中使用 Git Worktree](https://claudecode.io/tw/blog/how-to-use-git-worktree-in-claude-code)

### Phase 6 项目文档
- `/opt/claude/mystocks_spec/docs/reports/PHASE6_MULTI_CLI_COORDINATION.md`
- `/opt/claude/mystocks_spec/docs/reports/PHASE6_PROGRESS_REPORT_CURRENT.md`

---

**附录**: 常用 Git 命令参考
```bash
# 列出所有 worktree
git worktree list

# 查看特定 worktree 信息
git worktree list | grep phase6

# 强制删除 worktree
git worktree remove -f /path/to/worktree

# Prune 元数据
git worktree prune

# 查看详细状态
git worktree list -v

# 脚本友好格式
git worktree list --porcelain

# 修复损坏的 worktree
git worktree repair /path/to/worktree
```

---

**版本**: 1.0
**维护者**: Main CLI (Manager)
**最后更新**: 2025-12-28
