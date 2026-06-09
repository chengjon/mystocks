# Gap Detection In Technical Chart Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add reviewed gap detection (`common_gap`, `breakaway_gap`, `runaway_gap`, `exhaustion_gap`) to the existing technical pattern route and render read-only gap zones on the current K-line chart surface without breaking manual drawing behavior.

**Architecture:** Reuse the existing `technical-chart-analysis` truth pipeline. The backend continues to own reviewed automatic detections through `GET /api/v1/technical/patterns/{symbol}` and extends `PatternDetection` with gap-specific typed fields. The frontend continues to fetch reviewed detections through `technicalApi.getPatterns()` and renders gap detections as a new `mvpGapZone` automatic overlay on the same chart surface as manual drawings and existing automatic pattern segments.

**Tech Stack:** FastAPI, Pydantic, pandas, Vue 3, Vitest, klinecharts `9.8.12`, `UnifiedResponse`, existing `technical_analysis` data-source adapter.

---

## File Structure

### Backend

- Modify: `web/backend/app/api/_technical_patterns_models.py`
  Purpose: expand the reviewed contract with additive gap names, typed gap fields, and `GapZone`.
- Modify: `web/backend/app/api/_technical_patterns_router.py`
  Purpose: keep the existing reviewed route but surface reviewed gap detections and preserve `422/503` behavior.
- Modify: `src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py`
  Purpose: add deterministic reviewed gap detection with locked constants and precedence.
- Modify: `web/backend/app/services/technical_pattern_detection_service.py`
  Purpose: map detector findings to the expanded API model while preserving existing chart-pattern behavior.
- Modify: `web/backend/tests/test_technical_patterns_router_regressions.py`
  Purpose: extend route contract tests for reviewed gap payloads and typed semantics.
- Modify: `web/backend/tests/test_technical_pattern_detection_service.py`
  Purpose: add detector/service tests for reviewed gap classification, fill state, and `confidence` bands.

### Frontend

- Modify: `web/frontend/src/api/index.ts`
  Purpose: extend local reviewed technical pattern types with additive gap fields.
- Modify: `web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts`
  Purpose: add `mvpGapZone` automatic overlay rendering and keep legacy line-segment rendering for anchor-point patterns.
- Modify: `web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts`
  Purpose: verify automatic gap overlay rendering, unsupported-state handling, and coexistence with manual tools.

### Governance Closeout

- Modify: `docs/FUNCTION_TREE.md`
  Purpose: update `2.3 缺口识别` from `📝` only after implementation and verification are complete.

---

### Task 1: Backend Reviewed Contract Expansion

**Files:**
- Modify: `web/backend/app/api/_technical_patterns_models.py`
- Modify: `web/backend/tests/test_technical_patterns_router_regressions.py`

- [ ] **Step 1: Write a failing route-contract test for a reviewed gap payload**

```python
def test_detect_patterns_returns_available_gap_payload(monkeypatch):
    module = _import_patterns_router_module()

    async def _fake_detect(*_args, **_kwargs):
        return [
            PatternDetection(
                pattern_name="breakaway_gap",
                direction="bullish",
                confidence=0.74,
                anchor_points=[],
                gap_side="up",
                gap_fill_status="open",
                gap_zone=GapZone(
                    start_timestamp=1767225600000,
                    end_timestamp=1767312000000,
                    upper_value=10.6,
                    lower_value=10.2,
                    filled_at=None,
                ),
            )
        ]

    monkeypatch.setattr(module, "_detect_patterns_for_symbol", _fake_detect)

    app = FastAPI()
    app.include_router(module.router)
    client = TestClient(app)

    response = client.get("/patterns/600519.SH", params={"period": "daily"})

    assert response.status_code == 200
    payload = response.json()["data"]["patterns"][0]
    assert payload["pattern_name"] == "breakaway_gap"
    assert payload["gap_side"] == "up"
    assert payload["gap_fill_status"] == "open"
    assert payload["anchor_points"] == []
    assert payload["gap_zone"]["filled_at"] is None
```

- [ ] **Step 2: Run the reviewed route regression tests and confirm the new gap payload test fails**

Run:

```bash
pytest web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
```

Expected:

```text
FAIL ... PatternDetection got an unexpected keyword argument 'gap_side'
```

- [ ] **Step 3: Extend the backend reviewed models with additive gap fields**

