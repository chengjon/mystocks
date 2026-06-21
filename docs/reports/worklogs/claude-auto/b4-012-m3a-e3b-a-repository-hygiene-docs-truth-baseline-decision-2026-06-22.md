# B4.012-M3a-E3b-A Repository Hygiene Docs Truth Baseline Decision

- Date: 2026-06-22
- Node: `b4-012-m3a-e3b-a-repository-hygiene-docs-truth-baseline-decision`
- Parent: `b4-012-m3a-e3b-repository-hygiene-docs-truth-drift-decision`
- Mode: no-source decision
- Source edits authorized: false

## Scope Boundary

This package classifies the broad `tests/unit/scripts/test_repository_hygiene_paths.py` failure surface into baseline and follow-up tracks.

No implementation is authorized here:

- no test edits;
- no assertion weakening;
- no skip/xfail additions;
- no docs/index regeneration;
- no README/AGENTS/docs policy changes;
- no source/runtime/OpenSpec/OpenStock/frontend/backend edits;
- no staging of external dirty files.

## Fresh Verification Evidence

Executed against current HEAD `723b058e2`:

- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --tb=short --no-cov`
  - Result: failed.
  - Summary: `87 failed, 15 passed in 11.10s`.

The previous E3b evidence also showed:

- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`: pass.
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`: fail with 3 lint-only errors in the same file.

## Failure Family Classification

| Family | Count | Decision |
|---|---:|---|
| root-entrypoints-agent-contract | 7 | Active docs/agent contract drift. Needs no-source policy decision before edits. |
| reports-cleanup-and-generated-indexes | 27 | Generated/historical index artifact drift. Treat as repository-hygiene baseline debt until docs-authorized repair. |
| architecture-overview-standards-docs | 7 | Active docs trunk/reference drift. Requires docs truth decision, not test lint cleanup. |
| ai-tools-and-agent-guides | 6 | Mixed active/historical AI tooling guide drift. Needs family-specific docs decision. |
| web-frontend-guides | 16 | Guide family/index drift. Defer to docs truth repair, not E3a. |
| ops-cicd-testing-monitoring-guides | 8 | Operations/testing guide family drift. Defer to docs truth repair. |
| data-quant-domain-guides | 7 | Domain guide family/index drift. Defer to docs truth repair. |
| legacy-report-placement | 4 | Historical report placement drift. Candidate for archive/baseline decision. |
| uncategorized supporting-guide drift | 5 | Needs follow-up classification before implementation. |

Missing path counts from the focused pytest evidence:

- `docs/reports/**`: 14 unique missing paths.
- `docs/guides/**`: 9 unique missing paths.
- `openspec/**`: 1 unique missing path.
- other paths: 0.

## Baseline Decision

The broad pytest failures should be treated as pre-existing repository-hygiene docs truth baseline debt for the purpose of E3a.

Reasoning:

- E3a was scoped to a single test file and lint/import hygiene.
- The focused pytest failures span docs root, report indexes, guide family indexes, historical reports, OpenSpec planning paths, and root agent instruction text.
- Repairing those failures requires docs truth or policy edits outside E3a.
- Updating assertions to match current drift would be a test-policy change and is also outside E3a.

Therefore, E3a should not carry the full pytest gate as a blocking implementation acceptance unless a separate docs truth repair package has first been completed.

## Recommended Authorization Sequence

### 1. E3a-R1 lint-only recovery

Purpose: close the narrow lint hygiene debt in the already-isolated test file.

Allowed path:

- `tests/unit/scripts/test_repository_hygiene_paths.py`
- closeout worklog under `docs/reports/worklogs/claude-auto/`

Allowed action:

- fix only the three lint errors:
  - `F821 Undefined name guides_index`;
  - `F841 Local variable guides_index is assigned to but never used`;
  - `F841 Local variable maestro_quick_start is assigned to but never used`.

Explicit gate adjustment:

- required: `python -m py_compile`;
- required: `ruff check`;
- required: focused pytest execution as evidence;
- accepted baseline: focused pytest may remain red at `87 failed / 15 passed` or equivalent broad docs-truth failure count, provided no new failure family is introduced by the lint-only diff.

Forbidden:

- no assertion deletion;
- no skip/xfail;
- no docs/README/AGENTS updates;
- no broad rewrite of `test_repository_hygiene_paths.py`;
- no attempt to make all 102 tests pass inside E3a-R1.

### 2. E3b-B docs truth repair atlas

Purpose: decide whether to repair, regenerate, retire, or baseline the docs truth contracts.

Mode: no-source first, then docs-authorized family packages only if approved.

Recommended families:

1. reports cleanup/index artifacts;
2. guide family indexes;
3. docs root and active navigation contracts;
4. root AGENTS / CLAUDE GitNexus wording contract;
5. historical report/archive placement.

### 3. E3b-C focused test-policy package

Only after E3b-B decisions:

- split the oversized repository-hygiene test into family-specific tests, or
- update assertions to current docs truth, or
- retire obsolete historical assertions with explicit evidence.

## Current FUNCTION_TREE Impact

- `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`: remains blocked until E3a-R1 is explicitly authorized with adjusted acceptance, or until docs truth repair makes the focused pytest green.
- `b4-012-m3a-e3b-repository-hygiene-docs-truth-drift-decision`: remains decision-prepared.
- This E3b-A package prepares the next authorization decision; it does not grant implementation permission.
