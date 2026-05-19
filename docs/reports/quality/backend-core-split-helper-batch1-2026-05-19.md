# Backend Core Split Helper Batch 1

> **历史文档说明**:
> 本文件记录 2026-05-19 的 Core helper 拆分首批本地验证结果，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、`openspec/AGENTS.md`、当前代码与最近一次实际验证结果为准。

## Scope

OpenSpec change: `split-backend-core-modules-with-compatibility-wrappers`

This batch implements the first low-risk helper move:

- canonical path: `app.core.validation.messages`
- compatibility wrapper: `app.core.validation_messages`
- package re-export path: `app.core.validation`

No database, security, socketio, cache, logger, router, or OpenAPI contract code was intentionally changed.

## Changed Paths

| Path | Action |
|---|---|
| `web/backend/app/core/validation/messages.py` | moved implementation from `validation_messages.py` |
| `web/backend/app/core/validation/__init__.py` | added canonical package re-exports |
| `web/backend/app/core/validation_messages.py` | added old-path compatibility wrapper |
| `tests/unit/core/test_validation_messages_compat.py` | added compatibility and canonical import tests |

## Compatibility Contract

The following imports must continue to work:

```python
from app.core.validation_messages import CommonMessages
from app.core.validation.messages import CommonMessages
from app.core.validation import ValidationErrorBuilder
```

The legacy wrapper is intentionally retained. It should not be retired until all old-path imports are migrated and the rollback criteria in the OpenSpec change remain satisfied.

## Verification

| Check | Result |
|---|---|
| GitNexus impact for `CommonMessages` | `LOW`, impacted count `0` |
| GitNexus impact for `MarketMessages` | `LOW`, impacted count `0` |
| GitNexus impact for `TechnicalMessages` | `LOW`, impacted count `0` |
| GitNexus impact for `TradeMessages` | `LOW`, impacted count `0` |
| GitNexus impact for `ErrorMessages` | `LOW`, impacted count `0` |
| GitNexus impact for `ValidationErrorBuilder` | `LOW`, impacted count `0` |
| Import smoke | passed |
| `pytest tests/unit/core/test_validation_messages_compat.py -q -n 0 --tb=short --no-cov` | `2 passed` |
| `python -m py_compile ...` for moved/wrapper/dependent modules | passed |
| `ruff check ...` for moved/wrapper/test files | passed |

Import smoke command:

```bash
env PYTHONPATH=web/backend python -c "from app.core.validation_messages import CommonMessages as Old; from app.core.validation.messages import CommonMessages as New; from app.core.validation import ValidationErrorBuilder; assert Old is New; assert ValidationErrorBuilder.build_symbol_error('600519', 'empty')['field'] == 'symbol'; import app.core.error_codes; import app.core.validators"
```

## Runtime Gate Status

PM2 / health verification was attempted but is blocked by a pre-existing remote-head startup issue outside this batch:

```text
ImportError: cannot import name 'ContractDriftIncidentListResponse' from 'app.api.contract.schemas'
```

The failing chain is:

```text
app.main -> app.router_registry -> app.api.contract -> app.api.contract.routes -> app.api.contract.schemas
```

This batch did not modify `app.api.contract`, `router_registry`, or any route registration file. Therefore `4.3`, `4.4`, and `4.5` remain open in the OpenSpec task list.

## Wrapper Retirement Candidate

Wrapper:

- `web/backend/app/core/validation_messages.py`

Retirement criteria:

- old-path imports of `app.core.validation_messages` are migrated or intentionally waived;
- import smoke passes for canonical package imports;
- runtime smoke passes after the unrelated contract startup blocker is resolved;
- rollback path remains documented and tested.

Until those criteria are met, the wrapper must remain.

