# Multi-CLI Worktree 运维韧性补充手册

> **版本**: v3.2  
> **定位**: 补充现有 6 份核心文档中未覆盖但在实战中至关重要的方法与工作  
> **适用**: Git Worktree 多 CLI 协作体系 v3.2  
> **最后更新**: 2026-03-05

---

## 目录

1. [故障恢复与回滚](#1-故障恢复与回滚)
2. [紧急制动机制](#2-紧急制动机制)
3. [资源争用与容量规划](#3-资源争用与容量规划)
4. [密钥与环境变量管理](#4-密钥与环境变量管理)
5. [数据库迁移协调](#5-数据库迁移协调)
6. [跨 Worktree 集成测试](#6-跨-worktree-集成测试)
7. [端口与服务冲突管理](#7-端口与服务冲突管理)
8. [Worktree 生命周期状态机](#8-worktree-生命周期状态机)
9. [AI CLI 工具差异化处理](#9-ai-cli-工具差异化处理)
10. [通信协议容错](#10-通信协议容错)
11. [审计追踪与结构化日志](#11-审计追踪与结构化日志)
12. [事后复盘模板](#12-事后复盘模板)
13. [v3.2 治理门禁韧性](#13-v32-治理门禁韧性)

---

## 1. 故障恢复与回滚

现有文档覆盖了正常流程，但没有回答："出了事怎么办？"

### 1.1 Worker 推送了损坏代码

```bash
# 1. 立即在 main worktree 标记当前安全点
git tag safe/before-merge-$(date +%Y%m%d-%H%M)

# 2. 如果已合并，回滚合并
git revert -m 1 <merge_commit_hash>

# 3. 如果尚未合并，拒绝该分支
echo "❌ BLOCKED: branch worker/cli-3-feature 未通过验收" >> .multi-cli-tasks/MERGE_LOG.md
```

### 1.2 Worker Worktree 损坏

```bash
# 诊断
git worktree list  # 检查是否标记为 prunable
cd .worktrees/<name> && git status  # 检查 index 状态

# 轻度损坏：修复
git worktree repair

# 重度损坏：重建
git worktree remove <name> --force
git worktree add .worktrees/<name> -b worker/<name> origin/main
# 重新分发 TASK.md
cp .multi-cli-tasks/<name>/TASK.md .worktrees/<name>/TASK.md
```

### 1.3 Main CLI 中途崩溃

这是最危险的场景——指挥官倒下了。

```
恢复步骤：
1. 不要 panic，所有 worker worktree 是独立的，不受影响
2. 新开一个 CLI 会话，cd 到主仓库
3. 运行 git worktree list 确认所有 worktree 状态
4. 检查 .multi-cli-tasks/ 下的 TASK-REPORT.md 确认各 worker 进度
5. 从最后一个 safe/ tag 恢复（如有需要）
6. 继续调度流程
```

### 1.4 回滚决策矩阵

| 场景 | 影响范围 | 回滚方式 | 恢复时间 |
|------|---------|---------|---------|
| Worker 单文件错误 | 低 | `git checkout HEAD -- <file>` | 1 分钟 |
| Worker 分支整体有问题 | 中 | 拒绝合并，Worker 重做 | 10-30 分钟 |
| 合并后发现问题 | 高 | `git revert -m 1` | 5 分钟 |
| 主分支被污染 | 严重 | `git reset --hard safe/<tag>` | 2 分钟 |
| Worktree 损坏 | 中 | 删除重建 | 5 分钟 |

---

## 2. 紧急制动机制

现有文档没有"急停按钮"。当 Worker CLI 失控（无限循环写文件、疯狂提交、吃满磁盘），需要立即制动。

### 2.1 识别失控信号

```bash
# 监控磁盘增长（每 10 秒采样）
watch -n 10 'du -sh .worktrees/*/  2>/dev/null'

# 监控 git 对象膨胀
watch -n 30 'git count-objects -vH'

# 监控进程 CPU/内存
ps aux | grep -E 'claude|codex|gemini|opencode' | grep -v grep
```

### 2.2 紧急制动操作

```bash
# 方法 1：锁定 worktree（阻止写入）
git worktree lock .worktrees/<name> --reason "Emergency: runaway process"

# 方法 2：终止 CLI 进程
# 找到进程
pgrep -f "worktree_name" 
# 优雅终止
kill -SIGTERM <pid>
# 强制终止（最后手段）
kill -9 <pid>

# 方法 3：文件系统级只读（核弹级）
chmod -R a-w .worktrees/<name>/
# 恢复时
chmod -R u+w .worktrees/<name>/
```

### 2.3 制动后检查清单

- [ ] Worker 进程已终止
- [ ] Worktree 中未提交的变更已检查（`git diff` / `git stash`）
- [ ] 无异常大文件产生（`find .worktrees/<name> -size +10M -newer <ref>`）
- [ ] Git 对象库未膨胀（`git count-objects -vH`）
- [ ] 记录事件到 `.multi-cli-tasks/INCIDENT_LOG.md`

---

## 3. 资源争用与容量规划

6 个 CLI 同时编译/测试时，机器可能扛不住。现有文档没有提及这个问题。

### 3.1 资源基线测量

```bash
# 测量单个 CLI 的资源消耗
/usr/bin/time -v <cli_command> 2>&1 | grep -E 'Maximum resident|wall clock'

# 磁盘空间预算（每个 worktree）
du -sh .worktrees/*/ | sort -h

# 推荐：在启动前检查可用资源
df -h . | awk 'NR==2{print "可用磁盘:", $4}'
free -h | awk '/Mem/{print "可用内存:", $7}'
nproc | xargs -I{} echo "CPU 核心: {}"
```

### 3.2 并发上限建议

| 资源 | 单 CLI 典型消耗 | 建议并发上限 |
|------|----------------|-------------|
| 内存 | 2-4 GB | `可用内存 / 4GB` |
| CPU | 1-2 核 | `nproc - 2`（留 2 核给系统） |
| 磁盘 | 500MB-2GB/worktree | `可用空间 / 2GB`（留 20% 余量） |
| I/O | 中等 | SSD: 6 并发可接受；HDD: 建议 ≤3 |

### 3.3 分批调度策略

当资源不足以支撑全部 Worker 同时运行时：

```
Wave 1: CLI-1, CLI-2, CLI-3（高优先级 / 无依赖）
  ↓ 等待完成
Wave 2: CLI-4, CLI-5（依赖 Wave 1 的输出）
  ↓ 等待完成
Wave 3: CLI-6（集成任务）
```

在 TASK.md 中标注波次：
```markdown
## 调度信息
- **波次**: Wave 1
- **并发组**: [CLI-1, CLI-2, CLI-3]
- **前置依赖**: 无
```

---

## 4. 密钥与环境变量管理

多个 Worktree 共享同一套密钥，但各自可能需要不同的环境配置。现有文档的 CONFLICT_PREVENTION 没有覆盖这个场景。

### 4.1 核心原则

```
.env 文件绝不提交到 git
每个 worktree 使用独立的 .env 副本
密钥变更只在主仓库操作，然后同步到 worktree
```

### 4.2 .env 同步策略

```bash
# 主仓库维护 .env.example（无真实密钥）
# .env 在 .gitignore 中

# 创建 worktree 后，同步 .env
sync_env() {
    local wt_path="$1"
    if [ -f .env ] && [ -d "$wt_path" ]; then
        cp .env "$wt_path/.env"
        echo "✅ .env synced to $wt_path"
    fi
}

# 批量同步
for wt in .worktrees/*/; do
    sync_env "$wt"
done
```

### 4.3 环境隔离（当 Worker 需要不同配置时）

```bash
# 在 worktree 中覆盖特定变量
cat > .worktrees/cli-3/.env.local << 'EOF'
# 覆盖主 .env 中的端口，避免冲突
API_PORT=8003
DB_NAME=mystocks_test_cli3
EOF
```

### 4.4 密钥轮换流程

```
1. Main CLI 更新主仓库 .env
2. 通知所有 Worker 暂停（通过 TASK.md 追加 ⚠️ ENV_UPDATE 标记）
3. 批量同步：for wt in .worktrees/*/; do cp .env "$wt/.env"; done
4. Worker 重启服务
5. 移除 ⚠️ ENV_UPDATE 标记
```

---

## 5. 数据库迁移协调

多个 Worker 可能同时修改数据库 schema。这是高风险操作，现有文档完全没有覆盖。

### 5.1 所有权规则

```
数据库迁移文件（migrations/）归 Main CLI 所有
Worker 如需修改 schema，必须：
  1. 在 TASK-REPORT.md 中声明迁移需求
  2. 等待 Main CLI 审批
  3. Main CLI 统一生成迁移文件并分发
```

### 5.2 隔离策略

```bash
# 每个 worktree 使用独立的测试数据库
# 在 .env 中配置
DB_NAME=mystocks_dev          # 主仓库
DB_NAME=mystocks_test_cli1    # CLI-1 worktree
DB_NAME=mystocks_test_cli2    # CLI-2 worktree
# ...

# 快速创建隔离数据库
create_worker_db() {
    local cli_id="$1"
    psql -c "CREATE DATABASE mystocks_test_cli${cli_id} TEMPLATE mystocks_dev;"
}
```

### 5.3 迁移合并顺序

```
1. 所有 Worker 完成开发后，Main CLI 收集所有迁移需求
2. 按依赖关系排序迁移
3. 在主仓库统一执行迁移
4. 验证后合并各 Worker 分支
```

---

## 6. 跨 Worktree 集成测试

每个 Worker 在自己的 worktree 里跑单元测试是不够的。合并前需要验证多个 Worker 的产出能协同工作。

### 6.1 集成测试时机

```
阶段 1: Worker 各自跑单元测试（Worker 职责）
阶段 2: Main CLI 在合并前创建临时集成分支（Main CLI 职责）
阶段 3: 合并后在主分支跑全量回归（Main CLI 职责）
```

### 6.2 临时集成分支策略

```bash
# Main CLI 创建集成测试分支
git checkout -b integration/round-N main

# 按依赖顺序逐个合并 Worker 分支
git merge --no-ff worker/cli-1-feature
# 跑测试
python -m pytest tests/ -x --tb=short
# 通过后继续
git merge --no-ff worker/cli-2-feature
python -m pytest tests/ -x --tb=short
# ...

# 全部通过后，fast-forward main
git checkout main
git merge integration/round-N
git branch -d integration/round-N
```

### 6.3 冲突发现后的处理

```
如果 CLI-2 的代码与 CLI-1 冲突：
1. 不要在集成分支上修复（污染集成环境）
2. 记录冲突详情到 .multi-cli-tasks/CONFLICT_LOG.md
3. 将冲突信息写入对应 Worker 的 TASK.md（追加修复任务）
4. Worker 在自己的 worktree 中修复后重新推送
5. Main CLI 重新执行集成测试
```

---

## 7. 端口与服务冲突管理

多个 Worker 同时启动 dev server 会端口冲突。

### 7.1 端口分配表

```
| CLI    | API 端口 | 前端端口 | 数据库端口 | 调试端口 |
|--------|---------|---------|-----------|---------|
| Main   | 8000    | 3000    | 5432      | 9229    |
| CLI-1  | 8001    | 3001    | 5433      | 9230    |
| CLI-2  | 8002    | 3002    | 5434      | 9231    |
| CLI-3  | 8003    | 3003    | 5435      | 9232    |
| CLI-4  | 8004    | 3004    | 5436      | 9233    |
| CLI-5  | 8005    | 3005    | 5437      | 9234    |
| CLI-6  | 8006    | 3006    | 5438      | 9235    |
```

### 7.2 自动端口配置

```bash
# 在 worktree 的 .env 中自动设置端口偏移
configure_ports() {
    local cli_id="$1"
    local wt_path=".worktrees/cli-${cli_id}"
    cat >> "${wt_path}/.env" << EOF
API_PORT=$((8000 + cli_id))
FRONTEND_PORT=$((3000 + cli_id))
DB_PORT=$((5432 + cli_id))
DEBUG_PORT=$((9229 + cli_id))
EOF
}
```

### 7.3 端口冲突检测

```bash
# 启动前检查端口是否被占用
check_port() {
    local port="$1"
    if lsof -i ":${port}" >/dev/null 2>&1; then
        echo "❌ 端口 ${port} 已被占用:"
        lsof -i ":${port}" | head -3
        return 1
    fi
    echo "✅ 端口 ${port} 可用"
}
```

---

## 8. Worktree 生命周期状态机

现有文档只覆盖了"创建"和"删除"。实际上 worktree 有完整的生命周期。

### 8.1 状态定义

```
┌──────────┐    dispatch    ┌──────────┐    worker starts    ┌──────────┐
│ CREATED  │ ──────────────>│ ASSIGNED │ ──────────────────>│  ACTIVE  │
└──────────┘                └──────────┘                     └──────────┘
                                                                  │
                                                    ┌─────────────┼─────────────┐
                                                    ▼             ▼             ▼
                                              ┌──────────┐ ┌──────────┐ ┌──────────┐
                                              │ BLOCKED  │ │ COMPLETE │ │  FAILED  │
                                              └──────────┘ └──────────┘ └──────────┘
                                                    │             │             │
                                                    ▼             ▼             ▼
                                              ┌──────────┐ ┌──────────┐ ┌──────────┐
                                              │ RESUMED  │ │  MERGED  │ │ RETRYING │
                                              └──────────┘ └──────────┘ └──────────┘
                                                    │             │             │
                                                    └──────┐      │      ┌──────┘
                                                           ▼      ▼      ▼
                                                      ┌──────────────────────┐
                                                      │      ARCHIVED       │
                                                      └──────────────────────┘
```

### 8.2 状态追踪

在 `.multi-cli-tasks/<worktree>/` 下维护状态文件：

```bash
# 状态变更
echo "ACTIVE $(date -Iseconds)" >> .multi-cli-tasks/<wt>/STATUS_LOG
# 查询当前状态
tail -1 .multi-cli-tasks/<wt>/STATUS_LOG | cut -d' ' -f1
```

### 8.3 超时自动处理

```bash
# 检查超过 48 小时无更新的 worktree
check_stale_worktrees() {
    for wt_dir in .worktrees/*/; do
        local name=$(basename "$wt_dir")
        local last_commit=$(cd "$wt_dir" && git log -1 --format='%ct' 2>/dev/null)
        local now=$(date +%s)
        local age_hours=$(( (now - last_commit) / 3600 ))
        if [ "$age_hours" -gt 48 ]; then
            echo "🔴 $name: ${age_hours}h 无提交 — 建议检查或回收"
        elif [ "$age_hours" -gt 24 ]; then
            echo "🟡 $name: ${age_hours}h 无提交 — 关注"
        fi
    done
}
```

---

## 9. AI CLI 工具差异化处理

不同 AI CLI 工具有不同的行为特征。现有文档把所有 CLI 当作同质化的执行者，但实际上差异很大。

### 9.1 工具特征矩阵

| 特征 | Claude Code | Gemini CLI | Codex | OpenCode | iFlow |
|------|------------|------------|-------|----------|-------|
| 上下文窗口 | 200K | 1M+ | 200K | 取决于模型 | 取决于模型 |
| 文件编辑方式 | 直接写入 | 直接写入 | 沙箱 | 直接写入 | 直接写入 |
| 自主性 | 高 | 高 | 中 | 中 | 中 |
| 配置目录 | .claude/ | .gemini/ | .codex/ | .opencode/ | .iflow/ |
| 会话持久化 | 有 | 有 | 无 | 有 | 有 |
| 并发安全 | ✅ | ✅ | ✅(沙箱) | ✅ | ✅ |
| 适合任务类型 | 复杂重构 | 大范围分析 | 精确修改 | 灵活 | 灵活 |

### 9.2 任务分配建议

```
根据工具特长分配任务：
- 大量文件需要分析/理解 → 优先分配给上下文窗口大的 CLI
- 精确的代码修改 → 分配给编辑精度高的 CLI
- 需要多轮迭代 → 分配给会话持久化好的 CLI
- 高风险操作 → 分配给有沙箱机制的 CLI
```

### 9.3 工具特定注意事项

```markdown
## Claude Code
- CLAUDE.md 是其核心指令文件，每个 worktree 会继承主仓库的
- 可在 worktree 中创建 .claude/settings.local.json 覆盖配置
- 注意 .claude/ 目录不要跨 worktree 复制

## Gemini CLI
- .gemini/ 目录包含会话历史，体积可能很大
- 定期清理：find .worktrees/*/. gemini/cache -mtime +7 -delete

## Codex
- 默认在沙箱中运行，需要 --full-auto 才能直接写文件
- 适合分配"只读分析 + 生成补丁"类任务

## OpenCode
- .opencode/ 目录包含会话和配置
- 支持多模型切换，可根据任务复杂度选择模型
```

---

## 10. 通信协议容错

TASK.md / TASK-REPORT.md 是唯一的通信通道。如果这些文件损坏或格式错误，整个协作链断裂。

### 10.1 文件格式校验

```bash
# 验证 TASK-REPORT.md 基本结构
validate_report() {
    local file="$1"
    local errors=0
    
    # 必须包含状态标记
    if ! grep -q '## 状态\|## Status\|状态:' "$file"; then
        echo "❌ 缺少状态字段: $file"
        ((errors++))
    fi
    
    # 必须包含进度信息
    if ! grep -q '进度\|Progress\|完成度' "$file"; then
        echo "❌ 缺少进度字段: $file"
        ((errors++))
    fi
    
    # 文件不能为空
    if [ ! -s "$file" ]; then
        echo "❌ 文件为空: $file"
        ((errors++))
    fi
    
    [ "$errors" -eq 0 ] && echo "✅ $file 格式正确"
    return $errors
}
```

### 10.2 损坏恢复

```bash
# 从 git 历史恢复最后一个有效版本
recover_task_file() {
    local wt_path="$1"
    local file="$2"  # TASK.md 或 TASK-REPORT.md
    
    cd "$wt_path"
    # 找到最后一个有效提交
    local last_good=$(git log --oneline -- "$file" | head -1 | cut -d' ' -f1)
    if [ -n "$last_good" ]; then
        git checkout "$last_good" -- "$file"
        echo "✅ 已恢复 $file 到 $last_good"
    else
        echo "❌ 无历史版本可恢复，需要 Main CLI 重新分发"
    fi
}
```

### 10.3 通信冗余

```
除了 TASK-REPORT.md，建议增加备用通信通道：
1. git commit message 中包含进度摘要（已有规范）
2. 分支名包含状态后缀：worker/cli-1-feature → worker/cli-1-feature--done
3. 空文件信号：touch .worktrees/<name>/DONE 或 BLOCKED 或 HELP
```

---

## 11. 审计追踪与结构化日志

现有文档依赖人工检查。缺少自动化的操作审计。

### 11.1 操作日志格式

```bash
# .multi-cli-tasks/AUDIT_LOG.md
# 每行格式：[ISO时间] [操作者] [动作] [目标] [结果]

log_action() {
    local actor="$1"   # main-cli / cli-1 / cli-2 ...
    local action="$2"  # dispatch / merge / block / recover / ...
    local target="$3"  # worktree name / branch name
    local result="$4"  # success / failed / pending
    echo "[$(date -Iseconds)] [$actor] [$action] [$target] [$result]" \
        >> .multi-cli-tasks/AUDIT_LOG.md
}

# 使用示例
log_action "main-cli" "dispatch" "cli-3" "success"
log_action "main-cli" "merge" "worker/cli-1-feature" "failed:conflict"
log_action "main-cli" "recover" "cli-5-worktree" "success"
```

### 11.2 自动化审计脚本

```bash
#!/bin/bash
# audit_snapshot.sh — 每日自动生成审计快照

echo "## 审计快照 $(date -Idate)" >> .multi-cli-tasks/AUDIT_LOG.md
echo "" >> .multi-cli-tasks/AUDIT_LOG.md

# Worktree 状态
echo "### Worktree 状态" >> .multi-cli-tasks/AUDIT_LOG.md
git worktree list >> .multi-cli-tasks/AUDIT_LOG.md

# 各分支最后提交
echo "### 分支活跃度" >> .multi-cli-tasks/AUDIT_LOG.md
for branch in $(git branch -r --list 'origin/worker/*' | tr -d ' '); do
    echo "- $branch: $(git log -1 --format='%cr - %s' "$branch" 2>/dev/null)" \
        >> .multi-cli-tasks/AUDIT_LOG.md
done

# 磁盘使用
echo "### 磁盘使用" >> .multi-cli-tasks/AUDIT_LOG.md
du -sh .worktrees/*/ 2>/dev/null >> .multi-cli-tasks/AUDIT_LOG.md
echo "" >> .multi-cli-tasks/AUDIT_LOG.md
```

---

## 12. 事后复盘模板

现有文档有 PHASE_SUMMARY，但缺少结构化的复盘模板来提炼经验教训。

### 12.1 复盘模板

```markdown
# 复盘报告：[项目/阶段名称]

## 基本信息
- **时间范围**: YYYY-MM-DD ~ YYYY-MM-DD
- **参与 CLI**: [列表]
- **Worktree 数量**: N
- **任务总数**: N

## 量化指标
| 指标 | 计划值 | 实际值 | 偏差 |
|------|-------|-------|------|
| 总耗时 | | | |
| 合并冲突次数 | 0 | | |
| 回滚次数 | 0 | | |
| Worker 阻塞次数 | 0 | | |
| 一次通过率 | 100% | | |

## 做得好的（Keep）
1. 
2. 

## 需要改进的（Improve）
1. 
2. 

## 需要停止的（Stop）
1. 

## 需要开始的（Start）
1. 

## 根因分析（针对重大问题）
### 问题描述
### 时间线
### 根本原因
### 纠正措施
### 预防措施

## 文档更新建议
- [ ] 需要更新的文档：
- [ ] 需要新增的文档：
- [ ] 需要废弃的文档：
```

### 12.2 复盘触发条件

```
必须复盘：
- 每个 Phase 结束后
- 发生回滚事件后
- 合并冲突超过 3 次后
- 任何 Worker 阻塞超过 24 小时后

建议复盘：
- 每周五（如果项目跨周）
- 新 CLI 工具首次加入协作后
```

---

## 13. v3.2 治理门禁韧性

新增目标：让 main 协调验收制与 dev-* 开发制在异常场景下仍可执行，不因工具切换而失效。

### 13.1 门禁最小集（必须可恢复）

- **角色门禁**: `main` 仅做协调与验收，不直接进行功能开发。
- **分支门禁**: 所有功能分支必须使用 `dev-*` 并在 worktree 中开发。
- **PR 门禁**: 所有 Worker PR 目标必须是 `main`。
- **证据门禁**: PR 与 `TASK-REPORT.md` 必须提供“变更范围 + 验证命令与结果 + 风险/回滚说明”。
- **合并门禁**: 质量门（TS/Python/tests）、安全门（secrets/audit/SAST）、审查门（code review）必须全部通过。

### 13.2 异常处置流程

1. 发现功能提交直接落在 `main`：立即阻断并要求迁移到 `dev-*` 分支重提。  
2. 发现 PR `base` 不是 `main`：立即驳回并要求按 `base=main` 重提。  
3. 发现提交信息不规范：驳回并要求重写为 `type(scope): short description`。  
4. 发现缺失验证/风险回滚证据：标记阻塞，不进入合并队列。  
5. 将异常记录在 `.multi-cli-tasks/INCIDENT_LOG.md`，用于复盘。  

### 13.3 每日最小巡检命令

```bash
# 1) 当前仓库状态
git branch --show-current
git status -sb

# 2) 检查活跃 dev-* 分支相对 main 的差异窗口
git for-each-ref --format='%(refname:short)' refs/heads/dev-* | while read -r b; do
  echo "=== $b ==="
  git log --oneline "main..$b" | head -20
done

# 3) 抽查最近提交规范
git log --oneline -n 20
```

---

## 附录：快速参考卡片

### A. 紧急情况速查

| 情况 | 第一步 | 第二步 |
|------|-------|-------|
| Worker 失控 | `git worktree lock <path>` | 终止进程 |
| 合并出错 | `git revert -m 1 <hash>` | 通知 Worker 修复 |
| Worktree 损坏 | `git worktree repair` | 不行就删除重建 |
| Main CLI 崩溃 | 新开会话，`git worktree list` | 从 safe/ tag 恢复 |
| 磁盘满 | `du -sh .worktrees/*/` 找大户 | 清理或迁移 |
| .env 泄露 | `git reset HEAD .env && git checkout -- .env` | 轮换密钥 |

### B. 每日检查命令

```bash
# 一键健康检查（建议加入 Main CLI 的 Pre-flight）
echo "=== Worktree 状态 ===" && git worktree list
echo "=== 磁盘使用 ===" && du -sh .worktrees/*/ 2>/dev/null
echo "=== 分支活跃度 ===" && for b in $(git branch -r --list 'origin/worker/*'); do echo "$b: $(git log -1 --format='%cr' $b 2>/dev/null)"; done
echo "=== 端口占用 ===" && for p in 8001 8002 8003 8004 8005 8006; do lsof -i :$p >/dev/null 2>&1 && echo "⚠️ 端口 $p 被占用"; done
echo "=== 进程检查 ===" && ps aux | grep -E 'claude|codex|gemini|opencode|iflow' | grep -v grep | wc -l | xargs -I{} echo "活跃 CLI 进程: {}"
```

---

> **本文档与现有 6 份核心文档互补，不替代。**  
> 建议将本文档加入 Main CLI 的 Pre-flight 阅读清单。  
> 
> 最后更新：2026-03-05 | 版本：v3.2
