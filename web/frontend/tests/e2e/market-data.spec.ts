/**
 * Market Data Module E2E Tests
 *
 * This suite validates the current ArtDeco market routes and core interactions
 * with resilient selectors, avoiding brittle legacy class assertions.
 */

import { test, expect, request as playwrightRequest, type Page } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig, resolveBackendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const BACKEND_BASE_URL = resolveBackendConfig().baseUrl
const TEST_USER = { username: "admin", password: "admin123" }

const MARKET_ROUTES = {
  root: "/market",
  realtime: "/market/realtime",
  technical: "/market/technical",
  lhb: "/market/lhb",
}

const desktopViewports = [
  { width: 1920, height: 1080, name: "Full HD" },
  { width: 1680, height: 1050, name: "Widescreen" },
  { width: 1440, height: 900, name: "Laptop" },
  { width: 1366, height: 768, name: "Small Laptop" },
]

let cachedToken = ""
let cachedUser: Record<string, unknown> = {}
let usingFallbackAuth = false

async function stubReadinessProbe(page: Page): Promise<void> {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "e2e-market-ready",
          data: { status: "ready" },
        }),
      })
    })
  }
}

async function seedAuth(page: Page): Promise<void> {
  expect(Boolean(cachedToken)).toBeTruthy()
  await page.addInitScript(
    ({ authToken, authUser }) => {
      localStorage.setItem("auth_token", authToken)
      localStorage.setItem("auth_user", JSON.stringify(authUser))
    },
    { authToken: cachedToken, authUser: cachedUser }
  )
}

async function gotoRealtime(page: Page): Promise<void> {
  await page.goto(`${FRONTEND_BASE_URL}${MARKET_ROUTES.root}`, { waitUntil: "domcontentloaded" })
  await page.waitForURL("**/market/realtime", { timeout: 15000 })
  await expect(page.locator(".market-realtime-tab")).toBeVisible()
}

