# B4.012-M3a-C4 Akshare adapter tests authorization prep

Date: 2026-06-15
HEAD: `50b6d1df4d73dde911e2b50dc8a71c3575923a2f`

## Goal

Prepare a scoped implementation batch for the remaining Akshare adapter test-family dirty files under `B4.012-M3a-C`.

This is a test-only hygiene and contract-standardization package. It must not modify source/runtime/OpenSpec/API/frontend code or other residual test families.

## Allowed Paths

- `tests/adapters/test_akshare_adapter/helpers.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part2.py`
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part3.py`
- `tests/test_akshare_adapter.py`
- `tests/unit/adapters/test_akshare_adapter.py`
- `tests/unit/adapters/test_akshare_adapter_real.py`
- `docs/reports/worklogs/claude-auto/b4-012-m3a-c4-akshare-adapter-tests-closeout-2026-06-15.md`

## Forbidden Scope

- No `src/` source edits.
- No runtime, OpenSpec, API, frontend, ST-HOLD, marketKlineData, generated/tooling, or external dirty edits.
- No `C5` other-adapter files.
- No `C6` DataSourceManager files.
- No untracked data-source provenance file.

## Current Baseline

The seven C4 files are all modified in the worktree.

Diff size:

- `tests/adapters/test_akshare_adapter/helpers.py`: 1 add / 3 deletions
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part1.py`: 1 add / 5 deletions
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part2.py`: 1 add / 5 deletions
- `tests/adapters/test_akshare_adapter/test_akshare_market_data_adapter_methods/part3.py`: 1 add / 5 deletions
- `tests/test_akshare_adapter.py`: 4 adds / 4 deletions
- `tests/unit/adapters/test_akshare_adapter.py`: 1 add / 1 deletion
- `tests/unit/adapters/test_akshare_adapter_real.py`: 2 adds / 2 deletions

Static baseline:

- `python -m py_compile` on the seven C4 files: passed
- `python -m ruff check` on the seven C4 files: failed with 302 findings
  - `PT009`: 296
  - `F841`: 4
  - `PT018`: 1
  - `F401`: 1

Focused pytest baseline:

- `python -m pytest --collect-only -q <seven C4 files>` collected 131 tests but hit the repository coverage gate and timed out after 60 seconds while producing coverage output.
- `python -m pytest --no-cov --tb=short -q --maxfail=1 <seven C4 files>` stopped after the first failure:
  - 22 passed
  - 1 failed
  - failing test: `tests/adapters/test_akshare_adapter/helpers.py::TestAkshareDataSourceTHSIndustry::test_get_ths_industry_names_success`
  - failure reason: `AkshareDataSource` has no `get_ths_industry_names` attribute.

## Implementation Intent

Allowed actions for this batch:

- Standardize test assertions and pytest style inside the seven allowed C4 files.
- Remove or repair unused imports / unused local variables inside the seven allowed C4 files.
- Align Akshare tests with the current adapter public contract without changing source code.
- Preserve test intent and external dependency isolation.

Forbidden actions:

- Do not add missing Akshare source methods.
- Do not change adapter runtime behavior.
- Do not broaden skip markers without owner / issue / ttl metadata.
- Do not touch neighboring C5/C6 dirty files.

## Required Gates

- `python -m py_compile` for the seven C4 files
- `python -m ruff check` for the seven C4 files
- Focused pytest on the seven C4 files, using `--no-cov`
- GitNexus `verify-staged` and `detect-changes`
- OPENDOG verification
- Exact staging only for allowed paths

## Decision

Prepared for `source-authorized` implementation as `B4.012-M3a-C4 Akshare adapter tests implementation`.
