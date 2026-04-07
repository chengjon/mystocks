# 任务池使用指南

> **历史计划说明**:
> 本文件是阶段性计划、路线图、提案、任务方案或执行矩阵，不是当前基线、当前实施状态或仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线文档一并核对。
>
> 文内优先级、缺口清单、执行步骤、目标值和时间线如未重新复核，应视为历史计划上下文，不得直接当作当前事实。


**版本**: v1.0
**更新时间**: 2026-01-01
**相关文件**: [`scripts/dev/task_pool.py`](../../scripts/dev/task_pool.py)

---

## 📋 目录

1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [完整工作流程](#完整工作流程)
4. [命令参考](#命令参考)
5. [使用示例](#使用示例)
6. [文件说明](#文件说明)
7. [最佳实践](#最佳实践)

---

## 系统概述

### 什么是任务池？

任务池是Multi-CLI协作系统的核心组件，用于：
- ✅ **main发布任务** - main向任务池发布需要完成的工作
- ✅ **CLI浏览任务** - 其他CLI查看可认领的任务
- ✅ **任务认领** - CLI认领适合自己的任务
- ✅ **进度追踪** - 更新任务进度，查看任务状态

### 核心特性

**按技能匹配** - 任务可标注需要的技能，CLI根据自己的能力筛选
**优先级管理** - HIGH/MEDIUM/LOW优先级，重要任务优先处理
**进度跟踪** - 实时更新任务进度（0-100%）
**自动同步** - TASKS_POOL.md和CLI的TASK.md自动更新

---

## 快速开始

### 1. main发布任务

```bash
python scripts/dev/task_pool.py \
  --publish \
  --task=task-1.1 \
  --title="实现Web前端主页" \
  --description="使用Vue 3实现响应式主页" \
  --priority=HIGH \
  --skills="frontend,Vue,UI-design" \
  --hours=8
```

### 2. CLI查看任务

```bash
# 查看所有待认领任务
python scripts/dev/task_pool.py --list

# 查看需要特定技能的任务
python scripts/dev/task_pool.py --list --skills="frontend"
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
python scripts/dev/task_pool.py \
  --update \
  --task=task-1.1 \
  --cli=web \
  --progress=50
```

---

## 完整工作流程

### 流程图

```
┌─────────────────────────────────────────────────────────────┐
│                    任务池完整工作流程                         │
└─────────────────────────────────────────────────────────────┘

步骤1: main发布任务到任务池
┌──────────────┐         发布任务          ┌──────────────┐
│   CLI-main   │ ───────────────────────> │   任务池      │
│   (协调器)     │                          │ (TASKS_POOL)  │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/task_pool.py \
      |   --publish --task=task-1.1 \
      |   --title="实现主页" \
      |   --skills="frontend,Vue" \
      |   --priority=HIGH
      |
      V
✅ 任务保存到: CLIS/SHARED/tasks.json
✅ 生成Markdown: CLIS/SHARED/TASKS_POOL.md
✅ 状态: open (待认领)


步骤2: CLI浏览和筛选任务
┌──────────────┐         查看任务          ┌──────────────┐
│   CLI-web    │ <─────────────────────── │   任务池      │
│  (前端开发)    │                          │ (TASKS_POOL)  │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/task_pool.py \
      |   --list --skills="frontend"
      |
      V
📋 显示匹配的任务:
    - task-1.1: 实现Web前端主页 (HIGH, frontend, Vue)
    - task-1.2: 实现API数据集成 (HIGH, frontend, API)


步骤3: CLI认领任务
┌──────────────┐         认领任务          ┌──────────────┐
│   CLI-web    │ ───────────────────────> │   任务池      │
│  (前端开发)    │                          │ (TASKS_POOL)  │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/task_pool.py \
      |   --claim --task=task-1.1 --cli=web
      |
      V
✅ 任务状态更新: open → claimed
✅ 记录认领者: web
✅ 更新CLI-web的TASK.md
✅ 刷新TASKS_POOL.md


步骤4: CLI更新任务进度
┌──────────────┐         更新进度          ┌──────────────┐
│   CLI-web    │ ───────────────────────> │   任务池      │
│  (前端开发)    │                          │ (TASKS_POOL)  │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/task_pool.py \
      |   --update --task=task-1.1 --cli=web \
      |   --progress=50 --status=claimed
      |
      V
✅ 任务进度更新: 0% → 50%
✅ 更新CLI-web的TASK.md
✅ 刷新TASKS_POOL.md


步骤5: 完成任务
┌──────────────┐         完成任务          ┌──────────────┐
│   CLI-web    │ ───────────────────────> │   任务池      │
│  (前端开发)    │                          │ (TASKS_POOL)  │
└──────────────┘                          └──────────────┘
      |
      | python scripts/dev/task_pool.py \
      |   --update --task=task-1.1 --cli=web \
      |   --progress=100 --status=completed
      |
      V
🎉 任务已完成!
    - 状态: claimed → completed
    - 进度: 100%
    - 记录完成时间
```

---

## 命令参考

### 发布任务

```bash
python scripts/dev/task_pool.py --publish \
  --task=TASK_ID \
  --title="任务标题" \
  --description="任务描述" \
  --priority=PRIORITY \
  --skills="skill1,skill2" \
  --hours=HOURS
```

**参数说明**:
- `--task`: 任务ID（如: task-1.1, feature-web-homepage）
- `--title`: 任务标题（简短描述）
- `--description`: 任务描述（详细说明）
- `--priority`: 优先级（HIGH, MEDIUM, LOW）
- `--skills`: 需要的技能（逗号分隔）
- `--hours`: 预计工时（小时数）

### 查看任务

```bash
# 查看所有待认领任务
python scripts/dev/task_pool.py --list

# 查看特定CLI的任务
python scripts/dev/task_pool.py --list --cli=web

# 查看需要特定技能的任务
python scripts/dev/task_pool.py --list --skills="frontend"
```

### 认领任务

```bash
python scripts/dev/task_pool.py --claim \
  --task=TASK_ID \
  --cli=CLI_NAME
```

**参数说明**:
- `--task`: 要认领的任务ID
- `--cli`: 认领任务的CLI名称

### 更新进度

```bash
python scripts/dev/task_pool.py --update \
  --task=TASK_ID \
  --cli=CLI_NAME \
  --progress=PERCENT \
  --status=STATUS
```

**参数说明**:
- `--progress`: 进度百分比（0-100）
- `--status`: 新状态（claimed, completed）

### 释放任务

```bash
python scripts/dev/task_pool.py --release \
  --task=TASK_ID \
  --cli=CLI_NAME
```

**说明**: 取消认领，任务状态恢复为open

---

## 使用示例

### 示例1: main发布前端任务

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

**输出**:
```
✅ 任务已发布: task-1.1 - 实现Web前端主页
```

### 示例2: CLI-web浏览前端任务

```bash
python scripts/dev/task_pool.py --list --skills="frontend"
```

**输出**:
```
找到 2 个任务:

📋 🔴 **task-1.1**: 实现Web前端主页
   状态: open | 认领者: 待认领 | 进度: 0%
   技能: frontend, Vue, UI-design
   描述: 使用Vue 3实现响应式主页，包含顶部导航、侧边栏和主内容区域

📋 🔴 **task-1.2**: 实现API数据集成
   状态: open | 认领者: 待认领 | 进度: 0%
   技能: frontend, API-integration, async
   描述: 前端调用FastAPI后端接口，获取股票数据和指标数据
```

### 示例3: CLI-web认领任务

```bash
python scripts/dev/task_pool.py --claim --task=task-1.1 --cli=web
```

**输出**:
```
✅ web 已认领任务: task-1.1 - 实现Web前端主页

任务详情:
  标题: 实现Web前端主页
  描述: 使用Vue 3实现响应式主页，包含顶部导航、侧边栏和主内容区域
  技能: frontend, Vue, UI-design
  预计工时: 8小时
```

### 示例4: CLI-web更新进度

```bash
# 工作进行中，更新到50%
python scripts/dev/task_pool.py --update --task=task-1.1 --cli=web --progress=50

# 任务完成
python scripts/dev/task_pool.py --update --task=task-1.1 --cli=web --progress=100 --status=completed
```

**输出**:
```
✅ 任务进度已更新: task-1.1 - 实现Web前端主页 (50%)
任务 task-1.1 进度已更新到 50%
```

### 示例5: main查看所有任务状态

```bash
# 直接查看任务池Markdown文件
cat CLIS/SHARED/TASKS_POOL.md
```

**输出**:
```markdown
# 任务池

**Updated**: 2026-01-01 19:16:41

## 统计信息

- 总任务数: 3
- 待认领: 1
- 进行中: 2
- 已完成: 0

---

## 待认领任务

### 🔴 task-1.2: 实现API数据集成
...

## 进行中任务

- **task-1.1**: 实现Web前端主页 (认领者: web, 进度: 50%)
- **task-2.1**: 优化数据库查询性能 (认领者: db, 进度: 50%)
```

### 示例6: 使用Python API

```python
from scripts.dev.task_pool import TaskPool

# 创建任务池管理器
pool = TaskPool()

# 发布任务
pool.publish_task(
    task_id='task-1.3',
    title='实现用户认证',
    description='实现JWT认证和用户登录功能',
    priority='HIGH',
    skills=['backend', 'authentication', 'security'],
    estimated_hours=10
)

# 查看任务
tasks = pool.list_tasks(status='open', skills=['backend'])
for task_id, task in tasks.items():
    print(f"{task_id}: {task['title']}")

# 认领任务
pool.claim_task('task-1.3', 'api')

# 更新进度
pool.update_task_progress('task-1.3', 'api', progress=50)
```

---

## 文件说明

### 1. tasks.json

**位置**: `CLIS/SHARED/tasks.json`

**格式**:
```json
{
  "task-1.1": {
    "task_id": "task-1.1",
    "title": "实现Web前端主页",
    "description": "使用Vue 3实现响应式主页...",
    "priority": "HIGH",
    "skills": ["frontend", "Vue", "UI-design"],
    "estimated_hours": 8,
    "status": "claimed",
    "claimed_by": "web",
    "claimed_time": "2026-01-01T19:16:35.123456",
    "published_time": "2026-01-01T19:16:19.123456",
    "progress": 50
  }
}
```

**字段说明**:
- `task_id`: 任务唯一标识
- `status`: 状态（open, claimed, completed）
- `claimed_by`: 认领者（CLI名称）
- `progress`: 进度（0-100）

### 2. TASKS_POOL.md

**位置**: `CLIS/SHARED/TASKS_POOL.md`

**内容**:
- 统计信息（总任务数、待认领、进行中、已完成）
- 待认领任务列表（按优先级排序）
- 进行中任务列表（显示认领者和进度）
- 已完成任务列表（显示完成者）

**自动生成**: 每次任务状态变化时自动更新

### 3. CLI的TASK.md

**位置**: `CLIS/{cli_name}/TASK.md`

**自动更新**: 当CLI认领任务或更新进度时，自动添加或更新任务条目

**格式**:
```markdown
# 任务清单

## 当前任务
- [task-1.1] 实现Web前端主页 - 使用Vue 3实现响应式主页... (进度: 50%)

## 任务历史

| 任务ID | 任务名称 | 完成时间 | 状态 |
|--------|---------|---------|------|
```

---

## 最佳实践

### 1. 任务发布规范

**任务ID命名**:
- 使用层次化编号: `task-1.1`, `task-1.2`
- 或使用功能描述: `feature-web-homepage`, `bugfix-login-error`

**技能标注**:
- 使用明确的技能标签: `frontend`, `backend`, `database`, `api`
- 包含技术栈: `Vue`, `PostgreSQL`, `FastAPI`

**优先级设置**:
- `HIGH`: 阻塞问题、核心功能
- `MEDIUM`: 重要功能、优化改进
- `LOW`: 锦上添花、文档更新

### 2. 技能匹配建议

**前端技能**: `frontend`, `Vue`, `React`, `UI-design`, `CSS`
**后端技能**: `backend`, `FastAPI`, `authentication`, `API-design`
**数据库技能**: `database`, `PostgreSQL`, `TDengine`, `optimization`
**测试技能**: `testing`, `pytest`, `e2e`, `integration-test`

### 3. 进度更新建议

**工作流程**:
1. 认领任务时: 进度0%
2. 完成设计时: 进度20%
3. 实现核心功能时: 进度50%
4. 完成测试时: 进度80%
5. 代码审查通过: 进度100%，状态改为completed

### 4. 任务释放规范

**何时释放任务**:
- 发现任务与能力不匹配
- 遇到阻塞问题，需要其他CLI协助
- 优先级调整，需要先处理其他任务

**释放前**:
- 更新进度到当前状态
- 添加注释说明原因
- 通知main重新分配

### 5. 批量操作

**发布多个相关任务**:
```bash
#!/bin/bash
# 批量发布前端任务

python scripts/dev/task_pool.py --publish --task=task-1.1 --title="..." --skills="frontend,Vue"
python scripts/dev/task_pool.py --publish --task=task-1.2 --title="..." --skills="frontend,API"
python scripts/dev/task_pool.py --publish --task=task-1.3 --title="..." --skills="frontend,UI"
```

**查看特定CLI的所有任务**:
```bash
python scripts/dev/task_pool.py --list --cli=web
```

---

## 与其他系统集成

### 1. 与CLI报到系统集成

**报到时分配任务**:
```bash
# 步骤1: CLI报到
python scripts/dev/cli_registration.py --register --cli=web --capabilities="frontend,Vue"

# 步骤2: main确认并推荐任务
python scripts/dev/cli_registration.py --confirm --cli=web --role="前端开发" --tasks="task-1.1,task-1.2"

# 步骤3: CLI查看推荐的任务
cat CLIS/web/TASK.md

# 步骤4: CLI从任务池认领任务
python scripts/dev/task_pool.py --claim --task=task-1.1 --cli=web
```

### 2. 与智能协调器集成

**自动任务分配**:
智能协调器会自动扫描空闲CLI，并从任务池中推荐合适的任务。

**触发条件**:
- CLI状态为idle
- 任务池中有匹配该CLI技能的任务

**自动消息**:
```
您当前空闲，建议执行独立任务: task-1.1
```

### 3. 与STATUS.md集成

**工作流**:
1. 认领任务 → STATUS.md状态变为active
2. 更新进度 → STATUS.md显示当前任务和进度
3. 完成任务 → STATUS.md状态变为idle

---

## 故障排查

### 问题1: 任务未出现在TASKS_POOL.md

**症状**: 发布任务后，TASKS_POOL.md未更新

**排查**:
1. 检查tasks.json是否存在:
   ```bash
   cat CLIS/SHARED/tasks.json | jq .
   ```

2. 手动重新生成TASKS_POOL.md:
   ```python
   from scripts.dev.task_pool import TaskPool
   pool = TaskPool()
   tasks = pool._load_tasks_db()
   pool._update_tasks_pool_md(tasks)
   ```

### 问题2: CLI的TASK.md未更新

**症状**: 认领任务后，CLI的TASK.md没有变化

**排查**:
1. 检查TASK.md文件权限:
   ```bash
   ls -la CLIS/web/TASK.md
   ```

2. 手动更新TASK.md:
   ```python
   from scripts.dev.task_pool import TaskPool
   pool = TaskPool()
   task = pool._load_tasks_db()['task-1.1']
   pool._update_cli_task_md('web', task)
   ```

### 问题3: 无法认领任务

**症状**: 执行--claim时报错"任务不可认领"

**原因**: 任务已被其他CLI认领

**解决**:
1. 查看任务详情:
   ```bash
   python scripts/dev/task_pool.py --list --task=task-1.1
   ```

2. 联系当前认领者，询问是否可以释放或协作

3. 或选择其他待认领任务

---

## 相关文档

- **CLI报到指引**: [`CLI_REGISTRATION_GUIDE.md`](./CLI_REGISTRATION_GUIDE.md)
- **Multi-CLI V2实施方案**: [`MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md`](./MULTI_CLI_COLLABORATION_V2_IMPLEMENTATION.md)
- **实施完成报告**: [`../reports/MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md`](../reports/MULTI_CLI_IMPLEMENTATION_COMPLETION_REPORT.md)

---

## 常见问题 (FAQ)

**Q: 任务可以被多个CLI同时认领吗？**
A: 不可以。每个任务同一时间只能被一个CLI认领。

**Q: 认领任务后可以释放吗？**
A: 可以。使用`--release`命令释放任务，任务状态恢复为open。

**Q: 如何查看所有已完成的任务？**
A: 查看`CLIS/SHARED/TASKS_POOL.md`的"已完成任务"部分。

**Q: 任务完成后会被删除吗？**
A: 不会。已完成任务保留在TASKS_POOL.md中，用于历史记录。

**Q: 可以修改已发布的任务吗？**
A: 当前版本不支持直接修改。建议先释放任务，然后重新发布。

**Q: main如何知道哪些任务已完成？**
A: 查看TASKS_POOL.md的统计信息和已完成任务列表。

---

**文档维护**: 本文档应随任务池系统的更新而维护
**最后更新**: 2026-01-01
**维护者**: Main CLI (Claude Code)
