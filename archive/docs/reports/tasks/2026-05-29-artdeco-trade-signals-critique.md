# ArtDeco Critique: `trade/Signals.vue`

> Date: 2026-05-29
> Command intent: `$impeccable critique web/frontend/src/views/trade/Signals.vue`
> Target route: `/trade/signals`
> Target component: `web/frontend/src/views/trade/Signals.vue`
> Scope: critique only. No route changes, no API contract changes, no shared component extraction, and no Vue source edits in this batch.

## 1. Scope And Method

This critique reviews the current implementation of the active Web ArtDeco route `trade/Signals.vue`.

The file was already dirty before this critique, so this report treats the current working-tree version as the reviewed state and does not attempt to revert or normalize it.

Review inputs:

- static structure scan of `web/frontend/src/views/trade/Signals.vue`
- router ownership check in `web/frontend/src/router/index.ts`
- existing E2E selector and route evidence under `web/frontend/tests/e2e/**`
- deterministic scan: `npx impeccable --json src/views/trade/Signals.vue`
- ArtDeco token check: `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue`
- prior ArtDeco pilot conclusions from Realtime, Risk Alerts, and Trade Positions

## 2. Route And Ownership

Route evidence:

| Route | Route name | Component | Notes |
|---|---|---|---|
| `/trade/signals` | `trade-signals` | `@/views/trade/Signals.vue` | Active trade route |

Router excerpt:

```text
path: 'signals'
name: 'trade-signals'
component: () => import('@/views/trade/Signals.vue')
meta: { title: '信号监控', requiresAuth: true }
```

Related route/API context:

- `/watchlist/signals` and `/strategy/signals` also consume `/api/v1/trade/signals`.
- Existing E2E coverage includes `Trade-Signals` cases in `phase3-mainline-matrix.spec.ts`.
- `trade/Signals.vue` itself imports:
  - `ArtDecoTradingSignals` from `views/artdeco-pages/trading-tabs/`
  - `ArtDecoTradingSignalsControls` from `views/artdeco-pages/components/`

Ownership verdict:

- The page is a canonical routed page under `views/trade/`.
- It currently depends on ArtDeco workbench / compatibility-era internals.
- This is acceptable as existing implementation reality, but it should not be treated as a clean reusable-component boundary.

## 3. Current Implementation Signals

| Signal | Count / State | Interpretation |
|---|---:|---|
| Lines | 711 | Large route-level page; enough complexity to hide state and ownership drift |
| `ArtDeco` references | 27 | Uses ArtDeco vocabulary heavily |
| `data-test` references | 0 | Weak route-level verification surface compared with newer pilots |
| Runtime references | 5 | Runtime state exists, but is not a first-class strip |
| Status references | 7 | Status is present through `ArtDecoHeader`, not a full operational status band |
| Loading references | 6 | Loading is present through button and `v-loading` |
| Error references | 27 | Error/stale behavior is significant and should be more visible |
| Stale references | 8 | Stale snapshot handling exists |
| Segment references | 0 | Filter behavior exists, but does not use the newer segment/review-lens grammar |
| Control references | 3 | Controls are delegated to a workbench component |
| Table references | 5 | Data surface is delegated rather than owned by the route |
| `@media` rules | 2 | Conflicts with current desktop-only ArtDeco constraint |
| `title=` bindings | 5 | These are component title props, not proven native tooltip debt |
| Raw hex / `rgb()` / `rgba()` | 0 | Good touched-style token discipline |
| `border-left` accent | 0 | No side-stripe accent issue found |
| Gradient text | 0 | No gradient-text issue found |
| Layout width animation | 0 | No width-transition issue found |

Automated checks:

```text
npx impeccable --json src/views/trade/Signals.vue
[]
```

```text
node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue
ArtDeco Token Validation Passed.
```

## 4. Design Health Score

