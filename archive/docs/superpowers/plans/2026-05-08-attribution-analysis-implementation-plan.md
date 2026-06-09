# Attribution Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a repo-local shared attribution-analysis capability that delivers one-period `Brinson + factor attribution` for selected backtest-result snapshots and for current or date-scoped portfolio snapshots, using one shared backend engine and one shared frontend presentation layer.

**Architecture:** Keep the computation canonical and shared, but keep the entry shells domain-specific. The backend should normalize strategy and trade inputs into unified snapshot models, compute attribution in one engine, expose aligned v1 endpoints under existing route families, and downgrade legacy attribution helpers into compatibility wrappers. The frontend should add one shared attribution API/composable/component stack, then wire thin shells into the existing backtest and portfolio pages without introducing duplicate math or parallel state machines.

**Tech Stack:** OpenSpec, FastAPI, Pydantic, Python service modules, existing `DataService`, existing Baostock/efinance/financial adapters, Vue 3, existing ArtDeco UI primitives, Vitest, Playwright, `UnifiedResponse`.

---

## File Structure

### OpenSpec

- Create: `openspec/changes/add-portfolio-attribution-analysis/proposal.md`
  Purpose: justify the new shared attribution capability and its dual-domain scope.
- Create: `openspec/changes/add-portfolio-attribution-analysis/design.md`
  Purpose: freeze the approved architecture from the spec doc into change-local design notes.
- Create: `openspec/changes/add-portfolio-attribution-analysis/tasks.md`
  Purpose: OpenSpec execution checklist that mirrors the implementation plan.
- Create: `openspec/changes/add-portfolio-attribution-analysis/specs/portfolio-attribution-analysis/spec.md`
  Purpose: first canonical requirement set for shared attribution analysis.

### Backend Shared Attribution Engine

- Create: `web/backend/app/services/attribution/models.py`
  Purpose: shared snapshot, result, stale, and error models used by all attribution surfaces.
- Create: `web/backend/app/services/attribution/errors.py`
  Purpose: explicit attribution exceptions for stale, missing benchmark, missing factor data, and unsupported snapshot shape.
- Create: `web/backend/app/services/attribution/engine.py`
  Purpose: one canonical Brinson and factor-attribution engine.
- Create: `web/backend/app/services/attribution/market_data_dependencies.py`
  Purpose: thin dependency loader that coordinates benchmark constituents, industry classification, OHLCV, and financial-factor enrichment.
- Create: `web/backend/tests/test_attribution_engine.py`
  Purpose: validate canonical attribution math, output structure, and contribution ordering.
- Create: `web/backend/tests/test_attribution_market_data_dependencies.py`
  Purpose: validate benchmark constituent loading, industry lookup, and factor raw-field gap handling.

### Backend Domain Adapters And Routes

- Create: `web/backend/app/services/attribution/adapters/backtest_snapshot.py`
  Purpose: normalize a selected backtest result into `PortfolioSnapshot`, `BenchmarkSnapshot`, and `FactorSnapshot`.
- Create: `web/backend/app/services/attribution/adapters/trade_portfolio_snapshot.py`
  Purpose: normalize current or historical position payloads into the same shared snapshot models.
- Modify: `web/backend/app/api/v1/analysis/backtest.py`
  Purpose: add `GET /api/v1/backtest/{backtest_id}/attribution`.
- Modify: `web/backend/app/api/v1/trading/positions.py`
  Purpose: add `GET /api/v1/positions/attribution` with optional `date=YYYY-MM-DD`.
- Create: `web/backend/tests/test_attribution_backtest_route.py`
  Purpose: validate v1 backtest attribution route contract and hard-fail semantics.
- Create: `web/backend/tests/test_attribution_positions_route.py`
  Purpose: validate v1 positions attribution route contract, `date` handling, stale degradation, and error semantics.

### Legacy Compatibility Alignment

- Modify: `src/interfaces/business_data_source.py`
  Purpose: mark `perform_attribution_analysis(...)` as legacy compatibility surface and reconcile signature expectations in documentation/comments.
- Modify: `src/data_sources/real/composite_business.py`
  Purpose: replace local fake attribution ownership with delegation into the shared engine or an explicit compatibility wrapper.
- Modify: `src/data_sources/mock/business_mock.py`
  Purpose: stop using independent random attribution logic as a canonical path; delegate or demote to explicit demo/mock fallback.
- Create: `tests/unit/data_sources/test_attribution_compatibility_wrappers.py`
  Purpose: verify both legacy surfaces delegate consistently and do not drift from the shared engine contract.

### Frontend Shared Attribution Surface

- Create: `web/frontend/src/api/attribution.ts`
  Purpose: one shared frontend attribution API client for both domains.
- Create: `web/frontend/src/types/attribution.ts`
  Purpose: canonical frontend types for `AttributionAnalysisResponse`, industry rows, factor rows, and stale metadata.
- Create: `web/frontend/src/composables/attribution/useAttributionAnalysis.ts`
  Purpose: one canonical orchestration composable for loading, stale handling, error handling, and request-id capture.
- Create: `web/frontend/src/components/attribution/AttributionOverviewCards.vue`
  Purpose: summary cards for total return, excess return, and analysis date.
- Create: `web/frontend/src/components/attribution/BrinsonBreakdownPanel.vue`
  Purpose: present allocation, selection, and interaction effects.
- Create: `web/frontend/src/components/attribution/IndustryAttributionTable.vue`
  Purpose: table for industry-level breakdown.
- Create: `web/frontend/src/components/attribution/FactorExposureChart.vue`
  Purpose: render portfolio, benchmark, and active factor exposures.
