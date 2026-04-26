# Change: Plan Q2 Optimization Closure Program

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Why
`docs/reports/quality/MYSTOCKS_PHASE_EVALUATION_2026Q2.md` concludes that the project already has a workable architecture skeleton, but Q2 closure is blocked by several cross-cutting truth gaps:

- realtime delivery paths are split across multiple backend entrypoints without one canonical registry
- backend composition truth is not strict enough between `web/backend/app/main.py` and `web/backend/app/app_factory.py`
- data quality responsibilities are present but not yet governed as a single closure surface
- trading execution safety expectations are discussed in reports but not yet codified as a formal capability contract
- function-tree "completion" semantics are still too narrative and not criteria-backed
- evaluation and closure evidence are not yet normalized as a repeatable governance requirement

The report also collected optimization opinions and risks. Some are immediately suitable as governance requirements, while others should remain deferred until core truths are stabilized. This change creates the umbrella OpenSpec program for that staged closure work.

`docs/reports/quality/Q2_CLOSURE_PROGRAM_SPEC_REVIEW.md` further confirms the proposal direction as "PASS WITH SUGGESTIONS". This change absorbs the review items that tighten safety and cross-spec consistency without expanding the proposal into implementation-detail sprawl.

## What Changes
This proposal defines a Q2 architecture and quality closure program with sequential, single-CLI execution as the default model.

It introduces or extends requirements to:

1. establish a canonical realtime delivery truth registry and transport selection rule
2. require one explicit backend app composition source-of-truth
3. formalize unified data-quality governance as a standalone capability
4. formalize trading execution safety as a standalone capability
5. harden function-tree completion with criteria-backed semantics
6. require closure-wave evidence before claims of Q2 completion

It also incorporates the following review-driven adjustments:

1. make the realtime truth registry and canonical transport selection explicitly consistent across specs
2. require durable trading audit storage and a defined minimum retention period
3. require pre-execution trading risk gates for capital or exposure threshold breaches
4. clarify that data quality governance must identify storage-specific concerns in multi-engine scenarios
5. clarify the functional meaning of safety-sensitive completion claims

The following review suggestions remain intentionally deferred:

- observability-specific Q2 spec deltas remain follow-up work instead of being folded into this change
- closure-wave evidence remains in `code-quality` for now to avoid reshuffling base responsibility during this proposal step

The proposal is intentionally governance-first. It does not claim that the underlying implementation is already complete.

## Impact
- Affected specs:
  - `architecture-governance`
  - `code-quality`
  - `function-tree-governance`
  - `api-integration`
  - new `data-quality-governance`
  - new `trading-execution-safety`
- Likely affected surfaces in later implementation waves:
  - `web/backend/app/main.py`
  - `web/backend/app/app_factory.py`
  - `web/backend/app/services/**`
  - `web/backend/app/api/websocket.py`
  - `web/backend/app/api/realtime_market.py`
  - `web/backend/app/core/socketio_manager.py`
  - `web/backend/app/services/streaming/**`
  - `src/core/data_quality_validator.py`
  - `src/monitoring/data_quality_monitor.py`
  - `src/data_governance/**`
  - `src/application/trading/**`
  - `src/domain/trading/**`
  - `src/infrastructure/logging/**`
  - `docs/FUNCTION_TREE.md`
  - `governance/function-tree/**`
  - `architecture/STANDARDS.md`
- Breaking changes: none in this proposal-only step

## Execution Model
- Default execution SHALL be single-CLI, staged, and sequential.
- Cross-cutting truth-setting work SHALL NOT start as multi-CLI parallel implementation by default.
- Multi-CLI or Mongo-coordinated work MAY be introduced only after the canonical truths, write scopes, and closure gates are stable, and only for low-coupling follow-up work such as isolated adapters, documentation fill-in, or low-risk verification expansion.
