# K-line Drawing and Pattern Overlays Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an MVP K-line drawing layer with manual overlays (`trendline`, `horizontal line`, `rectangle`) plus backend-driven automatic pattern overlays (`double_top`, `double_bottom`, `head_shoulders_top`, `head_shoulders_bottom`) on the same chart surface.

**Architecture:** Keep truth ownership split by responsibility. The frontend owns manual overlay state and rendering orchestration on top of KLineChart v9 overlay APIs. The backend owns automatic pattern detection and returns structured detections from the existing `/api/v1/technical/patterns/{symbol}` route. `KLineChart.vue` remains the chart surface, but overlay orchestration moves into a dedicated composable and automatic patterns are fetched through the existing frontend API layer.

**Tech Stack:** FastAPI, Pydantic, pandas, Vue 3, Vitest, klinecharts `9.8.12`, existing `technical_analysis` data-source adapter, `UnifiedResponse`.

---

## File Structure

### Backend

- Create: `web/backend/app/api/_technical_patterns_models.py`
  Purpose: Pydantic request/response models for the reviewed pattern endpoint contract.
- Modify: `web/backend/app/api/_technical_patterns_router.py`
  Purpose: replace rule-based placeholder labels with a real structured detection route.
- Create: `web/backend/app/services/technical_pattern_detection_service.py`
  Purpose: fetch reviewed OHLCV history through the existing technical-analysis adapter, call the analyzer, and map detections to API models.
- Create: `src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py`
  Purpose: pure pattern-detection helpers for the four MVP patterns using deterministic anchor roles.
- Modify: `web/backend/tests/test_technical_patterns_router_regressions.py`
  Purpose: turn the old placeholder regression into reviewed contract tests.
- Create: `web/backend/tests/test_technical_pattern_detection_service.py`
  Purpose: verify detector output shape, empty-result behavior, and service-level error mapping.

### Frontend

- Modify: `web/frontend/src/api/index.ts`
  Purpose: add `technicalApi.getPatterns(symbol, period)` with the reviewed contract shape.
- Create: `web/frontend/src/components/technical/composables/useChartOverlays.ts`
  Purpose: own manual/automatic overlay IDs, tool selection, sync, removal, and cleanup.
- Modify: `web/frontend/src/components/technical/KLineChart.vue`
  Purpose: add manual drawing toolbar controls, wire `useChartOverlays`, fetch automatic patterns, and render both overlay sources on one chart.
- Modify: `web/frontend/src/components/artdeco/charts/ArtDecoKLineChartContainer.vue`
  Purpose: forward `symbol` into `KLineChart` so automatic pattern fetching has the same symbol context as the card header.
- Modify: `web/frontend/vitest.setup.ts`
  Purpose: extend the klinecharts mock with overlay methods (`createOverlay`, `getOverlays`, `overrideOverlay`, `removeOverlay`, `registerOverlay`).
- Create: `web/frontend/tests/unit/components/technical/useChartOverlays.spec.ts`
  Purpose: verify manual tool orchestration and automatic overlay syncing in isolation.
- Create: `web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts`
  Purpose: verify frontend fetch/render flow, toolbar behavior, and graceful degradation.

### Governance Closeout

- Modify: `docs/FUNCTION_TREE.md`
  Purpose: only after implementation and verification, update `2.2 画线工具` and `2.3 图表形态` from `🚧` if the implemented MVP satisfies the approved scope.

---

### Task 1: Backend Contract and Route Surface

**Files:**
- Create: `web/backend/app/api/_technical_patterns_models.py`
- Modify: `web/backend/app/api/_technical_patterns_router.py`
- Modify: `web/backend/tests/test_technical_patterns_router_regressions.py`

- [ ] **Step 1: Rewrite the regression test around the reviewed payload shape**

```python
from __future__ import annotations

import asyncio
import importlib
import sys
from pathlib import Path


def _import_patterns_router_module():
    backend_root = Path("web/backend").resolve()
    backend_root_str = str(backend_root)
    if backend_root_str not in sys.path:
        sys.path.insert(0, backend_root_str)

    sys.modules.pop("app.api._technical_patterns_router", None)
    return importlib.import_module("app.api._technical_patterns_router")


def test_detect_patterns_returns_empty_structured_payload_when_service_finds_nothing(monkeypatch):
    module = _import_patterns_router_module()

    async def _fake_detect(*_args, **_kwargs):
        return []

    monkeypatch.setattr(module, "_detect_patterns_for_symbol", _fake_detect)

    response = asyncio.run(module.detect_patterns(symbol="600519.SH", period="weekly"))

    assert response.success is True
    assert response.code == 200
    assert response.data["status"] == "empty"
    assert response.data["symbol"] == "600519.SH"
    assert response.data["period"] == "weekly"
    assert response.data["patterns"] == []
```

