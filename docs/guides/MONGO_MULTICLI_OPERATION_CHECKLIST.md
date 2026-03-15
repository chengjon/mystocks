# Mongo Multi-CLI Operation Checklist

## Purpose

本清单用于约束 `mystocks_spec` 当前仓库内的 Mongo 多 CLI 派单、跟进、审查和归档操作。

当前执行口径：

- Mongo control plane 是任务派发与状态跟踪的实时事实源。
- `TASK.md` / `TASK-REPORT.md` 仍保留为人工可读的契约与汇报视图。
- 在“Mongo 导出 Markdown”自动化落地前，主 CLI 应先写 Mongo，再按需要镜像到任务文档。

---

## Naming Standard

### `work_item_id`

统一格式：

`YYYY-MM-DD-<task-content>-<worker-cli-normalized>`

示例：

- `2026-03-14-api-route-governance-mystocks-spec1`
- `2026-03-14-active-tree-legacy-cleanup-mystocks-spec2`

### `task_key`

统一格式：

`YYYY-MM-DD-<task-content>`

示例：

- `2026-03-14-api-route-governance`
- `2026-03-14-datasource-config-convergence`

### Hard Rules

- 一律使用小写 kebab-case。
- 日期使用首次派单日期，不使用“最后更新时间”。
- `task-content` 必须直接表达任务内容，不允许再使用 `MT-401`、`task-1` 这类无语义编号。
- 同一任务若发生实质性换轨，应新建一条任务并归档旧任务，不要复用旧 ID 冒充新范围。
- 不要只改 `work_item_id` 而保留原 `task_key`。
  - 当前 Mongo 索引同时要求 `work_item_id` 唯一，以及 `(branch, task_key)` 唯一。
  - 见 `src/services/maestro/collab/backends/mongo/indexes.py` 中的 `ux_work_items_work_item_id` 与 `ux_work_items_branch_task_key`。
- 当前控制面没有 `rename` 子命令。
  - 需要重命名时，使用“新建新命名任务 + 旧任务转 `archived`”的方式处理。

---

## Credential And Auth

### Credential Source

默认情况下，`coordctl.py` 会通过项目 `.env` 自动构造 Mongo 连接，而不是要求每次手写 URI。

读取链路：

- `scripts/runtime/coordctl.py`
- `scripts/runtime/maestro_collab.py`
- `src/utils/mongo_runtime_config.py`

显式覆盖方式：

```bash
python scripts/runtime/coordctl.py --mongo-uri 'mongodb://user:pass@host:27017/admin?authSource=admin' work list --output json
```

默认环境变量来源：

- `MONGODB_HOST` / `MONGODB_PORT`
- 或遗留 `MONGODB_IP`
- `MONGODB_ROOT_USERNAME` / `MONGODB_ROOT_PASSWORD`
- 或遗留 `USERNAME` / `PASSWORD`
- `MONGODB_AUTH_SOURCE`

### Current Auth Boundary

服务层授权规则当前是：

- `main_cli` / `system`
  - 可创建或更新 `work_item`
  - 可做状态流转
  - 可审核 `work_request`
  - 可维护 `worker_status_view`
- `worker_cli`
  - 只能对自己 `owner_cli` 的任务执行 `claim`
  - 只能对自己 `owner_cli` 的任务追加 `plan item`
  - 只能对自己 `owner_cli` 的任务追加 `update`
  - 只能对自己 `owner_cli` 的任务创建 `request`
  - 只能对自己 `owner_cli` 的任务执行 `submit`

### Operational Caveat

当前 `coordctl.py` 的 `work list` / `work show` 封装仍以主 CLI 身份读取控制面，不是严格的 worker 只读视图。

因此当前执行约束必须写清：

- `work list` 视为主 CLI 专用命令。
- worker 不应自己扫全量任务列表。
- main 派单时必须直接给出明确的 `work_item_id`。
- worker 若需要查询，仅查询 main 明确分配给自己的那一条任务。

换言之：当前“授权规则已存在”，但“命令面隔离还未完全封口”，不要把它误写成已经完成的凭证级多租户隔离。

---

## Current Active Work Items

| owner_cli | branch | work_item_id | task_key | title |
| --- | --- | --- | --- | --- |
| `mystocks_spec1` | `mystocks_spec1` | `2026-03-14-api-route-governance-mystocks-spec1` | `2026-03-14-api-route-governance` | API route registration and prefix governance |
| `mystocks_spec2` | `mystocks_spec2` | `2026-03-14-active-tree-legacy-cleanup-mystocks-spec2` | `2026-03-14-active-tree-legacy-cleanup` | Classify and clean active-tree legacy backup files |
| `mystocks_spec3` | `mystocks_spec3` | `2026-03-14-frontend-structure-convergence-mystocks-spec3` | `2026-03-14-frontend-structure-convergence` | Split oversized active frontend pages and remove hardcoded API/WebSocket usage |
| `mystocks_spec4` | `mystocks_spec4` | `2026-03-14-datasource-config-convergence-mystocks-spec4` | `2026-03-14-datasource-config-convergence` | Build source-of-truth matrix for YAML/JSON data source configs |
| `mystocks_spec5` | `mystocks_spec5` | `2026-03-14-govern-function-tree-as-code-mystocks-spec5` | `2026-03-14-govern-function-tree-as-code` | Govern function tree as code |

