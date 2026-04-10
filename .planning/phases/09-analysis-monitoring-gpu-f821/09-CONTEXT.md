# Phase 9: Analysis + Monitoring + GPU F821 - Context

**Gathered:** 2026-04-10
**Status:** Ready for planning

<domain>
## Phase Boundary

Resolve all F821 errors in src/advanced_analysis/ (91 errors, 10 files), src/monitoring/ (83 errors, 8 files), and src/gpu/ (46 errors, 6 files). Total: 220 errors across 24 files.

This is NOT purely mechanical import-fixing. Two categories of errors exist:
1. **Missing imports** — undefined names that need import statements (majority)
2. **Non-mechanical errors** — variables used outside their scope requiring signature changes (minority, e.g. `stock_data` in canslim_analyzer.py)

Only import lines and function signatures may change. No logic changes.

</domain>

<decisions>
## Implementation Decisions

### Conditional imports strategy
- **D-01:** Use module-level `try/except ImportError` with `*_AVAILABLE` boolean flag pattern for optional third-party dependencies
- **D-02:** For SNOWNLP: create new `SNOWNLP_AVAILABLE = False` default, import `SnowNLP` and `jieba` inside try block. **Must also `import jieba.analyse`** — `jieba.analyse.extract_tags()` requires the submodule explicitly imported; bare `import jieba` does not expose `.analyse` at runtime
- **D-03:** For GPU: import `GPU_AVAILABLE` and `IsolationForest` from sibling `dataclasses.py` module where they're already properly defined (don't recreate the pattern)
- **D-04:** Pattern matches existing codebase convention: `try: from cuml import IsolationForest; GPU_AVAILABLE = True; except ImportError: GPU_AVAILABLE = False`

### Non-mechanical F821 errors
- **D-05:** Fix by adding missing parameters to function signatures only (e.g., add `stock_data: Dict` parameter to `get_canslim_score(self, score)` in `src/advanced_analysis/decision_models/models/canslim_analyzer.py:144` — it uses `stock_data` at line 160 without it being a parameter)
- **D-06:** Do NOT refactor to store as instance attributes — minimal change, preserve existing structure
- **D-07:** Each non-mechanical fix must be analyzed individually — the executor reads the file to understand the scope before fixing

### Cross-module types
- **D-08:** ALL cross-module types imported from their canonical implementation location — no local stubs, no placeholder definitions
- **D-09:** `MultiLevelCache` → import from `src.gpu.api_system.utils.cache_optimization` (canonical class at line 303)
- **D-10:** `IsolationForest` / `GPU_AVAILABLE` → import from `src.advanced_analysis.anomaly.dataclasses` (already has proper conditional import)
- **D-11:** `BacktestEngine` / `BacktestEngineGPU` / `MLTrainingGPU` → import from their actual module definitions in `src/gpu/`

### Plan structure
- **D-12:** One plan per directory: Plan 01 for advanced_analysis, Plan 02 for monitoring, Plan 03 for gpu. Enables parallel execution and per-directory verification.

### Claude's Discretion
- Exact import ordering within stdlib/third-party/local groups
- Handling of edge cases where a name's canonical source is ambiguous
- Per-file verification sequence

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Import patterns and conventions
- `src/advanced_analysis/anomaly/dataclasses.py` — canonical example of conditional import pattern (GPU_AVAILABLE + IsolationForest try/except)
- `src/governance/risk_management/calculators/gpu_calculator/utils.py` — another GPU_AVAILABLE pattern reference

### Cross-module type definitions
- `src/gpu/api_system/utils/cache_optimization.py` — canonical `MultiLevelCache` class (line 303)
- `src/advanced_analysis/anomaly/dataclasses.py` — canonical `AnomalyEvent`, conditional `IsolationForest`, `GPU_AVAILABLE`

### Requirements
- `.planning/REQUIREMENTS.md` — LINT-06, LINT-07, LINT-08 (Phase 9 requirements)
- `architecture/STANDARDS.md` — import ordering conventions, zero-breakage requirement

</canonical_refs>

<code_context>
## Existing Code Insights

### Established Patterns
- Phase 8 resolved 468 F821 errors in src/adapters/ using same approach — that work is the primary reference
- Conditional import pattern: `try: import X; FLAG = True; except ImportError: FLAG = False` — used consistently across gpu/, monitoring/, governance/
- Import order: stdlib → third-party → local (`from src.*`)

### Risk Areas
- `src/advanced_analysis/sentiment_analyzer/_sentiment_score_mixin.py` — 4 uses of SNOWNLP_AVAILABLE/SnowNLP/jieba with NO existing definition anywhere; must create the try/except block
- `src/advanced_analysis/decision_models/models/canslim_analyzer.py:160` — `stock_data` used outside `analyze()` scope; needs parameter threading
- `src/advanced_analysis/anomaly/detection.py:405` — `GPU_AVAILABLE` and `IsolationForest` used but not imported; sibling dataclasses.py has them

### Integration Points
- Verification command per directory: `ruff check src/<dir>/ --select F821 --statistics`
- Global verification: `ruff check src/ --select F821 --statistics` must report ≤131 errors (699 − 468 − 220 = 11 remaining for Phase 10)

</code_context>

<specifics>
## Specific Ideas

- Process directories in order: advanced_analysis first (most complex, has non-mechanical errors), then monitoring, then gpu (simplest)
- Per-directory verification after each directory's changes — don't wait until end
- For any file where F821 is NOT a missing import, the executor must read the full file to understand scope before fixing

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---
*Phase: 09-analysis-monitoring-gpu-f821*
*Context gathered: 2026-04-10*
