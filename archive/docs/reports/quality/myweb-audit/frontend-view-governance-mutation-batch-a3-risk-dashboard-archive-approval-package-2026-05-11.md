# Frontend View Governance A3 Risk Dashboard Archive Approval Package

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: approval package for `openspec/changes/update-frontend-view-governance` after `A3-risk-coverage-review`.

This package does not move files, edit runtime code, update tests, or change routes.

## Proposed Batch

```text
A3-risk-dashboard-archive-prep
```

Recommended next execution profile, only if approved:

```text
A3-risk-dashboard-archive
```

## Exact Archive Candidates

Move only these files:

- `web/frontend/src/views/monitoring/RiskDashboard.vue`
- `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts`
- `web/frontend/src/views/monitoring/styles/RiskDashboard.scss`

Target archive directory:

- `archive/web/frontend/src/views/monitoring/risk-dashboard/RiskDashboard.vue`
- `archive/web/frontend/src/views/monitoring/risk-dashboard/useRiskDashboard.ts`
- `archive/web/frontend/src/views/monitoring/risk-dashboard/RiskDashboard.scss`

No other `views/monitoring/*`, `views/risk/*`, router, menu, API, store, or package script file is in scope.

## Successor Coverage Decision

`RiskDashboard.vue` has no current route/menu ownership. Current risk-domain truth is split across:

- `/risk/overview`: rules, alerts, and explicit `未校验/待接入` risk metric states.
- `/risk/alerts`: alert records and alert-rule CRUD with verified snapshot retention.
- `/risk/stop-loss`: stop-loss monitoring through watchlist, quotes, selector-key isolation, and verified snapshot retention.
- `/risk/management`: position-derived risk overview and risk action observation.
- `/risk/pnl`: portfolio/pnl route family, outside this archive mutation.

The legacy page does not provide safe unique runtime truth:

- `getScoreChange()` uses `Math.random()`.
- Active/inactive position counts are a hard-coded `80/20` split.
- Portfolio health/risk scores and rebalance suggestions depend on stale `/api/monitoring/analysis/portfolio/*` fetch paths.
- Risk metrics render fallback/`N/A` states instead of canonical verified provenance.
- `useRiskDashboard()` is called without the required `watchlistId` options argument.

Therefore this batch should archive, not absorb, the old risk dashboard group.

## Direct Active Guard Retirements

If execution is approved, retire only these direct active guard entries:

- In `web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts`, remove `src/views/monitoring/styles/RiskDashboard.scss` from the guarded file list while keeping `WatchlistManagement.scss`.
- In `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`, remove `src/views/monitoring/RiskDashboard.vue` from the guarded file list while keeping `WatchlistManagement.vue` and non-monitoring entries.

Do not edit:

- `web/frontend/src/router/index.ts`
- `web/frontend/src/layouts/MenuConfig.ts`
- `web/frontend/src/views/risk/*`
- `web/frontend/src/views/monitoring/WatchlistManagement.vue`
- `web/frontend/src/views/monitoring/composables/useWatchlistManagement.ts`
- `web/frontend/src/views/monitoring/styles/WatchlistManagement.scss`
- Historical E2E specs that only mention labels or old `/monitoring/*` URLs and do not import the archived file.

## Required Pre-Move Checks

```bash
rg -n "RiskDashboard|useRiskDashboard|RiskDashboard.scss|monitoring/RiskDashboard|src/views/monitoring/RiskDashboard" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
```

Expected active mentions before the move:

- The three candidate source files.
- The two direct config guard entries listed above.
- Historical monitoring E2E label strings may appear under `web/frontend/tests/*`; they must not be treated as active route/menu ownership unless they import or route to the source file.

## Required Execution Steps

1. Move only the three exact candidate files into `archive/web/frontend/src/views/monitoring/risk-dashboard/`.
2. Update only the two direct config guard specs listed in this package.
3. Re-run active source/test/package reference checks.
4. Run the targeted validation commands.
5. Stage only the three archive moves, two guard edits, and `openspec/changes/update-frontend-view-governance/tasks.md`.
6. Run GitNexus staged change detection before commit.
7. Commit the mutation batch separately.

## Required Validation

```bash
cd web/frontend && npx vitest run tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts src/views/risk/__tests__/Overview.spec.ts src/views/risk/__tests__/Alerts.spec.ts src/views/risk/__tests__/StopLoss.spec.ts
openspec validate update-frontend-view-governance --strict
python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path openspec/changes/update-frontend-view-governance/tasks.md
git diff --check -- web/frontend/tests/unit/config/monitoring-fintech-bridge-style-sources.spec.ts web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts openspec/changes/update-frontend-view-governance/tasks.md
```

GitNexus staged scope:

```json
{
  "repo": "mystocks_spec",
  "scope": "staged",
  "cwd": "/opt/claude/mystocks_spec"
}
```

## Rejection Conditions

Do not execute the archive if any of these are found:

- A current router/menu/page-config/package script dynamic import to `monitoring/RiskDashboard`.
- A canonical `/risk/*` page still depends on `useRiskDashboard.ts` or `RiskDashboard.scss`.
- A hidden active guard imports the legacy page directly and cannot be retired in this narrow batch.
- The intended staged scope includes unrelated dirty worktree files.

## Approval Needed

Recommended approval wording:

```text
批准执行 A3-risk-dashboard-archive，只移动 RiskDashboard.vue、useRiskDashboard.ts、RiskDashboard.scss 到 archive/web/frontend/src/views/monitoring/risk-dashboard/，并只退休这三个文件的直接 config guard；不修改 canonical /risk/* runtime，不吸收旧页伪实时指标，不触碰 WatchlistManagement。
```

Without explicit approval, no file move or guard edit should occur.
