# B4.012-M2a-C g2-327 Source-Review Task-Card Disposition No-Source Audit

Date: 2026-06-13

## Scope

This is a no-source disposition audit for the final governance task-card residual.

Included:

- `governance/mainline/task-cards/g2-327.yaml`

Explicitly excluded:

- all already preserved accepted task cards
- source, test, runtime, API, route, OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, and external dirty files
- any task-card preservation, deletion, migration, or source implementation

## Baseline

- Branch: `wip/root-dirty-20260403`
- HEAD: `82240fb67 B4.012-M2a-B1: close accepted task-card preservation node`
- Staged changes: empty
- `governance/mainline/task-cards/` residuals: only `g2-327.yaml`

## Extracted Evidence

`g2-327.yaml` is not a low-risk accepted no-source card:

- title: `Implement technical_analysis DataSourceFactory provider`
- status: `source_implementation_review_required`
- approval status: `approved`
- review status: `reviewed-but-not-merged`
- size: 6,330 bytes, 111 lines

Risk keywords present:

- `source_implementation_review_required`
- `reviewed-but-not-merged`
- `DataSourceFactory`
- `technical_analysis`
- `implementation`
- `source`
- `tests`
- `docs/api`

Referenced source/test paths that currently exist and are tracked:

- `web/backend/app/api/technical_analysis.py`
- `tests/api/file_tests/test_technical_analysis_api.py`
- `web/backend/app/services/data_source_factory/`
- `web/backend/app/api/watchlist.py`
- `web/backend/app/api/strategy_management/`
- `web/backend/app/api/_technical_analysis_models.py`
- `web/backend/app/api/_technical_analysis_responses.py`
- `docs/api/`
- `web/frontend/`

Referenced implementation report path:

- active path missing: `docs/reports/quality/backend-technical-analysis-datasourcefactory-provider-implementation-2026-06-03.md`
- archived copy present: `archive/docs/reports/quality/backend-technical-analysis-datasourcefactory-provider-implementation-2026-06-03.md`

The card also records a historical caveat that GitNexus `detect_changes` timed out for the staged two-file scope in that older implementation context. That caveat must not be treated as current evidence for source correctness.

## Disposition

Do not delete `g2-327.yaml` as ordinary residue. It records source-review context for the technical_analysis DataSourceFactory provider lane and still references active tracked source/test surfaces.

Do not batch it with accepted no-source cards. Its status is explicitly source-review related, and its referenced implementation report is no longer at the active path.

Do not infer current source correctness from the card. Any source-level claim about `web/backend/app/api/technical_analysis.py` or `tests/api/file_tests/test_technical_analysis_api.py` requires a fresh, independently authorized source/test audit.

## Recommended Next Split

Recommended next package:

- `B4.012-M2a-C1 g2-327 source-review task-card preservation authorization`

Suggested C1 scope:

- preserve only `governance/mainline/task-cards/g2-327.yaml` as isolated high-risk governance evidence
- update only required FUNCTION_TREE closeout/worklog artifacts

Suggested C1 non-goals:

- no source or test edits
- no technical_analysis implementation review
- no API/runtime behavior changes
- no OpenSpec, ST-HOLD, marketKlineData, `docs/guides/**`, `docs/superpowers/**`, or external dirty files

If a source-level review is needed after preservation, it should be a separate later node:

- `B4.012-M2a-C2 technical_analysis DataSourceFactory source truth audit`

## Required Gates For Any Follow-Up

- exact staged allowlist
- `git diff --cached --check`
- GitNexus staged verification and staged detect-changes
- OPENDOG blockers check
- post-commit GitNexus index refresh

## Current Status

`source_edits_authorized: false`

This no-source audit does not authorize preserving, deleting, or modifying `g2-327.yaml`.
