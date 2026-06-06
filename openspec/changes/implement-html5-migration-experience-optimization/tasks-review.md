# Review: tasks.md

**Type**: .md / plan (task breakdown) | **Perspective**: completeness + feasibility | **Date**: 2026-05-08 | **Reviewer**: Claude

---

## Executive Summary

This is an exceptionally well-maintained task tracking document with rigorous repo-truth annotation. Every checked item has corresponding codebase evidence; every unchecked item has an explicit blocker explanation with dates. The 65 tasks across 3 phases show 31 completed, 34 open. The main structural issues are: 6 de-scoped mobile items still listed as open instead of formally closed/marked, and 3 stale unit tests blocking the coverage baseline are not tracked as remediation tasks within this plan.

## Document Metadata

| Field | Value |
|-------|-------|
| Source | `openspec/changes/implement-html5-migration-experience-optimization/tasks.md` |
| File Type | .md |
| Doc Type | plan (task breakdown with phases, validation criteria) |
| Sections | 12 (3 phases + success metrics) |
| Total Tasks | 65 |
| Completed | 31 |
| Open | 34 |
| Referenced Files | 24 found / 0 missing |
| Referenced Symbols | 8 found / 0 missing |

## Evidence Verification

### Files Referenced

| File | Exists? | Location |
|------|---------|----------|
| `web/frontend/src/layouts/MenuConfig.ts` | yes | confirmed, line 47: "7 Domains" |
| `web/frontend/src/router/index.ts` | yes | confirmed |
| `web/frontend/src/stores/menuStore.ts` | yes | confirmed |
| `web/frontend/src/stores/preferenceStore.ts` | yes | confirmed |
| `web/frontend/package.json` | yes | confirmed |
| `web/frontend/vite.config.mts` | yes | confirmed |
| `web/frontend/src/views/monitoring/composables/useRiskDashboard.ts` | historical yes; current no | G2.396 recheck confirms the file is no longer present in the current tree; keep earlier references as historical migration evidence only |
| `web/frontend/src/components/monitoring/MonitoringAlertPanel.vue` | yes | confirmed |
| `web/frontend/src/components/monitoring/MonitoringDataTable.vue` | yes | confirmed |
| `web/frontend/src/utils/workersManager/workers-manager.ts` | yes | confirmed, line 39: "Placeholder implementation" |
| `web/frontend/playwright.config.ts` | yes | confirmed, line 55: `testMatch: /.*\.spec\.(ts|js)$/` |
| `web/frontend/tests/design-token.test.ts` | yes | confirmed (uses `.test.ts`, not `.spec.ts`) |
| `web/frontend/tests/stock-colors.test.ts` | yes | confirmed (uses `.test.ts`, not `.spec.ts`) |
| `web/frontend/tests/artdeco-style.test.ts` | no | doc correctly states this file does not exist |
| `web/frontend/src/styles/theme-tokens.scss` | yes | confirmed, line 206: "Desktop-only, no mobile" |
| `web/frontend/ENTRY-TRUTH.md` | yes | confirmed |
| `web/frontend/src/_entry-archive/` | yes | confirmed, 9 archive files present |
| `docs/guides/frontend/HTML5_RUNTIME_CAPABILITY_GUIDE.md` | yes | confirmed |
| `docs/guides/frontend/HTML5_RUNTIME_USER_GUIDE.md` | yes | confirmed |
| `docs/guides/frontend/HTML5_RUNTIME_OPERATIONS_GUIDE.md` | yes | confirmed |
| `docs/guides/frontend/HTML5_RUNTIME_ROLLOUT_COMMUNICATION_GUIDE.md` | yes | confirmed |
| `web/frontend/src/views/artdeco-pages/settings/NotificationSettings.vue` | yes | confirmed |
| `web/frontend/src/composables/useNetworkStatus.ts` | yes | confirmed |

### Claims Verified

| Claim | Status | Evidence |
|-------|--------|----------|
| MenuConfig has 7 business domains | confirmed | `MenuConfig.ts:47` comment + 7 domain constants: MARKET, DATA, WATCHLIST, STRATEGY, TRADE, RISK, SYSTEM |
| `ant-design-vue` removed from runtime deps | confirmed | grep on `package.json` for `ant-design-vue` returns no matches; only `@ant-design/icons-vue` remains at line 79 |
| 3 source files still import `@ant-design/icons-vue` | confirmed | `useRiskDashboard.ts`, `MonitoringAlertPanel.vue`, `MonitoringDataTable.vue` |
| `artdeco-style.test.ts` does not exist | confirmed | Glob returns empty |
| `playwright.config.ts` only matches `*.spec.(ts\|js)` | confirmed | line 55: `testMatch: /.*\.spec\.(ts|js)$/` |
| Workers manager is placeholder | confirmed | `workers-manager.ts:39`: "Placeholder implementation - in production this would use actual Web Worker" |
| `theme-tokens.scss` states Desktop-only | confirmed | line 206: `// Breakpoints (Desktop-only, no mobile)` |
| `MarketKLineTab.spec.ts` still asserts `period: 'daily'` | confirmed | line 53: `period: 'daily'` |
| `_entry-archive/` contains 9 historical main files | confirmed | Glob found 9 files including README |

