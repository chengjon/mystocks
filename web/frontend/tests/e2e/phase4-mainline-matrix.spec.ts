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

type WatchlistRecord = {
  id: number
  name: string
  is_active: boolean
}

type WatchlistStockRecord = {
  stock_code: string
  name?: string
  stock_name?: string
  entry_price: number
  stop_loss_price?: number
}

type QuoteRowRecord = {
  symbol: string
  name: string
  current_price?: number
  price?: number
}

type Phase4State = {
  alertRules: AlertRuleRecord[]
  alertRecords: AlertRecord[]
  announcements: AnnouncementRecord[]
  dataSourceConfigs: DataSourceConfigRecord[]
  watchlists: WatchlistRecord[]
  watchlistStocks: WatchlistStockRecord[]
  quoteRows: QuoteRowRecord[]
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

function createPhase4State(overrides?: Partial<Pick<Phase4State, "watchlists" | "watchlistStocks" | "quoteRows">>): Phase4State {
  return {
    alertRules: ALERT_RULES.map((row) => ({ ...row })),
    alertRecords: ALERT_RECORDS.map((row) => ({ ...row })),
    announcements: ANNOUNCEMENTS.map((row) => ({ ...row })),
    dataSourceConfigs: DATA_SOURCE_CONFIGS.map((row) => ({ ...row })),
    watchlists: overrides?.watchlists?.map((row) => ({ ...row })) ?? WATCHLISTS.map((row) => ({ ...row })),
    watchlistStocks: overrides?.watchlistStocks?.map((row) => ({ ...row })) ?? WATCHLIST_STOCKS.map((row) => ({ ...row })),
    quoteRows: overrides?.quoteRows?.map((row) => ({ ...row })) ?? QUOTE_ROWS.map((row) => ({ ...row })),
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

async function restoreAuthSession(page: Page): Promise<void> {
  await page.evaluate(({ user }) => {
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

    const piniaState = (window as typeof window & {
      $vue?: {
        $pinia?: {
          state: {
            value: Record<string, unknown>
          }
          _s?: Map<string, { user?: unknown; token?: unknown; isAuthenticated?: unknown }>
        }
      }
    }).$vue?.$pinia

    if (piniaState?.state?.value) {
      piniaState.state.value.auth = {
        user,
        token,
        isAuthenticated: true,
      }
    }

    const authStoreInstance = piniaState?._s?.get("auth")
    if (authStoreInstance) {
      authStoreInstance.user = user
      authStoreInstance.token = token
      authStoreInstance.isAuthenticated = true
    }
  }, { user: E2E_USER })
}

async function setupPhase4Mock(
  page: Page,
  overrides?: Partial<Pick<Phase4State, "watchlists" | "watchlistStocks" | "quoteRows">>,
): Promise<Phase4State> {
  const state = createPhase4State(overrides)
  await page.setViewportSize({ width: 1440, height: 900 })
  await installBrowserSpies(page)
  await seedAuth(page)
  await stubPhase4Apis(page, state)
  return state
}

async function stubPhase4Apis(page: Page, state: Phase4State): Promise<void> {
  const context = page.context()

  await context.route("**/api/health/detailed", async (route) => {
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
  })

  await context.route("**/api/akshare/market/fund-flow/hsgt-summary**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(
        buildUnifiedResponse({
          northbound_net: 0,
          southbound_net: 0,
          shanghai_net: 0,
          shenzhen_net: 0,
        }, { request_id: "req-phase4-hsgt-summary" })
      ),
    })
  })

  await context.route("**/api/akshare/market/fund-flow/big-deal**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(buildUnifiedResponse([], { request_id: "req-phase4-big-deal" })),
    })
  })

  await context.route("**/api/v1/data-sources/config/", async (route) => {
    await route.fulfill({
      status: 200,
      headers: {
        "content-type": "application/json",
        "x-request-id": "req-phase4-config",
      },
      body: JSON.stringify(buildUnifiedResponse(state.dataSourceConfigs, { request_id: "req-phase4-config" })),
    })
  })

  await context.route("**/api/v1/data-sources/config/batch", async (route) => {
    const request = route.request()
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
  })

  await context.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
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

    if (normalizedPath === "/announcement/stats" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcement-stats",
        },
        body: JSON.stringify({
          success: true,
          total_count: state.announcements.length,
          today_count: state.announcements.length,
          important_count: state.announcements.filter((row) => row.importance_level >= 4).length,
          triggered_count: 0,
          by_source: {},
          by_type: {},
          by_sentiment: {},
        }),
      })
      return
    }

    if (normalizedPath === "/v1/sentiment/market" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-news-market",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              sentiment: "positive",
              average_sentiment: 0.67,
              coverage: 18,
              positive_ratio: 0.61,
              negative_ratio: 0.19,
              neutral_ratio: 0.2,
              hot_symbols: ["600519", "000001"],
              updated_at: "2026-05-07T00:00:00Z",
            },
            { request_id: "req-phase4-risk-news-market" },
          ),
        ),
      })
      return
    }

    if (normalizedPath.startsWith("/v1/sentiment/stock/") && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-news-stock",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              symbol: "600519",
              days: 7,
              mentions: 12,
              average_sentiment: 0.61,
              trend: "positive",
              latest_sentiment: "positive",
              latest_confidence: 0.88,
              timeline: [
                { date: "2026-05-06", sentiment: "positive", score: 0.58, confidence: 0.82 },
                { date: "2026-05-07", sentiment: "positive", score: 0.64, confidence: 0.88 },
              ],
            },
            { request_id: "req-phase4-risk-news-stock" },
          ),
        ),
      })
      return
    }

    if (normalizedPath === "/announcement/monitor-rules" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcement-rules",
        },
        body: JSON.stringify([]),
      })
      return
    }

    if (normalizedPath === "/announcement/triggered-records" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcement-triggered",
        },
        body: JSON.stringify({
          success: true,
          data: [],
        }),
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
        body: JSON.stringify(buildUnifiedResponse(state.watchlists, { request_id: "req-phase4-watchlists" })),
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
        body: JSON.stringify(buildUnifiedResponse(state.watchlistStocks, { request_id: "req-phase4-watchlist-stocks" })),
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
        body: JSON.stringify(buildUnifiedResponse(state.quoteRows, { request_id: "req-phase4-quotes" })),
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
  await page.goto(`${FRONTEND_BASE_URL}${path}`, { waitUntil: "domcontentloaded" })

  if (new URL(page.url()).pathname === "/login") {
    await restoreAuthSession(page)
    await page.goto(`${FRONTEND_BASE_URL}${path}`, { waitUntil: "domcontentloaded" })
  }
}