- Create: `web/frontend/src/components/attribution/FactorContributionChart.vue`
  Purpose: render factor contribution bars and residual.
- Create: `web/frontend/src/components/attribution/TopContributorsTable.vue`
  Purpose: render top contributors and detractors sorted by contribution value.
- Create: `web/frontend/src/components/attribution/AttributionEmptyState.vue`
  Purpose: empty-state panel for no available attribution.
- Create: `web/frontend/src/components/attribution/AttributionErrorState.vue`
  Purpose: error-state panel with stale/error messaging.
- Create: `web/frontend/src/components/attribution/__tests__/AttributionComponents.spec.ts`
  Purpose: verify shared rendering rules and stale banners.
- Create: `web/frontend/src/composables/attribution/__tests__/useAttributionAnalysis.spec.ts`
  Purpose: verify canonical API orchestration, stale handling, and request-id propagation.

### Frontend Strategy Shell

- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
  Purpose: add a visible attribution panel inside the existing backtest workbench.
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
  Purpose: add backtest attribution shell state and bridge it to the shared attribution composable.
- Create: `web/frontend/src/views/strategy/__tests__/Backtest.attribution.spec.ts`
  Purpose: verify the strategy shell loads attribution for the selected backtest result and shows hard-fail errors.

### Frontend Trade Shell

- Modify: `web/frontend/src/views/trade/Portfolio.vue`
  Purpose: replace local pseudo-attribution cards with the shared attribution presentation surface and add current/date-switching controls.
- Modify: `web/frontend/src/views/trade/__tests__/Portfolio.spec.ts`
  Purpose: update canonical portfolio assertions to the new attribution surface.
- Create: `web/frontend/src/views/trade/__tests__/Portfolio.attribution.spec.ts`
  Purpose: verify current-vs-historical attribution switching and stale-current behavior.

### Verification And Governance Closeout

- Create: `web/frontend/tests/e2e/attribution-analysis.spec.ts`
  Purpose: smoke both the strategy and trade attribution shells.
- Modify: `docs/FUNCTION_TREE.md`
  Purpose: promote `归因分析` only after both shells and both attribution types are verified.

---

### Task 1: OpenSpec Change For Shared Attribution Analysis

**Files:**
- Create: `openspec/changes/add-portfolio-attribution-analysis/proposal.md`
- Create: `openspec/changes/add-portfolio-attribution-analysis/design.md`
- Create: `openspec/changes/add-portfolio-attribution-analysis/tasks.md`
- Create: `openspec/changes/add-portfolio-attribution-analysis/specs/portfolio-attribution-analysis/spec.md`

- [ ] **Step 1: Write the OpenSpec proposal from the approved design**

