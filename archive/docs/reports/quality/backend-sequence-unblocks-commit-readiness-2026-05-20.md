# Backend Sequence Unblocks Commit Readiness - 2026-05-20

> **历史文档说明**:
> 本文件是 `sequence-backend-architecture-unblocks` 的 path-limited commit readiness 记录。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: ready for human commit decision
- Branch: `wip/root-dirty-20260403`
- HEAD: `7b097fffd`
- Total dirty entries in current worktree at readiness scan: `1493`
- Relevant entries for this line: `35`
- Unrelated dirty entries: `1473`
- Commit performed by this report: no

## Commit Boundary

This line must be committed with explicit paths only. Do not run broad `git add .`,
directory-wide staging outside the listed paths, or any cleanup command that touches
unrelated dirty files.

The two paired review files are review inputs, not required implementation artifacts:

- `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20-review.md`
- `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20-review.md`

Include them only if the human maintainer explicitly wants review artifacts in the same
commit set. Otherwise leave them unstaged.

## Recommended Commit Split

| Commit | Scope | Purpose |
|--------|-------|---------|
| 1 | Runtime + schema implementation | Restore import/runtime readiness and canonicalize validation model imports |
| 2 | Governance + evidence artifacts | Record OpenSpec task completion, route/OpenAPI/probe evidence, service proposal path, and codebase-map updates |

This split keeps source edits reviewable separately from the governance artifact volume.
If a single commit is required, use the same explicit file list and keep unrelated dirty
files out of staging.

## Commit 1 Candidate Paths

Runtime unblock and schema shim implementation paths:

- `web/backend/app/api/_data_lineage_responses.py`
- `web/backend/app/api/data_lineage.py`
- `web/backend/app/api/_data_source_config_responses.py`
- `web/backend/app/api/data_source_config.py`
- `web/backend/app/api/_technical_analysis_responses.py`
- `web/backend/app/api/technical_analysis.py`
- `web/backend/app/api/_governance_dashboard_responses.py`
- `web/backend/app/api/_monitoring_watchlists_models.py`
- `web/backend/app/api/_monitoring_watchlists_responses.py`
- `web/backend/app/api/monitoring_watchlists.py`
- `web/backend/app/api/_watchlist_responses.py`
- `web/backend/app/api/signal_monitoring/signal_history_response.py`
- `web/backend/app/api/_technical_analysis_models.py`
- `web/backend/app/api/data_quality.py`
- `web/backend/app/api/indicators/indicator_cache.py`
- `web/backend/app/api/indicators/__init__.py`
- `web/backend/app/api/trade/routes.py`
- `web/backend/app/api/data_source_registry.py`
- `web/backend/app/api/stock_search/stock_search_result.py`
- `web/backend/app/schema/validation_models.py`
- `web/backend/app/schemas/__init__.py`
- `web/backend/app/schemas/validation_models.py`
- `web/backend/tests/test_validation_models.py`

Suggested commit message:

```text
fix(backend): unblock runtime imports and canonicalize schema shim
```

## Commit 2 Candidate Paths

Governance, OpenSpec, and evidence paths:

- `.planning/codebase/CODEBASE-MAP-REVIEW-2026-05-18.md`
- `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md`
- `.planning/codebase/generated/backend-route-table-2026-05-20.json`
- `.planning/codebase/generated/probe-consumer-matrix-2026-05-20.json`
- `.planning/codebase/generated/route-openapi-snapshot-2026-05-20.json`
- `.planning/codebase/generated/service-singleton-inventory-2026-05-20.json`
- `docs/superpowers/plans/2026-05-19-codebase-map-openspec-execution-plan.md`
- `docs/reports/quality/backend-route-openapi-probe-refresh-2026-05-20.md`
- `docs/reports/quality/backend-schema-shim-closure-implementation-2026-05-20.md`
- `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md`
- `docs/reports/quality/backend-service-seam-proposal-path-2026-05-20.md`
- `docs/reports/quality/backend-sequence-unblocks-commit-readiness-2026-05-20.md`
- `openspec/changes/sequence-backend-architecture-unblocks/`

