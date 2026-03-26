# Multi-CLI 协作系统快速参考

**版本**: v2.1
**更新时间**: 2026-01-01
**完整文档**: [docs/guides/multi-cli-tasks/INDEX.md](../docs/guides/multi-cli-tasks/INDEX.md)

---

## 📚 快速导航

| 主题 | 快速参考 | 完整文档 |
|------|----------|----------|
| **系统概览** | [系统初始化](#系统初始化) | [V2实施方案](../docs/architecture/MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md) |
| **CLI报到** | [CLI报到流程](#cli报到流程) | [报到详细指南](../docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md) |
| **任务池** | [任务池使用](#任务池使用) | [任务池完整指南](../docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md) |
| **实施报告** | - | [实施完成报告](../docs/06-项目管理与报告/MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md) |

---

## 系统初始化

### 一键初始化环境

```bash
# 初始化完整的Multi-CLI环境（8个CLI + 共享目录）
bash scripts/dev/init_multi_cli.sh
```

**创建内容**:
- ✅ 8个CLI目录（main, web, api, db, it/worker{1-3}）
- ✅ 每个CLI的mailbox, archive目录
- ✅ TASK.md, RULES.md, STATUS.md模板
- ✅ 智能协调器自动启动

### 启动Mailbox监听器

```bash
# 为每个CLI启动mailbox监听器
python scripts/dev/mailbox_watcher.py --cli=main &
python scripts/dev/mailbox_watcher.py --cli=web &
python scripts/dev/mailbox_watcher.py --cli=api &
python scripts/dev/mailbox_watcher.py --cli=db &
```

### 查看CLI状态

```bash
# 扫描所有CLI状态
python scripts/dev/cli_coordinator.py --scan

# 查看特定CLI详细信息
python scripts/dev/cli_coordinator.py --info=web
```

---

## CLI报到流程

### 1. CLI向main报到

```bash
# 基础报到
python scripts/dev/cli_registration.py \
  --register \
  --cli=web

# 完整报到（包含能力声明）
python scripts/dev/cli_registration.py \
  --register \
  --cli=web \
  --type=worker \
  --capabilities="frontend,Vue,API-integration,UI-design"
```

### 2. main确认报到并分配角色

```bash
python scripts/dev/cli_registration.py \
  --confirm \
  --cli=web \
  --role="前端开发工程师" \
  --tasks="task-1.1,task-1.2"
```

### 3. 验证报到状态

```bash
# 查看报到信息
cat CLIS/main/registrations.json | jq .

# 查看CLI收到的确认消息
cat CLIS/web/mailbox/main_confirmation_*.md
```

### 完整流程图

```
CLI-web发送报到 → main收到请求 → main确认角色 → CLI-web收到确认
    ↓                    ↓                ↓              ↓
--register         registrations.json  --confirm      mailbox消息
```

**📖 详细文档**: [CLI报到完整指南](../docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md)

---

## 任务池使用

### 1. main发布任务到任务池

```bash
python scripts/dev/task_pool.py \
  --publish \
  --task=task-1.1 \
  --title="实现Web前端主页" \
  --description="使用Vue 3实现响应式主页，包含顶部导航、侧边栏和主内容区域" \
  --priority=HIGH \
  --skills="frontend,Vue,UI-design" \
  --hours=8
```

### 2. CLI查看可认领的任务

```bash
# 查看所有待认领任务
python scripts/dev/task_pool.py --list

# 按技能筛选任务（推荐）
python scripts/dev/task_pool.py --list --skills="frontend"

# 查看任务池Markdown文件
cat CLIS/SHARED/TASKS_POOL.md
```

### 3. CLI认领任务

```bash
python scripts/dev/task_pool.py \
  --claim \
  --task=task-1.1 \
  --cli=web
```

### 4. 更新任务进度

```bash
# 更新进度到50%
python scripts/dev/task_pool.py \
  --update \
  --task=task-1.1 \
  --cli=web \
  --progress=50

# 完成任务
python scripts/dev/task_pool.py \
  --update \
  --task=task-1.1 \
  --cli=web \
  --progress=100 \
  --status=completed
```

### 5. 释放任务（取消认领）

```bash
python scripts/dev/task_pool.py \
  --release \
  --task=task-1.1 \
  --cli=web
```

### 任务池流程图

```
main发布任务 → 任务池(TASKS_POOL.md) → CLI查看任务 → CLI认领 → 更新进度
     ↓                ↓                   ↓           ↓         ↓
 --publish       tasks.json          --list      --claim   --update
```

**📖 详细文档**: [任务池完整使用指南](../docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md)

---

## 核心脚本快速参考

### 报到和协调脚本

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| [`cli_registration.py`](../scripts/dev/cli_registration.py) | CLI报到和确认 | CLI启动时 |
| [`cli_coordinator.py`](../scripts/dev/cli_coordinator.py) | CLI状态扫描和消息发送 | 查看CLI状态 |
| [`smart_coordinator.py`](../scripts/dev/smart_coordinator.py) | 智能协调规则引擎 | 自动协调阻塞和资源 |
| [`task_pool.py`](../scripts/dev/task_pool.py) | 任务池管理 | 任务发布、认领、更新 |

### 监控和自动化脚本

| 脚本 | 功能 | 使用场景 |
|------|------|----------|
| [`mailbox_watcher.py`](../scripts/dev/mailbox_watcher.py) | 事件驱动mailbox监听 | 后台运行监听消息 |
| [`auto_status.py`](../scripts/dev/auto_status.py) | 自动更新STATUS.md | 装饰器方式跟踪任务 |
| [`simple_lock.py`](../scripts/dev/simple_lock.py) | 文件锁管理 | 防止并发冲突 |
| [`init_multi_cli.sh`](../scripts/dev/init_multi_cli.sh) | 一键初始化 | 首次搭建环境 |

---

## 常用命令速查

### CLI启动工作流

```bash
# Step 1: CLI报到（每个CLI启动时执行一次）
python scripts/dev/cli_registration.py --register --cli=web --capabilities="frontend,Vue"

# Step 2: 启动mailbox监听器（后台运行）
python scripts/dev/mailbox_watcher.py --cli=web &

# Step 3: 查看可认领的任务
python scripts/dev/task_pool.py --list --skills="frontend"

# Step 4: 认领任务
python scripts/dev/task_pool.py --claim --task=task-1.1 --cli=web

# Step 5: 开始工作...
# 使用 @track_task 装饰器自动更新STATUS.md

# Step 6: 更新任务进度
python scripts/dev/task_pool.py --update --task=task-1.1 --cli=web --progress=50
```

### main管理工作流

```bash
# Step 1: 初始化环境（首次）
bash scripts/dev/init_multi_cli.sh

# Step 2: 确认CLI报到
python scripts/dev/cli_registration.py --confirm --cli=web --role="前端开发" --tasks="task-1.1,task-1.2"

# Step 3: 发布任务到任务池
python scripts/dev/task_pool.py --publish --task=task-1.1 --title="..." --skills="frontend"

# Step 4: 监控CLI状态
python scripts/dev/cli_coordinator.py --scan

# Step 5: 查看任务池状态
cat CLIS/SHARED/TASKS_POOL.md
```

---

## 文件结构说明

### CLI目录结构

```
CLIS/
├── main/                  # CLI-main（协调器）
│   ├── mailbox/           # 收到的消息
│   ├── archive/           # 已处理的消息
│   ├── checkpoints/       # 检查点
│   ├── TASK.md            # 任务清单
│   ├── RULES.md           # 工作规范
│   ├── STATUS.md          # 当前状态
│   ├── .cli_config        # CLI配置
│   └── coordinator.log    # 协调器日志
├── web/                   # CLI-web（前端开发）
│   ├── mailbox/
│   ├── archive/
│   ├── TASK.md
│   ├── RULES.md
│   └── STATUS.md
├── api/                   # CLI-api（API开发）
├── db/                    # CLI-db（数据库管理）
├── it/                    # Worker CLI们
│   ├── worker1/
│   ├── worker2/
│   └── worker3/
├── locks/                 # 文件锁目录
├── SHARED/                # 共享资源
│   ├── TASKS_POOL.md      # 任务池总览
│   └── tasks.json         # 任务数据库
└── templates/             # 模板文件
```

### 关键文件说明

**报到处文件**:
- `CLIS/main/registrations.json` - 所有CLI的报到信息
- `CLIS/{cli}/mailbox/` - 收到的消息
- `CLIS/{cli}/TASK.md` - 当前任务清单

**任务池文件**:
- `CLIS/SHARED/TASKS_POOL.md` - 任务池Markdown总览
- `CLIS/SHARED/tasks.json` - 任务数据库

**状态文件**:
- `CLIS/{cli}/STATUS.md` - CLI当前状态（idle/active/blocked/error）

---

## 常见问题快速解决

### Q1: CLI如何查看可认领的任务？

```bash
# 方法1: 命令行查看（推荐）
python scripts/dev/task_pool.py --list --skills="YOUR_SKILL"

# 方法2: 查看Markdown文件
cat CLIS/SHARED/TASKS_POOL.md

# 方法3: 查看任务数据库
cat CLIS/SHARED/tasks.json | jq '.[] | select(.status=="open")'
```

### Q2: 报到消息未收到？

```bash
# 检查main的mailbox
ls -la CLIS/main/mailbox/

# 检查registrations.json
cat CLIS/main/registrations.json

# 重新发送报到
python scripts/dev/cli_registration.py --register --cli=web
```

### Q3: 任务认领失败？

```bash
# 查看任务详情
python scripts/dev/task_pool.py --list --task=task-1.1

# 检查任务状态（可能已被认领）
cat CLIS/SHARED/tasks.json | jq '.["task-1.1"]'

# 选择其他待认领任务
python scripts/dev/task_pool.py --list
```

### Q4: 如何停止mailbox监听器？

```bash
# 查看监听器进程
ps aux | grep mailbox_watcher

# 停止监听器
kill <PID>

# 或使用pkill
pkill -f mailbox_watcher
```

### Q5: 协调器未运行？

```bash
# 检查协调器进程
cat CLIS/main/.coordinator_pid
ps aux | grep $(cat CLIS/main/.coordinator_pid)

# 查看协调器日志
tail -f CLIS/main/coordinator.log

# 重启协调器
python scripts/dev/smart_coordinator.py --auto
```

---

## 最佳实践

### 1. 工作流程规范

**CLI启动时**:
1. 执行报到（`--register`）
2. 启动mailbox监听器
3. 查看可认领任务
4. 认领合适任务
5. 使用`@track_task`装饰器自动更新状态

**main工作流**:
1. 初始化环境
2. 确认CLI报到
3. 发布任务到任务池
4. 监控CLI状态
5. 定期检查任务池进度

### 2. 技能标签规范

**前端技能**: `frontend`, `Vue`, `React`, `UI-design`, `CSS`
**后端技能**: `backend`, `FastAPI`, `authentication`, `API-design`
**数据库技能**: `database`, `PostgreSQL`, `TDengine`, `optimization`
**测试技能**: `testing`, `pytest`, `e2e`, `integration-test`

### 3. 优先级设置规范

- `HIGH`: 阻塞问题、核心功能
- `MEDIUM`: 重要功能、优化改进
- `LOW`: 锦上添花、文档更新

### 4. 进度更新建议

- 认领任务时: 0%
- 完成设计时: 20%
- 实现核心功能: 50%
- 完成测试: 80%
- 代码审查通过: 100%, status=completed

---

## 相关文档索引

### 核心文档

- **[CLI报到详细指南](../docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md)** - 完整的报到流程、API文档、故障排查
- **[任务池使用指南](../docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md)** - 任务发布、认领、更新的完整说明
- **[V2实施方案](../docs/architecture/MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md)** - 架构设计、实现细节
- **[实施完成报告](../docs/06-项目管理与报告/MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md)** - 实施总结、验证结果
- **[V2.1修复总结](../docs/06-项目管理与报告/MULTI_CLI_V2_FIX_SUMMARY.md)** - 7个关键问题修复

### 脚本文档

所有脚本都在 [`scripts/dev/`](../scripts/dev/) 目录下：

**报到和协调**:
- [cli_registration.py](../scripts/dev/cli_registration.py) - CLI报到机制（269行）
- [cli_coordinator.py](../scripts/dev/cli_coordinator.py) - CLI协调器（161行）
- [smart_coordinator.py](../scripts/dev/smart_coordinator.py) - 智能协调器（457行）
- [task_pool.py](../scripts/dev/task_pool.py) - 任务池管理（488行）

**监控和自动化**:
- [mailbox_watcher.py](../scripts/dev/mailbox_watcher.py) - 事件驱动监听（231行）
- [auto_status.py](../scripts/dev/auto_status.py) - 自动状态更新（97行）
- [simple_lock.py](../scripts/dev/simple_lock.py) - 文件锁管理（164行）
- [init_multi_cli.sh](../scripts/dev/init_multi_cli.sh) - 一键初始化（182行）

### 外部文档

- **[CLAUDE.md](../CLAUDE.md)** - 项目开发指南（包含Multi-CLI章节）
- **[FILE_ORGANIZATION_RULES.md](../docs/standards/FILE_ORGANIZATION_RULES.md)** - 文件组织规范
- **[MULTI_CLI_COLLABORATION_METHOD.md](../docs/guides/multi-cli-tasks/MULTI_CLI_COLLABORATION_METHOD.md)** - V1方法文档（已归档）

---

## 获取帮助

### 查看详细文档

```bash
# 在CLIS目录下
ls ../docs/guides/

# 查看特定文档
cat ../docs/guides/multi-cli-tasks/CLI_REGISTRATION_GUIDE.md
cat ../docs/guides/multi-cli-tasks/TASK_POOL_USAGE_GUIDE.md
```

### 查看脚本帮助

```bash
# 查看脚本帮助信息
python scripts/dev/cli_registration.py --help
python scripts/dev/task_pool.py --help
python scripts/dev/cli_coordinator.py --help
```

### 查看示例

```bash
# 查看CLI使用示例
cat CLIS/main/TASK.md
cat CLIS/main/RULES.md

# 查看任务池示例
cat CLIS/SHARED/TASKS_POOL.md
```

---

**快速参考维护**: 本文档应保持简洁，主要作为快速参考
**详细问题**: 请参考 [docs/guides/multi-cli-tasks/INDEX.md](../docs/guides/multi-cli-tasks/INDEX.md) 下的完整文档
**最后更新**: 2026-01-01
**维护者**: Main CLI (Claude Code)
