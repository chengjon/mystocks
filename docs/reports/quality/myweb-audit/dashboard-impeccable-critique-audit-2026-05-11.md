# Dashboard Impeccable Critique and Audit

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

> Date: 2026-05-11
> Scope: `/dashboard` canonical Vue page
> Canonical component: `web/frontend/src/views/artdeco-pages/ArtDecoDashboard.vue`
> Related component: `web/frontend/src/views/artdeco-pages/components/DashboardMarketPanorama.vue`
> Style source: `web/frontend/src/views/artdeco-pages/styles/ArtDecoDashboard.scss`

IMPECCABLE_PREFLIGHT: context=pass product=pass command_reference=pass shape=not_required image_gate=skipped:critique/audit report only, no visual mutation mutation=open

## Current Status After Repair

This report keeps the original critique/audit findings as the audit trail. The current dashboard status is defined by the later `Repair Follow-up` and `Hardening Follow-up` sections.

As of the latest dashboard-only pass on 2026-05-11:

- Original hierarchy, alert triage, passive-hover affordance, title recognition, quick navigation weight, and decorative top-rule findings are fixed.
- The remaining live keyboard verification item is covered by an automated Chromium E2E test for both dashboard tablists.
- The current dashboard E2E grep passes at `16/16` on Chromium.
- The broad `npm run test:e2e:selectors` failure remains a repository-wide existing selector-policy debt, not a dashboard regression from this repair line.

## Method

- Loaded `impeccable` context from `PRODUCT.md` and `DESIGN.md`; register is `product`.
- Loaded command references: `reference/product.md`, `reference/critique.md`, `reference/audit.md`.
- Reviewed dashboard Vue and SCSS source directly.
- Ran deterministic detector:

```bash
cd web/frontend
npm_config_cache=/tmp/npm-cache npx impeccable --json --fast src/views/artdeco-pages/ArtDecoDashboard.vue src/views/artdeco-pages/components/DashboardMarketPanorama.vue
```

Result: `[]`. The detector reported no pattern findings for the two Vue targets.

Browser overlay was not used in this pass. The current request is a report-only critique/audit, and no live visual mutation was requested. Independent sub-agent assessment was also skipped because this Codex session only permits sub-agents when the user explicitly asks for delegation; this report uses a sequential source review fallback.

## Context Fit

Dashboard is a product surface for technically literate A-share quant users on a desktop terminal. The relevant design intent is restrained ArtDeco: dark mode, gold as structural accent, A-share red/green semantics, dense market data, and no decorative treatment that competes with real-time signal reading.

The current dashboard mostly matches that intent. It now exposes request provenance (`DATA`, `REQ`, `TIME`, `SYNC`), keeps degraded states visible, uses accessible chart labels, and avoids global hoverable treatment on the three top informational chart cards. Remaining issues are not blocking defects. They are mostly hierarchy and affordance problems that can still slow expert scanning.

## Critique: Design Health Score

| # | Heuristic | Score | Key Issue |
|---|-----------|-------|-----------|
| 1 | Visibility of System Status | 3 | Request meta and alerts are visible, but alert severity and next action are not strongly triaged. |
| 2 | Match System / Real World | 3 | A-share data language is strong; `QUANTIX` as the page title is less task-recognizable than a dashboard title. |
| 3 | User Control and Freedom | 3 | Collapsible sections and tabs work; pressure-test result reset or rerun state is not obvious from the template. |
| 4 | Consistency and Standards | 3 | ArtDeco tokens and components are consistent; some non-clickable rows still receive hover elevation. |
| 5 | Error Prevention | 3 | Disabled pressure-test state prevents premature execution; stale/degraded states could better separate warning from error. |
| 6 | Recognition Rather Than Recall | 3 | Core panel labels are understandable; quick-nav and dense equal-weight cards require scanning effort. |
| 7 | Flexibility and Efficiency | 3 | Expert density is appropriate; no obvious keyboard shortcuts or route-local command affordances are visible. |
| 8 | Aesthetic and Minimalist Design | 3 | The visual language is distinctive, but repeated cards, glows, and a decorative top rule add noise. |
| 9 | Error Recovery | 3 | Degraded messages keep the shell honest; recovery path or retry ownership is not explicit in alerts. |
| 10 | Help and Documentation | 2 | Domain users need little hand-holding, but local-estimate and degraded-data explanations need clearer operational meaning. |
| **Total** | | **29/40** | **Good, with hierarchy and affordance debt** |

