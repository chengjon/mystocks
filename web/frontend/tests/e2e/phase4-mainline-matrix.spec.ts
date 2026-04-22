// This suite depends on Playwright route stubs. Start the frontend with
// VITE_USE_MOCK_DATA=false so requests are not short-circuited by mockApiClient.
import { expect, test, type Page } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

const E2E_USER = {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  permissions: ["*"],
}

type AlertRuleRecord = {
  rule_name: string
  rule_type: string
  symbol: string
  is_active: boolean
  priority: number
  updated_at: string
}

type AlertRecord = {
  symbol: string
  stock_name: string
  alert_type: string
  alert_level: string
  alert_message: string
  alert_time: string
  is_read: boolean
}

type AnnouncementRecord = {
  stock_code: string
  stock_name: string
  announcement_type: string
  announcement_title: string
  importance_level: number
  publish_date: string
  publish_time: string
  url?: string
}

type DataSourceConfigRecord = {
  endpoint_name: string
  name: string
  endpoint: string
  status: "active" | "maintenance"
}

type Phase4State = {
  alertRules: AlertRuleRecord[]
  alertRecords: AlertRecord[]
  announcements: AnnouncementRecord[]
  dataSourceConfigs: DataSourceConfigRecord[]
  lastBatchPayload: Record<string, unknown> | null
  lastGeneralSettingsPayload: Record<string, unknown> | null
  detailedHealthFetchCount: number
  unhandledRequests: string[]
}

const POSITIONS_PAYLOAD = {
  positions: [
    {
      symbol: "600519",
      symbol_name: "贵州茅台",
      market_value: 202584,
      profit_loss_percent: -0.69,
    },
    {
      symbol: "300750",
      symbol_name: "宁德时代",
      market_value: 170080,
      profit_loss_percent: 1.24,
    },
  ],
  total_market_value: 372664,
  total_profit_loss: 6844,
  total_profit_loss_percent: 1.84,
}

const ALERT_RULES: AlertRuleRecord[] = [
  {
    rule_name: "单票止损线",
    rule_type: "stop_loss",
    symbol: "600519",
    is_active: true,
    priority: 1,
    updated_at: "2026-04-05T08:30:00Z",
  },
  {
    rule_name: "组合波动率约束",
    rule_type: "portfolio_volatility",
    symbol: "GLOBAL",
    is_active: true,
    priority: 2,
    updated_at: "2026-04-05T08:35:00Z",
  },
]

const ALERT_RECORDS: AlertRecord[] = [
  {
    symbol: "600519",
    stock_name: "贵州茅台",
    alert_type: "stop_loss",
    alert_level: "critical",
    alert_message: "已跌破止损线，请立即处理。",
    alert_time: "2026-04-05T09:30:00Z",
    is_read: false,
  },
  {
    symbol: "300750",
    stock_name: "宁德时代",
    alert_type: "position_limit",
    alert_level: "warning",
    alert_message: "仓位接近上限，建议控制风险敞口。",
    alert_time: "2026-04-05T09:10:00Z",
    is_read: true,
  },
]

const ANNOUNCEMENTS: AnnouncementRecord[] = [
  {
    stock_code: "600519",
    stock_name: "贵州茅台",
    announcement_type: "年度报告",
    announcement_title: "2026 年第一季度经营数据公告",
    importance_level: 5,
    publish_date: "2026-04-05",
    publish_time: "09:05:00",
    url: "https://example.com/announcements/600519-q1",
  },
  {
    stock_code: "300750",
    stock_name: "宁德时代",
    announcement_type: "董事会决议",
    announcement_title: "关于回购方案进展的公告",
    importance_level: 3,
    publish_date: "2026-04-05",
    publish_time: "08:42:00",
  },
]