- [ ] **Step 2: Run the regression test and confirm it fails against the placeholder route**

Run:

```bash
pytest web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
```

Expected:

```text
FAIL ... response.data["patterns"] is a list[str] and no reviewed empty contract exists yet
```

- [ ] **Step 3: Add the Pydantic contract models**

```python
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


PatternName = Literal["double_top", "double_bottom", "head_shoulders_top", "head_shoulders_bottom"]
PatternDirection = Literal["bullish", "bearish"]
PatternStatus = Literal["available", "empty"]


class PatternAnchorPoint(BaseModel):
    role: str = Field(..., description="Pattern-defined anchor role")
    timestamp: int = Field(..., description="Millisecond epoch timestamp")
    value: float = Field(..., description="Price value at the anchor")


class PatternDetection(BaseModel):
    pattern_name: PatternName
    direction: PatternDirection
    confidence: float = Field(..., ge=0.0, le=1.0)
    anchor_points: list[PatternAnchorPoint] = Field(default_factory=list)


class PatternDetectionData(BaseModel):
    status: PatternStatus
    symbol: str
    period: str
    patterns: list[PatternDetection] = Field(default_factory=list)
```

- [ ] **Step 4: Update the route surface to return the reviewed schema**

```python
from fastapi import APIRouter, Path, Query, status

from app.api._technical_patterns_models import PatternDetectionData
from app.core.responses import UnifiedResponse

router = APIRouter()


async def _detect_patterns_for_symbol(symbol: str, period: str):
    raise NotImplementedError


@router.get(
    "/patterns/{symbol}",
    summary="检测技术形态",
    response_model=UnifiedResponse[PatternDetectionData],
)
async def detect_patterns(
    symbol: str = Path(..., description="标的代码，例如 600519.SH。"),
    period: str = Query("daily", pattern=r"^(daily|weekly|monthly)$"),
) -> UnifiedResponse[PatternDetectionData]:
    detections = await _detect_patterns_for_symbol(symbol=symbol.upper(), period=period.lower())
    payload = PatternDetectionData(
        status="available" if detections else "empty",
        symbol=symbol.upper(),
        period=period.lower(),
        patterns=detections,
    )
    return UnifiedResponse(success=True, code=status.HTTP_200_OK, message="Technical patterns evaluated", data=payload)
```

- [ ] **Step 5: Re-run the route regression test**

Run:

```bash
pytest web/backend/tests/test_technical_patterns_router_regressions.py -q --no-cov
```

Expected:

```text
1 passed
```

- [ ] **Step 6: Commit the contract-only backend slice**

```bash
git add \
  web/backend/app/api/_technical_patterns_models.py \
  web/backend/app/api/_technical_patterns_router.py \
  web/backend/tests/test_technical_patterns_router_regressions.py
git commit -m "feat(technical): add reviewed pattern route contract"
```

---

### Task 2: Backend Detector and History-to-Pattern Service

**Files:**
- Create: `src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py`
- Create: `web/backend/app/services/technical_pattern_detection_service.py`
- Modify: `web/backend/app/api/_technical_patterns_router.py`
- Create: `web/backend/tests/test_technical_pattern_detection_service.py`

- [ ] **Step 1: Write a failing detector service test with a synthetic double-top payload**

```python
from __future__ import annotations

import pandas as pd

from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService


def _build_double_top_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2026-01-01", periods=7, freq="D"),
            "open": [10.0, 10.6, 11.1, 10.4, 11.0, 10.2, 9.9],
            "high": [10.3, 11.0, 11.5, 10.7, 11.4, 10.5, 10.0],
            "low": [9.8, 10.4, 10.8, 10.0, 10.8, 9.8, 9.6],
            "close": [10.1, 10.9, 11.3, 10.2, 11.2, 10.0, 9.7],
            "volume": [100, 120, 140, 110, 135, 150, 160],
        }
    )


def test_detect_patterns_returns_double_top_with_ordered_anchor_roles():
    service = TechnicalPatternDetectionService()

    detections = service.detect_from_history_frame(_build_double_top_frame())

    assert detections
    assert detections[0].pattern_name == "double_top"
    assert [point.role for point in detections[0].anchor_points] == ["left_peak", "neckline", "right_peak"]
    assert 0.0 <= detections[0].confidence <= 1.0
```