## Checklist Results

| # | Check | Result | Notes |
|---|-------|--------|-------|
| C1 | Required sections | PASS | 3 phases + success metrics with functional/performance/UX/business validation subsections |
| C2 | Edge cases | PASS | Every open item has explicit blocker explanation with dates and specific failure evidence |
| C3 | Implicit assumptions | PARTIAL | Assumes desktop-only scope (confirmed in codebase) but 6 mobile items remain listed as open rather than formally de-scoped |
| C4 | Acceptance criteria | PASS | Each checked item has repo-truth evidence; each unchecked item has blocker documentation |
| C5 | Missing roles/stakeholders | N/A | Single-user local deployment context |
| F1 | Technical risk | PASS | Placeholder implementations, stale tests, and missing assets all explicitly identified with specific file references |
| F2 | Dependency availability | PASS | `@ant-design/icons-vue` residual correctly tracked; `vite-plugin-pwa` disabled status documented |
| F3 | Timeline realism | N/A | No timeline estimates in document |
| F4 | Resource constraints | N/A | No resource estimates |
| F5 | Rollback plan | PARTIAL | Phase 3.3.3 mentions rollback but is unchecked with no detail; no specific rollback procedures documented for completed phases |

## Findings

### Medium Issues

| # | Section | Issue | Impact | Evidence | Recommendation |
|---|---------|-------|--------|----------|----------------|
| 1 | 2.7 HTML5 APIs (lines 242-246) | **6 de-scoped mobile items still listed as open tasks.** Items 2.7.1-2.7.5 and UX metric "mobile端响应式体验完善" have de-scope annotations (lines 233-240, 434-445) but remain `[ ]` unchecked, creating false open-task count | Inflates open task count by 6; creates ambiguity about whether these are TODO or formally closed | Doc lines 233-240 explicitly state these are "已去作用域的历史伸展项"; `theme-tokens.scss:206` confirms "Desktop-only, no mobile"; CLAUDE.md states "禁止移动端/平板适配" | Formally mark as `[x]` with a de-scope note like `[DE-SCOPED: Desktop-only product scope]`, or add a `[~]` skipped status to distinguish from active open tasks |
| 2 | 1.3.5 (lines 83-90) | **3 stale unit tests blocking coverage baseline are not tracked as remediation subtasks.** The blocker annotation correctly identifies `MarketKLineTab.spec.ts` (wrong period), `comprehensive-e2e-route-coverage.spec.ts` (wrong count), and `ci-workflow-gates.spec.ts` (wrong script name), but none are broken out as fix tasks | Coverage baseline (1.3.5) cannot close until these 3 tests are fixed; the fixes are trivial but not tracked as work items | Codebase confirms: `MarketKLineTab.spec.ts:53` has `period: 'daily'` (should be `'1d'`); `theme-tokens.scss` confirms desktop-only scope | Add 3 remediation subtasks (e.g., `1.3.5a Fix MarketKLineTab period assertion`, `1.3.5b Update route count`, `1.3.5c Fix CI workflow assertion`) to make the path to green explicit |

### Low Issues

| # | Section | Issue | Evidence | Recommendation |
|---|---------|-------|----------|----------------|
| 3 | 1.2.5 (lines 67-76) | Style test commands (`test:design-token`, `test:stock-colors`) point to `.test.ts` files but `playwright.config.ts` only matches `*.spec.(ts\|js)`. This config mismatch is documented as a blocker but no fix task exists | `playwright.config.ts:55` confirms `testMatch: /.*\.spec\.(ts|js)$/`; `package.json:66-68` confirms commands point to `.test.ts` files | Add a remediation subtask to either rename test files to `.spec.ts` or update `testMatch` to include `.test.ts` |
| 4 | 3.3.3 (line 293) | Rollback mechanism task is listed but has no detail about what rollback means for completed phases | Line 293: `[ ] 3.3.3 建立回滚机制和监控告警` with no annotation | Add annotation describing what rollback entails: e.g., "revert to pre-PWA Service Worker registration, disable manifest, restore previous Vite config" |
| 5 | Success Metrics (lines 461-480) | Business Impact metrics (留存率 >25%, 技术债减少 >60%, 开发效率提升 >40%) have no measurement methodology or baseline | Lines 461, 479, 480: these are purely aspirational with no annotation about how to measure | Either add measurement methodology notes or formally de-scope as post-launch metrics outside this change's scope |

