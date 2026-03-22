import { beforeEach, describe, expect, it } from "vitest";
import { http, HttpResponse } from "msw";
import { server } from "../../../../tests/mocks/server";
import { StrategyApiService } from "../strategyService";

describe("StrategyApiService with MSW", () => {
  beforeEach(() => {
    server.resetHandlers();
    window.history.replaceState({}, "", "http://localhost:3000/");
  });

  it("loads strategy list through network interception instead of class stubs", async () => {
    server.use(
      http.get("http://localhost:3000/api/v1/strategy/strategies", ({ request }) => {
        const url = new URL(request.url);

        expect(url.searchParams.get("page")).toBe("2");
        expect(url.searchParams.get("page_size")).toBe("5");
        expect(url.searchParams.get("status")).toBe("paused");

        return HttpResponse.json({
          success: true,
          code: 200,
          message: "ok",
          data: {
            items: [
              {
                id: 11,
                strategy_id: 11,
                strategy_name: "Paused Strategy",
                strategy_type: "momentum",
                description: "network-backed row",
                status: "paused",
              },
            ],
            total: 1,
            page: 2,
            page_size: 5,
          },
          request_id: "req-msw-list",
          process_time: "18ms",
          timestamp: "2026-03-22T00:00:00Z",
        });
      }),
    );

    const service = new StrategyApiService();
    const response = await service.getStrategyList({ page: 2, pageSize: 5, status: "paused" });

    expect(response.success).toBe(true);
    expect(response.request_id).toBe("req-msw-list");
    expect(response.data.items).toHaveLength(1);
    expect(response.data.items[0].strategy_name).toBe("Paused Strategy");
  });

  it("handles write requests through MSW including CSRF bootstrap", async () => {
    let csrfRequested = false;
    let startRequested = false;

    server.use(
      http.get("http://localhost:3000/api/csrf-token", () => {
        csrfRequested = true;
        return HttpResponse.json({
          success: true,
          data: { csrf_token: "msw-csrf-token" },
        });
      }),
      http.post("http://localhost:3000/api/v1/strategy/11/start", async ({ request }) => {
        startRequested = true;
        expect(request.headers.get("x-csrf-token")).toBe("msw-csrf-token");
        return HttpResponse.json({
          success: true,
          code: 200,
          message: "策略启动成功",
          data: { id: 11, status: "active" },
          request_id: "req-msw-start",
          timestamp: "2026-03-22T00:00:00Z",
        });
      }),
    );

    const service = new StrategyApiService();
    const response = await service.startStrategy("11", { dry_run: true });

    expect(csrfRequested).toBe(true);
    expect(startRequested).toBe(true);
    expect(response.success).toBe(true);
    expect(response.request_id).toBe("req-msw-start");
    expect(response.data).toEqual({ id: 11, status: "active" });
  });
});
