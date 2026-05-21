# Backend Core Validation Wrapper Retirement Readiness

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以
> `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、
> 当前代码与最近一次实际验证结果为准。

- Date: 2026-05-21
- Status: readiness packet prepared; wrapper retirement not authorized
- Parent issue: <https://github.com/chengjon/mystocks/issues/92>
- Parent split acceptance: `docs/reports/quality/backend-openspec-issue92-downstream-split-acceptance-2026-05-21.md`
- Track: D2.2 `decide-backend-core-validation-wrapper-retirement`
- Base HEAD: `458acb27888bfca6a024a03d778ae73061b02898`

## Boundary

This is a readiness packet only. It does not authorize deleting
`web/backend/app/core/validation_messages.py`, editing active imports, changing
tests, moving Core files, creating a new Core Batch 2, or moving any issue to
`ready-for-agent`.

The compatibility wrapper must remain until a separate implementation issue or
OpenSpec branch is explicitly approved and its gates pass.

## Current State

| Item | State |
|---|---|
| Canonical implementation | `web/backend/app/core/validation/messages.py` exists |
| Canonical package re-export | `web/backend/app/core/validation/__init__.py` exists |
| Legacy compatibility wrapper | `web/backend/app/core/validation_messages.py` exists |
| Compatibility test | `tests/unit/core/test_validation_messages_compat.py` exists and passes |
| Validation helper split commit | `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe` was previously recorded as reachable |
| GitNexus impact for `ValidationErrorBuilder` | `LOW`; `impactedCount=0`; `processes_affected=0` |

## Consumer Scan

Scan command:

```bash
rg -n "app\.core\.validation_messages|core\.validation_messages" web/backend tests docs/api docs/reports/quality
```

Classified results at this readiness review:

| Category | Count | Disposition |
|---|---:|---|
| Active source references, including the wrapper docstring | 3 | Not ready for wrapper deletion |
| Active source references, excluding the wrapper itself | 2 | Must migrate before retirement |
| Compatibility test references | 2 | Intentional while wrapper exists |
| API documentation examples | 6 | Must update or explicitly waive before retirement |
| Quality report historical references | 10 | Historical evidence; not a blocker |

Active source references that block deletion:

- `web/backend/app/core/validators.py:11`
- `web/backend/app/core/error_codes.py:11`

Documentation examples that should be updated before final retirement:

- `docs/api/VALIDATION_GUIDE.md`
- `docs/api/EXCEPTION_HANDLER_GUIDE.md`
- `docs/api/ERROR_CODE_GUIDE.md`

## Verification Evidence

| Check | Result |
|---|---|
| Compatibility test | `PYTHONPATH=web/backend pytest -o addopts= tests/unit/core/test_validation_messages_compat.py -q --no-cov` passed: `2 passed in 0.08s` |
| Import smoke without required env | Blocked by expected configuration validation: missing `POSTGRESQL_HOST`, `POSTGRESQL_USER`, `POSTGRESQL_PASSWORD`, `JWT_SECRET_KEY`, `BACKEND_PORT`, `BACKEND_BACKUP_PORT` |
| Import smoke with placeholder required env | Passed; canonical exports resolve and legacy wrapper symbols are identical to canonical symbols |

Placeholder-env import smoke:

```bash
POSTGRESQL_HOST=localhost \
POSTGRESQL_USER=placeholder \
POSTGRESQL_PASSWORD=placeholder \
JWT_SECRET_KEY=placeholder-placeholder-placeholder-placeholder \
BACKEND_PORT=8888 \
BACKEND_BACKUP_PORT=8889 \
PYTHONPATH=web/backend \
python -c "from app.core.logger import logger; from app.core.validation import CommonMessages; from app.core.validation_messages import CommonMessages as CompatCommonMessages; print(logger is not None, CommonMessages is CompatCommonMessages)"
```

Observed output:

```text
logger True
canonical CommonMessages MarketMessages TechnicalMessages TradeMessages ErrorMessages ValidationErrorBuilder
compat_identity True True True True True True
```

## Readiness Decision

`app.core.validation_messages` is **not ready for deletion** at this point.

Reason:

- active source imports remain in `validators.py` and `error_codes.py`;
- public API documentation still teaches the legacy import path;
- the compatibility test still intentionally asserts the old path;
- no implementation issue has approved source edits or wrapper deletion.

## Proposed Retirement Sequence

1. D2.2a: migrate active source consumers from
   `app.core.validation_messages` to `app.core.validation`.
2. D2.2b: update `docs/api/` examples to canonical import paths or record a
   deliberate compatibility-doc waiver.
3. D2.2c: keep `tests/unit/core/test_validation_messages_compat.py` while the
   wrapper exists; replace it only when wrapper deletion is explicitly approved.
4. D2.2d: rerun consumer scan and require zero active source legacy imports
   before wrapper deletion is considered.
5. D2.2e: create a separate wrapper-deletion approval only after all previous
   gates pass.

## Future Implementation Gate

Any future implementation issue for D2.2 must include:

| Gate | Required command or evidence |
|---|---|
| Pre-edit GitNexus | `impact(target="ValidationErrorBuilder", direction="upstream")`; if editing source consumers, also analyze the edited symbols/files |
| Consumer scan before edit | `rg -n "app\.core\.validation_messages|core\.validation_messages" web/backend tests docs/api` |
| Active source migration check | active source legacy imports excluding the wrapper itself must reach `0` before deletion |
| Import smoke | logger-inclusive import smoke with required placeholder env |
| Compatibility test | `PYTHONPATH=web/backend pytest -o addopts= tests/unit/core/test_validation_messages_compat.py -q --no-cov` while wrapper exists |
| Lint touched files | `ruff check` for touched source, docs helper scripts if any, and tests |
| Staged scope | `detect_changes(scope="staged")` after staging only the intended batch |

## Rollback

Rollback for a future source-consumer migration:

1. Revert source consumer imports back to `app.core.validation_messages`.
2. Keep `web/backend/app/core/validation_messages.py` in place.
3. Re-run compatibility import smoke and `test_validation_messages_compat.py`.

Rollback for a future wrapper deletion, if separately approved later:

1. Restore `web/backend/app/core/validation_messages.py` from the prior commit.
2. Restore compatibility tests.
3. Re-run canonical and compatibility import smoke.

## Next Gate

Human review of this readiness packet.

If accepted, create a separate implementation issue or OpenSpec branch for
D2.2a active source consumer migration only. Do not combine source migration,
documentation update, test conversion, and wrapper deletion into one unreviewed
batch.

