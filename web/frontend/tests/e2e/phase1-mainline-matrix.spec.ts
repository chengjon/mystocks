import { expect, test, type Page, type Route } from "@playwright/test"
const { loadPortEnv, resolveFrontendConfig } = require("./helpers/port-env.js")

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const PENDING_STUB_DELAY_MS = 15_000

async function holdPendingRoute(route: Route): Promise<void> {
  await new Promise((resolve) => setTimeout(resolve, PENDING_STUB_DELAY_MS))
  await route.abort("timedout").catch(() => {
    // The page may already be closed after the pending-state assertion.
  })
}

const E2E_USER = {
  id: 1,
  username: "admin",
  email: "admin@example.com",
  role: "admin",
  permissions: [],
}

const DASHBOARD_QUOTES = [
  { symbol: "000001.SH", latest_price: 3321.08, change_percent: 0.65, volume: 9123 },
  { symbol: "399001.SZ", latest_price: 10214.2, change_percent: 0.71, volume: 8450 },
  { symbol: "399006.SZ", latest_price: 1988.66, change_percent: -0.22, volume: 6012 },
]

const REALTIME_QUOTES_BY_SYMBOLS: Record<string, { quotes: Array<Record<string, unknown>> }> = {
  "000001,600519,000858,601318,600036": {
    quotes: [
      { symbol: "000001", name: "平安银行", current_price: 10.52, change_percent: 1.28, amount: 128000000, volume: 128000000 },
      { symbol: "600519", name: "贵州茅台", current_price: 1620.35, change_percent: -0.42, amount: 386000000, volume: 386000000 },
      { symbol: "000858", name: "五粮液", current_price: 132.48, change_percent: 0.86, amount: 214000000, volume: 214000000 },
    ],
  },
  "600036,601318,600000,601166,601288": {
    quotes: [
      { symbol: "600036", name: "招商银行", current_price: 38.62, change_percent: 0.92, amount: 176000000, volume: 176000000 },
      { symbol: "601318", name: "中国平安", current_price: 47.18, change_percent: -0.36, amount: 241000000, volume: 241000000 },
      { symbol: "600000", name: "浦发银行", current_price: 8.74, change_percent: 0.21, amount: 96000000, volume: 96000000 },
    ],
  },
  "600519,000858,600887,002304,603288": {
    quotes: [
      { symbol: "600519", name: "贵州茅台", current_price: 1620.35, change_percent: -0.42, amount: 386000000, volume: 386000000 },
      { symbol: "000858", name: "五粮液", current_price: 132.48, change_percent: 0.86, amount: 214000000, volume: 214000000 },
      { symbol: "600887", name: "伊利股份", current_price: 27.66, change_percent: 0.33, amount: 118000000, volume: 118000000 },
    ],
  },
}

const FUND_FLOW_SUMMARY = [
  { 板块: "沪股通", 资金方向: "北向", 成交净买额: 18.5, 指数涨跌幅: 0.82 },
  { 板块: "深股通", 资金方向: "北向", 成交净买额: 9.3, 指数涨跌幅: 0.45 },
]

const BIG_DEAL_ROWS = [
  { 股票简称: "贵州茅台", 成交额: 980000000, 大单性质: "买盘", 涨跌幅: 1.2 },
  { 股票简称: "宁德时代", 成交额: 420000000, 大单性质: "卖盘", 涨跌幅: -0.8 },
]

const INDUSTRY_ROWS = [
  {
    rank: 1,
    sector_name: "半导体",
    change_percent: 3.28,
    main_net_inflow: 1280000000,
    main_net_inflow_rate: 14.2,
  },
  {
    rank: 2,
    sector_name: "算力",
    change_percent: 2.16,
    main_net_inflow: 860000000,
    main_net_inflow_rate: 9.7,
  },
]

const KLINE_ROWS = Array.from({ length: 6 }).map((_, index) => ({
  datetime: `2026-04-${String(index + 1).padStart(2, "0")} 15:00:00`,
  open: 100 + index,
  high: 102 + index,
  low: 99 + index,
  close: 101 + index,
  volume: 1000000 + index * 5000,
}))

const LHB_ROWS = [
  {
    trade_date: "2026-04-03",
    symbol: "600519",
    name: "贵州茅台",
    reason: "日涨幅偏离值达7%",
    buy_amount: 820000000,
    sell_amount: 210000000,
    net_amount: 610000000,
    turnover_rate: 11.8,
    institution_buy: 1,
    institution_sell: 0,
  },
  {
    trade_date: "2026-04-02",
    symbol: "300750",
    name: "宁德时代",
    reason: "日跌幅偏离值达7%",
    buy_amount: 180000000,
    sell_amount: 460000000,
    net_amount: -280000000,
    turnover_rate: 8.4,
    institution_buy: 0,
    institution_sell: 1,
  },
  {
    trade_date: "2026-04-01",
    symbol: "300308",
    name: "中际旭创",
    reason: "3日涨幅偏离值达20%",
    buy_amount: 360000000,
    sell_amount: 120000000,
    net_amount: 240000000,
    turnover_rate: 15.6,
    institution_buy: 1,
    institution_sell: 0,
  },
]

function normalizePathname(url: string): string {
  const pathname = new URL(url).pathname
  return pathname.startsWith("/api/") ? pathname.slice(4) : pathname
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript(({ user }) => {
    localStorage.setItem("auth_token", "e2e-phase1-token")
    localStorage.setItem("auth_user", JSON.stringify(user))
  }, { user: E2E_USER })
}

