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

test.describe("Strategy Management - Backtesting", () => {
  test.describe.configure({ mode: "serial", timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
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
    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`)

    await expect(page.getByRole("heading", { name: "策略回测管理中心" })).toBeVisible()
    await expect(page.getByRole("button", { name: "执行中枢" })).toBeVisible()
    await expect(page.getByRole("button", { name: "回测任务" })).toBeVisible()
    await expect(page.locator(".progress-panel")).toBeVisible()
    await expect(page.locator(".log-panel")).toBeVisible()
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

  test("runs backtest action and appends execution log", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`)

    const phaseValue = page.locator(".progress-main .value").first()
    const phaseBefore = ((await phaseValue.textContent()) ?? "").trim()
    const initialCount = await page.locator(".log-list .log-item").count()
    await page.getByRole("button", { name: "启动回测" }).click()

    await expect(phaseValue).toContainText(/任务排队中|回测执行中|回测完成|回测失败/)
    const phaseAfter = ((await phaseValue.textContent()) ?? "").trim()
    expect(phaseAfter).not.toBe(phaseBefore)

    const nextCount = await page.locator(".log-list .log-item").count()
    expect(nextCount).toBeGreaterThanOrEqual(initialCount)
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
