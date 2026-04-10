# Triage: add-quantitative-trading-algorithms

> **治理裁定说明**:
> 本文件记录 2026-04-10 对 `add-quantitative-trading-algorithms` 的最终退场判断。
> 共享规则仍以 `architecture/STANDARDS.md` 为准；本文件只回答该 active change 现在是否还能继续保留。

## Decision

Retire `add-quantitative-trading-algorithms` from the active OpenSpec frontier using a retire-and-replace rationale.

## Why Retirement Is Now Required

- The change is not structurally valid as an active OpenSpec item: `openspec validate add-quantitative-trading-algorithms --strict` fails with `No delta sections found` and `Change must have at least one delta`.
- Its spec file is narrative documentation rather than a delta-based change file, so it cannot serve as an executable OpenSpec planning surface.
- Keeping an invalid change active would preserve a false execution surface and invite mechanical continuation of a 140-item checklist that OpenSpec itself rejects.

## Why This Is Not A "Nothing Exists" Judgment

Current repo evidence shows substantial implementation already exists outside the invalid change shell:

- Core algorithm modules exist in `src/algorithms/` across classification, pattern-matching, markov, bayesian, ngram, and neural slices.
- Backend algorithm-facing surfaces exist in:
  - `web/backend/app/api/algorithms/`
  - `web/backend/app/schemas/algorithm_schemas.py`
  - `web/backend/app/services/algorithm_service.py`
  - `web/backend/app/repositories/algorithm_model_repository/`
- Existing strategy code already imports algorithm implementations from `src/ml_strategy/strategy/ml_strategy_base.py`.

Retirement here means the active OpenSpec package is invalid and over-broad, not that the repo lacks quantitative algorithm work.

## Why Replacement Trunks Already Exist

The underlying intent is already better carried by current-truth trunks and repo surfaces:

- `openspec/specs/quantitative-trading-algorithms-api/spec.md`
  - formal capability trunk for the algorithm API contract surface
- `src/algorithms/`
  - current repo-truth for implemented quantitative algorithm modules
- `web/backend/app/api/algorithms/` and related schema/service/repository layers
  - current repo-truth for the exposed backend execution surface
- `src/ml_strategy/`
  - existing strategy/backtest integration surface that already consumes parts of the algorithm stack

## Why It Must Not Stay Active Anyway

Even with real code present, the proposal no longer works as a trustworthy active frontier item:

- It mixes core algorithm implementation, API exposure, frontend components, database/storage, GPU performance promises, and production-readiness into one oversized package.
- The advertised end-state over-claims closure relative to current repo truth; for example, service/export wiring is still uneven and broad frontend or E2E closure is not evidenced from this change.
- Some of the API-oriented intent is already represented more cleanly by the formal `quantitative-trading-algorithms-api` spec.

## Retirement Meaning

- Retirement does not mean quantitative algorithm capability is removed.
- Retirement means this invalid broad package is no longer the executable planning surface.
- Future work should be reopened as bounded follow-on changes only after restating current repo truth, for example:
  - algorithm export and service wiring closure
  - API contract completion for uncovered algorithm slices
  - concrete verification of GPU/performance claims
  - frontend integration as a separate scoped line if still needed

## Retirement Mode

- Remove the stale active change directory after this triage record is committed.
- Treat any remaining work as bounded follow-on planning under valid current-truth trunks rather than by reviving this invalid umbrella change.
