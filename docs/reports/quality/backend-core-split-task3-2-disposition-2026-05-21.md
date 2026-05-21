# Backend Core Split Task 3.2 Disposition

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-21

Status: review-ready; task disposition only; no backend implementation changes.

OpenSpec change:
`split-backend-core-modules-with-compatibility-wrappers`

Current evidence HEAD:

- Branch: `post-issue83-acceptance-3-2`
- Base: `origin/wip/root-dirty-20260403`
- HEAD before this report: `7b4abd2a60691cbfb82870cfcf8d6f7b4fbff7a3`
- Base subject: `Merge pull request #88 from chengjon/post-pr87-steward-closeout`

## Human Gate

The human maintainer accepted issue `#83` shared C/E/F evidence in the current
review thread.

Accepted evidence package:

- `docs/reports/quality/backend-openspec-issue83-shared-evidence-package-2026-05-21.md`
- GitHub issue comment:
  `https://github.com/chengjon/mystocks/issues/83#issuecomment-4502586566`

## Task 3.2 Disposition

Task:

```text
3.2 Introduce same-name packages with `__init__.py` re-exports.
```

Disposition: mark complete for the current Core split change.

Rationale:

- `app.core.validation` now resolves to a package:
  `web/backend/app/core/validation/__init__.py`.
- That package re-exports the validation-message helper symbols from
  `app.core.validation.messages`.
- The legacy `app.core.validation_messages` path remains as a compatibility
  wrapper and exports the same symbols.
- Current runtime-code references do not depend on the old `validation.py`
  module through `app.core.validation`; active references are the compatibility
  test and legacy `validation_messages` imports.

This closes the ambiguity around task `3.2`; it does not authorize another Core
helper implementation batch.

## Verification

Import smoke:

```text
app.core.validation_origin=/opt/claude/mystocks_spec/.worktrees/post-issue83-acceptance-3-2/web/backend/app/core/validation/__init__.py
app.core.validation_is_package=True
validation_py_exists=True
CommonMessages_pkg_messages=True
CommonMessages_legacy_messages=True
MarketMessages_pkg_messages=True
MarketMessages_legacy_messages=True
TechnicalMessages_pkg_messages=True
TechnicalMessages_legacy_messages=True
TradeMessages_pkg_messages=True
TradeMessages_legacy_messages=True
ErrorMessages_pkg_messages=True
ErrorMessages_legacy_messages=True
ValidationErrorBuilder_pkg_messages=True
ValidationErrorBuilder_legacy_messages=True
```

Runtime-code reference scan:

```text
match_count=10
runtime code refs:
- web/backend/app/core/validators.py: from app.core.validation_messages import ...
- web/backend/app/core/error_codes.py: from app.core.validation_messages import ...
test refs:
- tests/unit/core/test_validation_messages_compat.py imports package, canonical, and legacy paths
wrapper refs:
- web/backend/app/core/validation_messages.py documents the canonical path and wrapper
```

Targeted test:

```text
env PYTHONPATH=web/backend pytest tests/unit/core/test_validation_messages_compat.py -q -n 0 --tb=short --no-cov
2 passed
```

## Boundary

This disposition means the current OpenSpec task checklist can become complete.
It does not mean:

- Core helper Batch 2 may start automatically;
- broad Core module movement is approved;
- `validation.py` may be deleted;
- compatibility wrappers may be retired;
- issue15 may be converted into implementation authorization.

Any further Core split implementation needs a separate concrete plan, current
impact analysis, compatibility tests, and explicit approval.