type Phase1StubOptions = {
  failQuotes?: boolean
  failQuotesAfterFirstSuccess?: boolean
  hangQuoteSymbolRequests?: string[]
  failFundFlowAfterFirstSuccess?: boolean
  failCapitalFlowAfterFirstSuccess?: boolean
  hangCapitalFlowPeriods?: string[]
  emptyIndustry?: boolean
  failIndustry?: boolean
  failIndustryAfterFirstSuccess?: boolean
  hangFundFlow?: boolean
  hangIndustry?: boolean
  emptyLhb?: boolean
  failLhb?: boolean
  failLhbAfterFirstSuccess?: boolean
  failLhbDayBefore?: boolean
  hangLhb?: boolean
  hangQuotes?: boolean
  failKline?: boolean
  failKlineAfterFirstSuccess?: boolean
  hangKline?: boolean
  failHealth?: boolean
  failHealthAfterFirstSuccess?: boolean
  failIndicators?: boolean
  failIndicatorsAfterFirstSuccess?: boolean
  klineRequests?: string[]
  legacyMarketKlineRequests?: string[]
  lhbRequests?: string[]
}

async function stubPhase1Apis(page: Page, options: Phase1StubOptions = {}): Promise<void> {
  let quotesRequestCount = 0
  let fundFlowRequestCount = 0
  let capitalFlowRequestCount = 0
  let industryRequestCount = 0
  let lhbRequestCount = 0
  let klineRequestCount = 0
  let healthRequestCount = 0
  let indicatorsRequestCount = 0

  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
    const requestUrl = new URL(route.request().url())
    const normalizedPath = normalizePathname(route.request().url())

    if (normalizedPath === "/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          message: "system ready",
          request_id: "e2e-phase1-ready",
          data: { status: "ready" },
        }),
      })
      return
    }

    if (normalizedPath === "/health") {
      healthRequestCount += 1

      // App bootstrap probes /health once during version negotiation before the dashboard monitoring slice.
      if (options.failHealthAfterFirstSuccess && healthRequestCount > 2) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-health-refresh-fail",
            message: "system health unavailable",
          }),
        })
        return
      }

      if (options.failHealth) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-health-first-fail",
            message: "system health unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-health-aux",
          process_time: "77",
          data: {
            status: "healthy",
            service: "mystocks-backend",
            version: "2.0.0",
          },
        }),
      })
      return
    }

    if (normalizedPath === "/csrf-token") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { csrf_token: "e2e-phase1-csrf" },
        }),
      })
      return
    }

    if (normalizedPath === "/v1/market/quotes") {
      quotesRequestCount += 1
      const requestedSymbols = requestUrl.searchParams.get("symbols") ?? ""
      const realtimeQuotesPayload = REALTIME_QUOTES_BY_SYMBOLS[requestedSymbols]

      if (options.hangQuoteSymbolRequests?.includes(requestedSymbols)) {
        await holdPendingRoute(route)
        return
      }

      if (options.hangQuotes) {
        await holdPendingRoute(route)
        return
      }

      if (options.failQuotesAfterFirstSuccess && quotesRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-quotes-refresh-fail",
            message: "quotes refresh unavailable",
          }),
        })
        return
      }

      if (options.failQuotes) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-quotes-first-fail",
            message: "quotes unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-quotes",
          process_time: "11",
          data: realtimeQuotesPayload ?? DASHBOARD_QUOTES,
        }),
      })
      return
    }

    if (normalizedPath === "/akshare/market/fund-flow/hsgt-summary") {
      fundFlowRequestCount += 1

      if (options.hangFundFlow) {
        await holdPendingRoute(route)
        return
      }

      if (options.failFundFlowAfterFirstSuccess && fundFlowRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-fund-flow-refresh-fail",
            message: "fund flow unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-fund-flow",
          process_time: "22",
          data: FUND_FLOW_SUMMARY,
        }),
      })
      return
    }

    if (normalizedPath === "/akshare/market/fund-flow/big-deal") {
      const isRankingRequest = requestUrl.searchParams.has("period")
      const rankingPeriod = requestUrl.searchParams.get("period") ?? ""

      if (isRankingRequest) {
        capitalFlowRequestCount += 1
      }

      if (isRankingRequest && options.hangCapitalFlowPeriods?.includes(rankingPeriod)) {
        await holdPendingRoute(route)
        return
      }

      if (isRankingRequest && options.failCapitalFlowAfterFirstSuccess && capitalFlowRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-ranking-refresh-fail",
            message: "stock flow ranking unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-ranking-aux",
          process_time: "44",
          data: BIG_DEAL_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v2/market/sector/fund-flow") {
      industryRequestCount += 1

      if (options.hangIndustry) {
        await holdPendingRoute(route)
        return
      }

      if (options.failIndustryAfterFirstSuccess && industryRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-industry-refresh-fail",
            message: "industry flow unavailable",
          }),
        })
        return
      }

      if (options.failIndustry) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            message: "industry flow unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-industry",
          process_time: "33",
          process_time_ms: 33,
          data: options.emptyIndustry ? [] : INDUSTRY_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v1/market/kline") {
      klineRequestCount += 1
      options.klineRequests?.push(route.request().url())

      if (options.hangKline) {
        await holdPendingRoute(route)
        return
      }

      if (options.failKlineAfterFirstSuccess && klineRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-kline-refresh-fail",
            message: "kline refresh unavailable",
          }),
        })
        return
      }

      if (options.failKline) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-kline-first-fail",
            message: "kline feed unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-kline",
          data: {
            data: KLINE_ROWS,
          },
        }),
      })
      return
    }

    if (normalizedPath === "/market/kline") {
      options.legacyMarketKlineRequests?.push(route.request().url())
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            points: [],
          },
        }),
      })
      return
    }

    if (normalizedPath === "/v1/strategy/strategies") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-strategy-aux",
          process_time: "55",
          data: [
            { id: 1, name: "Northbound Momentum", status: "active" },
          ],
        }),
      })
      return
    }

    if (normalizedPath === "/v1/trade/positions") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-position-risk-aux",
          process_time: "66",
          data: {
            total_market_value: 1200000,
            positions: [
              { symbol: "600519", market_value: 800000, unrealized_pnl: 32000, realized_pnl: 6000 },
              { symbol: "300750", market_value: 400000, unrealized_pnl: -12000, realized_pnl: 2000 },
            ],
          },
        }),
      })
      return
    }

    if (normalizedPath === "/indicators/calculate/batch") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-indicators-aux",
          process_time: "88",
          data: {
            "000001.SH": [
              { name: "RSI", value: "61.2", trend: "rise", signal: "偏强" },
              { name: "MACD", value: "0.82", trend: "rise", signal: "金叉" },
            ],
          },
        }),
      })
      return
    }

    if (normalizedPath === "/v1/technical-indicators") {
      indicatorsRequestCount += 1

      if (options.failIndicatorsAfterFirstSuccess && indicatorsRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-indicators-refresh-fail",
            message: "indicators refresh unavailable",
          }),
        })
        return
      }

      if (options.failIndicators) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-indicators-first-fail",
            message: "indicators unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-indicators-aux",
          process_time: "88",
          data: {
            name: "RSI",
            value: "61.2",
            trend: "rise",
            signal: "偏强",
          },
        }),
      })
      return
    }

    if (normalizedPath === "/v2/market/lhb") {
      lhbRequestCount += 1
      options.lhbRequests?.push(route.request().url())
      if (options.hangLhb) {
        await holdPendingRoute(route)
        return
      }

      if (options.failLhbAfterFirstSuccess && lhbRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-lhb-refresh-fail",
            message: "lhb refresh unavailable",
          }),
        })
        return
      }

      const requestUrl = new URL(route.request().url())
      const startDate = requestUrl.searchParams.get("start_date")
      const endDate = requestUrl.searchParams.get("end_date")

      if (options.failLhbDayBefore && startDate === "2026-04-01" && endDate === "2026-04-01") {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-lhb-daybefore-fail",
            message: "lhb dayBefore unavailable",
          }),
        })
        return
      }

      if (options.failLhb) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase1-lhb-first-fail",
            message: "lhb feed unavailable",
          }),
        })
        return
      }
      const scopedRows = startDate && endDate
        ? LHB_ROWS.filter((row) => row.trade_date >= startDate && row.trade_date <= endDate)
        : LHB_ROWS

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-lhb",
          data: options.emptyLhb ? [] : scopedRows,
        }),
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        success: true,
        data: [],
      }),
    })
  })
}

