# OpenSpec Review: add-kline-drawing-and-pattern-overlays

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

**Reviewer**: Claude (automated review)
**Date**: 2026-05-05
**Verdict**: APPROVE WITH CONDITIONS

---

## Summary

This change proposes a focused MVP that adds interactive K-line drawing tools (frontend) and backend-driven chart pattern detection overlays, sharing a single chart overlay surface. The proposal is well-scoped, the truth-ownership split is sound, and the design decisions are defensible. The main concerns are: (1) a missing concrete API contract, (2) unclear composable extraction strategy, and (3) no acceptance test criteria for the backend detection quality.

---

## File-by-file Review

### 1. proposal.md - APPROVE

**Strengths**:
- Problem statement is precise and grounded in FUNCTION_TREE gaps (`2.2 画线工具 🚧`, `2.3 图表形态 🚧`).
- "Two parallel truth sources" risk is a genuine architectural concern; calling it out early is valuable.
- Non-goals are clear and appropriately restrictive (no persistence, no Fibonacci, no alert integration).
- The provenance separation rule (manual = frontend-owned, automatic = backend-owned) is the right call.

**Issues**:

| # | Severity | Issue |
|---|----------|-------|
| P1 | Medium | The "What Changes" section mentions `technical-chart-analysis` capability but doesn't specify where this capability definition lives (file path, module boundary). For a cross-cutting capability touching both frontend and backend, the anchor file should be named. |
| P2 | Low | Affected code lists `web/backend/app/api/` without specifying which route file. A grep shows no dedicated pattern route exists today (`glob pattern*` returns empty). The proposal should clarify whether this means creating a new route or extending an existing one like `advanced_analysis_api.py`. |

---

### 2. design.md - APPROVE WITH CONDITIONS

**Strengths**:
- Context section accurately describes the current state: KLineChart has rendering but no drawing tools; backend has placeholder labels, not real detection.
- The KLineChart v9 overlay API reference (`createOverlay`, `registerOverlay`, `registerFigure`) is confirmed present in `web/frontend/src/types/klinecharts.d.ts:224-227,318-322`. The design's reliance on these APIs is grounded.
- Risk about KLineChart.vue becoming too large is validated: the file is already 437 lines. Extracting to a composable is not optional, it is required.
- The "no fabricated inference" rule is excellent and prevents the most likely shortcut during implementation.

**Issues**:

| # | Severity | Issue |
|---|----------|-------|
| D1 | **High** | No concrete API contract defined. The design says backend must return `pattern_name`, `direction`, `confidence`, `anchor_points` but does not specify: (a) the endpoint path, (b) request/response schema, (c) HTTP status codes for empty results vs errors. This should be a Pydantic model or OpenAPI fragment in the design, not left to implementation time. |
| D2 | **High** | No `anchor_points` schema definition. The design says anchor points must have "time and price dimensions" but doesn't specify: How many anchor points per pattern? Is the count fixed per pattern type (e.g., double_top = 5 points: left peak, trough, right peak, neckline, target) or variable? This directly affects frontend rendering and must be frozen before implementation. |
| D3 | Medium | Migration plan step 2 says "frontend overlay adapter" but doesn't name the composable file or define its public interface. Given KLineChart.vue is already 437 lines, the extraction target should be explicit (e.g., `useChartOverlays.ts` or `ChartOverlayAdapter.ts`). |
| D4 | Medium | Open Question 1 (existing endpoint vs dedicated route) should be resolved before tasks.md is executed. If the answer is "dedicated route," the backend task list needs a route-creation task; if "existing endpoint," the impact on `advanced_analysis_api.py` needs assessment. |
| D5 | Low | The design mentions KLineChart v9 "overlay/figure API surface" but doesn't address version pinning. Is the project locked to v9? If klinecharts upgrades, the overlay API may change. A version constraint note would reduce future risk. |

---

### 3. tasks.md - APPROVE WITH CONDITIONS

**Strengths**:
- Task decomposition follows the proposal's split cleanly: Spec → Backend → Frontend → Validation → Follow-Up.
- Task 2.3 ("return empty, not fabricated") is explicitly tracked, which prevents the most common shortcut.
- Task 4.4 (re-run FUNCTION_TREE governance checks) shows awareness of the project's governance process.

**Issues**:

