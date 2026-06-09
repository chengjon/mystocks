# Backend Technical Analysis DataSourceFactory Provider Implementation - 2026-06-03

## Status

- Node: `G2.327`
- Status: source implementation ready for human review
- Parent: `G2.326 technical_analysis DataSourceFactory provider authorization preflight`
- Approval: user replied `同意，请继续`; source lane entered under `architecture/STANDARDS.md`
- Human review: required before merge
- Local review disposition: reviewed-but-not-merged as of `2026-06-03T22:08:19+08:00`

## Scope

Allowed source/test files:

- `web/backend/app/api/technical_analysis.py`
- `tests/api/file_tests/test_technical_analysis_api.py`

Forbidden surfaces preserved:

- `web/backend/app/services/data_source_factory/**`
- `web/backend/app/api/watchlist.py`
- `web/backend/app/api/strategy_management/**`
- `web/backend/app/api/_technical_analysis_models.py`
- `web/backend/app/api/_technical_analysis_responses.py`
- `docs/api/**`
- `web/frontend/**`
- `src/**`
- `config/**`
- `scripts/**`
- `openspec/**`
- PM2/runtime state

The two allowed files were already dirty before this implementation. Existing
local import cleanup in those files was preserved and not reverted.

## Implementation

`technical_analysis.py` now has a route-local provider:

```python
async def get_technical_analysis_data_source() -> Any:
    data_source_factory = DataSourceFactory()
    return await data_source_factory.get_data_source("technical_analysis")
```

The eight authorized route handlers now receive the adapter through:

```python
technical_analysis_adapter: Any = Depends(get_technical_analysis_data_source)
```

Affected handlers:

- `get_all_indicators`
- `get_trend_indicators`
- `get_momentum_indicators`
- `get_volatility_indicators`
- `get_volume_indicators`
- `get_trading_signals`
- `get_stock_history`
- `get_batch_indicators`

The shared DataSourceFactory package is unchanged. The route-local provider is
the only remaining backing location for `DataSourceFactory()` and
`get_data_source("technical_analysis")` in this module.

## TDD

Red:

- command: `pytest tests/api/file_tests/test_technical_analysis_api.py::TestTechnicalAnalysisAPIFile::test_data_source_factory_is_route_local_provider -q`
- result: failed as expected because `get_technical_analysis_data_source` was missing
- note: the repository default coverage fail-under also fired on this narrow run

Green:

- command: `pytest tests/api/file_tests/test_technical_analysis_api.py::TestTechnicalAnalysisAPIFile::test_data_source_factory_is_route_local_provider -q --no-cov`
- result: `1 passed`

Focused file test:

- command: `pytest tests/api/file_tests/test_technical_analysis_api.py -q --no-cov`
- result: `19 passed`

## Verification

Syntax:

- command: `python -m py_compile web/backend/app/api/technical_analysis.py tests/api/file_tests/test_technical_analysis_api.py`
- result: passed

Ruff:

- command: `ruff check web/backend/app/api/technical_analysis.py tests/api/file_tests/test_technical_analysis_api.py`
- result: `All checks passed!`

Static route contract check:

- HEAD routes: `8`
- Current routes: `8`
- result: route method/path summary unchanged

Static provider counts:

| Metric | Count |
|---|---:|
| module `DataSourceFactory()` calls | 1 |
| module `get_data_source(...)` calls | 1 |
| `Depends(get_technical_analysis_data_source)` bindings | 8 |
| handler direct `DataSourceFactory()` calls | 0 |
| handler direct `get_data_source(...)` calls | 0 |

## GitNexus

Pre-edit index refresh:

- command: `npx gitnexus analyze`
- result: repository indexed successfully in `519.9s`
- index size: `234825` nodes, `322154` edges, `2727` clusters, `300` flows

Impact evidence:

| Target | Risk | Direct callers | Affected processes |
|---|---|---:|---:|
| `web/backend/app/api/technical_analysis.py` routes via `api_impact` | LOW | 0 consumers | 0 |
| `technical_analysis.py` upstream impact | LOW | 1 | 0 |
| eight edited route handlers | LOW | 0 each | 0 each |

Change detection limitation:

- `gitnexus.detect_changes(scope=all)` timed out after `120s` because the local worktree is very dirty.
- `gitnexus.detect_changes(scope=staged)` also timed out after `120s` when only the two allowed source/test files were temporarily staged.
- temporary staging was restored; staged area is empty.

## Review Boundary

G2.327 is locally reviewed and accepted by the human maintainer, but it is not
merged and no PR was created. Keep `source_implementation_review_required` as
the source node state, with the review disposition recorded as
reviewed-but-not-merged. The next allowed action is a no-source G2.328 closeout
/ residual refresh for the technical analysis DataSourceFactory provider lane.
