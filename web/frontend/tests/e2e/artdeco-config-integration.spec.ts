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

function isIgnoredConsoleError(text: string, browserName: string): boolean {
  if (browserName === "firefox" && text.trim() === "Error") {
    return true
  }

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
    "Importing a module script failed",
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

async function stubReadinessProbe(page: Parameters<typeof test>[0]["page"]) {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "e2e-artdeco-ready",
          data: { status: "ready" },
        }),
      })
    })
  }
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
    await stubReadinessProbe(page)
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
      {
        path: "/market/realtime",
        verify: async () => {
          await expect(page.getByRole("heading", { name: "实时行情工作台" })).toBeVisible()
        },
      },
      {
        path: "/market/technical",
        verify: async () => {
          await expect(page.locator(".market-kline-tab, .artdeco-technical-analysis").first()).toBeVisible()
        },
      },
      {
        path: "/strategy/repo",
        verify: async () => {
          await expect(page.locator(".strategy-management").first()).toBeVisible()
        },
      },
      {
        path: "/strategy/backtest",
        verify: async () => {
          await expect(page.locator(".backtest-analysis-page").first()).toBeVisible()
        },
      },
      {
        path: "/watchlist/manage",
        verify: async () => {
          await expect(page.locator(".watchlist-manager, .watchlist-page, .page-enter").first()).toBeVisible()
        },
      },
    ]

    for (const item of routeChecks) {
      await page.goto(`${FRONTEND_BASE_URL}${item.path}`, { waitUntil: "domcontentloaded" })
      await item.verify()
    }
  })

  test("keeps nested routes free of uncaught page errors", async ({ page }) => {
    const nestedRoutes = ["/market/technical", "/trade/positions", "/watchlist/manage", "/system/settings"]

    for (const route of nestedRoutes) {
      const pageErrors: string[] = []
      const onPageError = (error: Error) => pageErrors.push(error.message)
      page.on("pageerror", onPageError)

      await page.goto(`${FRONTEND_BASE_URL}${route}`, { waitUntil: "domcontentloaded" })
      await page.waitForTimeout(500)
      page.off("pageerror", onPageError)

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
      { path: "/dashboard", selector: "main.artdeco-main" },
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

  test("does not emit critical console errors on key routes", async ({ page, browserName }) => {
    const routes = [
      { path: "/dashboard", selector: "main.artdeco-main" },
      { path: "/market/realtime", selector: "main.artdeco-main, .market-realtime-tab" },
      { path: "/strategy/repo", selector: "main.artdeco-main, .strategy-management" },
      { path: "/strategy/backtest", selector: "main.artdeco-main, .backtest-analysis-page" },
      { path: "/system/config", selector: "main.artdeco-main, .system-settings-page" },
    ]
    const criticalErrorsByRoute: Record<string, string[]> = {}

    for (const route of routes) {
      const consoleErrors: string[] = []
      const onConsole = (msg: { type: () => string; text: () => string }) => {
        if (msg.type() === "error" && !isIgnoredConsoleError(msg.text(), browserName)) {
          consoleErrors.push(msg.text())
        }
      }

      page.on("console", onConsole)

      await page.goto(`${FRONTEND_BASE_URL}${route.path}`, { waitUntil: "domcontentloaded" })
      await expect(page.locator(route.selector).first()).toBeVisible()
      await page.waitForTimeout(500)
      page.off("console", onConsole)
      criticalErrorsByRoute[route.path] = [...consoleErrors]
    }

    const remainingRoutes = Object.entries(criticalErrorsByRoute).filter(([, errors]) => errors.length > 0)
    expect(remainingRoutes, `critical console errors: ${JSON.stringify(remainingRoutes)}`).toHaveLength(0)
  })
})
