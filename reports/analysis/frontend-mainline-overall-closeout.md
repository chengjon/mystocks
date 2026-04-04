# MyStocks Frontend Mainline Overall Closeout

> Generated at: `2026-04-04T20:33:23+08:00`
> Overall plan: `docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> Scope: `34` pages across `Phase 1-4`
> Branch: `wip/root-dirty-20260403`

## 1. Overall Verdict

- Frontend mainline `Phase 1-4` has reached overall usable closeout on `2026-04-03`.
- Page-level verdict:
  - Mock: `34 / 34 PASS`
  - Real: `34 / 34 PASS`
- Aggregate issue classification:
  - `route/config drift`: `0`
  - `frontend render gap`: `0`
  - `backend contract/runtime gap`: `1`
- The single preserved residual debt is `System-Config`:
  - the page is routable and usable
  - the monitor panel reads real backend health endpoints
  - `2026-04-04` follow-up confirmed that no unified backend config write contract exists in current repo truth
  - the current `保存本地设置` action is still local-only degrade and must not be reported as verified backend real-write closure

## 2. Phase Summary

| Phase | Pages | Mock | Real | Classification | Key Result |
| --- | --- | --- | --- | --- | --- |
| Phase 1 | `6` | `6 / 6 PASS` | `6 / 6 PASS` | `0 / 0 / 0` | 收口启动链与市场首批页面；主要问题是 PM2 / proxy / readiness 运行态漂移，不是页面缺失 |
| Phase 2 | `6` | `6 / 6 PASS` | `6 / 6 PASS` | `0 / 0 / 0` | 收口数据分析与自选管理；唯一源码修复是 `Watchlist-Manage` 删除动作渲染缺口 |
| Phase 3 | `12` | `12 / 12 PASS` | `12 / 12 PASS` | `0 / 0 / 0` | 收口策略与交易主链；未发现新的生产源码回归 |
| Phase 4 | `10` | `10 / 10 PASS` | `10 / 10 PASS` | `0 / 0 / 1` | 收口风险与系统页；仅保留 `System-Config` 真实配置写链未确认 |

> Classification column order: `route/config drift / frontend render gap / backend contract/runtime gap`

## 3. Source Fix Footprint

Resolved during the full mainline run:

- Phase 1 runtime / config repairs:
  - `ecosystem.test.config.js`
  - `web/backend/ecosystem.config.js`
  - `web/backend/tests/test_post_rewrite_backend_import_stability.py`
  - fixed backend `PYTHONPATH` drift, frontend proxy drift, and readiness recovery prerequisites
- Phase 2 page repair:
  - `web/frontend/src/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue`
  - corrected shared table slot contract from `#action` to `#actions`
  - removed duplicated action column that hid the delete control
- Phase 3 closeout:
  - no production source fix required
- Phase 4 closeout:
  - no production source fix required

## 4. Residual Debt Kept Explicit

### `System-Config`

- Frontend page:
  - `web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue`
- Current behavior:
  - page banner already states: `统一系统配置后端契约仍未建立，当前页面仅保留本地设置持久化与健康监控视图；数据源真实配置写回请前往“系统数据”页。`
  - page CTA is `保存本地设置`
  - `saveAll()` only executes `localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...form }))`
  - monitor rows are read-only and come from `monitoringApi.getDetailedSystemHealth()` / `monitoringApi.getSystemHealth()`
- Backend truth check:
  - no backend route matching `/api/system/settings` was found under `web/backend/app`
  - confirmed read-only health endpoints exist:
    - `web/backend/app/api/health.py` -> `/health`
    - `web/backend/app/api/health.py` -> `/health/detailed`
  - nearest write-capable but non-equivalent backend contract is data source configuration:
    - `web/frontend/src/api/index.ts` -> `POST /v1/data-sources/config/batch`
    - `web/backend/app/api/data_source_config.py`
  - stale frontend constant hint for `/api/system/settings` has been removed from `web/frontend/src/types/unified-api.ts`
- Closeout rule:
  - `System-Config` counts as `Mock PASS` + `Real PASS` for route-shell and real-read
  - it does **not** count as verified real-write closure
  - the contract-truth follow-up is complete; the residual debt is now explicitly accepted rather than left as an open frontend discovery item

## 5. Quality Gate

- Structural syntax errors: `0`
- Frontend type baseline: `reports/analysis/tech-debt-baseline.json` -> `frontend_type_errors = 0`
- Type-check execution in overall closeout: not executed
- Type regression verdict:
  - no evidence of regression above baseline in the closeout batches
  - phases `1-4` all reported `frontend_type_check_executed = false`
- PM2 current state rechecked at closeout time:
  - `mystocks-backend`: `online`
  - `mystocks-frontend`: `online`
  - `mystocks-frontend-static`: `online`
- Service addresses:
  - `http://localhost:8020`
  - `http://localhost:3020`
- Service health recheck:
  - `/health` -> `200`
  - `/health/ready` -> `200`
  - `/api/health/ready` -> `200`

## 6. Execution Evidence

- Mock track:
  - Phase 1:
    - `34 passed, 0 failed, 0 skipped`
  - Phase 2:
    - `6 passed, 0 failed, 0 skipped`
  - Phase 3:
    - `12 passed, 0 failed, 0 skipped`
  - Phase 4:
    - `10 passed, 0 failed, 0 skipped`
- Real track:
  - Phase 1:
    - page subset `5 passed, 0 failed, 0 skipped`
    - real login chain: `PASS`
  - Phase 2:
    - `6 passed, 0 failed, 0 skipped`
  - Phase 3:
    - `12 passed, 0 failed, 0 skipped`
  - Phase 4:
    - `10 passed, 0 failed, 0 skipped`
  - Follow-up targeted smoke:
    - `phase4-mainline-matrix.spec.ts`
    - grep: `System-Config renders blocker note and persists local settings`
    - project: `chromium`
    - mode: `PLAYWRIGHT_EXTERNAL_FRONTEND=1` against live PM2 frontend on `http://127.0.0.1:3020`
    - result: `1 passed, 0 failed, 0 skipped`

## 7. Final Conclusion

- The frontend mainline overall plan is now fully executed through Phase `1-4`.
- The verified result is:
  - `34` target pages are present, routable, and green under the established Mock/Real matrix
  - no unresolved `route/config drift`
  - no unresolved `frontend render gap`
  - one intentionally preserved `backend contract/runtime gap`
- The next work should not reopen the whole mainline.
- The targeted `System-Config` follow-up is now complete:
  - confirmed no unified backend config write contract exists in current repo truth
  - aligned generated frontend `pageConfig` to that truth
  - passed a focused post-cutover route smoke against the live PM2 frontend shell
- No further frontend-mainline batch is required unless a new backend `System-Config` write contract is introduced and approved later.
