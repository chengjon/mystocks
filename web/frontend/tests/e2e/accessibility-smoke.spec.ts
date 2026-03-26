import AxeBuilder from "@axe-core/playwright"
import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

async function stubReadinessProbe(page: Parameters<typeof test>[0]["page"]) {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "e2e-axe-ready",
          data: { status: "ready" },
        }),
      })
    })
  }
}

async function seedStrategySession(page: Parameters<typeof test>[0]["page"]) {
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

  await page.route("**/api/csrf-token", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: { csrf_token: "e2e-axe-csrf" },
      }),
    })
  })

  await page.route("**/api/v1/strategy/strategies**", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "content-type": "application/json",
        "x-request-id": "req-axe-strategy",
        "x-process-time": "18ms",
      },
      body: JSON.stringify({
        success: true,
        code: 200,
        message: "ok",
        data: {
          items: [
            {
              id: "1",
              strategy_id: "1",
              strategy_name: "Accessibility Strategy",
              strategy_type: "momentum",
              description: "axe smoke",
              status: "active",
              updated_at: "2026-03-22T00:00:00Z",
            },
          ],
          total: 1,
          page: 1,
          page_size: 20,
        },
        request_id: "req-axe-strategy",
        process_time: "18ms",
        timestamp: "2026-03-22T00:00:00Z",
      }),
    })
  })
}

function expectNoSeriousViolations(results: Awaited<ReturnType<AxeBuilder["analyze"]>>) {
  const blockingViolations = results.violations.filter((violation) =>
    ["serious", "critical"].includes(violation.impact ?? ""),
  )

  expect(
    blockingViolations.map((violation) => ({
      id: violation.id,
      impact: violation.impact,
      nodes: violation.nodes.length,
    })),
  ).toEqual([])
}

test.describe("Accessibility smoke", () => {
  test("login page has no serious accessibility violations", async ({ page }) => {
    await stubReadinessProbe(page)
    await page.goto(`${FRONTEND_BASE_URL}/login`, { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("heading", { name: "LOGIN" })).toBeVisible()

    const results = await new AxeBuilder({ page })
      .disableRules(["color-contrast"])
      .analyze()
    expectNoSeriousViolations(results)
  })

  test("strategy repository page has no serious accessibility violations", async ({ page }) => {
    await stubReadinessProbe(page)
    await seedStrategySession(page)
    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`, { waitUntil: "domcontentloaded" })
    await expect(page.getByRole("heading", { level: 1, name: "策略仓库工作台" })).toBeVisible()

    const results = await new AxeBuilder({ page })
      .include("main")
      .disableRules(["color-contrast"])
      .analyze()
    expectNoSeriousViolations(results)
  })
})