test.describe("Phase 1 Mainline Matrix Gaps", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
  })

  test("dashboard renders shell and core cards under mock data", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
    await expect(page.locator(".request-meta-bar")).toContainText("REQ:")
    await expect(page.getByText("市场资金流向概览")).toBeVisible()
    await expect(page.getByText("主要市场指标")).toBeVisible()
  })

  test("dashboard keeps shell when an industry feed fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
    await expect(page.locator(".request-meta-bar")).toContainText("DATA: MIXED")
    await expect(page.locator(".request-meta-bar")).toContainText("SYNC: DEGRADED")
    await expect(page.locator(".request-meta-bar")).not.toContainText("DATA: REAL")
    await expect(page.locator(".dashboard-alerts")).toContainText("行业热度数据暂不可用")
    await expect(page.getByText("市场资金流向概览")).toBeVisible()
    await expect(page.getByText("主要市场指标")).toBeVisible()
  })

  test("dashboard keeps honest pending aggregate provenance while core slices are still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangQuotes: true, hangFundFlow: true, hangIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
    await expect(page.locator(".request-meta-bar")).toContainText("DATA: PENDING")
    await expect(page.locator(".request-meta-bar")).toContainText("SYNC: PENDING")
    await expect(page.locator(".request-meta-bar")).not.toContainText("DATA: REAL")
    await expect(page.locator(".dashboard-alerts")).toHaveCount(0)
  })

  test("dashboard keeps request meta aligned to core aggregate slices instead of later auxiliary responses", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".request-meta-bar")).toContainText("REQ: e2e-phase1-industry")
    await expect(page.locator(".request-meta-bar")).toContainText("TIME: 33ms")
    await expect(page.locator(".request-meta-bar")).not.toContainText("e2e-phase1-ranking-aux")
    await expect(page.locator(".request-meta-bar")).not.toContainText("e2e-phase1-strategy-aux")
    await expect(page.locator(".request-meta-bar")).not.toContainText("e2e-phase1-position-risk-aux")
    await expect(page.locator(".request-meta-bar")).not.toContainText("e2e-phase1-health-aux")
    await expect(page.locator(".request-meta-bar")).not.toContainText("e2e-phase1-indicators-aux")
  })

  test("dashboard keeps the last verified fund-flow slice visible when a later fund-flow refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failFundFlowAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".enhanced-fund-flow")).toContainText("沪股通净流入")
    await expect(page.locator(".enhanced-fund-flow")).toContainText("18.5亿")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".dashboard-alerts")).toContainText("资金流向数据暂不可用")
    await expect(page.locator(".enhanced-fund-flow")).toContainText("沪股通净流入")
    await expect(page.locator(".enhanced-fund-flow")).toContainText("18.5亿")
    await expect(page.locator(".enhanced-fund-flow .error-message")).toHaveCount(0)
  })

  test("dashboard keeps the last verified industry slice visible when a later industry refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustryAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".request-meta-bar")).toContainText("DATA: REAL")
    await expect(page.locator(".request-meta-bar")).toContainText("SYNC: READY")
    await expect(page.locator(".market-status-card")).toContainText("2↑/0↓")
    await expect(page.locator(".heat-map-card .chart-state-note")).toHaveCount(0)
    await expect(page.locator(".sector-radar-card .chart-state-note")).toHaveCount(0)

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".request-meta-bar")).toContainText("DATA: MIXED")
    await expect(page.locator(".request-meta-bar")).toContainText("SYNC: DEGRADED")
    await expect(page.locator(".dashboard-alerts")).toContainText("行业热度数据暂不可用")
    await expect(page.locator(".market-status-card")).toContainText("2↑/0↓")
    await expect(page.locator(".heat-map-card .chart-state-note")).toHaveCount(0)
    await expect(page.locator(".sector-radar-card .chart-state-note")).toHaveCount(0)
  })

  test("dashboard keeps the last verified capital-flow slice visible when a later ranking refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failCapitalFlowAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".capital-flow-card")).toContainText("贵州茅台")
    await expect(page.locator(".capital-flow-card")).toContainText("宁德时代")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".capital-flow-card")).toContainText("资金流向持续排名暂不可用")
    await expect(page.locator(".capital-flow-card")).toContainText("贵州茅台")
    await expect(page.locator(".capital-flow-card")).toContainText("宁德时代")
    await expect(page.locator(".capital-heatmap-card .chart-state-note")).toContainText("资金流向持续排名暂不可用")
  })

  test("dashboard does not leak the previous capital-flow rows into a different tab while that tab is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangCapitalFlowPeriods: ["3day"] })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    const capitalFlowCard = page.locator(".capital-flow-card")
    await expect(capitalFlowCard).toContainText("贵州茅台")
    await expect(capitalFlowCard).toContainText("宁德时代")

    await page.getByRole("tab", { name: "3日" }).click()

    await expect(page.locator(".capital-flow-card .flow-tab.active")).toContainText("3日")
    await expect(capitalFlowCard).not.toContainText("贵州茅台")
    await expect(capitalFlowCard).not.toContainText("宁德时代")
    await expect(capitalFlowCard).not.toContainText("资金流向持续排名暂不可用")
  })

  test("dashboard tablists support keyboard focus and selection semantics", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    const oneDayTab = page.getByRole("tab", { name: "1日" })
    const threeDayTab = page.getByRole("tab", { name: "3日" })
    const fiveDayTab = page.getByRole("tab", { name: "5日" })

    await oneDayTab.focus()
    await expect(oneDayTab).toBeFocused()
    await page.keyboard.press("ArrowRight")

    await expect(threeDayTab).toBeFocused()
    await expect(threeDayTab).toHaveAttribute("aria-selected", "true")
    await expect(page.locator(".capital-flow-card .flow-tab.active")).toContainText("3日")

    await page.keyboard.press("ArrowLeft")
    await expect(oneDayTab).toBeFocused()
    await expect(oneDayTab).toHaveAttribute("aria-selected", "true")

    await page.keyboard.press("ArrowLeft")
    await expect(fiveDayTab).toBeFocused()
    await expect(fiveDayTab).toHaveAttribute("aria-selected", "true")

    const watchlistTab = page.getByRole("tab", { name: "自选" })
    const positionTab = page.getByRole("tab", { name: "持仓" })
    const focusTab = page.getByRole("tab", { name: "重点" })

    await watchlistTab.focus()
    await expect(watchlistTab).toBeFocused()
    await page.keyboard.press("ArrowRight")

    await expect(positionTab).toBeFocused()
    await expect(positionTab).toHaveAttribute("aria-selected", "true")
    await expect(page.locator(".stock-pool-card .pool-tab.active")).toContainText("持仓")

    await page.keyboard.press("ArrowLeft")
    await expect(watchlistTab).toBeFocused()
    await expect(watchlistTab).toHaveAttribute("aria-selected", "true")

    await page.keyboard.press("ArrowLeft")
    await expect(focusTab).toBeFocused()
    await expect(focusTab).toHaveAttribute("aria-selected", "true")
  })

  test("dashboard keeps honest pending trend copy while the first trend snapshot is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangKline: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("button", { name: "刷新数据" })).toBeVisible()
    await expect(page.locator(".market-indicators .chart-section")).toContainText("分时趋势同步中...")
    await expect(page.locator(".market-indicators .chart-section")).not.toContainText("待接入真实行情时间序列接口")
  })

  test("dashboard keeps the last verified trend slice visible when a later trend refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failKlineAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".market-indicators .chart-section")).not.toContainText("分时趋势暂不可用")
    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".market-indicators .chart-section")).toContainText("分时趋势暂不可用，当前仍显示上次成功同步的分时趋势快照。")
    await expect(page.locator(".market-indicators .chart-section")).not.toContainText("当前暂无已验证分时趋势快照。")
  })

  test("dashboard reports explicit technical-indicator unavailability when the live indicator slice fails on first load", async ({ page }) => {
    await stubPhase1Apis(page, { failIndicators: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".indicators-section")).toContainText("技术指标暂不可用，当前暂无已验证指标快照。")
    await expect(page.locator(".indicators-section")).not.toContainText("技术指标真实接口待接入")
  })

  test("dashboard keeps the last verified technical indicators visible when a later indicator refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndicatorsAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".indicators-section")).toContainText("RSI")
    await expect(page.locator(".indicators-section")).toContainText("61.2")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".indicators-section")).toContainText("技术指标暂不可用，当前仍显示上次成功同步的技术指标快照。")
    await expect(page.locator(".indicators-section")).toContainText("RSI")
    await expect(page.locator(".indicators-section")).toContainText("61.2")
  })

  test("dashboard reports explicit monitoring unavailability when the live monitoring slice fails on first load", async ({ page }) => {
    await stubPhase1Apis(page, { failHealth: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".monitoring-section")).toContainText("系统监控暂不可用，当前暂无已验证监控快照。")
    await expect(page.locator(".monitoring-section")).not.toContainText("系统监控真实接口待接入")
  })

  test("dashboard keeps the last verified monitoring slice visible when a later monitoring refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failHealthAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".monitoring-section")).toContainText("服务状态")
    await expect(page.locator(".monitoring-section")).toContainText("HEALTHY")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".monitoring-section")).toContainText("系统监控暂不可用，当前仍显示上次成功同步的监控快照。")
    await expect(page.locator(".monitoring-section")).toContainText("服务状态")
    await expect(page.locator(".monitoring-section")).toContainText("HEALTHY")
  })

  test("dashboard disables default change chrome for description-only fund-flow summary cards", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: "domcontentloaded" })

    const fundFlowSection = page.locator(".enhanced-fund-flow")
    await expect(fundFlowSection).toContainText("北向资金总额")
    await expect(fundFlowSection).toContainText("主力净流入")
    await expect(fundFlowSection.locator(".artdeco-stat-change")).toHaveCount(2)
    await expect(fundFlowSection).not.toContainText("+0%")
  })

  test("market realtime keeps honest pending placeholders while the first quote snapshot is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangQuotes: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/realtime`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("实时行情工作台")).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "核心蓝筹样本", "--"])
    await expect(page.locator(".hero-meta")).toContainText("SAMPLE: --")
    await expect(page.locator(".content-shell-meta")).toContainText("MOOD: --")
    await expect(page.locator(".content-shell-meta")).toContainText("UP: --")
    await expect(page.locator(".content-shell-meta")).toContainText("DOWN: --")
    await expect(page.locator(".distribution-pending")).toContainText("首份样本快照同步中，涨跌分布待接入。")
    await expect(page.locator(".stats-strip")).not.toContainText("0亿")
    await expect(page.locator(".stats-strip")).not.toContainText("0%")
    await expect(page.locator(".stats-strip")).not.toContainText("0只")
  })

  test("market realtime does not leak a failed first-load request id into route metadata", async ({ page }) => {
    await stubPhase1Apis(page, { failQuotes: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/realtime`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("实时行情工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("TRACE_ID: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-quotes-first-fail")
    await expect(page.getByText("当前暂无已验证样本快照。")).toBeVisible()
    await expect(page.getByText("已保留上一份有效样本快照。")).toHaveCount(0)
  })

  test("market realtime keeps the last verified request id when a refresh fails after a successful sync", async ({ page }) => {
    await stubPhase1Apis(page, { failQuotesAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/realtime`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".hero-meta")).toContainText("TRACE_ID: e2e-phase1-quotes")
    await page.getByRole("button", { name: "刷新行情" }).first().click()
    await expect(page.locator(".hero-meta")).toContainText("TRACE_ID: e2e-phase1-quotes")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-quotes-refresh-fail")
  })

  test("market realtime does not leak the previous preset rows into a different preset while that preset is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangQuoteSymbolRequests: ["600036,601318,600000,601166,601288"] })

    await page.goto(`${FRONTEND_BASE_URL}/market/realtime`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".hero-meta")).toContainText("PRESET: 核心蓝筹样本")
    await expect(page.locator("tbody tr")).toHaveCount(3)
    await expect(page.locator("tbody")).toContainText("000001")
    await expect(page.locator("tbody")).toContainText("600519")

    await page.locator(".toolbar select").selectOption("finance")

    await expect(page.locator(".hero-meta")).toContainText("PRESET: 金融权重样本")
    await expect(page.locator(".hero-meta")).toContainText("TRACE_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("SAMPLE: --")
    await expect(page.locator("tbody tr")).toHaveCount(0)
    await expect(page.locator("tbody")).not.toContainText("000001")
    await expect(page.locator("tbody")).not.toContainText("600519")
    await expect(page.locator(".distribution-pending")).toContainText("当前暂无已验证样本快照，涨跌分布待接入。")
  })

  test("market lhb renders shell, filters, and table with mock rows", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("龙虎榜工作台")).toBeVisible()
    await expect(page.getByText("龙虎榜数据")).toBeVisible()
    await expect(page.getByRole("button", { name: "买入榜" })).toBeVisible()
    await expect(page.getByRole("button", { name: "卖出榜" })).toBeVisible()
    await expect(page.getByRole("button", { name: "机构榜" })).toBeVisible()
    await expect(page.getByRole("table")).toBeVisible()
    await expect(page.locator(".stats-strip")).not.toContainText("44.00")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("1.00")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("2.00")
  })

  test("market lhb keeps honest pending placeholders while the first leaderboard payload is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangLhb: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("龙虎榜工作台")).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "今日", "买入榜", "--"])
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".hero-shell")).not.toContainText("ROWS: 0")
    await expect(page.locator(".stats-strip")).not.toContainText("榜单条目0")
  })

  test("market lhb does not leak a failed first-load request id into route metadata", async ({ page }) => {
    await stubPhase1Apis(page, { failLhb: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("龙虎榜工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-lhb-first-fail")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "今日", "买入榜", "--"])
  })

  test("market lhb keeps the last verified request id when a refresh fails after a successful sync", async ({ page }) => {
    await stubPhase1Apis(page, { failLhbAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase1-lhb")
    await page.getByRole("button", { name: "刷新榜单" }).click()

    await expect(page.locator(".state-banner--error")).toContainText("龙虎榜加载失败，已保留上一份有效榜单。")
    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase1-lhb")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-lhb-refresh-fail")
    await expect(page.getByText("贵州茅台 (600519)")).toBeVisible()
  })

  test("market lhb keeps shell and filters on empty data", async ({ page }) => {
    await stubPhase1Apis(page, { emptyLhb: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("龙虎榜工作台")).toBeVisible()
    await expect(page.getByText("龙虎榜数据")).toBeVisible()
    await expect(page.getByRole("button", { name: "买入榜" })).toBeVisible()
    await expect(page.getByRole("button", { name: "卖出榜" })).toBeVisible()
    await expect(page.getByRole("button", { name: "机构榜" })).toBeVisible()
  })

  test("market lhb refetches route-consistent rows when trade date changes", async ({ page }) => {
    const lhbRequests: string[] = []
    await stubPhase1Apis(page, { lhbRequests })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("贵州茅台 (600519)")).toBeVisible()
    await page.getByRole("combobox", { name: "交易日筛选" }).selectOption("dayBefore")

    await expect.poll(() => lhbRequests.at(-1) ?? "").toContain("start_date=2026-04-01")
    await expect.poll(() => lhbRequests.at(-1) ?? "").toContain("end_date=2026-04-01")
    await expect(page.getByText("中际旭创 (300308)")).toBeVisible()
  })

  test("market lhb does not leak previous rows when a newly selected trade date has no verified snapshot", async ({ page }) => {
    await stubPhase1Apis(page, { failLhbDayBefore: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("贵州茅台 (600519)")).toBeVisible()
    await page.getByRole("combobox", { name: "交易日筛选" }).selectOption("dayBefore")

    await expect(page.locator(".hero-meta")).toContainText("DATE: 前日")
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".state-banner--error")).toContainText("龙虎榜加载失败，已保留上一份有效榜单。")
    await expect(page.getByText("贵州茅台 (600519)")).toHaveCount(0)
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-lhb")
  })

  test("market technical keeps chart on the page-owned kline request path", async ({ page }) => {
    const klineRequests: string[] = []
    const legacyMarketKlineRequests: string[] = []
    await stubPhase1Apis(page, { klineRequests, legacyMarketKlineRequests })

    await page.goto(`${FRONTEND_BASE_URL}/market/technical`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("K线分析工作台")).toBeVisible()
    await expect.poll(() => klineRequests.length).toBe(1)
    expect(legacyMarketKlineRequests).toHaveLength(0)

    await page.getByRole("button", { name: "刷新K线" }).click()

    await expect.poll(() => klineRequests.length).toBe(2)
    expect(legacyMarketKlineRequests).toHaveLength(0)
  })

  test("market technical keeps honest pending placeholders while the first k-line snapshot is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangKline: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/technical`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("K线分析工作台")).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["000001", "--", "--", "--"])
    await expect(page.locator(".hero-meta")).toContainText("POINTS: --")
    await expect(page.locator(".content-shell-meta")).toContainText("POINTS: --")
    await expect(page.getByText("Synchronizing K-Line Sample")).toBeVisible()
    await expect(page.locator(".hero-shell")).not.toContainText("POINTS: 0")
    await expect(page.locator(".content-shell")).not.toContainText("POINTS: 0")
    await expect(page.locator(".kline-container")).not.toContainText("Waiting For K-Line Sample")
  })

  test("market technical does not leak a failed first-load request id into route metadata", async ({ page }) => {
    await stubPhase1Apis(page, { failKline: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/technical`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("K线分析工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).toContainText("POINTS: --")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-kline-first-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("POINTS: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["000001", "--", "--", "--"])
  })

  test("market technical keeps the last verified request id when a refresh fails after a successful sync", async ({ page }) => {
    await stubPhase1Apis(page, { failKlineAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/market/technical`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase1-kline")
    await page.getByRole("button", { name: "刷新K线" }).click()

    await expect(page.locator(".state-banner--error")).toContainText("K线数据加载失败，已保留上一份有效样本。")
    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase1-kline")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-kline-refresh-fail")
    await expect(page.locator(".hero-meta")).toContainText("POINTS: 6")
    await expect(page.getByText("2026-04-06")).toBeVisible()
  })

  test("detail graphics keeps honest pending placeholders while the first k-line snapshot is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangKline: true })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "K 线指标分析面板" })).toBeVisible()
    await expect(page.locator(".module-meta")).toContainText("SYMBOL: 600519")
    await expect(page.locator(".module-meta")).toContainText("POINTS: --")
    await expect(page.locator(".module-meta")).not.toContainText("REQ_ID:")
    await expect(page.getByText("技术分析数据同步中...")).toBeVisible()
    await expect(page.locator(".module-meta")).not.toContainText("POINTS: 0")
  })

  test("detail graphics does not leak a failed first-load request id into route metadata", async ({ page }) => {
    await stubPhase1Apis(page, { failKline: true })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "K 线指标分析面板" })).toBeVisible()
    await expect(page.locator(".module-meta")).toContainText("POINTS: --")
    await expect(page.locator(".module-meta")).not.toContainText("REQ_ID:")
    await expect(page.locator(".module-meta")).not.toContainText("e2e-phase1-kline-first-fail")
    await expect(page.getByText("kline feed unavailable，当前暂无已验证K线分析快照。")).toBeVisible()
  })

  test("detail graphics keeps the last verified request id when analyze refresh fails after a successful sync", async ({ page }) => {
    await stubPhase1Apis(page, { failKlineAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline")
    await expect(page.locator(".module-meta")).toContainText("POINTS: 6")
    await page.getByRole("button", { name: "开始分析" }).click()

    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline")
    await expect(page.locator(".module-meta")).toContainText("POINTS: 6")
    await expect(page.locator(".module-meta")).not.toContainText("e2e-phase1-kline-refresh-fail")
    await expect(page.getByText("kline refresh unavailable，当前仍显示上次成功同步的K线分析快照。")).toBeVisible()
    await expect(page.locator(".trend-card")).not.toContainText("暂无趋势图表数据。")
  })

  test("detail graphics surfaces indicators-slice partial failure instead of a generic empty indicators card", async ({ page }) => {
    await stubPhase1Apis(page, { failIndicators: true })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "K 线指标分析面板" })).toBeVisible()
    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline")
    await expect(page.locator(".module-meta")).toContainText("POINTS: 6")
    await expect(page.locator(".runtime-message")).toContainText("技术指标部分加载失败：")
    await expect(page.locator(".runtime-message")).toContainText("当前仅显示已验证的K线趋势快照。")
    await expect(page.getByText("技术指标暂不可用，当前仅显示趋势数据。")).toBeVisible()
    await expect(page.locator(".trend-card")).not.toContainText("暂无趋势图表数据。")
    await expect(page.locator(".indicators-card")).not.toContainText("暂无技术指标结果。")
  })

  test("detail graphics keeps the last verified indicators visible when a later indicators refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndicatorsAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".indicators-card")).toContainText("RSI")
    await expect(page.locator(".indicators-card")).toContainText("61.2")

    await page.getByRole("button", { name: "开始分析" }).click()

    await expect(page.locator(".runtime-message")).toContainText("技术指标部分加载失败：")
    await expect(page.locator(".runtime-message")).toContainText("当前仍显示上次成功同步的技术指标快照。")
    await expect(page.locator(".indicators-card")).toContainText("RSI")
    await expect(page.locator(".indicators-card")).toContainText("61.2")
    await expect(page.locator(".indicators-card")).not.toContainText("暂无技术指标结果。")
  })

  test("detail graphics clears the previous symbol k-line snapshot when a new route symbol fails before its first verified snapshot", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.route(/https?:\/\/[^/]+\/api\/v1\/market\/kline.*/, async (route) => {
      const requestUrl = new URL(route.request().url())
      if (requestUrl.searchParams.get("stock_code") !== "000001") {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          success: false,
          request_id: "e2e-phase1-detail-000001-kline-fail",
          message: "kline detail 000001 unavailable",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".module-meta")).toContainText("SYMBOL: 600519")
    await expect(page.locator(".module-meta")).toContainText("POINTS: 6")
    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline")

    await page.evaluate(() => {
      window.history.pushState({}, "", "/detail/graphics/000001")
      window.dispatchEvent(new PopStateEvent("popstate"))
    })

    await expect(page.locator(".module-meta")).toContainText("SYMBOL: 000001")
    await expect(page.locator(".module-meta")).toContainText("POINTS: --")
    await expect(page.locator(".module-meta")).not.toContainText("REQ_ID: e2e-phase1-kline")
    await expect(page.locator(".module-meta")).not.toContainText("e2e-phase1-detail-000001-kline-fail")
    await expect(page.locator(".runtime-message")).toContainText("kline detail 000001 unavailable")
    await expect(page.locator(".trend-card")).toContainText("暂无趋势图表数据。")
    await expect(page.locator(".indicators-card")).not.toContainText("RSI")
  })

  test("detail graphics does not leak the previous symbol indicators when only the new route symbol enrichment slice failed", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.route(/https?:\/\/[^/]+\/api\/v1\/market\/kline.*/, async (route) => {
      const requestUrl = new URL(route.request().url())
      if (requestUrl.searchParams.get("stock_code") !== "000001") {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-kline-000001",
          data: {
            data: [
              { datetime: "2026-04-07 15:00:00", open: 90, high: 92, low: 89, close: 91, volume: 800000 },
              { datetime: "2026-04-08 15:00:00", open: 91, high: 93, low: 90, close: 92, volume: 820000 },
            ],
          },
        }),
      })
    })

    await page.route(/https?:\/\/[^/]+\/api\/v1\/technical-indicators.*/, async (route) => {
      const requestUrl = new URL(route.request().url())
      if (requestUrl.searchParams.get("symbol") !== "000001") {
        await route.fallback()
        return
      }

      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          success: false,
          request_id: "e2e-phase1-indicators-000001-fail",
          message: "indicators detail 000001 unavailable",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".indicators-card")).toContainText("RSI")
    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline")

    await page.evaluate(() => {
      window.history.pushState({}, "", "/detail/graphics/000001")
      window.dispatchEvent(new PopStateEvent("popstate"))
    })

    await expect(page.locator(".module-meta")).toContainText("SYMBOL: 000001")
    await expect(page.locator(".module-meta")).toContainText("POINTS: 2")
    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline-000001")
    await expect(page.locator(".runtime-message")).toContainText("indicators detail 000001 unavailable")
    await expect(page.locator(".runtime-message")).toContainText("当前仅显示已验证的K线趋势快照。")
    await expect(page.locator(".indicators-card")).toContainText("技术指标暂不可用，当前仅显示趋势数据。")
    await expect(page.locator(".indicators-card")).not.toContainText("RSI")
    await expect(page.locator(".trend-card")).not.toContainText("暂无趋势图表数据。")
  })

  test("detail graphics clears the previous period snapshot when the new period failed before its first verified snapshot", async ({ page }) => {
    const klineRequests: string[] = []
    await stubPhase1Apis(page, { klineRequests })

    await page.route(/https?:\/\/[^/]+\/api\/v1\/market\/kline.*/, async (route) => {
      const requestUrl = new URL(route.request().url())
      if (requestUrl.searchParams.get("period") !== "1w") {
        await route.fallback()
        return
      }

      klineRequests.push(route.request().url())

      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({
          success: false,
          request_id: "e2e-phase1-kline-1w-fail",
          message: "kline 1w unavailable",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/detail/graphics/600519`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".module-meta")).toContainText("SYMBOL: 600519")
    await expect(page.locator(".module-meta")).toContainText("PERIOD: 1d")
    await expect(page.locator(".module-meta")).toContainText("POINTS: 6")
    await expect(page.locator(".module-meta")).toContainText("REQ_ID: e2e-phase1-kline")
    await expect(page.locator(".indicators-card")).toContainText("RSI")

    await page.locator("select").selectOption("1w")
    await page.getByRole("button", { name: "开始分析" }).click()

    await expect.poll(() => klineRequests.at(-1) ?? "").toContain("period=1w")
    await expect(page.locator(".module-meta")).toContainText("PERIOD: 1w")
    await expect(page.locator(".module-meta")).toContainText("POINTS: --")
    await expect(page.locator(".module-meta")).not.toContainText("REQ_ID: e2e-phase1-kline")
    await expect(page.locator(".module-meta")).not.toContainText("e2e-phase1-kline-1w-fail")
    await expect(page.locator(".runtime-message")).toContainText("kline 1w unavailable")
    await expect(page.locator(".trend-card")).toContainText("暂无趋势图表数据。")
    await expect(page.locator(".indicators-card")).not.toContainText("RSI")
  })

  test("industry page renders request metadata and content blocks with honest ordinal and count surfaces", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.getByText("DATA: REAL")).toBeVisible()
    await expect(page.getByText(/REQ_ID:/)).toBeVisible()
    await expect(page.getByRole("heading", { name: "板块热度排行" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "资金轮动快照" })).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新板块" })).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["2", "2", "3.28%", "0"])
    await expect(page.locator(".hybrid-table__content")).toContainText("半导体")
    await expect(page.locator(".hybrid-table__content")).toContainText("算力")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("1.00")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("2.00")
  })

  test("industry page keeps honest pending provenance while the first board payload is still unresolved", async ({ page }) => {
    await stubPhase1Apis(page, { hangIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("DATA: PENDING")
    await expect(page.locator(".hero-meta")).not.toContainText("DATA: REAL")
    await expect(page.locator(".loading-state").getByText("板块数据同步中")).toBeVisible()
  })

  test("industry page shows empty state when real feed returns no rows", async ({ page }) => {
    await stubPhase1Apis(page, { emptyIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.locator(".empty-state").getByText("暂无板块数据")).toBeVisible()
  })

  test("industry page shows error state when real feed fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("DATA: UNAVAILABLE")
    await expect(page.locator(".hero-meta")).not.toContainText("DATA: REAL")
    await expect(page.locator(".error-state").getByText("板块数据加载失败").first()).toBeVisible()
  })

  test("industry page does not leak a failed first-load request id into route metadata", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-industry-first-fail")
  })

  test("industry page keeps last successful rows visible when a manual refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustryAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.getByRole("cell", { name: "半导体" })).toBeVisible()
    await expect(page.getByRole("cell", { name: "算力" })).toBeVisible()

    await page.getByRole("button", { name: "刷新板块" }).click()

    await expect(page.locator(".warning-panel").getByText("部分刷新失败")).toBeVisible()
    await expect(page.locator(".warning-panel")).toContainText("当前仍展示上次成功同步的行业板块数据")
    await expect(page.getByText("刷新异常")).toBeVisible()
    await expect(page.getByRole("cell", { name: "半导体" })).toBeVisible()
    await expect(page.getByRole("cell", { name: "算力" })).toBeVisible()
  })

  test("industry page keeps the last verified request id when a manual refresh fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustryAfterFirstSuccess: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: e2e-phase1-industry")

    await page.getByRole("button", { name: "刷新板块" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: e2e-phase1-industry")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase1-industry-refresh-fail")
  })
})
