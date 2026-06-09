# Frontend View Governance Mutation Batch A2 Error Shell Plan

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: proposed A2 mutation batch for `openspec/changes/update-frontend-view-governance`.

This plan does not move files, edit routes, edit tests, or change runtime code.

## Candidate Set

| File | Current route owner | Current menu owner | Guard status | Initial lifecycle |
| --- | --- | --- | --- | --- |
| `web/frontend/src/views/errors/Forbidden.vue` | none found | none found | direct style-source spec | `candidate-review/demo-error-shell` |
| `web/frontend/src/views/errors/NetworkError.vue` | none found | none found | direct style-source spec | `candidate-review/demo-error-shell` |
| `web/frontend/src/views/errors/ServiceUnavailable.vue` | none found | none found | indirect style asset spec | `candidate-review/demo-error-shell` |
| `web/frontend/src/views/errors/styles/ServiceUnavailable.scss` | n/a | n/a | direct style-source spec | `candidate-support-asset` |

## Current Evidence

- `router/index.ts` owns `/login` via `Login.vue` and catch-all 404 via `NotFound.vue`.
- `router/index.ts` does not import `@/views/errors/*`.
- `MenuConfig.ts` does not include `/login`, 404, or `views/errors/*`; this is expected for blank-layout and special routes.
- `web/frontend/package.json` still includes `--target-dir src/views/errors --changed-from-git` in `lint:artdeco:changed`.
- `web/frontend/tests/unit/config/errors-mainline-gate.spec.ts` requires directory-level ArtDeco coverage for `src/views/errors`.
- `errors-forbidden-style-source.spec.ts`, `errors-network-style-source.spec.ts`, and `errors-service-unavailable-style-source.spec.ts` directly guard these demo error assets.

## Decision Options

| Option | Work | Pros | Risks |
| --- | --- | --- | --- |
| A2-retain | Promote error pages into formal error route/error-state contract, then fix stale route links and health probes | Preserves potentially useful 403/network/503 UX | Expands scope into routing, auth, health endpoint truth, and blank-layout behavior |
| A2-archive | Retire `errors-*` guard specs and package directory guard, then move demo error shells into governed archive | Small cleanup; aligns with current no-route truth | Removes demo assets from active source tree; requires explicit no-successor rationale |
| A2-defer | Keep files and guards unchanged | Lowest immediate risk | Leaves guarded dead-route assets in active `views/` tree |

Recommended next profile: `A2-archive-prep`.

Reason: current evidence shows no active route/menu/runtime owner, while the direct blockers are tests and package guard coupling. The safe next mutation should first retire or migrate those guards in the same batch as the archive move, not move the files alone.

## Required Pre-Mutation Checks

Before any A2 archive move:

```bash
rg -n "views/errors|errors/Forbidden|errors/NetworkError|errors/ServiceUnavailable|src/views/errors" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "@/views/errors|../errors/|./errors/" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "Forbidden|NetworkError|ServiceUnavailable" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/src/config/pageConfig.ts web/frontend/package.json --glob '!**/.claude/**'
```

Before any A2 retain/promotion:

```bash
rg -n "HOME_ROUTE_PATH|/health|/health/database|/health/cache|/analysis|/settings" web/frontend/src/views/errors web/frontend/src web/backend/app --glob '!**/.claude/**'
```

## Required Validation

For `A2-archive`:

```bash
cd web/frontend && npx vitest run tests/unit/config/errors-mainline-gate.spec.ts tests/unit/config/errors-forbidden-style-source.spec.ts tests/unit/config/errors-network-style-source.spec.ts tests/unit/config/errors-service-unavailable-style-source.spec.ts
openspec validate update-frontend-view-governance --strict
```

If package guard is edited, also run:

```bash
cd web/frontend && npm run lint:artdeco:changed
```

If any route is added or blank-layout behavior changes, also run blank-layout smoke.

## Non-Scope

- Do not touch `Login.vue` or `NotFound.vue`; they are active blank-layout route truth.
- Do not add `views/errors/*` to the main menu.
- Do not move error assets without retiring/migrating their direct tests in the same batch.
- Do not convert local health probes into product truth without confirming backend endpoint contracts.

## Approval Needed

A2 is not yet approved for mutation. The next decision should choose exactly one profile:

- `A2-archive`: retire/migrate the error demo guards and move the four error-shell assets to governed archive.
- `A2-retain`: promote them into formal special routes/error handling and fix route/health truth.
- `A2-defer`: leave them untouched and choose another batch.
