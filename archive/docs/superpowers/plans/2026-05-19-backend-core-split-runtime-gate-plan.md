# Backend Core Split Runtime Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Close the remaining runtime verification gates for `split-backend-core-modules-with-compatibility-wrappers` without reopening the completed validation messages split batch.

**Architecture:** Treat the validation messages split as a closed helper batch and keep subsequent PM2, health, contract, and OpenAPI validation as a separate runtime evidence lane. Do not mix publication/governance artifacts, Core helper files, and runtime startup fixes in one commit.

**Tech Stack:** FastAPI, PM2, OpenSpec, PostgreSQL/TimescaleDB, TDengine, Redis, Python pytest, FastAPI OpenAPI generation.

---

## Boundary

- The completed Core helper split remains anchored at commit `caa5a6bd6339d2dea6ed5d55a3be28dae40c64fe`.
- The startup/import unblock commits already pushed in this line are `71d29d3b7` and `2d6682e81`.
- The dirty root checkout must not be fast-forwarded, merged, rebased, or reset for this work.
- Continue implementation or runtime verification only in a clean worktree or already-isolated worktree.
- Do not persist database passwords or monitoring credentials into tracked files.
- Do not mark OpenSpec tasks `4.3`, `4.4`, or `4.5` complete unless fresh runtime evidence exists.

## Task 1: Runtime Environment Preflight

**Files:**
- Read: `docs/reports/quality/backend-core-split-other-line-next-work-boundary-2026-05-19.md`
- Read: `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md`
- No source file modification expected.

- [ ] **Step 1: Confirm branch and commit baseline**

Run:

```bash
git status --short
git log -1 --oneline --decorate
git ls-remote origin refs/heads/wip/root-dirty-20260403
```

Expected:

```text
The root checkout may remain dirty.
Runtime verification must run in a clean worktree or the isolated implementation worktree.
Do not stage unrelated governance or publication artifacts.
```

- [ ] **Step 2: Confirm app import smoke still passes**

Run from the implementation worktree with the session-provided runtime DB environment exported only in the shell:

```bash
PYTHONPATH=web/backend:<worktree-root> \
BACKEND_PORT=8020 \
BACKEND_BACKUP_PORT=8021 \
FRONTEND_PORT=3020 \
FRONTEND_BACKUP_PORT=3021 \
POSTGRESQL_HOST=<provided-runtime-db-host> \
POSTGRESQL_PORT=<provided-runtime-db-port> \
POSTGRESQL_USER=<provided-runtime-db-user> \
POSTGRESQL_PASSWORD=<provided-runtime-db-password> \
POSTGRESQL_DATABASE=<provided-runtime-db-name> \
JWT_SECRET_KEY=<local-runtime-secret> \
python -c "import app.main; print('app-main-import-ok')"
```

Expected:

```text
app-main-import-ok
```

If this fails with an import error, stop and classify the blocker as a runtime startup/API import lane issue, not a Core validation messages split issue.

## Task 2: PM2 Backend Startup Gate

**Files:**
- Read: `ecosystem.test.config.js`
- No source file modification expected unless PM2 exposes a new concrete import/runtime bug.

- [ ] **Step 1: Ensure no stale PM2 process is running**

Run:

```bash
pm2 delete all
pm2 list
```

Expected:

```text
No active mystocks-backend process remains before the fresh run.
```

- [ ] **Step 2: Start backend with session-provided runtime DB environment**

Run from the implementation worktree:

```bash
BACKEND_PORT=8020 \
BACKEND_BACKUP_PORT=8021 \
FRONTEND_PORT=3020 \
FRONTEND_BACKUP_PORT=3021 \
POSTGRESQL_HOST=<provided-runtime-db-host> \
POSTGRESQL_PORT=<provided-runtime-db-port> \
POSTGRESQL_USER=<provided-runtime-db-user> \
POSTGRESQL_PASSWORD=<provided-runtime-db-password> \
POSTGRESQL_DATABASE=<provided-runtime-db-name> \
MONITOR_DB_HOST=<provided-monitor-db-host> \
MONITOR_DB_PORT=<provided-monitor-db-port> \
MONITOR_DB_USER=<provided-monitor-db-user> \
MONITOR_DB_PASSWORD=<provided-monitor-db-password> \
JWT_SECRET_KEY=<local-runtime-secret> \
pm2 start ecosystem.test.config.js --only mystocks-backend --update-env
```

Expected:

