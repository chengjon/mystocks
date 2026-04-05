# Mongo Multi-CLI Coordination Guide

## Purpose

本指南说明如何在 MyStocks 当前仓库内使用 `Maestro` 的 MongoDB 多 CLI 协作控制面。

操作层的命名规范、主/从 CLI 命令分工、以及当前有效开工顺序，统一以
`docs/guides/multi-cli-tasks/MONGO_MULTICLI_OPERATION_CHECKLIST.md` 为准。
本文件保留为控制面能力说明；不要再以 `MT-*` 作为新的正式任务命名。

当前定位：

- 属于 `maestro.collab` 的下一代协作控制面
- 当前阶段先服务 `mystocks_spec`
- 当前阶段不作为平行于 `Maestro` 的独立系统运行

## Boundary With Graphiti

`Graphiti` 在当前项目中的定位是 AI 记忆层，不是 control plane。

必须遵守：

- Mongo 负责任务状态、派单、回执、计划、提审、验收、合并
- Graphiti 负责长期记忆、handoff 摘要、历史事实检索
- 任何 `work_item.status`、review decision、ownership 判断，都不能以 Graphiti 结果替代 Mongo

如果需要查看 Graphiti 的具体用法与 `group_id` 约定，统一参考：

- `docs/guides/ai-tools/GRAPHITI_MCP_WORKFLOW.md`

## Current Modes

当前支持三种 collab backend 模式：

- `sqlite`
  - 默认模式
  - runtime 继续使用本地 SQLite collaboration registry
- `mongo`
  - runtime 直接使用 MongoDB 保存 assignment/workspace/heartbeat
- `dual-write`
  - runtime 同时写 MongoDB 和 SQLite
  - 读路径优先使用 MongoDB

## Runtime Configuration

可在 `WORKFLOW.md` 的 `runtime` 段配置：

```yaml
runtime:
  cli_name: gemini
  reclaim_stale_assignments: true
  collab_backend: dual-write
  collab_mongo_uri: mongodb://localhost:27017
  collab_mongo_db: mystocks_coord
```

也可通过环境变量覆盖：

- `MAESTRO_COLLAB_BACKEND`
- `MAESTRO_COLLAB_MONGO_URI`
- `MAESTRO_COLLAB_MONGO_DB`

## Tracker Configuration

若希望 `Symphony` 直接从 Mongo `work_items` 调度任务，可在 `WORKFLOW.md` 中使用：

```yaml
tracker:
  kind: mongo
  mongo_uri: mongodb://localhost:27017
  mongo_db: mystocks_coord
  active_states:
    - created
    - dispatched
    - in_progress
    - ready_for_review
  terminal_states:
    - verified
    - merged
    - archived
```

含义：

- runtime candidate issue 来源改为 Mongo `work_items`
- 若 `worker_status_views` 有状态，则优先使用摘要状态
- 若没有摘要状态，则退回 `work_items.status`

## CLI Entry Points

### Legacy-Compatible Entry

```bash
python scripts/runtime/maestro_collab.py suggest --ownership-path .FILE_OWNERSHIP --task-path TASK.md
python scripts/runtime/maestro_collab.py assign MT-1 --worker-cli cli-1
python scripts/runtime/maestro_collab.py state MT-1
```

### Coordination Control Plane Entry

```bash
python scripts/runtime/coordctl.py work create \
  --work-item-id 2026-03-14-api-route-governance-mystocks-spec1 \
  --task-key 2026-03-14-api-route-governance \
  --title "API route registration and prefix governance" \
  --objective "Converge route registration entrypoints and normalize scoped non-/api prefixes." \
  --branch mystocks_spec1 \
  --owner-cli mystocks_spec1 \
  --allowed-path scripts/runtime \
  --acceptance-check "pytest tests/unit/runtime -q"
```

```bash
python scripts/runtime/coordctl.py work list --output json
python scripts/runtime/coordctl.py work show 2026-03-14-api-route-governance-mystocks-spec1 --output json
python scripts/runtime/coordctl.py work transition 2026-03-14-api-route-governance-mystocks-spec1 --to merged --output json
```

```bash
python scripts/runtime/coordctl.py work mark 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --status in_progress \
  --summary "Accepted task and started execution" \
  --output json
```

