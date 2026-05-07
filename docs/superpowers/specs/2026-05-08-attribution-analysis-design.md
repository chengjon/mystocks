# Attribution Analysis Design

> **权威来源声明**:
> 本文件是专题设计说明，不是仓库共享规则的唯一事实来源。
> 若涉及仓库级共享规则、审批门禁或治理口径，请优先阅读 `architecture/STANDARDS.md`；若涉及执行入口、提案流程或当前实现事实，再分别参考根目录 `AGENTS.md`、根目录 `CLAUDE.md`、`openspec/AGENTS.md` 与当前代码。

## Context

`FUNCTION_TREE` currently marks `3.3 归因分析` as unfinished and describes it as `Brinson归因、因子归因`. The repository does contain attribution-shaped traces, but none of them form a canonical, user-facing attribution capability.

Current repository truth is:

- `web/frontend/src/views/trade/Portfolio.vue`
  - renders a local "绩效归因" card list based on weight and PnL contribution
  - this is not formal Brinson attribution and not factor attribution
- `src/data_sources/real/composite_business.py`
  - exposes `perform_attribution_analysis(...)`, but it currently returns a simplified mock-shaped result
- `src/data_sources/mock/business_mock.py`
  - exposes a mock attribution helper, not a canonical production contract
- strategy/backtest surfaces and trade/portfolio surfaces both exist
  - but there is no unified attribution engine, no stable API contract, and no dual-domain closure

The next feature should close `3.3 归因分析` as a formal repo-local capability without collapsing strategy/backtest analysis and trade/portfolio analysis into one mixed page.

## Goals

- Add a formal shared attribution-analysis capability that supports:
  - `Brinson attribution`
  - `factor attribution`
- Keep one shared calculation truth source and expose it through:
  - strategy/backtest domain entry points
  - trade/portfolio domain entry points
- Lock the first-batch benchmark to `沪深300`.
- Lock the first-batch factor set to:
  - `规模`
  - `价值`
  - `动量`
  - `波动率`
  - `质量`
- Support first-batch analysis targets:
  - strategy domain: selected backtest-result snapshot
  - trade domain: current live portfolio snapshot
  - trade domain: specified-date historical portfolio snapshot
- Provide one shared frontend component skeleton and one shared frontend orchestration model for both domains.

## Non-Goals

- Do not treat the current `Portfolio.vue` local contribution cards as canonical attribution.
- Do not unify strategy and trade into one giant mixed API.
- Do not implement rolling-window attribution or time-series attribution in this batch.
- Do not support user-switchable benchmarks in the first batch.
- Do not support user-configurable factor sets in the first batch.
- Do not depend on a new external premium factor-data provider.
- Do not expose internal factor-construction formulas as public API fields.
- Do not implement manual attribution overrides or analyst-adjusted decompositions.

## Chosen Scope

The approved first-batch scope is:

- dual-domain shared attribution engine
- dual domain-specific API entries
- one-period attribution only
- fixed benchmark: `沪深300`
- fixed factor set:
  - `size`
  - `value`
  - `momentum`
  - `volatility`
  - `quality`
- strategy-side analysis object:
  - selected backtest-result snapshot
- trade-side analysis objects:
  - current real portfolio snapshot
  - specified-date historical portfolio snapshot
- frontend shared component skeleton with both strategy and trade shells

## Capability Boundary

This feature adds a formal attribution-analysis capability. It does not merely extend one existing view.

### Shared truth source

The attribution engine is the only calculation truth source.

- the engine accepts unified snapshot inputs
- the engine returns one canonical attribution response model
- strategy and trade domains may adapt different raw inputs
- they may not implement different Brinson or factor math

### Domain shells

The first batch intentionally keeps domain shells separate:

- strategy/backtest shell
  - focused on selected backtest-result snapshots
- trade/portfolio shell
  - focused on current and historical portfolio snapshots

This preserves domain semantics while keeping computation unified.

### Explicit non-truth surfaces

The following existing surfaces are not canonical attribution truth sources:

- `web/frontend/src/views/trade/Portfolio.vue` current local contribution list
- `src/data_sources/real/composite_business.py` current simplified attribution payload
- `src/data_sources/mock/business_mock.py` random attribution helper