## Critique: Anti-Patterns Verdict

Pass overall. This does not read as generic AI output. It is recognizably a MyStocks ArtDeco trading terminal, not a stock SaaS template.

What keeps it out of generic territory:

- Domain-native labels such as 北向资金, 龙虎榜, 大宗交易, 资金流向持续排名, and A-share red/green semantics.
- Real provenance and degraded-state UI instead of decorative metrics only.
- Compact terminal density and tokenized ArtDeco vocabulary.

Residual anti-pattern risk:

- `ArtDecoDashboard.scss` still uses a decorative gold top rule at lines 37-48. It is tokenized and lightweight, but it is still decoration on a data-critical page.
- Several data rows (`.flow-item`, `.stock-item`, `.indicator-item`, `.monitor-item`) use hover glow/elevation even when the template does not show click handlers. This can imply interactivity.
- The page relies heavily on repeated framed panels. The detector did not flag identical card grids, but the human scan still sees a dense field of similarly weighted cards after the top panorama.

## Critique: Overall Impression

The dashboard now feels operationally credible: status provenance is present, data degradation is visible, and the main market panorama gives the route a strong terminal identity. The biggest opportunity is visual hierarchy. Too many panels ask for equal attention, while the user's actual first decision is likely: market condition, fund-flow pressure, then action or drill-down.

## Critique: What's Working

1. **Operational honesty**: `request-meta-bar` and `dashboard-alerts` expose data state and request identity instead of hiding backend uncertainty.
2. **Accessibility repairs are visible in source**: tablists now use `role="tablist"`, `role="tab"`, `aria-selected`, `aria-controls`, `tabindex`, and labelled panels. Charts pass specific accessible labels.
3. **Product density matches the audience**: this is not simplified for casual investors. Dense panels, numeric alignment, and A-share labels suit a quant terminal.

## Critique: Priority Issues

### [P1] Weak first-read hierarchy after the market panorama

**What**: The dashboard moves quickly from a strong top panorama into many similarly framed panels: heat map, capital heat map, sector radar, pressure test, Dragon-Tiger list, block trading, rankings, stock pool, and quick nav.
**Why it matters**: Expert users can handle density, but equal visual weight slows the first scan during market hours.
**Fix**: Group the page by decision sequence: market pulse, capital confirmation, operational action, then secondary drill-down. Reduce decorative emphasis on lower-priority panels.
**Suggested command**: `$impeccable layout dashboard`

### [P1] Alert states are visible but not operationally triaged

**What**: `dashboardAlerts` and chart state notes surface degraded states, but messages do not clearly separate stale data, partial data, backend failure, retryable state, or local-only estimate.
**Why it matters**: In a trading terminal, "data unavailable" and "using last verified slice" imply different risk. Users need the risk posture at a glance.
**Fix**: Add severity vocabulary and action ownership: stale, degraded, failed, local estimate. Keep it compact and avoid prose-heavy alerts.
**Suggested command**: `$impeccable clarify dashboard`

### [P2] Non-clickable rows still look interactive

**What**: `.flow-item`, `.stock-item`, `.indicator-item`, and `.monitor-item` use hover border/glow/elevation, but the corresponding template rows do not expose click behavior.
**Why it matters**: Hover lift is an affordance. If nothing happens, users learn to distrust the interaction vocabulary.
**Fix**: Reserve hover elevation for clickable rows and links. For passive data rows, use only subtle row tint or no hover treatment.
**Suggested command**: `$impeccable audit dashboard`

### [P2] Page title prioritizes brand over task recognition