| # | Severity | Issue |
|---|----------|-------|
| T1 | **High** | Backend task 2.1 says "Replace placeholder or inferred chart-pattern results" but no existing pattern detection code was found in the codebase. `grep pattern detect` in `web/backend/` returns only docstrings and a test script. There is nothing to "replace" — this task is actually "create from scratch." The task should acknowledge this to set accurate expectations. |
| T2 | Medium | No task for defining the Pydantic request/response models for the pattern endpoint. This should be task 2.0 or embedded in 2.1, because the frontend tasks depend on a stable contract. |
| T3 | Medium | Frontend tasks (3.1-3.6) are all at the same level, but there are hidden dependencies: 3.2 depends on 3.1 (adapter), and 3.4 depends on the backend contract from 2.x. The task list should reflect these dependencies or at least note the critical path. |
| T4 | Medium | No integration/E2E test task. Task 4.3 says "targeted frontend tests" but there's no task for verifying the full flow: backend returns pattern → frontend renders overlay → user can still draw manually. This cross-boundary verification is the highest-risk area. |
| T5 | Low | Task 3.2 mentions "KLineChart official overlay primitives or a reviewed custom overlay." This "or" should be resolved during implementation planning, not deferred. Rectangle overlay in particular needs an upfront decision (built-in vs custom `registerOverlay`). |

---

### 4. specs/technical-chart-analysis/spec.md - APPROVE WITH CONDITIONS

**Strengths**:
- Scenario-based requirements with WHEN/THEN/AND structure are clear and testable.
- "Graceful Degradation" requirement is well-defined and often overlooked in chart feature specs.
- The "protected overlay" scenario (automatic = read-only, no implicit conversion) prevents a real UX pitfall.

**Issues**:

| # | Severity | Issue |
|---|----------|-------|
| S1 | **High** | Missing: anchor point count per pattern type. The spec says anchor points "SHALL be chart-renderable with both time and price dimensions" but never specifies the expected schema per pattern. For example, `double_top` should have a defined set: `{left_peak, trough, right_peak, neckline}` at minimum. Without this, frontend rendering is underspecified and backend detection has no structural validation target. |
| S2 | Medium | Missing: `confidence` threshold or range. The spec requires `confidence` in the response but doesn't define whether it's 0-1, 0-100, or a categorical label (low/medium/high). This affects both backend implementation and any future "filter by confidence" UI. |
| S3 | Medium | Missing: overlay styling/provenance specification. The spec says "SHALL visually distinguish manual overlays from automatic pattern overlays" but provides no guidance on what "visually distinct" means (different color palette? dashed vs solid? label prefix? opacity?). This is testable but the acceptance criteria are vague. |
| S4 | Low | The "Graceful Degradation" scenario says "surface the automatic-pattern failure as a localized loading or error state." This introduces i18n concerns that are not discussed anywhere else in the change set. If the project uses a specific i18n approach, it should be noted; if not, "localized" should be replaced with "user-facing." |

---

## Overall Assessment

### Must-Fix Before Implementation (Blocks)

1. **Define the pattern-result Pydantic model** with explicit `anchor_points` schema per pattern type (addresses D1, D2, S1). This is the contract that both frontend and backend tasks depend on. Without it, implementation will drift.

2. **Clarify backend starting point** (addresses T1). There is no existing pattern detection code to "replace." Task 2.1 must be rewritten as "Implement chart pattern detection for the 4 MVP patterns" with an acknowledgment that this is net-new work.

3. **Resolve Open Question 1** (addresses D4): dedicated route vs existing endpoint. This determines whether the backend task list needs a route-creation task and whether `advanced_analysis_api.py` is in scope.

### Should-Fix Before Implementation (Recommended)

4. **Name the overlay composable** and define its public interface (addresses D3, T3). Given KLineChart.vue is already 437 lines, the extraction target must be explicit.

5. **Define `confidence` range** (addresses S2). A simple "0.0-1.0 float" is sufficient for MVP.

6. **Add an integration test task** (addresses T4). Cross-boundary verification is the highest-risk area and the task list has no task for it.

### Nice-to-Have (Non-blocking)

7. Pin klinecharts version constraint note (D5).
8. Specify "visually distinct" rendering approach (S3) — can be deferred to implementation.
9. Clarify "localized" i18n expectation (S4).

---

## Codebase Validation Notes

The following were verified against the live codebase during this review:

| Claim in Proposal | Verification | Status |
|-------------------|-------------|--------|
| KLineChart.vue exists | `web/frontend/src/components/technical/KLineChart.vue` — 437 lines | Confirmed |
| KLineChart overlay APIs available | `klinecharts.d.ts:224-227` — `createOverlay`, `getOverlays`, `overrideOverlay`, `removeOverlay`; `:318` — `registerOverlay` | Confirmed |
| FUNCTION_TREE 2.2 画线工具 = 🚧 | `docs/FUNCTION_TREE.md:181` — `画线工具 \| 🚧 \| - \| 计划中` | Confirmed |
| FUNCTION_TREE 2.3 图表形态 = 🚧 | `docs/FUNCTION_TREE.md:188` — `图表形态 \| 🚧 \| 头肩顶底、双顶双底` | Confirmed |
| Backend has placeholder pattern routes | No dedicated pattern route found; `advanced_analysis_api.py:154` mentions patterns in docstrings only | **Partially confirmed** — docstrings exist, actual detection endpoints do not |
| `src/advanced_analysis/` has analyzers | 70+ files found, but none for chart pattern detection | Confirmed — gap is real |

---

*End of review.*
