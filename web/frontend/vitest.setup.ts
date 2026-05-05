import { afterAll, afterEach, beforeAll, beforeEach, expect, vi } from "vitest";
import { server } from "./tests/mocks/server";

const createKLineChartMock = () => {
  const indicators: Array<{ name: string; paneId: string }> = [];
  const overlays: Array<{ id: string; name: string; paneId?: string; value: unknown }> = [];

  return {
    applyMoreData: vi.fn(),
    applyNewData: vi.fn(),
    createIndicator: vi.fn((name: string) => {
      indicators.push({ name, paneId: "mock-pane" });
    }),
    createOverlay: vi.fn((value: { name: string }, paneId?: string) => {
      const id = `overlay-${overlays.length + 1}`;
      overlays.push({ id, name: value.name, paneId, value });
      return id;
    }),
    dispose: vi.fn(),
    getIndicators: vi.fn(() => indicators),
    getOverlays: vi.fn(() => overlays),
    getTimeScaleVisibleRange: vi.fn(() => ({ from: 0, to: 100 })),
    getVisibleRange: vi.fn(() => ({ from: 0, to: 100 })),
    overrideOverlay: vi.fn(),
    removeIndicator: vi.fn((paneId: string, name: string) => {
      const index = indicators.findIndex((item) => item.name === name && item.paneId === paneId);
      if (index >= 0) {
        indicators.splice(index, 1);
      }
    }),
    removeOverlay: vi.fn((id: string) => {
      const index = overlays.findIndex((item) => item.id === id);
      if (index >= 0) {
        overlays.splice(index, 1);
      }
    }),
    resize: vi.fn(),
    scrollToRealTime: vi.fn(),
    setOffsetRightDistance: vi.fn(),
    setStyles: vi.fn(),
    setVisibleRange: vi.fn(),
    subscribeAction: vi.fn(() => vi.fn()),
    unsubscribeAction: vi.fn(),
    zoomAtCoordinate: vi.fn(),
  };
};

vi.mock("klinecharts", () => ({
  dispose: vi.fn(),
  init: vi.fn(() => createKLineChartMock()),
  registerIndicator: vi.fn(),
  registerOverlay: vi.fn(),
}));

const MSW_BYPASS_TEST_PATTERNS = [
  "src/utils/__tests__/websocket-manager.spec.ts",
];

let serverActive = false;

function startServer() {
  if (serverActive) {
    return;
  }

  server.listen({ onUnhandledRequest: "bypass" });
  serverActive = true;
}

function stopServer() {
  if (!serverActive) {
    return;
  }

  server.close();
  serverActive = false;
}

beforeAll(() => {
  startServer();
});

beforeEach(() => {
  const testPath = expect.getState().testPath ?? "";
  const shouldBypassMsw = MSW_BYPASS_TEST_PATTERNS.some((pattern) => testPath.endsWith(pattern));

  if (shouldBypassMsw) {
    stopServer();
    return;
  }

  startServer();
});

afterEach(() => {
  if (serverActive) {
    server.resetHandlers();
  }
});

afterAll(() => {
  stopServer();
});
