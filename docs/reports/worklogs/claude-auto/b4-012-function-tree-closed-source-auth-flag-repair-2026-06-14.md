# B4.012 Function Tree closed source authorization flag repair

## Scope

This package repairs Function Tree governance metadata only.

Target repair:

- `.governance/programs/artdeco-web-design-governance/nodes.json`
  - Node index: `45`
  - Node id: `b4-frontend-shared-ui-component-truth`
  - Current status: `closed`
  - Current invalid field: `source_edits_authorized: true`
  - Required repaired field: `source_edits_authorized: false`

Generated governance/report paths:

- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-012-function-tree-closed-source-auth-flag-repair.yaml`
- `docs/reports/worklogs/claude-auto/b4-012-function-tree-closed-source-auth-flag-repair-2026-06-14.md`

## Current Evidence

- Current observed `HEAD`: `726be97e24`
- `ft-governance validate --root /opt/claude/mystocks_spec` fails with:
  - `ERROR artdeco-web-design-governance.nodes[45] authorizes source edits from non-implementation status: closed`
- Helper validation logic checks `source_edits_authorized === true` outside implementation statuses.
- Program scan found exactly one invalid node with `source_edits_authorized: true` outside implementation statuses:
  - `b4-frontend-shared-ui-component-truth`
- The invalid node is already `closed` and has closeout evidence recorded.
- The node's `allowed_paths` list is historical authorization evidence and is not the validator blocker by itself.
- After repairing node index `45`, `ft-governance validate` exposed one additional active gate projection blocker:
  - `active-gates[6] blocked missing blocker_reason`
  - `active-gates[6] blocked missing unblock_target_state`
- The corresponding program node `b4-012-sync-opencode-model-catalog-restore-authorization` already has both fields. The active-gate projection had `current_blocker` and `next_allowed`, but lacked the validator-required mirror fields.

## Decision

Repair only Function Tree governance metadata required for validation:

- change `source_edits_authorized` from `true` to `false`
- preserve `status: closed`
- preserve `allowed_paths`
- preserve `closeout`
- preserve transition history
- add `blocker_reason` and `unblock_target_state` mirror fields to the blocked active gate for `b4-012-sync-opencode-model-catalog-restore-authorization`
- preserve the existing `current_blocker` and `next_allowed` active-gate fields

This is governance metadata cleanup, not source/test cleanup.

## Explicit Non-Goals

- Do not modify source code, tests, frontend, backend, OpenSpec, or OpenStock.
- Do not delete, rewrite, or clear historical `allowed_paths`.
- Do not change closeout evidence or transition history for `b4-frontend-shared-ui-component-truth`.
- Do not repair unrelated dirty worktree files.
- Do not change the Function Tree helper implementation.

## Implementation Notes

Applied repairs:

- `.governance/programs/artdeco-web-design-governance/nodes.json`
  - `b4-frontend-shared-ui-component-truth`
  - `source_edits_authorized: true -> false`
- `.governance/active-gates.json`
  - `b4-012-sync-opencode-model-catalog-restore-authorization`
  - added `blocker_reason` matching the existing `current_blocker`
  - added `unblock_target_state: "implementation-ready"` matching the node's unblock target

Validation result after repair:

- `ft-governance validate --root /opt/claude/mystocks_spec`: passed
- Function Tree scoped `scope-check --files ...`: passed for the authorized governance/report files

Forward caveat:

- The active-gate mirror-field repair is repo-local. A future helper `sync` may need to preserve `blocker_reason` / `unblock_target_state` in generated active gates whenever a blocked node remains active.

## Commit Gate

- Path-limited `git diff --check` passes for this package.
- Function Tree scoped `scope-check --files ...` passes for this package.
- `ft-governance validate --root /opt/claude/mystocks_spec` passes after the repair, or any remaining blocker is documented with exact node id and field.
- GitNexus staged detect is run after staging the repair.

## Closeout Gate

- The only semantic repair in `nodes.json` is the stale `source_edits_authorized` flag on `b4-frontend-shared-ui-component-truth`.
- Active gates no longer include the repair node after closeout.
- No source/test/OpenSpec/OpenStock paths are modified.