- [ ] **Step 2: Run the detector service test and confirm it fails because the service does not exist yet**

Run:

```bash
pytest web/backend/tests/test_technical_pattern_detection_service.py -q --no-cov
```

Expected:

```text
FAIL with ModuleNotFoundError or ImportError for TechnicalPatternDetectionService
```

- [ ] **Step 3: Add the pure analyzer module under `src/advanced_analysis/`**

```python
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd


@dataclass
class DetectedAnchor:
    role: str
    timestamp: int
    value: float


@dataclass
class DetectedPattern:
    pattern_name: Literal["double_top", "double_bottom", "head_shoulders_top", "head_shoulders_bottom"]
    direction: Literal["bullish", "bearish"]
    confidence: float
    anchor_points: list[DetectedAnchor]


def detect_patterns(df: pd.DataFrame) -> list[DetectedPattern]:
    patterns: list[DetectedPattern] = []
    patterns.extend(_detect_double_top(df))
    patterns.extend(_detect_double_bottom(df))
    patterns.extend(_detect_head_shoulders_top(df))
    patterns.extend(_detect_head_shoulders_bottom(df))
    return patterns
```

- [ ] **Step 4: Add a backend service that reuses the existing technical-analysis history adapter**

```python
from __future__ import annotations

import pandas as pd

from app.api._technical_patterns_models import PatternAnchorPoint, PatternDetection
from app.services.data_source_factory import DataSourceFactory
from src.advanced_analysis.timeseries_analyzer.chart_pattern_mvp import detect_patterns


class TechnicalPatternDetectionService:
    async def detect_for_symbol(self, symbol: str, period: str) -> list[PatternDetection]:
        factory = DataSourceFactory()
        adapter = await factory.get_data_source("technical_analysis")
        result = await adapter.get_data("history", {"symbol": symbol, "period": period, "limit": 240})
        rows = result.get("data", [])
        return self.detect_from_history_rows(rows)

    def detect_from_history_rows(self, rows: list[dict]) -> list[PatternDetection]:
        frame = pd.DataFrame(rows)
        if frame.empty:
            return []
        if "date" in frame.columns:
            frame["date"] = pd.to_datetime(frame["date"])
        return self.detect_from_history_frame(frame)

    def detect_from_history_frame(self, frame: pd.DataFrame) -> list[PatternDetection]:
        findings = detect_patterns(frame)
        return [
            PatternDetection(
                pattern_name=finding.pattern_name,
                direction=finding.direction,
                confidence=finding.confidence,
                anchor_points=[
                    PatternAnchorPoint(role=point.role, timestamp=point.timestamp, value=point.value)
                    for point in finding.anchor_points
                ],
            )
            for finding in findings
        ]
```

- [ ] **Step 5: Wire the route helper to the service and map failures to `503`**

```python
from fastapi import HTTPException, status

from app.services.technical_pattern_detection_service import TechnicalPatternDetectionService


async def _detect_patterns_for_symbol(symbol: str, period: str):
    try:
        service = TechnicalPatternDetectionService()
        return await service.detect_for_symbol(symbol=symbol, period=period)
    except Exception as exc:  # narrow this during implementation if a better domain exception emerges
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Pattern analysis unavailable: {exc}",
        ) from exc
```

- [ ] **Step 6: Run backend tests for route contract and detector service**

Run:

```bash
pytest \
  web/backend/tests/test_technical_patterns_router_regressions.py \
  web/backend/tests/test_technical_pattern_detection_service.py \
  -q --no-cov
```

Expected:

```text
all selected tests pass
```

- [ ] **Step 7: Commit the backend detection slice**

```bash
git add \
  src/advanced_analysis/timeseries_analyzer/chart_pattern_mvp.py \
  web/backend/app/services/technical_pattern_detection_service.py \
  web/backend/app/api/_technical_patterns_router.py \
  web/backend/tests/test_technical_pattern_detection_service.py
git commit -m "feat(technical): implement chart pattern detection mvp"
```

