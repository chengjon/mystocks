## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository already contains attribution-shaped traces, but none of them form a canonical attribution capability:

- `web/frontend/src/views/trade/Portfolio.vue`
  - currently renders local contribution cards based on weight and PnL
  - this is not formal Brinson attribution and not factor attribution
- `src/data_sources/real/composite_business.py`
  - exposes `perform_attribution_analysis(...)`, but its current payload is simplified and not a canonical v1 contract
- `src/data_sources/mock/business_mock.py`
  - exposes a mock attribution helper with its own drift-prone logic

The approved design closes this gap by adding one shared attribution engine and keeping strategy/backtest and trade/portfolio as separate domain shells over the same calculation truth source.

## Goals

- Add a formal shared attribution-analysis capability for one-period `Brinson + factor attribution`.
- Reuse one canonical calculation engine across:
  - selected backtest-result snapshots
  - current portfolio snapshots
  - date-scoped historical portfolio snapshots
- Expose aligned v1 entry points without collapsing strategy and trade into one mixed API surface.
- Reuse one shared frontend orchestration and presentation layer across both shells.

## Non-Goals

- User-switchable benchmarks in the first batch
- User-configurable factor sets in the first batch
- Rolling-window or time-series attribution
- A new premium external factor-data provider
- Manual attribution overrides or analyst-adjusted decompositions
- Continuing to treat local `Portfolio.vue` contribution cards as canonical attribution

## Decisions

- Decision: keep one shared attribution engine as the only calculation truth source
  - Rationale: strategy and trade must not drift into parallel Brinson or factor math.
- Decision: keep domain-specific entry shells instead of one mixed attribution endpoint
  - Rationale: backtest-result snapshots and trade portfolio snapshots have different semantics and stale/fail rules.
- Decision: lock the first-batch benchmark to `沪深300`
  - Rationale: this keeps Brinson semantics deterministic and repo-local.
- Decision: lock the first-batch factor set to `size`, `value`, `momentum`, `volatility`, and `quality`
  - Rationale: it matches the approved fixed-factor MVP and avoids user-configured factor drift.
- Decision: compute `PortfolioSnapshot.return` in adapters as interval return, not contribution
  - Rationale: contribution should remain an engine-derived value, not an input truth field.
- Decision: expose historical trade attribution through `GET /api/v1/positions/attribution?date=YYYY-MM-DD`
  - Rationale: one parameterized route is simpler than separate current/history routes for the MVP.

## Response Contract Notes

All first-batch attribution endpoints should align on one response model that includes:

- `analysis_date`
- `snapshot_meta`
- `benchmark_meta`
- `brinson`
- `factor_attribution`
- `top_contributors`
- `top_detractors`

`top_contributors` and `top_detractors` should be sorted by contribution value, not raw instrument return.

## Stale And Failure Semantics

- Strategy/backtest attribution
  - hard-fail if required benchmark, factor, or industry data is unavailable
- Trade attribution without `date`
  - may return attribution with `stale=true` and `stale_reason` when current snapshot enrichment is stale
- Trade attribution with `date`
  - hard-fail if the requested historical snapshot cannot be enriched consistently for that date

## Migration Boundary

- `Portfolio.vue` local contribution cards should stop acting as a competing attribution truth source
- `perform_attribution_analysis(...)` in real and mock data-source surfaces should become compatibility wrappers or explicitly legacy surfaces
- no second frontend attribution state machine may be introduced for strategy vs trade
