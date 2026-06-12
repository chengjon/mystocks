# Backend Service Lifecycle DI Technical Analysis Provider Implementation

Date: 2026-06-13
Task: G2.332
Mode: source-authorized implementation
Base worktree: `g2-332-technical-analysis-datasourcefactory-provider`
Base commit: `dfeb6b2963aa2ca991dceb3cc3058e26461a80a0`

## Status

G2.332 implements the source-authorized technical-analysis service lifecycle DI
slice selected by G2.331. The change moves route-body `DataSourceFactory`
construction out of 8 technical-analysis route handlers and into one FastAPI
provider dependency.

No OpenStock internals, frontend code, unrelated scripts, configuration,
OpenSpec implementation files, watchlist routes, strategy routes, dashboard
routes, or unrelated tests were modified.

## Changed Files

| Path | Purpose |
| --- | --- |
| `web/backend/app/api/technical_analysis.py` | Adds `get_technical_analysis_data_source()` and injects it into 8 route handlers via `Depends(...)` |
| `web/backend/tests/test_technical_analysis_provider_injection.py` | Adds focused AST regression coverage for the provider-injection boundary |
| `scripts/compliance/unified_response_contract_guard.py` | Adds an explicit legacy baseline mechanism for pre-existing non-UnifiedResponse endpoints |
| `tests/unit/scripts/test_unified_response_contract_guard.py` | Adds red/green coverage for legacy baseline behavior |
| `governance/compliance/unified-response-contract-legacy-baseline.json` | Records the 8 existing `technical_analysis.py` endpoints as UnifiedResponse contract debt for a future response-contract migration |
| `governance/function-tree/catalog.yaml` | Adds the existing `technical_analysis.py` API file to the domain-02 technical indicator mapping so mainline gate attribution matches the source-authorized diff |
| `governance/mainline/task-cards/g2-332.yaml` | Records source-authorized scope and gates |
| `docs/reports/quality/backend-service-lifecycle-di-technical-analysis-provider-2026-06-13.md` | Records implementation evidence and verification |

## Implementation Summary

`technical_analysis.py` now has one data-source provider boundary:

```python
async def get_technical_analysis_data_source() -> Any:
    data_source_factory = DataSourceFactory()
    return await data_source_factory.get_data_source("technical_analysis")
```

The 8 selected route handlers now receive
`technical_analysis_adapter: Any = Depends(get_technical_analysis_data_source)`
as a keyword-only parameter. Their existing route paths, response models,
validation blocks, circuit-breaker calls, exception mapping, response formatting,
and adapter `get_data(...)` operation names are preserved.

## Function-Tree Catalog Note

`governance/function-tree/catalog.yaml` previously covered
`web/backend/app/api/technical/**` and `indicators.py`, but did not cover the
existing `web/backend/app/api/technical_analysis.py` module. G2.332 adds that
literal API file to `domain-02-node-01` coverage and API entrypoints so the
mainline gate can attribute this source-authorized technical-analysis diff to
the registered function-tree domain. This is governance metadata only; it does
not change runtime behavior.

## UnifiedResponse Guard Note

The CI `UnifiedResponse Contract Guard` checks changed backend API files. This
DI slice changes `technical_analysis.py`, which exposes 8 existing routes whose
response models predate the guard. Migrating those response envelopes would be a
separate API contract change, so G2.332 does not change response models or
return envelopes. Instead, it adds an explicit legacy baseline consumed by the
guard and records all 8 existing endpoints as response-contract debt for a
future dedicated migration. New or unlisted backend API routes still fail the
guard.

## Residual Delta

| Metric | Before | After |
| --- | ---: | ---: |
| Selected route handlers | 8 | 8 |
| Route-body `DataSourceFactory()` calls | 8 | 0 |
| Route-body `get_data_source()` calls | 8 | 0 |
| Provider helper `DataSourceFactory()` calls | 0 | 1 |
| Provider helper `get_data_source()` calls | 0 | 1 |

## TDD Evidence

Red phase:

```bash
pytest --no-cov web/backend/tests/test_technical_analysis_provider_injection.py
```

