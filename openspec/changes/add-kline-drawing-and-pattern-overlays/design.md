## Context

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

The repository already has a working K-line chart surface and a partially wired technical-analysis flow, but the missing pieces sit on opposite sides of the stack:

1. The frontend chart can render OHLCV data and indicators, but it does not expose interactive drawing tools.
2. The backend has pattern-related routes and analyzers, but the current implementations are still placeholders, inferred labels, or `return []` stubs rather than a reviewed detection contract.
3. The provided KLineChart v9 reference shows a stable overlay/figure API surface (`createOverlay`, `getOverlays`, `overrideOverlay`, `removeOverlay`, built-in line overlays, and custom overlay registration) that is appropriate for the manual-drawing layer.
4. The repository already mounts a dedicated placeholder pattern route in `web/backend/app/api/_technical_patterns_router.py`, included by `web/backend/app/api/technical_analysis.py` under the versioned technical-analysis router. The reviewed MVP should upgrade that route into a real detection contract rather than inventing a second entry point.

The change therefore needs one shared chart-surface contract, but two different truths:

- manual overlays are a frontend interaction concern;
- automatic pattern detections are a backend analysis concern.

## Goals

- Add a reviewed capability contract for K-line manual drawing and automatic chart-pattern overlays.
- Reuse a single chart overlay surface for both manual and automatic annotations.
- Make backend pattern detection the only truth source for automatic chart patterns.
- Keep the MVP intentionally narrow enough to implement and verify without introducing a parallel chart workbench.

## Non-Goals

- Persisting manual drawings across sessions or users
- Adding Fibonacci tools, freehand tools, wedges, triangles, cup-and-handle, or gap detection in this batch
- Converting automatic pattern overlays into editable/manual overlays
- Integrating pattern detections directly into trading execution or alert firing in this change

## Decisions

- Decision: Create a new `technical-chart-analysis` capability.
  - Rationale: this is a stable business capability with both frontend and backend behavior, not just a page-local UI tweak.

- Decision: Split truth ownership by responsibility.
  - Manual drawing overlays are frontend-owned interaction state.
  - Automatic chart patterns are backend-owned analysis results.
  - Rationale: this avoids frontend-only heuristics becoming a second pattern truth source.

- Decision: Use the official KLineChart overlay primitives as the default frontend implementation path.
  - Manual trend lines and horizontal lines should use built-in overlay types where possible.
  - Rectangle drawing SHALL use a reviewed custom overlay built on the official overlay/figure APIs because the supported built-in overlay set does not provide a canonical editable rectangle drawing primitive.
  - Rationale: this keeps the chart integration aligned with the supported library surface rather than inventing a separate canvas layer.

- Decision: Keep the manual-drawing MVP to three tools only.
  - `trendline`
  - `horizontal line`
  - `rectangle`
  - Rationale: these tools cover the most common K-line annotation use cases while keeping toolbar, overlay state, and test scope bounded.

- Decision: Keep the backend pattern MVP to four outcomes only.
  - `double_top`
  - `double_bottom`
  - `head_shoulders_top`
  - `head_shoulders_bottom`
  - Rationale: these are the patterns already implied by current repository placeholders and FUNCTION_TREE wording, and they are enough to exercise the contract without pretending broader pattern coverage exists.

- Decision: Require structured pattern results.
  - Each detection result must include `pattern_name`, `direction`, `confidence`, and `anchor_points`.
  - Each anchor point must be chart-renderable and carry both time and price dimensions.
  - Rationale: string-only labels cannot drive overlay rendering or reviewable detection evidence.

- Decision: Freeze the MVP pattern endpoint contract on the existing dedicated route path.
  - Endpoint: `GET /api/v1/technical/patterns/{symbol}`
  - Request query:
    - `period`: `daily | weekly | monthly`
  - Success responses:
    - `200 available`: reviewed detection payload with one or more detections
    - `200 empty`: reviewed payload with `patterns: []`
  - Error responses:
    - `422`: invalid symbol or period
    - `503`: pattern analysis unavailable or upstream analysis dependency unavailable
  - Rationale: this keeps the reviewed MVP on the current versioned technical-analysis surface and avoids spawning a parallel endpoint family.

