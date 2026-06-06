# Review: sequence-backend-architecture-unblocks

**Type**: md / proposal | **Perspective**: completeness, consistency, feasibility, architecture | **Date**: 2026-05-20

> **历史文档说明**:
> 本文件是审查快照，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Summary

The proposal correctly identifies that backend architecture work items are at different readiness levels and creates a sensible sequencing plan. The current proposal text now identifies the runtime blocker as the `web/backend/app/api/data_lineage.py` import chain reaching `web/backend/app/api/_data_lineage_responses.py`, where `@asynccontextmanager` was used without importing it. The tracked `tasks.md` file remains a completed historical execution record and is not revised by this review update.

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
- **Runtime blocker statement**: The current proposal names `_data_lineage_responses.py` and the missing `asynccontextmanager` import in the Why section.
- **Impact section**: The current proposal lists `web/backend/app/api/_data_lineage_responses.py` in affected code.
- **Spec wording**: The architecture-governance delta describes the failure mode as a missing transitive import in a response-helper module, not a bare package-relative import.

## Issues

- [x] **[HIGH]** Root cause of runtime blocker is identified in the proposal.
      Evidence: proposal.md now describes the `data_lineage.py` import chain reaching `_data_lineage_responses.py`, where `@asynccontextmanager` was used without importing it. The proposal no longer describes the blocker as a bare import in `data_lineage.py`.

- [x] **[HIGH]** Historical task wording is not treated as a new executable fix.
      Evidence: tasks.md is already closed at 33/33 and remains unchanged by this revision path. The proposal now carries the corrected root-cause narrative, and the completed runtime-unblock implementation evidence is referenced from `docs/reports/quality/backend-sequence-runtime-unblock-implementation-2026-05-20.md`.

- [x] **[MED]** Historical collection wording is scoped as completed evidence rather than current failure truth.
      Evidence: tasks.md remains a closed execution record. The proposal success criteria now require runtime evidence to record targeted health route collection or test result without asserting a current collection failure chain.

- [x] **[MED]** Proposal Impact section mentions `_data_lineage_responses.py` as affected code.
      Evidence: proposal.md lists `web/backend/app/api/_data_lineage_responses.py` before the broader route/helper module set.

- [x] **[MED]** Spec wording describes the missing transitive import failure mode.
      Evidence: the architecture-governance delta scenario says `app.main` import fails because a response-helper module in the route import chain has a missing transitive import.

- [x] **[LOW]** Proposal names the actual failing file.
      Evidence: proposal.md names `web/backend/app/api/_data_lineage_responses.py` in both Why and Impact.

## Suggestions

- Keep the corrected proposal root-cause narrative and affected-code list.
- Keep `tasks.md` unchanged as a completed historical execution record.
- Keep the architecture-governance delta focused on sequencing and evidence boundaries, without adding new requirements.
- Validate the single change and full OpenSpec set before accepting the backfill package.

## Verdict

READY_FOR_BACKFILL_ACCEPTANCE -- The proposal and delta now state the runtime blocker accurately, while the tracked tasks remain a closed historical execution record. The sequencing logic and governance structure are suitable for accepting this OpenSpec backfill package after strict validation and staged scope checks.
