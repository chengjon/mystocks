# Review: add-gap-detection-to-technical-chart-analysis (4 documents)

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

**Type**: md / proposal+arch+plan+spec | **Perspective**: auto | **Date**: 2026-05-06

## Summary

The four OpenSpec documents form a coherent, well-scoped proposal to add gap detection to the existing reviewed technical pattern route. All 11 referenced source files exist in the codebase, the FUNCTION_TREE entry confirms gap detection is planned (📝), and the design correctly builds on the existing `PatternDetection` / `useKLinePatternOverlays` pipeline. The main concerns are: (1) silent gaps around how existing `confidence` and `anchor_points` fields behave for gap detections, (2) no quantitative heuristic thresholds in the spec, and (3) missing TypeScript type-impact discussion.

## Verified

- All 11 referenced files exist in the codebase (confirmed via Glob)
- `PatternDetection` class exists in `_technical_patterns_models.py:23` — current `PatternName` is `Literal["double_top", "double_bottom", "head_shoulders_top", "head_shoulders_bottom"]`
- `GET /api/v1/technical/patterns/{symbol}` route exists in `_technical_patterns_router.py:84`
- `getPatterns` API client function exists in `api/index.ts:236` returning `UnifiedResponse<TechnicalPatternData>`
- `AUTO` provenance is implemented in `useKLinePatternOverlays.ts:81` (`source: "AUTO"`)
- FUNCTION_TREE line 189 confirms `缺口识别 | 📝 | 计划中`
- No existing gap detection code in `chart_pattern_mvp.py` — clean extension target
- `PatternDirection = Literal["bullish", "bearish"]` aligns with proposed `gap_side→direction` mapping
- Proposal Non-Goals correctly bound scope (no alerts, no trading signals, daily-only frontend)
- Design Decision 1 (reuse existing route) is well-justified and avoids parallel truth sources
- Tasks follow the migration plan ordering: spec → backend tests → backend impl → frontend tests → frontend impl → governance

## Issues

- [ ] **[HIGH]** `confidence` field behavior unspecified for gap detections — proposal/design/spec all three documents
      Evidence: `PatternDetection` requires `confidence: float` (models.py:28), but none of the 4 documents state what confidence value gap detections should carry. If gaps use deterministic heuristics, should confidence be fixed at 1.0? Or should it reflect heuristic certainty? This ambiguity will cause implementer confusion and inconsistent test expectations.

- [ ] **[HIGH]** `anchor_points` field behavior unspecified for gap detections — proposal/design/spec all three documents
      Evidence: `PatternDetection` includes `anchor_points: list[PatternAnchorPoint]` (models.py:29-32). Gap zones use `GapZone` instead, but the design does not clarify whether `anchor_points` should be empty for gap detections, or whether gap zone corners should also be expressed as anchor points. This affects the frontend overlay contract.

- [ ] **[MED]** No quantitative heuristic thresholds provided — design Decision 3, spec "One raw gap emits one reviewed classification"
      Evidence: Design uses qualitative descriptions ("明显单边延伸", "短窗口内", "近端整理区间外部跳出") without defining what these mean in bars/percentages. The spec states "deterministic precedence order" but does not lock down the numeric parameters. This makes it impossible to write unambiguous acceptance tests for gap classification.
      Recommendation: Add a heuristic constants table to the spec (e.g., "exhaustion: requires ≥N bars of unidirectional move before gap; short window = M bars after gap").

- [ ] **[MED]** TypeScript type impact not discussed — design section 2, tasks 3.1
      Evidence: `api/index.ts:236` returns `UnifiedResponse<TechnicalPatternData>`. The design references extending the API client to accept gap detections (task 3.1) but does not specify whether `TechnicalPatternData` (the TypeScript type) needs new fields, or whether a discriminated union approach is needed. Without this, the frontend implementation task is underspecified.

- [ ] **[MED]** `filled_at` field cardinality ambiguous — design Decision 2, spec "Gap zone is chart-renderable"
      Evidence: Design says `GapZone` "应至少包含...filled_at" without specifying if it's `Optional[datetime]` or always present as `null` for unfilled gaps. The spec says "SHALL include filled_at when the reviewed gap has been fully filled" (conditional), but the design does not align — is it a required nullable field or an optional field? This affects Pydantic model definition.

- [ ] **[MED]** Backward compatibility of `PatternName` Literal expansion not addressed — design Decision 2
      Evidence: Current `PatternName` is a `Literal` with 4 entries (models.py:9). Expanding it to 8 entries is backward-compatible for the router response, but any existing consumers that exhaustively switch on `PatternName` will get type errors. The documents should note this is an additive-only change and verify no downstream code breaks.

- [ ] **[LOW]** `mvpGapZone` overlay naming convention not aligned with existing names — design Decision 4
      Evidence: Design proposes `mvpGapZone` custom overlay in `useKLinePatternOverlays.ts`. Existing overlays use names like `mvpPatternLine` (implied by the overlay registration pattern). The naming should follow whatever convention already exists for consistency.

- [ ] **[LOW]** Tasks reference `openspec validate` command without confirming it exists — tasks 4.1
      Evidence: Task 4.1 says "Run `openspec validate add-gap-detection-to-technical-chart-analysis --strict`". This assumes the openspec CLI supports a `validate` subcommand with `--strict` flag. Should verify this command actually exists in the project's openspec tooling.

## Suggestions

- Add a "Gap Detection Field Mapping" subsection to the design that explicitly maps every existing `PatternDetection` field to its gap-detection semantics, including `confidence`, `anchor_points`, and `direction`.
- Add a "Heuristic Constants" table to the spec with concrete bar counts and percentage thresholds for each gap classification, making acceptance tests deterministic.
- Add a "TypeScript Type Changes" subsection to the design specifying how `TechnicalPatternData`, the frontend pattern types, and any new interfaces (e.g., `GapZone`) should be defined.
- Clarify `filled_at` as either `Optional[datetime] = None` (preferred for Pydantic) or `datetime | None` in the GapZone contract.
- Include a backward-compatibility note that `PatternName` Literal expansion is additive-only and verify via grep that no consumer does exhaustive pattern matching on the current 4-value set.

## Verdict

**APPROVE_WITH_NOTES** — The proposal is well-scoped, correctly reuses the existing pipeline, and all referenced files exist. The two HIGH items (unspecified `confidence` and `anchor_points` behavior for gap detections) should be resolved before implementation begins, as they directly affect the backend contract and frontend overlay logic. The MED items around heuristic thresholds and TypeScript types should also be addressed to prevent ambiguity during implementation.