## Strengths

- **Exceptional repo-truth discipline**: Every checkbox decision is backed by dated evidence with specific file paths, command outputs, and line references. This is best-in-class task tracking.
- **Honest blocker documentation**: Open items explain exactly WHY they cannot close, with specific technical root causes (e.g., `playwright.config.ts` `testMatch` mismatch, placeholder worker manager)
- **De-scope transparency**: Mobile/desktop-only scope changes are clearly annotated with dates (2026-05-08) and rationale
- **Test evidence specificity**: Test results include exact pass/fail counts, specific failing test names, and the exact assertion mismatches
- **Anti-premature-closure**: Explicit warnings against misrepresenting partial implementations as complete (e.g., line 14: "不能把'有文件/有接口'机械等同为'完整生产能力已闭环'")

## Detailed Recommendations

1. **Formalize de-scoped items**: Change the 6 mobile-related items (2.7.1-2.7.5, mobile UX metric) from `[ ]` to `[x]` with annotation `[DE-SCOPED: Desktop-only]`. This gives an accurate completion ratio (37/65 = 57% vs current misleading 31/65 = 48%) and removes ambiguity.

2. **Break out stale-test fixes**: The 3 blocking test failures (MarketKLineTab period, route count, CI workflow script) are trivial fixes that would unblock the coverage baseline. Track them as explicit subtasks under 1.3.5 with clear "change X to Y" descriptions.

3. **Fix or de-scope style test infrastructure**: The `testMatch` vs `.test.ts` mismatch is a config bug, not a feature gap. Either fix `playwright.config.ts` to accept `.test.ts` or rename the test files. Either way, make it a tracked task.

4. **De-scope unmeasurable business metrics**: Items like "用户留存率提升 > 25%" and "技术债务减少 > 60%" (lines 461, 479) have no measurement infrastructure. Mark them as post-launch observability targets rather than blocking success criteria for this change.

## Scoring

| Dimension | Score (1-5) | Evidence |
|-----------|-------------|----------|
| Technical Accuracy | 5 | All 24 file references verified; all codebase claims confirmed; zero factual errors found |
| Completeness | 4 | Comprehensive blocker documentation; de-scoped items not formally closed; stale test fixes not tracked |
| Codebase Alignment | 5 | Every repo-truth annotation matches live codebase state; worker placeholder, icon residuals, and Playwright config all confirmed |
| Actionability | 4 | Clear per-item evidence; but some remediation paths (stale tests, style config) not broken into fix tasks |
| Terminology Consistency | 5 | Consistent use of "repo-truth", "de-scope", "blocker" terminology throughout 480 lines |
| **Overall** | **4.6** | |

## Verdict

**APPROVE_WITH_NOTES** — This is one of the most rigorously evidence-anchored task documents in the repository. Zero factual errors were found across 24 referenced files. The two medium issues (formal de-scope of 6 mobile items, tracking 3 stale-test fixes as subtasks) are process improvements that would make the already-excellent tracking even more precise. No blockers to continuing work against this plan.

---

## Disposition Update - 2026-05-10

This section preserves the 2026-05-08 review as a historical snapshot and records the follow-up disposition against current repo-truth.

| Finding | Status | Current Evidence |
|---------|--------|------------------|
| Medium 1: de-scoped mobile items still open | CLOSED | `tasks.md` now marks `2.7.1` through `2.7.5`, `HTML5 APIs在支持浏览器中正常工作`, `移动端响应式体验完善`, and `移动端使用率提升 > 40%` as `[x]` with explicit `[DE-SCOPED: Desktop-only]` style annotations. |
| Medium 2: coverage stale-test fixes not tracked | CLOSED | `tasks.md` now tracks `1.3.5a` through `1.3.5f`, and `1.3.5` is closed under the narrower repo-truth meaning of “coverage baseline can be generated,” not “coverage reached 60%.” |
| Low 3: style gate `testMatch` mismatch | CLOSED | `web/frontend/playwright.config.ts` now matches both `*.spec.(ts\|js)` and `*.test.(ts\|js)`; `web/frontend/tests/artdeco-style.test.ts` exists; `npm run test:design-token`, `npm run test:stock-colors`, and `npm run test:artdeco-style` have real passing results recorded in `tasks.md`. |
| Low 4: rollback mechanism lacks detail | PARTIALLY ADDRESSED | `docs/guides/frontend/HTML5_RUNTIME_ROLLBACK_RUNBOOK.md` now provides Desktop-only rollback scope, owner role, trigger conditions, manual alert signals, rollback steps, and a validation record template. `3.3.3` remains open because there is still no real monitoring/alerting loop or executed rollback validation record. |
| Low 5: unmeasurable business metrics | PARTIALLY ADDRESSED | Several business metrics are now explicitly de-scoped as post-launch or cross-cutting governance metrics, but remaining non-de-scoped success metrics still require external measurement or separate validation before closure. |

