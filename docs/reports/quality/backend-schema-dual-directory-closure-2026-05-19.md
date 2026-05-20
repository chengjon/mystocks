# Schema Dual-Directory Closure Record

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Status: static closure draft complete; runtime route/OpenAPI refresh remains deferred.

## Current scan

| Path | Exists | Python files | Consumer signal |
|---|---|---:|---|
| `web/backend/app/schema` | Yes | 2 | `from app.schema` appears in 3 current consumers |
| `web/backend/app/schemas` | Yes | 16 | `from app.schemas` appears in 16 files / 21 total references |

`web/backend/app/schema/__init__.py` re-exports the legacy validation models, so the old directory already behaves like a compatibility shim rather than a separate contract family.

## Decision

- Canonical contract direction: `web/backend/app/schemas/`
- `web/backend/app/schema/` remains a thin compatibility re-export shim

## Migration and rollback

- New imports should move to `app.schemas`
- The legacy `schema/__init__.py` re-exports should stay until the old imports are fully drained or explicitly waived
- Rollback is to restore the import sites, not to delete the compatibility package early
- No OpenAPI side effects were measured here because runtime diff collection is still deferred until Task 1 is clean

## Verification

- `git diff --check -- docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md`
- `python scripts/compliance/markdown_governance_gate.py --root-dir . --format json docs/reports/quality/backend-schema-dual-directory-closure-2026-05-19.md`