const DATA_SOURCE_CONFIGS: DataSourceConfigRecord[] = [
  {
    endpoint_name: "akshare.market.quotes",
    name: "AKShare 行情",
    endpoint: "/api/v1/market/quotes",
    status: "active",
  },
  {
    endpoint_name: "tushare.factor.daily",
    name: "Tushare 因子",
    endpoint: "/api/v1/factors/daily",
    status: "active",
  },
  {
    endpoint_name: "tdx.realtime.depth",
    name: "TDX 实时深度",
    endpoint: "/api/v1/market/depth",
    status: "maintenance",
  },
]

const WATCHLISTS = [
  { id: 101, name: "核心风控池", is_active: true },
  { id: 102, name: "备选观察池", is_active: false },
]

const WATCHLIST_STOCKS = [
  {
    stock_code: "600519",
    name: "贵州茅台",
    entry_price: 1692.5,
    stop_loss_price: 1700,
  },
  {
    stock_code: "300750",
    name: "宁德时代",
    entry_price: 208.4,
    stop_loss_price: 210,
  },
]

const QUOTE_ROWS = [
  { symbol: "600519", name: "贵州茅台", current_price: 1688.2 },
  { symbol: "300750", name: "宁德时代", current_price: 212.6 },
]

const HEALTH_DATA = {
  status: "healthy",
  service: "mystocks-backend",
  version: "2.0.0",
}

const DETAILED_HEALTH_DATA = {
  status: "healthy",
  service: "mystocks-backend",
  version: "2.0.0",
  apis: [
    { endpoint: "/api/v1/market/quotes", qps: 53, p95: 128, errorRate: "0.18%" },
    { endpoint: "/api/v1/auth/login", qps: 7, p95: 164, errorRate: "0.02%" },
    { endpoint: "/api/v1/data-sources/config/batch", qps: 2, p95: 231, errorRate: "0.00%" },
  ],
}

function normalizePathname(url: string): string {
  let pathname = new URL(url).pathname
  while (pathname.startsWith("/api/")) {
    pathname = pathname.slice(4)
  }
  return pathname
}

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: "ok",
    data,
    timestamp: "2026-04-05T00:00:00Z",
    request_id: "req-phase4-default",
    ...(overrides ?? {}),
  }
}

function createPhase4State(): Phase4State {
  return {
    alertRules: ALERT_RULES.map((row) => ({ ...row })),
    alertRecords: ALERT_RECORDS.map((row) => ({ ...row })),
    announcements: ANNOUNCEMENTS.map((row) => ({ ...row })),
    dataSourceConfigs: DATA_SOURCE_CONFIGS.map((row) => ({ ...row })),
    lastBatchPayload: null,
    lastGeneralSettingsPayload: null,
    detailedHealthFetchCount: 0,
    unhandledRequests: [],
  }
}

async function installBrowserSpies(page: Page): Promise<void> {
  await page.addInitScript(() => {
    const openedUrls: string[] = []
    const downloads: Array<{ href: string; download: string }> = []
    const blobUrls: string[] = []

    ;(window as typeof window & {
      __phase4OpenedUrls: string[]
      __phase4Downloads: Array<{ href: string; download: string }>
      __phase4BlobUrls: string[]
    }).__phase4OpenedUrls = openedUrls
    ;(window as typeof window & {
      __phase4OpenedUrls: string[]
      __phase4Downloads: Array<{ href: string; download: string }>
      __phase4BlobUrls: string[]
    }).__phase4Downloads = downloads
    ;(window as typeof window & {
      __phase4OpenedUrls: string[]
      __phase4Downloads: Array<{ href: string; download: string }>
      __phase4BlobUrls: string[]
    }).__phase4BlobUrls = blobUrls

    window.open = ((url?: string | URL | undefined) => {
      if (url) {
        openedUrls.push(String(url))
      }
      return null
    }) as typeof window.open

    URL.createObjectURL = (() => {
      const nextUrl = `blob:phase4-export-${blobUrls.length + 1}`
      blobUrls.push(nextUrl)
      return nextUrl
    }) as typeof URL.createObjectURL
    URL.revokeObjectURL = (() => {}) as typeof URL.revokeObjectURL

    HTMLAnchorElement.prototype.click = function click() {
      downloads.push({
        href: this.href,
        download: this.download,
      })
    }
  })
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript(({ user }) => {
    const token = "e2e-phase4-token"
    const authStore = {
      user,
      token,
      isAuthenticated: true,
      permissions: user.permissions,
    }
    localStorage.setItem("auth_token", token)
    localStorage.setItem("auth_user", JSON.stringify(user))
    localStorage.setItem("token", token)
    localStorage.setItem("user", JSON.stringify(user))
    localStorage.setItem("access_token", token)
    localStorage.setItem("auth-store", JSON.stringify(authStore))
  }, { user: E2E_USER })
}

