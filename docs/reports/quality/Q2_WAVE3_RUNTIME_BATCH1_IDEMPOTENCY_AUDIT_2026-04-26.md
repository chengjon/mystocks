# Q2 Wave 3 Runtime Batch 1 Idempotency Audit

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_IDEMPOTENCY_AND_DEDUP_CONTRACT_2026-04-26.md`
- `docs/reports/quality/Q2_WAVE3_AUDIT_BINDING_AND_RETENTION_2026-04-26.md`
- `src/application/dto/trading_dto.py`
- `src/application/trading/order_mgmt_service.py`

## Purpose

This batch starts the runtime descent of the Wave 3 contract without widening scope into broker integration or pre-order risk gating.

## Implemented Scope

### 1. Canonical request identity fields

`CreateOrderRequest` now exposes optional request identity fields for the canonical placement path:

- `idempotency_key`
- `request_id`
- `actor_id`
- `source_id`

This makes the contract explicit in runtime DTOs instead of keeping it only in governance text.

### 2. Best-effort deduplication in canonical placement path

`OrderManagementService` now keeps a narrow in-memory idempotency cache keyed by `idempotency_key`.

Current runtime semantics:
- first request with a new key is submitted normally
- repeated request with the same key inside the configured TTL returns the first response
- duplicate effective intent therefore becomes an explicit `deduplicated` decision outcome rather than a second blind persistence

### 3. Decision-point audit hook

`OrderManagementService` now emits a decision payload at the decision point for:

- `submitted`
- `deduplicated`
- `rejected`

The current implementation uses an injectable `decision_audit_sink` plus structured logger emission.

This is a minimal runtime bridge toward the Wave 3 audit contract.

## What This Batch Does Not Claim

This batch does not claim:

- durable audit persistence is fully wired to the canonical trading path
- deduplication survives process restarts or multi-instance execution
- pre-order risk gating is implemented
- confirmation or approved bypass is implemented
- broker execution closure is verified

## Verification

Targeted tests added:
- submit path audit emission
- deduplication path behavior
- rejected decision audit emission

Primary test target:
- `pytest tests/ddd/test_phase_7_application.py -q`

## Follow-Up

The next runtime batch should:

1. replace or augment in-memory dedup with a stronger persistence-backed decision model
2. bind decision-point audit to a durable sink
3. add pre-order risk gate ahead of effective submission
