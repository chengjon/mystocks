# Maestro Quick Start

本指南面向 MyStocks 当前仓库，目标是：在**本地 SQLite + 本地工作区 + 多 CLI 协作**模式下，把 Maestro 跑起来。

## 适用场景

适用于你想快速完成下面这条最小闭环：

1. 创建一个本地 issue
2. 写 `TASK.md`
3. 跑 owner suggestion
4. 做 assignment
5. 把 issue 推进到 `In Progress`
6. 启动 runtime
7. 查看状态 API

## 先决条件

- 已在仓库根目录执行
- Python 环境可用
- `codex app-server` 可执行
- 仓库里已有：
  - `WORKFLOW.md`
  - `.FILE_OWNERSHIP`
  - `scripts/runtime/local_tracker.py`
  - `scripts/runtime/maestro_collab.py`
  - `scripts/runtime/run_symphony.py`

## Step 0：准备环境变量

最小建议：

```bash
export SYMPHONY_WORKSPACE_ROOT='/tmp/symphony_workspaces'
export SYMPHONY_SOURCE_REPO='git@github.com:chengjon/mystocks.git'
export MAESTRO_CLI_NAME='main'
```

说明：

- `SYMPHONY_WORKSPACE_ROOT`：workspace 根目录
- `SYMPHONY_SOURCE_REPO`：after-create hook clone 使用的源仓库
- `MAESTRO_CLI_NAME`：当前 runtime 的 CLI 身份；`WORKFLOW.md` 已读取它

如果你仍沿用旧名字，也可以使用：

```bash
export SYMPHONY_CLI_NAME='main'
```

## Step 1：准备本地 tracker

默认 SQLite 文件：

```bash
.symphony/tracker.db
```

先看一下当前 issue：

```bash
python scripts/runtime/local_tracker.py --sqlite-path .symphony/tracker.db list
```

创建一个新 issue：

```bash
python scripts/runtime/local_tracker.py \
  --sqlite-path .symphony/tracker.db \
  create \
  --title 'Your task title' \
  --description 'Short task description' \
  --state 'Todo' \
  --labels 'maestro,local'
```

记下输出里的 identifier，例如 `LOCAL-3`。
下面凡是出现 `LOCAL-3` 的地方，都请替换成你实际创建出的 issue identifier。

## Step 2：起草 `TASK.md`

在 `TASK.md` 中至少写清：

- Scope Paths
- Suggested Owner
- Final Owner / Worker CLI
- Acceptance Summary

最小模板可直接参考：

- `docs/guides/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`

## Step 3：运行 owner suggestion

先根据 `TASK.md` 自动提取路径线索：

```bash
python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md
```

如果 `TASK.md` 路径不够明确，可手工补充：

```bash
python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md \
  --path src/services/maestro/collab/suggester.py \
  --path tests/unit/services/symphony/test_maestro_owner_suggester.py
```

解释规则：

- `suggested_owner` 是建议，不是最终分配
- 若输出 `main`，可能表示：
  - 未命中更细 owner
  - 多 owner 并列
  - 需要再拆任务

## Step 4：把最终 owner 写回 `TASK.md`

主 CLI 做最终判断后，把这些信息写回 `TASK.md`：

- `Suggested Owner`
- `Suggest Reasons`
- `Final Owner`
- `Worker CLI`
- `Decision Basis`

如果任务很小，最少也要保留这三行：

```markdown
- Suggested Owner: `<cli-x / main>`
- Final Owner / Worker: `<cli-x>`
- Assign Record: `<ISSUE-ID> | main | <验收摘要>`
```

## Step 5：持久化 assignment

假设最终决定由 `main` 处理，issue 是 `LOCAL-3`：

```bash
python scripts/runtime/maestro_collab.py \
  --sqlite-path .symphony/tracker.db \
  assign LOCAL-3 \
  --worker-cli main \
  --assigned-by main \
  --acceptance-summary '一句话写清验收口径'
```

查看 assignment：

```bash
python scripts/runtime/maestro_collab.py \
  --sqlite-path .symphony/tracker.db \
  state LOCAL-3
```

## Step 6：把 tracker 状态推进到 `In Progress`

