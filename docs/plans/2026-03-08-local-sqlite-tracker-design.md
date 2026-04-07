# Symphony Local SQLite Tracker Design

> **设计方案说明**:
> 本文件是架构设计、界面设计、系统模型、规格定义或映射方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先遵循 `architecture/STANDARDS.md`；若涉及仓库执行流程、命令或协作约束，再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、视觉规范和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


## Context

MyStocks 已经有一套基于 `src/services/symphony/` 的 Symphony 实现，但当前工作流默认依赖
Linear 作为远程 issue tracker。对本项目当前“个人、本地、低外部依赖优先”的使用方式来说，
Linear 带来了不必要的网络、鉴权和远程状态调试成本。

目标不是推翻 Symphony 调度模型，而是把“任务源”从远程 Linear 切换为本地 SQLite，同时保留
未来迁移到 PostgreSQL 的清晰路径。

## Goals

- 为 Symphony 增加 `tracker.kind: local` 能力
- 使用 SQLite 作为默认本地 tracker 存储
- 保留当前 orchestrator/runner 的主要代码路径，避免大范围重写
- 提供最小本地 issue 管理 CLI，覆盖创建、查看、状态更新
- 让本地 tracker 数据模型未来易于迁移到 PostgreSQL

## Non-Goals

- 本次不移除现有 Linear 支持
- 本次不做 Web 管理界面
- 本次不把 orchestrator 的运行态、retry 队列和 worker 会话全部持久化
- 本次不同时实现 PostgreSQL 后端
- 本次不实现本地版 `linear_graphql` 替代工具

## Recommended Approach

采用“方案 B”：

- 一张 `issues` 当前态表
- 一张 `issue_events` 事件表
- Symphony 继续使用现有内存调度状态
- 通过新增 `LocalIssueTrackerClient` 替换远程 Linear 查询

这是当前最平衡的方案：

- 比单表方案更容易排障和回放
- 比完整工作流引擎持久化方案更轻
- 数据结构天然可迁移到 PostgreSQL

## Architecture

### 1. Tracker Config

扩展 `TrackerConfig`：

- 允许 `kind` 取值为 `linear` 或 `local`
- 新增 `sqlite_path`
- 当 `kind=local` 时，默认 SQLite 路径为 `.symphony/tracker.db`

### 2. Tracker Client Abstraction

新增一个本地 tracker 客户端，遵循现有 orchestrator 所需接口：

- `fetch_candidate_issues()`
- `fetch_issues_by_states(state_names)`
- `fetch_issue_states_by_ids(issue_ids)`
- `close()`

Linear 客户端保留不动，服务层通过工厂函数按 `tracker.kind` 创建具体实现。

### 3. SQLite Schema

#### `issues`

- `id`
- `identifier`
- `title`
- `description`
- `state`
- `state_normalized`
- `priority`
- `branch_name`
- `url`
- `labels_json`
- `blocked_by_json`
- `created_at`
- `updated_at`

#### `issue_events`

- `id`
- `issue_id`
- `event_type`
- `payload_json`
- `created_at`

`issues` 是读模型，`issue_events` 是审计/排障辅助表。后续迁移到 PostgreSQL 时，这两个表可直接
平移。

### 4. Local Tracker CLI

新增一个最小 CLI：

- `create`
- `list`
- `update-state`

这样用户不需要手工写 SQL，也不依赖外部服务就能把任务送入 Symphony。

### 5. Workflow Switch

将仓库根 `WORKFLOW.md` 切换为：

- `tracker.kind: local`
- `tracker.sqlite_path: $SYMPHONY_TRACKER_DB`（或默认路径）

并移除对 Linear API key 和 `linear_graphql` 工具的依赖。

## Data Flow

1. 用户通过本地 tracker CLI 创建或更新 issue
2. 数据写入 SQLite `issues` 表，并追加一条 `issue_events`
3. Symphony 轮询 `LocalIssueTrackerClient`
4. Orchestrator 读取候选 issue 并执行现有工作区/agent 流程
5. 用户继续通过 CLI 改状态，Symphony 在下一轮 reconciliation 中感知变化

## Error Handling

- SQLite 文件不存在时自动建库建表
- 无法解析 JSON 字段时返回结构化错误或安全默认值
- 非法状态更新通过 CLI 拒绝并给出明确错误
- 配置不完整时在 `validate_dispatch_config()` 阶段阻塞启动

## Migration to PostgreSQL

这次实现将遵循两个原则，确保未来迁移成本低：

1. **业务接口与存储解耦**
   - Orchestrator 只依赖 tracker client 接口
2. **表结构保持通用**
   - JSON、时间戳、字符串列尽量不用 SQLite 独占技巧

未来切 PostgreSQL 时，优先新增 `PostgresIssueTrackerClient`，再提供数据迁移脚本即可。

## Testing Strategy

按 TDD 垂直切片推进：

1. 配置允许 `local` tracker，并解析默认 SQLite 路径
2. 本地 tracker SQLite schema 初始化与基础查询
3. 服务层按 `tracker.kind` 创建正确 client
4. 本地 CLI 创建/list/状态更新
5. `WORKFLOW.md` 切到本地 tracker 后的短时 dry-run
