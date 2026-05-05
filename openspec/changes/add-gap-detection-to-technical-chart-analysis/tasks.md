## 1. Specification

> **历史文档说明**:
> 本文件是历史快照、历史方案或历史总结，不代表当前仓库的唯一事实状态。
> 若需确认当前共享规则、执行口径、目录结构或实现状态，请优先以 `architecture/STANDARDS.md`、根目录 `AGENTS.md`、根目录 `CLAUDE.md`、当前代码与最近一次实际验证结果为准。

- [ ] 1.1 Extend the existing `technical-chart-analysis` capability with reviewed gap detection rather than creating a parallel capability.
- [ ] 1.2 Freeze the gap classification scope to `common`, `breakaway`, `runaway`, and `exhaustion`.
- [ ] 1.3 Freeze the direction scope to `up` and `down`, with reviewed fill states `open`, `partially_filled`, and `filled`.
- [ ] 1.4 Define a typed gap-zone contract on the existing reviewed pattern payload.

## 2. Backend Contract And Detection

- [ ] 2.1 Extend `web/backend/app/api/_technical_patterns_models.py` with typed gap fields, additive `PatternName` expansion, `filled_at: int | null`, and explicit gap-detection `anchor_points=[]` semantics.
- [ ] 2.2 Extend the existing reviewed route in `web/backend/app/api/_technical_patterns_router.py` to document and return gap detections on the same endpoint.
- [ ] 2.3 Implement deterministic reviewed gap detection in `src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py` using the locked heuristic constants and precedence rules from the spec.
- [ ] 2.4 Ensure each raw gap event emits at most one reviewed classification according to explicit precedence.
- [ ] 2.5 Ensure the backend expresses gap fill state as `open`, `partially_filled`, or `filled`.
- [ ] 2.6 Add backend tests for empty payloads, available gap payloads, typed gap fields, `confidence` bands, `anchor_points=[]` semantics, and reviewed `422/503` behavior.

## 3. Frontend Overlay Rendering

- [ ] 3.1 Extend the frontend technical API client and local reviewed TypeScript types in `web/frontend/src/api/index.ts` to accept additive gap detections from the existing reviewed route.
- [ ] 3.2 Add a reviewed automatic `mvpGapZone` overlay implementation under `web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts`.
- [ ] 3.3 Keep manual drawings and automatic gap zones on the same K-line overlay surface.
- [ ] 3.4 Ensure automatic gap zones remain read-only and keep `AUTO` provenance.
- [ ] 3.5 Surface user-facing unavailable/unsupported states without breaking manual drawing behavior.

## 4. Validation

- [ ] 4.1 Run `openspec validate add-gap-detection-to-technical-chart-analysis --strict`.
- [ ] 4.2 Run targeted backend tests for reviewed gap detection and route payload shape.
- [ ] 4.3 Run targeted frontend tests for automatic gap overlay rendering and manual-tool coexistence.
- [ ] 4.4 Verify cross-boundary behavior: backend returns reviewed gap payload, frontend renders the gap zone, and manual drawing remains usable.

## 5. Governance Closeout

- [ ] 5.1 Update `docs/FUNCTION_TREE.md` only after gap detection is implemented and verified.
- [ ] 5.2 Keep alerts, strategy linkage, and non-daily frontend period expansion out of this batch.
