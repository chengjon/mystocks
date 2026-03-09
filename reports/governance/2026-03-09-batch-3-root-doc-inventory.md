# Batch 3 Root Document Migration Inventory

- Date: `2026-03-09`
- Worktree: `dev-repo-hygiene-b1`
- Change: `integrate-repository-hygiene`

## Migration Batch

This batch converges five low-risk legacy root documents into canonical lifecycle directories.

| Legacy Root Path | Target Path | Lifecycle |
|---|---|---|
| `E2E_TEST_EXECUTION_SUCCESS_REPORT.md` | `archive/docs/e2e/E2E_TEST_EXECUTION_SUCCESS_REPORT_2026-03-01.md` | `archive/` |
| `E2E_TEST_QUICK_REFERENCE.md` | `docs/guides/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md` | `docs/` |
| `GEMINI_设置相关文件迁移清单.md` | `archive/docs/tooling/GEMINI_SETTINGS_FILE_MIGRATION_CHECKLIST_2026-03.md` | `archive/` |
| `Gemini代理配置成功经验与固化指南.updated.md` | `docs/guides/GEMINI_PROXY_CONFIGURATION_GUIDE.md` | `docs/` |
| `OMC_README.md` | `docs/guides/OMC_WORKFLOW_GUIDE.md` | `docs/` |

## Link Updates

- `README.md` now points to `docs/guides/OMC_WORKFLOW_GUIDE.md`.
- `docs/guides/INDEX_root.md` now exposes the migrated active guides.
- The archived E2E execution report now points to `docs/guides/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md`.

## Expected Governance Delta

- Root warnings should drop by `5` after this batch.
- Root `error` findings remain expected at `0`.
