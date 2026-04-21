import { expect, test } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: "ok",
    data,
    timestamp: "2026-04-19T00:00:00Z",
    request_id: "req-risk-default",
    ...(overrides ?? {}),
  }
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
    localStorage.setItem("auth_token", "e2e-risk-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  })
}

async function mockRiskOverviewApis(page: Parameters<typeof test>[0]["page"]) {
  await page.route(/https?:\/\/[^/]+\/api\/.*/, async (route) => {
    const url = new URL(route.request().url())

    if (url.pathname === "/api/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { status: "ready" },
            { request_id: "req-risk-ready", message: "system ready" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              csrf_token: "e2e-risk-csrf",
              token_type: "bearer",
              expires_in: 3600,
            },
            { request_id: "req-risk-csrf" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/v1/data/markets/overview" || url.pathname === "/api/v1/market/overview") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            { up_count: 1888, down_count: 1024, turnover: 8234 },
            { request_id: "req-risk-market-overview" },
          ),
        ),
      })
      return
    }

    if (url.pathname === "/api/v1/monitoring/alert-rules") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-risk-rules",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              {
                id: "rule-1",
                rule_name: "单票止损线",
                rule_type: "stop_loss",
                symbol: "600519",
                is_active: true,
                priority: 1,
              },
              {
                id: "rule-2",
                rule_name: "组合波动率约束",
                rule_type: "portfolio_volatility",
                symbol: "GLOBAL",
                is_active: true,
                priority: 2,
              },
            ],
            { request_id: "req-risk-rules" },
          ),
        ),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildUnifiedResponse([])),
    })
  })
}

test.describe("Risk Overview E2E", () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockRiskOverviewApis(page)
  })

  test("loads risk overview shell, rule tab, and alert tab", async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/overview`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { level: 1, name: "风险概览工作台" })).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新概览" })).toBeVisible()
    await expect(page.locator(".stats-strip")).toContainText("规则总数")
    await expect(page.locator(".stats-strip")).toContainText("启用规则")

    await page.getByRole("button", { name: "规则清单" }).click()
    await expect(page.locator(".content-shell")).toContainText("单票止损线")
    await expect(page.locator(".content-shell")).toContainText("组合波动率约束")

    await page.getByRole("button", { name: "预警消息" }).click()
    await expect(page.locator(".alerts-list")).toContainText("组合波动率超过阈值 18%")

    await page.getByRole("button", { name: "刷新概览" }).click()
    await expect(page.getByRole("heading", { level: 1, name: "风险概览工作台" })).toBeVisible()
  })
})
