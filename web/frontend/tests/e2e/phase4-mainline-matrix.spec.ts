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
  permissions: [],
}

type AlertRuleRecord = {
  id: string
  rule_name: string
  rule_type: string
  symbol: string
  is_active: boolean
  priority: string
  updated_at: string
}

type AlertRecord = {
  id: string
  symbol: string
  stock_name: string
  alert_type: string
  alert_level: string
  alert_message: string
  alert_time: string
  created_at: string
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
  url: string
}

type DataSourceConfigRecord = {
  endpoint_name: string
  name: string
  status: "active" | "maintenance"
  endpoint: string
}

type Phase4State = {
  positionsPayload: Record<string, unknown>
  watchlists: Array<Record<string, unknown>>
  watchlistStocks: Map<string, Array<Record<string, unknown>>>
  alertRules: AlertRuleRecord[]
  alertRecords: AlertRecord[]
  announcements: AnnouncementRecord[]
  dataSourceConfigs: DataSourceConfigRecord[]
  configBatchCalls: number
  detailedHealthCalls: number
  savedConfigPayloads: Array<Record<string, unknown>>
  unhandledRequests: string[]
}

const POSITIONS_PAYLOAD = {
  positions: [
    {
      symbol: "600519",
      symbol_name: "贵州茅台",
      market_value: 420000,
      profit_loss_percent: 2.61,
    },
    {
      symbol: "300750",
      symbol_name: "宁德时代",
      market_value: 180000,
      profit_loss_percent: -4.12,
    },
    {
      symbol: "002594",
      symbol_name: "比亚迪",
      market_value: 95000,
      profit_loss_percent: 1.38,
    },
  ],
  total_market_value: 695000,
  total_profit_loss: 12840,
  total_profit_loss_percent: 1.88,
}

const ALERT_RULES: AlertRuleRecord[] = [
  {
    id: "rule-1",
    rule_name: "组合波动率阈值",
    rule_type: "volatility",
    symbol: "Global",
    is_active: true,
    priority: "P1",
    updated_at: "2026-04-03T09:20:00Z",
  },
  {
    id: "rule-2",
    rule_name: "单票仓位上限",
    rule_type: "position_limit",
    symbol: "600519",
    is_active: true,
    priority: "P0",
    updated_at: "2026-04-03T09:22:00Z",
  },
]

const ALERT_RECORDS: AlertRecord[] = [
  {
    id: "alert-1",
    symbol: "600519",
    stock_name: "贵州茅台",
    alert_type: "position_limit",
    alert_level: "critical",
    alert_message: "单票仓位已超过 50% 风险阈值",
    alert_time: "2026-04-03T09:35:00Z",
    created_at: "2026-04-03T09:35:00Z",
    is_read: false,
  },
  {
    id: "alert-2",
    symbol: "300750",
    stock_name: "宁德时代",
    alert_type: "drawdown",
    alert_level: "warning",
    alert_message: "回撤接近止损阈值",
    alert_time: "2026-04-03T10:05:00Z",
    created_at: "2026-04-03T10:05:00Z",
    is_read: true,
  },
]

const ANNOUNCEMENTS: AnnouncementRecord[] = [
  {
    stock_code: "600519",
    stock_name: "贵州茅台",
    announcement_type: "业绩快报",
    announcement_title: "2026Q1 业绩快报发布",
    importance_level: 5,
    publish_date: "2026-04-03",
    publish_time: "08:30:00",
    url: "https://example.com/announcements/600519-q1",
  },
  {
    stock_code: "300750",
    stock_name: "宁德时代",
    announcement_type: "投资者关系",
    announcement_title: "回购计划说明会纪要",
    importance_level: 3,
    publish_date: "2026-04-03",
    publish_time: "09:15:00",
    url: "https://example.com/announcements/300750-ir",
  },
]

