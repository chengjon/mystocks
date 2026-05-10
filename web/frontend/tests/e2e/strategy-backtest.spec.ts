/**
 * Strategy Backtest Workbench E2E
 *
 * Validates the current ArtDeco backtest workbench interactions.
 */

import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const STRATEGY_LIST_ENDPOINTS = [
  "**/api/v1/strategy/strategies**",
  "**/api/mock/strategy/strategies**",
  "**/api/api/v1/strategy/strategies**",
  "**/api/api/mock/strategy/strategies**",
]
const BACKTEST_RUN_ENDPOINTS = [
  "**/api/v1/strategy/backtest/run**",
  "**/api/api/v1/strategy/backtest/run**",
]

const backtestStatusEndpoints = (taskId: string) => [
  `**/api/v1/strategy/backtest/status/${taskId}**`,
  `**/api/api/v1/strategy/backtest/status/${taskId}**`,
]

const backtestResultEndpoints = (taskId: string) => [
  `**/api/v1/strategy/backtest/results/${taskId}**`,
  `**/api/api/v1/strategy/backtest/results/${taskId}**`,
]

const backtestAttributionEndpoints = (backtestId: number) => [
  `**/api/v1/backtest/${backtestId}/attribution**`,
  `**/api/api/v1/backtest/${backtestId}/attribution**`,
]

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: "ok",
    data,
    timestamp: "2026-03-01T00:00:00Z",
    request_id: "req-default",
    ...(overrides ?? {}),
  }
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
    localStorage.setItem("auth_token", "e2e-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })
}

async function routeStrategyList(
  page: Parameters<typeof test>[0]["page"],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of STRATEGY_LIST_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

async function routeBacktestRun(
  page: Parameters<typeof test>[0]["page"],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of BACKTEST_RUN_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

async function routeBacktestStatus(
  page: Parameters<typeof test>[0]["page"],
  taskId: string,
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of backtestStatusEndpoints(taskId)) {
    await page.route(endpoint, handler)
  }
}

async function routeBacktestResult(
  page: Parameters<typeof test>[0]["page"],
  taskId: string,
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of backtestResultEndpoints(taskId)) {
    await page.route(endpoint, handler)
  }
}

async function routeBacktestAttribution(
  page: Parameters<typeof test>[0]["page"],
  backtestId: number,
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of backtestAttributionEndpoints(backtestId)) {
    await page.route(endpoint, handler)
  }
}

async function mockSupportEndpoints(page: Parameters<typeof test>[0]["page"]) {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              status: "ready",
            },
            { request_id: "req-backtest-ready", message: "backend ready" }
          )
        ),
      })
    })
  }

  await page.route("**/api/csrf-token", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        buildUnifiedResponse(
          {
            csrf_token: "e2e-csrf-token",
            token_type: "bearer",
            expires_in: 3600,
          },
          { request_id: "req-backtest-csrf" }
        )
      ),
    })
  })
}

