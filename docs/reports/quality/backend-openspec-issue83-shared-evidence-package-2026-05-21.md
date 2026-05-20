# Backend OpenSpec Issue 83 Shared C/E/F Evidence Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-21

Status: ready for human review; evidence-only; no backend implementation is
authorized by this report.

GitHub issue: `#83` `[Backend OpenSpec] Build shared C/E/F evidence package`

Current evidence HEAD:

- Branch: `post-pr86-steward-sync`
- HEAD: `5f48cca02`
- Commit: `5f48cca02 Merge pull request #86 from chengjon/post-pr85-openspec-closure`
- Base: `origin/wip/root-dirty-20260403`

## Scope

This package reconciles the shared C/E/F evidence lane after PR `#85` and PR
`#86`:

- C: route table / OpenAPI / probe-governance evidence from the archived
  `sequence-backend-architecture-unblocks` line.
- E: singleton/getter lifecycle evidence from the service routing matrix.
- F: Core split compatibility evidence for the validation-messages Batch 1
  wrapper.

It intentionally does not:

- mutate backend implementation files;
- approve Core helper Batch 2;
- close OpenSpec task `3.2`;
- publish issue15;
- remove `BLOCKED_BY_TODO: shared evidence package.` from issue15;
- reopen the completed P3-C5 error-contract migration;
- convert evidence-only findings into implementation authorization.

## Acceptance Criteria Mapping

| Issue `#83` criterion | Current disposition |
|---|---|
| Evidence records branch and HEAD used for collection | Recorded above: branch `post-pr86-steward-sync`, HEAD `5f48cca02` |
| C route/OpenAPI evidence is refreshed, or blocker is recorded | Refreshed with placeholder required environment variables; result: `routes=548`, `openapi_paths=500`, `openapi_operations=536`, `duplicate_operation_ids=0`, `warnings=0` |
| F Core import compatibility accounts for validation messages Batch 1 | Legacy and canonical validation message symbols resolve to the same objects for all six checked exports |
| E singleton/getter lifecycle evidence is refreshed or explicitly confirmed current | Existing matrix remains the evidence source: `111` files matched patterns, `0` low-risk stateless pilot selected |
| No backend implementation files are modified | This package is documentation/governance only |
| No scope upgrade into implementation or runtime gate | Preserved; runtime smoke is evidence only |
| Issue15 remains unpublished and blocked until evidence acceptance | Preserved; this package is review input, not issue15 authorization |

## C Evidence: Route / OpenAPI

Initial `app.main` import without project runtime environment variables failed on
configuration preconditions:

- Missing: `POSTGRESQL_HOST`, `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD`,
  `JWT_SECRET_KEY`, `BACKEND_PORT`, `BACKEND_BACKUP_PORT`

The route/OpenAPI smoke was then rerun with local placeholder values only. No
real credential values were used, and no environment file was written.

Result:

```text
routes=548
openapi_paths=500
openapi_operations=536
duplicate_operation_ids=0
warnings=0
```

Observed stderr/stdout noise included CPU fallback warnings, monitoring/mock-data
initialization logs, and expected optional dependency warnings. None changed the
route/OpenAPI counts above.

## F Evidence: Core Validation Messages Compatibility

Validation message Batch 1 compatibility smoke:

```text
CommonMessages=True
MarketMessages=True
TechnicalMessages=True
TradeMessages=True
ErrorMessages=True
ValidationErrorBuilder=True
```

Interpretation:

- `app.core.validation_messages` remains a legacy compatibility wrapper.
- `app.core.validation.messages` is the canonical implementation path.
- The wrapper exports identity-equivalent objects for the checked symbols.
- OpenSpec task `3.2` remains intentionally unchecked; Batch 2 still requires an
  explicit follow-up decision before implementation.

## E Evidence: Singleton / Getter Lifecycle

Source report:

- `docs/reports/quality/backend-singleton-lifecycle-routing-matrix-2026-05-19.md`

Accepted evidence summary:

- `111` files matched singleton/getter/spec-loading patterns.
- `0` low-risk stateless pilot was selected.
- External-client wrappers, DB/session-backed services, cache/task-running
  services, process-level singletons, factory/helpers, and false positives must
  stay separated.
- The next service lifecycle step should use interface extraction and test-double
  design, not a random clean-pilot search.

## Decision Boundary

This report can be attached to issue `#83` as the shared C/E/F evidence package
for human review. It does not close issue `#83` by itself.

The next allowed decision after human acceptance is:

1. decide whether issue15 may consume this evidence;
2. decide whether `split-backend-core-modules-with-compatibility-wrappers` task
   `3.2` remains open, is explicitly marked non-blocking, or receives a concrete
   follow-up implementation plan;
3. keep Batch 2 blocked until that decision is explicit.
