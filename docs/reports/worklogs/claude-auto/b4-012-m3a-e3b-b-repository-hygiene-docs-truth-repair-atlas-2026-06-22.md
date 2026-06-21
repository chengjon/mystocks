# B4.012-M3a-E3b-B repository hygiene docs truth repair atlas

Date: 2026-06-22
Repo: `/opt/claude/mystocks_spec`
Branch: `wip/root-dirty-20260403`
Mode: no-source baseline evidence only

## Scope

This package is a governance-only documentation truth atlas for the repository hygiene test surface.

In scope:

- Record the current baseline for `tests/unit/scripts/test_repository_hygiene_paths.py`
- Classify the failure families that still describe repository docs truth drift
- Preserve boundary isolation from source/runtime/OpenSpec/external dirty files
- Prepare the next decision package for family-based repair authorization

Out of scope:

- Any source edits
- Any test edits
- Any runtime edits
- Any OpenSpec edits
- Any change to external dirty files
- Any cleanup of the already-closed B4.007/B4.008/B4.009/B4.010/B4.011/B4.013 governance lines

## Fresh baseline evidence

Current HEAD at evidence time:

- `8727c81073a0f67ee9c64dd224ce85a478887aee`

Focused repository hygiene test baseline:

- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q`
- Result: `87 failed, 15 passed`

This remains a broad documentation truth drift baseline, not a source/runtime regression claim.

## Failure family map

The remaining failures cluster into the following families:

- `reports-cleanup-and-generated-indexes`: 27
- `web-frontend-guides`: 16
- `ops-cicd-testing-monitoring-guides`: 8
- `root-entrypoints-agent-contract`: 7
- `architecture-overview-standards-docs`: 7
- `data-quant-domain-guides`: 7
- `ai-tools-and-agent-guides`: 6
- `legacy-report-placement`: 4
- `uncategorized`: 5

Observed missing-path pressure:

- `reports`: 14
- `guides`: 9
- `openspec`: 1
- `other`: 0

## Interpretation

The repository hygiene failures are concentrated in documentation-truth and generated-index surfaces, not in the product runtime.

The highest-signal drift is:

1. report cleanup and generated index placement
2. guide navigation / canonical-path drift
3. root entrypoint documentation contract mismatches
4. cross-domain documentation references that still point at removed or moved surfaces

## Decision recommendation

Keep `b4-012-m3a-e3b-b-repository-hygiene-docs-truth-repair-atlas` in the evidence/decision lane and do not authorize source edits yet.

Next package should be family-based, not file-by-file:

- one low-risk reports/index family
- one guides/navigation family
- one root-entrypoint contract family
- one cross-domain legacy placement family

Each family should get its own authorization and closeout boundary so the remediation stays isolated and auditable.

## Boundary note

Do not mix this atlas with:

- the closed B4.007 / B4.008 / B4.009 / B4.010 / B4.011 / B4.013 governance lines
- source/runtime edits
- the known external dirty files in `.governance/programs/.../cards/`
- frontend or backend code changes

This worklog is evidence only and is intended to support the next governance transition.