**What**: The route header title is `QUANTIX`, with subtitle `实时 洞察 策略 执行`.
**Why it matters**: It is distinctive, but first-time or cross-route users may need a stronger route cue that this is the main dashboard/market overview.
**Fix**: Keep `QUANTIX` as brand identity, but add or substitute a task-recognizable page label such as `市场总览` or `量化驾驶舱` in the header hierarchy.
**Suggested command**: `$impeccable clarify dashboard`

### [P3] Quick navigation may be low-value inside an already navigated app shell

**What**: The bottom `快速导航` card repeats top-level navigation destinations.
**Why it matters**: It consumes a full-width region and competes with actual dashboard data.
**Fix**: Either convert it into a compact command strip for the most common next actions, or demote it below data-first content with less visual weight.
**Suggested command**: `$impeccable distill dashboard`

## Critique: Persona Red Flags

**Power user during market hours**: The user can read data quickly, but equal-weight panels and hover glows on passive rows increase scan cost. The fastest path from market state to drill-down is not yet visually dominant.

**First-time quant user migrating from TongDaXin/Bloomberg-style tools**: Domain terms feel right, but `QUANTIX` as the primary title and local-estimate wording require interpretation. The page should confirm "this is the main market cockpit" faster.

**Risk-conscious operator**: Request IDs and degraded alerts are valuable. The missing piece is severity vocabulary that distinguishes stale, partial, failed, and locally estimated signals.

## Audit: Health Score

| # | Dimension | Score | Key Finding |
|---|-----------|-------|-------------|
| 1 | Accessibility | 3 | Good ARIA/tab/chart-label coverage in source; live keyboard focus behavior still needs browser verification. |
| 2 | Performance | 3 | No `transition: all`; animations are scoped. Chart density and hover glows should be watched under live data. |
| 3 | Responsive Design | 3 | Meets documented desktop-only baseline; there is one <= lg collapse branch but no unsupported mobile ambition. |
| 4 | Theming | 3 | Strong token usage. Remaining decoration uses gradients/glows but through ArtDeco tokens. |
| 5 | Anti-Patterns | 3 | Detector found no issues; human review flags only subtle product-surface affordance and density debt. |
| **Total** | | **15/20** | **Good, address weak dimensions** |

## Audit: Detailed Findings by Severity

### [P1] Alert severity and recovery path are underspecified

- **Location**: `ArtDecoDashboard.vue` lines 19-24, 82, 96, 108, 177; `ArtDecoDashboard.scss` lines 365-375
- **Category**: Accessibility / UX state clarity
- **Impact**: Screen-reader and sighted users can perceive that something changed, but not the operational severity or next step.
- **WCAG/Standard**: Supports status messaging, but could better satisfy understandable status communication.
- **Recommendation**: Encode severity class and terse action copy. Example categories: degraded, stale, failed, local-estimate.
- **Suggested command**: `$impeccable harden dashboard`

### [P2] Passive data rows use interactive hover vocabulary

- **Location**: `ArtDecoDashboard.scss` lines 267-282, 387-403, 531-544, 596-611, 733-747
- **Category**: Anti-Pattern / Interaction affordance
- **Impact**: Hover glow suggests clickability, but passive rows have no declared action.
- **Recommendation**: Remove transform/glow from passive rows, or add explicit clickable behavior with keyboard semantics if drill-down is intended.
- **Suggested command**: `$impeccable audit dashboard`

### [P2] Keyboard focus still needs live verification

- **Location**: `ArtDecoDashboard.vue` lines 159-176 and 202-219; `ArtDecoDashboard.scss` lines 724-731
- **Category**: Accessibility
- **Impact**: Source shows roving `tabindex` and focus-visible styles, but the final behavior depends on `handleFlowTabKeydown` and `handlePoolTabKeydown` runtime handling.
- **Recommendation**: Run an authenticated dashboard keyboard pass: Tab into each tablist, arrow through tabs, verify focus ring and panel update.
- **Suggested command**: `$impeccable harden dashboard`