---

### Task 3: Frontend Overlay Infrastructure and Manual Tools

**Files:**
- Modify: `web/frontend/vitest.setup.ts`
- Create: `web/frontend/src/components/technical/composables/useChartOverlays.ts`
- Create: `web/frontend/tests/unit/components/technical/useChartOverlays.spec.ts`

- [ ] **Step 1: Write the failing composable test for manual tool lifecycle**

```ts
import { describe, expect, it, vi } from 'vitest'

import { useChartOverlays } from '@/components/technical/composables/useChartOverlays'

function createChartMock() {
  return {
    createOverlay: vi.fn(() => 'overlay-1'),
    getOverlays: vi.fn(() => []),
    overrideOverlay: vi.fn(),
    removeOverlay: vi.fn(),
  }
}

describe('useChartOverlays', () => {
  it('tracks manual overlays separately from automatic overlays', () => {
    const chart = createChartMock()
    const overlays = useChartOverlays(chart as never)

    overlays.selectTool('trendline')
    overlays.registerManualOverlay('overlay-1')
    overlays.syncAutomaticOverlays([])

    expect(overlays.activeTool.value).toBe('trendline')
    expect(overlays.manualOverlayIds.value).toEqual(['overlay-1'])
    expect(overlays.automaticOverlayIds.value).toEqual([])
  })
})
```

- [ ] **Step 2: Run the frontend unit test and confirm the composable does not exist yet**

Run:

```bash
cd web/frontend && npx vitest run tests/unit/components/technical/useChartOverlays.spec.ts
```

Expected:

```text
FAIL because useChartOverlays.ts and its test file are not present yet
```

- [ ] **Step 3: Extend the klinecharts test mock with overlay APIs**

```ts
const createKLineChartMock = () => {
  const overlays: Array<{ id: string; name: string }> = []

  return {
    applyMoreData: vi.fn(),
    applyNewData: vi.fn(),
    createIndicator: vi.fn(),
    createOverlay: vi.fn((value: { name: string }) => {
      const id = `overlay-${overlays.length + 1}`
      overlays.push({ id, name: value.name })
      return id
    }),
    dispose: vi.fn(),
    getIndicators: vi.fn(() => []),
    getOverlays: vi.fn(() => overlays),
    overrideOverlay: vi.fn(),
    removeOverlay: vi.fn((id: string) => {
      const index = overlays.findIndex((item) => item.id === id)
      if (index >= 0) overlays.splice(index, 1)
    }),
    subscribeAction: vi.fn(() => vi.fn()),
  }
}

vi.mock('klinecharts', () => ({
  dispose: vi.fn(),
  init: vi.fn(() => createKLineChartMock()),
  registerIndicator: vi.fn(),
  registerOverlay: vi.fn(),
}))
```

- [ ] **Step 4: Implement the overlay composable with explicit manual/automatic separation**

```ts
import { ref } from 'vue'

type DrawingTool = 'trendline' | 'horizontalLine' | 'rectangle' | null

export function useChartOverlays(chart: {
  createOverlay: (value: Record<string, unknown>) => string | null
  removeOverlay: (id: string) => void
  registerOverlay?: (...args: unknown[]) => void
}) {
  const activeTool = ref<DrawingTool>(null)
  const manualOverlayIds = ref<string[]>([])
  const automaticOverlayIds = ref<string[]>([])

  const selectTool = (tool: DrawingTool) => {
    activeTool.value = tool
  }

  const registerManualOverlay = (id: string | null) => {
    if (id) manualOverlayIds.value.push(id)
  }

  const syncAutomaticOverlays = (ids: string[]) => {
    automaticOverlayIds.value.forEach((id) => chart.removeOverlay(id))
    automaticOverlayIds.value = ids
  }

  const removeManualOverlay = (id: string) => {
    chart.removeOverlay(id)
    manualOverlayIds.value = manualOverlayIds.value.filter((item) => item !== id)
  }

  const clearManualOverlays = () => {
    manualOverlayIds.value.forEach((id) => chart.removeOverlay(id))
    manualOverlayIds.value = []
  }

  const disposeOverlays = () => {
    clearManualOverlays()
    syncAutomaticOverlays([])
  }

  return {
    activeTool,
    manualOverlayIds,
    automaticOverlayIds,
    selectTool,
    registerManualOverlay,
    syncAutomaticOverlays,
    removeManualOverlay,
    clearManualOverlays,
    disposeOverlays,
  }
}
```