const DETAILED_HEALTH_PAYLOAD = {
  metrics: [
    { endpoint: "/api/v1/market/quotes", qps: 53, p95: 128, error_rate: 0.18 },
    { endpoint: "/api/v1/auth/login", qps: 7, p95: 164, error_rate: 0.02 },
    { endpoint: "/api/v1/strategy/backtest", qps: 3, p95: 342, error_rate: 0.64 },
  ],
  output: "API端点正常: /api/v1/market/quotes\nAPI端点正常: /api/v1/auth/login",
  status: "healthy",
  service: "mystocks-backend",
  version: "2.0.0",
}

const HEALTH_PAYLOAD = {
  status: "healthy",
  service: "mystocks-backend",
  version: "2.0.0",
}

const DATA_SOURCE_CONFIGS: DataSourceConfigRecord[] = [
  {
    endpoint_name: "akshare.market",
    name: "AKShare",
    status: "active",
    endpoint: "https://akshare.example/api",
  },
  {
    endpoint_name: "tushare.market",
    name: "Tushare",
    status: "active",
    endpoint: "https://tushare.example/api",
  },
  {
    endpoint_name: "tdx.realtime",
    name: "TDX",
    status: "maintenance",
    endpoint: "tcp://tdx.example:7709",
  },
]

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
    timestamp: "2026-04-03T00:00:00Z",
    request_id: "req-phase4-default",
    ...(overrides ?? {}),
  }
}

function createPhase4State(): Phase4State {
  return {
    positionsPayload: JSON.parse(JSON.stringify(POSITIONS_PAYLOAD)) as Record<string, unknown>,
    watchlists: [
      { id: 1, name: "核心止损监控", is_active: true },
      { id: 2, name: "备选观察池", is_active: false },
    ],
    watchlistStocks: new Map<string, Array<Record<string, unknown>>>([
      [
        "1",
        [
          { stock_code: "600519", name: "贵州茅台", entry_price: 1680, stop_loss_price: 1700 },
          { stock_code: "300750", name: "宁德时代", entry_price: 208, stop_loss_price: 208 },
        ],
      ],
      [
        "2",
        [{ stock_code: "002594", name: "比亚迪", entry_price: 255, stop_loss_price: 248 }],
      ],
    ]),
    alertRules: ALERT_RULES.map((row) => ({ ...row })),
    alertRecords: ALERT_RECORDS.map((row) => ({ ...row })),
    announcements: ANNOUNCEMENTS.map((row) => ({ ...row })),
    dataSourceConfigs: DATA_SOURCE_CONFIGS.map((row) => ({ ...row })),
    configBatchCalls: 0,
    detailedHealthCalls: 0,
    savedConfigPayloads: [],
    unhandledRequests: [],
  }
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript(({ user }) => {
    const token = "e2e-phase4-token"
    localStorage.setItem("auth_token", token)
    localStorage.setItem("auth_user", JSON.stringify(user))
    localStorage.setItem("token", token)
    localStorage.setItem("user", JSON.stringify(user))
    localStorage.setItem("access_token", token)
  }, { user: E2E_USER })
}