### [P3] Decorative top rule remains on a data-critical page

- **Location**: `ArtDecoDashboard.scss` lines 37-48
- **Category**: Theming / Anti-Pattern
- **Impact**: It is unlikely to break usability, but it spends attention budget before data appears.
- **Recommendation**: Keep only if dashboard is intended as a brand-forward overview. Otherwise remove or reduce opacity further.
- **Suggested command**: `$impeccable quieter dashboard`

## Audit: Positive Findings

- `transition: all` was not found in the reviewed dashboard files. Transitions are property-scoped.
- `prefers-reduced-motion: reduce` handling exists for key hover/transition elements.
- Informational chart cards use `:hoverable="false"` at the `ArtDecoCard` level.
- Financial numeric values are covered by `font-variant-numeric: tabular-nums`.
- The deterministic `impeccable` scan returned no findings for the two Vue targets.

## Verification Context From Dashboard Repair Line

The following dashboard-specific verification evidence was already recorded in the repair line and is relevant context for this critique/audit:

| Check | Result |
|---|---|
| `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts` | Passed, `23/23`. |
| `npx vitest run src/components/artdeco/base/__tests__/ArtDecoCard.spec.ts` | Passed, `5/5`. |
| `npx vitest run src/api/services/__tests__/dashboardService.spec.ts` | Passed, `8/8`. |
| `npm run type-check` | Passed, `0` type-check errors for the current checked batch. |
| Authenticated dashboard Chromium E2E smoke | Passed, `1/1` for dashboard shell and core cards. |
| PM2 services | Previously confirmed online for `mystocks-backend` and `mystocks-frontend`. |

Additional caveat: a broader local dashboard grep E2E run was observed at `14/15`, with the failure in an uncommitted dashboard capital-flow test expecting a `3日` button. This is not evidence of a committed dashboard regression, but it should be resolved before relying on the broader grep suite as a release gate.

## Recommended Actions

1. **[P1] `$impeccable layout dashboard`**: Rebalance hierarchy after the market panorama so market pulse, capital confirmation, and action panels do not compete equally with secondary panels.
2. **[P1] `$impeccable clarify dashboard`**: Make alert/provenance wording operational: stale, degraded, failed, local estimate, last verified.
3. **[P2] `$impeccable harden dashboard`**: Run keyboard and live-state checks for tablists, alert announcements, disabled pressure-test state, and chart fallback states.
4. **[P2] `$impeccable audit dashboard`**: Remove passive-row hover affordance or convert intended drill-down rows into real keyboard-accessible interactions.
5. **[P3] `$impeccable polish dashboard`**: Final visual pass after hierarchy and state clarity are fixed.

## Conclusion

Dashboard passes the Impeccable audit at a good level: no deterministic detector findings, no obvious AI-slop pattern, and no blocking accessibility or implementation issue was found in this source pass. The remaining work is product craft: stronger first-read hierarchy, clearer operational alert semantics, and stricter separation between passive data rows and interactive affordances.

## Repair Follow-up

Repair date: 2026-05-11

| Report item | Repair status | Evidence |
|---|---|---|
| Weak first-read hierarchy | Fixed in dashboard layout | `ArtDecoDashboard.scss` now uses explicit dashboard grid areas so market heat, capital signal, pressure test, ranking, secondary lists, stock pool, and quick navigation have different visual weight. |
| Alert states not operationally triaged | Fixed in dashboard state model and template | `useArtDecoDashboard.ts` now exposes `dashboardAlertItems` with severity, label, message, and action copy; `ArtDecoDashboard.vue` renders `FAILED` and `DEGRADED` alert vocabulary. |
| Passive rows looked interactive | Fixed in route-local SCSS | Passive `.flow-item`, `.stock-item`, `.indicator-item`, and `.monitor-item` hover glow/elevation rules were removed. |
| Page title favored brand over task recognition | Fixed in header copy | Header title is now `量化驾驶舱`; `QUANTIX` remains in the subtitle as the brand cue. |
| Quick navigation visual weight | Reduced | Quick navigation card no longer opts into `hoverable`; its link items remain interactive. |
| Decorative top rule | Reduced | Dashboard top rule is now a low-opacity token line without gradient or glow. |