## Shared Engine Contract

The shared engine should operate on three normalized inputs.

### PortfolioSnapshot

Represents the portfolio being analyzed at a single attribution point.

At minimum it should include:

- `analysis_date`
- `symbol`
- `weight`
- `market_value`
- `return`
- `industry`

`PortfolioSnapshot.return` is explicitly defined as the instrument return over the attribution interval, computed by the domain adapter. It is not a contribution field. The engine consumes the instrument return and derives portfolio-level contribution from weight and return.

### BenchmarkSnapshot

Represents the `沪深300` benchmark at the same attribution point.

At minimum it should include:

- `analysis_date`
- `symbol`
- `weight`
- `return`
- `industry`

### FactorSnapshot

Represents factor exposures for the analyzed portfolio and the benchmark.

At minimum it should include:

- `analysis_date`
- `size`
- `value`
- `momentum`
- `volatility`
- `quality`

The factor-construction formulas are an implementation-level internal standard, not an external API contract. First-batch implementation should still standardize them internally:

- size: log free-float market cap
- value: inverse PB or inverse PE
- momentum: trailing 12-month return excluding the latest month
- volatility: trailing 60-day annualized volatility
- quality: ROE or gross-profit-to-assets proxy

## Output Model

All first-batch attribution endpoints should return the same `AttributionAnalysisResponse`.

At minimum it should include:

- `analysis_date`
- `snapshot_meta`
- `benchmark_meta`
- `brinson`
- `factor_attribution`
- `top_contributors`
- `top_detractors`

### analysis_date

`analysis_date` is required in the public response.

- for current trade portfolio attribution
  - it is the effective snapshot date used by the calculation
- for historical trade attribution
  - it is the requested historical snapshot date
- for backtest-result attribution
  - it is the backtest result snapshot date used by the adapter

This field exists to support frontend display, cache correctness, and audit clarity.

### Brinson output

The first batch should expose:

- `allocation_effect`
- `selection_effect`
- `interaction_effect`
- `industry_breakdown[]`

Each `industry_breakdown` row should include, at minimum:

- `industry`
- `portfolio_weight`
- `benchmark_weight`
- `portfolio_return`
- `benchmark_return`
- `allocation_effect`
- `selection_effect`
- `interaction_effect`

### Factor attribution output

The first batch should expose two layers:

- `factor_exposures`
  - portfolio exposures
  - benchmark exposures
  - active exposures
- `factor_contributions`
  - contribution per factor
  - residual or specific return

### Top lists

`top_contributors` and `top_detractors` should be sorted by contribution value, not by raw instrument return.

The sort basis should be the first-batch contribution metric:

- `instrument contribution = weight * instrument return`

This better reflects actual impact on total portfolio return.

## API Shape

The first batch should use dual entry points with one shared response shape.

### Strategy domain

- `GET /api/v1/strategy/backtests/{backtest_id}/attribution`

This endpoint analyzes the selected backtest-result snapshot.

### Trade domain

- `GET /api/v1/trade/portfolio/attribution`

Query behavior:

- no `date` parameter
  - analyze the current live portfolio snapshot
- `date=YYYY-MM-DD`
  - analyze the specified historical portfolio snapshot

This parameterized trade endpoint is preferred over separate `/history` attribution endpoints for the first batch.

## Frontend Information Architecture

The frontend should use dual shells over a shared attribution presentation layer.

### Strategy shell

The strategy shell lives inside the backtest workflow and focuses on:

- selected backtest-result snapshot
- backtest attribution summary
- strategy-domain context text

### Trade shell

The trade shell lives inside the portfolio workflow and focuses on:

- current portfolio attribution
- specified-date historical attribution
- trade-domain context text

### Shared component skeleton

The first batch should introduce shared attribution components such as:

- `AttributionOverviewCards.vue`
- `BrinsonBreakdownPanel.vue`
- `IndustryAttributionTable.vue`
- `FactorExposureChart.vue`
- `FactorContributionChart.vue`
- `TopContributorsTable.vue`
- `AttributionEmptyState.vue`
- `AttributionErrorState.vue`

These components should be shared across both strategy and trade shells. The shells may differ in selectors, labels, and context copy, but not in attribution math or result interpretation.

