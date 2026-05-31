import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

function buildUnifiedResponse<T>(data: T, requestId = "req-trade-execution-tracking") {
  return {
    success: true,
    code: 200,
    message: "ok",
    data,
    timestamp: "2026-05-09T00:00:00Z",
    request_id: requestId,
  }
}

const trackedItem = {
  tracking_id: "track-101",
  account_id: "backtest:7",
  order_id: "backtest-7-101",
  symbol: "600519.SH",
  direction: "buy",
  quantity: 100,
  price: 1750,
  requested_at: "2026-05-09T09:31:00+08:00",
  channel: "miniqmt",
  submission_status: "bridge_task_accepted",
  broker_state: "review_required",
  reconciliation_status: "review_required",
  bridge_evidence: {
    bridge_task_id: "mini-task-101",
    receipt_status: "accepted",
    result_status: "terminal_without_broker_identity",
    source_name: "miniQMT bridge",
  },
  broker_correlation: {
    external_order_id: null,
    broker_event_type: null,
    identity_status: "missing_broker_identity",
  },
}

const trackingListPayload = {
  status: "available",
  endpoint: "trade",
  resource: "execution_tracking",
  items: [trackedItem],
  summary: {
    total_count: 1,
    bridge_accepted_count: 1,
    broker_acknowledged_count: 0,
    review_required_count: 1,
    reconciled_count: 0,
  },
  total_count: 1,
  page: 1,
  page_size: 20,
}

const trackingDetailPayload = {
  status: "available",
  endpoint: "trade",
  resource: "execution_tracking_detail",
  item: trackedItem,
  evidence_timeline: [
    {
      event_type: "external_trigger_requested",
      occurred_at: "2026-05-09T09:31:00+08:00",
      summary: "外部触发请求已记录，等待 miniQMT bridge 接收。",
      evidence: {
        channel: "miniqmt",
      },
    },
    {
      event_type: "bridge_submission_receipt",
      occurred_at: "2026-05-09T09:31:02+08:00",
      summary: "miniQMT bridge 已接收任务，但这不是券商确认。",
      evidence: {
        bridge_task_id: "mini-task-101",
      },
    },
    {
      event_type: "review_required",
      occurred_at: "2026-05-09T09:31:05+08:00",
      summary: "bridge 终态缺少券商生命周期身份，仍需复核。",
      evidence: {
        broker_identity: null,
      },
    },
  ],
}

const triggerPayload = {
  status: "accepted",
  endpoint: "trade",
  resource: "external_execution_trigger",
  tracking_id: "track-new",
  accepted: true,
  channel: "miniqmt",
  submission_status: "bridge_task_accepted",
  broker_state: "review_required",
  bridge_receipt: {
    bridge_task_id: "miniqmt-task-new",
    receipt_status: "accepted",
    result_status: null,
    source_name: "miniQMT bridge",
  },
}

async function setupAuthenticatedSession(page: Parameters<typeof test>[0]["page"]) {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: "e2e-admin",
      email: "e2e-admin@mystocks.local",
      role: "admin",
      permissions: ["*"],
    }
    localStorage.setItem("auth_token", "e2e-trade-execution-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })
}

async function mockExecutionTrackingApis(page: Parameters<typeof test>[0]["page"]) {
  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|(?:api\/(?:v1\/)?)?trade\/execution-tracking.*)/, async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const apiPath = url.pathname.replace(/^\/api\/v1/, "").replace(/^\/api/, "")

    if (url.pathname === "/api/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "ready" }, "req-execution-ready")),
      })
      return
    }

    if (url.pathname === "/api/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              csrf_token: "e2e-trade-execution-csrf",
              token_type: "bearer",
              expires_in: 3600,
            },
            "req-execution-csrf",
          ),
        ),
      })
      return
    }

    if (apiPath.replace(/\/$/, "") === "/trade/execution-tracking" && request.method() === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(trackingListPayload, "req-execution-list")),
      })
      return
    }

    if (apiPath.replace(/\/$/, "") === "/trade/execution-tracking/track-101") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(trackingDetailPayload, "req-execution-detail")),
      })
      return
    }

    if (apiPath.replace(/\/$/, "") === "/trade/execution-tracking/trigger" && request.method() === "POST") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(triggerPayload, "req-execution-trigger")),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildUnifiedResponse([])),
    })
  })
}

test.describe("Trade execution tracking workbench", () => {
  test.beforeEach(async ({ page }) => {
    await setupAuthenticatedSession(page)
    await mockExecutionTrackingApis(page)
  })

  test("exposes route-level ArtDeco hooks for execution tracking", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/trade/execution`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "执行跟踪 / 外部触发观测台" })).toBeVisible()
    await expect(page.getByTestId("trade-execution-page")).toBeVisible()
    await expect(page.getByTestId("trade-execution-header")).toBeVisible()
    await expect(page.getByTestId("trade-execution-header")).toHaveClass(/artdeco-route-header/)
    await expect(page.getByTestId("trade-execution-refresh")).toBeVisible()
    await expect(page.getByTestId("trade-execution-stats-strip")).toBeVisible()
    await expect(page.getByTestId("trade-execution-filter-row")).toBeVisible()
    await expect(page.getByTestId("trade-execution-trigger-row")).toBeVisible()
    await expect(page.getByTestId("trade-execution-work-area")).toBeVisible()
  })

  test("observes external triggers without promoting bridge evidence to broker truth", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/trade/execution`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "执行跟踪 / 外部触发观测台" })).toBeVisible()
    await expect(page.getByText("实际交易由 miniQMT、TdxQuant 或其他外部程序完成")).toBeVisible()
    await expect(page.getByText("600519.SH")).toBeVisible()
    await expect(page.getByText("mini-task-101")).toBeVisible()
    await expect(page.getByRole("table").getByText("需复核")).toBeVisible()

    await page.getByTestId("execution-detail-track-101").click()
    await expect(page.getByRole("complementary", { name: "执行证据详情" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "证据时间线" })).toBeVisible()
    await expect(page.getByText("外部触发请求已记录，等待 miniQMT bridge 接收。")).toBeVisible()
    await expect(page.getByText("miniQMT bridge 已接收任务，但这不是券商确认。")).toBeVisible()
    await expect(page.getByText("bridge 终态缺少券商生命周期身份，仍需复核。")).toBeVisible()
    await page.getByRole("button", { name: "关闭" }).click()
    await expect(page.getByRole("complementary", { name: "执行证据详情" })).toHaveCount(0)

    await page.getByTestId("execution-symbol-input").fill("000001.SZ")
    await page.getByTestId("execution-quantity-input").fill("200")
    await page.getByTestId("execution-price-input").fill("12.34")
    await page.getByTestId("execution-trigger-button").click()

    await expect(page.getByText("bridge task: miniqmt-task-new")).toBeVisible()
    await expect(page.getByText("券商已确认")).toHaveCount(0)
    await expect(page.getByText("已成交")).toHaveCount(0)

    await page.getByTestId("execution-reconcile-track-101").click()
    await expect(page).toHaveURL(/\/trade\/reconciliation/)
    await expect.poll(() => new URL(page.url()).searchParams.get("account_id")).toBe("backtest:7")
    await expect.poll(() => new URL(page.url()).searchParams.get("order_id")).toBe("backtest-7-101")
    await expect.poll(() => new URL(page.url()).searchParams.get("bridge_task_id")).toBe("mini-task-101")
  })
})
