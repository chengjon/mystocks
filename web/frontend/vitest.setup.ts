import { afterAll, afterEach, beforeAll, beforeEach, expect, vi } from "vitest";
import { server } from "./tests/mocks/server";

const createKLineChartMock = () => {
  const indicators: Array<{ name: string; paneId: string }> = [];

  return {
    applyNewData: vi.fn(),
    createIndicator: vi.fn((name: string) => {
      indicators.push({ name, paneId: "mock-pane" });
    }),
    dispose: vi.fn(),
    getIndicators: vi.fn(() => indicators),
    getTimeScaleVisibleRange: vi.fn(() => ({ from: 0, to: 100 })),
    getVisibleRange: vi.fn(() => ({ from: 0, to: 100 })),
    removeIndicator: vi.fn((paneId: string, name: string) => {
      const index = indicators.findIndex((item) => item.name === name && item.paneId === paneId);
      if (index >= 0) {
        indicators.splice(index, 1);
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