```text
mystocks-backend remains online after at least 15 seconds.
```

- [ ] **Step 3: Check PM2 stability**

Run:

```bash
sleep 15
pm2 list
pm2 logs mystocks-backend --lines 80 --nostream
```

Expected:

```text
mystocks-backend status is online.
No repeating import error or DB connection refused error appears in the latest log window.
```

If PM2 still fails, record the exact topmost application error and keep OpenSpec task `4.3` open.

## Task 3: Health Endpoint Smoke

**Files:**
- No source file modification expected.

- [ ] **Step 1: Smoke the required readiness endpoints**

Run:

```bash
python - <<'PY'
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

paths = [
    "http://localhost:8020/api/health/services",
    "http://localhost:8020/health/ready",
    "http://localhost:8020/api/health/ready",
]

for url in paths:
    try:
        with urlopen(url, timeout=10) as response:
            print(f"{url} {response.status}")
    except HTTPError as exc:
        print(f"{url} HTTP_ERROR {exc.code}")
    except URLError as exc:
        print(f"{url} URL_ERROR {exc.reason}")
PY
```

Expected:

```text
Each endpoint returns an explicit HTTP status.
OpenSpec task 4.4 can be marked done only if the observed statuses match the accepted readiness contract.
```

If DB/Redis/TDengine readiness returns degraded status, keep `4.4` open or document it as environment-blocked rather than complete.

## Task 4: Route And OpenAPI Drift Check

**Files:**
- Read or generate route/OpenAPI evidence only after PM2 startup is stable.
- Do not commit generated evidence unless the implementation issue explicitly requires it.

- [ ] **Step 1: Generate OpenAPI in-process**

Run:

```bash
PYTHONPATH=web/backend:<worktree-root> \
BACKEND_PORT=8020 \
BACKEND_BACKUP_PORT=8021 \
FRONTEND_PORT=3020 \
FRONTEND_BACKUP_PORT=3021 \
POSTGRESQL_HOST=<provided-runtime-db-host> \
POSTGRESQL_PORT=<provided-runtime-db-port> \
POSTGRESQL_USER=<provided-runtime-db-user> \
POSTGRESQL_PASSWORD=<provided-runtime-db-password> \
POSTGRESQL_DATABASE=<provided-runtime-db-name> \
JWT_SECRET_KEY=<local-runtime-secret> \
python - <<'PY'
from app.main import app
schema = app.openapi()
print(f"paths={len(schema.get('paths', {}))}")
PY
```

Expected:

```text
OpenAPI schema generation completes.
Record the path count as a timestamped observation, not as a permanent baseline unless separately approved.
```

- [ ] **Step 2: Run duplicate operationId smoke if available**

Run the repo's current OpenAPI/route drift command or named equivalent used by the active implementation issue.

Expected:

```text
No unintended route/OpenAPI drift attributable to the Core helper split or startup import fixes.
```

Task `4.5` remains open if generation fails, duplicate operation IDs appear, or route deltas cannot be attributed.

## Task 5: OpenSpec Task Reconciliation

**Files:**
- Modify only if evidence is fresh and complete: `openspec/changes/split-backend-core-modules-with-compatibility-wrappers/tasks.md`
- Optional evidence report path if needed: `docs/reports/quality/backend-core-split-runtime-gates-2026-05-19.md`

- [ ] **Step 1: Update only evidence-backed checkboxes**

Rules:

```text
Mark 4.3 done only after stable PM2 backend startup.
Mark 4.4 done only after accepted health/readiness smoke.
Mark 4.5 done only after route/OpenAPI drift check completes.
Do not mark tasks done using import smoke, unit tests, or expected behavior.
```

- [ ] **Step 2: Leave the next Core split blocked until reconciliation is complete**

Expected:

```text
Do not start another Core split batch until 4.3/4.4/4.5 are either closed with evidence or explicitly documented as externally blocked.
```

## Task 6: Cleanup

**Files:**
- No source file modification expected.

- [ ] **Step 1: Stop PM2 test process unless the user explicitly wants it left running**

Run:

```bash
pm2 delete all
pm2 list
```

Expected:

```text
No local PM2 restart loop remains.
```

- [ ] **Step 2: Report exact residual risks**

Report:

```text
Commands run
Pass/fail counts
PM2 backend state
Health endpoint statuses
OpenAPI path count or failure reason
Whether OpenSpec tasks changed
Whether any source code changed
```
