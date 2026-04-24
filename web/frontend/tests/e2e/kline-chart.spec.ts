import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

// Canonical stable E2E smoke coverage for the technical shell.
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

    await page.route("**/api/health/ready", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "e2e-kline-ready",
          data: { status: "ready" },
        }),
      })
    })

    const fulfillKline = async (route: { fulfill: (options: { status: number; contentType: string; body: string }) => Promise<void> }) => {
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
    }

    await page.route("**/api/v1/market/kline**", fulfillKline)
    await page.route("**/api/market/kline**", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          data: MOCK_KLINE.map((item) => ({
            timestamp: Date.parse(item.datetime),
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
            volume: item.volume,
          })),
          categoryData: MOCK_KLINE.map((item) => item.datetime),
          values: MOCK_KLINE.map((item) => [item.open, item.close, item.low, item.high]),
          volumes: MOCK_KLINE.map((item) => item.volume),
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/market/technical`, { waitUntil: "domcontentloaded" })
  })

  test("loads technical page shell", async ({ page }) => {
    await expect(page.getByRole("heading", { level: 2, name: "K-Line Analysis" })).toBeVisible({ timeout: 10000 })
    await expect(page.locator(".pro-kline-chart")).toBeVisible()
    await expect(page).toHaveURL(/\/market\/technical/)
  })

  test("renders chart placeholder and latest summary", async ({ page }) => {
    await expect(page.locator(".chart-summary")).toContainText("DATA POINTS:")
    await expect(page.locator(".pro-kline-chart")).toBeVisible()
  })

  test("renders recent K-line rows", async ({ page }) => {
    const rows = page.getByRole("table").getByRole("row")
    await expect(rows).toHaveCount(6)
    await expect(rows.nth(1)).toBeVisible()
    await expect(rows.nth(1).getByRole("cell").nth(1)).toContainText(/^\d+/)
  })

  test("shows request trace metadata when available", async ({ page }) => {
    await expect(page.getByText(/SYMBOL:\s*000001/)).toBeVisible()
  })

  test("keeps layout stable on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 812 })
    await page.reload({ waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible()
    await expect(page.getByRole("heading", { level: 2, name: "K-Line Analysis" })).toBeVisible()
  })

  test("keeps layout stable on tablet viewport", async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 })
    await page.reload({ waitUntil: "domcontentloaded" })
    await expect(page.getByRole("main")).toBeVisible()
    await expect(page.getByRole("heading", { level: 2, name: "K-Line Analysis" })).toBeVisible()
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
    await expect(page.getByRole("heading", { level: 2, name: "K-Line Analysis" })).toBeVisible()
    await page.waitForTimeout(400)
    page.off("console", onConsole)
    expect(consoleErrors).toHaveLength(0)
  })
})
