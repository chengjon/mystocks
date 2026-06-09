# Frontend View Governance A3 Static Shell Execution Report

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

Date: 2026-05-11

Scope: `A3-static-shell-archive` mutation batch for `openspec/changes/update-frontend-view-governance`.

## Executed Change

Moved the monitoring static shell assets from active source tree to governed archive:

```text
web/frontend/src/views/monitoring/MonitoringDashboard.vue
web/frontend/src/views/monitoring/__tests__/MonitoringDashboard.spec.ts
web/frontend/src/views/monitoring/styles/MonitoringDashboard.scss
```

Archive target:

```text
archive/web/frontend/src/views/monitoring/static-shell/
```

Updated direct active guards:

- Removed `src/views/monitoring/styles/MonitoringDashboard.scss` from `web/frontend/tests/unit/config/monitoring-style-sources.spec.ts`.
- Removed `src/views/monitoring/MonitoringDashboard.vue` from `web/frontend/tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts`.
- Removed `src/views/monitoring/MonitoringDashboard.vue` from `web/frontend/tests/unit/config/console-log-cleanup-batch-1.spec.ts`.

No changes were made to:

- `web/frontend/src/router/index.ts`
- `web/frontend/src/layouts/MenuConfig.ts`
- `web/frontend/package.json`
- `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue`
- `web/frontend/src/views/monitoring/AlertRulesManagement.vue`
- `web/frontend/src/views/monitoring/RiskDashboard.vue`
- `web/frontend/src/views/monitoring/WatchlistManagement.vue`

## Pre-Move Evidence

- GitNexus upstream impact for `web/frontend/src/views/monitoring/MonitoringDashboard.vue`: LOW, 0 direct dependents, 0 affected processes.
- No active router or menu owner was found for `@/views/monitoring/MonitoringDashboard.vue` or `/monitoring/dashboard`.
- Direct active blockers were limited to the local static-shell proof spec and three config guards.
- Historical docs and old E2E `/monitoring/*` strings were not treated as current route truth.

## Validation Results

```bash
rg -n "src/views/monitoring/MonitoringDashboard|src/views/monitoring/styles/MonitoringDashboard|../MonitoringDashboard.vue" web/frontend/src web/frontend/tests web/frontend/package.json --glob '!**/.claude/**'
```

Result:

- Passed with no active matches.

```bash
cd web/frontend && npx vitest run tests/unit/config/monitoring-style-sources.spec.ts tests/unit/config/monitoring-system-strategy-style-normalization.spec.ts tests/unit/config/console-log-cleanup-batch-1.spec.ts
```

Result:

- Passed: 3 test files, 3 tests.
- Note: the first sandboxed run failed before tests because `vitest.config.mts` could not read `../../../package.json`; the same command was rerun outside the sandbox and passed.

```bash
openspec validate update-frontend-view-governance --strict
```

Result:

- Passed.

```bash
python scripts/compliance/markdown_governance_gate.py --root-dir /opt/claude/mystocks_spec --format text --path archive/web/frontend/src/views/monitoring/static-shell/README.md --path docs/reports/quality/myweb-audit/frontend-view-governance-a3-static-shell-execution-report-2026-05-11.md --path openspec/changes/update-frontend-view-governance/tasks.md
```

Result:

- Passed: 3 files checked, 0 errors.

```bash
gitnexus_detect_changes(scope="staged")
```

Result:

- Risk: LOW.
- Changed files: 1.
- Affected processes: 0.

If the broad `npm run lint:artdeco:changed` command is run, the known unrelated `advanced-analysis` ArtDeco token debt must remain separate from the A3 result unless this batch edits those files.

## Completion Decision

A3 static-shell archive is governance-complete for the approved mutation scope after staged GitNexus detection and commit-scope checks pass.
