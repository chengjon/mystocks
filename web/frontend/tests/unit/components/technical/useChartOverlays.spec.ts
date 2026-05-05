import { describe, expect, it, vi } from "vitest";

import {
  type AutomaticOverlayDefinition,
  type OverlayChart,
  useChartOverlays,
} from "@/components/technical/composables/useChartOverlays";

function createChartMock() {
  let sequence = 0;

  return {
    createOverlay: vi.fn((overlay: string | AutomaticOverlayDefinition, _paneId?: string) => {
      if (typeof overlay !== "string" && overlay.name === "skip") {
        return null;
      }

      sequence += 1;
      return `auto-${sequence}`;
    }),
    removeOverlay: vi.fn(),
  } satisfies OverlayChart;
}

describe("useChartOverlays", () => {
  it("tracks manual overlays separately from automatic overlays", () => {
    const chart = createChartMock();
    const overlays = useChartOverlays(chart);

    overlays.selectTool("trendline");
    overlays.registerManualOverlay("overlay-1");
    overlays.syncAutomaticOverlays([]);

    expect(overlays.activeTool.value).toBe("trendline");
    expect(overlays.manualOverlayIds.value).toEqual(["overlay-1"]);
    expect(overlays.automaticOverlayIds.value).toEqual([]);
  });

  it("replaces automatic overlays, removes manual overlays, and disposes the session state", () => {
    const chart = createChartMock();
    const overlays = useChartOverlays(chart);

    overlays.selectTool("horizontalLine");
    overlays.registerManualOverlay("manual-1");
    overlays.syncAutomaticOverlays([
      { name: "segment" } as AutomaticOverlayDefinition,
      { name: "skip" } as AutomaticOverlayDefinition,
    ]);

    expect(overlays.automaticOverlayIds.value).toEqual(["auto-1"]);

    overlays.syncAutomaticOverlays([{ name: "segment", paneId: "candle_pane" } as AutomaticOverlayDefinition]);

    expect(chart.removeOverlay).toHaveBeenCalledWith("auto-1");
    expect(chart.createOverlay).toHaveBeenLastCalledWith(
      expect.objectContaining({ name: "segment", paneId: "candle_pane" }),
      "candle_pane",
    );
    expect(overlays.automaticOverlayIds.value).toEqual(["auto-2"]);

    overlays.removeManualOverlay("manual-1");

    expect(chart.removeOverlay).toHaveBeenCalledWith("manual-1");
    expect(overlays.manualOverlayIds.value).toEqual([]);

    overlays.registerManualOverlay("manual-2");
    overlays.disposeOverlays();

    expect(chart.removeOverlay).toHaveBeenCalledWith("auto-2");
    expect(chart.removeOverlay).toHaveBeenCalledWith("manual-2");
    expect(overlays.activeTool.value).toBeNull();
    expect(overlays.manualOverlayIds.value).toEqual([]);
    expect(overlays.automaticOverlayIds.value).toEqual([]);
  });
});