| Heuristic | Score | Rationale |
|---|---:|---|
| Visibility of system status | 3/5 | Header status, `DATA`, `REQ_ID`, loading, stale, and error handling exist; they are split across hero/meta/runtime text instead of a scannable trust strip |
| Match to user workflow | 3/5 | The page focuses on signal review and execution, but quality/history panels are secondary placeholders and compete with the live signal list |
| User control and freedom | 3/5 | Filters and refresh exist; no route-local segment affordance or explicit reset/recovery surface is visible |
| Consistency and standards | 2/5 | Canonical routed page depends on `artdeco-pages` internals and still has responsive `@media` rules despite desktop-only constraints |
| Error prevention | 3/5 | Stale snapshot behavior prevents bad refreshes from destroying verified rows; execution actions still need stronger visible readiness / non-readiness hierarchy |
| Recognition over recall | 3/5 | Labels are domain-specific, but English metadata (`DATA`, `REQ_ID`, `signal review route`) mixes with Chinese operational copy |
| Flexibility and efficiency | 3/5 | Embedded mode exists and list filtering works; the route lacks the newer pilot grammar for dense triage |
| Aesthetic and minimalist design | 3/5 | Token discipline is strong; page remains somewhat card-heavy and repeats summary/analysis panels around the primary data surface |
| Error recovery | 3/5 | First-load failure and stale refresh states exist; recovery is not promoted into a dedicated state strip |
| Help and documentation | 2/5 | Confidence, unverified quality, strategy source, and execution readiness are present but not explained as a coherent signal trust model |

Total: **28/50**

Verdict: good engineering foundation with clear route value, but not yet aligned with the newer ArtDeco operational-page grammar proven by Trade Positions.

## 5. What Works

1. The route is not generic or marketing-like.
   It speaks in real trade-signal terms: buy, sell, hold, confidence, strategy source, execution readiness, stale snapshot, request ID, and unverified quality.

2. Runtime truth is already modeled in code.
   `hasVerifiedSignalSnapshot`, `lastVerifiedRequestId`, `lastVerifiedProcessTime`, `staleError`, `routeError`, and `dataSource` are valuable foundations.

3. Token discipline is strong.
   The deterministic token check passes, and the file has no raw hex colors or `rgb()` / `rgba()` usage in the scanned source.

4. E2E coverage already protects important honesty rules.
   Existing tests check mocked rows, pending provenance, first-load failure, stale refresh failure, and absence of fake quality metrics.

5. The page already avoids several known design anti-patterns.
   No side-stripe accents, gradient text, raw-color styling, or width-transition layout animation were found.

## 6. Main Issues

### P0: Desktop Constraint Drift

The file contains two `@media` rules:

```text
@media (width <= 75rem)
@media (width <= 48rem)
```

Current project constraints define the Web product as desktop-only with minimum 1280x720 and no mobile/tablet adaptation rules.

Impact:

- the page still carries responsive behavior that does not match current ArtDeco governance
- later shared extraction could accidentally normalize mobile-responsive patterns into the design system
- visual QA can drift between desktop route behavior and legacy responsive rules

Recommended handling:

- do not fix in critique
- flag for any future shape/craft brief
- remove or replace only after approval, preserving stable desktop grid behavior

### P1: Runtime State Is Present But Not Operationally Prominent

Runtime information is split across:

- hero meta: `DATA`, `REQ_ID`
- `ArtDecoHeader` status text
- content meta: `FILTER`
- a single `runtime-message` paragraph
- loading overlay on the list section

This works technically, but it is harder to scan than the pattern proven in the Trade Positions pilot:

```text
header -> review lens -> runtime status strip -> primary data surface
```

Recommended future direction:

- introduce a route-level signal trust strip in a shape brief
- include verified, syncing, stale, degraded, empty, and unavailable states
- keep the signal list dominant
- keep request ID and last verified process time close to the trust strip

### P1: No Stable Route-Level `data-test` Surface

The page currently has `0` `data-test` references.

Existing E2E tests use visible text and broad `.signals-view` selectors. That is acceptable for legacy coverage, but weaker than the later page-pilot standard.

Recommended future route-local hooks:

- page root
- header/status band
- filter controls
- runtime trust strip
- signal list
- signal rows
- empty state
- first-load error state
- stale refresh state
- retry / refresh action

This should be added only in an approved craft slice.

### P1: Canonical Route Depends On Workbench Internals

The page imports:

```text
@/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue
@/views/artdeco-pages/components/ArtDecoTradingSignalsControls.vue
```

