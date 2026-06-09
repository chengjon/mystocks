# G2.347 Dashboard Cache Helper Source Authorization Preflight

## Metadata

- Date: `2026-06-04`
- Node: `G2.347`
- Mode: dashboard cache helper source authorization preflight / no-source
- `source_edit_authority`: `false`
- Branch: `wip/root-dirty-20260403`
- Evidence head: `2408edaf7`
- Parent: `G2.346 Dashboard Cache Helper Surface Inventory`
- Authorized work: decide whether the dashboard cache helper surface may move to any source node
- Not authorized: source edits, test edits, deletion, consolidation, route changes, GitNexus repair actions that alter source history, or splitting the cluster into one-file confirmation nodes

## Source Edit Statement

No source files were edited by G2.347.

This node writes only this report:

- `docs/reports/worklogs/claude-auto/g2-347-dashboard-cache-helper-source-authorization-preflight-2026-06-04.md`

## Preflight Question

Can the dashboard cache helper surface now be authorized for source work?

The answer for G2.347 is **no**.

## Evidence Reviewed

Local static evidence for the source-facing cluster:

| Surface | Scan status | Lines | Role evidence |
|---|---:|---:|---|
| `web/backend/app/api/dashboard.py` | clean | 436 | active route orchestrator; imports `dashboard_cache`, `dashboard_data_source`, `dashboard_builders`, dashboard models, and `CacheManager` |
| `web/backend/app/api/dashboard_cache.py` | clean | 84 | helper module with `generate_cache_key`, `try_get_cached_dashboard`, and `cache_dashboard_data` |
| `tests/api/file_tests/test_dashboard_api.py` | clean | 409 | dashboard file test surface with cache, bypass, and wrapper coverage |

File-level test coverage relevant to the helper surface:

- `test_cache_management_operations`
- `test_async_cache_operations`
- `test_dashboard_local_cache_wrapper_delegates_to_canonical_async_getter`
- `test_dashboard_summary_bypass_cache_skips_cache_read_and_writes_fresh_data`

GitNexus evidence:

- `get_dashboard_summary` context resolved successfully and showed direct calls to `get_cache_manager`, `try_get_cached_dashboard`, `cache_dashboard_data`, `get_data_source`, and the four dashboard builders.
- `get_dashboard_summary` impact returned `LOW` risk and `impactedCount: 0` for upstream changes.
- `try_get_cached_dashboard` context resolved successfully and showed a single upstream caller: `get_dashboard_summary`.
- `try_get_cached_dashboard` impact returned `LOW` risk, `direct: 1`, and `affected_processes` anchored on `get_dashboard_summary`.
- `cache_dashboard_data` context resolved successfully and showed the same single upstream caller: `get_dashboard_summary`.
- `cache_dashboard_data` impact returned `LOW` risk, `direct: 1`, and the same `get_dashboard_summary` process anchor.

GitNexus freshness caveat:

- The graph still reports `stale: true` with `current_commit_differs_from_indexed_commit`.
- The index is usable for staged-diff style inspection, but it is not yet fresh enough to treat as a clean source-authorization gate.
- That is acceptable for a no-source preflight report, but it is not sufficient to authorize a source node.

## Decision Table

| Surface | Current role | Preflight reading | Authorization decision | Next condition |
|---|---|---|---|---|
| `web/backend/app/api/dashboard.py` | Route orchestrator and cache-wrapper entrypoint | Single dashboard route owns the call chain into cache helper, data source, and builders. The helper boundary is coherent, but no defect or explicit source requirement has been established. | Do not authorize source work from this node. | If source work is later requested, the next source node must include route behavior and response-contract checks together with a fresh GitNexus index. |
| `web/backend/app/api/dashboard_cache.py` | Small dashboard-local cache helper | The file is a narrow helper surface with one caller. Low blast radius does not itself justify source work. | Do not authorize source work from this node. | Any future source node must treat this file and `dashboard.py` together; do not split into one-file confirmation nodes. |
| `tests/api/file_tests/test_dashboard_api.py` | Existing coverage surface | The file already covers cache operations, async cache operations, wrapper delegation, and bypass behavior. That is evidence of existing coverage, not a reason to edit source now. | Do not authorize source work from this node. | If behavior changes later, tests may be updated in the same bounded source node, but not before a source need exists. |
| `web/backend/app/api/dashboard_data_source.py` | Adjacent data-source surface | It is adjacent to the dashboard route, but it is not the small cache-helper surface and it carries broader `get_data_source` usage. | Out of scope for this authorization preflight. | If source work is later needed, this requires a separate data-source boundary decision. |
| `web/backend/app/api/dashboard_builders.py` | Response builder surface | Builder helpers are part of the route path, but this preflight did not establish any builder defect or shape change requirement. | Out of scope for this authorization preflight. | Consider only if a later route-contract node requires response-shape changes. |
| `web/backend/app/models/dashboard.py` | Contract/model surface | Model contracts are adjacent to the route, but this preflight did not find a contract drift requiring source action. | Out of scope for this authorization preflight. | Consider only in a dedicated schema/contract node. |
| `web/backend/app/api/governance_dashboard.py` | Separate dashboard-named governance route | Dirty in the worktree before this node, but unrelated to the dashboard cache helper cluster. It must not be used as authorization evidence for the dashboard cache helper. | Explicitly excluded from source authorization here. | Keep separate governance route handling out of the dashboard cache helper lane. |

## Authorization Decision

G2.347 does **not** authorize any source node for the dashboard cache helper surface.

Reasoning:

1. G2.346 already fixed the cluster boundary and explicitly said there is no immediate source node authorized.
2. Local static evidence shows a coherent but small route-local helper surface: one caller, one helper module, existing dashboard file tests, and no new defect signal.
3. GitNexus impact for `get_dashboard_summary`, `try_get_cached_dashboard`, and `cache_dashboard_data` is low, but the index still reports stale status. That is not a sufficient gate to start source authorization.
4. The presence of existing coverage means the next source node, if any, must be justified by an actual behavioral change request or defect, not by the mere existence of the cluster.

## Resulting Gate State

- `source_edit_authority=false` remains in force.
- No dashboard cache helper source node is opened by G2.347.
- No deletion, consolidation, or route rewrite is authorized.
- No test edit is authorized from this preflight.

## Recommended Next Gate

Continue the remaining cache modernization queue with the next no-source inventory node:

`G2.348 cache API route cluster inventory / no-source`

Required properties:

- `source_edit_authority=false`
- inventory `web/backend/app/api/cache.py` and split cache route helpers together
- keep route/helper ownership and response-contract behavior in one decision table
- do not treat the dashboard cache helper cluster as merged into the cache API route cluster
- do not perform source edits during inventory
