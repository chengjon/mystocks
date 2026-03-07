import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

const E2E_USER = {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  permissions: [],
}

const MOCK_KLINE = Array.from({ length: 12 }).map((_, index) => {
  const base = 100 + index
  return {
    datetime: `2026-02-${String(index + 1).padStart(2, "0")} 15:00:00`,
    open: base,
    high: base + 2,
    low: base - 1,
    close: base + 1,
    volume: 1000000 + index * 10000,
  }
})

function isIgnoredConsoleError(text: string, browserName: string): boolean {
  const ignored = [
    "favicon",
    "downloadable font",
    "fonts.gstatic.com",
    "Failed to load resource",
    "WebSocket",
  ]
  if (browserName === "webkit" && text.includes("Importing a module script failed")) {
    return true
  }
  return ignored.some((item) => text.includes(item))
}

test.describe("K-line Chart E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(({ user }) => {
      localStorage.setItem("auth_token", "e2e-kline-token")
      localStorage.setItem("auth_user", JSON.stringify(user))
    }, { user: E2E_USER })

    await page.route("**/api/csrf-token", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { csrf_token: "e2e-kline-csrf" },
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
            data: MOCK_KLINE,
          },
          request_id: "e2e-kline-rid",
          process_time_ms: 9,
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/market/technical`, { waitUntil: "domcontentloaded" })
  })

  test("loads technical page shell", async ({ page }) => {
    await expect(page.locator(".market-kline-tab")).toBeVisible()
    await expect(page.locator("h2.section-title")).toContainText("K-Line Analysis")
    await expect(page).toHaveURL(/\/market\/technical/)
  })

  test("renders chart placeholder and latest summary", async ({ page }) => {
    await expect(page.locator(".kline-container")).toBeVisible()
    await expect(page.locator(".chart-placeholder")).toContainText("Real-time K-Line Data Stream Active")
    await expect(page.locator(".data-summary")).toContainText("Data Points: 12")
  })

  test("renders recent K-line rows", async ({ page }) => {
    const rows = page.locator(".artdeco-table tbody tr")
    await expect(rows).toHaveCount(5)
    await expect(rows.first()).toBeVisible()
    await expect(rows.first().locator("td").nth(1)).toContainText(/^\d+/)
  })

  test("shows request trace metadata when available", async ({ page }) => {
    await expect(page.locator(".trace-id")).toContainText("REQ:")
  })

  test("keeps layout stable on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.reload({ waitUntil: "domcontentloaded" })
    await expect(page.locator("main.artdeco-main")).toBeVisible()
    await expect(page.locator(".market-kline-tab")).toBeVisible()
  })

  test("keeps layout stable on tablet viewport", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.reload({ waitUntil: "domcontentloaded" })
    await expect(page.locator("main.artdeco-main")).toBeVisible()
    await expect(page.locator(".market-kline-tab")).toBeVisible()
  })

  test("does not emit critical console errors", async ({ page, browserName }) => {
    const consoleErrors: string[] = []
    const onConsole = (msg: { type: () => string; text: () => string }) => {
      if (msg.type() === "error" && !isIgnoredConsoleError(msg.text(), browserName)) {
        consoleErrors.push(msg.text())
      }
    }

    page.on("console", onConsole)

    await page.reload({ waitUntil: "domcontentloaded" })
    await expect(page.locator(".market-kline-tab")).toBeVisible()
    await page.waitForTimeout(400)
    page.off("console", onConsole)
    expect(consoleErrors).toHaveLength(0)
  })
})
