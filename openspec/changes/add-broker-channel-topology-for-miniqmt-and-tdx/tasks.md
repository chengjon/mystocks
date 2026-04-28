## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [x] 1.1 Add the `broker-truth-channel-topology` capability spec with requirements for primary-vs-supplemental channel roles, channel-scoped correlation identity, and channel-specific reconciliation authority.
- [x] 1.2 Validate that the new capability stays separate from the generic broker-truth foundation already covered by `add-broker-acknowledgement-reconciliation-contract`.

## 2. Line Split And Planning
- [x] 2.1 Publish a repo-visible line-splitting note that assigns ownership between the foundation line and the channel-topology line.
- [x] 2.2 Define the first implementation slices for:
  - registry update for `miniQMT` primary and Tongdaxin supplemental roles
  - channel-scoped correlation fields such as `broker_channel`, `adapter_path`, `account_scope`, and `session_scope`
  - `miniQMT` lifecycle ingestion path
  - Tongdaxin review-first supplemental path
- [x] 2.3 Define the acceptance evidence that must exist before this line may claim stronger channel-specific replay suppression or bounded auto-resolution behavior.

## 3. Channel Topology Implementation
- [x] 3.1 Update the broker execution truth registry to classify `miniQMT` as primary, Tongdaxin as supplemental, and orchestration-only surfaces as non-truth.
  - Repo-truth note: `docs/guides/quant-trading/broker-execution-truth-registry.md` now records `miniQMT` as the first `primary-candidate` through the existing `qmt` provider slot in `web/backend/app/services/windows_bridge_adapter.py`, records Tongdaxin semi-manual trading as `supplemental-operator-assisted`, and explicitly distinguishes both from existing orchestration surfaces and the repo's many market-data-only `tdx` paths. This closes topology publication only; channel-scoped correlation and live ingestion remain open.
- [x] 3.2 Extend the channel-scoped correlation model with `broker_channel`, concrete `adapter_path`, `account_scope`, and `session_scope`, plus tests preventing cross-channel identity collision.
  - Repo-truth note: `src/application/trading/broker_order_correlation.py` now persists `broker_channel` alongside `adapter_path`, `account_scope`, and `session_scope`, upgrades the SQLite ledger to channel-scoped indexes, and blocks ambiguous lookup reuse by returning `None` when `local_submission_id` or `external_order_id` collides across channels without an explicit `broker_channel`. `OrderManagementService.place_order()` currently writes the conservative `local_anchor` channel label, while `tests/ddd/test_phase_7_application.py` now verifies both the persisted field and cross-channel collision prevention for `miniqmt` vs `tdx_manual`. This closes correlation-boundary groundwork only; verified `miniQMT` / Tongdaxin lifecycle ingestion remains open in `3.3` and `3.4`.
- [x] 3.3 Introduce the first verified `miniQMT` broker-facing lifecycle ingestion path and normalize its payloads into `BrokerLifecycleEvent`.
  - Repo-truth note: `src/application/trading/miniqmt_lifecycle_ingestion.py` now normalizes `miniQMT` / Windows-bridge-style payload aliases such as `status`, `entrust_no`, `client_order_id`, `sequence_no`, and `updated_at` into `BrokerLifecycleEvent` with `broker_channel=miniqmt` and `source_name=miniqmt/windows_bridge`. `OrderManagementService.ingest_miniqmt_lifecycle_payload()` routes that normalized event through the existing broker lifecycle ledger and acknowledgement binding path, while `src/application/trading/broker_reconciliation.py` now resolves `local_submission_id` and `external_order_id` lookups with the optional channel scope when present. `tests/ddd/test_phase_7_application.py` verifies the end-to-end acknowledgement path from raw `miniQMT` payload to persisted lifecycle evidence and correlation binding.
- [x] 3.4 Add the Tongdaxin supplemental lifecycle capture path with default `review_required` reconciliation semantics unless stronger identity evidence exists.
  - Repo-truth note: `src/application/trading/tdx_manual_lifecycle_ingestion.py` now normalizes Tongdaxin semi-manual payload aliases such as `status`, `captured_at`, `external_order_id`, and `client_order_id` into `BrokerLifecycleEvent` with `broker_channel=tdx_manual` and `source_name=tdx/manual`. `OrderManagementService.ingest_tdx_manual_lifecycle_payload()` routes that event through the shared lifecycle ledger, and `src/application/trading/broker_reconciliation.py` now emits the explicit divergence category `supplemental_channel_review_required` for Tongdaxin supplemental events when no stronger identity contract exists. `tests/ddd/test_phase_7_application.py` verifies that a Tongdaxin acknowledgement is preserved in the lifecycle ledger, binds external identity back to correlation, and still lands a `review_required` divergence record rather than inheriting primary-path automation semantics.
- [x] 3.5 Add channel-specific replay suppression and bounded auto-resolution authority checks so unsupported channels cannot inherit primary-path privileges.
  - Repo-truth note: `src/application/trading/broker_reconciliation.py` now treats `miniQMT` as the only explicit channel with automated replay-suppression / auto-resolution authority; legacy generic events without `broker_channel` keep their existing foundation behavior, while `tdx_manual` and other explicit non-primary channels are blocked with `broker_channel_not_replay_authorized` and `broker_channel_not_auto_resolution_authorized`. Duplicate-event matching now also respects `broker_channel` when present. `tests/ddd/test_phase_7_application.py` verifies that Tongdaxin manual payloads do not suppress repeated lifecycle evidence and do not auto-resolve externally terminal rejects even when sequence identity is present.
- [x] 3.6 Update `docs/FUNCTION_TREE.md` and related trading docs to reflect the two-line topology once implementation evidence exists.
  - Repo-truth note: `docs/FUNCTION_TREE.md` now records the `miniQMT primary-candidate / Tongdaxin supplemental` broker-truth topology directly under `05-投资组合与交易`, links the domain to `docs/guides/quant-trading/broker-execution-truth-registry.md`, and points validation readers at `tests/ddd/test_phase_7_application.py` as the current DDD evidence for broker-truth foundation plus channel-topology work. `docs/guides/quant-trading/broker-execution-truth-registry.md` also reflects the current implementation boundary: repo-facing `miniQMT` lifecycle ingestion and Tongdaxin supplemental lifecycle capture now exist, while live broker-facing adapter proof and production-eligible execution closure still remain explicitly open.

## 4. Validation
- [x] 4.1 Run `openspec validate add-broker-channel-topology-for-miniqmt-and-tdx --strict`.
- [x] 4.2 Review the new line against:
  - `docs/reports/quality/Q2_WAVE3_BROKER_TRUTH_LINE_SUMMARY_2026-04-28.md`
  - `docs/superpowers/plans/2026-04-28-miniqmt-broker-reconciliation-implementation-plan.md`
  to confirm the split is complementary rather than duplicative.
- [x] 4.3 Run targeted trading tests and repo-truth review for each implementation batch before claiming channel-topology closure.
  - Repo-truth note: each implementation batch from `3.2` through `3.5` was closed only after rerunning `pytest tests/ddd/test_phase_7_application.py -q --cov-fail-under=0 -o log_cli=false` and revalidating `openspec validate add-broker-channel-topology-for-miniqmt-and-tdx --strict`. The current repo-truth closeout also routes readers through `docs/FUNCTION_TREE.md` and `docs/guides/quant-trading/broker-execution-truth-registry.md`, while the latest targeted trading run remains green at `52 passed`.