async function setupPhase4Mock(page: Page): Promise<Phase4State> {
  const state = createPhase4State()
  await page.setViewportSize({ width: 1440, height: 900 })
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
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(HEALTH_PAYLOAD, { request_id: "req-phase4-health" })),
      })
      return
    }

    if (normalizedPath === "/health/detailed" && method === "GET") {
      state.detailedHealthCalls += 1
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(DETAILED_HEALTH_PAYLOAD, { request_id: "req-phase4-health-detailed" })),
      })
      return
    }

    if (normalizedPath === "/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              csrf_token: "e2e-phase4-csrf",
              token_type: "bearer",
              expires_in: 3600,
            },
            { request_id: "req-phase4-csrf" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/trade/positions" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(state.positionsPayload, { request_id: "req-phase4-positions" })),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/watchlists" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(state.watchlists, { request_id: "req-phase4-watchlists" })),
      })
      return
    }

    const watchlistStocksMatch = normalizedPath.match(/^\/v1\/monitoring\/watchlists\/([^/]+)\/stocks$/)
    if (watchlistStocksMatch && method === "GET") {
      const watchlistId = watchlistStocksMatch[1]
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(state.watchlistStocks.get(watchlistId) || [], { request_id: "req-phase4-watchlist-stocks" })
        ),
      })
      return
    }

    if (normalizedPath === "/v1/market/quotes" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              { symbol: "600519", name: "贵州茅台", current_price: 1688.2 },
              { symbol: "300750", name: "宁德时代", current_price: 209.0 },
              { symbol: "002594", name: "比亚迪", current_price: 258.3 },
            ],
            { request_id: "req-phase4-quotes" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/alert-rules" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(state.alertRules, { request_id: "req-phase4-alert-rules" })),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/alerts" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(state.alertRecords, { request_id: "req-phase4-alerts" })),
      })
      return
    }

    if (normalizedPath === "/announcement/list" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse(state.announcements, { request_id: "req-phase4-announcements" })),
      })
      return
    }

    if ((normalizedPath === "/v1/data-sources/config/" || normalizedPath === "/v1/data-sources/config") && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              endpoints: state.dataSourceConfigs.map((row) => ({ ...row })),
            },
            { request_id: "req-phase4-data-config" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/data-sources/config/batch" && method === "POST") {
      state.configBatchCalls += 1
      const payload = JSON.parse(request.postData() || "{}") as {
        operations?: Array<{
          endpoint_name?: string
          updates?: { status?: "active" | "maintenance" }
        }>
      }
      state.savedConfigPayloads.push(payload as Record<string, unknown>)

      for (const operation of payload.operations || []) {
        const endpointName = operation.endpoint_name
        const nextStatus = operation.updates?.status
        if (!endpointName || !nextStatus) {
          continue
        }
        const target = state.dataSourceConfigs.find((item) => item.endpoint_name === endpointName)
        if (target) {
          target.status = nextStatus
        }
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              operations: (payload.operations || []).map((operation) => ({
                endpoint_name: operation.endpoint_name,
                status: operation.updates?.status || "active",
              })),
            },
            { request_id: "req-phase4-data-config-save" }
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

test.describe("Phase 4 Mainline Matrix", () => {
  test.describe.configure({ timeout: 180000 })

  test("Risk-Management renders workflow shell and derived risk alerts", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/risk/management`)

    await expect(page.getByText("风险控制工作流").first()).toBeVisible()
    await expect(page.getByRole("button", { name: "导出" })).toBeVisible()
    await expect(page.getByRole("button", { name: "设置", exact: true })).toBeVisible()
    await expect(page.locator(".stats-grid")).toContainText("总资产")
    await expect(page.locator(".risk-table")).toContainText("贵州茅台")
    await expect(page.locator(".risk-table")).toContainText("宁德时代")
    await expect(page.locator(".custom-tabs-trace")).toContainText("REQ_ID:")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Overview renders rules and alerts tabs from mocked rule payload", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/risk/overview`)

    await expect(page.getByText("风险概览工作台").first()).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新概览" })).toBeVisible()
    await page.getByRole("button", { name: "规则清单" }).click()
    await expect(page.locator(".tab-panel")).toContainText("组合波动率阈值")
    await page.getByRole("button", { name: "预警消息" }).click()
    await expect(page.locator(".alerts-list")).toContainText("组合波动率超过阈值 18%")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-PnL renders portfolio attribution and rebalance suggestions", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/risk/pnl`)

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip")).toContainText("总资产")
    await expect(page.locator(".positions-grid")).toContainText("贵州茅台")
    await expect(page.locator(".attribution-grid")).toContainText("收益贡献")
    await expect(page.locator(".rebalance-list")).toContainText("建议减仓")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-StopLoss renders triggered and critical stop-loss cards", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/risk/stop-loss`)

    await expect(page.getByText("止损雷达工作台").first()).toBeVisible()
    await expect(page.getByText("止损距离监控面板")).toBeVisible()
    await expect(page.locator(".monitor-grid")).toContainText("贵州茅台")
    await expect(page.locator(".monitor-grid")).toContainText("宁德时代")
    await expect(page.locator(".monitor-grid")).toContainText("TRIGGERED")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-Alerts renders alert records and rule list", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/risk/alerts`)

    await expect(page.getByText("风险告警工作台").first()).toBeVisible()
    await expect(page.getByRole("heading", { name: "近期告警" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "规则列表" })).toBeVisible()
    await expect(page.locator(".table-card").first()).toContainText("贵州茅台")
    await expect(page.locator(".table-card").nth(1)).toContainText("组合波动率阈值")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Risk-News renders announcement ledger with linked source action", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/risk/news`)

    await expect(page.getByText("公告与舆情工作台").first()).toBeVisible()
    await expect(page.getByText("公告列表")).toBeVisible()
    await expect(page.locator(".table-card")).toContainText("2026Q1 业绩快报发布")
    await expect(page.getByRole("button", { name: "查看原文" }).first()).toBeEnabled()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Config renders blocker note and persists local settings", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/system/config`)

    await expect(page.locator(".system-settings-page")).toBeVisible()
    await expect(page.locator(".analysis-blocker")).toContainText("统一系统配置后端契约仍未建立")
    await page.locator(".system-settings-page .tabs").getByRole("button", { name: "系统监控" }).click()
    await expect(page.locator(".hybrid-table")).toContainText("/api/v1/market/quotes")

    await page.locator(".system-settings-page .tabs").getByRole("button", { name: "系统设置" }).click()
    await page.locator(".field input").first().fill("http://127.0.0.1:9000")
    await page.getByRole("button", { name: "保存本地设置" }).click()

    const saved = await page.evaluate(() => window.localStorage.getItem("artdeco-system-settings"))
    expect(saved).toContain("127.0.0.1:9000")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Health renders health matrix and middleware deck", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/system/health`)

    await expect(page.getByText("系统健康矩阵").first()).toBeVisible()
    await expect(page.getByText("服务状态与中间件面板")).toBeVisible()
    await expect(page.locator(".status-card").first()).toContainText("mystocks-backend")
    await expect(page.locator(".middleware-list")).toContainText("Redis Caching")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-API renders telemetry panel and exports detailed report", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/system/api`)

    await expect(page.getByText("系统监控工作台").first()).toBeVisible()
    await expect(page.getByText("系统健康与遥测面板")).toBeVisible()
    await expect(page.locator(".health-grid")).toContainText("mystocks-backend")

    const [download] = await Promise.all([
      page.waitForEvent("download"),
      page.getByRole("button", { name: "导出报告" }).click(),
    ])
    expect(await download.suggestedFilename()).toMatch(/^system-health-.*\.json$/)
    await expect.poll(() => state.detailedHealthCalls).toBe(1)
    expect(state.unhandledRequests).toEqual([])
  })

  test("System-Data renders config table and submits batch save payload", async ({ page }) => {
    const state = await setupPhase4Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/system/data`)

    await expect(page.getByText("数据源治理工作台").first()).toBeVisible()
    await expect(page.getByText("数据源配置与写回面板")).toBeVisible()
    await expect(page.locator(".config-table")).toContainText("AKShare")

    await page.locator(".config-row").nth(1).getByRole("button", { name: "禁用" }).click()
    await expect(page.locator(".config-row").nth(1).getByRole("button", { name: "启用" })).toBeVisible()
    await page.getByRole("button", { name: "保存配置" }).click()

    await expect.poll(() => state.configBatchCalls).toBe(1)
    expect(state.savedConfigPayloads[0]).toMatchObject({
      operations: [
        {
          endpoint_name: "akshare.market",
          updates: { status: "maintenance" },
        },
      ],
    })
    await expect(page.locator(".config-row").nth(1)).toContainText("禁用")
    expect(state.unhandledRequests).toEqual([])
  })
})
