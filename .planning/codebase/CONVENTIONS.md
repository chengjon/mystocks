# Coding Conventions

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前执行口径请优先遵循 `architecture/STANDARDS.md`、根目录 `AGENTS.md`，并结合当前代码实现与主线治理文档使用。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码或主线文档冲突，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、当前代码与主线治理文档为准。


**Last mapped**: 2026-04-05

## Python Conventions

### Import Style
- **Required**: Absolute imports using `from src.*`
- **Import order**: stdlib → third-party → local
- **Violations found**: Root shim files use bare `from core import *` (no `src.` prefix)

### Type Hints
- Function parameters and return values should use type hints
- Pydantic models for data validation
- `# type: ignore` found in 12 files (~40 occurrences), mostly in `web/backend/app/services/stock_search_service.py` (15)

### Naming
- **Modules**: snake_case
- **Classes**: PascalCase
- **Constants**: UPPER_SNAKE_CASE
- **Violations**: `src/calcu/` (truncated name)

### File Organization
- Max 800 lines for Python files (enforced by `architecture/standards/large_file_splitting_principles.md`)
- Max 500 lines for Vue/TS files
- Max 1000 lines for test files
- **Current violations**: All under 800 lines (previously >1000 line files were mechanically split)

### Error Handling
- Bare `except` forbidden (E722 — 13 occurrences remain)
- External calls should consider retry logic
- Contextual exception logging required

### Configuration
- Ports injected via `.env` only, no hardcoding
- Frontend: 3020-3029, Backend: 8020-8029
- Config centralized in `config/` directory

## Frontend (TypeScript / Vue) Conventions

### Import Convention
- ES modules with explicit extensions for local imports
- Import order: third-party → local → styles

### Function Patterns
- Top-level pure functions: `function` declarations
- Callbacks/closures: arrow functions
- `defineStore`, composables: `const xxx = () =>` allowed

### Type Annotations
- Exported functions in `api/`, `services/`, `utils/` must have explicit return types
- No bare `any` in business code
- `@ts-ignore` / `@ts-expect-error` forbidden without approval

### CSS/SCSS
- No inline styles in Vue components
- Styles in sibling `styles/` directory
- `npx stylelint` must pass with zero errors

## Code Quality Gates

| Tool | Command | Standard |
|------|---------|----------|
| Ruff | `ruff check src/ web/backend/app/` | Currently ~1456 issues |
| Mypy | `mypy src/ --no-error-summary` | Type safety |
| Pytest | `pytest` | Test execution |
| Stylelint | `npx stylelint "src/**/*.{vue,scss,css}"` | Zero errors |
| vue-tsc | `npx vue-tsc --noEmit` | TS type check |
| Black | `black --check .` | Formatting |

## Anti-Patterns Found in Codebase

1. **Wildcard imports**: `from core import *` in shim files
2. **Mechanical file splitting**: `part1.py`, `part2.py`, `part3.py` — no semantic meaning
3. **"new" suffix**: `database_service_new.py` — incomplete migration marker
4. **Root shim chain**: `src/core.py` → `from core import *` → potential circular dependency
5. **Mixed entry points**: 8 main*.js/ts files in frontend
6. **Case-inconsistent directories**: `Charts/` vs `charts/` in same parent
