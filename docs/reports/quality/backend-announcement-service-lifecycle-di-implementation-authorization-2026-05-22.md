# Backend Announcement Service Lifecycle DI Implementation Authorization - 2026-05-22

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Status

- Status: implementation-authorization-prepared-for-review
- Workline: G2.5 service lifecycle DI authorization
- Candidate: `web/backend/app/services/announcement_service.py`
- Current HEAD: `f149534f8dd01802cf40cbe266223c51e4475a49`
- Prepared at: `2026-05-22T18:47:20+08:00`
- Source edits in this package: none
- Generated artifact: `.planning/codebase/generated/announcement-service-lifecycle-di-implementation-authorization-2026-05-22.json`

## Governance Boundary

This package is an authorization packet for a future implementation PR. This PR
does not modify source code or tests.

If the human maintainer accepts this packet, the future implementation may edit
only the explicitly allowed files listed below. Any broader route-contract,
OpenAPI, adapter/data-layer, schema, generated-client, PM2, or issue-label work
requires a separate packet.

This package does not authorize:

- backend source edits in this governance PR
- frontend source edits
- generated client edits
- `docs/api/` edits
- OpenSpec proposal or spec creation
- issue label changes
- moving issue `#79` or issue `#92` to `ready-for-agent`
- PM2 command execution, service restart, process deletion, or process
  recreation

## Current Issue State

| Issue | State | Labels | Role |
|---|---|---|---|
| `#79` | OPEN | `needs-triage` | Parent service lifecycle DI lane |
| `#92` | OPEN | `enhancement`, `ready-for-human`, `ready-for-downstream` | Parent downstream decision lane |

Relevant predecessor gates:

- PR `#140`: service lifecycle candidate classification accepted
- PR `#141`: `email_service.py` implementation authorization accepted
- PR `#142`: `email_service.py` lifecycle DI implementation merged
- PR `#143`: `email_service.py` closeout recorded
- PR `#144`: steward-tree retrospective and second-candidate selection merged

## Candidate Decision

`announcement_service.py` is authorized as the next implementation candidate if
this package is accepted.

It is selected over `watchlist_service.py` because current-head GitNexus
evidence keeps the impact inside one direct route owner module:

| Candidate | Getter | Risk | Direct callers | Extra impacted symbols | Disposition |
|---|---|---:|---:|---:|---|
| `announcement_service.py` | `get_announcement_service` | MEDIUM | 11 | 0 | Authorize as next candidate |
| `watchlist_service.py` | `get_watchlist_service` | MEDIUM | 9 | 6 | Defer; crosses adapter/data-layer helper surfaces |

## GitNexus Pre-Edit Snapshot

| Symbol | File | Risk | Direct callers | Processes affected | Disposition |
|---|---|---:|---:|---:|---|
| `AnnouncementService` | `web/backend/app/services/announcement_service.py` | LOW | 0 | 0 | service class candidate |
| `get_announcement_service` | `web/backend/app/services/announcement_service.py` | MEDIUM | 11 | 0 | compatibility getter and route seam |

The future implementation PR must rerun GitNexus impact before editing:

```bash
gitnexus impact --repo mystocks_spec --target AnnouncementService --direction upstream --max-depth 3
gitnexus impact --repo mystocks_spec --target get_announcement_service --direction upstream --max-depth 3
```

If either impact result changes to HIGH or CRITICAL, the implementation worker
must stop and return to review before editing source.

## Current Direct Caller Surface

All current direct route callers are in
`web/backend/app/api/announcement/routes.py`:

| Route function | Current seam |
|---|---|
| `fetch_announcements` | direct `get_announcement_service()` call |
| `get_announcements` | direct `get_announcement_service()` call |
| `get_today_announcements` | direct `get_announcement_service()` call |
| `get_important_announcements` | direct `get_announcement_service()` call |
| `get_announcement_stats` | direct `get_announcement_service()` call |
| `get_monitor_rules` | direct `get_announcement_service()` call |
| `create_monitor_rule` | direct `get_announcement_service()` call |
| `update_monitor_rule` | direct `get_announcement_service()` call |
| `delete_monitor_rule` | direct `get_announcement_service()` call |
| `get_triggered_records` | direct `get_announcement_service()` call |
| `evaluate_monitor_rules` | direct `get_announcement_service()` call |

The current service file has one module singleton:

```python
_announcement_service = None
```

The future implementation must preserve the compatibility getter. The
implementation target is route-level injection and app-state installation, not
deleting the legacy getter.

## Future Allowed Write Scope

If this authorization packet is accepted, the future implementation PR may edit:

- `web/backend/app/services/announcement_service.py`
- `web/backend/app/api/announcement/routes.py`
- `web/backend/tests/test_announcement_service_lifecycle_di.py`
- `web/backend/tests/test_announcement_routes_regressions.py`
- `docs/reports/quality/backend-announcement-service-lifecycle-di-implementation-*.md`
- `governance/mainline/task-cards/pr-*.yaml`