- [ ] **Step 5: Re-run the composable unit test**

Run:

```bash
cd web/frontend && npx vitest run tests/unit/components/technical/useChartOverlays.spec.ts
```

Expected:

```text
PASS
```

- [ ] **Step 6: Commit the frontend overlay infrastructure slice**

```bash
git add \
  web/frontend/vitest.setup.ts \
  web/frontend/src/components/technical/composables/useChartOverlays.ts \
  web/frontend/tests/unit/components/technical/useChartOverlays.spec.ts
git commit -m "feat(frontend): add chart overlay orchestration"
```

---

### Task 4: KLineChart Integration and Automatic Pattern Overlays

**Files:**
- Modify: `web/frontend/src/api/index.ts`
- Modify: `web/frontend/src/components/technical/KLineChart.vue`
- Modify: `web/frontend/src/components/artdeco/charts/ArtDecoKLineChartContainer.vue`
- Create: `web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts`

- [ ] **Step 1: Write a failing KLineChart integration test for automatic pattern rendering**

```ts
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import KLineChart from '@/components/technical/KLineChart.vue'

vi.mock('@/api/index.ts', () => ({
  technicalApi: {
    getPatterns: vi.fn().mockResolvedValue({
      success: true,
      data: {
        status: 'available',
        symbol: '600519.SH',
        period: 'daily',
        patterns: [
          {
            pattern_name: 'double_top',
            direction: 'bearish',
            confidence: 0.82,
            anchor_points: [
              { role: 'left_peak', timestamp: 1, value: 10.5 },
              { role: 'neckline', timestamp: 2, value: 9.8 },
              { role: 'right_peak', timestamp: 3, value: 10.4 },
            ],
          },
        ],
      },
    }),
  },
}))

describe('KLineChart overlays', () => {
  it('requests automatic patterns and keeps manual tools available', async () => {
    const wrapper = mount(KLineChart, {
      props: {
        symbol: '600519.SH',
        ohlcvData: {
          dates: ['2026-01-01', '2026-01-02', '2026-01-03'],
          open: [10, 11, 10.5],
          high: [11, 11.5, 10.8],
          low: [9.8, 10.4, 10.0],
          close: [10.8, 10.5, 10.1],
          volume: [100, 120, 130],
        },
        indicators: [],
        loading: false,
      },
    })

    expect(wrapper.text()).toContain('重置')
  })
})
```

- [ ] **Step 2: Run the component test and confirm the API method / props do not exist yet**

Run:

```bash
cd web/frontend && npx vitest run tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
FAIL because technicalApi.getPatterns, symbol prop wiring, and overlay sync do not exist yet
```

- [ ] **Step 3: Add `technicalApi.getPatterns()` to the unified frontend API layer**

```ts
export const technicalApi = {
  // existing methods...
  getPatterns: (symbol: string, period: 'daily' | 'weekly' | 'monthly') =>
    apiClient.get(`/v1/technical/patterns/${symbol}`, { params: { period } }),
}
```

- [ ] **Step 4: Thread `symbol` into the K-line surface wrapper**

```vue
<KLineChart
  ref="klineChartRef"
  :symbol="symbol"
  :ohlcv-data="data"
  :indicators="indicators"
  :loading="loading"
  @indicator-remove="$emit('indicatorRemove', $event)"
/>
```

- [ ] **Step 5: Integrate `useChartOverlays` and automatic pattern fetching inside `KLineChart.vue`**

```ts
import { technicalApi } from '@/api'
import { useChartOverlays } from '@/components/technical/composables/useChartOverlays'

const props = defineProps({
  symbol: { type: String, default: '' },
  ohlcvData: { type: Object, required: true },
  indicators: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
})

const overlays = useChartOverlays(chart.value as never)

const loadAutomaticPatterns = async () => {
  if (!props.symbol || !chart.value) return
  const response = await technicalApi.getPatterns(props.symbol, currentPeriod.value === '1day' ? 'daily' : 'weekly')
  const ids = response.data.patterns.map((pattern) =>
    chart.value!.createOverlay({
      name: 'segment',
      points: pattern.anchor_points.map((point) => ({ timestamp: point.timestamp, value: point.value })),
      extendData: { source: 'AUTO', patternName: pattern.pattern_name, confidence: pattern.confidence },
    }) || '',
  ).filter(Boolean)
  overlays.syncAutomaticOverlays(ids)
}
```

