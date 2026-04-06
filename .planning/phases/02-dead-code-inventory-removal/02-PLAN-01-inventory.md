---
wave: 1
depends_on: []
files_modified:
  - DELETION-CANDIDATES.md (new)
  - .planning/phases/02-dead-code-inventory-removal/02-PLAN-01-inventory.md
autonomous: true
requirements_addressed:
  - DEAD-06
---

# Plan 01: Dead Code Inventory & Functional Tree

**Objective:** Produce a comprehensive DELETION-CANDIDATES.md with grep evidence AND functional tree analysis for all 5 deletion targets. NO code changes in this plan — documentation only.

## Tasks

<task id="1">
<objective>
Run comprehensive import analysis for all 5 deletion targets
</objective>

<read_first>
- .planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md (decisions D-08 through D-11)
- .planning/phases/02-dead-code-inventory-removal/02-RESEARCH.md (caller analysis already partially done)
- architecture/STANDARDS.md (lines 103-111 — deletion governance rules)
</read_first>

<action>
For each of the 5 target directories, run the following grep commands and capture full output with file:line references:

1. `src/routes/` (19 files):
   ```bash
   grep -rn "from src\.routes\b\|import src\.routes\b" --include="*.py" src/ web/ tests/ scripts/
   grep -rn "src\.routes\b" --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" .github/ scripts/
   grep -rn "importlib\|__import__\|import_module" --include="*.py" src/routes/
   ```

2. `src/api/` (5 files):
   ```bash
   grep -rn "from src\.api\b\|import src\.api\b" --include="*.py" src/ web/ tests/ scripts/
   grep -rn "src\.api\b" --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" .github/ scripts/
   grep -rn "importlib\|__import__\|import_module" --include="*.py" src/api/
   ```

3. `src/data_access_pkg/` (5 files):
   ```bash
   grep -rn "from src\.data_access_pkg\b\|import src\.data_access_pkg\b" --include="*.py" src/ web/ tests/ scripts/
   ```

4. `src/db_manager/` (1 file):
   ```bash
   grep -rn "from src\.db_manager\b\|import src\.db_manager\b" --include="*.py" src/ web/ tests/ scripts/
   grep -rn "from db_manager\b\|import db_manager\b" --include="*.py" src/ web/ tests/ scripts/
   ```

5. `src/database_optimization/` (5 files):
   ```bash
   grep -rn "from src\.database_optimization\b\|import src\.database_optimization\b" --include="*.py" src/ web/ tests/ scripts/
   ```

Also run a CI/CD sweep:
```bash
grep -rn "src\.routes\|src\.api\|src\.data_access_pkg\|src\.db_manager\|src\.database_optimization" --include="*.sh" --include="*.yml" --include="*.yaml" --include="*.toml" scripts/ .github/ config/
```
</action>

<acceptance_criteria>
- All grep commands have been run for all 5 targets
- Output captured with file:line references
- CI/CD scripts checked
- Dynamic import scan complete for src/routes/ and src/api/
</acceptance_criteria>
</task>

<task id="2">
<objective>
Build functional tree for each target directory
</objective>

<read_first>
- All files in src/routes/ (19 files — read __init__.py and main route files to understand purpose)
- All files in src/api/ (5 files)
- src/data_access_pkg/__init__.py, src/data_access_pkg/interface.py
- src/db_manager/__init__.py
- src/database_optimization/__init__.py
</read_first>

<action>
For each target directory, document:

