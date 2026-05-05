import { ref, type Ref } from "vue";
import { registerOverlay, type Overlay } from "klinecharts";

import { technicalApi } from "@/api";
import {
  useChartOverlays,
  type ManualDrawingTool,
  type OverlayChart,
} from "@/components/technical/composables/useChartOverlays";

type PatternPeriod = "daily" | "weekly" | "monthly";

type PatternAnchorPoint = {
  timestamp: number;
  value: number;
};

type PatternDetection = {
  pattern_name: string;
  direction: string;
  confidence: number;
  gap_side?: string | null;
  gap_fill_status?: string | null;
  gap_zone?: {
    start_timestamp: number;
    end_timestamp: number;
    upper_value: number;
    lower_value: number;
    filled_at: number | null;
  } | null;
  anchor_points: PatternAnchorPoint[];
};

type PatternChart = {
  createOverlay: (value: string | Overlay, paneId?: string) => string | null;
  removeOverlay: (id: string) => void;
};

const MANUAL_OVERLAY_BY_TOOL: Record<Exclude<ManualDrawingTool, null>, string> = {
  trendline: "segment",
  horizontalLine: "horizontalStraightLine",
  rectangle: "mvpRectangle",
};

let rectangleOverlayRegistered = false;
let gapZoneOverlayRegistered = false;

function ensureRectangleOverlayRegistered() {
  if (rectangleOverlayRegistered) {
    return;
  }

  registerOverlay({
    name: "mvpRectangle",
    totalStep: 2,
    createPointFigures: ({ coordinates }) => {
      if (!coordinates || coordinates.length < 2) {
        return null;
      }

      const [start, end] = coordinates;
      return {
        type: "rect",
        attrs: {
          x: Math.min(start.x, end.x),
          y: Math.min(start.y, end.y),
          width: Math.abs(end.x - start.x),
          height: Math.abs(end.y - start.y),
        },
      };
    },
  });

  rectangleOverlayRegistered = true;
}

function ensureGapZoneOverlayRegistered() {
  if (gapZoneOverlayRegistered) {
    return;
  }

  registerOverlay({
    name: "mvpGapZone",
    totalStep: 2,
    createPointFigures: ({ coordinates }) => {
      if (!coordinates || coordinates.length < 2) {
        return null;
      }

      const [start, end] = coordinates;
      return {
        type: "rect",
        attrs: {
          x: Math.min(start.x, end.x),
          y: Math.min(start.y, end.y),
          width: Math.max(Math.abs(end.x - start.x), 1),
          height: Math.max(Math.abs(end.y - start.y), 1),
        },
      };
    },
  });

  gapZoneOverlayRegistered = true;
}

function buildAutomaticPatternOverlays(patterns: PatternDetection[]) {
  return patterns
    .flatMap((pattern) => {
      if (pattern.gap_zone) {
        return [{
          name: "mvpGapZone",
          paneId: "candle_pane",
          points: [
            {
              timestamp: pattern.gap_zone.start_timestamp,
              value: pattern.gap_zone.upper_value,
            },
            {
              timestamp: pattern.gap_zone.end_timestamp,
              value: pattern.gap_zone.lower_value,
            },
          ],
          extendData: {
            source: "AUTO",
            patternName: pattern.pattern_name,
            gapSide: pattern.gap_side,
            gapFillStatus: pattern.gap_fill_status,
            upperValue: pattern.gap_zone.upper_value,
            lowerValue: pattern.gap_zone.lower_value,
            confidence: pattern.confidence,
            direction: pattern.direction,
          },
        }];
      }

      if (!Array.isArray(pattern.anchor_points) || pattern.anchor_points.length <= 1) {
        return [];
      }

      const points = pattern.anchor_points.map((point) => ({
        timestamp: point.timestamp,
        value: point.value,
      }));

      return points.slice(1).map((point, index) => ({
        name: "segment",
        paneId: "candle_pane",
        points: [points[index], point],
        extendData: {
          source: "AUTO",
          patternName: pattern.pattern_name,
          direction: pattern.direction,
          confidence: pattern.confidence,
          segmentIndex: index,
          segmentCount: points.length - 1,
        },
      }));
    });
}

function mapChartPeriodToPatternPeriod(period: string): PatternPeriod | null {
  if (period === "1day") {
    return "daily";
  }

  return null;
}

export function useKLinePatternOverlays(
  chartRef: Ref<PatternChart | null>,
  options: {
    getSymbol: () => string;
    getChartPeriod: () => string;
  },
) {
  const automaticPatternMessage = ref("");
  const patternRequestSequence = ref(0);

  const overlayBridge: OverlayChart = {
    createOverlay: (value, paneId) => {
      if (!chartRef.value) {
        return null;
      }

      return chartRef.value.createOverlay(value, paneId);
    },
    removeOverlay: (id) => {
      if (chartRef.value) {
        chartRef.value.removeOverlay(id);
      }
    },
  };

  const {
    activeTool: activeDrawingTool,
    selectTool,
    registerManualOverlay,
    clearManualOverlays,
    clearAutomaticOverlays,
    syncAutomaticOverlays,
    disposeOverlays,
  } = useChartOverlays(overlayBridge);

  const startManualDrawing = (tool: Exclude<ManualDrawingTool, null>) => {
    ensureRectangleOverlayRegistered();
    selectTool(tool);

    const overlayName = MANUAL_OVERLAY_BY_TOOL[tool];
    if (!overlayName || !chartRef.value) {
      return;
    }

    const overlayId = chartRef.value.createOverlay({ name: overlayName }, "candle_pane");
    registerManualOverlay(overlayId);
  };

  const clearManualDrawings = () => {
    clearManualOverlays();
    selectTool(null);
  };

  const loadAutomaticPatterns = async () => {
    if (!chartRef.value) {
      return;
    }

    const requestId = patternRequestSequence.value + 1;
    patternRequestSequence.value = requestId;

    const symbol = options.getSymbol();
    if (!symbol) {
      automaticPatternMessage.value = "";
      clearAutomaticOverlays();
      return;
    }

    const patternPeriod = mapChartPeriodToPatternPeriod(options.getChartPeriod());
    if (!patternPeriod) {
      automaticPatternMessage.value = "自动形态当前仅支持日线视图";
      clearAutomaticOverlays();
      return;
    }

    try {
      automaticPatternMessage.value = "";
      const response = await technicalApi.getPatterns(symbol, patternPeriod);
      if (requestId !== patternRequestSequence.value) {
        return;
      }

      if (!response?.success || !response?.data) {
        throw new Error(response?.message || "automatic pattern request failed");
      }

      const patterns = response.data.patterns as PatternDetection[];
      if (patterns.some((pattern) => pattern.gap_zone)) {
        ensureGapZoneOverlayRegistered();
      }
      syncAutomaticOverlays(buildAutomaticPatternOverlays(patterns));
    } catch (error) {
      if (requestId !== patternRequestSequence.value) {
        return;
      }

      console.error("[KLineChart] Failed to load automatic patterns:", error);
      automaticPatternMessage.value = "自动形态暂不可用";
      clearAutomaticOverlays();
    }
  };

  return {
    activeDrawingTool,
    automaticPatternMessage,
    startManualDrawing,
    clearManualDrawings,
    loadAutomaticPatterns,
    cleanupPatternOverlays: disposeOverlays,
  };
}
