# Phase 9: Analysis + Monitoring + GPU F821 - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-10
**Phase:** 09-analysis-monitoring-gpu-f821
**Areas discussed:** Conditional imports, Non-mechanical F821 errors, Cross-module types, Plan structure

---

## Conditional Imports

| Option | Description | Selected |
|--------|-------------|----------|
| Module-level try/except + AVAILABLE flag | Add try/except ImportError at module top: SNOWNLP_AVAILABLE = False by default, SnowNLP and jieba imported when available. Same pattern as GPU_AVAILABLE in dataclasses.py. | ✓ |
| Direct imports (hard dependency) | Import snownlp/jieba directly as hard dependencies. Risk: breaks runtime if packages missing. | |

**User's choice:** Module-level try/except + AVAILABLE flag
**Notes:** User flagged this as a must-discuss area — simple direct imports would turn optional deps into hard deps, changing runtime behavior. SNOWNLP_AVAILABLE has NO existing definition anywhere in codebase; must be created from scratch. GPU_AVAILABLE already exists in sibling dataclasses.py — import from there, don't recreate.

---

## Non-mechanical F821 Errors

| Option | Description | Selected |
|--------|-------------|----------|
| Fix signatures only | Add missing parameters to function signatures (e.g. add stock_data param to _generate_summary). Minimal change, preserves existing structure. | ✓ |
| Store as instance attributes | Store on self in analyze(), reference via self.stock_data in helpers. More invasive but avoids parameter threading. | |
| Claude's discretion per-file | Let the executor decide per-file based on what's simplest. | |

**User's choice:** Fix signatures only
**Notes:** User identified that this is NOT purely mechanical. canslim_analyzer.py:160 uses stock_data outside analyze() scope — needs parameter added to method signature. Each non-mechanical fix must be analyzed individually by reading the full file.

---

## Cross-module Types

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical imports only | Import MultiLevelCache from src.gpu.api_system.utils.cache_optimization, IsolationForest from dataclasses.py, etc. No stubs. | ✓ |
| Canonical + TYPE_CHECKING fallback | If canonical import creates circular dependency, fall back to TYPE_CHECKING guard. | |

**User's choice:** Canonical imports only
**Notes:** User explicitly stated: "always from canonical location, never create local stubs." MultiLevelCache canonical at src.gpu.api_system.utils.cache_optimization:303.

---

## Plan Structure

**Decision:** One plan per directory (3 plans total) — enables parallel execution and per-directory verification. This was identified as an execution orchestration concern, not a core risk point.

---

## Claude's Discretion

- Exact import ordering within stdlib/third-party/local groups
- Handling of edge cases where a name's canonical source is ambiguous
- Per-file verification sequence
- Processing order within each directory

## Deferred Ideas

None — discussion stayed within phase scope.
