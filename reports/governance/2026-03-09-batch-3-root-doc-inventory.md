# Batch 3 Root Document Migration Inventory

> **设计方案说明**:
> 本文件是架构设计、系统模型、功能结构、映射关系或规格方案，不是当前仓库共享规则、当前实现边界或当前主线契约的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内结构分层、字段约定、模块职责、功能清单和实施建议应结合当前代码与主线文档复核；若冲突，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


- Date: `2026-03-09`
- Worktree: `dev-repo-hygiene-b1`
- Change: `integrate-repository-hygiene`

## Migration Batch

This batch converges five low-risk legacy root documents into canonical lifecycle directories.

| Legacy Root Path | Target Path | Lifecycle |
|---|---|---|
| `E2E_TEST_EXECUTION_SUCCESS_REPORT.md` | `archive/docs/e2e/E2E_TEST_EXECUTION_SUCCESS_REPORT_2026-03-01.md` | `archive/` |
| `E2E_TEST_QUICK_REFERENCE.md` | `docs/testing/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md` | `docs/` |
| `GEMINI_设置相关文件迁移清单.md` | `archive/docs/tooling/GEMINI_SETTINGS_FILE_MIGRATION_CHECKLIST_2026-03.md` | `archive/` |
| `Gemini代理配置成功经验与固化指南.updated.md` | `docs/guides/ai-tools/GEMINI_PROXY_CONFIGURATION_GUIDE.md` | `docs/` |
| `OMC_README.md` | `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md` | `docs/` |

## Link Updates

- `README.md` now points to `docs/guides/ai-tools/OMC_WORKFLOW_GUIDE.md`.
- `docs/reports/cleanup/index-artifacts/INDEX_root.md` preserves the historical guides root index generated during that cleanup batch.
- The archived E2E execution report now points to `docs/testing/E2E_TEST_QUICK_REFERENCE_COMPATIBILITY.md`.

## Expected Governance Delta

- Root warnings should drop by `5` after this batch.
- Root `error` findings remain expected at `0`.
