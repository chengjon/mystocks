# B4.012-M3a-E3b-E2c Chrome DevTools Guide Bootstrap Closeout

Date: 2026-06-24

## Scope

Node: `b4-012-m3a-e3b-e2c-chrome-devtools-guide-bootstrap`

Program: `.governance/programs/artdeco-web-design-governance`

Authorized paths:

- `docs/guides/chrome-devtools/`
- `docs/reports/worklogs/claude-auto/`

Non-goals preserved:

- No source, runtime, test, or OpenSpec edits.
- No deletion or retirement of `docs/guides/ai-tools/chrome-devtools/`.
- No `docs/INDEX.md` or cleanup-index edits.
- No external dirty-file staging.

## Landed Changes

Implementation commit: `54e927882`

Created canonical Chrome DevTools guide family under `docs/guides/chrome-devtools/`:

- `INDEX.md`
- `CHROME_DEVTOOLS_MCP_FIX_GUIDE.md`
- `CHROME_DEVTOOLS_MCP_GUIDE.md`
- `CHROME_DEVTOOLS_MCP_SOLUTION.md`
- `chrome-devtools-wsl2-guide.md`
- `mystocks-chromedevtools-testing-guide.md`

The canonical files were bootstrapped from the existing `docs/guides/ai-tools/chrome-devtools/` family. `CHROME_DEVTOOLS_MCP_FIX_GUIDE.md` had copied trailing whitespace removed in the new canonical file only so `git diff --cached --check` can pass; the normalized content remains equivalent to the source file.

## Verification

Passed:

- `git diff --cached --check`
- `node /root/.codex/skills/myskills/skills/function-tree/scripts/ft-governance.cjs validate --root /opt/claude/mystocks_spec`
- `node .gitnexus/run.cjs verify-staged --repo mystocks`
- `node .gitnexus/run.cjs detect-changes --scope staged --repo mystocks`
- `pytest -q --no-cov -o addopts='' --tb=short tests/unit/scripts/test_repository_hygiene_paths.py::test_chrome_devtools_guides_are_converged_under_guides_chrome_devtools_family`
- OPENDOG `run-verification` recorded the focused test as passed.
- `node .gitnexus/run.cjs analyze --force --index-only --verbose --worker-timeout 60`

GitNexus staged result before commit:

- Changed files: 9
- Indexed symbols: 0
- Affected processes: 0
- Risk: low

Post-commit GitNexus result:

- Indexed commit: `54e927882`
- Nodes: 223,660
- Edges: 280,762
- Flows: 300

## Boundary Notes

`ft-governance scope-check` is not usable as a whole-worktree gate in this long-running dirty worktree because it reports pre-existing external dirty files outside this node's `allowed_paths`. This package therefore used exact staged-file gates as the enforceable boundary.

The old `docs/guides/ai-tools/chrome-devtools/` path remains intact as compatibility surface. Any retirement or alias cleanup for that path must be authorized as a separate package.

## Result

The Chrome DevTools guide family now exists at the canonical repository-hygiene path expected by the focused test. This unblocks the next repository-hygiene docs-truth family item without changing runtime behavior.

Recommended next package:

- `B4.012-M3a-E3b-E2d`: continue the docs-truth guide-family queue from the next failing repository-hygiene path, using the same no-source-first and exact-staging pattern.
