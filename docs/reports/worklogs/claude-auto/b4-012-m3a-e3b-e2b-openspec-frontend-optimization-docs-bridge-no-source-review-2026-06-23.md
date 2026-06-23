# B4.012-M3a-E3b-E2b OpenSpec Frontend Optimization Docs Bridge No-Source Review

## Scope

- Parent: `b4-012-m3a-e3b-e2-web-frontend-guides-family-split`
- Proposed node: `b4-012-m3a-e3b-e2b-openspec-frontend-optimization-docs-bridge`
- Source/OpenSpec edits authorized: no

## Trigger

After closing the completion report cleanup-index bridge, the web-guide focused
repository-hygiene residuals still include OpenSpec file-read failures:

```text
tests/unit/scripts/test_repository_hygiene_paths.py::test_selected_web_guides_are_converged_under_guides_web_family
tests/unit/scripts/test_repository_hygiene_paths.py::test_additional_web_runtime_and_planning_guides_are_converged_under_guides_web_family

FileNotFoundError:
openspec/changes/frontend-optimization-six-phase/tasks.md
openspec/changes/frontend-optimization-six-phase/implementation-plan.md
```

## Findings

- `openspec/changes/frontend-optimization-six-phase/` is absent.
- `tests/changes/frontend-optimization-six-phase/` exists and contains:
  - `README.md`
  - `proposal.md`
  - `design.md`
  - `tasks.md`
  - `implementation-plan.md`
- The test mirror documents already reference canonical web-guide paths:
  - `docs/guides/web/WEB_FRAMEWORK_INCREMENTAL_OPTIMIZATION_PLAN.md`
  - `docs/guides/web/WEB_ROUTER_MIGRATION_RECORD.md`
- The test mirror documents do not contain retired `docs/frontend/` or
  `docs/frontend/KLINE_COMPONENT_GUIDE.md` references in the checked files.

## OpenSpec Validation Risk

Directly restoring only the five markdown documents into
`openspec/changes/frontend-optimization-six-phase/` would create an invalid
active OpenSpec change:

```text
openspec validate frontend-optimization-six-phase --strict --no-interactive
=> Change must have at least one delta. No deltas found.
```

A simulated safe restore that also adds
`openspec/changes/frontend-optimization-six-phase/specs/documentation-governance/spec.md`
with a minimal documentation-governance delta validates successfully:

```text
Change 'frontend-optimization-six-phase' is valid
```

## Recommended Authorization

Allowed paths:

- `openspec/changes/frontend-optimization-six-phase/README.md`
- `openspec/changes/frontend-optimization-six-phase/proposal.md`
- `openspec/changes/frontend-optimization-six-phase/design.md`
- `openspec/changes/frontend-optimization-six-phase/tasks.md`
- `openspec/changes/frontend-optimization-six-phase/implementation-plan.md`
- `openspec/changes/frontend-optimization-six-phase/specs/documentation-governance/spec.md`
- `docs/reports/worklogs/claude-auto/`

Allowed actions:

- Restore the five active OpenSpec change documents from the existing
  `tests/changes/frontend-optimization-six-phase/` mirror.
- Add the minimal `documentation-governance` OpenSpec delta required for strict
  validation.
- Do not alter the mirrored `tests/changes/` files.

## Non-Goals

- No source/runtime edits.
- No tests edits.
- No `docs/guides/` edits.
- No `docs/reports/completion_reports/` edits.
- No root agent-rule edits.
- No external dirty file staging.
- No broad OpenSpec archive migration.

## Expected Validation

- `openspec validate frontend-optimization-six-phase --strict --no-interactive`
- Focused repository-hygiene tests:
  - `test_selected_web_guides_are_converged_under_guides_web_family`
  - `test_additional_web_runtime_and_planning_guides_are_converged_under_guides_web_family`
- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus verify-staged and detect-changes, expected risk `low`
- OPENDOG verification, expected fresh with no blockers