1. **src/routes/** — For each of the 19 files, document:
   - Module path (e.g., `src/routes/monitoring_routes/check_monitoring_health.py`)
   - Functional purpose: what endpoint/capability does it define?
   - HTTP method + path pattern (if it defines FastAPI routes)
   - Canonical equivalent in `web/backend/app/api/` (the actual active route layer)
   - All known callers (from task 1 grep output)
   - Keep/delete recommendation

2. **src/api/** — For each of the 5 files:
   - Module path
   - Functional purpose
   - All known callers
   - Check if `src/api/types/` directory exists and what it contains
   - Keep/delete recommendation

3. **src/data_access_pkg/** — For each of the 5 files:
   - Module path
   - Classes/functions exported
   - Compare with canonical `src/data_access/` equivalents
   - CRITICAL: Compare `tdengine_access.py` content (23,514 bytes vs 2,770 bytes canonical)
   - Keep/delete/merge recommendation

4. **src/db_manager/** — Single file analysis:
   - Verify `__init__.py` is ONLY a re-export shim pointing to `src.storage.database`
   - Confirm no other files exist in directory
   - Keep/delete recommendation

5. **src/database_optimization/** — For each of the 5 files:
   - Module path, classes/functions exported
   - Compare with `src/data_access/optimizers/query_optimizer.py`
   - Determine if each file has unique functionality not in canonical layer
   - Keep/delete/merge recommendation with specific merge target path
</action>

<acceptance_criteria>
- Functional tree documented for all 5 directories (34 files total)
- Each file has: module path, purpose, status, callers, recommendation
- tdengine_access.py content comparison completed (23KB vs 3KB discrepancy resolved)
- database_optimization file-by-file overlap analysis complete
</acceptance_criteria>
</task>

<task id="3">
<objective>
Write DELETION-CANDIDATES.md per CONTEXT.md format requirements (D-08 through D-11)
</objective>

<read_first>
- .planning/phases/02-dead-code-inventory-removal/02-CONTEXT.md (decisions D-08 through D-11)
- Task 1 and Task 2 outputs
</read_first>

<action>
Create `DELETION-CANDIDATES.md` at project root with this structure:

```markdown
# Deletion Candidates — Phase 2 Review

**Generated:** [date]
**Status:** PENDING USER APPROVAL
**Phase:** 2 (Dead Code Inventory & Removal)

---

## Summary

| Target | Files | Prod Callers | Test Callers | Script Refs | Recommendation |
|--------|-------|-------------|-------------|-------------|---------------|
| src/routes/ | 19 | 1 | 0 | 2 | DELETE |
| src/api/ | 5 | 0 | 1 | 1 | DELETE |
| src/data_access_pkg/ | 5 | 0 | 0 | 0 | MERGE → src/data_access/ |
| src/db_manager/ | 1 | 0 | 0 | 3 | DELETE |
| src/database_optimization/ | 5 | 0 | 2 | 1 | MERGE → src/data_access/optimizers/ |

---

## Table 1: src/routes/ (19 files)

| File | Purpose | Status | Callers (file:line) | Action | Redirect To |
|------|---------|--------|--------------------|----:|------------|
| ... | ... | ... | ... | DELETE | web/backend/app/api/... |
...

## Table 2: src/api/ (5 files)
...

## Table 3: src/data_access_pkg/ (5 files)
...

## Table 4: src/db_manager/ (1 file)
...

## Table 5: src/database_optimization/ (5 files)
...

---

## Caller Redirection Map

| Current Import | Redirect To | Files Affected |
|---------------|------------|---------------|
| from src.routes.wencai_routes import ... | from web.backend.app.api.... import ... | src/database/services/database_service.py:155 |
...

## Verification Commands

```bash
# After all sub-stages complete:
ruff check src/ web/backend/app/ | wc -l  # Must be <900
cd web/backend && PYTHONPATH=$(git rev-parse --show-toplevel):. python -c "from app.main import app; print('OK')"
pytest --tb=short
```
```

Each table must include actual grep output as evidence, not summaries. Per D-10: "Include grep evidence as inline command output (not just 'grep returned X results')."
</action>

<acceptance_criteria>
- `DELETION-CANDIDATES.md` exists at project root
- Contains 5 tables (one per target directory) with per-file analysis
- Each row has: file path, purpose, status, callers with file:line, keep/delete, redirect target
- Summary table with aggregate stats
- Caller Redirection Map with exact import transformations
- Grep evidence included inline (not summarized)
- Status marked as "PENDING USER APPROVAL"
</acceptance_criteria>
</task>

<task id="4">
<objective>
Commit DELETION-CANDIDATES.md and present for user review
</objective>

<read_first>
- DELETION-CANDIDATES.md (just created)
</read_first>

<action>
Stage and commit:
```bash
git add DELETION-CANDIDATES.md
git commit -m "docs(02): add deletion candidates inventory for phase 2 review"
```

Present the summary table to the user for review and approval. Do NOT proceed to Plans 02-04 until user explicitly approves.
</action>

<acceptance_criteria>
- DELETION-CANDIDATES.md committed
- Commit message references sub-stage 2a
- User has reviewed and approved the deletion list before any code changes
</acceptance_criteria>
</task>

---

## Verification

```bash
test -f DELETION-CANDIDATES.md && echo "EXISTS" || echo "MISSING"
grep -c "PENDING USER APPROVAL" DELETION-CANDIDATES.md
grep -c "src/routes/" DELETION-CANDIDATES.md
grep -c "src/api/" DELETION-CANDIDATES.md
grep -c "src/data_access_pkg/" DELETION-CANDIDATES.md
grep -c "src/db_manager/" DELETION-CANDIDATES.md
grep -c "src/database_optimization/" DELETION-CANDIDATES.md
```

## Must-Haves

- [ ] DELETION-CANDIDATES.md exists with all 5 target directories analyzed
- [ ] Every target file has grep evidence (not just counts)
- [ ] Caller Redirection Map with exact import → redirect mappings
- [ ] tdengine_access.py size discrepancy investigated and documented
- [ ] User has approved before any code changes
