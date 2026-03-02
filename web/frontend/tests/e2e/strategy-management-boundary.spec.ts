/**
 * Strategy Management - Boundary and Edge Cases
 *
 * Rebased to current ArtDeco Strategy Management page (`/strategy/repo`).
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
    request_id: "req-boundary",
    ...(overrides ?? {}),
  }
}

function buildStrategyDataset(count: number, statuses?: Array<"active" | "paused" | "archived">) {
  const statusList = statuses ?? ["active", "paused", "archived"]
  const types = ["momentum", "mean_reversion", "breakout"] as const
  return Array.from({ length: count }, (_, idx) => ({
    strategy_id: idx + 1,
    strategy_name: `Boundary-${String(idx + 1).padStart(2, "0")}`,
    strategy_type: types[idx % types.length],
    description: `boundary case ${idx + 1}`,
    status: statusList[idx % statusList.length],
    updated_at: "2026-03-01T08:00:00Z",
  }))
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

async function mockCsrfEndpoint(page: Parameters<typeof test>[0]["page"]) {
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
          { request_id: "req-csrf-boundary" }
        )
      ),
    })
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

test.describe("Strategy Management - Boundary and Edge Cases", () => {
  test.describe.configure({ mode: "serial", timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await setupAuthenticatedSession(page)
    await mockCsrfEndpoint(page)
  })

  test("shows empty-state when search has no matches", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-empty-search", "x-process-time": "22ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(8), { request_id: "req-empty-search" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await page.getByPlaceholder("搜索策略名称 / 类型").fill("NonExistentStrategyXYZ123")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(0)
    await expect(page.locator(".empty-state")).toBeVisible()
  })

  test("handles filter combination with no results", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-empty-filter", "x-process-time": "18ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(10, ["active", "paused"]), { request_id: "req-empty-filter" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await page.locator(".toolbar-select").selectOption("error")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(0)
    await expect(page.locator(".empty-state")).toBeVisible()
  })

  test("paginates correctly with large dataset", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-page-large", "x-process-time": "25ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(25), { request_id: "req-page-large" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".pagination-text")).toContainText("第 1 / 4 页")

    await page.getByRole("button", { name: "下一页" }).click()
    await page.getByRole("button", { name: "下一页" }).click()
    await page.getByRole("button", { name: "下一页" }).click()

    await expect(page.locator(".pagination-text")).toContainText("第 4 / 4 页")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(1)
  })

  test("falls back to MOCK when strategy API fails", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.abort("failed")
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".source-badge.mock")).toContainText("SOURCE: MOCK")
    const rows = await page.locator(".strategy-table tbody tr").count()
    expect(rows).toBeGreaterThan(0)
  })

  test("recovers from temporary strategy API failure after refresh", async ({ page }) => {
    let requestCount = 0
    await routeStrategyList(page, async (route) => {
      requestCount += 1
      if (requestCount === 1) {
        await route.abort("failed")
        return
      }

      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-recover", "x-process-time": "20ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(9), { request_id: "req-recover" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".source-badge.mock")).toContainText("SOURCE: MOCK")

    await page.getByRole("button", { name: "刷新" }).click()
    await expect(page.locator(".source-badge.real")).toContainText("SOURCE: REAL")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(8)
  })

  test("handles special characters and unicode in search safely", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-special-search", "x-process-time": "16ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(12), { request_id: "req-special-search" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    const searchInput = page.getByPlaceholder("搜索策略名称 / 类型")
    const pageErrors: string[] = []
    page.on("pageerror", (error) => pageErrors.push(error.message))

    const inputs = [
      "!@#$%^&*()",
      "<script>alert(1)</script>",
      "\";DROP TABLE strategy;",
      "../../etc/passwd",
      "策略测试",
      "📈💰🚀",
      "こんにちは",
    ]

    for (const value of inputs) {
      await searchInput.fill(value)
      await page.waitForTimeout(120)
      await expect(page.locator(".strategy-management")).toBeVisible()
    }

    expect(pageErrors).toHaveLength(0)
  })

  test("keeps page stable with malformed query parameters", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-query", "x-process-time": "17ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(6), { request_id: "req-query" })),
      })
    })

    const urls = [
      `${FRONTEND_BASE_URL}/strategy/repo?id=`,
      `${FRONTEND_BASE_URL}/strategy/repo?foo=bar&baz=qux`,
      `${FRONTEND_BASE_URL}/strategy/repo?[]=test`,
      `${FRONTEND_BASE_URL}/strategy/repo?id[]=1&id[]=2`,
    ]

    for (const url of urls) {
      await page.goto(url, { waitUntil: "domcontentloaded" })
      await expect(page.locator(".strategy-management")).toBeVisible()
      await expect(page.getByRole("heading", { name: "策略管理" })).toBeVisible()
    }
  })

  test("remains consistent under rapid search and filter changes", async ({ page }) => {
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-rapid", "x-process-time": "19ms" },
        body: JSON.stringify(buildUnifiedResponse(buildStrategyDataset(20), { request_id: "req-rapid" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    const searchInput = page.getByPlaceholder("搜索策略名称 / 类型")
    const statusSelect = page.locator(".toolbar-select")

    await searchInput.fill("Boundary-01")
    await statusSelect.selectOption("running")
    await searchInput.fill("Boundary")
    await statusSelect.selectOption("paused")
    await searchInput.fill("mean_reversion")
    await statusSelect.selectOption("all")

    await expect(page.locator(".strategy-management")).toBeVisible()
    await expect(page.locator(".strategy-table, .empty-state").first()).toBeVisible()
  })
})
