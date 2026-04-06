# MyStocks Frontend Mainline Overall Closeout

> **历史文档说明**:
> 本文件是某阶段的历史文档、过程记录或专题材料，不是当前基线、当前系统总览或仓库共享规则的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现、验证结果与主线文档使用。
>
> 文内描述、背景、结论和上下文如未重新复核，应视为历史快照，不得直接当作当前事实。


> Generated at: `2026-04-06T13:32:02+08:00`
> Overall plan: `docs/plans/2026-04-02-frontend-mainline-testing-overall-plan.md`
> Scope: `34` pages across `Phase 1-4`
> Branch: `wip/root-dirty-20260403`

## 1. Overall Verdict

- Frontend mainline `Phase 1-4` remains in overall usable closeout after the `2026-04-06` refresh.
- Page-level verdict:
  - Mock: `34 / 34 PASS`
  - Real: `34 / 34 PASS`
- Aggregate issue classification:
  - `route/config drift`: `0`
  - `frontend render gap`: `0`
  - `backend contract/runtime gap`: `0`
- `System-Config` no longer remains as a residual gap:
  - the page is routable and usable
  - the monitor panel reads real backend health endpoints
  - the settings form now reads and writes the `general` section through `/api/v1/system/settings/general`
  - the broader settings truth remains intentionally sectioned rather than monolithic

## 2. Phase Summary

| Phase | Pages | Mock | Real | Classification | Key Result |
| --- | --- | --- | --- | --- | --- |
| Phase 1 | `6` | `6 / 6 PASS` | `6 / 6 PASS` | `0 / 0 / 0` | 收口启动链与市场首批页面；主要问题是 PM2 / proxy / readiness 运行态漂移，不是页面缺失 |
| Phase 2 | `6` | `6 / 6 PASS` | `6 / 6 PASS` | `0 / 0 / 0` | 收口数据分析与自选管理；唯一源码修复是 `Watchlist-Manage` 删除动作渲染缺口 |
| Phase 3 | `12` | `12 / 12 PASS` | `12 / 12 PASS` | `0 / 0 / 0` | 收口策略与交易主链；未发现新的生产源码回归 |
| Phase 4 | `10` | `10 / 10 PASS` | `10 / 10 PASS` | `0 / 0 / 0` | 收口风险与系统页；`System-Config` 已切换到分段后端契约并完成主线收口 |

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
  - `2026-04-05` refresh additionally reloaded the live PM2 frontend shell so its proxy env returned from stale `BACKEND_PORT=8888` to repo truth `BACKEND_PORT=8020`
  - `2026-04-06` approved sectioned contract landing additionally updated:
    - `web/backend/app/api/v1/system/settings.py`
    - `web/backend/tests/test_system_settings_contract.py`
    - `web/frontend/src/services/systemSettingsContract.ts`
    - `web/frontend/src/views/system/Settings.vue`
    - `web/frontend/src/views/system/__tests__/Settings.spec.ts`

## 4. Sectioned Contract Closure

### `System-Config`

- Frontend route truth:
  - route entry: [index.ts](/opt/claude/mystocks_spec/web/frontend/src/router/index.ts)
  - active page: [Settings.vue](/opt/claude/mystocks_spec/web/frontend/src/views/system/Settings.vue)
  - compatibility surface: [ArtDecoSystemSettings.vue](/opt/claude/mystocks_spec/web/frontend/src/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue) only wraps the canonical page
- Current behavior:
  - page banner now states that `System-Config` runs on a sectioned truth and does not use a monolithic backend store
  - page CTA is `保存系统设置`
  - `saveAll()` now calls `monitoringApi.updateSystemGeneralSettings(...)`
  - monitor rows remain read-only and come from `monitoringApi.getDetailedSystemHealth()` / `monitoringApi.getSystemHealth()`
- Backend truth check:
  - canonical system-scoped routes now exist:
    - [settings.py](/opt/claude/mystocks_spec/web/backend/app/api/v1/system/settings.py) -> `/api/v1/system/settings/general`
    - [settings.py](/opt/claude/mystocks_spec/web/backend/app/api/v1/system/settings.py) -> `/api/v1/system/settings/security`
  - canonical persistence is PostgreSQL `system_config`
  - datasource and notification continue to use their own canonical owners rather than a duplicated merged store
