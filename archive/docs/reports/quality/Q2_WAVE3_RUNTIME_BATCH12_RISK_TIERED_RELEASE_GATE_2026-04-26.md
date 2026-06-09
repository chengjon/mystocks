# Q2 Wave 3 Runtime Batch 12 Risk-Tiered Release Gate

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-04-26
Wave: `Wave 3 / Trading Safety Runtime Hardening`
Mode: single-CLI execution
Related inputs:
- `docs/reports/quality/Q2_WAVE3_RUNTIME_BATCH11_MANUAL_RELEASE_AUDIT_TRAIL_2026-04-26.md`
- `docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md`
- `scripts/runtime/trading_cash_reservations.py`
- `tests/unit/runtime/test_trading_cash_reservations_cli.py`

## Purpose

This batch narrows the next governance step for manual reservation release.

The earlier follow-up direction was "stronger approval workflow". After operator-fit review for a private / small-fund operating model, that was intentionally refined into a smaller and more practical rule:

- automatic gate first
- strong audit always
- dual control only as an optional higher-governance review path

The goal is to reduce false process weight while keeping local release actions attributable and reviewable.

## Implemented Scope

### 1. Reservation age now drives the default gate

The `release` command now distinguishes:

- `auto_release`
  - stale reservation age is at or above `--stale-age-seconds`
- `review_required`
  - reservation is not stale and cannot be auto-released

This keeps the gate tied to a local fact already available in the runtime ledger instead of pretending broker-state validation exists.

### 2. Fresh reservations now require an explicit review path

When a reservation is not stale, the CLI now rejects the release by default with:

- `manual_reservation_release_review_required`

The operator must then choose one of two bounded review paths:

- `--allow-single-operator`
  - records an explicit single-operator override with durable audit
- `--approved-by <reviewer>`
  - records a dual-control review path

This means the tool no longer hard-codes dual control as the only possible governance path for a small team.

### 3. Dual control remains available, but is no longer mandatory

Dual control is still supported for higher-governance cases, and it now remains guarded by:

- actor and approver must be distinct

Rejected same-person approval attempts emit:

- `manual_reservation_release_approval_rejected`

### 4. Audit payload now preserves release-governance context

The durable local audit payload now also records:

- `approval_mode`
- `review_required`
- `reservation_age_seconds`
- `stale_age_seconds`
- `approved_by`
- `approval_note`

This makes later review more useful than a bare "release happened" record.

## What This Batch Does Not Claim

This batch does not claim:

- broker open-order reconciliation
- frozen-funds validation
- centralized approval workflow
- mandatory dual control for all operating contexts
- production-grade real-trading release safety

The execution path remains `experimental`.

## Verification

Operator tooling target:

- `pytest tests/unit/runtime/test_trading_cash_reservations_cli.py -q`
  - functional result: `8 passed`
  - covered behavior now includes:
    - stale reservation auto-release
    - fresh reservation review-required rejection
    - explicit single-operator override
    - explicit dual-control release
    - same-person approver rejection
  - command exits non-zero because repo-wide total coverage remains below configured `fail-under=80`
  - observed repo-wide coverage snapshot from this narrow run: `3.27%`

Trading regression target:

- `pytest tests/ddd/test_phase_7_application.py -q`
  - functional result: `20 passed`
  - command exits non-zero because the same repo-wide coverage threshold applies to narrow runs
  - observed repo-wide coverage snapshot from this narrow run: `3.83%`

## Follow-Up

The next bounded hardening choice should be one of:

1. add broker/open-order evidence so more non-stale release cases can be decided automatically,
2. add configurable thresholds for when fresh manual release should escalate from single-operator review to dual control,
3. or keep the current local CLI model and stop here until a real broker-adapter path exists.