```python
PatternName = Literal[
    "double_top",
    "double_bottom",
    "head_shoulders_top",
    "head_shoulders_bottom",
    "common_gap",
    "breakaway_gap",
    "runaway_gap",
    "exhaustion_gap",
]
GapSide = Literal["up", "down"]
GapFillStatus = Literal["open", "partially_filled", "filled"]


class GapZone(BaseModel):
    start_timestamp: int
    end_timestamp: int
    upper_value: float
    lower_value: float
    filled_at: int | None


class PatternDetection(BaseModel):
    pattern_name: PatternName
    direction: PatternDirection
    confidence: float = Field(..., ge=0.0, le=1.0)
    anchor_points: list[PatternAnchorPoint] = Field(default_factory=list)
    gap_side: GapSide | None = None
    gap_fill_status: GapFillStatus | None = None
    gap_zone: GapZone | None = None
```

- [ ] **Step 4: Re-run the route regression tests and confirm the reviewed gap payload test passes**

Run:

```bash
pytest web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
```

Expected:

```text
all selected route regression tests pass
```

- [ ] **Step 5: Commit the contract-only slice**

```bash
git add \
  web/backend/app/api/_technical_patterns_models.py \
  web/backend/tests/test_technical_patterns_router_regressions.py
git commit -m "feat(technical): expand reviewed gap contract"
```

---

### Task 2: Backend Gap Detector And Service Mapping

**Files:**
- Modify: `src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py`
- Modify: `web/backend/app/services/technical_pattern_detection_service.py`
- Modify: `web/backend/tests/test_technical_pattern_detection_service.py`
- Modify: `web/backend/app/api/_technical_patterns_router.py`

- [ ] **Step 1: Write failing detector tests for one gap per classification**

```python
def test_detect_patterns_returns_breakaway_gap_with_gap_zone():
    service = TechnicalPatternDetectionService()
    detections = service.detect_from_history_frame(_build_breakaway_gap_frame())

    assert detections
    assert detections[0].pattern_name == "breakaway_gap"
    assert detections[0].gap_side == "up"
    assert detections[0].gap_fill_status == "open"
    assert detections[0].anchor_points == []
    assert detections[0].gap_zone is not None
    assert 0.68 <= detections[0].confidence <= 0.88


def test_detect_patterns_returns_exhaustion_gap_when_fast_fill_confirms():
    service = TechnicalPatternDetectionService()
    detections = service.detect_from_history_frame(_build_exhaustion_gap_frame())

    assert detections
    assert detections[0].pattern_name == "exhaustion_gap"
    assert detections[0].gap_fill_status == "filled"
    assert detections[0].gap_zone is not None
    assert detections[0].gap_zone.filled_at is not None
```

- [ ] **Step 2: Run the detector tests and confirm the new gap tests fail**

Run:

```bash
pytest web/backend/tests/test_technical_pattern_detection_service.py -q --no-cov
```

Expected:

```text
FAIL ... no reviewed gap detections are emitted yet
```

- [ ] **Step 3: Add deterministic reviewed gap helpers to `chart_pattern_mvp.py`**

```python
MIN_GAP_RATIO = 0.005
BREAKAWAY_LOOKBACK_BARS = 10
BREAKAWAY_MAX_PRE_RANGE_RATIO = 0.08
BREAKAWAY_NO_FILL_WINDOW_BARS = 3
RUNAWAY_TREND_LOOKBACK_BARS = 5
RUNAWAY_MIN_TREND_RATIO = 0.04
RUNAWAY_NO_FULL_FILL_WINDOW_BARS = 5
EXHAUSTION_TREND_LOOKBACK_BARS = 5
EXHAUSTION_MIN_TREND_RATIO = 0.06
EXHAUSTION_FILL_CONFIRM_WINDOW_BARS = 3


def _detect_gaps(frame: pd.DataFrame) -> list[DetectedPattern]:
    # iterate raw gaps, classify by precedence, and emit one reviewed detection per raw gap
    ...


def _make_gap_pattern(...):
    return DetectedPattern(
        pattern_name=pattern_name,
        direction="bullish" if gap_side == "up" else "bearish",
        confidence=confidence,
        anchor_points=[],
        gap_side=gap_side,
        gap_fill_status=gap_fill_status,
        gap_zone=DetectedGapZone(...),
    )
```

- [ ] **Step 4: Extend the service mapping to carry gap-specific fields into API models**