```bash
python scripts/runtime/local_tracker.py \
  --sqlite-path .symphony/tracker.db \
  update-state LOCAL-3 'In Progress'
```

这是任务执行状态；它和 collab 里的 `assigned` 是两套不同但互补的状态。

## Step 7：启动 runtime

直接使用仓库自带入口：

```bash
python scripts/runtime/run_symphony.py WORKFLOW.md --port 8035
```

说明：

- 入口文件名还是 `run_symphony.py`
- 但它运行的正是当前这套本地优先的 Maestro/Symphony 兼容运行时
- `WORKFLOW.md` 已经配置为默认使用 local tracker

## Step 8：查看状态 API

运行后可看：

```bash
curl http://localhost:8035/api/v1/state
```

看某个 issue：

```bash
curl http://localhost:8035/api/v1/LOCAL-3
```

看 collab issue 状态：

```bash
curl http://localhost:8035/api/v1/collab/issues/LOCAL-3
```

看 workspaces：

```bash
curl http://localhost:8035/api/v1/collab/workspaces
```

看 stale：

```bash
curl http://localhost:8035/api/v1/collab/stale
```

## Step 9：常用命令速查

### 创建 issue

```bash
python scripts/runtime/local_tracker.py --sqlite-path .symphony/tracker.db create --title 'Example task'
```

### 列出 issue

```bash
python scripts/runtime/local_tracker.py --sqlite-path .symphony/tracker.db list
```

### 更新 issue 状态

```bash
python scripts/runtime/local_tracker.py --sqlite-path .symphony/tracker.db update-state LOCAL-3 'Done'
```

### 建议 owner

```bash
python scripts/runtime/maestro_collab.py suggest --ownership-path .FILE_OWNERSHIP --task-path TASK.md
```

### assignment

```bash
python scripts/runtime/maestro_collab.py --sqlite-path .symphony/tracker.db assign LOCAL-3 --worker-cli main
```

### 查看 assignment / heartbeat / workspace

```bash
python scripts/runtime/maestro_collab.py --sqlite-path .symphony/tracker.db state LOCAL-3
python scripts/runtime/maestro_collab.py --sqlite-path .symphony/tracker.db list-workspaces
python scripts/runtime/maestro_collab.py --sqlite-path .symphony/tracker.db list-stale
```

## 一个最小可运行示例

```bash
export SYMPHONY_WORKSPACE_ROOT='/tmp/symphony_workspaces'
export SYMPHONY_SOURCE_REPO='git@github.com:chengjon/mystocks.git'
export MAESTRO_CLI_NAME='main'

python scripts/runtime/local_tracker.py \
  --sqlite-path .symphony/tracker.db \
  create \
  --title 'Demo task' \
  --description 'Demo Maestro quick start' \
  --state 'Todo' \
  --labels 'demo,maestro'

python scripts/runtime/maestro_collab.py suggest \
  --ownership-path .FILE_OWNERSHIP \
  --task-path TASK.md

python scripts/runtime/maestro_collab.py \
  --sqlite-path .symphony/tracker.db \
  assign LOCAL-3 \
  --worker-cli main \
  --assigned-by main \
  --acceptance-summary 'Run Maestro quick start demo'

python scripts/runtime/local_tracker.py \
  --sqlite-path .symphony/tracker.db \
  update-state LOCAL-3 'In Progress'

python scripts/runtime/run_symphony.py WORKFLOW.md --port 8035
```

## 常见误区

### 1. `suggest` 不会自动 assignment

不会。`suggest` 只是建议层，最终仍是：

- 人工决定
- 写 `TASK.md`
- 执行 `assign`

### 2. `assigned` 不等于 `In Progress`

不是同一层状态：

- `assigned`：collab 机器态分配事实
- `In Progress`：tracker 中的任务执行状态

### 3. `Symphony` 和 `Maestro` 不是两套系统

当前不是。

更准确地说：

- `Symphony` 是现有兼容实现名
- `Maestro` 是未来长期家族名

## 推荐继续阅读

- `docs/guides/MAESTRO_SUMMARY.md`
- `docs/guides/SYMPHONY_LOCAL_MULTICLI_WORKFLOW.md`
- `src/services/maestro/README.md`
- `WORKFLOW.md`
