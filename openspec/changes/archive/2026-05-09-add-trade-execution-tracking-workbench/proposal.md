# Change: Add Trade Execution Tracking Workbench

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
Trading execution semantics need a canonical observation surface that separates external trigger and bridge evidence from broker truth. The current trade UI still risks implying that MyStocks executes real broker trades.

## What Changes
- Add `/api/v1/trade/execution-tracking` list and detail endpoints for execution-chain evidence.
- Add `/api/v1/trade/execution-tracking/trigger` for external trigger requests that return bridge receipt evidence only.
- Add `/trade/execution` as the trade-domain execution tracking workbench.
- Link execution tracking with `/trade/reconciliation` through account, order, and bridge task context.
- Keep `/api/v1/trade/execute` as legacy compatibility, not the canonical new trigger path.

## Impact
- Affected specs: `trading-execution-safety`, `trade-reconciliation-statement`, `frontend-routing`
- Affected code: `web/backend/app/api/trade/`, `web/frontend/src/api/`, `web/frontend/src/views/trade/`, `web/frontend/src/router/index.ts`, `web/frontend/src/layouts/MenuConfig.ts`