```bash
python scripts/runtime/coordctl.py update add 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Verified scoped prefixes and duplicate registrations" \
  --status in_progress \
  --output json
```

```bash
python scripts/runtime/coordctl.py request create 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --request-id req-scope-1 \
  --request-type definition_change \
  --summary "Need broader allowed path coverage" \
  --output json
```

```bash
python scripts/runtime/coordctl.py work preflight 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --task-path TASK.md \
  --output json
```

```bash
python scripts/runtime/coordctl.py update add 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Code, verification, and TASK-REPORT are ready for review" \
  --status ready_for_review \
  --output json
```

```bash
python scripts/runtime/coordctl.py work transition 2026-03-14-api-route-governance-mystocks-spec1 \
  --to ready_for_review \
  --actor-cli mystocks_spec1 \
  --output json
```

## Real Smoke Verification

可直接运行真实 Mongo smoke：

```bash
python scripts/runtime/smoke_mongo_multicli.py \
  --mongo-uri 'mongodb://<user>:<password>@<host>:27017/admin?authSource=admin'
```

若不传 `--mongo-uri`，脚本会自动读取项目现有 Mongo 环境配置：

- `MAESTRO_COLLAB_MONGO_URI`
- `COLLAB_MONGO_URI`
- `MONGODB_URI`
- `MONGO_URI`
- `MONGODB_HOST` / `MONGODB_PORT`
- 或遗留 `MONGODB_IP`
- `MONGODB_ROOT_USERNAME` / `MONGODB_ROOT_PASSWORD`
- 或遗留 `USERNAME` / `PASSWORD`
- `MONGODB_AUTH_SOURCE`

优先级规则：

- 显式 `--mongo-uri` 最高优先
- 未显式传入时，先按 URI 环境变量顺序解析
- 只有 URI 环境变量都不存在时，才回落到 host/port + username/password + authSource
- 若上述路径仍未提供账号密码，且本机存在 `mystocks-mongodb` 容器，脚本会尝试从容器初始化环境中读取 root 凭据作为 local-only fallback
- 同样的 local-only fallback 也适用于共享 CLI 入口 `coordctl.py` / `maestro_collab.py` 的 Mongo control-plane 命令

只有在当前会话已经提供可写 Mongo 凭据时，才建议无参运行：

```bash
python scripts/runtime/smoke_mongo_multicli.py
```

前提：

- 项目根目录 `.env` 或当前 shell 环境已提供可写 Mongo 凭据
- 或本机 Docker 中存在可访问的 `mystocks-mongodb` 容器，并保留了初始化 root 凭据
- 本机会话允许访问该 Mongo 实例

输出示例：

```json
{
  "assignment_status": "retrying",
  "control_plane_status": "ready_for_review",
  "db_name": "mystocks_coord_smoke_xxxxxxxx",
  "status_api_control_plane_count": 1,
  "work_item_id": "SMOKE-1"
}
```

说明：

- 该脚本会创建唯一临时数据库
- 执行 control-plane -> runtime -> status API 的 smoke 链路
- 执行结束后自动删除临时数据库
- 本地 Mongo 若开启鉴权，必须传入可写认证 URI
- 若凭据无效或无写权限，相关 CLI / smoke / 导出 / 迁移脚本会返回结构化 JSON 错误，至少包含 `error_code` 与 `message`

## Validated Local Commands

在当前本机 WSL + Docker 环境下，以下命令已实际验证：

```bash
python scripts/runtime/coordctl.py work list --output json
python scripts/runtime/smoke_mongo_multicli.py
python scripts/runtime/smoke_graphiti_preflight.py --actor-cli cli-preflight
python scripts/runtime/export_collab_snapshots.py --output-dir /tmp/mongo-collab-snapshots-codex
```

预期：

- `coordctl.py work list --output json` 返回 Mongo control plane 中的 work item 列表
- `smoke_mongo_multicli.py` 返回 `work_item_id=SMOKE-1` 与 `control_plane_status=ready_for_review`
- `smoke_graphiti_preflight.py --actor-cli cli-preflight` 返回 `server_status=ok` 与 `search_outcome=hit`
- `export_collab_snapshots.py --output-dir /tmp/mongo-collab-snapshots-codex` 在目标目录生成快照文件

### One-Command Local Acceptance

