# Pitfalls Research: Codebase Consolidation Mistakes

> **参考指南说明**:
> 本文件是补充指南、命令参考、操作说明或专题文档，不是当前仓库共享规则、当前实现边界或当前主线流程的唯一事实来源。
> 当前共享规则与治理口径请优先遵循 `architecture/STANDARDS.md`；执行流程、命令与协作约束再结合根目录 `AGENTS.md`，并与当前代码实现及主线治理文档一并核对。
>
> 文内步骤、示例、命令和说明应视为补充参考；若与当前代码、`architecture/STANDARDS.md` 或主线治理文档不一致，应以 `architecture/STANDARDS.md`、当前代码实现及主线治理文档为准。


**Researched:** 2026-04-06
**Project:** MyStocks codebase cleanup

---

## Critical Pitfalls

### P-01: Deleting "dead" code that's dynamically imported

**Warning signs:**
- Module has zero static `import` references
- But referenced via string: `importlib.import_module("src.routes." + name)`
- Or loaded by framework: FastAPI's `APIRouter.include_router()`
- Or used in configuration: `pyproject.toml` plugin paths

**Prevention:**
- Before deleting any module, grep for BOTH `import module_name` AND the string `"module_name"` across the entire codebase
- Check `conftest.py`, `pyproject.toml`, `pytest.ini`, `setup.cfg` for dynamic references
- Check `router_registry.py` and `VERSION_MAPPING.py` for route auto-discovery

**Phase:** Phase 2 (Dead Code Removal)

---

### P-02: Auto-fixing ruff errors that change semantics

**Warning signs:**
- `F841` (unused variable) — variable might be unused but assignment has side effects
- `F401` (unused import) — import might register something (e.g., `import pandas as pd` in `__init__.py`)
- `E722` (bare except) — might be intentional error suppression

**Prevention:**
- Run `ruff check --fix --select F401,F841,W291,W293,E701` — these are safe
- Do NOT auto-fix `E722`, `F811` without manual review
- After auto-fix, run `pytest` immediately to catch regressions
- Git diff review before committing

**Phase:** Phase 1 (Lint Baseline)

---

### P-03: Frontend case-conflict merges break imports

**Warning signs:**
- `Charts/` and `charts/` coexist on macOS (case-insensitive) but are different on Linux
- Import paths like `@/components/Charts/` vs `@/components/charts/` — both resolve on Mac, only one on Linux
- After merge, some imports may need case-sensitive path updates

**Prevention:**
- Before merging, list all import paths referencing the upper-case version
- After merge, search-replace imports to use the surviving case (lowercase)
- Test on Linux or use `git ls-files` to see actual case
- Run `npm run build` to verify no unresolved imports

**Phase:** Phase 3 (Structural Consolidation)

---

### P-04: Root shim removal breaks external/tooling imports

**Warning signs:**
- `core.py` at root uses `from core import *` — tools or scripts may import `from core import ...`
- `unified_manager.py` is documented as the entry point — might be used by external scripts
- `.env` or `docker-compose.yml` may reference root-level modules

**Prevention:**
- `grep -r "from core import\|import core\b" --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" .` before deletion
- Check `Dockerfile`, `docker-compose*.yml`, `Makefile`, `Procfile` for references
- If external references exist, keep shim but add deprecation warning

**Phase:** Phase 4 (Naming & Polish)

---

### P-05: Merging data access layers breaks transaction patterns

**Warning signs:**
- `data_access/` uses one connection pool pattern
- `data_access_pkg/` uses a different one
- `database/` has its own `database_service.py`
- After merge, mixing patterns could cause connection leaks or deadlocks

**Prevention:**
- Before merging, read each layer's connection management approach
- Choose ONE pattern as canonical (recommend `data_access/` since it's largest)
- Migrate files from other layers into canonical pattern
- Keep database connection handling in ONE file after merge

**Phase:** Phase 3 (Structural Consolidation)

---

### P-06: Low test coverage means regressions go undetected

**Warning signs:**
- Current coverage: 0.16% (effectively zero)
- 908 test files but most are infrastructure, not actual tests
- `pytest` might pass even if imports are broken (no tests exercise import paths)

**Prevention:**
- Add a **smoke test** before each phase: a single test file that imports every module
- Run `python -c "import src; import src.core; import src.adapters; import src.data_access"` after each change
- Run FastAPI app startup check: `python -c "from web.backend.app.main import app; print('OK')"`
- Trust grep verification more than pytest for this project

**Phase:** All phases (ongoing mitigation)

---

### P-07: Duplicate adapter layer has hidden dependents

**Warning signs:**
- `src/interfaces/adapters/` appears to be dead but might be imported via:
  - `from src.interfaces.adapters.akshare import ...`
  - `from src.interfaces import adapters`
  - Dynamic loading via `__init__.py` re-exports
- Test files may import from the interface layer specifically

**Prevention:**
- Comprehensive grep before deletion:
  ```bash
  grep -r "src.interfaces.adapters\|src.interfaces.adaptors\|from src.interfaces" --include="*.py" src/ web/ tests/ scripts/
  ```
- If imports exist, redirect them to `src/adapters/` first, then delete duplicate layer
- This is the single highest-impact fix (eliminates 500+ errors)

**Phase:** Phase 1 (Lint Baseline)

---

## Phase Pitfall Mapping

| Pitfall | Phase | Risk Level | Detection |
|---------|-------|-----------|-----------|
| P-07: Hidden adapter dependents | Phase 1 | **Critical** | grep before delete |
| P-02: Unsafe auto-fix | Phase 1 | High | ruff --select only safe rules |
| P-01: Dynamic imports | Phase 2 | **Critical** | grep strings + config files |
| P-06: Low test coverage | All | Ongoing | Smoke tests + import checks |
| P-03: Case-conflict imports | Phase 3 | High | Build verification |
| P-05: Transaction patterns | Phase 3 | Medium | Read before merge |
| P-04: Root shim dependents | Phase 4 | Medium | grep + Dockerfile check |

---
*Research completed: 2026-04-06*