```python
PatternDetection(
    pattern_name=finding.pattern_name,
    direction=finding.direction,
    confidence=finding.confidence,
    anchor_points=[] if finding.gap_zone is not None else [
        PatternAnchorPoint(role=point.role, timestamp=point.timestamp, value=point.value)
        for point in finding.anchor_points
    ],
    gap_side=finding.gap_side,
    gap_fill_status=finding.gap_fill_status,
    gap_zone=GapZone(
        start_timestamp=finding.gap_zone.start_timestamp,
        end_timestamp=finding.gap_zone.end_timestamp,
        upper_value=finding.gap_zone.upper_value,
        lower_value=finding.gap_zone.lower_value,
        filled_at=finding.gap_zone.filled_at,
    ) if finding.gap_zone is not None else None,
)
```

- [ ] **Step 5: Keep the router behavior stable and re-run all backend reviewed technical tests**

Run:

```bash
pytest \
  web/backend/tests/test_technical_patterns_router_regressions.py \
  web/backend/tests/test_technical_pattern_detection_service.py \
  -q --no-cov
```

Expected:

```text
all selected backend reviewed technical tests pass
```

- [ ] **Step 6: Commit the backend detector slice**

```bash
git add \
  src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py \
  web/backend/app/services/technical_pattern_detection_service.py \
  web/backend/app/api/_technical_patterns_router.py \
  web/backend/tests/test_technical_pattern_detection_service.py \
  web/backend/tests/test_technical_patterns_router_regressions.py
git commit -m "feat(technical): add reviewed gap detection"
```

---

### Task 3: Frontend Reviewed Type Surface And Failing Overlay Tests

**Files:**
- Modify: `web/frontend/src/api/index.ts`
- Modify: `web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts`

- [ ] **Step 1: Write a failing frontend test for automatic gap-zone rendering**

```ts
it("renders reviewed automatic gap zones while keeping manual tools available", async () => {
  getPatternsMock.mockResolvedValue({
    success: true,
    data: {
      status: "available",
      symbol: "600519.SH",
      period: "daily",
      patterns: [
        {
          pattern_name: "breakaway_gap",
          direction: "bullish",
          confidence: 0.74,
          anchor_points: [],
          gap_side: "up",
          gap_fill_status: "open",
          gap_zone: {
            start_timestamp: 1,
            end_timestamp: 3,
            upper_value: 10.6,
            lower_value: 10.2,
            filled_at: null,
          },
        },
      ],
    },
  });

  const wrapper = mountKLineChart();
  await flushPromises();

  const chartInstance = vi.mocked(init).mock.results.at(-1)?.value;
  expect(chartInstance?.createOverlay).toHaveBeenCalledWith(
    expect.objectContaining({
      name: "mvpGapZone",
      extendData: expect.objectContaining({
        source: "AUTO",
        patternName: "breakaway_gap",
        gapSide: "up",
        gapFillStatus: "open",
      }),
    }),
    "candle_pane",
  );
  expect(wrapper.text()).toContain("趋势线");
});
```

- [ ] **Step 2: Run the frontend unit tests and confirm the gap overlay test fails**

Run:

```bash
cd web/frontend && npx vitest run tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
FAIL ... expected createOverlay to be called with name "mvpGapZone"
```

- [ ] **Step 3: Extend the frontend reviewed technical API types**

```ts
type TechnicalPatternName =
  | "double_top"
  | "double_bottom"
  | "head_shoulders_top"
  | "head_shoulders_bottom"
  | "common_gap"
  | "breakaway_gap"
  | "runaway_gap"
  | "exhaustion_gap";

type TechnicalGapSide = "up" | "down";
type TechnicalGapFillStatus = "open" | "partially_filled" | "filled";

interface TechnicalGapZone {
  start_timestamp: number;
  end_timestamp: number;
  upper_value: number;
  lower_value: number;
  filled_at: number | null;
}
```

- [ ] **Step 4: Re-run the frontend test and confirm it still fails at rendering rather than typing**

Run:

```bash
cd web/frontend && npx vitest run tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
FAIL ... overlay renderer still maps only anchor-point segment patterns
```

- [ ] **Step 5: Commit the reviewed type-surface slice**

```bash
git add \
  web/frontend/src/api/index.ts \
  web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts
git commit -m "test(technical): add reviewed gap overlay expectations"
```

---

