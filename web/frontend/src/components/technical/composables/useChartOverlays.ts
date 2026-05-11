import { ref, type Ref } from "vue";

import type { OverlayCreate } from "klinecharts";

export type ManualDrawingTool = "trendline" | "horizontalLine" | "rectangle" | null;

export type OverlayChart = {
  createOverlay: (value: string | OverlayCreate, paneId?: string) => string | null;
  removeOverlay: (id: string) => void;
};

export type AutomaticOverlayDefinition = OverlayCreate & {
  paneId?: string;
};

export function useChartOverlays(chart: OverlayChart) {
  const activeTool = ref<ManualDrawingTool>(null);
  const manualOverlayIds = ref<string[]>([]);
  const automaticOverlayIds = ref<string[]>([]);

  const removeFromCollection = (collection: Ref<string[]>, id: string) => {
    const index = collection.value.indexOf(id);
    if (index >= 0) {
      collection.value.splice(index, 1);
    }
  };

  const selectTool = (tool: ManualDrawingTool) => {
    activeTool.value = tool;
  };

  const registerManualOverlay = (id: string | null | undefined) => {
    if (!id || manualOverlayIds.value.includes(id)) {
      return;
    }

    manualOverlayIds.value.push(id);
  };

  const removeManualOverlay = (id: string) => {
    chart.removeOverlay(id);
    removeFromCollection(manualOverlayIds, id);
  };

  const clearManualOverlays = () => {
    manualOverlayIds.value.forEach((id) => {
      chart.removeOverlay(id);
    });
    manualOverlayIds.value = [];
  };

  const clearAutomaticOverlays = () => {
    automaticOverlayIds.value.forEach((id) => {
      chart.removeOverlay(id);
    });
    automaticOverlayIds.value = [];
  };

  const syncAutomaticOverlays = (overlays: AutomaticOverlayDefinition[]) => {
    clearAutomaticOverlays();

    automaticOverlayIds.value = overlays
      .map((overlay) => chart.createOverlay(overlay, overlay.paneId))
      .filter((id): id is string => typeof id === "string" && id.length > 0);
  };

  const disposeOverlays = () => {
    clearAutomaticOverlays();
    clearManualOverlays();
    activeTool.value = null;
  };

  return {
    activeTool,
    manualOverlayIds,
    automaticOverlayIds,
    selectTool,
    registerManualOverlay,
    removeManualOverlay,
    clearManualOverlays,
    clearAutomaticOverlays,
    syncAutomaticOverlays,
    disposeOverlays,
    cleanup: disposeOverlays,
  };
}