test.describe("Strategy Management - Backtesting", () => {
  test.describe.configure({ mode: "serial", timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockSupportEndpoints(page)
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-backtest-list",
          "x-process-time": "38ms",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              {
                strategy_id: 101,
                strategy_name: "Momentum Alpha",
                strategy_type: "momentum",
                status: "active",
                description: "alpha",
                updated_at: "2026-03-01T09:00:00Z",
              },
              {
                strategy_id: 102,
                strategy_name: "Mean Reversion Beta",
                strategy_type: "mean_reversion",
                status: "paused",
                description: "beta",
                updated_at: "2026-03-01T09:05:00Z",
              },
            ],
            { request_id: "req-backtest-list" }
          )
        ),
      })
    })
  })

  test("loads backtest workbench successfully", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".backtest-analysis-page")).toBeVisible()
    await expect(page.locator(".backtest-header .section-title")).toContainText("策略回测管理中心")
    await expect(page.getByRole("button", { name: "执行中枢" })).toBeVisible()
    await expect(page.getByRole("button", { name: "回测任务" })).toBeVisible()
    await expect(page.getByRole("button", { name: "生成上下文快照" })).toBeVisible()
    await expect(page.getByRole("button", { name: "查看 GPU 接入状态" })).toBeVisible()
    await expect(page.locator(".state-banner")).toContainText("任务、KPI 与报告摘要仍基于策略列表派生")
    await expect(page.locator(".progress-panel")).toBeVisible()
    await expect(page.locator(".log-panel")).toBeVisible()
  })

  test("keeps non-run execution actions informational instead of issuing fake backend work", async ({ page }) => {
    let runCalls = 0
    const apiRequests: string[] = []

    page.on("request", (request) => {
      if (request.url().includes("/api/")) {
        apiRequests.push(`${request.method()} ${request.url()}`)
      }
    })

    await routeBacktestRun(page, async (route) => {
      runCalls += 1
      await route.fulfill({
        status: 202,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-backtest-run-informational",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              backtest_id: "bt-info-101",
              status: "pending",
              message: "回测任务已提交",
            },
            { request_id: "req-backtest-run-informational" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await page.getByRole("button", { name: "生成上下文快照" }).click()
    await expect(page.locator(".state-banner")).toContainText("不会创建后端任务")
    await expect(page.locator(".execution-action-hint")).toContainText("最近快照")
    expect(runCalls).toBe(0)

    await page.getByRole("button", { name: "查看 GPU 接入状态" }).click()
    await expect(page.locator(".state-banner")).toContainText("未接入 GPU 资源分配 API")
    expect(runCalls).toBe(0)

    const runRequests = apiRequests.filter((entry) => entry.includes("/strategy/backtest/run"))
    expect(runRequests).toHaveLength(0)
  })

  test("switches tabs and renders corresponding content", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`)

    await page.getByRole("button", { name: "策略库" }).click()
    await expect(page.locator(".strat-library .strategy-item").first()).toBeVisible()

    await page.getByRole("button", { name: "回测任务" }).click()
    await expect(page.locator(".task-list .task-item").first()).toBeVisible()

    await page.getByRole("button", { name: "报告中心" }).click()
    await expect(page.locator(".tab-panel")).toContainText("回测报告")
  })

  test("runs the real v1 backtest chain through run, status, and results", async ({ page }) => {
    let runPayload: Record<string, unknown> | null = null
    let statusCalls = 0
    let resultCalls = 0
    let attributionCalls = 0
    const apiRequests: string[] = []

    page.on("request", (request) => {
      if (request.url().includes("/api/")) {
        apiRequests.push(`${request.method()} ${request.url()}`)
      }
    })

    await routeBacktestRun(page, async (route) => {
      runPayload = route.request().postDataJSON() as Record<string, unknown>
      await route.fulfill({
        status: 202,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-backtest-run",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              backtest_id: "bt-101",
              status: "pending",
              message: "回测任务已提交",
            },
            { request_id: "req-backtest-run" }
          )
        ),
      })
    })

    await routeBacktestStatus(page, "bt-101", async (route) => {
      statusCalls += 1
      const statusPayload = statusCalls === 1
        ? {
            backtest_id: "bt-101",
            status: "running",
            message: "回测执行中",
          }
        : {
            backtest_id: "bt-101",
            status: "completed",
            message: "回测完成",
          }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": `req-backtest-status-${statusCalls}`,
        },
        body: JSON.stringify(buildUnifiedResponse(statusPayload, { request_id: `req-backtest-status-${statusCalls}` })),
      })
    })

    await routeBacktestResult(page, "bt-101", async (route) => {
      resultCalls += 1
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-backtest-result",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              backtest_id: 101,
              strategy_id: 101,
              start_date: "2026-01-01",
              end_date: "2026-03-01",
              completed_at: "2026-03-10T09:30:00Z",
              status: "completed",
              performance: {
                total_return: 15.2,
                annual_return: 12.3,
                max_drawdown: -4.5,
                win_rate: 62.5,
                sharpe_ratio: 1.8,
                volatility: 8.1,
                total_trades: 18,
                profit_factor: 1.6,
              },
            },
            { request_id: "req-backtest-result" }
          )
        ),
      })
    })

    await routeBacktestAttribution(page, 101, async (route) => {
      attributionCalls += 1
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-backtest-attribution",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              analysis_date: "2026-03-10",
              brinson: {
                allocation_effect: 0.012,
                selection_effect: 0.018,
                interaction_effect: -0.003,
              },
              factor_attribution: {
                factor_exposures: {
                  value: {
                    portfolio_exposure: 0.42,
                    benchmark_exposure: 0.21,
                    active_exposure: 0.21,
                  },
                },
                factor_contributions: { value: 0.014 },
                specific_return: 0.006,
              },
            },
            { request_id: "req-backtest-attribution" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`)

    await page.getByRole("button", { name: "启动回测" }).click()
    await page.waitForTimeout(500)
    console.log("[backtest-e2e-api]", apiRequests.join("\n"))

    await expect.poll(() => runPayload?.strategy_id ?? null).toBe("101")
    await expect.poll(() => statusCalls).toBe(2)
    await expect.poll(() => resultCalls).toBe(1)
    await expect(page.locator(".progress-panel")).toContainText("回测完成")
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")
    await page.getByRole("button", { name: "报告中心" }).click()
    await expect(page.locator(".hybrid-table__content")).toContainText("Momentum Alpha")
    await expect(page.locator(".hybrid-table__content")).toContainText("+15.2%")
    await page.locator('[data-testid="backtest-attribution-101"]').click()
    await expect.poll(() => attributionCalls).toBe(1)
    await expect(page.locator(".attribution-panel")).toContainText("回测归因")
    await expect(page.locator(".attribution-panel")).toContainText("Brinson 归因")
    await expect(page.locator(".attribution-panel")).toContainText("五因子归因")
    await expect(page.locator(".attribution-panel")).toContainText("req-backtest-attribution")
  })

  test("shows the real backend error when v1 backtest run fails", async ({ page }) => {
    let statusCalls = 0
    let resultCalls = 0

    await routeBacktestRun(page, async (route) => {
      await route.fulfill({
        status: 400,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-backtest-run-error",
        },
        body: JSON.stringify({
          success: false,
          code: 400,
          message: "风控校验未通过",
          data: null,
          request_id: "req-backtest-run-error",
          timestamp: "2026-03-10T09:10:00Z",
        }),
      })
    })

    await routeBacktestStatus(page, "bt-101", async (route) => {
      statusCalls += 1
      await route.abort("failed")
    })

    await routeBacktestResult(page, "bt-101", async (route) => {
      resultCalls += 1
      await route.abort("failed")
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`)
    await page.getByRole("button", { name: "启动回测" }).click()

    await expect(page.locator(".progress-panel")).toContainText("回测失败")
    await expect(page.locator(".log-panel")).toContainText("风控校验未通过")
    await expect(page.locator(".log-panel")).not.toContainText("结果已载入报告中心")
    await expect(page.locator(".progress-panel")).not.toContainText("回测完成")
    await page.getByRole("button", { name: "回测任务" }).click()
    await expect(page.locator(".task-list")).toContainText("风控校验未通过")
    expect(statusCalls).toBe(0)
    expect(resultCalls).toBe(0)
  })

  test("resets execution config to defaults", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`)

    const capitalInput = page.getByPlaceholder("例如 1000000")
    await expect(capitalInput).toBeVisible()
    await capitalInput.fill("2000000")
    await expect(capitalInput).toHaveValue("2000000")

    await page.getByRole("button", { name: "重置参数" }).click()
    await expect(capitalInput).toHaveValue("1000000")
  })
})
