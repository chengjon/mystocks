# Decision Record: P3-A1 Announcement Canonical Route

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> **Date**: 2026-05-18
> **Status**: Proposed
> **Deciders**: Pending review

## Context

The announcement domain has three route sources producing potential URL conflicts:

1. **Flat file** `app/api/announcement.py` — defines 11 routes with `APIRouter()` (no prefix)
2. **Package** `app/api/announcement/routes.py` — defines 14 routes with `APIRouter(prefix="/announcement")`
3. **Dual registration** in `router_registry.py`:
   - Line 83: `router_modules["announcement"]` registered via VERSION_MAPPING at prefix `/api/v1/announcement`
   - Line 96: `announcement.router` registered at prefix `/api` with tags `["announcement"]`

Since `from .api import announcement` resolves to the **package** (not the flat file), both registrations target `announcement/routes.py`'s router. The flat file is unreachable via normal import.

## Current Facts

| Fact | Value | Source |
|------|-------|--------|
| Flat file routes | 11 decorators | AST scan `announcement.py` |
| Package routes | 14 decorators | AST scan `announcement/routes.py` |
| Full-path from registry line 96 | `/api/announcement/{local_path}` | `/api` + `/announcement` + local |
| Full-path from VERSION_MAPPING (line 83) | `/api/v1/announcement/announcement/{local_path}` | `/api/v1/announcement` + `/announcement` + local (DOUBLE PREFIX BUG) |
| Flat file registration | None (orphan) | Not in `router_registry.py` |
| Frontend consumers | All use `/api/announcement/*` | `useAnnouncementMonitor.ts` |
| Test consumers | All use `/api/announcement/*` | `test_announcement_api.py`, e2e tests |
| `/api/v1/announcement` consumers | None found | `versionNegotiationPolicy.ts` declares version but no direct calls |
| Local decorator duplicates | 11 (flat vs package same local paths) | Baseline §2.1 |
| Full-path conflicts | **0** (flat file is orphan; package registered at different prefixes) | P3-0.5 output |

## Options Considered

### Option A: Keep package as canonical, delete flat file, remove VERSION_MAPPING entry

- **Result**: Single router at `/api/announcement/*`. Remove VERSION_MAPPING `"announcement"` key to eliminate the double-prefix bug at `/api/v1/announcement/announcement/*`.
- **Pros**: Cleanest outcome. One source of truth. No compat burden.
- **Cons**: None — `/api/v1/announcement` has zero consumers.

### Option B: Keep both, add compat alias

- **Result**: Package at `/api/announcement/*`, flat file at `/api/announcement-legacy/*`, VERSION_MAPPING alias at `/api/v1/announcement/*`.
- **Pros**: Maximum backward compatibility.
- **Cons**: Unnecessary complexity. No evidence of `/api/v1/announcement` usage. Adds three registrations for one domain.

### Option C: Migrate flat file routes into package, keep VERSION_MAPPING

- **Result**: All 11 flat routes merged into package. VERSION_MAPPING kept for v1 alias.
- **Cons**: Same double-prefix bug remains. More work for no additional benefit.

## Decision

**Option A**: Package `announcement/routes.py` is the canonical router. Flat file `announcement.py` is dead code and should be deleted. VERSION_MAPPING `"announcement"` entry should be removed to eliminate the double-prefix registration bug.

### Compatibility Policy

- **Canonical URL**: `/api/announcement/*` (current working path)
- **Deprecated alias**: `/api/v1/announcement/*` — never had consumers; remove immediately
- **Flat file**: `announcement.py` — orphan (not registered); remove after verification

### Rollback

If `/api/v1/announcement` consumers are discovered after removal, add a one-line `include_router` with prefix `/api/v1/announcement` pointing to the same package router (without the `/announcement` sub-prefix).

## OpenSpec

- **required**: no — this is a dead-code cleanup with zero consumer impact
- **reason**: No API contract change. The canonical URL `/api/announcement/*` is unchanged. Only unreachable routes are removed.

## Follow-up Issues Unlocked

- [ ] P3-B1: Delete `app/api/announcement.py` (flat file)
- [ ] Remove `"announcement"` key from `VERSION_MAPPING`
- [ ] Update `router_registry.py` to remove announcement from `router_modules` dict
- [ ] Verify no `/api/v1/announcement` references in test suites
- [ ] Update route table baseline numbers

## Verification

```bash
# 1. Verify flat file has no import references
grep -r "from.*api.*import.*announcement\b" web/backend/ --include="*.py" | grep -v "__pycache__" | grep -v "announcement/"
grep -r "announcement\.py" web/backend/ --include="*.py" | grep -v "__pycache__"

# 2. Verify no /api/v1/announcement consumers
grep -r "v1/announcement" web/frontend/src/ web/backend/tests/ tests/ --include="*.ts" --include="*.py" | grep -v "versionNegotiationPolicy"

# 3. After fix, regenerate baseline
cd web/backend && python3 ../../scripts/dev/backend_audit_baseline.py /opt/claude/mystocks_spec/docs/reports/quality/generated
cd web/backend && python3 ../../scripts/dev/backend_audit_fullpath_routes.py /opt/claude/mystocks_spec/docs/reports/quality/generated
```
