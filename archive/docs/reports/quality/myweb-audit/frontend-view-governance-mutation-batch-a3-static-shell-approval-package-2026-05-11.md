# Frontend View Governance A3 Static Shell Approval Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for the `A3-static-shell-archive` profile under `openspec/changes/update-frontend-view-governance`.

This package does not move files, edit runtime code, update tests, or change routes.

## Decision Needed

Approve or defer the smallest monitoring mutation profile:

```text
A3-static-shell-archive
```

Exact active files in scope:

- `web/frontend/src/views/monitoring/MonitoringDashboard.vue`
- `web/frontend/src/views/monitoring/__tests__/MonitoringDashboard.spec.ts`
- `web/frontend/src/views/monitoring/styles/MonitoringDashboard.scss`

Direct guard files to update in the same batch:

- `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts`
- `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`
- `web/frontend/tests/unit/config/console-log-cleanup-batch-1.spec.ts`

## Preflight Result

Active runtime truth:

- No current `router/index.ts` import or route owner found for `@/views/monitoring/MonitoringDashboard.vue`.
- No current `MenuConfig.ts` owner found for `/monitoring/dashboard`.
- No `web/frontend/package.json` direct target for `MonitoringDashboard.vue`.
- The page is already an honest static legacy shell and does not contain live data logic.

Active blockers:

- `src/views/monitoring/__tests__/MonitoringDashboard.spec.ts` imports the page directly.
- `monitoring-style-sources.spec.ts` reads `src/views/monitoring/styles/MonitoringDashboard.scss`.
- `monitoring-system-strategy-style-normalization.spec.ts` includes `src/views/monitoring/MonitoringDashboard.vue` in its style-entrypoint file list.
- `console-log-cleanup-batch-1.spec.ts` includes `src/views/monitoring/MonitoringDashboard.vue` in its file list.

Historical references:

- Many docs and historical audit artifacts mention `MonitoringDashboard.vue`.
- These references record prior migration/repair evidence and should not block archive movement if the archive manifest records the current status.
- `ArtDecoMonitoringDashboard.vue` is a different compat-retained ArtDeco system wrapper and is explicitly out of scope.

## Proposed Mutation

Move:

```text
web/frontend/src/views/monitoring/MonitoringDashboard.vue
web/frontend/src/views/monitoring/__tests__/MonitoringDashboard.spec.ts
web/frontend/src/views/monitoring/styles/MonitoringDashboard.scss
```

to:

```text
archive/web/frontend/src/views/monitoring/static-shell/
```

Update active guard files:

- Remove `MonitoringDashboard.scss` from `monitoring-style-sources.spec.ts`.
- Remove `MonitoringDashboard.vue` from `monitoring-system-strategy-style-normalization.spec.ts`.
- Remove `MonitoringDashboard.vue` from `console-log-cleanup-batch-1.spec.ts`.

Do not edit:

- `web/frontend/src/router/index.ts`
- `web/frontend/src/layouts/MenuConfig.ts`
- `web/frontend/package.json`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue`
- `AlertRulesManagement.vue`, `RiskDashboard.vue`, or `WatchlistManagement.vue`

## Successor / Rationale

Successor:

- `no-successor-needed` for the static shell itself.
- Existing shell guidance already points users to canonical live surfaces: `/market/realtime`, `/risk/overview`, and `/market/lhb`.

Reason:

- The page has no active route/menu owner and was intentionally degraded to a static shell because no reusable canonical monitoring truth exists for its prior pseudo-live dashboard surface.
- The static-shell test served as repair proof and can move with the archived page.

## Required Final Checks

Before moving:

```bash
rg -n "MonitoringDashboard|monitoring/MonitoringDashboard|src/views/monitoring/MonitoringDashboard|MonitoringDashboard.scss" web/frontend/src web/frontend/tests web/frontend/package.json docs openspec --glob '!**/.claude/**'
rg -n "@/views/monitoring|../monitoring|./monitoring" web/frontend/src web/frontend/tests --glob '!**/.claude/**'
rg -n "/monitoring/dashboard|/monitoring/risk|/monitoring/watchlists" web/frontend/src/router/index.ts web/frontend/src/layouts/MenuConfig.ts web/frontend/tests docs --glob '!**/.claude/**'
```

After moving:

```bash
rg -n "src/views/monitoring/MonitoringDashboard|src/views/monitoring/styles/MonitoringDashboard|../MonitoringDashboard.vue" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
cd web/frontend && npx vitest run tests/unit/config/monitoring-style-sources.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts tests/unit/config/console-log-cleanup-batch-1.spec.ts
openspec validate update-frontend-view-governance --strict
```

If the broad `lint:artdeco:changed` command is run, any existing unrelated `advanced-analysis` token debt must be reported separately from the A3 result.

## Approval Wording

To execute this profile, use:

```text
批准执行 A3-static-shell-archive，仅处理 MonitoringDashboard 静态壳、其本地测试和 MonitoringDashboard.scss，并同步更新直接 guard；不改 router/menu/package，不处理其他 monitoring functional pages。
```

Without explicit approval, `3.16` remains open and no A3 mutation should occur.
