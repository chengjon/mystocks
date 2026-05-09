## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

MyStocks acts as the trade-domain data, trigger, observation, audit, and reconciliation platform. Actual order placement, cancellation, and broker lifecycle confirmation remain outside the process in miniQMT, TdxQuant, or another external program.

## Goals / Non-Goals
- Goals: expose canonical execution tracking endpoints, provide a trade-domain workbench, preserve bridge evidence, and link execution chains to reconciliation.
- Non-Goals: implement real broker execution, cancellation, automatic retry, manual remediation workflow, or a production broker adapter.

## Decisions
- Decision: use `execution-tracking/trigger` for new external trigger semantics.
- Decision: treat miniQMT bridge receipts as transport evidence only.
- Decision: keep `review_required` unless broker lifecycle identity such as `external_order_id` is present.
- Decision: keep `/api/v1/trade/execute` compatibility untouched and out of the new canonical UI.

## Risks / Trade-offs
- In-memory first-batch evidence is suitable for the local observation contract but not durable production audit retention.
- The list endpoint projects internal statement rows and trigger evidence together; broker truth still comes from lifecycle and reconciliation evidence, not from the trigger response.

## Migration Plan
1. Add the OpenSpec change and validate it.
2. Add backend route tests and implement the additive endpoints.
3. Add frontend API normalizers, route, menu item, and workbench page.
4. Keep legacy execution entrypoints available without linking the new page to them.