async function setupPhase4Mock(page: Page): Promise<Phase4State> {
  const state = createPhase4State()
  await page.setViewportSize({ width: 1440, height: 900 })
  await installBrowserSpies(page)
  await seedAuth(page)
  await stubPhase4Apis(page, state)
  return state
}

async function stubPhase4Apis(page: Page, state: Phase4State): Promise<void> {
  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
    const request = route.request()
    const normalizedPath = normalizePathname(request.url())
    const method = request.method()

    if (normalizedPath === "/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "ready" }, { request_id: "req-phase4-ready" })),
      })
      return
    }

    if (normalizedPath === "/health" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-health",
          "x-process-time": "18ms",
        },
        body: JSON.stringify(buildUnifiedResponse(HEALTH_DATA, { request_id: "req-phase4-health" })),
      })
      return
    }

    if (normalizedPath === "/health/detailed" && method === "GET") {
      state.detailedHealthFetchCount += 1
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-health-detailed",
          "x-process-time": "27ms",
        },
        body: JSON.stringify(buildUnifiedResponse(DETAILED_HEALTH_DATA, { request_id: "req-phase4-health-detailed" })),
      })
      return
    }

    if ((normalizedPath === "/v1/auth/me" || normalizedPath === "/auth/me") && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-auth-me",
          "x-process-time": "12ms",
        },
        body: JSON.stringify(buildUnifiedResponse(E2E_USER, { request_id: "req-phase4-auth-me" })),
      })
      return
    }

    if (normalizedPath === "/v1/system/settings/general" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-general-settings",
          "x-process-time": "23ms",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              backend_url: "http://localhost:8020",
              max_backtest_jobs: 4,
              default_slippage_percent: 0.05,
              fee_rate_bps: 2.5,
            },
            { request_id: "req-phase4-general-settings" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/system/settings/general" && method === "POST") {
      const payload = JSON.parse(request.postData() || "{}") as Record<string, unknown>
      state.lastGeneralSettingsPayload = payload

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-general-settings-save",
          "x-process-time": "26ms",
        },
        body: JSON.stringify(
          buildUnifiedResponse(payload, { request_id: "req-phase4-general-settings-save" })
        ),
      })
      return
    }

    if (normalizedPath === "/csrf-token" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ csrf_token: "e2e-phase4-csrf" }, { request_id: "req-phase4-csrf" })),
      })
      return
    }

    if (normalizedPath === "/v1/trade/positions" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-positions",
          "x-process-time": "29ms",
        },
        body: JSON.stringify(buildUnifiedResponse(POSITIONS_PAYLOAD, { request_id: "req-phase4-positions" })),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/alert-rules" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-rules",
        },
        body: JSON.stringify(buildUnifiedResponse(state.alertRules, { request_id: "req-phase4-rules" })),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/alerts" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-alerts",
        },
        body: JSON.stringify(buildUnifiedResponse(state.alertRecords, { request_id: "req-phase4-alerts" })),
      })
      return
    }

    if (normalizedPath === "/announcement/list" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcements",
        },
        body: JSON.stringify(buildUnifiedResponse(state.announcements, { request_id: "req-phase4-announcements" })),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/watchlists" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-watchlists",
        },
        body: JSON.stringify(buildUnifiedResponse(WATCHLISTS, { request_id: "req-phase4-watchlists" })),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/watchlists/101/stocks" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-watchlist-stocks",
        },
        body: JSON.stringify(buildUnifiedResponse(WATCHLIST_STOCKS, { request_id: "req-phase4-watchlist-stocks" })),
      })
      return
    }

    if (normalizedPath === "/v1/market/quotes" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-quotes",
        },
        body: JSON.stringify(buildUnifiedResponse(QUOTE_ROWS, { request_id: "req-phase4-quotes" })),
      })
      return
    }

    if (normalizedPath === "/v1/data-sources/config/" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-config",
        },
        body: JSON.stringify(buildUnifiedResponse(state.dataSourceConfigs, { request_id: "req-phase4-config" })),
      })
      return
    }

    if (normalizedPath === "/v1/data-sources/config/batch" && method === "POST") {
      const payload = JSON.parse(request.postData() || "{}") as {
        operations?: Array<{ endpoint_name?: string; updates?: { status?: "active" | "maintenance" } }>
      }
      state.lastBatchPayload = payload as Record<string, unknown>

      for (const operation of payload.operations || []) {
        const item = state.dataSourceConfigs.find((entry) => entry.endpoint_name === operation.endpoint_name)
        if (item && operation.updates?.status) {
          item.status = operation.updates.status
        }
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-config-batch",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              operations_applied: (payload.operations || []).length,
            },
            { request_id: "req-phase4-config-batch" }
          )
        ),
      })
      return
    }

    state.unhandledRequests.push(`${method} ${normalizedPath}`)
    await route.fulfill({
      status: 404,
      contentType: "application/json",
      body: JSON.stringify({
        success: false,
        code: 404,
        message: `Unhandled phase4 mock route: ${method} ${normalizedPath}`,
      }),
    })
  })
}

