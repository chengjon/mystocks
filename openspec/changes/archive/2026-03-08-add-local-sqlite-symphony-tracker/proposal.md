# Add Local SQLite Symphony Tracker

> **历史计划说明**:
> 本文件记录某次历史提案、计划或分工设想，反映的是当时准备推动的方向与范围，而非当前已生效事实。
> 若其内容与现行 `architecture/STANDARDS.md`、当前 `openspec/specs/`、已归档结论或实际实现不一致，应以 `architecture/STANDARDS.md`、当前 `openspec/specs/` 正式规格与实际实现为准，并将已归档结论仅视为历史背景。


## Why

MyStocks 当前的 Symphony 默认依赖 Linear 作为远程任务源，但项目当前使用方式以个人、本地为主，
远程 SaaS 增加了鉴权、网络和排障复杂度。需要一个不依赖第三方服务的本地 tracker 方案。

## What Changes

- 为 Symphony 增加 `tracker.kind: local`
- 使用 SQLite 作为默认本地 tracker 存储
- 新增本地 issue 管理 CLI
- 将仓库默认 `WORKFLOW.md` 从 Linear 切到本地 tracker
- 保留现有 Linear 代码路径，避免破坏性移除

## Impact

- Affected specs: `symphony-service`
- Affected code:
  - `src/services/symphony/`
  - `scripts/runtime/local_tracker.py`
  - `WORKFLOW.md`
  - `tests/unit/services/symphony/`
