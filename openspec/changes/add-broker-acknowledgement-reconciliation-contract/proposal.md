# Change: Add Broker Acknowledgement And Reconciliation Contract

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
Wave 3 runtime hardening closed several local observability gaps for `cancel`, `reject`, and
`handle_execution_report(...)`, but the current trading path still stops at local application
truth. The repository now has stronger local audit evidence, yet it still lacks an approved
contract for broker-facing acknowledgement identity, external lifecycle truth, and
reconciliation boundaries.

Without that contract, the project cannot safely claim replay-safe execution-report handling,
broker-aligned terminal order truth, or production-eligible trading lifecycle guarantees.
Trying to implement "true idempotency" first would force heuristic duplicate suppression on
top of incomplete broker identity semantics.

## What Changes
- Add a new OpenSpec capability for broker acknowledgement and reconciliation.
- Define the minimum contract for local-to-external order identity binding, broker lifecycle
  event identity, divergence classification, and reconciliation resolution boundaries.
- Modify the trading execution safety spec so production-eligible claims and broker-facing
  replay suppression require an explicit broker truth contract.
- Modify architecture governance so any broker-facing execution path records its canonical
  adapter, lifecycle source, and reconciliation owner in a governance-visible registry.
- Keep this change strictly at the contract and planning layer; it does not introduce broker
  adapter implementation, external ingestion code, or automatic reconciliation logic.

## Impact
- Affected specs:
  - `broker-acknowledgement-reconciliation`
  - `trading-execution-safety`
  - `architecture-governance`
- Affected code:
  - future broker-facing execution adapter entrypoints under `src/` or `web/backend/`
  - `src/application/trading/order_mgmt_service.py`
  - local audit, order-state, and reservation evidence surfaces that will later bind to
    external broker truth
  - governance reports and source-of-truth documents that classify trading execution paths