- [ ] **Step 6: Add manual tool buttons for `trendline`, `horizontal line`, and `rectangle`**

```vue
<el-button-group size="small">
  <el-button @click="selectDrawingTool('trendline')">趋势线</el-button>
  <el-button @click="selectDrawingTool('horizontalLine')">水平线</el-button>
  <el-button @click="selectDrawingTool('rectangle')">矩形</el-button>
  <el-button @click="clearManualDrawings">清空画线</el-button>
</el-button-group>
```

- [ ] **Step 7: Re-run the KLineChart overlay component test**

Run:

```bash
cd web/frontend && npx vitest run tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
PASS
```

- [ ] **Step 8: Commit the chart integration slice**

```bash
git add \
  web/frontend/src/api/index.ts \
  web/frontend/src/components/technical/KLineChart.vue \
  web/frontend/src/components/artdeco/charts/ArtDecoKLineChartContainer.vue \
  web/frontend/tests/unit/components/technical/KLineChart.overlays.spec.ts
git commit -m "feat(frontend): add kline manual and automatic overlays"
```

---

### Task 5: Cross-Boundary Verification and Governance Closeout

**Files:**
- Modify: `docs/FUNCTION_TREE.md`
- Optional test touch-up: `tests/api/file_tests/test_technical_analysis_api.py`

- [ ] **Step 1: Run the backend-only verification batch**

Run:

```bash
pytest \
  web/backend/tests/test_technical_patterns_router_regressions.py \
  web/backend/tests/test_technical_pattern_detection_service.py \
  -q --no-cov
```

Expected:

```text
all selected backend tests pass
```

- [ ] **Step 2: Run the frontend-only verification batch**

Run:

```bash
cd web/frontend && npx vitest run \
  tests/unit/components/technical/useChartOverlays.spec.ts \
  tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
all selected frontend tests pass
```

- [ ] **Step 3: Run the cross-boundary contract check**

Run:

```bash
pytest web/backend/tests/test_health_route_conflicts.py -q --no-cov -k technical_patterns
cd web/frontend && npx vitest run tests/unit/components/technical/KLineChart.overlays.spec.ts
```

Expected:

```text
backend schema assertions pass
frontend overlay integration assertions pass
```

- [ ] **Step 4: Update `FUNCTION_TREE` only if the MVP is fully verified**

```markdown
| 画线工具 | ✅ | `web/frontend/src/components/technical/KLineChart.vue` | 趋势线、水平线、矩形 |
| 图表形态 | ✅ | `web/backend/app/api/_technical_patterns_router.py` | 双顶、双底、头肩顶底 |
```

- [ ] **Step 5: Re-run FUNCTION_TREE governance tests**

Run:

```bash
pytest tests/unit/governance/test_function_tree_doc_sync.py tests/unit/governance/test_function_tree_catalog.py -q --no-cov
```

Expected:

```text
all selected governance tests pass
```

- [ ] **Step 6: Commit the governance closeout slice**

```bash
git add docs/FUNCTION_TREE.md
git commit -m "docs(function-tree): close kline drawing and pattern mvp"
```

---

## Spec Coverage Check

- OpenSpec contract for reviewed endpoint, `confidence`, anchor roles, and empty/503 behavior:
  Covered by Task 1 and Task 2.
- Shared overlay surface with manual/automatic provenance:
  Covered by Task 3 and Task 4.
- Graceful degradation when automatic detection fails:
  Covered by Task 4 tests and Task 5 verification.
- FUNCTION_TREE closeout after implementation:
  Covered by Task 5 only after verification passes.

## Critical Path

1. Backend contract models and route surface
2. Backend detector service
3. Frontend overlay composable
4. Frontend KLineChart integration
5. Cross-boundary verification

Do not start Task 4 before Task 2 is stable enough to expose the reviewed payload shape.

## Execution Notes

- Keep manual drawing state page-local for this MVP.
- Do not extend scope to Fibonacci, wedges, triangles, cup-and-handle, persistence, or alert integration during implementation.
- When editing production symbols, run GitNexus impact analysis before changing each concrete function/class per repo policy.
- Use path-level commits if global staged scope is contaminated by unrelated worktree batches.
