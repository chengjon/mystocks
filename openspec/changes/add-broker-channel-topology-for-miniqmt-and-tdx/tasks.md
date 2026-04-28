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
- [ ] 3.2 Extend the channel-scoped correlation model with `broker_channel`, concrete `adapter_path`, `account_scope`, and `session_scope`, plus tests preventing cross-channel identity collision.
- [ ] 3.3 Introduce the first verified `miniQMT` broker-facing lifecycle ingestion path and normalize its payloads into `BrokerLifecycleEvent`.
- [ ] 3.4 Add the Tongdaxin supplemental lifecycle capture path with default `review_required` reconciliation semantics unless stronger identity evidence exists.
- [ ] 3.5 Add channel-specific replay suppression and bounded auto-resolution authority checks so unsupported channels cannot inherit primary-path privileges.
- [ ] 3.6 Update `docs/FUNCTION_TREE.md` and related trading docs to reflect the two-line topology once implementation evidence exists.

## 4. Validation
- [x] 4.1 Run `openspec validate add-broker-channel-topology-for-miniqmt-and-tdx --strict`.
- [x] 4.2 Review the new line against:
  - `docs/reports/quality/Q2_WAVE3_BROKER_TRUTH_LINE_SUMMARY_2026-04-28.md`
  - `docs/superpowers/plans/2026-04-28-miniqmt-broker-reconciliation-implementation-plan.md`
  to confirm the split is complementary rather than duplicative.
- [ ] 4.3 Run targeted trading tests and repo-truth review for each implementation batch before claiming channel-topology closure.
