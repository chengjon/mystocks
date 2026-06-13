# B4.012-M2b-B2-C-A sync OpenCode model catalog restore authorization prep

Date: 2026-06-14
Branch: `wip/root-dirty-20260403`
Mode: `authorization-prepared`
Node: `b4-012-sync-opencode-model-catalog-restore-authorization`
Parent decision: `b4-012-scripts-sync-opencode-model-catalog-disposition-audit`

## Source Decision

This authorization prep is based on:

- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-c-sync-opencode-model-catalog-disposition-no-source-2026-06-14.md`

The no-source disposition found that the dirty `scripts/opencode/sync_opencode_model_catalog.py` diff changes the OpenCode/OMO provider contract from the currently tested `gmn/glm` contract toward `glm/asxs`, removes GMN constants, removes OMO xhigh variant logic, and fails the current paired test suite 4/4.

The decision is to prepare a restore-only implementation boundary. Accepting the ASXS migration requires a separate source/test package.

## Current Evidence

- Current HEAD when prepared: `95d990a6d B4.012-M2b-B2-B-B: close sync OMC test restore`
- Target dirty state: `M scripts/opencode/sync_opencode_model_catalog.py`
- Target diff size at no-source review: `25` insertions, `92` deletions
- Paired test at no-source review: `tests/unit/test_sync_opencode_model_catalog.py`
- Focused paired test against current dirty script:
  - Command: `env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider`
  - Result: `4 failed in 0.44s`

## Allowed Paths

Future implementation is limited to:

- `scripts/opencode/sync_opencode_model_catalog.py`
- `.governance/active-gates.json`
- `.governance/active-gates.md`
- `.governance/programs/artdeco-web-design-governance/nodes.json`
- `.governance/programs/artdeco-web-design-governance/tree.md`
- `.governance/programs/artdeco-web-design-governance/cards/b4-012-sync-opencode-model-catalog-restore-authorization.yaml`
- `docs/reports/worklogs/claude-auto/b4-012-m2b-b2-c-a-sync-opencode-model-catalog-restore-authorization-prep-2026-06-14.md`

## Explicit Non-Goals

- Do not restore, edit, stage, delete, or retire `scripts/opencode/sync_opencode_model_catalog.py` during authorization prep.
- Do not modify `scripts/opencode/sync_omc_model_catalog.py`.
- Do not modify `tests/unit/test_sync_opencode_model_catalog.py`.
- Do not modify `tests/unit/test_sync_omc_model_catalog.py`.
- Do not modify docs/guides, OpenSpec, frontend, API, ST-HOLD, marketKlineData, or unrelated dirty paths.
- Do not implement or validate the ASXS provider migration in this restore-only package.

## Commit Gate For This Authorization Prep

- Exact staged allowlist only.
- No target script staged during authorization prep.
- `git diff --cached --check` passes.
- GitNexus staged review runs and reports low or no process impact.
- OPENDOG verification reports no cleanup/refactor blockers.

## Future Implementation Gate

If the user approves source implementation, the restore package must:

- Restore `scripts/opencode/sync_opencode_model_catalog.py` byte-equivalent to `HEAD`
- Keep both OMC files untouched
- Keep both paired tests untouched
- Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/unit/test_sync_opencode_model_catalog.py -q --no-cov -p no:cacheprovider
```

- Record GitNexus `verify-staged` and `detect-changes --scope staged`
- Stage only the target script plus this package's governance/report files

## Boundary Confirmation

This package prepares authorization only. It does not authorize source edits until the user explicitly approves implementation and the node reaches `approved-for-implementation`.