## Explicitly Forbidden Scope

The future implementation PR must not edit:

- `web/backend/app/services/watchlist_service.py`
- `web/backend/app/services/data_adapters/watchlist.py`
- `web/backend/app/services/adapters/watchlist_adapter.py`
- `web/backend/app/services/email_service.py`
- `web/backend/app/services/email_notification_service.py`
- `web/backend/app/services/strategy_service.py`
- `web/backend/app/services/tdx_service.py`
- `web/backend/app/services/stock_search_service/`
- `web/backend/app/api/watchlist.py`
- `docs/api/`
- generated clients
- OpenSpec proposal or spec files
- PM2 scripts or runtime process configuration
- frontend files

## Future Implementation Shape

The implementation should mirror the proven `email_service.py` pattern.

### Service Provider Pattern

Add provider helpers while keeping the compatibility getter:

```python
from typing import Any

from fastapi import Request

_announcement_service = None
ANNOUNCEMENT_SERVICE_STATE_KEY = "announcement_service"


def get_announcement_service() -> AnnouncementService:
    """Compatibility getter retained for non-route callers."""
    global _announcement_service
    if _announcement_service is None:
        _announcement_service = AnnouncementService()
    return _announcement_service


def install_announcement_service(
    app: Any, service: AnnouncementService | None = None
) -> AnnouncementService:
    selected_service = service if service is not None else get_announcement_service()
    setattr(app.state, ANNOUNCEMENT_SERVICE_STATE_KEY, selected_service)
    return selected_service


def get_announcement_service_dependency(request: Request) -> AnnouncementService:
    service = getattr(request.app.state, ANNOUNCEMENT_SERVICE_STATE_KEY, None)
    if service is None:
        service = install_announcement_service(request.app)
    return service
```

The implementation worker must confirm the file already has or receives the
imports required for `Any` and `Request`.

### Route Injection Pattern

Each route function that currently calls `get_announcement_service()` should
accept the injected service:

```python
from fastapi import APIRouter, Body, Depends, Path, Query

from app.services.announcement_service import (
    AnnouncementService,
    get_announcement_service_dependency,
)


async def fetch_announcements(
    service: AnnouncementService = Depends(get_announcement_service_dependency),
):
    ...
```

Then remove the local line:

```python
service = get_announcement_service()
```

from each converted route function.

The existing fallback import behavior around `HAS_ANNOUNCEMENT_SERVICE` must be
preserved unless the worker first creates a separate decision packet to change
that compatibility behavior.

## Future Test Plan

### New lifecycle DI test file

Create `web/backend/tests/test_announcement_service_lifecycle_di.py`.

Required checks:

- `install_announcement_service(app, fake_service)` writes to `app.state`
- `get_announcement_service_dependency(request)` reuses an existing app-state
  service
- `get_announcement_service_dependency(request)` installs a service when app
  state is empty
- every converted announcement route has a `service` parameter
- `fetch_announcements` can use an injected fake service without calling the
  module-level getter

### Existing route regression test

Extend `web/backend/tests/test_announcement_routes_regressions.py` only if the
implementation changes route import or load behavior. Keep the existing
`analyze_data` rule-based response test passing.

## Future Verification Commands

The implementation PR must run:

```bash
env PYTHONPATH=web/backend pytest -q -n 0 --tb=short --no-cov \
  web/backend/tests/test_announcement_service_lifecycle_di.py \
  web/backend/tests/test_announcement_routes_regressions.py
```

```bash
ruff check \
  web/backend/app/services/announcement_service.py \
  web/backend/app/api/announcement/routes.py \
  web/backend/tests/test_announcement_service_lifecycle_di.py \
  web/backend/tests/test_announcement_routes_regressions.py
```

```bash
env PYTHONPATH=web/backend python - <<'PY'
from app.services.announcement_service import (
    AnnouncementService,
    get_announcement_service,
    get_announcement_service_dependency,
    install_announcement_service,
)
from app.api.announcement import routes

print("announcement service DI import smoke passed")
PY
```

After staging the implementation files, run:

```bash
gitnexus detect-changes --repo mystocks_spec --scope staged
```

The implementation report must record the exact command outputs. Full backend
pytest, PM2, OpenAPI drift, frontend E2E, and generated-client checks are not
required for this narrow authorization unless the implementation changes their
surfaces.

## Rollback Plan

If the future implementation fails tests or review:

1. Revert the implementation PR.
2. Restore route functions to direct `get_announcement_service()` calls.
3. Remove the new announcement lifecycle DI test file.
4. Leave the G2.5 authorization packet as historical evidence and mark the
   implementation attempt as reverted in the steward tree.

## Next Gate

Human review of this G2.5 authorization packet.

If accepted, create a separate implementation worktree and PR. That future PR
may edit only the allowed write scope above and must produce an implementation
report before closeout.
