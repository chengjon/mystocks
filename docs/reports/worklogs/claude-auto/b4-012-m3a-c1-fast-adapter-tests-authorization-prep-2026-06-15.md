# B4.012-M3a-C1 fast adapter compatibility tests authorization prep

Date: 2026-06-15 Asia/Shanghai

## Scope

- Parent split node: `b4-012-m3a-c-adapter-data-source-tests-split`
- Proposed implementation node: `b4-012-m3a-c1-fast-adapter-tests-authorization`
- Mode: no-source authorization preparation
- Source edits authorized: no

## Current-head boundary

- Current HEAD: `e4877ce7c B4.012-M3a-B4: close tracked contract tests`
- Staged files: none at audit start
- M3a-C tracked candidate count remains 25 modified files.
- M3a-C still has no source edit authorization at the parent node.

## Candidate family split

The prior C split remains valid, but the adapter family is too broad for one implementation batch.

### C1-A deferred: Akshare split adapter assertion migration

- Files: 4
- Main risk: large mechanical assertion conversion
- Ruff result: 299 issues in this subgroup, mostly `PT009`.
- Disposition: defer to a dedicated authorization because the diff would be large even though the changes are test-only.

Files:

- `tests/adapters/test_akshare_adapter/helpers.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part2.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part3.py`

### C1-fast proposed first implementation batch

This batch is fast-verifiable, already passes focused static and runtime checks at the current dirty baseline, and avoids the Akshare slow/network path.

Allowed implementation files:

- `tests/adapters/test_financial_adapter_refactored.py`
- `tests/adapters/test_tdx_adapter_refactored.py`
- `tests/test_tdx_adapter.py`

Closeout report:

- `docs/reports/worklogs/claude-auto/b4-012-m3a-c1-fast-adapter-tests-closeout-2026-06-15.md`

### C1-B/C deferred: mixed adapter basics, real adapters, manager tests

- Files: 13 remaining non-Akshare-split adapter files after C1-fast
- Main risks:
  - Slow or external dependency behavior observed when `tests/test_akshare_adapter.py` entered execution.
  - `tests/unit/adapters/test_data_source_manager.py` left a long-running single-file probe before natural exit.
  - 15 ruff issues remain across the 16-file non-Akshare-split pool before removing the three C1-fast files.
- Disposition: split after C1-fast into smaller low-delta and slow/network packages.

## Verification evidence

Current-head no-source probes:

- `python -m py_compile` on all 20 adapter-family files: passed.
- `python -m ruff check` on all 20 adapter-family files: failed with 314 issues.
  - Top codes: `PT009` 296, `F841` 9, `E712` 6, `PT018` 1, `F401` 1, `PT019` 1.
- Full C1 adapter-family pytest was terminated after exceeding 3.5 minutes during boundary review.
- 16-file non-Akshare-split pytest timed out after 90 seconds after entering slow Akshare behavior.
- `tests/test_tdx_adapter.py` single-file pytest: `12 passed in 1.12s`.
- Proposed C1-fast focused verification:
  - `python -m py_compile tests/adapters/test_financial_adapter_refactored.py tests/adapters/test_tdx_adapter_refactored.py tests/test_tdx_adapter.py`: passed.
  - `python -m ruff check tests/adapters/test_financial_adapter_refactored.py tests/adapters/test_tdx_adapter_refactored.py tests/test_tdx_adapter.py`: passed.
  - `python -m pytest --no-cov --tb=short -q tests/adapters/test_financial_adapter_refactored.py tests/adapters/test_tdx_adapter_refactored.py tests/test_tdx_adapter.py`: `45 passed in 2.17s`.

## Non-goals

- Do not modify `src/`, `web/`, `scripts/runtime/`, `openspec/`, `ST-HOLD`, or `marketKlineData`.
- Do not touch `tests/api/file_tests/run_file_tests.py`; it remains an external dirty file.
- Do not include Akshare split adapter assertion migration in C1-fast.
- Do not include slow/network Akshare root or real adapter tests in C1-fast.
- Do not delete or move tests.

## Required implementation gates

If approved, C1-fast implementation must run:

- GitNexus impact / staged verification.
- `python -m py_compile` for the 3 allowed test files.
- `python -m ruff check` for the 3 allowed test files.
- `python -m pytest --no-cov --tb=short -q` for the 3 allowed test files.
- `git diff --cached --check`.
- Function Tree `scope-check`.
- GitNexus `verify-staged` and `detect-changes --scope staged`.
- OPENDOG verification check.
- Post-commit GitNexus `analyze --index-only`.

## Authorization request

Prepare `b4-012-m3a-c1-fast-adapter-tests-authorization` for implementation with only the three C1-fast test files and the closeout worklog allowed. This is test-only standardization and must not touch production source, runtime scripts, OpenSpec, or any external dirty file.