async function gotoRoute(page: Page, path: string): Promise<void> {
  await page.goto(`${FRONTEND_BASE_URL}${path}`)
  await page.waitForLoadState("networkidle").catch(() => {})
}

test.describe("Phase 4 Mainline Matrix", () => {
  test.describe.configure({ timeout: 180000 })

  test("Risk-Management renders portfolio guard shell and actions", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/management")

    await expect(page.getByText("风险管理中心").first()).toBeVisible()
    await expect(page.getByText("风险控制工作流").first()).toBeVisible()
    await expect(page.locator(".risk-table tbody tr")).toHaveCount(2)
    await expect(page.locator(".risk-table")).toContainText("贵州茅台")
    await expect(page.getByRole("button", { name: "导出" })).toBeVisible()
    await expect(page.getByRole("main").getByRole("button", { name: "设置", exact: true })).toBeVisible()
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Overview renders rule table and alert tab under mock data", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/overview")

    await expect(page.getByText("风险概览工作台").first()).toBeVisible()
    await page.getByRole("button", { name: "规则清单" }).click()
    await expect(page.locator(".content-shell")).toContainText("单票止损线")
    await page.getByRole("button", { name: "预警消息" }).click()
    await expect(page.locator(".alerts-list")).toContainText("组合波动率超过阈值 18%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-PnL renders portfolio metrics and top positions", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/pnl")

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".portfolio-overview-tab")).toContainText("Top Positions")
    await expect(page.locator(".portfolio-overview-tab")).toContainText("贵州茅台")
    await expect(page.locator(".rebalance-section")).toContainText("自动再平衡建议")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss renders triggered and critical stop-loss cards", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".risk-card")).toHaveCount(2)
    await expect(page.locator(".monitor-grid")).toContainText("TRIGGERED")
    await expect(page.locator(".monitor-grid")).toContainText("宁德时代")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Alerts renders mocked alerts and rules tables", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/alerts")

    await expect(page.getByText("风险告警工作台").first()).toBeVisible()
    await expect(page.locator(".risk-alerts")).toContainText("近期告警")
    await expect(page.locator(".risk-alerts")).toContainText("已跌破止损线，请立即处理。")
    await expect(page.locator(".risk-alerts")).toContainText("规则列表")
    await expect(page.locator(".risk-alerts")).toContainText("组合波动率约束")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-News renders announcements and opens source links", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/news")

    await expect(page.getByText("公告与舆情工作台").first()).toBeVisible()
    await expect(page.locator(".announcement-monitor")).toContainText("公告列表")
    await expect(page.locator(".announcement-monitor")).toContainText("2026 年第一季度经营数据公告")
    await page.getByRole("button", { name: "查看原文" }).first().click()
    const openedUrls = await page.evaluate(() => (window as typeof window & { __phase4OpenedUrls: string[] }).__phase4OpenedUrls)
    expect(openedUrls).toEqual(["https://example.com/announcements/600519-q1"])
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Config keeps blocker copy and saves local settings", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/config")

    await expect(page.getByText("系统配置中心").first()).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("System-Config 仍按分段真相运行")
    await expect(page.locator(".analysis-blocker")).toContainText("general 与 security 已接入系统级 /api/v1/system/settings/* 契约")
    await expect(page.locator(".header-meta")).toContainText("DATA: REAL")
    await page.locator(".tabs").getByRole("button", { name: "系统设置", exact: true }).click()
    await page.locator(".form-grid input").first().fill("http://localhost:9999")
    await page.getByRole("button", { name: "保存系统设置", exact: true }).click()
    await expect.poll(() => state.lastGeneralSettingsPayload).toEqual({
      backend_url: "http://localhost:9999",
      max_backtest_jobs: 4,
      default_slippage_percent: 0.05,
      fee_rate_bps: 2.5,
    })
    expect(state.detailedHealthFetchCount).toBe(1)
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Health renders health matrix and middleware panel", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/health")

    await expect(page.getByText("系统健康矩阵").first()).toBeVisible()
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await expect(page.locator(".health-grid")).toContainText("Performance Tracing")
    await expect(page.locator(".content-shell")).toContainText("服务状态与中间件面板")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-API renders observability deck and exports detailed health", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/api")

    await expect(page.getByText("系统监控工作台").first()).toBeVisible()
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await page.getByRole("button", { name: "导出报告" }).click()
    const blobUrls = await page.evaluate(
      () => (window as typeof window & { __phase4BlobUrls: string[] }).__phase4BlobUrls
    )
    expect(state.detailedHealthFetchCount).toBe(1)
    expect(blobUrls).toHaveLength(1)
    expect(blobUrls[0]).toContain("blob:phase4-export-")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Data renders config table and posts batch write payload", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/data")

    await expect(page.getByText("数据源治理工作台").first()).toBeVisible()
    await expect(page.locator(".config-row")).toHaveCount(4)
    await expect(page.locator(".config-table")).toContainText("AKShare 行情")
    const firstConfigRow = page.locator(".config-row").filter({ hasText: "AKShare 行情" })
    await firstConfigRow.getByRole("button", { name: "禁用", exact: true }).click()
    await expect(firstConfigRow.locator(".col.status")).toContainText("禁用")
    await expect(firstConfigRow.getByRole("button", { name: "启用", exact: true })).toBeVisible()
    await page.getByRole("button", { name: "保存配置" }).click()
    await expect.poll(() => state.lastBatchPayload).toEqual({
      operations: [
        {
          action: "update",
          endpoint_name: "akshare.market.quotes",
          updates: {
            status: "maintenance",
          },
        },
      ],
    })
    await expect(page.locator(".config-table")).toContainText("TDX 实时深度")
    expect(state.unhandledRequests).toEqual([])
  })
})
