# Design: ArtDeco Route Grammar Standardization

## Context

The implemented pilots prove a repeated route structure across market, risk, and trade workflows. The structure supports dense desktop financial operations without turning each page into a bespoke visual redesign.

The route grammar is:

```text
compact operational header
-> first-level review/control lens
-> runtime trust/status strip
-> primary data surface
-> secondary evidence panels
```

## Design Principles

1. Route grammar before shared components.
   The standard describes page structure and verification obligations first. Vue extraction is a later implementation choice.

2. Runtime truth before decoration.
   Trust/status surfaces must expose whether data is loading, verified, stale, degraded, empty, unavailable, or failed during refresh.

3. Route-local semantics remain route-local.
   Labels, financial domain copy, API normalization, stale snapshot behavior, and row-level semantics stay in the route unless a later proposal proves a stable contract.

4. Verification hooks are design infrastructure.
   Data-heavy routes need route-level hooks so E2E tests verify user-visible design surfaces instead of nested implementation details.

## Proposed Vocabulary

Runtime trust/status terms:

- `loading` / syncing / pending
- `verified`
- `refreshing`
- `stale`
- `degraded`
- `empty`
- `unavailable`
- `refresh-failed`

Route-level hook roles:

- page
- header
- primary action or refresh action
- review/control lens
- runtime trust/status strip
- primary data surface
- runtime message
- empty state
- error or unavailable state
- retry action when present

## Shared Component Gate

A shared component proposal must define:

- exact props, slots, and events
- supported runtime state vocabulary
- route-local ownership boundaries
- token requirements
- E2E hook naming
- migration order
- rollback behavior

The component must not own API orchestration, route metadata, router configuration, backend contracts, or financial row semantics.
