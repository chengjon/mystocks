# Change: Connect Execution Tracking To miniQMT Evidence

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
The execution tracking workbench is now canonical for external trigger observation, but the first implementation still uses a process-local trigger ledger for demonstration and route tests. The repository already has miniQMT primary runtime ledgers for bridge submission attempts, live bridge follow-up incidents, and broker lifecycle correlation.

The next slice should connect the execution tracking aggregate to those existing evidence stores so `/trade/execution` can observe real miniQMT bridge evidence while preserving the safety contract that bridge receipts and bridge-only terminal results are not broker truth.

## What Changes
- Add an evidence source layer for execution tracking that reads miniQMT submission attempts by account, order id, and bridge task id.
- Preserve the existing in-memory trigger ledger only as a request-session fallback, not as the canonical evidence source.
- Enrich execution tracking details with bridge submission attempt evidence and live bridge follow-up incidents when available.
- Keep broker state as `review_required` unless broker lifecycle identity and acknowledgement status are present.
- Add tests proving bridge-only terminal evidence does not promote to broker acknowledgement or filled state.

## Impact
- Affected specs:
  - `trading-execution-safety`
- Affected code:
  - `web/backend/app/api/trade/execution_tracking_routes.py`
  - new backend execution tracking evidence service under `web/backend/app/services/trade/`
  - `src/application/trading/broker_submission_attempt.py`
  - optional read-only adapters around existing miniQMT divergence/correlation stores
  - `web/backend/tests/test_trade_execution_tracking_routes.py`
  - new backend tests for miniQMT evidence-source mapping