Verification after repair:

| Command | Result |
|---|---|
| `git diff --check -- <dashboard repair target files>` | Passed. |
| `npm run lint:artdeco -- --target-file src/views/artdeco-pages/ArtDecoDashboard.vue --target-file src/views/artdeco-pages/styles/ArtDecoDashboard.scss` | Passed. |
| `npm run type-check` | Passed. |
| `npx vitest run tests/unit/components/ArtDecoDashboardLogic.spec.ts src/components/artdeco/base/__tests__/ArtDecoCard.spec.ts src/api/services/__tests__/dashboardService.spec.ts` | Passed, `37/37`. |
| `npm_config_cache=/tmp/npm-cache npx impeccable --json --fast src/views/artdeco-pages/ArtDecoDashboard.vue src/views/artdeco-pages/components/DashboardMarketPanorama.vue` | Passed, detector returned `[]`. |
| `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase1-mainline-matrix.spec.ts -g "dashboard renders shell and core cards"` | Passed, `1/1` Chromium. |
| `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase1-mainline-matrix.spec.ts -g "dashboard"` | Passed, `15/15` Chromium after aligning the capital-flow tab assertion to the actual ARIA role `tab` for `3日`. |
| `npx playwright test --config=tests/visual/config/visual.config.ts tests/visual/pages/dashboard.spec.ts --project=chromium` | Passed, `6/6` dashboard visual checks. |
| `npm run test:e2e:selectors` | Failed on broad pre-existing selector policy debt across multiple E2E files. The dashboard capital-flow fix in this repair line moves the local assertion from role `button` to role `tab`, matching the component semantics. |
| `gitnexus_detect_changes(scope="staged")` after staging only the seven dashboard repair/report files | Low risk, `changed_files=7`, `changed_count=40`, `affected_processes=[]`. |

PM2 service check after repair: `mystocks-backend` and `mystocks-frontend` were both `online`; service URLs remain `http://localhost:8020` and `http://localhost:3020`.

## Hardening Follow-up

Follow-up date: 2026-05-11

| Report item | Repair status | Evidence |
|---|---|---|
| Keyboard focus still needs live verification | Fixed by automated dashboard E2E coverage | Added `dashboard tablists support keyboard focus and selection semantics` in `web/frontend/tests/e2e/phase1-mainline-matrix.spec.ts`. The test covers ArrowRight and ArrowLeft on both the capital-flow tablist (`1日` / `3日` / `5日`) and stock-pool tablist (`自选` / `持仓` / `重点`), including focus movement, wraparound behavior, active tab class, and `aria-selected` updates. |

Verification after hardening:

| Command | Result |
|---|---|
| `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase1-mainline-matrix.spec.ts -g "dashboard tablists support keyboard focus and selection semantics"` | Passed, `1/1` Chromium. |
| `PLAYWRIGHT_EXTERNAL_FRONTEND=1 npx playwright test --config playwright.config.js --project=chromium tests/e2e/phase1-mainline-matrix.spec.ts -g "dashboard"` | Passed, `16/16` Chromium after adding the keyboard tablist coverage. |
| `npm run lint:artdeco -- --target-file src/views/artdeco-pages/ArtDecoDashboard.vue --target-file src/views/artdeco-pages/styles/ArtDecoDashboard.scss` | Passed after the follow-up report consistency pass. |
| `npm_config_cache=/tmp/npm-cache npx impeccable --json --fast src/views/artdeco-pages/ArtDecoDashboard.vue src/views/artdeco-pages/components/DashboardMarketPanorama.vue` | Passed after the follow-up report consistency pass, detector returned `[]`. |
| `gitnexus_detect_changes(scope="staged")` after staging only the hardening E2E file | Low risk, `changed_files=1`, `changed_count=4`, `affected_processes=[]`. |