### Task 4: Frontend Gap-Zone Overlay Implementation

**Files:**
- Modify: `web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts`
- Modify: `web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts`

- [ ] **Step 1: Add a reviewed `mvpGapZone` custom overlay and branch gap detections away from segment rendering**

```ts
function ensureGapZoneOverlayRegistered() {
  registerOverlay({
    name: "mvpGapZone",
    totalStep: 2,
    createPointFigures: ({ coordinates, overlay }) => {
      if (!coordinates || coordinates.length < 2) return null;
      const [start, end] = coordinates;
      const upper = overlay.extendData?.upperValue ?? Math.min(start.y, end.y);
      const lower = overlay.extendData?.lowerValue ?? Math.max(start.y, end.y);
      return {
        type: "rect",
        attrs: {
          x: Math.min(start.x, end.x),
          y: Math.min(upper, lower),
          width: Math.abs(end.x - start.x),
          height: Math.abs(lower - upper),
        },
      };
    },
  });
}
```

- [ ] **Step 2: Map reviewed gap detections to automatic zone overlays**

```ts
function buildAutomaticPatternOverlays(patterns: TechnicalPatternDetection[]) {
  return patterns.flatMap((pattern) => {
    if (pattern.gap_zone) {
      return [{
        name: "mvpGapZone",
        paneId: "candle_pane",
        points: [
          { timestamp: pattern.gap_zone.start_timestamp, value: pattern.gap_zone.upper_value },
          { timestamp: pattern.gap_zone.end_timestamp, value: pattern.gap_zone.lower_value },
        ],
        extendData: {
          source: "AUTO",
          patternName: pattern.pattern_name,
          gapSide: pattern.gap_side,
          gapFillStatus: pattern.gap_fill_status,
          upperValue: pattern.gap_zone.upper_value,
          lowerValue: pattern.gap_zone.lower_value,
        },
      }];
    }

    return buildAutomaticSegmentOverlays(pattern);
  });
}
```

- [ ] **Step 3: Keep unsupported/failure behavior stable and run targeted frontend tests**

Run:

```bash
cd web/frontend && npx vitest run \
  tests/unit/components/technical/useChartOverlays.spec.ts \
  tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
all selected frontend overlay tests pass
```

- [ ] **Step 4: Run targeted lint on the changed frontend files**

Run:

```bash
cd web/frontend && npx eslint --no-warn-ignored \
  src/api/index.ts \
  src/components/technical/composables/useKLinePatternOverlays.ts \
  tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
no output
```

- [ ] **Step 5: Commit the frontend overlay slice**

```bash
git add \
  web/frontend/src/api/index.ts \
  web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts \
  web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts
git commit -m "feat(technical): render reviewed gap zones"
```

---

### Task 5: Governance Closeout And Final Verification

**Files:**
- Modify: `docs/FUNCTION_TREE.md`

- [ ] **Step 1: Update the FUNCTION_TREE entry only after backend and frontend verification are green**

```markdown
| 缺口识别 | ✅ | `web/backend/app/api/_technical_patterns_router.py`<br>`web/frontend/src/components/technical/composables/useKLinePatternOverlays.ts` | reviewed common / breakaway / runaway / exhaustion gaps |
```

- [ ] **Step 2: Run governance verification**

Run:

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py tests/unit/governance/test_function_tree_catalog.py -q --no-cov
```

Expected:

```text
all selected governance tests pass
```

- [ ] **Step 3: Run the final reviewed technical verification bundle**

Run:

```bash
pytest \
  web/backend/tests/test_technical_patterns_router_regressions.py \
  web/backend/tests/test_technical_pattern_detection_service.py \
  tests/unit/governance/test_function_tree_doc_sync.py \
  tests/unit/governance/test_function_tree_catalog.py \
  -q --no-cov

cd web/frontend && npx vitest run \
  tests/unit/components/technical/useChartOverlays.spec.ts \
  tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
all selected backend, frontend, and governance checks pass
```

- [ ] **Step 4: Commit governance closeout**

```bash
git add docs/FUNCTION_TREE.md
git commit -m "docs(function-tree): close gap detection mvp"
```

- [ ] **Step 5: Request a final code review before claiming completion**

Run:

```bash
git status --short
```

Expected:

```text
no unintended files in this micro-batch; if the repo is globally dirty, note that only the reviewed technical-chart-analysis paths were touched in this batch
```