- Evidence split:
  - measured runtime checks:
    - `GET http://localhost:8020/api/v1/system/settings/general` -> `200`
    - `GET http://localhost:8020/api/v1/system/settings/security` -> `200`
  - measured targeted tests:
    - backend contract tests passed
    - frontend `Settings.vue` + section-composition tests passed
    - `vue-tsc --noEmit` passed
  - not measured in this refresh:
    - no destructive shared-runtime live write mutation was executed against PM2
- Closeout rule:
  - `System-Config` now counts as closed for the frontend-mainline `backend contract/runtime gap`
  - this does **not** imply a single monolithic unified settings API exists
  - future work should keep section ownership explicit for `general` / `security` / `datasource` / `notification`

## 5. Quality Gate

- Structural syntax errors: `0`
- Frontend type baseline: `reports/analysis/tech-debt-baseline.json` -> `frontend_type_errors = 0`
- Type-check execution in overall closeout refresh:
  - `cd web/frontend && npx vue-tsc --noEmit --pretty false`
  - Result: `exit 0`, no output
- Supplemental contract verification in this refresh:
  - `cd web/backend && PYTHONPATH=. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/test_system_settings_contract.py tests/test_health_route_conflicts.py -q -o addopts="" -k system_settings`
  - Result: `passed`
  - `cd web/frontend && npx vitest run src/views/system/__tests__/Settings.spec.ts src/services/__tests__/systemSettingsContract.spec.ts src/services/__tests__/TradingApiManager.system-settings.spec.ts`
  - Result: `passed`
  - `curl -sS -o /tmp/system-settings-general.json -w '%{http_code}' http://localhost:8020/api/v1/system/settings/general`
  - Result: `200`
  - `curl -sS -o /tmp/system-settings-security.json -w '%{http_code}' http://localhost:8020/api/v1/system/settings/security`
  - Result: `200`
- Type regression verdict:
  - no evidence of regression above baseline in the closeout refresh batch
  - the overall closeout artifacts now reflect a fresh zero-output type check against the current repo head
- PM2 current state rechecked at closeout time:
  - `mystocks-backend`: `online`
  - `mystocks-frontend`: `online`
- Service addresses:
  - `http://localhost:8020`
  - `http://localhost:3020`
- Service health recheck:
  - `/health` -> `200`
  - `/health/ready` -> `200`
  - `/api/health/ready` -> `200`
  - live PM2 frontend proxy env re-aligned to `BACKEND_PORT=8020`

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
  - Historical follow-up smoke (`2026-04-04`):
    - `phase4-mainline-matrix.spec.ts`
    - grep: `System-Config renders blocker note and persists local settings`
    - project: `chromium`
    - mode: `PLAYWRIGHT_EXTERNAL_FRONTEND=1` against live PM2 frontend on `http://127.0.0.1:3020`
    - result: `1 passed, 0 failed, 0 skipped`
  - Current sectioned-contract refresh (`2026-04-06`):
    - `GET /api/v1/system/settings/general` -> `200`
    - `GET /api/v1/system/settings/security` -> `200`
    - backend contract tests: `passed`
    - frontend sectioned-settings tests: `passed`
  - Refresh rerun:
    - `phase4-mainline-matrix.spec.ts` against live PM2 frontend
    - result: `10 passed, 0 failed, 0 skipped` (`15.0s`)
    - `comprehensive-all-pages.spec.ts` Phase 4 subset against live PM2 frontend
    - result: `10 passed, 0 failed, 0 skipped` (`4.4m`)

## 7. Final Conclusion

- The frontend mainline overall plan is now fully executed through Phase `1-4`.
- The verified result is:
  - `34` target pages are present, routable, and green under the established Mock/Real matrix
  - no unresolved `route/config drift`
  - no unresolved `frontend render gap`
  - no unresolved `backend contract/runtime gap`
- The next work should not reopen the whole mainline.
- The targeted `System-Config` follow-up is now complete:
  - landed the approved sectioned backend contract for `general` / `security`
  - retired the canonical page-level local draft fallback
  - refreshed active mainline artifacts so they no longer describe `System-Config` as `localStorage`-only
- The `2026-04-05` refresh also cleared a stale PM2 frontend proxy env drift so live `/api/health/ready` is back to `200`.
- No further frontend-mainline batch is required unless the page later expands to new section owners and needs additional live-browser non-destructive smoke.