test.describe("Phase 4 Mainline Matrix", () => {
  test.use({ serviceWorkers: "block" })

  test.describe.configure({ timeout: 180000 })

  test("Risk-Management renders portfolio guard shell and actions", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/management")

    const riskContent = page.locator("#artdeco-main-content")

    await expect(page.getByText("风险管理中心").first()).toBeVisible()
    await expect(page.getByText("风险控制工作流").first()).toBeVisible()
    await expect(page.getByRole("tab", { name: "风险概览" })).toHaveAttribute("aria-selected", "true")
    await expect(page.locator(".stats-grid")).toContainText("总资产")
    await expect(page.locator(".stats-grid")).toContainText("今日收益")
    await expect(page.locator(".stats-grid")).not.toContainText("+1.84%")
    await expect(page.locator(".stats-grid")).not.toContainText("+0%")
    await expect(page.locator(".risk-footer")).not.toContainText("每5分钟自动更新")
    await expect(page.locator(".risk-footer")).toContainText("按当前页同步结果更新")
    await expect(riskContent).toContainText("风险观察列表")
    await expect(riskContent).toContainText("股票名称")
    await expect(riskContent).toContainText("当前仅基于真实持仓暴露生成风险观察项，未接入止损/减仓策略参数。")
    await expect(riskContent).toContainText("策略状态")
    await expect(riskContent).toContainText("复核状态")
    await expect(riskContent).toContainText("待复核")
    await expect(riskContent).toContainText("未校验")
    await expect(riskContent).not.toContainText("风险预警列表")
    await expect(page.getByRole("button", { name: "导出" })).toBeVisible()
    await expect(page.getByRole("button", { name: "设置", exact: true })).toBeVisible()
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Management keeps footer freshness unresolved when the first positions payload fails before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/trade/positions", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-management-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "positions unavailable",
            request_id: "req-phase4-risk-management-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/management")

    await expect(page.getByText("风险管理中心").first()).toBeVisible()
    await expect(page.locator(".error-boundary")).toContainText("数据请求失败，请稍后重试")
    await expect(page.locator(".risk-footer")).toContainText("最后一次更新：--")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Management stock tab degrades unsupported single-name analysis into pending integration copy", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/management")
    await page.getByRole("tab", { name: "个股分析" }).click()

    const riskContent = page.locator("#artdeco-main-content")

    await expect(page.getByRole("tab", { name: "个股分析" })).toHaveAttribute("aria-selected", "true")
    await expect(riskContent).toContainText("个股风险分析入口")
    await expect(riskContent).toContainText("当前仅保留个股风险分析入口，个股级仓位、止损与波动联动待接入。")
    await expect(riskContent).toContainText("当前路由仍复用组合级风险数据，不直接生成单标的风控动作。")
    await expect(page.getByRole("button", { name: "查看接入说明" })).toBeVisible()
    await expect(riskContent).not.toContainText("下钻单一标的的仓位、止损与波动特征，形成可执行的个股风控动作。")
    await expect(riskContent).not.toContainText("选择持仓股票查看详细风险分析")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Overview renders rule table and alert tab under mock data", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/overview")

    await expect(page.getByText("风险概览工作台").first()).toBeVisible()
    await expect(page.locator(".content-shell")).toContainText("未校验")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("1.00")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await page.getByRole("button", { name: "规则清单" }).click()
    await expect(page.locator(".content-shell")).toContainText("单票止损线")
    await expect(page.locator(".content-shell")).not.toContainText("1.00")
    await expect(page.locator(".content-shell")).not.toContainText("2.00")
    await page.getByRole("button", { name: "预警消息" }).click()
    await expect(page.locator(".alerts-list")).toContainText("已跌破止损线，请立即处理。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Overview keeps unavailable provenance honest when the first rules and alerts payloads fail before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/monitoring/alert-rules", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-overview-rules-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk rules unavailable",
            request_id: "req-phase4-risk-overview-rules-first-fail",
          }),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/alerts?page=1&page_size=50", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-overview-alerts-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alerts unavailable",
            request_id: "req-phase4-risk-overview-alerts-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/overview")

    await expect(page.getByText("风险概览工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("ALERTS: --")
    await expect(page.locator(".stats-strip")).toContainText("--")
    await expect(page.locator(".content-shell")).toContainText("获取预警记录失败，当前暂无已验证风险概览快照。")
    await expect(page.locator(".content-shell")).toContainText("当前暂无已验证风险概览快照。")
    await expect(page.locator(".content-shell")).not.toContainText("req-phase4-risk-overview-rules-first-fail")
    await expect(page.locator(".content-shell")).not.toContainText("req-phase4-risk-overview-alerts-first-fail")
    await expect(page.locator(".content-shell")).not.toContainText("今日告警0")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Overview exposes the verified rules slice when alerts are still unavailable on the first load", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/monitoring/alert-rules", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-overview-rules-first-success",
        },
        body: JSON.stringify(
          buildUnifiedResponse(ALERT_RULES, {
            request_id: "req-phase4-risk-overview-rules-first-success",
          }),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/alerts?page=1&page_size=50", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-overview-alerts-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alerts unavailable",
            request_id: "req-phase4-risk-overview-alerts-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/overview")

    await expect(page.getByText("风险概览工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("ALERTS: --")
    await expect(page.locator(".stats-strip")).toContainText("2")
    await expect(page.locator(".stats-strip")).toContainText("--")
    await expect(page.locator(".stats-strip")).toContainText("未校验")

    await page.getByRole("button", { name: "规则清单" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-overview-rules-first-success")
    await expect(page.locator(".content-shell-meta")).toContainText("RULES: 2")
    await expect(page.locator(".content-shell")).toContainText("单票止损线")
    await expect(page.locator(".content-shell")).toContainText("获取预警记录失败，当前预警消息暂不可用。")
    await expect(page.locator(".content-shell")).toContainText("当前预警消息暂不可用。")
    await expect(page.locator(".content-shell")).not.toContainText("当前暂无已验证风险概览快照。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Overview keeps the last verified request id and visible rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let rulesFetchCount = 0
    let alertsFetchCount = 0

    await page.context().route("**/api/v1/monitoring/alert-rules", async (route) => {
      rulesFetchCount += 1

      if (rulesFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-risk-overview-rules-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(ALERT_RULES, {
              request_id: "req-phase4-risk-overview-rules-success",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-overview-rules-refresh-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk rules refresh unavailable",
            request_id: "req-phase4-risk-overview-rules-refresh-fail",
          }),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/alerts?page=1&page_size=50", async (route) => {
      alertsFetchCount += 1

      if (alertsFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-risk-overview-alerts-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(ALERT_RECORDS, {
              request_id: "req-phase4-risk-overview-alerts-success",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-overview-alerts-refresh-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alerts refresh unavailable",
            request_id: "req-phase4-risk-overview-alerts-refresh-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/overview")

    await expect(page.getByText("风险概览工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-overview-alerts-success")
    await expect(page.locator(".stats-strip")).toContainText("2")
    await expect(page.locator(".stats-strip")).toContainText("2")
    await expect(page.locator(".stats-strip")).toContainText("未校验")

    await page.getByRole("button", { name: "刷新概览" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-overview-alerts-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-risk-overview-rules-refresh-fail")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-risk-overview-alerts-refresh-fail")
    await expect(page.locator(".content-shell")).toContainText("获取预警记录失败，当前仍显示上次成功同步的风险概览快照。")
    await expect(page.locator(".content-shell")).toContainText("当前仍显示上次成功同步的风险概览快照。")
    await expect(page.locator(".stats-strip")).toContainText("2")
    await page.getByRole("button", { name: "规则清单" }).click()
    await expect(page.locator(".content-shell")).toContainText("单票止损线")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-PnL renders portfolio metrics and top positions", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/pnl")

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".portfolio-overview-tab")).toContainText("Top Positions")
    await expect(page.locator(".portfolio-overview-tab")).toContainText("贵州茅台")
    await expect(page.locator(".rebalance-section")).toContainText("再平衡策略待接入")
    await expect(page.locator(".rebalance-section")).not.toContainText("目标 25%")
    await expect(page.locator(".rebalance-section")).not.toContainText("建议减仓约")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss renders triggered and critical stop-loss cards", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".risk-card")).toHaveCount(2)
    await expect(page.locator(".monitor-grid")).toContainText("TRIGGERED")
    await expect(page.locator(".monitor-grid")).toContainText("宁德时代")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("1.00")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss degrades to pending-policy copy when watchlist stocks have no stop-loss thresholds", async ({ page }) => {
    const state = await setupPhase4Mock(page, {
      watchlistStocks: [
        {
          stock_code: "600519",
          stock_name: "贵州茅台",
          entry_price: 1820,
        },
      ],
      quoteRows: [
        {
          symbol: "600519",
          name: "贵州茅台",
          current_price: 1805,
        },
      ],
    })

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("策略待接入")
    await expect(page.locator(".content-shell")).toContainText("当前仅同步观察标的与行情，止损参数待接入。")
    await expect(page.locator(".monitor-grid")).toContainText("待接入")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("1.00")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".stop-loss-monitor-tab")).not.toContainText("止损观察中")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss keeps unavailable provenance honest when the first watchlist-stock payload fails before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/monitoring/watchlists/101/stocks", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-stoploss-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "watchlist stocks unavailable",
            request_id: "req-phase4-stoploss-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("CRITICAL: --")
    await expect(page.locator(".hero-meta")).toContainText("TRIGGERED: --")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).toContainText("--")
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("watchlist stocks unavailable")
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("当前暂无已验证止损快照。")
    await expect(page.locator(".stop-loss-monitor-tab")).not.toContainText("req-phase4-stoploss-first-fail")
    await expect(page.locator(".stop-loss-monitor-tab")).not.toContainText("暂无止损监控卡片")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss keeps the last verified request id and cards when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let stopLossStockFetchCount = 0

    await page.context().route("**/api/v1/monitoring/watchlists/101/stocks", async (route) => {
      stopLossStockFetchCount += 1

      if (stopLossStockFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-stoploss-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(state.watchlistStocks, {
              request_id: "req-phase4-stoploss-success",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-stoploss-refresh-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "watchlist stocks refresh unavailable",
            request_id: "req-phase4-stoploss-refresh-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-stoploss-success")
    await expect(page.locator(".risk-card")).toHaveCount(2)
    await expect(page.locator(".monitor-grid")).toContainText("宁德时代")

    await page.getByRole("button", { name: "刷新雷达" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-stoploss-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-stoploss-refresh-fail")
    await expect(page.locator(".risk-card")).toHaveCount(2)
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("watchlist stocks refresh unavailable")
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("当前仍显示上次成功同步的止损快照。")
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss does not keep the previous watchlist cards visible while a new primary watchlist is still unresolved", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let watchlistRequestCount = 0

    await page.context().route("**/api/v1/monitoring/watchlists", async (route) => {
      watchlistRequestCount += 1

      if (watchlistRequestCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-watchlists-101",
          },
          body: JSON.stringify(
            buildUnifiedResponse([{ id: 101, name: "核心止损监控", is_active: true }], {
              request_id: "req-phase4-watchlists-101",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-watchlists-202",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              { id: 202, name: "成长止损监控", is_active: true },
              { id: 101, name: "核心止损监控", is_active: false },
            ],
            { request_id: "req-phase4-watchlists-202" },
          ),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/watchlists/202/stocks", async () => {
      await new Promise(() => {})
    })

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-watchlist-stocks")
    await expect(page.locator(".risk-card")).toHaveCount(2)
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("贵州茅台")

    await page.getByRole("button", { name: "刷新雷达" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("CRITICAL: --")
    await expect(page.locator(".hero-meta")).toContainText("TRIGGERED: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("止损标的同步中...")
    await expect(page.locator(".risk-card")).toHaveCount(0)
    await expect(page.locator(".stop-loss-monitor-tab")).not.toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss does not leak a previous watchlist snapshot after the primary watchlist switched to a new selector without its own verified cards", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let watchlistRequestCount = 0

    await page.context().route("**/api/v1/monitoring/watchlists", async (route) => {
      watchlistRequestCount += 1

      if (watchlistRequestCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-watchlists-101",
          },
          body: JSON.stringify(
            buildUnifiedResponse([{ id: 101, name: "核心止损监控", is_active: true }], {
              request_id: "req-phase4-watchlists-101",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-watchlists-202",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              { id: 202, name: "成长止损监控", is_active: true },
              { id: 101, name: "核心止损监控", is_active: false },
            ],
            { request_id: "req-phase4-watchlists-202" },
          ),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/watchlists/202/stocks", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-stoploss-202-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "watchlist 202 stocks unavailable",
            request_id: "req-phase4-stoploss-202-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/stop-loss")

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-watchlist-stocks")
    await expect(page.locator(".risk-card")).toHaveCount(2)
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("贵州茅台")

    await page.getByRole("button", { name: "刷新雷达" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("CRITICAL: --")
    await expect(page.locator(".hero-meta")).toContainText("TRIGGERED: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".risk-card")).toHaveCount(0)
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("watchlist 202 stocks unavailable")
    await expect(page.locator(".stop-loss-monitor-tab")).toContainText("当前暂无已验证止损快照。")
    await expect(page.locator(".stop-loss-monitor-tab")).not.toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Alerts renders mocked alerts and rules tables", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/alerts")

    await expect(page.getByText("风险告警工作台").first()).toBeVisible()
    await expect(page.getByTestId("risk-alerts-page")).toBeVisible()
    await expect(page.getByTestId("risk-alerts-header")).toBeVisible()
    await expect(page.getByTestId("risk-alerts-header")).toHaveClass(/artdeco-route-header/)
    await expect(page.getByTestId("risk-alerts-refresh")).toBeVisible()
    await expect(page.getByTestId("risk-alerts-review-lens")).toBeVisible()
    await expect(page.getByTestId("risk-alerts-status-strip")).toContainText("存在未读告警")
    await expect(page.getByTestId("risk-alerts-table")).toBeVisible()
    await expect(page.getByTestId("risk-alerts-rules-secondary")).toBeVisible()
    await expect(page.locator(".risk-alerts")).toContainText("近期告警")
    await expect(page.locator(".risk-alerts")).toContainText("已跌破止损线，请立即处理。")
    await expect(page.locator(".risk-alerts")).toContainText("规则列表")
    await expect(page.locator(".risk-alerts")).toContainText("组合波动率约束")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("2.00")
    await expect(page.locator(".stats-strip")).not.toContainText("1.00")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Alerts keeps unavailable provenance honest when the first rules and alerts payloads fail before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/monitoring/alert-rules", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-alerts-rules-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alert rules unavailable",
            request_id: "req-phase4-risk-alerts-rules-first-fail",
          }),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/alerts?page=1&page_size=50", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-alerts-records-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alert records unavailable",
            request_id: "req-phase4-risk-alerts-records-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/alerts")

    await expect(page.getByText("风险告警工作台").first()).toBeVisible()
    await expect(page.getByTestId("risk-alerts-status-strip")).toContainText("获取告警记录失败")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("UNREAD: --")
    await expect(page.locator(".content-shell-meta")).toContainText("RULES: --")
    await expect(page.locator(".content-shell-meta")).toContainText("ALERTS: --")
    await expect(page.locator(".stats-strip")).toContainText("--")
    await expect(page.locator(".risk-alerts")).toContainText("获取告警记录失败")
    await expect(page.locator(".risk-alerts")).toContainText("当前暂无已验证告警快照。")
    await expect(page.locator(".risk-alerts")).not.toContainText("req-phase4-risk-alerts-rules-first-fail")
    await expect(page.locator(".risk-alerts")).not.toContainText("req-phase4-risk-alerts-records-first-fail")
    await expect(page.locator(".risk-alerts")).not.toContainText("暂无告警记录，近期告警面板为空。")
    await expect(page.locator(".risk-alerts")).not.toContainText("暂无风险告警规则。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Alerts keeps verified rules visible when alert records fail on the first load before any full snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/monitoring/alert-rules", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-alerts-rules-first-success",
        },
        body: JSON.stringify(
          buildUnifiedResponse(ALERT_RULES, {
            request_id: "req-phase4-risk-alerts-rules-first-success",
          }),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/alerts?page=1&page_size=50", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-alerts-records-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alerts unavailable",
            request_id: "req-phase4-risk-alerts-records-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/alerts")

    await expect(page.getByText("风险告警工作台").first()).toBeVisible()
    await expect(page.getByTestId("risk-alerts-status-strip")).toContainText("获取告警记录失败")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("UNREAD: --")
    await expect(page.locator(".content-shell-meta")).toContainText("RULES: 2")
    await expect(page.locator(".content-shell-meta")).toContainText("ALERTS: --")
    await expect(page.locator(".stats-strip")).toContainText("2")
    await expect(page.locator(".stats-strip")).toContainText("--")
    await expect(page.locator(".risk-alerts")).toContainText("获取告警记录失败")
    await expect(page.locator(".risk-alerts")).toContainText("当前告警记录暂不可用。")
    await expect(page.locator(".risk-alerts")).toContainText("组合波动率约束")
    await expect(page.locator(".risk-alerts")).not.toContainText("req-phase4-risk-alerts-rules-first-success")
    await expect(page.locator(".risk-alerts")).not.toContainText("req-phase4-risk-alerts-records-first-fail")
    await expect(page.locator(".risk-alerts")).not.toContainText("已跌破止损线，请立即处理。")
    await expect(page.locator(".risk-alerts")).not.toContainText("当前暂无已验证告警快照。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Alerts keeps the last verified request id and visible rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let rulesFetchCount = 0
    let alertsFetchCount = 0

    await page.context().route("**/api/v1/monitoring/alert-rules", async (route) => {
      rulesFetchCount += 1

      if (rulesFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-risk-alerts-rules-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(ALERT_RULES, {
              request_id: "req-phase4-risk-alerts-rules-success",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-alerts-rules-refresh-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alert rules refresh unavailable",
            request_id: "req-phase4-risk-alerts-rules-refresh-fail",
          }),
        ),
      })
    })

    await page.context().route("**/api/v1/monitoring/alerts?page=1&page_size=50", async (route) => {
      alertsFetchCount += 1

      if (alertsFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-risk-alerts-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(ALERT_RECORDS, {
              request_id: "req-phase4-risk-alerts-success",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-alerts-refresh-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "risk alert records refresh unavailable",
            request_id: "req-phase4-risk-alerts-refresh-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/alerts")

    await expect(page.getByText("风险告警工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-alerts-success")
    await expect(page.locator(".hero-meta")).toContainText("UNREAD: 1")
    await expect(page.locator(".content-shell-meta")).toContainText("RULES: 2")
    await expect(page.locator(".content-shell-meta")).toContainText("ALERTS: 2")
    await expect(page.locator(".stats-strip")).toContainText("2")
    await expect(page.locator(".stats-strip")).toContainText("1")
    await expect(page.locator(".risk-alerts")).toContainText("组合波动率约束")
    await expect(page.locator(".risk-alerts")).toContainText("已跌破止损线，请立即处理。")

    await page.getByRole("button", { name: "刷新告警" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-alerts-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-risk-alerts-rules-refresh-fail")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-risk-alerts-refresh-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("RULES: 2")
    await expect(page.locator(".content-shell-meta")).toContainText("ALERTS: 2")
    await expect(page.locator(".risk-alerts")).toContainText("获取告警记录失败")
    await expect(page.locator(".risk-alerts")).toContainText("当前仍显示上次成功同步的告警快照。")
    await expect(page.locator(".risk-alerts")).toContainText("组合波动率约束")
    await expect(page.locator(".risk-alerts")).toContainText("已跌破止损线，请立即处理。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-News renders announcements and opens source links", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/risk/news")

    await expect(page.getByText("舆情预警").first()).toBeVisible()
    await expect(page.locator(".announcement-monitor")).toContainText("公告列表")
    await expect(page.locator(".announcement-monitor")).toContainText("2026 年第一季度经营数据公告")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("2.00")
    await expect(page.locator(".stats-strip")).not.toContainText("1.00")
    await page.getByRole("button", { name: "查看原文" }).first().click()
    const openedUrls = await page.evaluate(() => (window as typeof window & { __phase4OpenedUrls: string[] }).__phase4OpenedUrls)
    expect(openedUrls).toEqual(["https://example.com/announcements/600519-q1"])
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-News keeps unavailable provenance honest when the first announcements payload fails before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/announcement/list**", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-news-first-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "announcement feed unavailable",
            request_id: "req-phase4-risk-news-first-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/news")

    await expect(page.getByText("舆情预警").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("TODAY: --")
    await expect(page.locator(".content-shell-meta")).toContainText("ANNOUNCEMENTS: --")
    await expect(page.locator(".content-shell-meta")).toContainText("LINKED: --")
    await expect(page.locator(".stats-strip")).toContainText("--")
    await expect(page.locator(".announcement-monitor")).toContainText("公告与舆情流同步失败")
    await expect(page.locator(".announcement-monitor")).toContainText("当前暂无已验证工作台快照。")
    await expect(page.locator(".announcement-monitor")).not.toContainText("req-phase4-risk-news-first-fail")
    await expect(page.locator(".announcement-monitor")).not.toContainText("暂无公告数据，公告列表为空。")
    await expect(page.locator(".announcement-monitor")).not.toContainText("当前没有可展示的公告记录。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-News keeps the last verified request id and visible rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let announcementsFetchCount = 0

    await page.context().route("**/api/announcement/list**", async (route) => {
      announcementsFetchCount += 1

      if (announcementsFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-risk-news-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(ANNOUNCEMENTS, {
              request_id: "req-phase4-risk-news-success",
            }),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-risk-news-refresh-fail",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "announcement refresh unavailable",
            request_id: "req-phase4-risk-news-refresh-fail",
          }),
        ),
      })
    })

    await gotoRoute(page, "/risk/news")

    await expect(page.getByText("舆情预警").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-news-stock")
    await expect(page.locator(".content-shell-meta")).toContainText("ANNOUNCEMENTS: 2")
    await expect(page.locator(".content-shell-meta")).toContainText("LINKED: 1")
    await expect(page.locator(".announcement-monitor")).toContainText("2026 年第一季度经营数据公告")

    await page.getByRole("button", { name: "刷新公告" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-risk-news-stock")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-risk-news-refresh-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("ANNOUNCEMENTS: 2")
    await expect(page.locator(".content-shell-meta")).toContainText("LINKED: 1")
    await expect(page.locator(".announcement-monitor")).toContainText("公告与舆情流同步失败")
    await expect(page.locator(".announcement-monitor")).toContainText("当前仍显示上次成功同步的工作台快照。")
    await expect(page.locator(".announcement-monitor")).toContainText("2026 年第一季度经营数据公告")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News renders live announcement stats instead of zero fallback or label-only stat cards", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.getByText("ANNOUNCEMENT MONITOR").first()).toBeVisible()
    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 600519")
    await expect(page.locator(".announcements-card")).toContainText("2026 年第一季度经营数据公告")
    await expect(page.locator(".stats-grid .stat-number")).toHaveCount(4)
    await expect(page.locator(".stats-grid .stat-number").nth(0)).toHaveText("2")
    await expect(page.locator(".stats-grid .stat-number").nth(1)).toHaveText("2")
    await expect(page.locator(".stats-grid .stat-number").nth(2)).toHaveText("1")
    await expect(page.locator(".stats-grid .stat-number").nth(3)).toHaveText("0")
    await expect(page.locator(".stats-grid")).not.toContainText("--")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News clears stale stats cards when the announcement stats slice refresh fails but keeps the verified announcement rows", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let statsFetchCount = 0

    await page.context().route("**/api/announcement/stats", async (route) => {
      statsFetchCount += 1

      if (statsFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-announcement-stats-success",
          },
          body: JSON.stringify({
            success: true,
            total_count: 2,
            today_count: 2,
            important_count: 1,
            triggered_count: 0,
            by_source: {},
            by_type: {},
            by_sentiment: {},
          }),
        })
        return
      }

      await route.fulfill({
        status: 503,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcement-stats-fail",
        },
        body: JSON.stringify({
          success: false,
          message: "announcement stats unavailable",
        }),
      })
    })

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.locator(".announcements-card")).toContainText("2026 年第一季度经营数据公告")
    await expect(page.locator(".stats-grid .stat-number").nth(0)).toHaveText("2")
    await expect(page.locator(".stats-grid .stat-number").nth(1)).toHaveText("2")
    await expect(page.locator(".stats-grid .stat-number").nth(2)).toHaveText("1")
    await expect(page.locator(".stats-grid .stat-number").nth(3)).toHaveText("0")

    await page.locator(".search-card").getByRole("button", { name: "刷新" }).click()

    await expect(page.locator(".announcements-card")).toContainText("2026 年第一季度经营数据公告")
    await expect(page.locator(".stats-grid .stat-number").nth(0)).toHaveText("--")
    await expect(page.locator(".stats-grid .stat-number").nth(1)).toHaveText("--")
    await expect(page.locator(".stats-grid .stat-number").nth(2)).toHaveText("--")
    await expect(page.locator(".stats-grid .stat-number").nth(3)).toHaveText("--")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News keeps the last verified auxiliary rule and trigger snapshots when those slices fail on a later refresh", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let rulesFetchCount = 0
    let triggeredFetchCount = 0

    await page.context().route("**/api/announcement/monitor-rules", async (route) => {
      rulesFetchCount += 1

      if (rulesFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-announcement-rules-success",
          },
          body: JSON.stringify([
            {
              id: 11,
              rule_name: "高重要性公告",
              stock_codes: ["600519"],
              keywords: ["经营数据"],
              min_importance_level: 4,
              notify_enabled: true,
              is_active: true,
            },
          ]),
        })
        return
      }

      await route.fulfill({
        status: 503,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcement-rules-fail",
        },
        body: JSON.stringify({
          success: false,
          error: "monitor rules unavailable",
        }),
      })
    })

    await page.context().route("**/api/announcement/triggered-records", async (route) => {
      triggeredFetchCount += 1

      if (triggeredFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-announcement-triggered-success",
          },
          body: JSON.stringify({
            success: true,
            data: [
              {
                rule_name: "高重要性公告",
                stock_code: "600519",
                announcement_title: "2026 年第一季度经营数据公告",
                matched_keywords: ["经营数据"],
                triggered_at: "2026-05-05 10:00:00",
              },
            ],
          }),
        })
        return
      }

      await route.fulfill({
        status: 503,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-announcement-triggered-fail",
        },
        body: JSON.stringify({
          success: false,
          error: "triggered records unavailable",
        }),
      })
    })

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.locator(".rules-card")).toContainText("高重要性公告")
    await expect(page.locator(".records-card")).toContainText("2026 年第一季度经营数据公告")

    await page.locator(".search-card").getByRole("button", { name: "刷新" }).click()

    await expect(page.locator(".rules-card")).toContainText("当前仍显示上次成功同步的监控规则快照。")
    await expect(page.locator(".rules-card")).toContainText("高重要性公告")
    await expect(page.locator(".records-card")).toContainText("当前仍显示上次成功同步的触发记录快照。")
    await expect(page.locator(".records-card")).toContainText("2026 年第一季度经营数据公告")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News clears the previous symbol rows when a new detail symbol failed before its first verified announcement snapshot", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/announcement/list**", async (route) => {
      const url = new URL(route.request().url())
      const stockCode = url.searchParams.get("stock_code") || ""

      if (stockCode === "000001") {
        await route.fulfill({
          status: 503,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-detail-news-symbol-fail",
          },
          body: JSON.stringify({
            success: false,
            error: "announcement list unavailable for 000001",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-detail-news-symbol-success",
        },
        body: JSON.stringify({
          success: true,
          data: [
            {
              id: 1,
              stock_code: "600519",
              stock_name: "贵州茅台",
              title: "2026 年第一季度经营数据公告",
              type: "经营数据",
              importance_level: 4,
              sentiment: "neutral",
              publish_date: "2026-05-05",
              data_source: "cninfo",
              url: "https://example.com/600519-q1",
            },
          ],
          total: 1,
        }),
      })
    })

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 600519")
    await expect(page.locator(".announcements-card")).toContainText("2026 年第一季度经营数据公告")

    await gotoRoute(page, "/detail/news/000001")

    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 000001")
    await expect(page.locator(".announcements-card")).toContainText("当前标的公告暂不可用，请稍后重试。")
    await expect(page.locator(".announcements-card")).not.toContainText("2026 年第一季度经营数据公告")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News clears the previous symbol rows while a newly selected detail symbol is still unresolved", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/announcement/list**", async (route) => {
      const url = new URL(route.request().url())
      const stockCode = url.searchParams.get("stock_code") || ""

      if (stockCode === "000001") {
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-detail-news-symbol-pending-success",
        },
        body: JSON.stringify({
          success: true,
          data: [
            {
              id: 1,
              stock_code: "600519",
              stock_name: "贵州茅台",
              title: "2026 年第一季度经营数据公告",
              type: "经营数据",
              importance_level: 4,
              sentiment: "neutral",
              publish_date: "2026-05-05",
              data_source: "cninfo",
              url: "https://example.com/600519-q1",
            },
          ],
          total: 1,
        }),
      })
    })

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 600519")
    await expect(page.locator(".announcements-card")).toContainText("2026 年第一季度经营数据公告")

    await gotoRoute(page, "/detail/news/000001")

    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 000001")
    await expect(page.locator(".announcements-card")).not.toContainText("2026 年第一季度经营数据公告")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News clears the previous stats cards while a newly selected detail symbol stats slice is still unresolved", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let statsFetchCount = 0

    await page.context().route("**/api/announcement/stats", async (route) => {
      statsFetchCount += 1

      if (statsFetchCount === 2) {
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": `req-phase4-detail-news-stats-${statsFetchCount}`,
        },
        body: JSON.stringify({
          success: true,
          total_count: 2,
          today_count: 2,
          important_count: 1,
          triggered_count: 0,
        }),
      })
    })

    await page.context().route("**/api/announcement/list**", async (route) => {
      const url = new URL(route.request().url())
      const stockCode = url.searchParams.get("stock_code") || ""

      if (stockCode === "000001") {
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-detail-news-stats-symbol-pending-success",
        },
        body: JSON.stringify({
          success: true,
          data: [
            {
              id: 1,
              stock_code: "600519",
              stock_name: "贵州茅台",
              title: "2026 年第一季度经营数据公告",
              type: "经营数据",
              importance_level: 4,
              sentiment: "neutral",
              publish_date: "2026-05-05",
              data_source: "cninfo",
              url: "https://example.com/600519-q1",
            },
          ],
          total: 1,
        }),
      })
    })

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.locator(".stats-grid .stat-number").nth(0)).toHaveText("2")
    await expect(page.locator(".stats-grid .stat-number").nth(1)).toHaveText("2")
    await expect(page.locator(".stats-grid .stat-number").nth(2)).toHaveText("1")
    await expect(page.locator(".stats-grid .stat-number").nth(3)).toHaveText("0")

    await gotoRoute(page, "/detail/news/000001")

    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 000001")
    await expect(page.locator(".stats-grid .stat-number").nth(0)).toHaveText("--")
    await expect(page.locator(".stats-grid .stat-number").nth(1)).toHaveText("--")
    await expect(page.locator(".stats-grid .stat-number").nth(2)).toHaveText("--")
    await expect(page.locator(".stats-grid .stat-number").nth(3)).toHaveText("--")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Detail-News does not leak selector-specific auxiliary rows into a new detail symbol shell", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/announcement/list**", async (route) => {
      const url = new URL(route.request().url())
      const stockCode = url.searchParams.get("stock_code") || ""

      if (stockCode === "000001") {
        await route.fulfill({
          status: 503,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-detail-news-aux-symbol-fail",
          },
          body: JSON.stringify({
            success: false,
            error: "announcement list unavailable for 000001",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-detail-news-aux-symbol-success",
        },
        body: JSON.stringify({
          success: true,
          data: [
            {
              id: 1,
              stock_code: "600519",
              stock_name: "贵州茅台",
              title: "2026 年第一季度经营数据公告",
              type: "经营数据",
              importance_level: 4,
              sentiment: "neutral",
              publish_date: "2026-05-05",
              data_source: "cninfo",
              url: "https://example.com/600519-q1",
            },
          ],
          total: 1,
        }),
      })
    })

    await page.context().route("**/api/announcement/monitor-rules", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-detail-news-aux-rules",
        },
        body: JSON.stringify([
          {
            id: 11,
            rule_name: "高重要性公告",
            stock_codes: ["600519"],
            keywords: ["经营数据"],
            min_importance_level: 4,
            notify_enabled: true,
            is_active: true,
          },
          {
            id: 12,
            rule_name: "全市场风险提示",
            stock_codes: [],
            keywords: ["风险提示"],
            min_importance_level: 3,
            notify_enabled: true,
            is_active: true,
          },
        ]),
      })
    })

    await page.context().route("**/api/announcement/triggered-records", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-detail-news-aux-records",
        },
        body: JSON.stringify({
          success: true,
          data: [
            {
              rule_name: "高重要性公告",
              stock_code: "600519",
              announcement_title: "2026 年第一季度经营数据公告",
              matched_keywords: ["经营数据"],
              triggered_at: "2026-05-05 10:00:00",
            },
          ],
        }),
      })
    })

    await gotoRoute(page, "/detail/news/600519")

    await expect(page.locator(".rules-card")).toContainText("高重要性公告")
    await expect(page.locator(".records-card")).toContainText("2026 年第一季度经营数据公告")

    await gotoRoute(page, "/detail/news/000001")

    await expect(page.locator(".route-banner")).toContainText("当前详情标的: 000001")
    await expect(page.locator(".rules-card")).toContainText("全市场风险提示")
    await expect(page.locator(".rules-card")).not.toContainText("高重要性公告")
    await expect(page.locator(".records-card")).not.toContainText("高重要性公告")
    await expect(page.locator(".records-card")).not.toContainText("2026 年第一季度经营数据公告")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Config keeps blocker copy and saves local settings", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/config")

    await expect(page.getByText("系统配置中心").first()).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("System-Config 仍按分段真相运行")
    await expect(page.locator(".analysis-blocker")).toContainText("general 与 security 已接入系统级 /api/v1/system/settings/* 契约")
    await expect(page.locator(".header-meta")).toContainText("DATA: REAL")
    await expect(page.locator(".header-meta")).toContainText("REQ_ID: req-phase4-config")
    await expect(page.locator(".stats-grid .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-grid")).toContainText("3")
    await expect(page.locator(".stats-grid")).toContainText("2")
    await expect(page.locator(".stats-grid")).toContainText("ON")
    await expect(page.locator(".stats-grid")).not.toContainText("+0%")
    await expect(page.locator(".stats-grid")).not.toContainText("4.00")
    await expect(page.locator(".stats-grid")).not.toContainText("3/4")
    await expect(page.locator(".stats-grid")).not.toContainText("28,412")
    await expect(page.locator(".stats-grid")).not.toContainText("2.00")
    await expect(page.locator(".hybrid-table__content")).toContainText("AKShare 行情")
    await expect(page.locator(".hybrid-table__content")).toContainText("Tushare 因子")
    await expect(page.locator(".hybrid-table__content")).toContainText("TDX 实时深度")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("Wind")
    await page.locator(".tabs").getByRole("button", { name: "系统监控", exact: true }).click()
    await expect(page.locator(".header-meta")).toContainText("REQ_ID: req-phase4-health-detailed")
    await page.locator(".tabs").getByRole("button", { name: "系统设置", exact: true }).click()
    await expect(page.locator(".header-meta")).toContainText("REQ_ID: req-phase4-general-settings")
    await page.locator(".form-grid input").first().fill("http://localhost:9999")
    await page.getByRole("button", { name: "保存系统设置", exact: true }).click()
    await expect.poll(() => state.lastGeneralSettingsPayload).toEqual({
      backend_url: "http://localhost:9999",
      max_backtest_jobs: 4,
      default_slippage_percent: 0.05,
      fee_rate_bps: 2.5,
    })
    expect(state.detailedHealthFetchCount).toBeGreaterThanOrEqual(1)
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Health renders health matrix and middleware panel", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/health")

    await expect(page.getByText("系统健康矩阵").first()).toBeVisible()
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await expect(page.locator(".health-grid")).toContainText("Performance Tracing")
    await expect(page.locator(".content-shell")).toContainText("服务状态与中间件面板")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("3.00")
    await expect(page.locator(".stats-strip")).not.toContainText("2.00")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Health does not leak failed request ids before any verified health snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-health-first-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 503,
          message: "health failed",
          request_id: "req-phase4-health-first-fail",
        }),
      })
    })

    await gotoRoute(page, "/system/health")

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-health-first-fail")
    await expect(page.locator(".runtime-message")).toContainText("无法连接到后端服务")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Health keeps the last verified request id when refresh fails after success", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let healthFetchCount = 0

    await page.context().route("**/api/health", async (route) => {
      healthFetchCount += 1

      if (healthFetchCount <= 2) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": healthFetchCount === 1 ? "req-phase4-health-preflight" : "req-phase4-health-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(
              HEALTH_DATA,
              {
                request_id: healthFetchCount === 1 ? "req-phase4-health-preflight" : "req-phase4-health-success",
              },
            ),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-health-refresh-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 503,
          message: "health failed",
          request_id: "req-phase4-health-refresh-fail",
        }),
      })
    })

    await gotoRoute(page, "/system/health")

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-health-success")
    await page.getByRole("button", { name: "刷新矩阵" }).click()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-health-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-health-refresh-fail")
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await expect(page.locator(".runtime-message")).toContainText("无法连接到后端服务")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-API renders observability deck and exports detailed health", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/api")

    await expect(page.getByText("系统监控工作台").first()).toBeVisible()
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("3.00")
    await expect(page.locator(".stats-strip")).not.toContainText("2.00")
    await page.getByRole("button", { name: "导出报告" }).click()
    const blobUrls = await page.evaluate(
      () => (window as typeof window & { __phase4BlobUrls: string[] }).__phase4BlobUrls
    )
    expect(state.detailedHealthFetchCount).toBeGreaterThanOrEqual(1)
    expect(blobUrls).toHaveLength(1)
    expect(blobUrls[0]).toContain("blob:phase4-export-")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-API does not leak failed request ids before any verified system probe snapshot exists", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/health", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-system-api-first-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 503,
          message: "health failed",
          request_id: "req-phase4-system-api-first-fail",
        }),
      })
    })

    await gotoRoute(page, "/system/api")

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-system-api-first-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".runtime-message")).toContainText("无法连接到后端服务")
    await expect(page.locator(".runtime-message")).toContainText("当前暂无已验证系统探针快照。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-API keeps the last verified request id and visible snapshot when refresh fails after success", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let healthFetchCount = 0

    await page.context().route("**/api/health", async (route) => {
      healthFetchCount += 1

      if (healthFetchCount <= 2) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": healthFetchCount === 1 ? "req-phase4-system-api-preflight" : "req-phase4-system-api-success",
          },
          body: JSON.stringify(
            buildUnifiedResponse(
              HEALTH_DATA,
              {
                request_id: healthFetchCount === 1 ? "req-phase4-system-api-preflight" : "req-phase4-system-api-success",
              },
            ),
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-system-api-refresh-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 503,
          message: "health failed",
          request_id: "req-phase4-system-api-refresh-fail",
        }),
      })
    })

    await gotoRoute(page, "/system/api")

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-system-api-success")
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await expect(page.locator(".health-grid")).toContainText("2.0.0")

    await page.getByRole("button", { name: "刷新探针" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-system-api-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-system-api-refresh-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("REQ_ID: req-phase4-system-api-success")
    await expect(page.locator(".runtime-message")).toContainText("无法连接到后端服务")
    await expect(page.locator(".runtime-message")).toContainText("当前仍显示上次成功同步的系统探针快照。")
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")
    await expect(page.locator(".health-grid")).toContainText("2.0.0")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Data renders config table and posts batch write payload", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await gotoRoute(page, "/system/data")

    await expect(page.getByText("数据源治理工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("3.00")
    await expect(page.locator(".stats-strip")).not.toContainText("2.00")
    await expect(page.locator(".config-row:not(.header)")).toHaveCount(3)
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

  test("System-Data does not fabricate a request id when the verified config snapshot has no request metadata", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.context().route("**/api/v1/data-sources/config/", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify(buildUnifiedResponse(state.dataSourceConfigs, { request_id: "" })),
      })
    })

    await gotoRoute(page, "/system/data")

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".stats-strip")).toContainText("当前请求")
    await expect(page.locator(".stats-strip")).toContainText("N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("cfg-")
    await expect(page.locator(".stats-strip")).not.toContainText("cfg-")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Data keeps the last verified request id and visible rows when refresh fails after success", async ({ page }) => {
    const state = await setupPhase4Mock(page)
    let dataSourceFetchCount = 0

    await page.context().route("**/api/v1/data-sources/config/", async (route) => {
      dataSourceFetchCount += 1

      if (dataSourceFetchCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase4-system-data-success",
          },
          body: JSON.stringify(buildUnifiedResponse(state.dataSourceConfigs, { request_id: "req-phase4-system-data-success" })),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase4-system-data-refresh-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 503,
          message: "config refresh failed",
          request_id: "req-phase4-system-data-refresh-fail",
        }),
      })
    })

    await gotoRoute(page, "/system/data")

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-system-data-success")
    await expect(page.locator(".config-table")).toContainText("AKShare 行情")

    await page.getByRole("button", { name: "刷新配置" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase4-system-data-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase4-system-data-refresh-fail")
    await expect(page.locator(".runtime-message")).toContainText("获取数据源配置失败")
    await expect(page.locator(".runtime-message")).toContainText("当前仍显示上次成功同步的数据源配置快照。")
    await expect(page.locator(".config-table")).toContainText("AKShare 行情")
    await expect(page.locator(".config-table")).toContainText("TDX 实时深度")
    expect(state.unhandledRequests).toEqual([])
  })
})
