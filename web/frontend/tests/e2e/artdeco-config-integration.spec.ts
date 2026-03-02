/**
 * ArtDeco Route & Configuration Integration E2E
 *
 * Updated to verify current route shells and integration stability.
 */

import { expect, test, request as playwrightRequest } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig, resolveBackendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const BACKEND_BASE_URL = resolveBackendConfig().baseUrl
const TEST_USER = { username: "admin", password: "admin123" }
let cachedToken = ""
let cachedUser: Record<string, unknown> = {}

function isIgnoredConsoleError(text: string): boolean {
  const ignored = [
    "favicon",
    "manifest",
    "Service Worker",
    "ResizeObserver loop",
    "Failed to load resource",
    "access control checks",
    "WebSocket",
    "ws://",
    "downloadable font",
    "fonts.gstatic.com",
  ]
  return ignored.some((item) => text.includes(item))
}

async function setupAuthenticatedSession(page: Parameters<typeof test>[0]["page"]) {
  expect(Boolean(cachedToken)).toBeTruthy()
  await page.addInitScript(
    ({ token, user }) => {
      localStorage.setItem("auth_token", token)
      localStorage.setItem("auth_user", JSON.stringify(user))
    },
    { token: cachedToken, user: cachedUser }
  )
}

test.describe("ArtDeco Configuration Integration", () => {
  test.describe.configure({ mode: "serial", timeout: 120000 })

  test.beforeAll(async () => {
    test.setTimeout(120000)
    const api = await playwrightRequest.newContext()
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
    await api.dispose()
  })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await page.route("**/api/v1/strategy/strategies**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: [
            {
              id: "strat-001",
              name: "MA Crossover",
              description: "E2E mock strategy",
              status: "active",
              type: "trend_following",
              parameters: { fast_period: 5, slow_period: 20 },
              created_at: "2026-02-01T00:00:00Z",
              updated_at: "2026-02-01T00:00:00Z",
            },
          ],
          request_id: "e2e-artdeco-config-rid",
          process_time_ms: 8,
        }),
      })
    })
  })

  test("loads key route shells with expected components", async ({ page }) => {
    const routeChecks = [
      { path: "/market/realtime", selector: ".market-realtime-tab" },
      { path: "/market/technical", selector: ".market-kline-tab" },
      { path: "/strategy/repo", selector: ".strategy-management" },
      { path: "/strategy/backtest", selector: ".backtest-analysis-page" },
      { path: "/watchlist/manage", selector: ".watchlist-manager, .watchlist-page, .page-enter" },
    ]

    for (const item of routeChecks) {
      await page.goto(`${FRONTEND_BASE_URL}${item.path}`, { waitUntil: "domcontentloaded" })
      await expect(page.locator(item.selector).first()).toBeVisible()
    }
  })

  test("keeps nested routes free of uncaught page errors", async ({ page }) => {
    const nestedRoutes = ["/market/technical", "/trade/positions", "/watchlist/manage", "/system/settings"]

    for (const route of nestedRoutes) {
      const pageErrors: string[] = []
      page.on("pageerror", (error) => pageErrors.push(error.message))

      await page.goto(`${FRONTEND_BASE_URL}${route}`, { waitUntil: "domcontentloaded" })
      await page.waitForTimeout(500)

      expect(pageErrors).toHaveLength(0)
    }
  })

  test("supports expected route redirects", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/market`)
    await expect(page).toHaveURL(/\/market\/realtime/)

    await page.goto(`${FRONTEND_BASE_URL}/strategy`)
    await expect(page).toHaveURL(/\/strategy\/repo/)
  })

  test("renders main layout container for domain entry routes", async ({ page }) => {
    const domainRouteChecks = [
      { path: "/dealing-room", selector: "main.artdeco-main" },
      { path: "/market/realtime", selector: "main.artdeco-main, .market-realtime-tab" },
      { path: "/strategy/repo", selector: "main.artdeco-main, .strategy-management" },
      { path: "/system/config", selector: "main.artdeco-main, .system-settings-page" },
    ]

    for (const item of domainRouteChecks) {
      await page.goto(`${FRONTEND_BASE_URL}${item.path}`, { waitUntil: "domcontentloaded" })
      expect(new URL(page.url()).pathname).not.toBe("/login")
      await expect(page.locator(item.selector).first()).toBeVisible()
      await expect(page).toHaveTitle(/MyStocks/)
    }
  })

  test("does not emit critical console errors on key routes", async ({ page }) => {
    const routes = ["/dealing-room", "/market/realtime", "/strategy/repo", "/strategy/backtest", "/system/config"]
    const criticalErrorsByRoute: Record<string, string[]> = {}

    for (const route of routes) {
      const consoleErrors: string[] = []
      page.on("console", (msg) => {
        if (msg.type() === "error" && !isIgnoredConsoleError(msg.text())) {
          consoleErrors.push(msg.text())
        }
      })

      await page.goto(`${FRONTEND_BASE_URL}${route}`, { waitUntil: "domcontentloaded" })
      await page.waitForTimeout(500)
      criticalErrorsByRoute[route] = [...consoleErrors]
    }

    const remainingRoutes = Object.entries(criticalErrorsByRoute).filter(([, errors]) => errors.length > 0)
    expect(remainingRoutes, `critical console errors: ${JSON.stringify(remainingRoutes)}`).toHaveLength(0)
  })
})
