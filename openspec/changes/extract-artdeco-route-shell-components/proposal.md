# Change: Extract ArtDeco Route Shell Components

## Why

The `standardize-artdeco-route-grammar` line proved the same ArtDeco route grammar across eight canonical routed pages:

- `/risk/alerts`
- `/trade/reconciliation`
- `/market/realtime`
- `/trade/execution`
- `/trade/positions`
- `/ai/sentiment`
- `/ai/batch`
- `/trade/portfolio`

The repeated surfaces are now stable enough to plan extraction, but direct component creation is still too risky without an explicit contract. The page pilots also proved that each route must continue to own API orchestration, stale snapshot behavior, fallback copy, financial row semantics, and route-specific controls.

This change proposes the next phase: define and migrate a small set of route shell components only after route-level contracts, hooks, token behavior, migration order, and rollback are approved.

## What Changes

- Define the approved extraction scope for ArtDeco route shell components.
- Introduce component contracts for route-level shell surfaces such as header, runtime status strip, control lens, data surface shell, and report/evidence wrapper.
- Require migrated pages to keep route-specific API orchestration, data normalization, stale snapshot logic, row semantics, and fallback copy route-local.
- Require each migrated page to keep or map its route-level E2E hooks.
- Require migration in small route slices with focused E2E, ArtDeco token checks, `impeccable --json`, type-check, PM2 status, and GitNexus scope gates.

## Impact

- Affected spec: `artdeco-design-governance`
- Depends on: completed closeout of `standardize-artdeco-route-grammar`
- Candidate source evidence: `docs/reports/tasks/2026-05-30-artdeco-route-grammar-closeout-checklist.md`
- Candidate pages: the eight route grammar pilots listed above
- No router changes are proposed.
- No backend API or OpenAPI contract changes are proposed.
- No frontend API client changes are proposed.
- No `web/frontend/src/views/artdeco-pages/**` migration is proposed.

## Non-Goals

- Do not implement shared components during proposal creation.
- Do not migrate all pages in one batch.
- Do not centralize API calls, stale snapshot orchestration, fallback copy, financial row semantics, route metadata, or router behavior.
- Do not replace Element Plus, ArtDeco primitives, Pinia stores, or route-local composables.
- Do not treat cosmetic similarity alone as sufficient evidence for extraction.
