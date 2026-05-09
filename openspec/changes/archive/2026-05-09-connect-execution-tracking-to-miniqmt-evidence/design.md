# Design: miniQMT Evidence Source For Execution Tracking

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Context
The current execution tracking API intentionally avoids claiming that `mystocks` performs real trading. It records external trigger intent and displays evidence chains. The next step is to replace the demonstration-only evidence source with a read-only aggregate over existing miniQMT runtime ledgers.

Existing relevant evidence:
- `src/application/trading/broker_submission_attempt.py` records local submission attempts, bridge task ids, transport status, external order ids, and source names.
- `src/application/trading/miniqmt_live_bridge_followup.py` records review-required incidents for timeout, invalid result, identity mismatch, auth failure, and bridge-only terminal result cases.
- broker lifecycle correlation stores may contain actual broker identity and acknowledgement state.

## Goals
- Make miniQMT submission-attempt evidence visible in `/api/v1/trade/execution-tracking`.
- Keep execution tracking read-only except for `/trigger`, which only records external trigger intent.
- Preserve the safety rule that bridge evidence is evidence, not broker truth.
- Keep existing route response models stable for the frontend.

## Non-Goals
- No real order placement implementation inside `mystocks`.
- No cancellation, retry, auto-repair, or manual disposition workflow.
- No production broker adapter declaration.
- No TdxQuant implementation beyond existing enum/extension slots.

## Approach
Introduce a small backend service that maps existing miniQMT evidence records into the current `ExecutionTrackingItem` and `ExecutionEvidenceEvent` shapes.

The route layer should delegate data loading to this service:
- internal statement projection remains a base signal
- miniQMT submission attempts add bridge evidence
- live bridge incidents add review timeline evidence
- broker lifecycle identity, when present, is the only basis for broker acknowledgement

The service must be dependency-injectable in tests so route tests can use in-memory stores without touching runtime SQLite paths.

## Safety Rules
- `bridge_task_accepted` means the bridge accepted a task; it does not mean broker acknowledgement.
- Bridge terminal evidence without `external_order_id` and broker lifecycle event type remains `review_required`.
- Identity mismatch, timeout, auth failure, invalid result, and bridge-only result incidents remain review evidence.
- The aggregate must not synthesize filled, partially filled, or broker acknowledged states from bridge status text.
