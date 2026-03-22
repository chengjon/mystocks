import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("../helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

const E2E_USER = {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  permissions: [],
}

test.describe("Critical Menu Navigation - Fixed", { tag: "@critical" }, () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(({ user }) => {
      localStorage.setItem("auth_token", "e2e-menu-token")
      localStorage.setItem("auth_user", JSON.stringify(user))
    }, { user: E2E_USER })

    await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
      const url = new URL(route.request().url())

      if (url.pathname === "/api/health/ready") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "system ready",
            request_id: "e2e-menu-ready",
            data: { status: "ready" },
          }),
        })
        return
      }

      if (url.pathname === "/api/csrf-token") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ success: true, data: { csrf_token: "e2e-menu-csrf" } }),
        })
        return
      }

      if (url.pathname === "/api/v1/data/markets/overview" || url.pathname === "/api/v1/market/overview") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: { up_count: 1800, down_count: 1100, turnover: 8234 },
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ success: true, data: [] }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })
    // Cold-start Vite runs can take >10s on the first dashboard render.
    await expect(page.locator(".artdeco-layout")).toBeVisible({ timeout: 20000 })
    await expect(page.getByText("QUANTIX")).toBeVisible({ timeout: 20000 })
  })

  test("navigates to dealing room shell without errors", async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.getByRole("main")).toBeVisible()
    await expect(page.getByRole("button", { name: "市场行情" })).toBeVisible()
    await expect(page.getByText("QUANTIX")).toBeVisible()
  })

  test("navigates to market realtime via sidebar menu", async ({ page }) => {
    await page.getByRole("button", { name: "市场行情" }).click()
    await page.getByRole("link", { name: /实时行情流/i }).click()
    await expect(page).toHaveURL(/\/market\/realtime/)
    await expect(page.getByRole("heading", { level: 2, name: "实时行情流" })).toBeVisible({ timeout: 10000 })
    await expect(page.getByRole("button", { name: "刷新行情" })).toBeVisible({ timeout: 10000 })
  })

  test("keeps market page usable when a key API fails", async ({ page }) => {
    await page.route("**/api/v1/data/markets/overview", (route) => route.abort("failed"))
    await page.goto(`${FRONTEND_BASE_URL}/market/realtime`, { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("heading", { level: 2, name: "实时行情流" })).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新行情" })).toBeVisible()
  })
})