```md
# Change: add portfolio attribution analysis

## Why
`FUNCTION_TREE` still marks the `归因分析` row under `3.3 回测分析` as unfinished. The repository has pseudo-attribution UI and legacy helper methods, but no canonical shared attribution engine or dual-domain closure.

## What Changes
- Add a shared attribution-analysis capability with one-period Brinson and five-factor attribution.
- Add aligned v1 endpoints for selected backtest snapshots and current/date-scoped portfolio snapshots.
- Add one shared frontend attribution presentation layer reused by both the strategy and trade shells.

## Impact
- Affected specs: `portfolio-attribution-analysis`
- Affected code: `web/backend/app/services/attribution/*`, `web/backend/app/api/v1/analysis/backtest.py`, `web/backend/app/api/v1/trading/positions.py`, `web/frontend/src/views/artdeco-pages/strategy-tabs/*`, `web/frontend/src/views/trade/Portfolio.vue`
```

- [ ] **Step 2: Write the capability spec delta**

```md
## ADDED Requirements
### Requirement: Shared Attribution Analysis Engine
The system SHALL provide a shared attribution-analysis engine for one-period Brinson and five-factor attribution.

#### Scenario: Dual domains use one canonical engine
- **WHEN** attribution is requested for a selected backtest result or for a current/date-scoped portfolio snapshot
- **THEN** the system SHALL normalize the input into shared snapshot models
- **AND** SHALL compute attribution through one shared calculation engine

### Requirement: Dual-Domain Attribution Entry Points
The system SHALL expose attribution through existing v1 analysis and trading route families.

#### Scenario: Backtest attribution is requested
- **WHEN** the user calls `GET /api/v1/backtest/{backtest_id}/attribution`
- **THEN** the system SHALL return an `AttributionAnalysisResponse` for the selected backtest-result snapshot

#### Scenario: Portfolio attribution is requested
- **WHEN** the user calls `GET /api/v1/positions/attribution`
- **THEN** the system SHALL return current portfolio attribution by default
- **AND** SHALL return historical attribution when `date=YYYY-MM-DD` is provided
```

- [ ] **Step 3: Write the OpenSpec tasks checklist**

```md
## 1. Backend
- [ ] 1.1 Add shared attribution models, errors, and engine
- [ ] 1.2 Add benchmark, industry, price, and factor enrichment dependencies
- [ ] 1.3 Add backtest and trade snapshot adapters
- [ ] 1.4 Add v1 backtest attribution route
- [ ] 1.5 Add v1 positions attribution route
- [ ] 1.6 Align legacy compatibility wrappers

## 2. Frontend
- [ ] 2.1 Add shared attribution API client and types
- [ ] 2.2 Add canonical attribution composable
- [ ] 2.3 Add shared attribution components
- [ ] 2.4 Wire strategy backtest shell
- [ ] 2.5 Wire trade portfolio shell

## 3. Verification
- [ ] 3.1 Run targeted backend tests
- [ ] 3.2 Run targeted frontend unit tests
- [ ] 3.3 Run attribution E2E smoke
- [ ] 3.4 Update `FUNCTION_TREE`
```

- [ ] **Step 4: Validate the OpenSpec change**

Run:

```bash
openspec validate add-portfolio-attribution-analysis --strict
```

Expected:

```text
Change 'add-portfolio-attribution-analysis' is valid
```

- [ ] **Step 5: Commit the OpenSpec slice**

```bash
git add \
  openspec/changes/add-portfolio-attribution-analysis/proposal.md \
  openspec/changes/add-portfolio-attribution-analysis/design.md \
  openspec/changes/add-portfolio-attribution-analysis/tasks.md \
  openspec/changes/add-portfolio-attribution-analysis/specs/portfolio-attribution-analysis/spec.md
git commit -m "docs(openspec): add portfolio attribution analysis change"
```

---

### Task 2: Shared Attribution Models, Errors, And Engine

**Files:**
- Create: `web/backend/app/services/attribution/models.py`
- Create: `web/backend/app/services/attribution/errors.py`
- Create: `web/backend/app/services/attribution/engine.py`
- Create: `web/backend/tests/test_attribution_engine.py`

- [ ] **Step 1: Write the failing engine tests**

```python
from web.backend.app.services.attribution.engine import AttributionEngine
from web.backend.app.services.attribution.models import (
    BenchmarkConstituentSnapshot,
    FactorExposureSnapshot,
    PortfolioConstituentSnapshot,
)


def test_engine_returns_brinson_and_factor_sections():
    engine = AttributionEngine()
    portfolio = [
        PortfolioConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600000.SH",
            weight=0.6,
            market_value=600000.0,
            return_rate=0.10,
            industry="银行",
        ),
        PortfolioConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600519.SH",
            weight=0.4,
            market_value=400000.0,
            return_rate=-0.02,
            industry="食品饮料",
        ),
    ]
    benchmark = [
        BenchmarkConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600000.SH",
            weight=0.5,
            return_rate=0.08,
            industry="银行",
        ),
        BenchmarkConstituentSnapshot(
            analysis_date="2026-05-08",
            symbol="600519.SH",
            weight=0.5,
            return_rate=0.01,
            industry="食品饮料",
        ),
    ]
    factors = FactorExposureSnapshot(
        analysis_date="2026-05-08",
        portfolio={"size": 0.2, "value": 0.1, "momentum": 0.4, "volatility": -0.1, "quality": 0.3},
        benchmark={"size": 0.1, "value": 0.0, "momentum": 0.2, "volatility": 0.0, "quality": 0.1},
    )

    result = engine.analyze(portfolio=portfolio, benchmark=benchmark, factors=factors)

    assert result.analysis_date == "2026-05-08"
    assert result.brinson.allocation_effect is not None
    assert result.factor_attribution.factor_contributions["momentum"] is not None
    assert result.top_contributors[0].contribution >= result.top_contributors[1].contribution
```

- [ ] **Step 2: Run the test and confirm the engine module does not exist yet**

Run:

```bash
pytest web/backend/tests/test_attribution_engine.py -q --no-cov
```

Expected:

```text
FAIL ... ModuleNotFoundError: No module named '...services.attribution.engine'
```

- [ ] **Step 3: Add shared models and error types**

```python
from pydantic import BaseModel, Field


class PortfolioConstituentSnapshot(BaseModel):
    analysis_date: str
    symbol: str
    weight: float = Field(..., ge=0, le=1)
    market_value: float = Field(..., ge=0)
    return_rate: float
    industry: str


class BenchmarkConstituentSnapshot(BaseModel):
    analysis_date: str
    symbol: str
    weight: float = Field(..., ge=0, le=1)
    return_rate: float
    industry: str


class FactorExposureSnapshot(BaseModel):
    analysis_date: str
    portfolio: dict[str, float]
    benchmark: dict[str, float]


class AttributionStaleError(RuntimeError):
    pass


class AttributionDependencyError(RuntimeError):
    pass
```

- [ ] **Step 4: Add the canonical engine with contribution sorting and one-period math**

```python
class AttributionEngine:
    def analyze(self, *, portfolio, benchmark, factors):
        industry_rows = self._build_industry_breakdown(portfolio, benchmark)
        contribution_rows = self._build_contribution_rows(portfolio)
        factor_payload = self._build_factor_payload(factors)
        return AttributionAnalysisResult(
            analysis_date=portfolio[0].analysis_date,
            snapshot_meta={...},
            benchmark_meta={...},
            brinson=BrinsonBreakdown(
                allocation_effect=sum(item.allocation_effect for item in industry_rows),
                selection_effect=sum(item.selection_effect for item in industry_rows),
                interaction_effect=sum(item.interaction_effect for item in industry_rows),
                industry_breakdown=industry_rows,
            ),
            factor_attribution=factor_payload,
            top_contributors=sorted(
                [row for row in contribution_rows if row.contribution >= 0],
                key=lambda row: row.contribution,
                reverse=True,
            )[:5],
            top_detractors=sorted(
                [row for row in contribution_rows if row.contribution < 0],
                key=lambda row: row.contribution,
            )[:5],
        )
```

- [ ] **Step 5: Re-run the engine tests**

Run:

```bash
pytest web/backend/tests/test_attribution_engine.py -q --no-cov
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit the engine slice**

```bash
git add \
  web/backend/app/services/attribution/models.py \
  web/backend/app/services/attribution/errors.py \
  web/backend/app/services/attribution/engine.py \
  web/backend/tests/test_attribution_engine.py
git commit -m "feat(attribution): add shared attribution engine"
```

---

### Task 3: Market Data Dependencies And Strategy-Side Snapshot Adapter

**Files:**
- Create: `web/backend/app/services/attribution/market_data_dependencies.py`
- Create: `web/backend/app/services/attribution/adapters/backtest_snapshot.py`
- Modify: `web/backend/app/api/v1/analysis/backtest.py`
- Create: `web/backend/tests/test_attribution_market_data_dependencies.py`
- Create: `web/backend/tests/test_attribution_backtest_route.py`

- [ ] **Step 1: Write failing tests for dependency loading and strategy adapter shape**

```python
from web.backend.app.services.attribution.adapters.backtest_snapshot import (
    build_backtest_attribution_snapshot,
)


def test_build_backtest_snapshot_requires_position_level_enrichment():
    backtest_result = {
        "backtest_id": 42,
        "symbols": ["600000.SH", "600519.SH"],
        "equity_curve": [],
        "trades": [
            {"symbol": "600000.SH", "side": "buy", "price": 10.0, "quantity": 100},
            {"symbol": "600519.SH", "side": "buy", "price": 1800.0, "quantity": 10},
        ],
    }

    snapshot = build_backtest_attribution_snapshot._from_trade_projection_for_test(
        backtest_result=backtest_result,
        analysis_date="2026-05-08",
    )

    assert {row.symbol for row in snapshot.portfolio} == {"600000.SH", "600519.SH"}
    assert snapshot.analysis_date == "2026-05-08"
```

- [ ] **Step 2: Run the new tests and confirm the adapter is missing**

Run:

```bash
pytest \
  web/backend/tests/test_attribution_market_data_dependencies.py \
  web/backend/tests/test_attribution_backtest_route.py \
  -q --no-cov
```

Expected:

```text
FAIL ... ModuleNotFoundError or attribute error for the missing adapter/dependency loader
```

- [ ] **Step 3: Add benchmark, industry, OHLCV, and factor dependency loader**

```python
class AttributionMarketDataDependencies:
    def load_benchmark_constituents(self, analysis_date: str) -> pd.DataFrame:
        return self.baostock_importer.query_hs300_stocks(analysis_date)

    def load_industry_classification(self, symbols: list[str], analysis_date: str) -> dict[str, str]:
        mapping: dict[str, str] = {}
        for symbol in symbols:
            frame = self.baostock_importer.query_stock_industry(symbol, analysis_date)
            if frame.empty:
                raise AttributionDependencyError(f"missing industry classification for {symbol} at {analysis_date}")
            mapping[symbol] = str(frame.iloc[0]["industry"])
        return mapping

    def load_daily_returns(self, symbol: str, start_date: datetime, end_date: datetime) -> float:
        frame, _ = self.data_service.get_daily_ohlcv(symbol, start_date, end_date)
        return float((frame.iloc[-1]["close"] - frame.iloc[0]["close"]) / frame.iloc[0]["close"])
```

- [ ] **Step 4: Add the backtest snapshot adapter and v1 route**

```python
@router.get(
    "/{backtest_id}/attribution",
    response_model=UnifiedResponse[dict[str, Any]],
    summary="Get Backtest Attribution",
)
async def get_backtest_attribution(backtest_id: int = Path(..., ge=1)):
    snapshot = build_backtest_attribution_snapshot(
        backtest_id=backtest_id,
        dependencies=get_attribution_market_data_dependencies(),
    )
    result = AttributionEngine().analyze(
        portfolio=snapshot.portfolio,
        benchmark=snapshot.benchmark,
        factors=snapshot.factors,
    )
    return UnifiedResponse(success=True, code=200, message="Backtest attribution retrieved", data=result.model_dump())
```

- [ ] **Step 5: Re-run dependency and backtest route tests**

Run:

```bash
pytest \
  web/backend/tests/test_attribution_market_data_dependencies.py \
  web/backend/tests/test_attribution_backtest_route.py \
  -q --no-cov
```

Expected:

```text
... passed
```

- [ ] **Step 6: Commit the strategy backend slice**

```bash
git add \
  web/backend/app/services/attribution/market_data_dependencies.py \
  web/backend/app/services/attribution/adapters/backtest_snapshot.py \
  web/backend/app/api/v1/analysis/backtest.py \
  web/backend/tests/test_attribution_market_data_dependencies.py \
  web/backend/tests/test_attribution_backtest_route.py
git commit -m "feat(attribution): add backtest attribution route"
```

---

### Task 4: Trade Portfolio Snapshot Adapter And Positions Attribution Route

**Files:**
- Create: `web/backend/app/services/attribution/adapters/trade_portfolio_snapshot.py`
- Modify: `web/backend/app/api/v1/trading/positions.py`
- Create: `web/backend/tests/test_attribution_positions_route.py`

- [ ] **Step 1: Write the failing positions route tests**

```python
def test_positions_attribution_defaults_to_current_snapshot(client, monkeypatch):
    response = client.get("/api/v1/positions/attribution")

    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["analysis_date"]
    assert "brinson" in payload["data"]


def test_positions_attribution_accepts_date_query(client):
    response = client.get("/api/v1/positions/attribution?date=2026-05-07")

    assert response.status_code == 200
    assert response.json()["data"]["analysis_date"] == "2026-05-07"


def test_positions_attribution_rejects_invalid_date(client):
    response = client.get("/api/v1/positions/attribution?date=bad-date")

    assert response.status_code == 400
```

- [ ] **Step 2: Run the route test and confirm the endpoint does not exist**

Run:

```bash
pytest web/backend/tests/test_attribution_positions_route.py -q --no-cov
```

Expected:

```text
FAIL ... 404 != 200
```

- [ ] **Step 3: Add current and historical trade snapshot adapter**

```python
def build_trade_portfolio_attribution_snapshot(*, positions: list[dict[str, Any]], analysis_date: str, dependencies):
    if not positions:
        raise AttributionDependencyError("portfolio snapshot contains no positions")

    normalized_rows = [
        PortfolioConstituentSnapshot(
            analysis_date=analysis_date,
            symbol=item["symbol"],
            weight=float(item["weight"]),
            market_value=float(item["market_value"]),
            return_rate=dependencies.load_daily_return_window(
                symbol=item["symbol"],
                analysis_date=analysis_date,
            ),
            industry=dependencies.load_industry_value(item["symbol"], analysis_date),
        )
        for item in positions
    ]
    return TradePortfolioAttributionSnapshot(
        analysis_date=analysis_date,
        portfolio=normalized_rows,
        benchmark=dependencies.build_benchmark_snapshot(analysis_date),
        factors=dependencies.build_factor_snapshot(normalized_rows, analysis_date),
    )
```

- [ ] **Step 4: Add positions attribution route with stale/current and hard-fail/historical behavior**

```python
@router.get(
    "/attribution",
    response_model=UnifiedResponse[dict[str, Any]],
    summary="Get Portfolio Attribution",
)
async def get_positions_attribution(date: Optional[str] = Query(None, description="Optional historical snapshot date")):
    if date is not None:
        analysis_date = _parse_iso_date(date)
        snapshot = build_historical_trade_attribution_snapshot(analysis_date=analysis_date, ...)
        result = AttributionEngine().analyze(...)
        return UnifiedResponse(success=True, code=200, message="Historical portfolio attribution retrieved", data=result.model_dump())

    try:
        snapshot = build_current_trade_attribution_snapshot(...)
        result = AttributionEngine().analyze(...)
        return UnifiedResponse(success=True, code=200, message="Current portfolio attribution retrieved", data=result.model_dump())
    except AttributionStaleError as exc:
        stale_result = exc.result
        return UnifiedResponse(success=True, code=200, message="Current portfolio attribution is stale", data=stale_result.model_dump())
```

- [ ] **Step 5: Re-run the positions attribution tests**

Run:

```bash
pytest web/backend/tests/test_attribution_positions_route.py -q --no-cov
```

Expected:

```text
3 passed
```

- [ ] **Step 6: Commit the trade backend slice**

```bash
git add \
  web/backend/app/services/attribution/adapters/trade_portfolio_snapshot.py \
  web/backend/app/api/v1/trading/positions.py \
  web/backend/tests/test_attribution_positions_route.py
git commit -m "feat(attribution): add portfolio attribution route"
```

---

### Task 5: Legacy Compatibility Wrappers

**Files:**
- Modify: `src/interfaces/business_data_source.py`
- Modify: `src/data_sources/real/composite_business.py`
- Modify: `src/data_sources/mock/business_mock.py`
- Create: `tests/unit/data_sources/test_attribution_compatibility_wrappers.py`

- [ ] **Step 1: Write the failing compatibility tests**

```python
def test_real_business_data_source_delegates_to_shared_engine(monkeypatch):
    delegated = {}

    def fake_delegate(*args, **kwargs):
        delegated["called"] = True
        return {"analysis_date": "2026-05-08", "brinson": {}, "factor_attribution": {}}

    monkeypatch.setattr(
        "src.data_sources.real.composite_business._run_legacy_attribution_delegate_for_test",
        fake_delegate,
    )

    result = CompositeBusinessDataSource(...).perform_attribution_analysis(
        user_id=1,
        start_date=date(2026, 5, 1),
        end_date=date(2026, 5, 8),
    )

    assert delegated["called"] is True
    assert result["analysis_date"] == "2026-05-08"
```

- [ ] **Step 2: Run the tests and confirm current implementations still own random/local logic**

Run:

```bash
pytest tests/unit/data_sources/test_attribution_compatibility_wrappers.py -q --no-cov
```

Expected:

```text
FAIL ... because perform_attribution_analysis still returns local fake data
```

- [ ] **Step 3: Reconcile the legacy contract comments and signatures**

```python
@abstractmethod
def perform_attribution_analysis(self, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Legacy compatibility surface.

    Implementations SHALL normalize their inputs and delegate into the shared
    attribution engine rather than owning independent attribution logic.
    """
```

- [ ] **Step 4: Replace local fake ownership with delegated wrappers**

```python
def perform_attribution_analysis(self, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
    return run_legacy_attribution_delegate(
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        source=self,
    )
```

- [ ] **Step 5: Re-run the compatibility tests**

Run:

```bash
pytest tests/unit/data_sources/test_attribution_compatibility_wrappers.py -q --no-cov
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit the legacy-alignment slice**

```bash
git add \
  src/interfaces/business_data_source.py \
  src/data_sources/real/composite_business.py \
  src/data_sources/mock/business_mock.py \
  tests/unit/data_sources/test_attribution_compatibility_wrappers.py
git commit -m "refactor(attribution): align legacy compatibility wrappers"
```

---

### Task 6: Shared Frontend Attribution API, Types, Composable, And Components

**Files:**
- Create: `web/frontend/src/api/attribution.ts`
- Create: `web/frontend/src/types/attribution.ts`
- Create: `web/frontend/src/composables/attribution/useAttributionAnalysis.ts`
- Create: `web/frontend/src/components/attribution/AttributionOverviewCards.vue`
- Create: `web/frontend/src/components/attribution/BrinsonBreakdownPanel.vue`
- Create: `web/frontend/src/components/attribution/IndustryAttributionTable.vue`
- Create: `web/frontend/src/components/attribution/FactorExposureChart.vue`
- Create: `web/frontend/src/components/attribution/FactorContributionChart.vue`
- Create: `web/frontend/src/components/attribution/TopContributorsTable.vue`
- Create: `web/frontend/src/components/attribution/AttributionEmptyState.vue`
- Create: `web/frontend/src/components/attribution/AttributionErrorState.vue`
- Create: `web/frontend/src/components/attribution/__tests__/AttributionComponents.spec.ts`
- Create: `web/frontend/src/composables/attribution/__tests__/useAttributionAnalysis.spec.ts`

- [ ] **Step 1: Write the failing composable tests**

```ts
import { describe, expect, it, vi } from 'vitest'
import { useAttributionAnalysis } from '@/composables/attribution/useAttributionAnalysis'

describe('useAttributionAnalysis', () => {
  it('keeps analysis_date and request id from a successful response', async () => {
    const loader = vi.fn().mockResolvedValue({
      success: true,
      data: {
        analysis_date: '2026-05-08',
        stale: false,
        brinson: { allocation_effect: 0.01, selection_effect: 0.02, interaction_effect: -0.01, industry_breakdown: [] },
        factor_attribution: { factor_exposures: {}, factor_contributions: {} },
        top_contributors: [],
        top_detractors: [],
      },
      request_id: 'req-attr-001',
    })

    const model = useAttributionAnalysis(loader)
    await model.load()

    expect(model.analysis.value?.analysis_date).toBe('2026-05-08')
    expect(model.requestId.value).toBe('req-attr-001')
  })
})
```

- [ ] **Step 2: Run the tests and confirm the shared stack does not exist yet**

Run:

```bash
cd web/frontend && npx vitest run \
  src/composables/attribution/__tests__/useAttributionAnalysis.spec.ts \
  src/components/attribution/__tests__/AttributionComponents.spec.ts
```

Expected:

```text
FAIL ... Failed to resolve import '@/composables/attribution/useAttributionAnalysis'
```

- [ ] **Step 3: Add canonical types and API client**

```ts
export interface AttributionContributionRow {
  symbol: string
  name?: string
  contribution: number
  weight: number
  return_rate: number
}

export interface AttributionAnalysisResponse {
  analysis_date: string
  stale?: boolean
  stale_reason?: string | null
  brinson: {
    allocation_effect: number
    selection_effect: number
    interaction_effect: number
    industry_breakdown: Array<Record<string, unknown>>
  }
  factor_attribution: {
    factor_exposures: Record<string, unknown>
    factor_contributions: Record<string, number>
  }
  top_contributors: AttributionContributionRow[]
  top_detractors: AttributionContributionRow[]
}

export const attributionApi = {
  getBacktestAttribution: (backtestId: number) => apiClient.get(`/v1/backtest/${backtestId}/attribution`),
  getPortfolioAttribution: (date?: string) => apiClient.get('/v1/positions/attribution', {
    params: date ? { date } : undefined,
  }),
}
```

- [ ] **Step 4: Add the canonical composable and shared components**

```ts
export function useAttributionAnalysis(
  loader: () => Promise<{ success: boolean; data: AttributionAnalysisResponse; request_id?: string }>
) {
  const loading = ref(false)
  const error = ref('')
  const requestId = ref('')
  const analysis = ref<AttributionAnalysisResponse | null>(null)

  async function load() {
    loading.value = true
    error.value = ''
    try {
      const response = await loader()
      analysis.value = response.data
      requestId.value = response.request_id ?? requestId.value
    } catch (err) {
      error.value = err instanceof Error ? err.message : '归因分析加载失败'
    } finally {
      loading.value = false
    }
  }

  return { loading, error, requestId, analysis, load }
}
```

- [ ] **Step 5: Re-run the shared frontend tests**

Run:

```bash
cd web/frontend && npx vitest run \
  src/composables/attribution/__tests__/useAttributionAnalysis.spec.ts \
  src/components/attribution/__tests__/AttributionComponents.spec.ts
```

Expected:

```text
... passed
```

- [ ] **Step 6: Commit the shared frontend slice**

```bash
git add \
  web/frontend/src/api/attribution.ts \
  web/frontend/src/types/attribution.ts \
  web/frontend/src/composables/attribution/useAttributionAnalysis.ts \
  web/frontend/src/components/attribution \
  web/frontend/src/composables/attribution/__tests__/useAttributionAnalysis.spec.ts
git commit -m "feat(attribution): add shared frontend attribution surface"
```

---

### Task 7: Strategy Backtest Shell Integration

**Files:**
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue`
- Modify: `web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts`
- Create: `web/frontend/src/views/strategy/__tests__/Backtest.attribution.spec.ts`

- [ ] **Step 1: Write the failing strategy shell test**

```ts
import { render, screen } from '@testing-library/vue'
import BacktestPage from '@/views/strategy/Backtest.vue'

it('shows attribution panel for the selected backtest result', async () => {
  render(BacktestPage)

  expect(await screen.findByText('归因分析')).toBeInTheDocument()
  expect(await screen.findByText('Brinson 分解')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the test and confirm the panel is not present**

Run:

```bash
cd web/frontend && npx vitest run src/views/strategy/__tests__/Backtest.attribution.spec.ts
```

Expected:

```text
FAIL ... Unable to find text '归因分析'
```

- [ ] **Step 3: Add attribution shell state to the backtest view model**

```ts
const selectedBacktestId = computed(() => {
  const raw = readNumber(selectedStrategySnapshot.value?.backtest ?? null, ['id', 'backtest_id'])
  return raw ?? null
})

const attributionModel = useAttributionAnalysis(async () => {
  if (!selectedBacktestId.value) {
    throw new Error('当前策略缺少可用的回测结果快照')
  }
  return await attributionApi.getBacktestAttribution(selectedBacktestId.value)
})
```

- [ ] **Step 4: Render the shared attribution surface in the backtest workbench**

```vue
<section v-else-if="activeTab === 'report'" class="tab-panel">
  <ArtDecoCard title="归因分析" hoverable>
    <AttributionErrorState v-if="attributionError" :message="attributionError" />
    <AttributionEmptyState v-else-if="!attributionAnalysis" title="暂无归因结果" />
    <template v-else>
      <AttributionOverviewCards :analysis="attributionAnalysis" :request-id="attributionRequestId" />
      <BrinsonBreakdownPanel :brinson="attributionAnalysis.brinson" />
      <FactorExposureChart :payload="attributionAnalysis.factor_attribution.factor_exposures" />
      <FactorContributionChart :payload="attributionAnalysis.factor_attribution.factor_contributions" />
      <TopContributorsTable
        :contributors="attributionAnalysis.top_contributors"
        :detractors="attributionAnalysis.top_detractors"
      />
    </template>
  </ArtDecoCard>
</section>
```

- [ ] **Step 5: Re-run the strategy shell test**

Run:

```bash
cd web/frontend && npx vitest run src/views/strategy/__tests__/Backtest.attribution.spec.ts
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit the strategy frontend slice**

```bash
git add \
  web/frontend/src/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue \
  web/frontend/src/views/artdeco-pages/strategy-tabs/backtestAnalysisViewModel.ts \
  web/frontend/src/views/strategy/__tests__/Backtest.attribution.spec.ts
git commit -m "feat(attribution): wire strategy backtest shell"
```

---

### Task 8: Trade Portfolio Shell Integration

**Files:**
- Modify: `web/frontend/src/views/trade/Portfolio.vue`
- Modify: `web/frontend/src/views/trade/__tests__/Portfolio.spec.ts`
- Create: `web/frontend/src/views/trade/__tests__/Portfolio.attribution.spec.ts`
- Create: `tests/e2e/attribution-analysis.spec.ts`
- Modify: `docs/FUNCTION_TREE.md`

- [ ] **Step 1: Write the failing portfolio attribution tests**

```ts
import { render, screen, fireEvent } from '@testing-library/vue'
import PortfolioPage from '@/views/trade/Portfolio.vue'

it('replaces local pseudo-attribution with the shared attribution surface', async () => {
  render(PortfolioPage)

  expect(await screen.findByText('Brinson 分解')).toBeInTheDocument()
})

it('switches between current and historical attribution', async () => {
  render(PortfolioPage)

  const dateInput = await screen.findByLabelText('归因日期')
  await fireEvent.update(dateInput, '2026-05-07')

  expect(await screen.findByText('分析日期 2026-05-07')).toBeInTheDocument()
})
```

- [ ] **Step 2: Run the portfolio tests and confirm the page still shows local pseudo-attribution**

Run:

```bash
cd web/frontend && npx vitest run \
  src/views/trade/__tests__/Portfolio.spec.ts \
  src/views/trade/__tests__/Portfolio.attribution.spec.ts
```

Expected:

```text
FAIL ... because the page still renders local `performanceAttribution`
```

- [ ] **Step 3: Replace local pseudo-attribution logic with the shared attribution shell**

```ts
const attributionDate = ref('')
const attributionModel = useAttributionAnalysis(async () => {
  const date = attributionDate.value.trim()
  return await attributionApi.getPortfolioAttribution(date || undefined)
})

const attributionStatusText = computed(() => {
  if (attributionModel.analysis.value?.stale) {
    return `基于过期快照：${attributionModel.analysis.value.stale_reason ?? '请谨慎参考'}`
  }
  return ''
})
```

- [ ] **Step 4: Render current/date controls and shared components**

```vue
<div class="attribution-section">
  <h3 class="subsection-title">归因分析</h3>
  <div class="attribution-controls artdeco-card">
    <label class="field">
      <span>归因日期</span>
      <input v-model="attributionDate" aria-label="归因日期" type="date" />
    </label>
    <ArtDecoButton variant="outline" size="sm" @click="refreshAttribution">刷新归因</ArtDecoButton>
  </div>

  <AttributionErrorState v-if="attributionModel.error.value" :message="attributionModel.error.value" />
  <AttributionEmptyState v-else-if="!attributionModel.analysis.value" title="暂无归因结果" />
  <template v-else>
    <AttributionOverviewCards :analysis="attributionModel.analysis.value" :request-id="attributionModel.requestId.value" />
    <BrinsonBreakdownPanel :brinson="attributionModel.analysis.value.brinson" />
    <IndustryAttributionTable :rows="attributionModel.analysis.value.brinson.industry_breakdown" />
    <FactorExposureChart :payload="attributionModel.analysis.value.factor_attribution.factor_exposures" />
    <FactorContributionChart :payload="attributionModel.analysis.value.factor_attribution.factor_contributions" />
    <TopContributorsTable
      :contributors="attributionModel.analysis.value.top_contributors"
      :detractors="attributionModel.analysis.value.top_detractors"
    />
  </template>
</div>
```

- [ ] **Step 5: Add smoke coverage for both shells and update `FUNCTION_TREE`**

```ts
test('strategy and trade attribution surfaces render', async ({ page }) => {
  await page.route('**/api/v1/backtest/*/attribution', async (route) => {
    await route.fulfill({ json: { success: true, code: 200, message: 'ok', data: mockedBacktestAttribution } })
  })
  await page.route('**/api/v1/positions/attribution**', async (route) => {
    await route.fulfill({ json: { success: true, code: 200, message: 'ok', data: mockedPortfolioAttribution } })
  })

  await page.goto('/strategy/backtest')
  await expect(page.getByText('归因分析')).toBeVisible()

  await page.goto('/trade/portfolio')
  await expect(page.getByText('Brinson 分解')).toBeVisible()
})
```

`docs/FUNCTION_TREE.md` change:

```md
| 归因分析 | ✅ | Brinson归因、因子归因 |
```

- [ ] **Step 6: Re-run portfolio/unit/E2E verification**

Run:

```bash
cd web/frontend && npx vitest run \
  src/views/trade/__tests__/Portfolio.spec.ts \
  src/views/trade/__tests__/Portfolio.attribution.spec.ts \
  src/views/strategy/__tests__/Backtest.attribution.spec.ts

