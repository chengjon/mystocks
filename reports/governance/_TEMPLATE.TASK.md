# TASK

> Governance template. Copy this file to a dated task file under `reports/governance/` and then fill the placeholders.

- Issue Identifier: `<yyyy-mm-dd-scope-topic-owner>`
- Issue Title: `<task title>`
- Objective: `<one-sentence objective>`
- Branch: `<branch-name>`
- Assigned Worker CLI: `<main|worker-name>`
- Tracker State: `<planned|in_progress|verified|merged|archived>`

## Allowed Paths
- `<path-1>`

## Forbidden Paths
- `<path-or-(none)>`

## Acceptance Checks
- `<verification command>`

## OpenSpec
- `<change-id or (none)>`

## Related Plans
- `<plan path or (none)>`

## Owner Decision
- Suggested Owner: `<owner>`
- Final Owner: `<owner>`
- Worker CLI: `<worker>`
- Decision Basis:
  - `<reason-1>`

## Scope Paths
- `<path-1>`

## Structural Debt Disclosure

> Fill this section when the task touches migration closure, duplicate layers, compatibility shims, `*_new.py`, mechanical splits, backup files, temporary entrypoints, or cleanup/removal work.

- canonical_source: `<single source of truth after closure>`
- compatibility_surface: `<compatibility surfaces retained in this batch or N/A>`
- callers_or_consumers: `<known callers/consumers or N/A>`
- verification_command: `<command(s) proving migration/closure success or N/A>`
- exit_condition: `<sunset condition for legacy layer or N/A>`

## Cleanup / Removal Decision

> Fill this section when the task deletes, archives, or proposes keeping a suspicious legacy object.

- code_path_verdict: `<used|unused-but-needs-proof|safe-to-remove|N/A>`
- function_tree_verdict: `<有效|失效但兼容保留|实验/灰度|重复冗余|待判定|N/A>`
- removal_basis: `<why removal is safe or N/A>`
- keep_reason: `<why object must remain or N/A>`

## Temporary / Compatibility Asset Ledger

> Fill this table when the task introduces, retains, or audits temporary layers. Use `introduced_by` = `issue_or_task=<...>; created_at=<...>`.

| path | type | owner | introduced_by | reason | exit_condition | planned_removal_milestone | target_removal_date | current_status |
|---|---|---|---|---|---|---|---|---|
| `<path>` | `<shim / backup / temporary-entry / mechanical-split / other>` | `<owner>` | `<issue_or_task=<task-or-issue>; created_at=<yyyy-mm-dd or unknown>>` | `<reason>` | `<exit condition>` | `<milestone or N/A>` | `<yyyy-mm-dd or N/A>` | `<active / planned-removal / retained / removed>` |

## Metrics Lens

> All core numbers must distinguish measured values from baselines, inference, and targets.

| metric | measured | baseline | inferred | target | source_or_command |
|---|---|---|---|---|---|
| `<metric>` | `<value or N/A>` | `<value or N/A>` | `<value or N/A>` | `<value or N/A>` | `<command/file/date>` |

## Next Steps
- `<next step or (none)>`

## Compatibility Notes
- `<note or (none)>`

## Artifact Links
- `<path or (none)>`
