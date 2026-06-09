# AkShare Market Gate Design

## Context

`expand-akshare-data-sources` has moved from broad API expansion into a repo-truth closure phase. The current rule is strict: MyStocks only integrates AkShare market endpoints when the locally installed `akshare` package exposes the exact same-named function. Missing functions remain gaps and must not be filled with adjacent providers, approximate APIs, or cross-project logic borrowed from `akquant`.

The current worktree is dirty, so this batch must stay isolated: new scripts, new tests, and minimal doc updates only. No runtime adapter or route behavior changes are allowed in this batch.

## Goals

- Add a machine-readable local availability probe for the tracked AkShare market functions in section 6 of `expand-akshare-data-sources`.
- Add a repo consistency gate that cross-checks local availability against OpenSpec tasks, repo-truth docs, registry presence, adapter methods, API routes, and focused tests.
- Produce standardized JSON reports for both steps.
- Keep MyStocks scoped to validation and audit only.

## Non-Goals

- Do not generate or scaffold new business endpoints.
- Do not change runtime adapter, API, caching, or batch-request logic.
- Do not implement missing AkShare functions in MyStocks.
- Do not import or mirror `akquant` implementation logic into this repository.

## Scope

### In Scope

- `scripts/dev/quality_gate/collect_akshare_market_function_availability.py`
- `scripts/dev/quality_gate/validate_akshare_market_repo_truth.py`
- Focused tests for both scripts
- Minimal AkShare maintenance / troubleshooting doc updates
- Optional implementation plan and design artifacts under `docs/superpowers/`

### Out of Scope

- `src/adapters/akshare/market_adapter/*.py`
- `web/backend/app/api/akshare_market/*.py`
- `config/data_sources_registry.yaml`
- OpenSpec task state changes unless future function availability materially changes

## Canonical Function Set

The gate tracks the current section 6 targets only:

- `stock_hot_follow_xq`
- `stock_board_change_em`
- `stock_news_main_em`
- `stock_zt_pool_em`
- `stock_dt_pool_em`
- `stock_strong_pool_em`
- `stock_weak_pool_em`
- `stock_changes_em`
- `stock_new_em`

## Design

### 1. Availability Probe

The probe script imports `akshare`, checks the canonical function set with `hasattr`, captures the installed `akshare` version when possible, and writes a JSON snapshot containing:

- generation metadata
- import status
- per-function availability
- summary counts and grouped lists

Missing functions are reported as data, not treated as automatic failures. Import failure is a hard failure.

### 2. Repo-Truth Gate

The gate script owns a single manifest that maps each canonical function to its expected repository artifacts:

- OpenSpec task id
- repo-truth documentation row
- registry key
- adapter method
- API route path
- focused tests

The script either reads a prior availability report or probes live. It then validates:

- OpenSpec task checkbox matches expected implemented / unimplemented state
- repo-truth doc row exists and carries the correct status semantics
- implemented functions have registry / adapter / route / focused test evidence
- unavailable functions do not leave behind implementation artifacts

The gate writes a JSON report with `pass`, `summary`, `functions`, and `violations`.

## Artifact Semantics

- Availability report answers: "What does local `akshare` expose right now?"
- Repo-truth gate answers: "Does this repository match that reality and our documented closure rules?"

Neither script generates business code or mutates OpenSpec automatically.

## Verification

- Targeted pytest for the probe script
- Targeted pytest for the repo-truth gate
- Direct CLI execution for both scripts against the live worktree

## Risks And Mitigations

- Parsing drift in markdown tables or task checkboxes:
  - Keep parsing narrow and anchored to section 6 wording that already exists in repo-truth docs.
- Dirty worktree noise:
  - Limit edits to new files plus two focused AkShare docs.
- Future scope creep into code generation:
  - Explicitly keep all outputs read-only and report-only.