npx playwright test tests/e2e/attribution-analysis.spec.ts --project=chromium
```

Expected:

```text
... passed
... chromium 1 passed
```

- [ ] **Step 7: Commit the trade shell and governance slice**

```bash
git add \
  web/frontend/src/views/trade/Portfolio.vue \
  web/frontend/src/views/trade/__tests__/Portfolio.spec.ts \
  web/frontend/src/views/trade/__tests__/Portfolio.attribution.spec.ts \
  web/frontend/tests/e2e/attribution-analysis.spec.ts \
  docs/FUNCTION_TREE.md
git commit -m "feat(attribution): close dual-domain attribution analysis"
```

---

### Task 9: Final Verification And OpenSpec Archive

**Files:**
- Modify: `openspec/changes/add-portfolio-attribution-analysis/tasks.md`
- Archive: `openspec/changes/add-portfolio-attribution-analysis/`
- Promote: `openspec/specs/portfolio-attribution-analysis/spec.md`

- [ ] **Step 1: Run targeted backend verification**

Run:

```bash
pytest \
  web/backend/tests/test_attribution_engine.py \
  web/backend/tests/test_attribution_market_data_dependencies.py \
  web/backend/tests/test_attribution_backtest_route.py \
  web/backend/tests/test_attribution_positions_route.py \
  tests/unit/data_sources/test_attribution_compatibility_wrappers.py \
  -q --no-cov
