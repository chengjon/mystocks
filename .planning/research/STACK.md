# Stack Research: Codebase Cleanup Tools

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**Researched:** 2026-04-06
**Confidence:** High (well-established tooling)

---

## Python Cleanup Tools

### Lint & Auto-fix (Required)

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **ruff** | 0.11+ | Linter + formatter, replaces flake8/isort/pydocstyle | High |
| **ruff check --fix** | — | Auto-fix safe issues (F401, F841, W291, W293, E701) | High |
| **autoflake** | 2.x | Remove unused imports/variables that ruff won't touch | High |

### Dead Code Detection (Recommended)

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **vulture** | 0.14+ | Find unused code (functions, classes, variables) | Medium |
| **dead** | 1.x | Alternative dead code finder, cross-module analysis | Medium |

**Recommendation:** Use vulture for initial scan, but verify every finding manually (it has false positives with dynamic imports and string-based references).

### Import Cleanup (Required)

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **ruff** (F401, F811) | — | Remove unused imports, detect redefined-while-unused | High |
| **pydeps** | 1.x | Visualize module dependency graph for circular import detection | Medium |

### Safe Refactoring (Recommended)

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **rope** | 1.x+ | Python refactoring library (rename, move, extract) | High |
| **libcst** | 1.x | AST-based code transformation (preserve formatting) | Medium |

**Recommendation:** For bulk import path changes (e.g., `from data_access_pkg` → `from data_access`), use `rope` or a simple `sed`/`ast_grep` approach. Rope is safer for renames.

## Vue/TypeScript Cleanup Tools

### Lint (Required)

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **eslint** | 9.x | JS/TS linter | High |
| **stylelint** | 16.x | CSS/SCSS linter (already configured in project) | High |
| **vue-tsc** | 2.x | Vue TypeScript type checking | High |

### Dead Code (Recommended)

| Tool | Version | Purpose | Confidence |
|------|---------|---------|------------|
| **ts-prune** | 0.10+ | Find unused exports in TypeScript | Medium |
| **knip** | 5.x+ | Find unused files, exports, dependencies in JS/TS projects | High |

**Recommendation:** Use knip — it's more comprehensive than ts-prune and handles Vue SFC files.

## NOT Recommended

| Tool | Why Not |
|------|---------|
| **pylint** | Too noisy, overlaps with ruff, slow |
| **black** | Ruff handles formatting now (ruff format) |
| **flake8** | Fully replaced by ruff |
| **pre-commit auto-fixes** | Too aggressive for cleanup — need manual review |

## Execution Order

1. **ruff check --fix** — Auto-fix safe issues first (~46% of 1,456 errors)
2. **Resolve duplicate adapters** — Eliminates 500+ F821 errors at source
3. **autoflake** — Clean remaining unused imports
4. **vulture** — Identify dead code for user review
5. **knip** — Find unused Vue/TS exports

---
*Research completed: 2026-04-06*
