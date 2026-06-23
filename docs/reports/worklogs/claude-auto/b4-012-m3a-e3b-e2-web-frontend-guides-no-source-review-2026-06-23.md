# B4.012-M3a-E3b-E2 Web/Frontend Guides No-Source Review

> **Historical evidence note**:
> This worklog records a no-source boundary review for the E2 docs-guides family.
> It is not a source of current documentation truth. Current navigation truth remains in `docs/README.md`,
> family indexes, and FUNCTION_TREE governance state.

## Scope

- Program: `artdeco-web-design-governance`
- Parent node: `b4-012-m3a-e3b-e-docs-guides-family-split`
- Candidate node: `b4-012-m3a-e3b-e2-web-frontend-guides-family-split`
- Mode: no-source review only
- Source edits authorized: false

No source, runtime, test, OpenSpec, root `AGENTS.md` / `CLAUDE.md`, or external dirty files were modified.

## Focused Evidence

Command:

```bash
pytest -q --no-cov -o addopts='' --tb=no \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_web_dev_tracking_runtime_artifacts_are_converged_under_var_log \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_selected_web_guides_are_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_html5_migration_experience_doc_is_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_theme_guides_are_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_additional_web_runtime_and_planning_guides_are_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_realtime_integration_guide_is_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_websocket_performance_guide_is_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_html_to_vue_conversion_guides_are_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_artdeco_guides_are_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_additional_ui_and_visualization_guides_are_converged_under_guides_web_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_typescript_document_cluster_is_converged_under_guides_typescript_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_chrome_devtools_guides_are_converged_under_guides_chrome_devtools_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_frontend_topic_guides_are_converged_under_guides_frontend_family \
  tests/unit/scripts/test_repository_hygiene_paths.py::test_dayjs_guides_are_converged_under_guides_frontend_family
```

Result:

- Passed: 0
- Failed: 14

## Boundary Findings

E2 is broader than a single safe implementation package. The focused failures read across guide indexes,
cleanup indexes, completion reports, OpenSpec change docs, root agent-rule files, scripts, and frontend
task reports. A direct E2 implementation would mix unrelated risk classes.

### In-Family Candidates

- `docs/guides/web/` exists and contains 60 Markdown files.
- `docs/guides/frontend/` exists and contains 33 Markdown files.
- `docs/guides/typescript/` exists and contains 19 Markdown files.
- `docs/guides/chrome-devtools/` exists as a directory but has no Markdown index.
- `docs/reports/cleanup/index-artifacts/INDEX_root.md` exists but lacks many expected web/frontend/typescript index entries.

### Out-of-Family Blockers

The following blockers are not safe to solve inside one broad E2 guide package:

- `docs/reports/completion_reports/PHASE1_UI_UX_FOUNDATION_COMPLETION_REPORT.md` is missing.
- `docs/reports/completion_reports/MYSTOCKS_HTML_VUE_CONVERSION_SUMMARY.md` is missing.
- `openspec/changes/frontend-optimization-six-phase/implementation-plan.md` is missing.
- Some later assertions inspect root `AGENTS.md`, root `CLAUDE.md`, `web/frontend/TASK-REPORT.md`, scripts, and `tests/changes/`.

These require independent authorization or must remain documented residual blockers.

## Failure Buckets

| Bucket | Representative failure | Primary surface | Disposition |
|---|---|---|---|
| Cleanup index bridge | `test_html5_migration_experience_doc_is_converged_under_guides_web_family` | `docs/reports/cleanup/index-artifacts/INDEX_root.md` | Separate E2a candidate |
| Web guide family | `test_selected_web_guides_are_converged_under_guides_web_family` | `docs/guides/web/` | Separate E2b candidate |
| Frontend guide family | `test_frontend_topic_guides_are_converged_under_guides_frontend_family` | `docs/guides/frontend/` | Separate E2c candidate |
| TypeScript guide family | `test_typescript_document_cluster_is_converged_under_guides_typescript_family` | `docs/guides/typescript/` | Separate E2d candidate |
| Chrome DevTools bootstrap | `test_chrome_devtools_guides_are_converged_under_guides_chrome_devtools_family` | `docs/guides/chrome-devtools/` | Separate E2e candidate |
| Reports anchors | selected web/html-to-vue failures | `docs/reports/completion_reports/` | Separate reports package |
| OpenSpec workflow docs | additional web runtime/planning failure | `openspec/changes/frontend-optimization-six-phase/` | Separate OpenSpec package |

## Recommendation

Do not authorize a single broad E2 implementation.

Recommended sequence:

1. `E2a cleanup-index bridge`: update only `docs/reports/cleanup/index-artifacts/` and related cleanup-directory evidence if explicitly authorized.
2. `E2b web guides`: update `docs/guides/web/` indexes and compatibility references only.
3. `E2c frontend guides`: update `docs/guides/frontend/` indexes and compatibility references only.
4. `E2d typescript guides`: update `docs/guides/typescript/` indexes and compatibility references only.
5. `E2e chrome-devtools bootstrap`: restore/create `docs/guides/chrome-devtools/INDEX.md` and associated family references only.
6. Handle reports anchors and OpenSpec missing files as independent packages; do not mix them into E2a-E2e.

## Non-Goals

- No source/runtime/test edits.
- No OpenSpec edits.
- No root `AGENTS.md` or `CLAUDE.md` edits.
- No `web/frontend/TASK-REPORT.md` edits.
- No external dirty file staging.
- No data-source/provider runtime work; MyStocks remains only a consumer/adaptor of OpenStock data.