```

Expected:

```text
..... passed
```

- [ ] **Step 2: Run targeted frontend and governance verification**

Run:

```bash
cd web/frontend && npx vitest run \
  src/composables/attribution/__tests__/useAttributionAnalysis.spec.ts \
  src/components/attribution/__tests__/AttributionComponents.spec.ts \
  src/views/strategy/__tests__/Backtest.attribution.spec.ts \
  src/views/trade/__tests__/Portfolio.spec.ts \
  src/views/trade/__tests__/Portfolio.attribution.spec.ts

cd /opt/claude/mystocks_spec && pytest \
  tests/unit/governance/test_function_tree_doc_sync.py \
  tests/unit/governance/test_function_tree_catalog.py \
  -q --no-cov
```

Expected:

```text
... passed
18 passed
```

- [ ] **Step 3: Run E2E smoke and strict OpenSpec validation**

Run:

```bash
cd /opt/claude/mystocks_spec/web/frontend && npx playwright test tests/e2e/attribution-analysis.spec.ts --project=chromium

cd /opt/claude/mystocks_spec && openspec validate add-portfolio-attribution-analysis --strict
```

Expected:

```text
chromium 1 passed
Change 'add-portfolio-attribution-analysis' is valid
```

- [ ] **Step 4: Refresh the OpenSpec task checklist and archive the change**

```bash
openspec archive add-portfolio-attribution-analysis --yes
openspec validate --specs --strict
```

Expected:

```text
Archived change 'add-portfolio-attribution-analysis'
... passed
```

- [ ] **Step 5: Commit the archive closeout**

```bash
git add openspec/changes openspec/specs
git commit -m "docs(openspec): archive portfolio attribution analysis change"
```

---

## Plan Self-Review

### Spec coverage

- Shared engine, unified snapshots, and shared response model are covered by Tasks 1-2.
- Strategy-side selected backtest-result attribution is covered by Tasks 3 and 7.
- Trade-side current and historical attribution is covered by Tasks 4 and 8.
- `analysis_date`, contribution-based top sorting, and stale semantics are covered by Tasks 2, 4, and 8.
- Legacy interface alignment is covered by Task 5.
- OpenSpec and `FUNCTION_TREE` closure are covered by Tasks 1 and 9.

### Placeholder scan

- The plan contains no unfinished placeholder markers or "same as above" shortcuts in executable steps.
- Every file path is explicit.
- Every testing step includes the exact command and expected outcome.

### Type consistency

- Canonical frontend response type is `AttributionAnalysisResponse` across Tasks 6-8.
- Backend shared model uses `return_rate`, not `contribution`, as the snapshot input field.
- Strategy route path stays `/api/v1/backtest/{backtest_id}/attribution`.
- Trade route path stays `/api/v1/positions/attribution`.
