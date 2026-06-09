# HTML5 Migration Background Sync Audit

Date: 2026-05-12
Change: `implement-html5-migration-experience-optimization`
Task focus: `2.2.4 Implement background sync for failed requests`
Scope: Desktop-only, repo-local audit only

## Decision

`2.2.4` remains open.

This batch records the current background-sync surface. The service worker already defines sync handlers and a queue, but the repo does not yet show a verified client-side registration path or an end-to-end failed-request requeue flow.

## Evidence Checked

Commands:

```bash
rg -n "sync|BackgroundSync|registration\\.sync|SyncManager|failed request|queue|retry|offline|fetch" web/frontend/public/sw.js web/frontend/src web/frontend/tests
sed -n '300,470p' web/frontend/public/sw.js
```

Observed repo facts:

- `web/frontend/public/sw.js` listens for `sync` events and dispatches `background-sync`, `market-data-sync`, and `user-preferences-sync`.
- The service worker defines a `BackgroundSyncQueue` class with retry and exponential backoff behavior.
- `syncQueue.processQueue()` can retry queued requests and requeue failed items.
- The audit did not find a front-end `registration.sync.register(...)` call or a clear client-side path that pushes failed requests into this queue.

## Gap Summary

The repo has service-worker-side background sync machinery, but it does not yet demonstrate an end-to-end browser registration and enqueue flow for failed requests.

That means the presence of the queue and sync handlers is still only half of the capability. The client-side half and the operational proof remain missing.

## Task Disposition

Keep `2.2.4` unchecked until a later approved batch verifies the browser registration and failed-request enqueue path.

Minimum future evidence should include:

- A verified `registration.sync.register(...)` or approved equivalent client registration path.
- A reproducible failed-request enqueue flow.
- An acceptance path that proves a queued request can be retried successfully by the service worker.
