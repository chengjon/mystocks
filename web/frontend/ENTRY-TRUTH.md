# Frontend Entry Point Truth Source

**Created:** 2026-04-07
**Phase:** 03-structural-consolidation (Plan 03-01, Task 1)

## Canonical Entry

**`main-standard.ts`** — loaded by `index.html` line 67:
```html
<script type="module" src="/src/main-standard.ts"></script>
```

`main-standard.ts` creates the Vue app with: createApp, createPinia, router, App.vue, and core style imports.

## Tooling Consumer

**`verify-mount.js`** reads `src/main.js` via `fs.readFileSync` to validate `app.mount` is present.
- This is a Node.js validation script, NOT a runtime import.
- `main.js` must be preserved until `verify-mount.js` is updated or confirmed obsolete.

## Main Variant Inventory (8 total)

| # | File | Consumers | Safe to Archive? |
|---|------|-----------|-----------------|
| 1 | `main-standard.ts` | index.html (canonical entry) | NO |
| 2 | `main.js` | verify-mount.js (tooling read) | NO |
| 3 | `main-debug.js` | 0 | YES |
| 4 | `main-original.js` | 0 | YES |
| 5 | `main-simplified.js` | 0 | YES |
| 6 | `main-test.js` | 0 | YES |
| 7 | `main-enhanced.ts` | 0 | YES |
| 8 | `main-minimal.ts` | 0 | YES |

## Key Difference: main-standard.ts vs main.js

`main-standard.ts` is a **minimal entry** — createApp + Pinia + router + styles. No security, no PWA, no session restore.

`main.js` is the **full entry** — includes Element Plus icons, CSRF/security init, PWA service worker, API version negotiation, session restore, global error handler, and Bloomberg style overrides.

Both mount to `#app`. Only `main-standard.ts` is loaded by index.html.

## Backup Files

- `App.vue.backup` — stale backup, audit consumers before deletion
- `main.js.backup` — stale backup, audit consumers before deletion

## Decision

- Keep `main-standard.ts` (canonical entry, loaded by index.html)
- Keep `main.js` (verify-mount.js consumer)
- Archive 6 zero-consumer variants to `_entry-archive/`