Current validation after disposition updates:

- `openspec validate implement-html5-migration-experience-optimization --strict`: pass.
- `git diff --check -- openspec/changes/implement-html5-migration-experience-optimization/tasks.md ...`: no output in the latest checked batch.
- `openspec list`: `implement-html5-migration-experience-optimization 55/111 tasks`.

## Disposition Update - 2026-05-11

This section preserves the 2026-05-08 review and 2026-05-10 disposition as historical snapshots. The current repo-truth has moved forward again, so counts and examples in the original review must not be read as live status.

Current status snapshot:

- `openspec list`: `implement-html5-migration-experience-optimization 62/111 tasks`.
- `openspec validate implement-html5-migration-experience-optimization --strict`: pass.
- The current product scope remains **Desktop-only**.
- `optimize-data-source-v2` remains out of scope for repo-local work; this review concerns only `implement-html5-migration-experience-optimization`.

Additional disposition since 2026-05-10:

| Area | Status | Current Evidence |
|------|--------|------------------|
| Manifest asset drift | CLOSED FOR DESKTOP-ONLY | `2.1.2` is now closed as Desktop-only manifest asset consistency: current manifest references existing core icons only; mobile screenshots, splash screens, and shortcuts are not part of the current closed scope. |
| IndexedDB browser persistence | CLOSED FOR CURRENT V1 SURFACE | `3.2.3` is now closed for Desktop Chromium `MyStocksDB` version `1` schema bootstrap and close/reopen persistence. This does not cover future schema upgrades, cross-browser persistence, mobile, or production data migration. |
| Server PWA support | CLOSED FOR REPO-LOCAL PREVIEW | `3.3.1` is now closed for repo-local production preview static asset support (`/`, `/manifest.json`, `/sw.js`, `/offline.html`, and history fallback). This does not mean production deployment, HTTPS/CDN/Nginx configuration, or release owner sign-off is complete. |
| Push notifications | STILL OPEN | `2.5.1-2.5.5` remain unchecked: service worker has push/click handlers, but there is no browser permission/subscription flow, no backend Web Push subscribe/unsubscribe route, and no active settings form. |
| Accessibility | STILL OPEN | `2.8.1-2.8.5` remain unchecked: local ARIA/semantic/keyboard surfaces and axe smoke exist, but no full semantic audit matrix, comprehensive ARIA inventory, keyboard-only E2E, screen reader acceptance, WAVE, or WCAG AA closure exists. |
| Menu + PWA integration | STILL OPEN | `3.1.1` remains unchecked: service-worker-controlled online `/dashboard -> /market/realtime` evidence exists, but the seven-domain offline menu matrix is not closed. |
| Workers + IndexedDB data flow | STILL OPEN | `3.1.2` remains unchecked: IndexedDB and Worker API probes exist, but there is no real Worker + IndexedDB business dataflow; `workers-manager.ts` remains a façade/placeholder. |
| Web Worker performance | STILL OPEN | `3.2.4` remains unchecked: production preview can reach the worker asset, but worker protocol asset/orchestration remains insufficient for a real same-dataset main-thread vs worker benchmark. |
| Rollout / rollback / training execution | STILL OPEN | `3.3.2`, `3.3.3`, and `3.4.4` remain unchecked because templates and runbooks exist, but no real rollout record, monitoring/alerting loop, rollback drill, release owner sign-off, or training execution record exists. |

Guide alignment completed on 2026-05-11:

- HTML5 runtime guides now use the current Desktop-only manifest boundary: existing core icons are referenced; mobile screenshots/splash screens/shortcuts are not promised.
- Guides no longer use fixed old Chromium counts such as `295/295`; they require reporting actual command, browser project, and case counts.
- Web Workers are described as worker files / protocol source / manager façade unless a later task proves real orchestration and performance benefit.
- `controllerchange` behavior is documented as update-only reload when the page already had a controller; first install / first control does not force-refresh the active page.
