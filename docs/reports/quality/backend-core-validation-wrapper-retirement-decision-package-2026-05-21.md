# Backend Core Validation Wrapper Retirement Decision Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: D2.2c decision package prepared; no deletion executed
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Track: D2.2c validation compatibility-wrapper retirement / retention decision
- Base HEAD: `7d4e86d71e2f505f698f028b184f59d4da7b43df`
- Prior implementation evidence:
  - D2.2a PR `#99`: active source import migration
  - D2.2b PR `#100`: docs/API example canonicalization

## Boundary

This package is decision and evidence only.

It does not delete `web/backend/app/core/validation_messages.py`, does not modify
backend source, does not modify tests, does not modify OpenSpec change/spec files,
does not change route/OpenAPI runtime behavior, does not run PM2, and does not
move any issue to `ready-for-agent`.

## Decision Question

Should the compatibility wrapper `web/backend/app/core/validation_messages.py`
remain available as a long-term compatibility path, or should a future approved
batch retire it?

## Current Evidence Snapshot

| Evidence | Result |
|---|---|
| Wrapper file | `web/backend/app/core/validation_messages.py` exists |
| Canonical package | `app.core.validation` imports successfully |
| Compatibility identity smoke | `CommonMessages` and `ValidationErrorBuilder` are identity-equivalent from canonical and wrapper paths |
| Compatibility test | `tests/unit/core/test_validation_messages_compat.py`: `2 passed` |
| Active source import scan | `active_source_legacy_imports_excluding_wrapper=0` |
| Active source text-only reference | `web/backend/app/core/error_codes.py` contains one historical comment text reference; it is not an import consumer |
| Docs/API legacy scan | `docs/api/` legacy `validation_messages` references: `0` |
| Boundary test | `tests/unit/core/test_validation_import_boundaries.py`: `1 passed` |
| Current issue state | Issue `#92` remains `OPEN`, with `ready-for-human` and `ready-for-downstream`; no `ready-for-agent` label |

## Consumer Matrix

| Consumer class | Current state | Decision impact |
|---|---|---|
| Active backend source imports | `0` import consumers outside the wrapper | No known runtime source blocker to a future deletion batch |
| Docs/API examples | `0` legacy references | D2.2b closed the public example blocker |
| Compatibility tests | `tests/unit/core/test_validation_messages_compat.py` still imports the wrapper intentionally | Must be converted, deleted, or replaced in any deletion batch |
| Boundary tests | `tests/unit/core/test_validation_import_boundaries.py` contains the legacy path as a forbidden import sentinel | Keep or adjust depending on final retirement decision |
| Wrapper self | `web/backend/app/core/validation_messages.py` documents the historical path | Removed only in an approved deletion batch |
| Historical/governance docs | 23 historical/governance doc files, 79 text hits | Treat as historical evidence unless a separate documentation cleanup is approved |
| Mainline task cards | 3 governance task-card files, 12 text hits | Retain as audit trail |
| Structure baseline reports | 2 baseline files, 5 text hits | Retain as generated historical baseline |

## Option A: Retain Wrapper

Retain `web/backend/app/core/validation_messages.py` as a documented compatibility
wrapper.

Recommended when:

- avoiding churn in compatibility tests and historical references is preferred;
- downstream or external consumers might still rely on the legacy import path;
- the team wants a stable fallback while additional Core split work proceeds.

Required follow-up if selected:

- record explicit long-term retention in the task tree and issue `#92`;
- keep `tests/unit/core/test_validation_messages_compat.py`;
- keep active source and docs/API canonicalization guards.

## Option B: Retire Wrapper In A Future Batch

Approve a separate implementation batch to remove
`web/backend/app/core/validation_messages.py`.

Prerequisites:

- explicit human approval for deletion;
- path-limited task card for the deletion batch;
- GitNexus impact analysis before code deletion;
- compatibility test conversion, removal, or replacement;
- boundary test review so it continues to enforce canonical imports;
- active source import scan remains `0`;
- docs/API legacy scan remains `0`;
- rollback plan restores the wrapper exactly if downstream imports fail.

Suggested deletion-batch verification:

- `PYTHONPATH=web/backend pytest -o addopts= tests/unit/core/test_validation_import_boundaries.py -q --no-cov`
- selected replacement or retirement test for compatibility coverage;
- canonical import smoke for `app.core.validation`;
- `app.main` import smoke;
- `git diff --check`;
- mainline scope gate;
- GitNexus staged/compare risk check.

## Decision Package Recommendation

Do not delete the wrapper from this package.

For the next human decision, choose exactly one of:

1. retain `app.core.validation_messages` as a long-term compatibility wrapper; or
2. approve a separate D2.2d deletion implementation batch with the prerequisites
   above.

Until that decision is recorded, wrapper deletion remains locked.
