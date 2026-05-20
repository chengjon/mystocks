# Review: sequence-backend-architecture-unblocks

**Type**: md / proposal | **Perspective**: completeness, consistency, feasibility, architecture | **Date**: 2026-05-20

> **历史文档说明**:
> 本文件是审查快照，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

The proposal correctly identifies that backend architecture work items are at different readiness levels and creates a sensible sequencing plan. However, it contains a **factual error** in its central claim: the runtime blocker is misidentified as a "bare import" in `data_lineage.py` when the actual failure is a missing `asynccontextmanager` import in `_data_lineage_responses.py`. Tasks 2.1-2.2 prescribe the wrong fix and will not resolve the blocker.

## Verified

- **A9 Named entities**: All referenced files and directories exist in the codebase: `data_lineage.py`, `app/schema/`, `app/schemas/`, `app/services/`, `docs/reports/quality/`, codebase-map artifacts, `markdown_governance_gate.py`.
- **A7 Backward compatibility**: Scope Boundaries explicitly prohibit deleting `app/schema/` until compatibility is proved. Sound.
- **C4 Acceptance criteria**: Success Criteria section provides 4 objective checkpoints. Adequate.
- **F5 Rollback plan**: Each phase is isolated; the proposal does not authorize implementation on its own (Scope Boundaries). Reversible by design.
- **F2 Dependency availability**: `openspec` CLI verified at `/root/.nvm/versions/node/v24.7.0/bin/openspec`. `markdown_governance_gate.py` exists.
- **N4 Cross-references**: Internal references between proposal, tasks, and spec are consistent and resolve correctly.
- **Schema consumer count**: Tasks.md 3.3 claims "three `from app.schema` consumers" -- confirmed: `test_validation_models.py`, `technical_analysis.py`, `stock_search_result.py`.
- **C5 Stakeholders**: Scope Boundaries clearly identify affected specs, code, and workflows.
- **N1 Terminology**: Terms "runtime unblock", "schema shim", "singleton lifecycle" are used consistently across all three documents.

## Issues

- [ ] **[HIGH]** Root cause of runtime blocker is misidentified -- proposal.md line 11, tasks.md 2.1
      Evidence: proposal says `data_lineage.py` "still uses a bare import that prevents `app.main` import." Actual code at `data_lineage.py:43` uses `from ._data_lineage_responses import (...)` which is a proper package-relative import. The real failure is `NameError: name 'asynccontextmanager' is not defined` in `_data_lineage_responses.py:403`. Verified by running `PYTHONPATH=web/backend python -c "from app.main import app"` -- traceback points to `_data_lineage_responses.py:403`, not `data_lineage.py`. Checked proposal Scope Boundaries and Why section -- neither mentions `_data_lineage_responses.py` or the missing import.

- [ ] **[HIGH]** Task 2.1 prescribes the wrong fix -- tasks.md line 16
      Evidence: Task 2.1 says "Update `web/backend/app/api/data_lineage.py` to use a package-relative import for `_data_lineage_responses`." The file already uses `from ._data_lineage_responses import (...)` at line 43. The fix belongs in `_data_lineage_responses.py` (add `from contextlib import asynccontextmanager`). Without correcting this, tasks 2.2-2.4 will show the same failure. Checked all of tasks.md Section 2 -- no mention of `_data_lineage_responses.py`.

- [ ] **[MED]** Task 1.2 implies a test failure chain that does not currently fail -- tasks.md line 10
      Evidence: Running `pytest web/backend/tests/test_health_route_conflicts.py --collect-only -q --no-cov` returns "No tests collected" (no error, exit 0). The task says "Reconfirm the current ... failure chain." A "no tests collected" result is not a failure chain. Checked tasks.md Sections 1 and 2 -- no clarification on what the expected failure looks like.

- [ ] **[MED]** Proposal Impact section does not mention `_data_lineage_responses.py` as affected code -- proposal.md line 39-43
      Evidence: The Impact section lists `web/backend/app/api/data_lineage.py` but not `web/backend/app/api/_data_lineage_responses.py`. Since the actual blocker lives in the latter file, it should be listed. Verified by grep: `_data_lineage_responses.py` is the file containing the `NameError`. Checked the entire proposal -- file is not referenced anywhere.

- [ ] **[MED]** Spec.md uses imprecise language "bare package-relative dependency" -- spec.md line 8
      Evidence: Spec says "WHEN `app.main` import fails on a bare package-relative dependency." The term "bare package-relative dependency" is ambiguous -- the actual import is already package-relative (`from .`). The failure is a missing transitive import, not a bare dependency. Checked the full spec -- no further clarification of what "bare package-relative dependency" means.

- [ ] **[LOW]** Proposal does not name the actual failing file anywhere -- proposal.md
      Evidence: The file `_data_lineage_responses.py` is never mentioned in proposal.md, tasks.md, or spec.md. The 409-line file contains the `@asynccontextmanager` decorator at line 403 without the corresponding import. Any implementer would need to discover this independently.

## Suggestions

- Amend proposal.md line 11 to read: `_data_lineage_responses.py` uses `@asynccontextmanager` without importing it, which prevents `app.main` from importing. Update the Why section and Impact section accordingly.
- Rewrite task 2.1 as: "Add `from contextlib import asynccontextmanager` to `web/backend/app/api/_data_lineage_responses.py`." Keep the remaining task 2 items as-is since verification steps are correct.
- Add `_data_lineage_responses.py` to the "Affected code" list in the Impact section.
- Rewrite task 1.2 to specify the expected current state explicitly: e.g., "Confirm `test_health_route_conflicts.py --collect-only` either collects 0 tests or fails, and record which."
- Replace "bare package-relative dependency" in spec.md with a precise description of the actual failure mode (missing transitive import in a response-helpers module).

## Verdict

NEEDS_REVISION -- The central factual claim (root cause of the runtime blocker) is wrong, and the primary fix task (2.1) targets the wrong file. The sequencing logic and governance structure are sound, but the proposal cannot be executed as written.
