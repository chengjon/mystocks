import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("../helpers/port-env.js")
import { waitForAppReady } from "../helpers/readiness"

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

      if (url.pathname === "/api/csrf-token") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ success: true, data: { csrf_token: "e2e-menu-csrf" } }),
        })
        return
      }

      if (url.pathname === "/api/v1/data/markets/overview") {
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

      if (url.pathname === "/api/health/ready") {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            message: "系统就绪检查完成",
            request_id: "e2e-menu-ready",
            data: { status: "ready" },
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
    await waitForAppReady(page)
  })

  test("navigates to dealing room shell without errors", async ({ page }) => {
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.locator("main.artdeco-main")).toBeVisible()
    await expect(page.locator(".artdeco-dashboard")).toBeVisible()
    await expect(page.locator(".artdeco-sidebar-v3")).toBeVisible()
  })

  test("navigates to market realtime via sidebar menu", async ({ page }) => {
    await page.locator("button.domain-root", { hasText: "市场行情" }).click()
    await page.locator('a.nav-item.child-item[href="/market/realtime"]').click()
    await expect(page).toHaveURL(/\/market\/realtime/)
    await expect(page.locator(".market-realtime-tab")).toBeVisible()
  })

  test("keeps market page usable when a key API fails", async ({ page }) => {
    await page.route("**/api/v1/data/markets/overview", (route) => route.abort("failed"))
    await page.goto(`${FRONTEND_BASE_URL}/market/realtime`, { waitUntil: "domcontentloaded" })
    await waitForAppReady(page)
    await expect(page.locator(".market-realtime-tab")).toBeVisible()
    await expect(page.locator("h2.section-title")).toContainText("实时行情流")
  })
})
