# B4.012-M3a-E3b-C repository hygiene reports/index family decision

Date: 2026-06-22
Repo: `/opt/claude/mystocks_spec`
Branch: `wip/root-dirty-20260403`
Mode: no-source family decision preparation

## Scope

This package is the first family slice under the repository hygiene docs-truth atlas. It stays in the low-risk documentation / generated-index lane.

In scope:

- Report cleanup and generated index placement drift
- Documentation truth for canonical report landing paths
- Root-level report / README placement consistency when tied to generated indexes
- Boundary isolation from source/runtime/OpenSpec/external dirty files

Out of scope:

- Any source edits
- Any test edits
- Any runtime edits
- Any OpenSpec edits
- Any changes to the other three families: guides/navigation, root-entrypoint contract, legacy placement
- Any cleanup of the already-closed B4.007/B4.008/B4.009/B4.010/B4.011/B4.013 lines

## Evidence Anchor

This family is derived from the docs-truth atlas baseline captured in:

- `docs/reports/worklogs/claude-auto/b4-012-m3a-e3b-b-repository-hygiene-docs-truth-repair-atlas-2026-06-22.md`

The shared baseline remains:

- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q` -> `87 failed, 15 passed`

## Decision Intent

This is not yet an implementation package. It prepares the first family-level authorization boundary so later edits, if approved, can stay tightly isolated to the report/index surface.

## Next Step

Move this family node to `evidence-prepared` and then `decision-prepared`, then draft its authorization package separately from the other families.
