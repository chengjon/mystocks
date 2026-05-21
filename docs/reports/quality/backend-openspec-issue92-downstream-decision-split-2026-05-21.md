# Backend OpenSpec Issue92 Downstream Decision Split

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: human-review draft
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Approval input: <https://github.com/chengjon/mystocks/issues/92#issuecomment-4503757722>
- Base HEAD: `25cbc4b0fd13eb60f1d620e77dd93a51ce97eec3`
- Scope: decision split and downstream issue/proposal boundaries only

## Boundary

This record is a draft decision packet for issue `#92`. It does not authorize
backend implementation, route mutation, Core file movement, PM2 workflow
execution, OpenSpec proposal creation, or movement of any issue to
`ready-for-agent`.

If accepted by the human maintainer, this packet should be used to create or
update downstream decision records. Implementation still requires an explicit
follow-up issue or OpenSpec branch with its own approval, impact analysis,
verification gates, and rollback plan.

## Input Evidence

| Input | Disposition used here |
|---|---|
| Issue `#92` | Approved for downstream decision work only; still open and not `ready-for-agent` |
| `backend-openspec-issue92-approval-record-2026-05-21.md` | Approval boundary source for this draft |
| Issue `#83` | Accepted and closed; shared C/E/F evidence package is the baseline |
| `split-backend-core-modules-with-compatibility-wrappers` archive | Completed baseline for the validation-helper split; not reopened here |
| `backend-core-split-task3-2-disposition-2026-05-21.md` | Task `3.2` is complete for the validation-helper package/wrapper scope |
| `backend-service-seam-proposal-path-2026-05-20.md` and review | No generic clean service pilot exists; use an interface/test-double pilot strategy |
| `backend-route-openapi-probe-refresh-2026-05-20.md` and review | Route/OpenAPI/probe evidence refreshed; `/metrics` duplicate is a control-plane taxonomy item |
| `backend-schema-shim-closure-implementation-2026-05-20.md` | Schema shim implementation evidence is complete; future retirement still needs a decision branch |
| `backend-error-contract-completion-verification-2026-05-19.md` | #77 / P3-C5 main migration is resolved; do not reopen without current-HEAD contradiction |

## Proposed Split

Issue `#92` should remain the parent human decision issue and should be split
into the following downstream tracks before any implementation issue is created.

| Track | Proposed child work | Type | State after this draft |
|---|---|---|---|
| D2.1 | `select-backend-technical-pattern-di-pilot` | decision/design issue or proposal candidate | draft-selected, not authorized |
| D2.2 | `decide-backend-core-validation-wrapper-retirement` | decision issue | deferred implementation |
| D2.3 | `refresh-backend-route-openapi-governance` | OpenSpec proposal candidate | evidence-ready, proposal uncreated |
| D2.4 | `settle-backend-backup-route-ownership` | OpenSpec proposal candidate | candidate, proposal uncreated |
| D2.5 | `stabilize-backend-control-plane-openapi-docs` | residual-tail decision issue | candidate, issue uncreated |
| D2.6 | `approve-backend-pm2-stateful-gate` | residual-tail approval issue | candidate, issue uncreated |

The parent issue should not be closed until a human maintainer accepts this split
or replaces it with a different decision structure.

## Issue92 Acceptance Mapping

