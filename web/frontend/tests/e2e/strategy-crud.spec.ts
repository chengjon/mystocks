/**
 * Strategy Management CRUD E2E
 *
 * Uses deterministic API mocking against the current ArtDeco Strategy Management
 * implementation (`/strategy/repo`) to verify stable CRUD/lifecycle behavior.
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

const strategyDetailEndpoints = (id: string) => [
  `**/api/v1/strategy/strategies/${id}**`,
  `**/api/mock/strategy/strategies/${id}**`,
  `**/api/api/v1/strategy/strategies/${id}**`,
  `**/api/api/mock/strategy/strategies/${id}**`,
]

const strategyLifecycleEndpoints = (id: string, action: "start" | "pause" | "resume" | "stop") => [
  `**/api/v1/strategy/${id}/${action}**`,
  `**/api/mock/strategy/${id}/${action}**`,
  `**/api/api/v1/strategy/${id}/${action}**`,
  `**/api/api/mock/strategy/${id}/${action}**`,
]

interface StrategyRecord {
  strategy_id: number
  strategy_name: string
  strategy_type: string
  description: string
  status: string
  updated_at: string
}

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

async function stubReadinessProbe(page: Parameters<typeof test>[0]["page"]) {
  for (const endpoint of ["**/api/health/ready", "**/health/ready"]) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              status: "ready",
            },
            { request_id: "req-ready-1" }
          )
        ),
      })
    })
  }
}

async function routeStrategyList(
  page: Parameters<typeof test>[0]["page"],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of STRATEGY_LIST_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

async function routeStrategyDetail(
  page: Parameters<typeof test>[0]["page"],
  id: string,
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of strategyDetailEndpoints(id)) {
    await page.route(endpoint, handler)
  }
}

async function routeStrategyLifecycle(
  page: Parameters<typeof test>[0]["page"],
  id: string,
  action: "start" | "pause" | "resume" | "stop",
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of strategyLifecycleEndpoints(id, action)) {
    await page.route(endpoint, handler)
  }
}

test.describe("Strategy Management - CRUD", () => {
  test.describe.configure({ mode: "serial", timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await stubReadinessProbe(page)
    await mockCsrfEndpoint(page)
  })

  test("loads strategy table with trace metadata", async ({ page }) => {
    const listPayload: StrategyRecord[] = [
      {
        strategy_id: 11,
        strategy_name: "Momentum Alpha",
        strategy_type: "momentum",
        description: "alpha strategy",
        status: "active",
        updated_at: "2026-03-01T10:00:00Z",
      },
      {
        strategy_id: 12,
        strategy_name: "Mean Reversion Beta",
        strategy_type: "mean_reversion",
        description: "beta strategy",
        status: "paused",
        updated_at: "2026-03-01T10:05:00Z",
      },
    ]

    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-list-1",
          "x-process-time": "125ms",
        },
        body: JSON.stringify(buildUnifiedResponse(listPayload, { request_id: "req-list-1" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByRole("heading", { name: "策略管理" })).toBeVisible()
    await expect(page.locator(".source-badge.real")).toContainText("SOURCE: REAL")
    await expect(page.locator(".trace-id").first()).toContainText("REQ_ID: req-list-1")
    await expect(page.locator(".trace-id").nth(1)).toContainText("PROCESS: 125.00 ms")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(2)
  })

  test("filters strategy list by keyword and status", async ({ page }) => {
    const listPayload: StrategyRecord[] = [
      {
        strategy_id: 21,
        strategy_name: "Gamma Momentum",
        strategy_type: "momentum",
        description: "gamma",
        status: "active",
        updated_at: "2026-03-01T11:00:00Z",
      },
      {
        strategy_id: 22,
        strategy_name: "Delta Mean",
        strategy_type: "mean_reversion",
        description: "delta",
        status: "paused",
        updated_at: "2026-03-01T11:05:00Z",
      },
      {
        strategy_id: 23,
        strategy_name: "Omega Breakout",
        strategy_type: "breakout",
        description: "omega",
        status: "archived",
        updated_at: "2026-03-01T11:10:00Z",
      },
    ]

    await routeStrategyList(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-filter-1",
          "x-process-time": "45ms",
        },
        body: JSON.stringify(buildUnifiedResponse(listPayload, { request_id: "req-filter-1" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(3)

    await page.getByPlaceholder("搜索策略名称 / 类型").fill("Gamma")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".strategy-table tbody tr").first()).toContainText("Gamma Momentum")

    await page.getByPlaceholder("搜索策略名称 / 类型").fill("")
    await page.locator(".toolbar-select").selectOption("paused")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".strategy-table tbody tr").first()).toContainText("Delta Mean")
  })

  test("supports lifecycle actions start/pause/resume/stop", async ({ page }) => {
    let currentStatus = "archived"
    const strategyId = "31"
    const strategyName = "Lifecycle Strategy"

    await routeStrategyList(page, async (route) => {
      const listPayload: StrategyRecord[] = [
        {
          strategy_id: Number(strategyId),
          strategy_name: strategyName,
          strategy_type: "momentum",
          description: "lifecycle case",
          status: currentStatus,
          updated_at: "2026-03-01T12:00:00Z",
        },
      ]

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-life-list",
          "x-process-time": "30ms",
        },
        body: JSON.stringify(buildUnifiedResponse(listPayload, { request_id: "req-life-list" })),
      })
    })

    await routeStrategyLifecycle(page, strategyId, "start", async (route) => {
      currentStatus = "active"
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "running" }, { request_id: "req-life-start" })),
      })
    })
    await routeStrategyLifecycle(page, strategyId, "pause", async (route) => {
      currentStatus = "paused"
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "paused" }, { request_id: "req-life-pause" })),
      })
    })
    await routeStrategyLifecycle(page, strategyId, "resume", async (route) => {
      currentStatus = "active"
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "running" }, { request_id: "req-life-resume" })),
      })
    })
    await routeStrategyLifecycle(page, strategyId, "stop", async (route) => {
      currentStatus = "archived"
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "stopped" }, { request_id: "req-life-stop" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    const row = page.locator(".strategy-table tbody tr", { hasText: strategyName })
    await expect(row).toHaveCount(1)

    await row.getByRole("button", { name: "启动" }).click()
    await expect(row.locator(".status-chip")).toContainText("RUNNING")

    await row.getByRole("button", { name: "暂停" }).click()
    await expect(row.locator(".status-chip")).toContainText("PAUSED")

    await row.getByRole("button", { name: "恢复" }).click()
    await expect(row.locator(".status-chip")).toContainText("RUNNING")

    await row.getByRole("button", { name: "停止" }).click()
    await expect(row.locator(".status-chip")).toContainText("STOPPED")
  })

  test("supports create, edit and delete strategy workflow", async ({ page }) => {
    let strategiesState: StrategyRecord[] = [
      {
        strategy_id: 41,
        strategy_name: "Base Strategy",
        strategy_type: "momentum",
        description: "base row",
        status: "active",
        updated_at: "2026-03-01T13:00:00Z",
      },
    ]

    await routeStrategyList(page, async (route) => {
      const method = route.request().method()
      if (method === "GET") {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-crud-list",
            "x-process-time": "42ms",
          },
          body: JSON.stringify(buildUnifiedResponse(strategiesState, { request_id: "req-crud-list" })),
        })
        return
      }

      if (method === "POST") {
        const payload = JSON.parse(route.request().postData() || "{}") as Record<string, unknown>
        const created: StrategyRecord = {
          strategy_id: 99,
          strategy_name: String(payload.name || "Created Strategy"),
          strategy_type: String(payload.type || "momentum"),
          description: String(payload.description || ""),
          status: "archived",
          updated_at: "2026-03-01T13:10:00Z",
        }
        strategiesState = [created, ...strategiesState]

        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(buildUnifiedResponse(created, { request_id: "req-crud-create" })),
        })
        return
      }

      await route.fallback()
    })

    await routeStrategyDetail(page, "*", async (route) => {
      const method = route.request().method()
      const id = Number(route.request().url().split("/").pop()?.split("?")[0] || 0)

      if (method === "PUT") {
        const payload = JSON.parse(route.request().postData() || "{}") as Record<string, unknown>
        strategiesState = strategiesState.map((item) =>
          item.strategy_id === id
            ? {
                ...item,
                strategy_name: String(payload.name || item.strategy_name),
                description: String(payload.description || item.description),
                updated_at: "2026-03-01T13:20:00Z",
              }
            : item
        )
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(buildUnifiedResponse({ id }, { request_id: "req-crud-update" })),
        })
        return
      }

      if (method === "DELETE") {
        strategiesState = strategiesState.filter((item) => item.strategy_id !== id)
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify(buildUnifiedResponse(null, { request_id: "req-crud-delete" })),
        })
        return
      }

      await route.fallback()
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(1)

    await page.getByRole("button", { name: "新建策略" }).click()
    await expect(page.locator(".editor-panel")).toBeVisible()

    await page.getByPlaceholder("请输入策略名称").fill("Gamma Strategy")
    await page.getByPlaceholder("请输入策略描述").fill("created by e2e")
    await page.getByRole("button", { name: "添加参数" }).click()
    await page.getByPlaceholder("参数名").fill("lookback")
    await page.getByPlaceholder("参数值").fill("21")
    await page.getByRole("button", { name: "创建" }).click()

    let createdRow = page.locator(".strategy-table tbody tr", { hasText: "Gamma Strategy" })
    await expect(createdRow).toHaveCount(1)

    await createdRow.getByRole("button", { name: "编辑" }).click()
    await expect(page.locator(".editor-panel")).toBeVisible()
    await page.getByPlaceholder("请输入策略名称").fill("Gamma Strategy V2")
    await page.getByRole("button", { name: "保存" }).click()

    createdRow = page.locator(".strategy-table tbody tr", { hasText: "Gamma Strategy V2" })
    await expect(createdRow).toHaveCount(1)

    page.once("dialog", (dialog) => dialog.accept())
    await createdRow.getByRole("button", { name: "删除" }).click()
    await expect(page.locator(".strategy-table tbody tr", { hasText: "Gamma Strategy V2" })).toHaveCount(0)
  })
})