This is a practical existing dependency, but it blurs the current ArtDeco boundary:

- `views/trade/*.vue` is the active canonical route layer
- `views/artdeco-pages/**` is a workbench / compatibility layer
- `src/components/artdeco/**` is the sustainable reusable asset layer

Recommended handling:

- do not extract or move components during critique
- document this as ownership debt
- if future extraction is approved, first decide whether these components become sustainable ArtDeco assets or remain compatibility-layer consumers

### P2: Primary Data Surface Competes With Secondary Placeholder Panels

The page includes:

- overview grid
- signal list
- signal quality analysis
- signal type distribution
- signal history tracking

The copy is honest about missing execution result / quality statistics, but the secondary placeholder panels still occupy meaningful visual weight.

Recommended future direction:

- make the live signal list the dominant surface
- keep quality/history panels visibly secondary or collapsed until verified execution data exists
- avoid presenting placeholder analysis as equally important to real-time signal rows

### P2: Mixed English And Chinese Operational Copy

Examples:

- `signal execution desk`
- `DATA`
- `REQ_ID`
- `signal review route`
- Chinese page title, subtitles, and state messages

This is not a blocker, but the prior pilots moved toward Chinese operational copy for user-facing surfaces.

Recommended future direction:

- keep technical identifiers like request ID, but localize surrounding labels
- use terms like `数据状态`, `请求编号`, `信号筛选`, `实时交易信号`
- reserve English identifiers for debug-like metadata only when they are intentionally operator-facing

## 7. Anti-Patterns Verdict

LLM slop assessment:

- Not obviously AI-generated.
- Domain language is specific.
- State logic is real.
- Fake quality metrics are explicitly suppressed by existing tests.

Design debt assessment:

- The page is closer to a transitional ArtDeco route than a finished pilot.
- The biggest risks are governance and hierarchy, not raw visual styling.
- Future work should be a shape brief, not an immediate polish pass.

Absolute-ban scan:

| Ban | Result |
|---|---|
| Side-stripe border accents | Not found |
| Gradient text | Not found |
| Raw hex/rgb color styling | Not found |
| Layout width animation | Not found |
| Mobile/tablet responsive rules | Found, should be addressed in future approved slice |

## 8. Priority Recommendations

### Recommended Next Step

Create a shape brief before implementation:

```text
$impeccable shape trade signals ArtDeco signal trust desk
```

The brief should define:

- page grammar
- primary data surface priority
- signal trust strip states
- filter/review lens behavior
- secondary panel demotion rules
- route-local E2E hook expectations
- what to do with `artdeco-pages` component ownership debt

### Do Not Do Yet

- do not craft implementation without user approval
- do not edit router metadata
- do not change `/api/v1/trade/signals`
- do not extract `ArtDecoTradingSignals` or controls into shared components
- do not remove `@media` rules without an approved shape/craft scope

## 9. Suggested Shape Brief Scope

If approved later, the smallest useful craft scope would be:

1. Route header/status band refinement.
2. Signal trust strip for verified / syncing / stale / unavailable states.
3. First-level signal review lens: all / buy / sell / hold / high confidence.
4. Keep `ArtDecoTradingSignals` as-is unless explicitly approved otherwise.
5. Demote placeholder quality/history panels below the live signal list.
6. Add route-local `data-test` hooks.
7. Remove desktop-incompatible responsive rules only if the approved scope includes layout cleanup.

This would keep implementation local to the routed page and its route tests.

## 10. Verification

Completed for this critique-only batch:

- `npx impeccable --json src/views/trade/Signals.vue`: `[]`
- `node scripts/check-artdeco-tokens.js --target-file src/views/trade/Signals.vue`: `ArtDeco Token Validation Passed.`
- Static route check: `/trade/signals` maps to `@/views/trade/Signals.vue`
- Existing E2E evidence found for `Trade-Signals` in `phase3-mainline-matrix.spec.ts`

Not run:

- frontend type-check
- Playwright E2E
- PM2 status checks

Reason: this batch is critique-only documentation and does not modify Vue, TypeScript, SCSS, routes, APIs, tests, or shared components.
