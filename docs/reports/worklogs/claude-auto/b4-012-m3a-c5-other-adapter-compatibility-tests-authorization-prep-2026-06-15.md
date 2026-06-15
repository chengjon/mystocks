# B4.012-M3a-C5 Other Adapter Compatibility Tests Authorization Prep

- Node: `b4-012-m3a-c5-other-adapter-compatibility-tests-authorization`
- Program: `.governance/programs/artdeco-web-design-governance`
- Phase: no-source boundary audit and authorization preparation
- Current HEAD: `ecd9947c8897c2db730e81808774a20513883b9a`
- Date: 2026-06-15

## Scope Candidate

C5 is limited to the tracked other-adapter compatibility test family:

- `tests/unit/adapters/test_baostock_adapter_real.py`
- `tests/unit/adapters/test_byapi_adapter_basic.py`
- `tests/unit/adapters/test_customer_adapter_basic.py`
- `tests/unit/adapters/test_financial_adapter_real.py`
- `tests/unit/adapters/test_financial_adapter_simple.py`
- `tests/unit/adapters/test_tdx_connection_manager.py`
- `tests/unit/adapters/test_tushare_adapter_basic.py`

Closeout evidence path:

- `docs/reports/worklogs/claude-auto/b4-012-m3a-c5-other-adapter-compatibility-tests-closeout-2026-06-15.md`

## Explicit Exclusions

- C6 `DataSourceManager` files:
  - `tests/unit/adapters/test_data_source_manager.py`
  - `tests/unit/adapters/test_data_source_manager_basic.py`
  - `tests/unit/adapters/test_data_source_manager_fixed.py`
- `tests/data_sources/test_query_builder.py`
- generated/tooling overlap: `tests/generated/test_new_market_data_adapter_new_feature.py`
- untracked provenance directories, including `tests/unit/data_source/`
- source/runtime/OpenSpec/API/frontend files
- ST-HOLD, marketKlineData, and all external dirty files

## Current Dirty Boundary

The 7 C5 files are all modified tracked test files. Current diff size is small and localized:

- `test_baostock_adapter_real.py`: 1 insertion, 1 deletion
- `test_byapi_adapter_basic.py`: 1 insertion, 1 deletion
- `test_customer_adapter_basic.py`: 2 insertions, 2 deletions
- `test_financial_adapter_real.py`: 2 insertions, 2 deletions
- `test_financial_adapter_simple.py`: 2 insertions, 2 deletions
- `test_tdx_connection_manager.py`: 1 insertion, 3 deletions
- `test_tushare_adapter_basic.py`: 1 insertion, 1 deletion

Current visible diffs are marker metadata updates and import cleanup residue. They do not change production behavior.

## No-Source Verification Baseline

- `python -m py_compile <7 C5 files>`: passed.
- `python -m ruff check <7 C5 files>`: failed with 8 style/test issues:
  - `tests/unit/adapters/test_customer_adapter_basic.py`: E712 boolean equality assertions.
  - `tests/unit/adapters/test_tushare_adapter_basic.py`: PT019 injected unused patch fixture.
  - Remaining hidden unsafe fixes are localized to test style cleanup.
- Focused pytest baseline:
  - `tests/unit/adapters/test_byapi_adapter_basic.py`: `18 passed`
  - `tests/unit/adapters/test_customer_adapter_basic.py`: `15 passed`
  - `tests/unit/adapters/test_tushare_adapter_basic.py`: `19 passed`
  - `tests/unit/adapters/test_baostock_adapter_real.py`: fails at stale module patch target `src.adapters.baostock_adapter.bs`.
  - `tests/unit/adapters/test_financial_adapter_real.py`: fails at stale module patch target `src.adapters.financial_adapter.efinance`.
  - `tests/unit/adapters/test_financial_adapter_simple.py`: fails because `FinancialDataSource.__init__()` no longer accepts `api_key`.
  - `tests/unit/adapters/test_tdx_connection_manager.py`: fails because `TdxConnectionManager` no longer exposes an instance `logger` attribute.

## Runtime Contract Observations

- `BaostockDataSource` imports `baostock` lazily inside `__init__` and stores the module as `self.bs`; the module does not expose `src.adapters.baostock_adapter.bs`.
- `FinancialDataSource.__init__()` takes no `api_key` argument and sets `efinance_available` / `easyquotation_available` based on lazy imports.
- `financial_adapter.py` does not expose module-level `efinance`; tests must avoid patching non-existent module globals.
- `TdxConnectionManager` uses module-level `logger` and does not expose `manager.logger`.

## Proposed Authorized Actions

If source/test implementation is approved, restrict changes to:

- Test-only contract alignment with current adapter constructor signatures and runtime patch targets.
- Test-only ruff cleanup for the 7 C5 files.
- Focused tests/verification only for this adapter compatibility family.
- Closeout report update.

No source/runtime implementation change is needed or requested for C5.

## Proposed Gates

- `python -m py_compile <7 C5 files>`
- `python -m ruff check <7 C5 files>`
- Focused pytest for the 7 C5 files
- GitNexus staged verify/detect, expected low risk and 0 production processes affected
- OPENDOG fresh verification with no failing runs/blockers
- Exact staging containing only authorized C5 files plus governance/worklog files

## Authorization Recommendation

Prepare `B4.012-M3a-C5` for source-authorized test implementation, limited to the 7 C5 test files and the closeout worklog path above. Keep C6 and all external dirty state out of this package.
