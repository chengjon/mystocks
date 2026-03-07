/**
 * Strategy Management - Monitoring & UI
 *
 * Updated for the table-based Strategy Management page (`/strategy/repo`).
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

const desktopViewports = [
  { width: 1920, height: 1080, name: "Full HD" },
  { width: 1680, height: 1050, name: "Widescreen" },
  { width: 1440, height: 900, name: "Laptop" },
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

function buildStrategyDataset(count: number) {
  const statuses = ["active", "paused", "archived"] as const
  const types = ["momentum", "mean_reversion", "breakout"] as const
  return Array.from({ length: count }, (_, idx) => ({
    strategy_id: idx + 1,
    strategy_name: `Strategy-${String(idx + 1).padStart(2, "0")}`,
    strategy_type: types[idx % types.length],
    description: `strategy description ${idx + 1}`,
    status: statuses[idx % statuses.length],
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
          { request_id: "req-csrf-1" }
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

test.describe("Strategy Management - Monitoring & UI", () => {
  test.describe.configure({ timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await setupAuthenticatedSession(page)
    await mockCsrfEndpoint(page)
  })

  test("searches strategies by keyword", async ({ page }) => {
    const dataset = buildStrategyDataset(18)
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-search-1", "x-process-time": "24ms" },
        body: JSON.stringify(buildUnifiedResponse(dataset, { request_id: "req-search-1" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(8)

    await page.getByPlaceholder("搜索策略名称 / 类型").fill("Strategy-03")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".strategy-table tbody tr").first()).toContainText("Strategy-03")
  })

  test("filters strategies by status", async ({ page }) => {
    const dataset = buildStrategyDataset(18)
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-filter-1", "x-process-time": "20ms" },
        body: JSON.stringify(buildUnifiedResponse(dataset, { request_id: "req-filter-1" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await page.locator(".toolbar-select").selectOption("paused")

    const rows = page.locator(".strategy-table tbody tr")
    await expect(rows).toHaveCount(6)
    await expect(rows.first().locator(".status-chip")).toContainText("PAUSED")
  })

  test("paginates table rows", async ({ page }) => {
    const dataset = buildStrategyDataset(18)
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-page-1", "x-process-time": "31ms" },
        body: JSON.stringify(buildUnifiedResponse(dataset, { request_id: "req-page-1" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    const paginationText = page.locator(".pagination-text")
    const nextPageButton = page.locator(".pagination-row .toolbar-button").last()
    await expect(paginationText).toContainText("第 1 / 3 页")
    await expect(nextPageButton).toBeEnabled()
    await nextPageButton.scrollIntoViewIfNeeded()

    try {
      await nextPageButton.click({ timeout: 3000 })
    } catch {
      // WebKit occasionally reports visible footer buttons as outside viewport.
      await nextPageButton.evaluate((button: HTMLButtonElement) => button.click())
    }
    await expect.poll(async () => (await paginationText.textContent())?.trim() ?? "").toContain("第 2 / 3 页")
  })

  test("refreshes strategy list and keeps page stable", async ({ page }) => {
    const dataset = buildStrategyDataset(10)
    let hitCount = 0
    await routeStrategyList(page, async (route) => {
      hitCount += 1
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": `req-refresh-${hitCount}`,
          "x-process-time": "28ms",
        },
        body: JSON.stringify(buildUnifiedResponse(dataset, { request_id: `req-refresh-${hitCount}` })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".strategy-table")).toBeVisible()

    const refreshButton = page.getByRole("button", { name: "刷新" })
    await expect(refreshButton).toBeEnabled()
    await refreshButton.click()

    await expect.poll(() => hitCount).toBeGreaterThanOrEqual(2)
    await expect(page.locator(".strategy-table")).toBeVisible()
    await expect(page.locator(".trace-id").first()).toContainText("REQ_ID: req-refresh-")
  })

  test("supports layout rendering across desktop viewports", async ({ page }) => {
    const dataset = buildStrategyDataset(9)
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-layout-1", "x-process-time": "19ms" },
        body: JSON.stringify(buildUnifiedResponse(dataset, { request_id: "req-layout-1" })),
      })
    })

    for (const viewport of desktopViewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })
      await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
      await expect(page.locator("main.artdeco-main")).toBeVisible()
      await expect(page.locator(".strategy-management")).toBeVisible()
    }
  })

  test("keeps interactive buttons accessible", async ({ page }) => {
    const dataset = buildStrategyDataset(8)
    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: { "content-type": "application/json", "x-request-id": "req-a11y-1", "x-process-time": "23ms" },
        body: JSON.stringify(buildUnifiedResponse(dataset, { request_id: "req-a11y-1" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".strategy-management")).toBeVisible()
    await expect.poll(async () => page.locator("button").count()).toBeGreaterThan(0)

    const buttons = page.locator("button")
    const count = await buttons.count()
    expect(count).toBeGreaterThan(0)

    const sampleSize = Math.min(count, 12)
    let accessibleCount = 0
    for (let i = 0; i < sampleSize; i += 1) {
      const button = buttons.nth(i)
      const ariaLabel = await button.getAttribute("aria-label")
      const text = (await button.textContent())?.trim() ?? ""
      if (Boolean(ariaLabel) || text.length > 0) {
        accessibleCount += 1
      }
    }
    expect(accessibleCount).toBeGreaterThanOrEqual(Math.max(1, Math.floor(sampleSize * 0.6)))
  })
})
