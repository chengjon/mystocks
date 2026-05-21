# Backend Core Validation Active Source Migration

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: D2.2a implementation batch complete; wrapper retained
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Parent readiness packet: `docs/reports/quality/backend-core-validation-wrapper-retirement-readiness-2026-05-21.md`
- Track: D2.2a active-source consumer migration
- Base HEAD: `ac6c209cc5254a4616e527d65a844f01020d6655`

## Boundary

This batch migrates active source consumers from the legacy
`app.core.validation_messages` import path to the canonical `app.core.validation`
package.

This batch does not delete `web/backend/app/core/validation_messages.py`, does
not convert compatibility tests, does not update `docs/api/`, does not create a
new Core Batch 2, and does not move any issue to `ready-for-agent`.

## Files Changed

| File | Change |
|---|---|
| `web/backend/app/core/validators.py` | Import `CommonMessages`, `MarketMessages`, and `TechnicalMessages` from `app.core.validation` |
| `web/backend/app/core/error_codes.py` | Import validation message classes from `app.core.validation` |
| `tests/unit/core/test_validation_import_boundaries.py` | Add an AST boundary test to keep active source consumers on the canonical package |
| `.planning/codebase/CODEBASE-MAP-OPENSPEC-TASK-TREE-2026-05-20.md` | Record D2.2a completion and next gate |
| `governance/mainline/task-cards/pr-99.yaml` | Scope card for this implementation batch |

## TDD Evidence

RED:

```bash
PYTHONPATH=web/backend pytest -o addopts= tests/unit/core/test_validation_import_boundaries.py -q --no-cov
```

Result: failed as expected because `validators.py` and `error_codes.py` still
imported `app.core.validation_messages`.

GREEN:

```bash
PYTHONPATH=web/backend pytest -o addopts= tests/unit/core/test_validation_import_boundaries.py -q --no-cov
```

Result: `1 passed in 0.08s`.

## Verification

| Check | Result |
|---|---|
| GitNexus impact, `web/backend/app/core/validators.py` | `LOW`, `impactedCount=0` |
| GitNexus impact, `web/backend/app/core/error_codes.py` | `MEDIUM`; direct upstream importer is `exception_handler.py`; no affected execution processes |
| Boundary test | `tests/unit/core/test_validation_import_boundaries.py`: `1 passed` |
| Compatibility test | `tests/unit/core/test_validation_messages_compat.py`: `2 passed` |
| Placeholder-env import smoke | Passed; canonical and compatibility imports resolve; source imports load |
| Active source consumer scan | `active_source_legacy_imports_excluding_wrapper=0` |
| App import smoke | `app.main` imports with `routes 548`; startup emits existing environment/library warnings unrelated to this import migration |
| Health route collection smoke | `web/backend/tests/test_health_route_conflicts.py --collect-only`: `112 tests collected` |
| Ruff touched files | `All checks passed!` |

## Consumer Scan After Migration

The legacy import scan still finds historical, documentation, test, and wrapper
references, but no active source consumer outside the wrapper itself.

Post-migration summary:

```json
{
  "active_source_legacy_imports_excluding_wrapper": 0,
  "active": []
}
```

Remaining non-active references are expected:

- `web/backend/app/core/validation_messages.py` remains the compatibility
  wrapper.
- `tests/unit/core/test_validation_messages_compat.py` intentionally verifies
  old-path compatibility while the wrapper exists.
- `docs/api/` still contains legacy import examples and should be handled in a
  later D2.2b documentation-canonicalization batch.
- historical reports remain historical evidence.

## Rollback

Rollback is limited and direct:

1. Change the two active source imports in `validators.py` and `error_codes.py`
   back to `app.core.validation_messages`.
2. Remove or update `test_validation_import_boundaries.py`.
3. Re-run the compatibility test and import smoke.

The compatibility wrapper was not changed, so runtime rollback does not require
restoring a deleted file.

## Next Gate

D2.2b should update `docs/api/` examples to canonical `app.core.validation`
imports or record explicit compatibility-doc waivers.

Wrapper deletion remains blocked until:

- active source legacy imports stay at `0`;
- docs are canonicalized or waived;
- compatibility-test conversion is explicitly approved;
- a separate wrapper-deletion approval exists.
