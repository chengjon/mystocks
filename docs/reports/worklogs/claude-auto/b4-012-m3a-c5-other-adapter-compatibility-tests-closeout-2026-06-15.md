# B4.012-M3a-C5 Other Adapter Compatibility Tests Closeout

Date: 2026-06-15
Branch: `wip/root-dirty-20260403`
Implementation commit: `e231f0a45 B4.012-M3a-C5: standardize other adapter tests`
FUNCTION_TREE node: `artdeco-web-design-governance/b4-012-m3a-c5-other-adapter-compatibility-tests-authorization`

## Scope

Allowed test files only:

- `tests/unit/adapters/test_baostock_adapter_real.py`
- `tests/unit/adapters/test_byapi_adapter_basic.py`
- `tests/unit/adapters/test_customer_adapter_basic.py`
- `tests/unit/adapters/test_financial_adapter_real.py`
- `tests/unit/adapters/test_financial_adapter_simple.py`
- `tests/unit/adapters/test_tdx_connection_manager.py`
- `tests/unit/adapters/test_tushare_adapter_basic.py`

No changes were made to C6/DataSourceManager, `tests/data_sources/test_query_builder.py`, source/runtime/OpenSpec/API/frontend/generated/tooling/untracked provenance/ST-HOLD/marketKlineData, or external dirty files.

## What Landed

- Updated baostock tests from stale module-global patching to lazy-import `sys.modules` patching and baostock-style cursor mocks.
- Aligned baostock assertions with current formatted symbols, dict-returning stock-basic contract, and empty-result handling.
- Updated financial adapter tests to no-arg initialization, current availability flags, current legacy data methods, cache wrapper shape, and fake `efinance` isolation.
- Updated TDX connection manager tests to current thin-delegation behavior, 6-digit symbol market-code contract, module-level logger, and retry decorator ownership.
- Cleaned local test style issues in byapi, customer, and tushare tests without touching runtime logic.

## Verification

Local focused gates:

- `python -m py_compile <7 C5 test files>`: passed
- `python -m ruff check <7 C5 test files>`: passed
- `python -m pytest --no-cov --tb=short -q <7 C5 test files>`: `115 passed, 2 warnings in 1.11s`

Known non-blocking warning:

- Baostock failure-path tests surface an existing runtime destructor warning when `BaostockDataSource.__del__` calls `self.bs.logout()` after failed import sets `self.bs = None`. This is not changed in C5 because source/runtime edits were out of scope.

Governance and safety gates:

- FUNCTION_TREE scope-check: 7 changed files within active authorization
- `git diff --cached --check`: passed
- GitNexus `verify-staged`: low risk, 7 files, 61 symbols, 0 affected processes
- GitNexus `detect-changes --scope staged`: low risk, 7 files, 61 symbols, 0 affected processes
- GitNexus post-commit index refresh: `222,097 nodes | 278,900 edges | 2932 clusters | 300 flows`
- OPENDOG `run-verification` lint id `119`: passed
- OPENDOG `run-verification` test id `120`: passed, with suspicious-pass note caused by the known baostock destructor warning in passed output

## Disposition

B4.012-M3a-C5 implementation is complete. The test compatibility surface now reflects the current adapter contracts without modifying source/runtime behavior. C6/DataSourceManager remains untouched for a separate authorization path.
