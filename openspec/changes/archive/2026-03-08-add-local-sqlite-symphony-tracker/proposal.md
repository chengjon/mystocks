# Add Local SQLite Symphony Tracker

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
