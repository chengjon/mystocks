# B4.012-M3a-E3a Repository Hygiene Unit Script Implementation Blocker

- Date: 2026-06-22
- Node: `b4-012-m3a-e3a-repository-hygiene-unit-script-authorization`
- Parent: `b4-012-m3a-e3-governance-script-tests-split`
- Source edits authorized by prior card: not usable for the current dirty diff

## Blocker

E3a implementation was not safe to proceed under the prepared authorization.

The E3a authorization card allowed only syntax/lint/import hygiene in:

- `tests/unit/scripts/test_repository_hygiene_paths.py`

However, the current dirty diff in that file is broader than the authorization prep described. It removes repository-hygiene assertions and expected path entries for `OMC_WORKFLOW_GUIDE`, including:

- `OMC_WORKFLOW_GUIDE.md` from the expected AI tooling guide list
- `assert "guides/ai-tools/OMC_WORKFLOW_GUIDE.md" in docs_index`
- `assert "docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md" in readme`
- `assert "OMC_WORKFLOW_GUIDE" in ai_tools_index`

Those changes are policy/assertion changes, not lint-only cleanup. E3a explicitly forbids assertion weakening, skip/xfail addition, broad repository-hygiene policy changes, deletion, restore, or migration.

## Read-Only Evidence

Read-only checks showed:

- `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` still exists.
- The OMC guide still has historical preserve evidence under B4.011 worklogs.
- `README.md`, `docs/INDEX.md`, and `docs/guides/ai-tools/INDEX.md` no longer contain `OMC_WORKFLOW_GUIDE` references in the current worktree.

This means the current dirty diff may reflect a real repository-hygiene contract change, but that decision is outside the E3a lint/import hygiene authorization.

## Safe Next Options

Option A: strict E3a hygiene only

- Authorize restoring the OMC assertion deletions in `tests/unit/scripts/test_repository_hygiene_paths.py`.
- Keep or remove only genuinely unused code after restoring the original repository-hygiene contract.
- Run `py_compile`, `ruff`, and focused pytest for the file.

Option B: repository-hygiene policy update

- Create a separate authorization that explicitly allows changing the `OMC_WORKFLOW_GUIDE` repository-hygiene expectations.
- Include a no-source decision on whether `OMC_WORKFLOW_GUIDE` is still an active docs contract, HOLD artifact, or retired path.
- If approved, update assertions with evidence rather than treating the change as lint cleanup.

## Disposition

E3a is blocked until the implementation authorization is clarified. No test file was staged or committed in this blocker package.

## 2026-06-22 Strict Hygiene Follow-Up

After user approval, E3a was temporarily unblocked for the strict hygiene route:

- restore/preserve the removed `OMC_WORKFLOW_GUIDE` repository-hygiene assertions;
- avoid README/docs policy edits;
- avoid assertion weakening, skip/xfail additions, broad test rewrites, and source/runtime changes.

The OMC assertion deletion was restored to the HEAD contract, leaving `tests/unit/scripts/test_repository_hygiene_paths.py` with no OMC-removal diff.

Read-only and verification evidence from the strict route:

- `python -m py_compile tests/unit/scripts/test_repository_hygiene_paths.py`: passed.
- `ruff check tests/unit/scripts/test_repository_hygiene_paths.py`: initially found lint-only issues in the same file (`guides_index` scope/unused local and `maestro_quick_start` unused local). A minimal lint fix was tested but not landed because the full E3a gate below failed.
- `pytest tests/unit/scripts/test_repository_hygiene_paths.py -q --tb=short --no-cov`: failed with `87 failed, 15 passed`.

The pytest failures are broad repository-hygiene/documentation-truth drift, not a safe lint-only E3a closure. Representative failure classes:

- docs root file list drift (`PRODUCT.md`, `README.md`, `troubleshooting.md`);
- missing generated/cleanup indexes such as `docs/reports/reviews/INDEX.md` and `docs/reports/cleanup/index-artifacts/INDEX_root.md`;
- missing guide-family indexes such as `docs/guides/tdx-integration/INDEX.md` and `docs/guides/buger/INDEX.md`;
- existing documentation navigation/assertion drift across docs reports, guides, API, testing, operations, and AI tooling families;
- root `AGENTS.md` no longer containing the exact historical GitNexus staged microbatch snippet asserted by the test.

Because the required focused pytest gate did not pass, no lint fix or test change was staged or committed. The target test file was returned to a clean worktree state before recording this blocker update.

Updated disposition:

- E3a remains blocked as a lint/import hygiene implementation package.
- Unblocking requires a separate no-source decision package for repository-hygiene docs truth drift, or a revised E3a acceptance scope that explicitly treats the current broad pytest failures as pre-existing baseline debt.
- Do not repair README/docs/index artifacts inside E3a without separate authorization.