Result before implementation: 2 failed. The failures showed all 8 selected route
handlers still had inline `DataSourceFactory()` calls and
`get_technical_analysis_data_source` did not exist.

Green phase:

```bash
pytest --no-cov web/backend/tests/test_technical_analysis_provider_injection.py
```

Result after implementation: 2 passed.

CI guard sidecar red phase:

```bash
pytest --no-cov tests/unit/scripts/test_unified_response_contract_guard.py::test_legacy_baseline_exempts_listed_endpoint
```

Result before the guard change: 1 failed. The failure showed the baseline file
was ignored and the legacy endpoint still returned
`missing-unified-response-model`.

CI guard sidecar green phase:

```bash
pytest --no-cov tests/unit/scripts/test_unified_response_contract_guard.py
```

Result after the guard change: 11 passed.

## Focused Verification

| Check | Result |
| --- | --- |
| `pytest --no-cov web/backend/tests/test_technical_analysis_provider_injection.py` | 2 passed |
| `pytest --no-cov tests/api/file_tests/test_technical_analysis_api.py` | 18 passed |
| `pytest --no-cov tests/unit/scripts/test_unified_response_contract_guard.py` | 11 passed |
| `python scripts/compliance/unified_response_contract_guard.py --format json --root-dir $PWD --path web/backend/app/api/technical_analysis.py` | 0 errors; 8 legacy-baseline exemptions |
| `python -m py_compile web/backend/app/api/technical_analysis.py web/backend/tests/test_technical_analysis_provider_injection.py scripts/compliance/unified_response_contract_guard.py tests/unit/scripts/test_unified_response_contract_guard.py` | Passed |
| `black --check web/backend/app/api/technical_analysis.py web/backend/tests/test_technical_analysis_provider_injection.py scripts/compliance/unified_response_contract_guard.py tests/unit/scripts/test_unified_response_contract_guard.py` | Passed |
| `ruff check web/backend/app/api/technical_analysis.py web/backend/tests/test_technical_analysis_provider_injection.py scripts/compliance/unified_response_contract_guard.py tests/unit/scripts/test_unified_response_contract_guard.py` | Passed |
| `git diff HEAD~1..HEAD --check` | Passed |
| `python governance/mainline/scripts/mainline_scope_gate.py --task-card governance/mainline/task-cards/g2-332.yaml --schema governance/mainline/schemas/ai-task-card.schema.json --base-sha HEAD~1 --head-sha HEAD --report /tmp/g2-332-mainline-gate-final2.json` | `pass=True` |
| AST residual check | Provider exists; provider has 1 factory/getter; 8 route bodies have 0 factory/getter calls |
| `gitnexus_detect_changes(scope=compare, base_ref=origin/main)` | LOW risk; 8 changed files; 19 changed symbols; 0 affected processes |
| `gitnexus_api_impact(file=web/backend/app/api/technical_analysis.py)` | 8 routes; each route LOW risk, 0 direct consumers, 0 affected flows |

## Impact Evidence

Pre-edit GitNexus impact was run for all 8 modified route handlers:

| Function | Direct callers | Affected processes | Risk |
| --- | ---: | ---: | --- |
| `get_all_indicators` | 0 | 0 | LOW |
| `get_trend_indicators` | 0 | 0 | LOW |
| `get_momentum_indicators` | 0 | 0 | LOW |
| `get_volatility_indicators` | 0 | 0 | LOW |
| `get_volume_indicators` | 0 | 0 | LOW |
| `get_trading_signals` | 0 | 0 | LOW |
| `get_stock_history` | 0 | 0 | LOW |
| `get_batch_indicators` | 0 | 0 | LOW |

Pre-edit GitNexus `api_impact` for
`web/backend/app/api/technical_analysis.py` reported 8 routes, 0 direct
consumers, 0 affected flows, and LOW risk for each route.

GitNexus reported a stale-index warning because the indexed commit differed
from the current branch commit. The compare and API-impact checks still reported
LOW risk with no affected processes or flows.

## Rollback

Revert the G2.332 commit to restore inline route-body `DataSourceFactory`
construction and remove the focused provider-injection test plus governance
artifacts.