- Decision: Freeze the detection payload schema for the MVP.
  - Top-level `data` payload:
    - `status`: `available | empty`
    - `symbol`: normalized symbol
    - `period`: normalized period
    - `patterns`: list of `PatternDetection`
  - `PatternDetection`:
    - `pattern_name`: `double_top | double_bottom | head_shoulders_top | head_shoulders_bottom`
    - `direction`: `bullish | bearish`
    - `confidence`: float in the inclusive range `0.0-1.0`
    - `anchor_points`: ordered list of `PatternAnchorPoint`
  - `PatternAnchorPoint`:
    - `role`: pattern-defined role name
    - `timestamp`: millisecond epoch value
    - `value`: numeric price value
  - Rationale: both backend validation and frontend overlay rendering need one frozen structural target.

- Decision: Freeze the minimum ordered anchor-point set per pattern type.
  - `double_top`: `left_peak`, `neckline`, `right_peak`
  - `double_bottom`: `left_bottom`, `neckline`, `right_bottom`
  - `head_shoulders_top`: `left_shoulder`, `left_neckline`, `head`, `right_neckline`, `right_shoulder`
  - `head_shoulders_bottom`: `left_shoulder`, `left_neckline`, `head`, `right_neckline`, `right_shoulder`
  - Rationale: the frontend needs deterministic anchors to render shape lines, and the backend needs a structural validation target beyond “some points”.

- Decision: Name the frontend overlay extraction target explicitly.
  - The reviewed extraction target is `web/frontend/src/components/technical/composables/useChartOverlays.ts`.
  - Minimum public surface:
    - `activeTool`
    - `manualOverlayIds`
    - `automaticOverlayIds`
    - `selectTool(toolName)`
    - `syncAutomaticOverlays(patterns)`
    - `removeManualOverlay(id)`
    - `clearManualOverlays()`
    - `disposeOverlays()`
  - Rationale: `KLineChart.vue` is already large enough that overlay orchestration needs an explicit extraction boundary before implementation starts.

- Decision: Automatic overlays are read-only and visually distinct from manual overlays.
  - Manual overlays use the manual tool palette and solid strokes.
  - Automatic overlays use a dedicated automatic-analysis palette, dashed strokes, and an `AUTO` source label or equivalent provenance marker.
  - Rationale: users must be able to see provenance at a glance and must not accidentally treat backend detections as manual edits.

- Decision: Placeholder pattern endpoints must not masquerade as real detection.
  - Rationale: a response inferred only from symbol or period is not a technical-pattern detection result and must not be exposed as one under the reviewed MVP contract.

- Decision: Bind the frontend integration to the currently typed KLineChart v9 surface.
  - The repository currently types `klinecharts` as `9.8.12` in `web/frontend/src/types/klinecharts.d.ts`.
  - Any future major-version overlay API change requires re-review of this capability before extending or replacing the drawing integration.
  - Rationale: the MVP depends on concrete overlay APIs, not on a version-agnostic abstraction.

## Risks / Trade-offs

- Risk: the existing `KLineChart.vue` component could become too large if all overlay state is embedded directly into it.
  - Mitigation: keep chart-surface state and overlay orchestration in a dedicated composable or adapter layer instead of pushing all behavior into the view component.

- Risk: backend pattern detection may initially produce conservative or sparse results.
  - Mitigation: the MVP contract allows empty result sets and does not require every symbol/timeframe to emit a pattern.

- Risk: users may expect more drawing tools or more pattern families immediately.
  - Mitigation: the proposal explicitly freezes the MVP scope and treats additional tools/patterns as follow-up changes.

## Migration Plan

1. Add the `technical-chart-analysis` capability contract.
2. Implement a frontend overlay adapter that supports the three approved manual tools.
3. Upgrade the existing dedicated pattern route at `web/backend/app/api/_technical_patterns_router.py` from placeholder inference to the reviewed detection contract.
4. Render backend pattern detections on the same K-line surface with read-only provenance styling.
5. Update FUNCTION_TREE only after the implemented MVP is verified.

## Open Questions

- Whether manual drawings should remain page-local state only in the first shipped batch, or also support URL/session restoration in a later change