## Shared Logic and Reuse Rules

The following rules should be treated as hard design constraints:

- the shared attribution engine is the only calculation truth source
- strategy and trade domains may only contribute normalized adapters
- frontend may only keep one canonical attribution orchestration layer
- neither strategy nor trade pages may duplicate Brinson or factor calculation logic
- domain-specific differences are limited to:
  - snapshot selectors
  - titles and explanatory copy
  - small view-specific filters
  - empty-state and error-state phrasing

In practical terms:

- algorithm: shared
- response structure: shared
- component skeleton: shared
- domain entry points: separate

## Data Freshness and Staleness Rules

The first batch should explicitly separate stale-handling by domain.

### Strategy domain: hard fail

`/api/v1/strategy/backtests/{backtest_id}/attribution` should hard-fail if required benchmark, factor, or industry snapshots are unavailable or incomplete.

Rationale:

- backtest attribution is an audit-style analysis target
- stale or incomplete supporting data should not be silently tolerated

### Trade domain, current snapshot: stale degradation allowed

`GET /api/v1/trade/portfolio/attribution` without `date` may return a degraded but explicit stale result when current supporting snapshots are late.

The response should include, at minimum:

- `stale`
- `stale_reason`

The frontend should display a prominent warning that the attribution result is based on stale snapshot inputs and is for reference only.

### Trade domain, historical snapshot: hard fail

`GET /api/v1/trade/portfolio/attribution?date=YYYY-MM-DD` should hard-fail if the required historical benchmark, factor, or industry snapshots are missing or incomplete.

Rationale:

- historical attribution is an audit-style query
- returning stale or incomplete historical data would misstate the snapshot

## Testing Strategy

The minimum required validation should cover four layers.

### Backend unit tests

Validate:

- snapshot model normalization
- Brinson decomposition stability
- factor exposure and factor contribution structure
- strategy backtest adapter normalization
- trade current snapshot adapter normalization
- trade historical snapshot adapter normalization
- `date` parameter:
  - absent
  - valid
  - invalid
- data freshness paths:
  - current trade snapshot stale degradation
  - historical trade snapshot hard failure
  - strategy snapshot hard failure

### Backend contract tests

Validate:

- `GET /api/v1/strategy/backtests/{backtest_id}/attribution`
- `GET /api/v1/trade/portfolio/attribution`

Tests should lock:

- unified response shape
- error semantics
- `analysis_date` presence
- stale metadata presence when degradation is allowed

### Frontend unit tests

Validate:

- shared attribution orchestration state flow
- strategy attribution shell rendering
- trade attribution shell rendering
- trade current vs historical date switching
- shared charts/tables consuming one canonical view model

### E2E or smoke

At minimum:

- open strategy/backtest attribution view
- open trade/portfolio attribution view
- switch trade attribution date and confirm refreshed output
- cover at least one empty state
- cover at least one error or stale state

## Governance Closure

### FUNCTION_TREE

`3.3 归因分析` may move from `🚧` to `✅` only when all of the following are true:

- strategy domain can attribute selected backtest-result snapshots
- trade domain can attribute both:
  - current portfolio snapshots
  - specified-date historical portfolio snapshots
- the result includes both:
  - Brinson attribution
  - factor attribution
- the capability is no longer just a local pseudo-contribution card inside `Portfolio.vue`

### OpenSpec

The implementation should begin with a new change proposal. Recommended change id:

- `add-portfolio-attribution-analysis`

The change should affect at least:

- an attribution-analysis or performance-analysis capability
- `frontend-routing` if a new significant attribution surface or route-level requirement needs formalization

## Implementation Order

The recommended implementation sequence is:

1. Create the OpenSpec change.
2. Define shared snapshot models and shared attribution engine contracts.
3. Implement the strategy-domain adapter and route.
4. Implement the trade-domain adapter and route.
5. Add the shared frontend attribution component skeleton.
6. Wire the strategy/backtest shell.
7. Wire the trade/portfolio shell.
8. Run backend, frontend, and smoke verification.
9. Update `FUNCTION_TREE` and archive the OpenSpec change after closure.

This order keeps the truth source stable before wiring UI shells and avoids building two separate page implementations over an unsettled attribution contract.