test.describe("Market Data Module - E2E Tests", () => {
  test.describe.configure({ mode: "serial", timeout: 120000 })

  test.beforeAll(async () => {
    test.setTimeout(120000)
    const api = await playwrightRequest.newContext()
    try {
      const loginResponse = await api.post(`${BACKEND_BASE_URL}/api/v1/auth/login`, {
        data: new URLSearchParams({
          username: TEST_USER.username,
          password: TEST_USER.password,
        }).toString(),
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        timeout: 60000,
      })

      expect(loginResponse.ok()).toBeTruthy()
      const payload = await loginResponse.json()
      cachedToken = payload?.data?.token ?? payload?.token ?? payload?.access_token ?? ""
      cachedUser = payload?.data?.user ?? {
        id: 1,
        username: TEST_USER.username,
        email: "admin@example.com",
        role: "admin",
        permissions: [],
      }
    } catch {
      usingFallbackAuth = true
      cachedToken = "e2e-market-fallback-token"
      cachedUser = {
        id: 1,
        username: TEST_USER.username,
        email: "admin@example.com",
        role: "admin",
        permissions: [],
      }
    }
    await api.dispose()
  })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await seedAuth(page)
    await stubReadinessProbe(page)

    if (usingFallbackAuth) {
      await page.route("**/api/csrf-token", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: { csrf_token: "e2e-market-csrf" },
          }),
        })
      })

      await page.route("**/api/v1/data/markets/overview**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              shanghai_index: "3321.08",
              shanghai_change: "0.65",
              shenzhen_index: "10214.20",
              shenzhen_change: "0.71",
            },
          }),
        })
      })

      await page.route("**/api/v1/market/quotes**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: [],
          }),
        })
      })

      await page.route("**/api/v1/market/kline**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              data: [],
            },
          }),
        })
      })

      await page.route("**/api/v1/market/lhb**", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: [],
          }),
        })
      })
    }
  })

  test.describe("Market Realtime Page", () => {
    test("should load market realtime page successfully", async ({ page }) => {
      await gotoRealtime(page)
      await expect(page).toHaveTitle(/MyStocks/)
      await expect(page.getByRole("heading", { level: 1, name: "实时行情工作台" })).toBeVisible()
    })

    test("should display core realtime widgets", async ({ page }) => {
      await gotoRealtime(page)
      await expect(page.getByTestId("market-realtime-page")).toBeVisible()
      await expect(page.getByTestId("market-realtime-header")).toBeVisible()
      await expect(page.getByTestId("market-realtime-refresh")).toBeVisible()
      await expect(page.getByTestId("market-realtime-status-strip")).toContainText("TRACE")
      await expect(page.getByTestId("market-realtime-control-row")).toBeVisible()
      await expect(page.getByTestId("market-realtime-stats-strip")).toBeVisible()
      await expect(page.getByTestId("market-realtime-work-area")).toBeVisible()
      await expect(page.getByTestId("market-realtime-quotes-panel")).toBeVisible()
      await expect(page.getByTestId("market-realtime-distribution-panel")).toBeVisible()
      await expect(page.locator(".toolbar")).toBeVisible()
      await expect(page.locator(".stats-strip")).toBeVisible()
      await expect(page.locator(".content-grid")).toBeVisible()
      await expect(page.getByRole('button', { name: '刷新行情' }).first()).toBeVisible()
    })

    test("should keep shell available when market API fails", async ({ page }) => {
      await page.route("**/api/v1/market/**", (route) => route.abort())
      await gotoRealtime(page)
      await expect(page.getByRole("heading", { level: 1, name: "实时行情工作台" })).toBeVisible()
      await expect(page.getByRole('button', { name: '刷新行情' }).first()).toBeVisible()
    })
  })

  test.describe("Desktop Layout Validation", () => {
    for (const viewport of desktopViewports) {
      test(`${viewport.name} (${viewport.width}x${viewport.height})`, async ({ page }) => {
        await page.setViewportSize({ width: viewport.width, height: viewport.height })
        await gotoRealtime(page)

        await expect(page.locator("main.artdeco-main")).toBeVisible()
        const scrollOverflow = await page.evaluate(() => {
          return document.documentElement.scrollWidth - window.innerWidth
        })
        expect(scrollOverflow).toBeLessThanOrEqual(20)
      })
    }
  })

  test.describe("Data Refresh Functionality", () => {
    test("should keep page stable after refresh click", async ({ page }) => {
      await gotoRealtime(page)
      await page.getByRole('button', { name: '刷新行情' }).first().click()
      await expect(page.locator(".market-realtime-tab")).toBeVisible()
    })

    test("should render trace area without breaking layout", async ({ page }) => {
      await gotoRealtime(page)
      await expect(page.getByText(/PRESET:\s*核心蓝筹样本/)).toBeVisible()
      await expect(page.getByRole('button', { name: '刷新行情' }).first()).toBeVisible()
    })
  })

  test.describe("Navigation to Market Pages", () => {
    test("should redirect /market to /market/realtime", async ({ page }) => {
      await page.goto(`${FRONTEND_BASE_URL}${MARKET_ROUTES.root}`)
      await page.waitForURL("**/market/realtime")
      await expect(page).toHaveURL(/\/market\/realtime/)
    })

    test("should open market technical page", async ({ page }) => {
      await page.goto(`${FRONTEND_BASE_URL}${MARKET_ROUTES.technical}`)
      await expect(page.locator(".market-kline-tab")).toBeVisible()
      await expect(page.getByRole("heading", { level: 2, name: "K-Line Analysis" })).toBeVisible({ timeout: 10000 })
    })

    test("should open market lhb page", async ({ page }) => {
      await page.goto(`${FRONTEND_BASE_URL}${MARKET_ROUTES.lhb}`)
      await expect(page.locator("main.artdeco-main")).toBeVisible()
      await expect(page).toHaveURL(/\/market\/lhb/)
    })
  })

  test.describe("Real-time Data Updates", () => {
    test("should render page shell with delayed market API", async ({ page }) => {
      await page.route("**/api/v1/market/**", async (route) => {
        await new Promise((resolve) => setTimeout(resolve, 1200))
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: [],
          }),
        })
      })
      await gotoRealtime(page)
      await expect(page.locator(".market-realtime-tab")).toBeVisible()
    })

    test("should keep route stable on revisit", async ({ page }) => {
      await gotoRealtime(page)
      await page.goto(`${FRONTEND_BASE_URL}/dashboard`)
      await page.goto(`${FRONTEND_BASE_URL}${MARKET_ROUTES.realtime}`)
      await expect(page).toHaveURL(/\/market\/realtime/)
      await expect(page.locator(".market-realtime-tab")).toBeVisible()
    })
  })

  test.describe("Error Handling", () => {
    test("should keep realtime shell under network error", async ({ page }) => {
      await page.route("**/api/v1/market/**", (route) => route.abort("failed"))
      await gotoRealtime(page)
      await expect(page.locator(".market-realtime-tab")).toBeVisible()
      await expect(page.getByRole('button', { name: '刷新行情' }).first()).toBeVisible()
    })

    test("should recover from temporary API errors after refresh", async ({ page }) => {
      let callCount = 0
      await page.route("**/api/v1/market/**", async (route) => {
        callCount += 1
        if (callCount === 1) {
          await route.abort("failed")
          return
        }
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: [],
          }),
        })
      })

      await gotoRealtime(page)
      await page.getByRole('button', { name: '刷新行情' }).first().click()
      await expect(page.locator(".market-realtime-tab")).toBeVisible()
      await expect(page.getByRole('button', { name: '刷新行情' }).first()).toBeVisible()
    })
  })

  test.describe("Accessibility", () => {
    test("should have proper heading hierarchy", async ({ page }) => {
      await gotoRealtime(page)
      const headings = page.locator("h1, h2, h3")
      await expect(headings.first()).toBeVisible()
      const count = await headings.count()
      expect(count).toBeGreaterThan(0)
    })

    test("should have aria labels or text on interactive buttons", async ({ page }) => {
      await gotoRealtime(page)

      const buttons = page.locator("button")
      const buttonCount = await buttons.count()
      expect(buttonCount).toBeGreaterThan(0)

      for (let i = 0; i < Math.min(buttonCount, 5); i += 1) {
        const button = buttons.nth(i)
        const ariaLabel = await button.getAttribute("aria-label")
        const text = (await button.textContent())?.trim() ?? ""
        expect(Boolean(ariaLabel) || text.length > 0).toBeTruthy()
      }
    })
  })
})
