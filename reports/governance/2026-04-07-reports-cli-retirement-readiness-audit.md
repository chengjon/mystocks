# Reports CLI Retirement Readiness Audit (2026-04-07)

## Scope

- target:
  - `reports/cli/`
- goal:
  - complete the required pre-deletion two-layer judgment for the retained `reports/cli` slice
  - determine whether the directory is currently retirement-ready
- non-goal:
  - do not delete `reports/cli`
  - do not move `docs/reports/cli_reports/`
  - do not rewrite unrelated report indexes in this audit

## Measured Inputs

Commands used:

```bash
find reports/cli -maxdepth 3 -type f | sort

rg -n "reports/cli/" .
rg -n "docs/reports/cli_reports|reports/cli_reports|cli_reports/" .

find docs/reports/cli_reports -maxdepth 2 -type f | sort

sed -n '1,220p' docs/reports/cli_reports/INDEX.md
sed -n '35,60p' docs/api/task_plan.md
sed -n '965,990p' tests/unit/scripts/test_repository_hygiene_paths.py
sed -n '350,380p' docs/reports/INDEX.md
sed -n '1058,1076p' docs/INDEX.md

gitnexus_impact({
  target: "reports/cli/INDEX.md",
  direction: "upstream",
  includeTests: true,
  maxDepth: 3,
  minConfidence: 0.7
})
```

Metric stance for this audit:

- measured:
  - current tracked files under `reports/cli/`
  - current text references to `reports/cli/`
  - current text references to `docs/reports/cli_reports/` and `cli_reports/`
  - current tracked files under `docs/reports/cli_reports/`
  - current GitNexus upstream impact result for `reports/cli/INDEX.md`
- historical baseline:
  - [2026-04-07-reports-entrypoint-round2-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-entrypoint-round2-audit.md)
- inferred:
  - function-tree classification and deletion readiness verdict in later sections
- target:
  - `N/A`

## Current Measured State

Measured on `2026-04-07`:

- `reports/cli/` contains exactly `1` tracked file:
  - `INDEX.md`
- `docs/reports/cli_reports/` contains `6` tracked files:
  - `CLI_2_URGENT_FIX_PRIORITY.md`
  - `CLI_2_WORK_GUIDANCE.md`
  - `CLI_2_WORK_GUIDANCE_UPDATED.md`
  - `CLI_3_FRONTEND_PROGRESS.md`
  - `INDEX.md`
  - `frontend_access_issue_20260117.md`

Measured direct text references to `reports/cli/` include:

- [docs/api/task_plan.md](/opt/claude/mystocks_spec/docs/api/task_plan.md):45
- [reports/governance/2026-04-07-reports-entrypoint-round2-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-entrypoint-round2-audit.md):55
- [reports/governance/2026-04-07-reports-entrypoint-round2-audit.md](/opt/claude/mystocks_spec/reports/governance/2026-04-07-reports-entrypoint-round2-audit.md):228
- [docs/reports/cleanup/directory-organization/legacy/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md](/opt/claude/mystocks_spec/docs/reports/cleanup/directory-organization/legacy/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md):513
- [docs/reports/cleanup/directory-organization/legacy/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md](/opt/claude/mystocks_spec/docs/reports/cleanup/directory-organization/legacy/DIRECTORY_ORGANIZATION_PLAN_OPTIMIZED.md):882

Measured direct text references to `docs/reports/cli_reports/` or `cli_reports/` include:

- [tests/unit/scripts/test_repository_hygiene_paths.py](/opt/claude/mystocks_spec/tests/unit/scripts/test_repository_hygiene_paths.py):977
- [tests/unit/scripts/test_repository_hygiene_paths.py](/opt/claude/mystocks_spec/tests/unit/scripts/test_repository_hygiene_paths.py):981
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1064
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1068
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1069
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1070
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1071
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1072
- [docs/INDEX.md](/opt/claude/mystocks_spec/docs/INDEX.md):1073
- [docs/reports/INDEX.md](/opt/claude/mystocks_spec/docs/reports/INDEX.md):361
- [docs/reports/INDEX.md](/opt/claude/mystocks_spec/docs/reports/INDEX.md):364
- [docs/reports/INDEX.md](/opt/claude/mystocks_spec/docs/reports/INDEX.md):367
- [docs/reports/INDEX.md](/opt/claude/mystocks_spec/docs/reports/INDEX.md):370
- [docs/reports/INDEX.md](/opt/claude/mystocks_spec/docs/reports/INDEX.md):2512

Measured GitNexus result for `reports/cli/INDEX.md`:

- upstream impact risk: `LOW`
- impacted graph items: `0`
- affected processes: `0`

## Observed Role Split

Measured file layout and references show a current split:

- `reports/cli/`
  - holds a governance-grade directory entrypoint only
- `docs/reports/cli_reports/`
  - holds the actual historical CLI report payload files that are still linked by docs and read by at least one unit test

This is a measured coexistence pattern. It is not yet a proof that one side is safe to delete.

## Code-Path Verdict

### Verdict

- `code_path_verdict`: `unsafe_to_delete`

### Measured basis

1. `reports/cli/` is still referenced directly in current tracked documentation and governance artifacts.
2. `docs/reports/cli_reports/` remains actively referenced by:
   - repository documentation indexes
   - repository hygiene tests
3. A current task-planning document still states a migration intent:
   - `cli_reports/ -> reports/cli/`

### Interpretation

Deletion cannot be justified by "directory only has one file" or by the low GitNexus graph result.

Reason:

- GitNexus graph impact is helpful for code-graph callers, but this deletion question also depends on documentation, tests, and migration-plan references.
- Those path references still exist in the repo and therefore fail the required code-path safety test.

## Function-Tree Verdict

### Verdict

- `function_tree_verdict`: `pending_classification`

### Reasoning

`reports/cli/` is not cleanly classifiable today as any of the deletion-safe states:

- not clearly `重复冗余`
  - because current governance work deliberately retains it as the `reports/`-layer CLI entrypoint
- not clearly `正式下线`
  - because no approved exit condition or cutover report declares the slice retired
- not clearly `有效主真相源`
  - because the actual CLI payload files still live under `docs/reports/cli_reports/`

So the current function-tree state is:

- migration-tail placeholder with unresolved final ownership
- therefore `pending_classification`

## Retirement Readiness Verdict

### Final verdict

- `reports/cli/` is **not retirement-ready** on `2026-04-07`

### Why

Deletion requires both:

- code-path safe removal
- function-tree state explicitly equal to `重复冗余` or formal offline state

Current state satisfies neither requirement.

## Required Exit Conditions Before Any Future Deletion

Before a future deletion proposal can be considered, all of the following must be completed:

1. Decide the canonical home for retained CLI report artifacts.
   - either keep `docs/reports/cli_reports/` as truth
   - or complete a real cutover into `reports/cli/`
2. Update all direct references so only the chosen canonical path remains.
   - docs indexes
   - tests
   - cleanup or migration planning docs that are still treated as active references
3. Record the migration closure explicitly.
   - target truth source
   - retained compatibility surface
   - verification command set
   - old-path exit condition
4. Re-run the two-layer deletion judgment after the cutover.
5. If deletion is later proposed, cite the exact authorization registry path in that proposal or closeout:
   - `governance/deletion-evidence.yaml`
   - or emergency-only `governance/waivers/deletion-evidence-waivers.yaml`

## Explicit Non-Recommendation

This audit does **not** recommend:

- deleting `reports/cli/` now
- deleting `docs/reports/cli_reports/` now
- using the low GitNexus graph impact result as sufficient deletion evidence
- treating a one-file directory as automatically deletion-safe
