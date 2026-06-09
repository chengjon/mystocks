# ArtDeco Route Grammar Closeout Checklist

Date: 2026-05-30
OpenSpec change: `standardize-artdeco-route-grammar`
Primary guide: `docs/guides/web/ARTDECO_COMPONENT_GUIDE.md` §8

## 1. Purpose

This checklist closes the route-grammar pilot line by converting repeated page work into a stable review gate. It is a governance artifact, not a shared component implementation plan.

The checklist applies to future ArtDeco critique, shape, craft, audit, or polish work on canonical routed pages under `web/frontend/src/views/<domain>/`.

## 2. Completed Pilot Evidence

| Pilot | Route | Evidence report |
|---|---|---|
| `web/frontend/src/views/risk/Alerts.vue` | `/risk/alerts` | `docs/reports/tasks/2026-05-29-artdeco-risk-alerts-hook-alignment-report.md` |
| `web/frontend/src/views/trade/Reconciliation.vue` | `/trade/reconciliation` | `docs/reports/tasks/2026-05-29-artdeco-trade-reconciliation-hook-alignment-report.md` |
| `web/frontend/src/views/market/Realtime.vue` | `/market/realtime` | `docs/reports/tasks/2026-05-30-artdeco-market-realtime-hook-alignment-report.md` |
| `web/frontend/src/views/trade/Execution.vue` | `/trade/execution` | `docs/reports/tasks/2026-05-30-artdeco-trade-execution-hook-alignment-report.md` |
| `web/frontend/src/views/trade/Center.vue` | `/trade/positions` | `docs/reports/tasks/2026-05-30-artdeco-trade-positions-hook-alignment-report.md` |
| `web/frontend/src/views/ai/Sentiment.vue` | `/ai/sentiment` | `docs/reports/tasks/2026-05-30-artdeco-ai-sentiment-hook-alignment-report.md` |
| `web/frontend/src/views/ai/BatchAnalysis.vue` | `/ai/batch` | `docs/reports/tasks/2026-05-30-artdeco-ai-batch-hook-alignment-report.md` |
| `web/frontend/src/views/trade/Portfolio.vue` | `/trade/portfolio` | `docs/reports/tasks/2026-05-30-artdeco-trade-portfolio-hook-alignment-report.md` |

## 3. Route Grammar Checklist

For each future routed page batch, confirm:

- Canonical page path is under `web/frontend/src/views/<domain>/`.
- Compatibility or embedded `web/frontend/src/views/artdeco-pages/**` files are not touched unless explicitly approved.
- The page has a compact operational header.
- The page has a first-level review/control lens when the route has filters, modes, date ranges, segments, account selectors, or query controls.
- The page exposes runtime trust/status: loading, verified, refreshing, stale/degraded, empty, unavailable, or refresh failure where those states apply.
- The primary data surface is identifiable by route-level hook, not by nested shared component internals.
- Secondary evidence panels remain route-local unless a separate extraction proposal is approved.

## 4. Minimum Hook Checklist

Required for data-heavy routes when the surface exists:

- `*-page`
- `*-header`
- `*-refresh` or `*-primary-action`
- `*-status-strip` or `*-trust-strip`
- `*-control-lens` or `*-review-lens`
- `*-primary-surface`

Conditional hooks:

- `*-runtime-message` or `*-runtime-state` when state copy is visible.
- `*-table`, `*-list`, or `*-row` when E2E needs row-count or row-content assertions.
- `*-segment-<key>` when route-owned segment tabs exist.
- `*-filtered-empty` when a filter can produce a no-match state.
- `*-empty-state`, `*-unavailable-state`, `*-error-state`, and `*-retry` when those visible states/actions exist.

Do not create empty DOM solely to satisfy the checklist. Mark absent surfaces as `not applicable` in the implementation report.

## 5. Report Evidence Checklist

Every route implementation report must include:

- Scope and excluded boundaries.
- GitNexus impact result before editing.
- TDD evidence when behavior or hooks are added: RED command, failure reason, GREEN command, pass count.
- Focused E2E command, browser project, pass/fail/skip count.
- `npx impeccable --json <page>` output.
- ArtDeco token check output for changed page files.
- ESLint and type-check results.
- OpenSpec validation result when an OpenSpec change is in scope.
- PM2 status for `mystocks-backend` and `mystocks-frontend` when frontend runtime work is verified.
- Staged GitNexus detect-changes result before commit.

## 6. Extraction Readiness Gate

Route grammar repetition is now proven, but shared component extraction remains blocked until a separate approved OpenSpec proposal defines:

- Component props, slots, and events.
- Supported runtime state vocabulary.
- Token ownership and class naming.
- Hook naming and migration behavior.
- Route-local responsibilities that must not move into shared components.
- Candidate page migration order.
- Rollback plan.

Shared components must not own API orchestration, route metadata, router config, backend contracts, frontend API clients, financial row semantics, stale snapshot logic, or page-specific fallback copy.
