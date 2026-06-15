# B4.012-M3a-C4 Akshare Adapter Tests Closeout

- Node: `b4-012-m3a-c4-akshare-adapter-tests-authorization`
- Program: `.governance/programs/artdeco-web-design-governance`
- Scope: C4 Akshare adapter test family only
- Implementation commit: `7efcc8cf1 B4.012-M3a-C4: standardize Akshare adapter tests`
- Closeout date: 2026-06-15

## Landed Changes

- Standardized C4 Akshare test files to current pytest fixture style and async test execution where required.
- Replaced stale Akshare mock targets with the runtime entrypoints used by current adapters.
- Sealed fallback and realtime tests from real network calls by mocking `stock_zh_a_spot`, `stock_zh_a_hist`, and current index endpoints as needed.
- Updated current `get_stock_basic(symbol)` assertions from legacy DataFrame-list behavior to the current single-symbol dict contract.
- Reframed stock daily fallback coverage from stale same-call retry expectations to current primary-api-to-spot-fallback behavior.
- Added owner/issue/ttl metadata to known legacy-method and source-gap xfails without changing production source.

## Explicit Non-Changes

- No source/runtime files were modified.
- No OpenSpec, API, frontend, generated/tooling, C5/C6, ST-HOLD, marketKlineData, or external dirty files were modified.
- No adapter runtime behavior was changed.

## Verification

- `python -m ruff check <7 C4 allowed test files>`: passed.
- `python -m py_compile <7 C4 allowed test files>`: passed.
- `python -m pytest --no-cov --tb=short -q <7 C4 allowed test files>`: passed via OPENDOG run id `118`.
- C4 aggregate pytest result: `120 passed, 4 skipped, 7 xfailed, 2 warnings in 94.88s`.
- OPENDOG verification: fresh, no cleanup blockers, no refactor blockers, no failing runs.
- GitNexus staged verify/detect before implementation commit: low risk, 10 files, 120 changed symbols, 0 affected processes.
- `git diff --cached --check`: passed before implementation commit.
- GitNexus post-commit index refresh: completed successfully; `222,073 nodes`, `278,875 edges`, `2,926 clusters`, `300 flows`.

## Residual Notes

- `test_get_index_daily_success` remains a conditional xfail because `AkshareDataSource.get_index_daily` currently depends on an unexposed `_process_index_data` helper. This is a source-side follow-up and was intentionally not fixed under C4 test-only authorization.
- Legacy `get_stock_concept`, `get_stock_sector`, `get_ths_industry_names`, `get_minute_kline`, and `get_industry_classify` expectations remain xfailed where the current `AkshareDataSource` does not expose those legacy methods.

## Boundary Result

C4 is safe to close. The Akshare test family is standardized and no longer relies on stale pytest setup, stale mock paths, or real-network fallback behavior inside the focused gate.