### Archived Generic IDs

2026-03-14 已归档的历史泛型 ID：

| archived_id | replacement |
| --- | --- |
| `MT-401` | `2026-03-14-api-route-governance-mystocks-spec1` |
| `MT-402` | `2026-03-14-active-tree-legacy-cleanup-mystocks-spec2` |
| `MT-403` | `2026-03-14-frontend-structure-convergence-mystocks-spec3` |
| `MT-404` | `2026-03-14-datasource-config-convergence-mystocks-spec4` |

---

## Main CLI Checklist

### 1. Verify Mongo control plane is reachable

```bash
python scripts/runtime/smoke_mongo_multicli.py
python scripts/runtime/coordctl.py work list --output json
```

### 2. Create a new work item

推荐由主 CLI 明确写入：

```bash
python scripts/runtime/coordctl.py work create \
  --work-item-id 2026-03-14-api-route-governance-mystocks-spec1 \
  --task-key 2026-03-14-api-route-governance \
  --title "API route registration and prefix governance" \
  --objective "Converge route registration entrypoints and normalize scoped non-/api prefixes." \
  --branch mystocks_spec1 \
  --owner-cli mystocks_spec1 \
  --status dispatched \
  --allowed-path web/backend/app/router_registry.py \
  --allowed-path web/backend/app/api/register_routers.py \
  --acceptance-check "pytest ..."
```

### 3. Re-dispatch or archive a replaced task

```bash
python scripts/runtime/coordctl.py work transition MT-401 --to archived --actor-cli main --output json
```

### 4. Inspect one task

```bash
python scripts/runtime/coordctl.py work show 2026-03-14-api-route-governance-mystocks-spec1 --output json
```

### 5. Review a worker request

```bash
python scripts/runtime/coordctl.py request review \
  2026-03-14-api-route-governance-mystocks-spec1 \
  2026-03-14-scope-change \
  --reviewed-by main \
  --status approved \
  --output json
```

### 6. Export Markdown snapshots when needed

```bash
python scripts/runtime/export_collab_snapshots.py \
  --output-dir reports/governance/mongo-collab-snapshots
```

### 7. Main CLI dispatch discipline

- 先创建 Mongo `work_item`，再通知 worker。
- 派单消息必须包含：
  - `work_item_id`
  - `branch`
  - `owner_cli`
  - 范围限制
  - 验收命令
- 若任务文档仍保留，文档中的任务编号应引用新的语义化 `work_item_id`，不要继续传播 `MT-*`。

### 8. Unified worker startup message template

当前可直接发给 worker 的统一开工指令模板如下：

```text
请按你当前 worktree 的 TASK.md 开工。

本次任务：
- work_item_id: <WORK_ITEM_ID>
- branch/worktree: <BRANCH_OR_WORKTREE>
- owner_cli: <WORKER_CLI>

先阅读：
1. Mongo control plane 中属于你的任务定义：
   python scripts/runtime/coordctl.py work show <WORK_ITEM_ID> --output json
2. 你当前 worktree 根目录下的 TASK.md 和 TASK-REPORT.md
3. 本任务涉及的 OpenSpec / docs / .FILE_OWNERSHIP / 其他约束文件

然后执行：
- 只做任务范围内修改
- 每完成一个批次就在 TASK-REPORT.md 记录证据
- 提交前做最小必要验证，并把命令和结果写入 TASK-REPORT.md
- 遇到范围冲突、定义不清、或不确定是否可删除的项，先停下来上报 main CLI

Mongo 协作要求：
- 开工时先 `work claim`
- 认领后立刻补 `plan add`
- 过程中按批次 `plan mark` / `update add`
- 准备交付时执行 `work submit`

禁止事项：
- 不要自行扩范围
- 不要修改未派发给你的 Mongo work item
- 不要继续使用 MT-* 这类无语义编号创建新任务
```

补充说明：

- 当前仓库尚未完成“从 Mongo 自动导出 `TASK.md` / `TASK-REPORT.md`”。
- 因此现在的正确口径是：
  - Mongo 读取任务定义与状态
  - 从当前 worktree 读取本地 `TASK.md` / `TASK-REPORT.md`
- 等 Mongo 导出链路完成后，再把上面的第 2 步改成“从 Mongo 导出快照中读取你的 `TASK.md` / `TASK-REPORT.md`”。

---

## Worker CLI Checklist

### 1. Do not self-discover the queue

当前 worker 不应以 `work list` 自行扫描控制面。

worker 启动输入应由 main 直接给出：

- `work_item_id`
- worktree / branch
- 允许修改路径
- 验收标准