| Issue92 criterion | Draft disposition |
|---|---|
| Exactly one low-risk DI pilot candidate is selected | Draft-select `TechnicalPatternDetectionService` as the first DI design pilot candidate. GitNexus upstream impact for `TechnicalPatternDetectionService` reported `LOW`, `impactedCount=0`, and `processes_affected=0`; text search shows one route consumer in `web/backend/app/api/_technical_patterns_router.py` plus focused tests. |
| If the selected DI pilot touches Core modules | Not applicable. The selected draft candidate is under `web/backend/app/services/technical_pattern_detection_service.py` and its route consumer is under `web/backend/app/api/`; no Core movement is part of this pilot. |
| Dependency override strategy is named | Introduce a route-local provider such as `get_technical_pattern_detection_service()` and use FastAPI `app.dependency_overrides` in tests. If implementation later avoids FastAPI dependency injection, the approved implementation plan must name the replacement strategy before coding. |
| Teardown artifact type is named | Pytest fixture that clears `app.dependency_overrides`; if an implementation uses `app.state`, the fixture must also remove the app-state key. |
| DI pilot rollback path is named | Revert the route from dependency-provider construction back to direct `TechnicalPatternDetectionService()` construction and leave the service class unchanged. |
| Validation messages split presence is recorded | Present in the target branch. Commit `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` is reachable from HEAD, and the canonical/compat files exist: `web/backend/app/core/validation/messages.py`, `web/backend/app/core/validation_messages.py`, `web/backend/app/core/validation/__init__.py`, and `tests/unit/core/test_validation_messages_compat.py`. |
| Next Core split planning lane or deferral is recorded | Defer Core Batch 2 implementation. The next Core work should be a wrapper-retirement readiness packet for `web/backend/app/core/validation_messages.py`, or a separately approved one-domain pure-helper packet. |
| Any selected next Core split batch is narrow | No Core implementation batch is selected in this draft. |
| No lifecycle-owned Core module is included | No lifecycle-owned Core module is selected. |
| Import smoke is named | Future Core decision packet must run an import smoke that includes `from app.core.logger import logger`, `from app.core.validation import CommonMessages`, and `from app.core.validation_messages import CommonMessages as CompatCommonMessages`. |
| PM2/backend smoke command is named without stateful execution | Non-stateful smoke: `PYTHONPATH=web/backend python -c "from app.main import app; print(len(app.routes))"`. Stateful PM2 workflow remains blocked behind explicit approval or a named equivalent. |
| Core rollback and wrapper-retirement criteria are named | Rollback is to restore the old compatibility wrapper/import path. Retirement criteria: no old-path imports except approved waivers, canonical import smoke passes, compatibility tests pass, backend import smoke passes, and rollback remains documented. |
| Trading follow-up strategy is recorded | Fold trading route ownership into `refresh-backend-route-openapi-governance` as a broader route ownership proposal candidate, using route table/OpenAPI evidence as input. Do not create a standalone trading implementation issue from `#92`. |
| Backup follow-up strategy is recorded | Create a separate backup route ownership proposal candidate, because backup route ownership has a clear ownership question and `cleanup_old_backups.py` must not be silently absorbed into health/status work. |
| `cleanup_old_backups.py` owner is assigned | Assign `backup_recovery_secure/cleanup_old_backups.py` to backup route ownership. Health/status taxonomy may reference it as a related control-plane consumer, but backup route ownership is the primary owner. |
| Held G drafts 08/09 disposition | Replace the held drafts with residual-tail issues: `stabilize-backend-control-plane-openapi-docs` and `approve-backend-pm2-stateful-gate`. |
| Aggregated issue remains single or splits | Split before implementation. Keep issue `#92` as the parent decision issue until human acceptance of the split. |
| Adopted codebase-map concerns are classified | See the concern classification table below. |
| Governance document updates | Update the steward tree now. Defer `web/backend/CONTEXT.md` and `docs/FUNCTION_TREE.md` updates until a concrete route/schema/service proposal is accepted. |
| No backend implementation mutation | Satisfied by this draft: governance documents only. |

## Concern Classification

| Concern | Downstream lane | Proposed disposition |
|---|---|---|
| Service seam and singleton lifecycle | D2.1 | First design pilot: `TechnicalPatternDetectionService`; no code until a concrete implementation plan is approved |
| Core helper continuation | D2.2 | Defer Batch 2; prepare wrapper-retirement readiness for validation messages first |
| API flat/package route ownership | D2.3 and D2.4 | Route governance handles trading broadly; backup receives a separate ownership proposal candidate |
| Health/status/control-plane OpenAPI | D2.5 | Residual-tail documentation stabilization, including the `/metrics` duplicate classification |
| PM2 workflow gate | D2.6 | Separate stateful approval issue or named equivalent; do not run from issue `#92` |
| Schema dual directory | Future schema branch | Use schema shim closure evidence; do not retire shims without a separate approved branch |
| CSRF composition root | Decision-only | Keep as a future decision candidate with test-factory exit criteria |
| Error contract canonicalization | Resolved evidence lane | Keep #77 / P3-C5 resolved unless current HEAD contradicts the completion evidence |
| miniQMT evidence | External evidence lane | Keep non-backend-blocking and non-promotion-authorizing |

## Proposed Downstream Order

1. Ask the human maintainer to review this split.
2. If accepted, comment on issue `#92` with the accepted split and keep
   `ready-for-agent` absent.
3. Draft D2.1 as the first concrete decision/design packet for
   `TechnicalPatternDetectionService`.
4. Draft D2.2 wrapper-retirement readiness for validation messages.
5. Draft route governance proposals for D2.3 and D2.4.
6. Create residual-tail decision issues for D2.5 and D2.6 only after the parent
   split is accepted.

## Verification Performed For This Draft

| Check | Result |
|---|---|
| GitHub issue `#92` state | `OPEN`; labels: `enhancement`, `ready-for-human`, `ready-for-downstream`; no `ready-for-agent` |
| Validation messages commit reachability | `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` exists and is reachable from HEAD |
| Validation messages files | canonical package, compatibility wrapper, package re-export, and compat test all exist |
| `TechnicalPatternDetectionService` GitNexus impact | `LOW`; impacted count `0`; affected processes `0` |
| `StockSearchService` GitNexus impact | `LOW`; impacted count `0`; retained as secondary design candidate because it has broader text consumers and module-level cache state |

## Human Review Questions

1. Should `TechnicalPatternDetectionService` be accepted as the first DI design
   pilot candidate, or should the service lane stay fully blocked until a
   broader interface/test-double proposal is drafted?
2. Should trading route ownership be folded into the broader route governance
   proposal, as proposed here, or split into its own follow-up proposal?
3. Should backup route ownership be a standalone proposal candidate, as proposed
   here, because `cleanup_old_backups.py` needs a clear owner?