如果需要把 Mongo control plane、Graphiti preflight、以及快照导出串成一条本机验收链路，统一使用：

```bash
bash scripts/runtime/run_local_maestro_acceptance.sh
```

该脚本会顺序执行并落盘：

- `python scripts/runtime/coordctl.py work list --output json`
- `python scripts/runtime/smoke_mongo_multicli.py`
- `python scripts/runtime/smoke_graphiti_preflight.py --actor-cli cli-preflight`
- `python scripts/runtime/export_collab_snapshots.py --output-dir /tmp/mongo-collab-snapshots-codex`

默认输出位置：

- `/tmp/maestro_work_list.json`
- `/tmp/maestro_mongo_smoke.json`
- `/tmp/maestro_graphiti_preflight.json`
- `/tmp/mongo-collab-snapshots-codex`

适用场景：

- cleanup wave 收尾时做本机一键回归
- 向主 CLI / reviewer 证明当前 Mongo + Graphiti 收敛线可复跑
- 需要快速确认共享 CLI 入口与导出快照没有漂移

## Migration Scripts

### 1. SQLite Runtime Facts -> Mongo Runtime Registry

```bash
python scripts/runtime/migrate_collab_to_mongo.py \
  --sqlite-path .symphony/tracker.db \
  --mongo-uri mongodb://localhost:27017 \
  --mongo-db mystocks_coord
```

用途：

- 导入已有 SQLite runtime facts
- 覆盖 assignment
- 覆盖 workspace/worktree registry
- 覆盖 heartbeat/stale 数据

### 1B. Legacy Markdown Contract -> Mongo Control Plane

当前脚本也支持把旧的 `TASK.md / TASK-REPORT.md` 的必要字段导入 Mongo control plane，
仅用于兼容历史任务，不应作为新任务主流程：

- `Issue Identifier`
- `Issue Title`
- `Assigned Worker CLI`
- `Acceptance Summary`
- `Latest Progress`

当前实现是最小导入，不做通用 Markdown 语义解析。

### 2. Export Markdown Snapshots

```bash
python scripts/runtime/export_collab_snapshots.py \
  --mongo-uri mongodb://localhost:27017 \
  --mongo-db mystocks_coord \
  --output-dir reports/governance/mongo-collab-snapshots
```

用途：

- 从 Mongo control plane 导出 Markdown 快照
- 供主 CLI 审阅、归档、回放
- 供 worker worktree 生成只读 `TASK.md` / `TASK-REPORT.md`
- 在当前本机 WSL + Docker 环境下，若未显式传 `--mongo-uri`，该脚本同样会复用 `mystocks-mongodb` 容器的 local-only 凭据 fallback

### 2B. Export Worktree Task Artifacts

```bash
python scripts/runtime/coordctl.py work export-task <WORK_ITEM_ID> \
  --output-path /path/to/TASK.md \
  --output json

python scripts/runtime/coordctl.py work export-task-report <WORK_ITEM_ID> \
  --output-path /path/to/TASK-REPORT.md \
  --output json
```

用途：

- 从 Mongo 主事实源生成 worker 可读快照
- 避免继续手工维护 active `TASK.md`
- 保留 `请按你当前 worktree 的 TASK.md 开工。` 这句口令，但让 `TASK.md` 不再是人工主源

## Current Guarantees

- worker 不能直接改 `work_item` 定义
- worker 只能读取/写入自己 owner 的任务范围
- `work mark` / `update add` / `request create|review` / `work transition` 已作为正式命令面提供
- `work_update` / `work_request` 会自动触发审计事件
- `worker_status_views` 会在任务、update、request 变化后自动刷新
- `worker_status_views` 当前已汇总最新状态、最近更新、pending request 标记
- 旧的 `assign/state/suggest` CLI 仍兼容
- `tracker.kind: mongo` 已可直接驱动 runtime candidate dispatch

## Current Limitations

- runtime 主流程仍以现有 `Symphony` orchestration 为核心
- 历史任务仍可能残留手工 `TASK.md` 契约
- `TASK-REPORT.md` 仍允许人工追加异常说明，但 active 状态不应以其为准
- 旧文档与旧脚本仍有部分 `TASK.md` 人工主源口径，需分阶段清理
- 目前尚未提供 Web UI