### 2. Claim task receipt and start execution

```bash
python scripts/runtime/coordctl.py work claim \
  2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Synced worktree to main and started route audit" \
  --output json
```

### 3. Publish initial plan items

```bash
python scripts/runtime/coordctl.py plan add \
  2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --title "Inspect current router state" \
  --order 10 \
  --output json
```

### 4. Append progress updates

```bash
python scripts/runtime/coordctl.py update add \
  2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Verified duplicate router registration paths and collected scoped prefix mismatches" \
  --status in_progress \
  --output json
```

### 5. Mark plan progress

```bash
python scripts/runtime/coordctl.py plan mark \
  2026-03-14-api-route-governance-mystocks-spec1 \
  plan-abc123 \
  --actor-cli mystocks_spec1 \
  --status done \
  --evidence "Verified scoped prefixes and duplicate registrations" \
  --output json
```

### 6. Request a scope or definition change

```bash
python scripts/runtime/coordctl.py request create \
  2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --request-id 2026-03-14-scope-change \
  --request-type definition_change \
  --summary "Need one extra backend test file outside current allowed paths" \
  --output json
```

### 7. Submit completed work for review

```bash
python scripts/runtime/coordctl.py work submit \
  2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Code, tests, and TASK-REPORT are ready for main review" \
  --commit abc123def \
  --branch mystocks_spec1 \
  --remote origin \
  --verify "pytest tests/unit/runtime -q" \
  --output json
```

### 8. Worker CLI operating rules

- 只操作 main 明确派发给自己的 `work_item_id`。
- 不手工修改 Mongo collection。
- 不伪造别的 `actor_cli`。
- 不继续使用 `MT-*` 作为新任务编号。
- 若发现任务范围实质变化，先提 `request`，不要先改再补手续。

---

## Recommended Command Split

### Main CLI preferred commands

- `python scripts/runtime/smoke_mongo_multicli.py`
- `python scripts/runtime/coordctl.py work list --output json`
- `python scripts/runtime/coordctl.py work board --active-only --output json`
- `python scripts/runtime/coordctl.py work create ...`
- `python scripts/runtime/coordctl.py work show <work_item_id> --output json`
- `python scripts/runtime/coordctl.py work show <work_item_id> --include-plan --output json`
- `python scripts/runtime/coordctl.py work transition <work_item_id> --to <status> --actor-cli main --output json`
- `python scripts/runtime/coordctl.py request review <work_item_id> <request_id> --reviewed-by main --status approved --output json`

### Worker CLI preferred commands

- `python scripts/runtime/coordctl.py work claim <work_item_id> --actor-cli <worker_cli> --summary "..."`
- `python scripts/runtime/coordctl.py plan add <work_item_id> --actor-cli <worker_cli> --title "..." --order <n>`
- `python scripts/runtime/coordctl.py plan mark <work_item_id> <plan_item_id> --actor-cli <worker_cli> --status <status> --evidence "..."`
- `python scripts/runtime/coordctl.py update add <work_item_id> --actor-cli <worker_cli> --summary "..." --status in_progress`
- `python scripts/runtime/coordctl.py request create <work_item_id> --actor-cli <worker_cli> --request-id <request_id> --request-type definition_change --summary "..."`
- `python scripts/runtime/coordctl.py work submit <work_item_id> --actor-cli <worker_cli> --summary "..." --commit <sha> --branch <branch> --verify "..."`

### Commands workers should not treat as default workflow

- `python scripts/runtime/coordctl.py work list --output json`
- `python scripts/runtime/coordctl.py work create ...`
- `python scripts/runtime/coordctl.py work transition ...`

这些命令不是 worker 的默认工作流；即便在当前实现中“能跑”，也不代表它们符合协作边界。

---

## Rename / Archive Procedure

当已有任务命名不合规时，按下面顺序处理：

1. 设计新的 `work_item_id` 与 `task_key`
2. 用新命名创建新任务
3. 将 main 派单入口、worker 引用、任务文档引用切到新任务
4. 把旧任务转为 `archived`
5. 在汇报文档里保留旧 ID 到新 ID 的映射

禁止做法：

- 直接继续沿用 `MT-*`
- 只换 `work_item_id` 不换 `task_key`
- 直接手改 Mongo 主键而不处理 `work_updates` / `work_requests` / `work_events` / `worker_status_views`

---

## Status Note

截至 2026-03-15，本仓库已经具备“用 Mongo 进行主 CLI 派单、worker claim、plan progress、submit handoff、main 审核”的基础能力，但还没有完成以下事项：

- 由 Mongo 自动导出 `TASK.md` / `TASK-REPORT.md`
- 命令层面的严格 worker 只读列表/查看隔离
- 基于独立 worker 凭证的数据库级访问隔离

因此当前最佳实践是：

- 用 Mongo 作为实时控制面
- 用 Markdown 作为人类审阅和归档视图
- 由主 CLI 维持边界纪律，避免把“已有一部分授权规则”误当成“已完成全链路隔离”