Suggested commit message:

```text
docs(backend): record sequence architecture unblock evidence
```

## Validation Already Run

| Gate | Result |
|------|--------|
| targeted schema ruff | passed |
| `test_validation_models.py` | `60 passed` |
| route/OpenAPI/probe artifacts | generated and parsed |
| markdown governance on touched reports/tasks | passed |
| `openspec validate sequence-backend-architecture-unblocks --strict` | valid; PostHog telemetry flush still reports `ECONNREFUSED` after validation |
| path-limited `git diff --check` | no output |

## Pre-Commit Gate

Before committing:

1. Stage only the selected paths for the intended commit split.
2. Run `git status --short` and confirm no unrelated dirty path is staged.
3. Run `gitnexus_detect_changes(scope="staged")` for each source-edit commit.
4. Re-run path-limited `git diff --cached --check`.
5. For governance-only commit, re-run markdown governance and OpenSpec validate.

## Current Next Decision

Original pre-attempt decision options were:

- approve the two-commit split above,
- request a single explicit-path commit,
- or keep the branch uncommitted for further review.

The maintainer selected the single explicit-path commit option. That attempt is
now recorded in the next section and is blocked by the UnifiedResponse contract
gate.

No OpenSpec archive should run until the accepted commit state is clear.

## Combined Commit Attempt

The maintainer selected the single explicit-path commit option in the review
thread.

Result: no commit was created.

Attempted command:

```bash
git commit -m "chore(backend): record sequence architecture unblocks"
```

First hook stop:

- `Backend Singleton None Guard` rejected
  `web/backend/app/api/monitoring_watchlists.py`.
- GitNexus impact was run for
  `web/backend/app/api/monitoring_watchlists.py` before editing.
- Impact result: `LOW`, impacted count `0`.
- Fix applied: runtime watchlist globals are now explicit top-level
  `Optional[...] = None` declarations.
- Follow-up validation:
  - `python scripts/compliance/backend_singleton_none_guard.py web/backend/app/api/monitoring_watchlists.py`
    reported `errors: 0`.
  - targeted staged `ruff check` passed.
  - `env PYTHONPATH=web/backend pytest -o addopts= web/backend/tests/test_validation_models.py -q --no-cov --tb=short`
    reported `60 passed`.
  - `env PYTHONPATH=web/backend python -c "from app.main import app; print('routes', len(app.routes))"`
    reported `routes 548`.

Second hook stop:

- `UnifiedResponse Contract Guard` rejected staged backend API route files.
- Reproduced guard summary for the staged API file set:
  - `checked_files`: `18`
  - `checked_routes`: `72`
  - `errors`: `34`
- Failing files:
  - `web/backend/app/api/data_quality.py`: `9` route-contract errors
  - `web/backend/app/api/indicators/indicator_cache.py`: `6`
    route-contract errors
  - `web/backend/app/api/signal_monitoring/signal_history_response.py`: `4`
    route-contract errors
  - `web/backend/app/api/stock_search/stock_search_result.py`: `7`
    route-contract errors
  - `web/backend/app/api/technical_analysis.py`: `8`
    route-contract errors

Disposition:

- The staged file set remains path-limited and explicit, but the combined commit
  is blocked by an API response-contract gate.
- Do not satisfy this gate by opportunistically migrating 34 route contracts
  inside this commit. That would be a wider API contract implementation task and
  requires its own approved scope, impact analysis, route/OpenAPI evidence, and
  regression tests.
- Do not use `--no-verify`; it would hide a real repository contract gate.

Recommended next decision:

- split or narrow the commit so governance evidence that does not touch failing
  route files can land first, or
- create an explicit follow-up implementation lane for the five failing route
  modules and run it through the normal OpenSpec/GitNexus/test gates, or
- keep the index staged for further human review.
