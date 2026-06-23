# B4.012-M3a-E3b-E2c Chrome DevTools Guide Bootstrap No-Source Review

## Scope

- Parent: `b4-012-m3a-e3b-e2-web-frontend-guides-family-split`
- Proposed node: `b4-012-m3a-e3b-e2c-chrome-devtools-guide-bootstrap`
- Source/runtime/test edits authorized: no

## Trigger

The focused repository-hygiene test still fails because the canonical Chrome
DevTools guide family is missing:

```text
tests/unit/scripts/test_repository_hygiene_paths.py::test_chrome_devtools_guides_are_converged_under_guides_chrome_devtools_family

AssertionError:
docs/guides/chrome-devtools/CHROME_DEVTOOLS_MCP_FIX_GUIDE.md is not a file
```

## Findings

- `docs/guides/chrome-devtools/` does not exist.
- Existing source material is present under:
  `docs/guides/ai-tools/chrome-devtools/`
- The existing source family contains:
  - `INDEX.md`
  - `CHROME_DEVTOOLS_MCP_FIX_GUIDE.md`
  - `CHROME_DEVTOOLS_MCP_GUIDE.md`
  - `CHROME_DEVTOOLS_MCP_SOLUTION.md`
  - `chrome-devtools-wsl2-guide.md`
  - `mystocks-chromedevtools-testing-guide.md`
- `docs/INDEX.md` already points to the canonical family:
  - `guides/chrome-devtools/INDEX.md`
  - `guides/chrome-devtools/CHROME_DEVTOOLS_MCP_GUIDE.md`
  - `guides/chrome-devtools/chrome-devtools-wsl2-guide.md`
  - `guides/chrome-devtools/mystocks-chromedevtools-testing-guide.md`
- `docs/reports/cleanup/index-artifacts/INDEX_root.md` already lists all five
  Chrome DevTools guide filenames under the `chrome-devtools/` bridge.
- `docs/guides/web/WEB_FRONTEND_STARTUP_GUIDE.md` and
  `docs/guides/web/WEB_ACCESS_VERIFICATION_STANDARD.md` already reference the
  canonical `docs/guides/chrome-devtools/` family.

## Decision

The safe first implementation is a canonical-family bootstrap:

- Copy the existing Chrome DevTools guide family from
  `docs/guides/ai-tools/chrome-devtools/` to `docs/guides/chrome-devtools/`.
- Do not delete or alter the existing `ai-tools/chrome-devtools` source in this
  package.
- Treat retirement of the old path as a separate follow-up decision, because it
  is not required to clear the focused repository-hygiene failure.

## Proposed Authorization

Allowed paths:

- `docs/guides/chrome-devtools/`
- `docs/reports/worklogs/claude-auto/`

Allowed action:

- Bootstrap `docs/guides/chrome-devtools/` from the existing
  `docs/guides/ai-tools/chrome-devtools/` files.

## Non-Goals

- No source/runtime/test edits.
- No `docs/guides/ai-tools/chrome-devtools/` edits or deletions.
- No `docs/INDEX.md` edits.
- No `docs/reports/cleanup/index-artifacts/INDEX_root.md` edits.
- No OpenSpec edits.
- No root agent-rule files or external dirty files.

## Expected Validation

- Focused repository-hygiene test:
  `pytest -q --no-cov -o addopts='' --tb=no tests/unit/scripts/test_repository_hygiene_paths.py::test_chrome_devtools_guides_are_converged_under_guides_chrome_devtools_family`
- `git diff --cached --check`
- FUNCTION_TREE validate
- GitNexus verify-staged and detect-changes, expected risk `low`
- OPENDOG verification, expected fresh with no blockers
