# Backend Health / Status PM2 Gate Evidence

Date: 2026-05-18
OpenSpec change: `consolidate-backend-health-endpoints`
Scope: `4.7` PM2 integration workflow gate

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

## Result

`./scripts/run_pm2_integration_workflow.sh gate` completed successfully after explicit approval to run the stateful workflow.

Final gate summary:

- Type check command: `npm run type-check`
- Type check exit code: `0`
- Frontend test command: `npm run test`
- Frontend test exit code: `0`
- Frontend unit result: `378 passed (378)` test files, `1415 passed (1415)` tests
- PM2 E2E command: `bash scripts/run_e2e_pm2.sh`
- PM2 E2E exit code: `0`
- PM2 E2E result: `14 passed`
- Gate result: `PASS`

## Service Restore

The PM2 gate deletes the temporary PM2 processes after completion. Services were restarted with:

```bash
pm2 start ecosystem.test.config.js
```

Post-restore checks:

- `mystocks-backend`: `online`
- `mystocks-frontend`: `online`
- `http://localhost:8020/health`: HTTP 200
- `http://localhost:8020/api/health/ready`: HTTP 200
- `http://localhost:3020/`: HTTP 200

## Gate Stabilization Notes

The first full PM2 gate run exposed frontend gate drift before the PM2 E2E phase. The following minimal fixes were required before the final passing run:

- Stabilized ML workbench generated request types by mapping `NonBlankString` fields to `string` in `web/frontend/src/api/types/strategy.ts`.
- Removed stale `SkeletonUsage.vue` ArtDeco governance expectations because `web/frontend/src/views/SkeletonUsage.vue` is not present in the current tree.
- Added `/ai/ml` and `/ai/batch` to the comprehensive E2E route inventory and aligned `/ai/sentiment` with router API metadata.
- Updated the K-line tab unit expectation to include the current `refresh_seq` query parameter.
- Added missing `getSystemSecuritySettings` / `updateSystemSecuritySettings` mocks for the system settings test wrapper.

## Closure Boundary

This evidence closes OpenSpec task `4.7` for the health/status consolidation line. It does not archive the OpenSpec change by itself; archive timing remains a separate governance decision after the intended change set is reviewed and committed.
