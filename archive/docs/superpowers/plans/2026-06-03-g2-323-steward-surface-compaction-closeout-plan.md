# G2.323 Steward Surface Compaction Closeout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

## Scope

This is a no-source governance closeout plan for the current steward surface compaction lane.

Current state:

- `G2.321 watchlist DataSourceFactory provider implementation` is accepted/merged by PR `#474`.
- `G2.322 watchlist DataSourceFactory provider closeout / residual refresh` is recorded as `accepted_merged`.
- `G2.323 watchlist DataSourceFactory provider steward surface compaction` is the active no-source gate and is recorded as `started_no_source`.

The next task is to finish G2.323, not to start a source implementation.

## Files

Allowed files for G2.323 closeout:

- `.planning/codebase/steward-tree/branch-register.md`
- `.planning/codebase/steward-tree/current-next-gates.md`
- `.planning/codebase/steward-tree/completed-ledger.md`
- `.planning/codebase/steward-tree/evidence-index.md`
- `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md`
- `.planning/codebase/steward-tree/steward-index.json`
- `.planning/codebase/generated/watchlist-datasourcefactory-provider-steward-surface-compaction-2026-06-03.json`
- `docs/reports/quality/backend-watchlist-datasourcefactory-provider-steward-surface-compaction-2026-06-03.md`
- `governance/mainline/task-cards/g2-323.yaml`

Forbidden files:

- `web/**`
- `src/**`
- `tests/**`
- `docs/api/**`
- `config/**`
- `scripts/**`
- `openspec/**`
- PM2 or runtime state
- unrelated dirty SCSS or out-of-scope prior governance artifacts

## Task 1: Verify G2.323 Current Gate

- [x] Read `.planning/codebase/steward-tree/current-next-gates.md`.
- [x] Confirm the P0 gate is `G2.323 watchlist DataSourceFactory provider steward surface compaction`.
- [x] Confirm G2.322 is recorded as `accepted_merged`.
- [x] Confirm there is no current out-of-scope G2.324/G2.325 path in active/current surfaces.

## Task 2: Verify Machine Evidence

- [x] Parse `.planning/codebase/steward-tree/steward-index.json`.
- [x] Confirm `current_gate.id` is `g2-323-watchlist-datasourcefactory-provider-steward-surface-compaction`.
- [x] Confirm `current_gate.state` is `started_no_source`.
- [x] Confirm `source_edit_authority` is `false`.
- [x] Parse `.planning/codebase/generated/watchlist-datasourcefactory-provider-steward-surface-compaction-2026-06-03.json`.
- [x] Confirm the generated evidence records G2.321, G2.322, and G2.323 parent chain consistently.

## Task 3: Close G2.323 As Accepted Merged

- [x] Update `governance/mainline/task-cards/g2-323.yaml` from `started_no_source` to `accepted_merged`.
- [x] Update `.planning/codebase/steward-tree/steward-index.json` so G2.323 moves from `active_nodes` to `accepted_recent_nodes`.
- [x] Update `.planning/codebase/steward-tree/current-next-gates.md` so G2.323 is no longer an active unfinished gate.
- [x] Update `.planning/codebase/steward-tree/completed-ledger.md` with a compact G2.323 accepted_merged row.
- [x] Update `.planning/codebase/steward-tree/evidence-index.md` to mark the G2.323 JSON/report/task-card as accepted closeout evidence.
- [x] Update `.planning/codebase/steward-tree/tracks/service-lifecycle-di.md` to show G2.323 as accepted_merged and source authorization as still not started.

## Task 4: Select The Next Gate Conservatively

- [x] Do not reuse any previous out-of-scope G2.323/G2.324/G2.325 path as current truth.
- [x] Select the next gate only from accepted G2.322/G2.323 evidence.
- [x] Keep the next gate no-source unless the maintainer explicitly authorizes a source lane.
- [x] If a source lane is later proposed, create a separate authorization node before implementation.
- [x] Record the next gate in `current-next-gates.md`, `steward-index.json`, and the relevant task card only after G2.323 is accepted_merged.

## Task 5: Verify Path Scope

- [x] Parse JSON files with `JSON.parse` or `python -m json.tool`.
- [x] Parse YAML task cards with `python -c "import yaml"`.
- [x] Run a path-limited status check for the G2.323 files.
- [x] Confirm no touched G2.323 path begins with `web/`, `src/`, `tests/`, `docs/api/`, `config/`, `scripts/`, or `openspec/`.
- [x] Explicitly report existing unrelated dirty files as out of scope.

## Completion Criteria

- G2.323 is accepted_merged in task card, current gates, completed ledger, evidence index, service lifecycle track, and steward index.
- Current steward surfaces remain compact and do not rehydrate long historical ledgers.
- The next gate is recorded without authorizing source edits.
- JSON/YAML validation passes.
- No business code, tests, API contract docs, config, scripts, OpenSpec, PM2, or runtime state is touched.
