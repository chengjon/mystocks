# Mongo Multi-CLI Coordination Guide

## Purpose

本指南说明如何在 MyStocks 当前仓库内使用 `Maestro` 的 MongoDB 多 CLI 协作控制面。

操作层的命名规范、主/从 CLI 命令分工、以及当前有效任务编号，统一以
`docs/guides/MONGO_MULTICLI_OPERATION_CHECKLIST.md` 为准。
本文件保留为控制面能力说明；不要再以 `MT-*` 作为新的正式任务命名。

当前定位：

- 属于 `maestro.collab` 的下一代协作控制面
- 当前阶段先服务 `mystocks_spec`
- 当前阶段不作为平行于 `Maestro` 的独立系统运行

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
python scripts/runtime/coordctl.py work show 2026-03-14-api-route-governance-mystocks-spec1 --include-plan --output json
python scripts/runtime/coordctl.py work board --active-only --output json
python scripts/runtime/coordctl.py work transition 2026-03-14-api-route-governance-mystocks-spec1 --to merged --output json
```

```bash
python scripts/runtime/coordctl.py work claim 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Accepted task and started execution"
```

```bash
python scripts/runtime/coordctl.py plan add 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --title "Inspect current router state" \
  --order 10
```

```bash
python scripts/runtime/coordctl.py plan mark 2026-03-14-api-route-governance-mystocks-spec1 plan-abc123 \
  --actor-cli mystocks_spec1 \
  --status done \
  --evidence "Verified scoped prefixes and duplicate registrations"
```

```bash
python scripts/runtime/coordctl.py update add 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Implemented CLI command surface" \
  --status in_progress
```

```bash
python scripts/runtime/coordctl.py work submit 2026-03-14-api-route-governance-mystocks-spec1 \
  --actor-cli mystocks_spec1 \
  --summary "Code, verification, and TASK-REPORT are ready for review" \
  --commit abc123def \
  --branch mystocks_spec1 \
  --remote origin \
  --verify "pytest tests/unit/runtime -q"
```

## Real Smoke Verification

可直接运行真实 Mongo smoke：

```bash
python scripts/runtime/smoke_mongo_multicli.py \
  --mongo-uri 'mongodb://<user>:<password>@<host>:27017/admin?authSource=admin'
```

若不传 `--mongo-uri`，脚本会自动读取项目现有 Mongo 环境配置：

- `MONGODB_HOST` / `MONGODB_PORT`
- 或遗留 `MONGODB_IP`
- `MONGODB_ROOT_USERNAME` / `MONGODB_ROOT_PASSWORD`
- 或遗留 `USERNAME` / `PASSWORD`
- `MONGODB_AUTH_SOURCE`

当前仓库实测可直接无参运行：

```bash
python scripts/runtime/smoke_mongo_multicli.py
```

前提：

- 项目根目录 `.env` 已提供可写 Mongo 凭据
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

### 1B. Markdown Contract -> Mongo Control Plane

当前脚本也支持把 `TASK.md / TASK-REPORT.md` 的必要字段导入 Mongo control plane：

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

## Current Guarantees

- worker 不能直接改 `work_item` 定义
- worker 只能读取/写入自己 owner 的任务范围
- `work claim` / `plan add` / `plan mark` / `work submit` 已作为正式命令面提供
- `work_update` / `work_request` 会自动触发审计事件
- `worker_status_views` 会在任务、claim、plan、update、request、submit 变化后自动刷新
- `worker_status_views` 当前已汇总 claim、plan progress、delivery metadata
- 旧的 `assign/state/suggest` CLI 仍兼容
- `tracker.kind: mongo` 已可直接驱动 runtime candidate dispatch

## Current Limitations

- runtime 主流程仍以现有 `Symphony` orchestration 为核心
- `TASK.md` 仍承担任务契约作用，但现在应显式引导 worker 走 `claim -> plan -> submit`
- `TASK-REPORT.md` 仍保留为人工补充与导出摘要面
- 目前尚未实现完整的 `TASK.md / TASK-REPORT.md` 自动导入
- 目前尚未实现从 Mongo 自动导出 `TASK.md / TASK-REPORT.md`
- 目前尚未提供 Web UI
