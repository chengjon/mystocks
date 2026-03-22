import { afterAll, afterEach, beforeAll, beforeEach, expect } from "vitest";
import { server } from "./tests/mocks/server";

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
