# Backend Core Validation Docs API Canonicalization

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: D2.2b documentation batch complete; wrapper retained
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Parent readiness packet: `docs/reports/quality/backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`
- Prior implementation packet: `docs/reports/quality/backend-core-validation-active-source-migration-2026-05-21.md`
- Track: D2.2b docs/API examples canonicalization
- Base HEAD: `c54c17e30e0ac25b71ca4358d2816d6f0a9fc78f`

## Boundary

This batch canonicalizes documentation examples under `docs/api/` from the
legacy `app.core.validation_messages` import path to the canonical
`app.core.validation` package.

This batch does not delete `web/backend/app/core/validation_messages.py`, does
not modify backend source, does not modify tests, does not modify OpenSpec
change files, does not run or change PM2 behavior, and does not move any issue
to `ready-for-agent`.

## Files Changed

| File | Change |
|---|---|
| `docs/api/VALIDATION_GUIDE.md` | Update module overview and import examples to `app.core.validation` |
| `docs/api/ERROR_CODE_GUIDE.md` | Update integration wording and import examples to `app.core.validation` |
| `docs/api/EXCEPTION_HANDLER_GUIDE.md` | Update example import to `app.core.validation` |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record D2.2b completion and next gate |
| `governance/mainline/task-cards/pr-100.yaml` | Scope card for this docs-only batch |

## Evidence

| Check | Result |
|---|---|
| Pre-change docs/API scan | `10` legacy `validation_messages` references in `docs/api/` |
| Post-change docs/API scan | `docs_api_legacy_reference_count=0` |
| Source boundary | No `web/backend/app/**` files are modified in this batch |
| Wrapper boundary | `web/backend/app/core/validation_messages.py` remains unchanged and retained |

## Closure Statement

D2.2b closes the docs/API example portion of the validation wrapper retirement
readiness track. It does not authorize wrapper deletion.

The remaining retirement question is a separate D2.2c decision: either keep the
compatibility wrapper intentionally, or approve a wrapper deletion batch with
explicit compatibility-test and consumer-retirement handling.
