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

const DASHBOARD_QUOTES = [
  { symbol: "000001.SH", latest_price: 3321.08, change_percent: 0.65, volume: 9123 },
  { symbol: "399001.SZ", latest_price: 10214.2, change_percent: 0.71, volume: 8450 },
  { symbol: "399006.SZ", latest_price: 1988.66, change_percent: -0.22, volume: 6012 },
]

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
    trade_date: "2026-04-03",
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
  emptyIndustry?: boolean
  failIndustry?: boolean
  emptyLhb?: boolean
}

async function stubPhase1Apis(page: Page, options: Phase1StubOptions = {}): Promise<void> {
  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
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
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
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
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase1-quotes",
          data: DASHBOARD_QUOTES,
        }),
      })
      return
    }

    if (normalizedPath === "/akshare/market/fund-flow/hsgt-summary") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: FUND_FLOW_SUMMARY,
        }),
      })
      return
    }

    if (normalizedPath === "/akshare/market/fund-flow/big-deal") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: BIG_DEAL_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v2/market/sector/fund-flow") {
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
          process_time_ms: 12,
          data: options.emptyIndustry ? [] : INDUSTRY_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v1/market/kline") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            data: KLINE_ROWS,
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

    if (normalizedPath === "/v2/market/lhb") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: options.emptyLhb ? [] : LHB_ROWS,
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
    await expect(page.getByText("市场资金流向概览")).toBeVisible()
    await expect(page.getByText("主要市场指标")).toBeVisible()
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

  test("industry page renders request metadata and content blocks with mock rows", async ({ page }) => {
    await stubPhase1Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.getByText("DATA: REAL")).toBeVisible()
    await expect(page.getByText(/REQ_ID:/)).toBeVisible()
    await expect(page.getByRole("heading", { name: "板块热度排行" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "资金轮动快照" })).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新板块" })).toBeVisible()
  })

  test("industry page shows empty state when real feed returns no rows", async ({ page }) => {
    await stubPhase1Apis(page, { emptyIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.getByText("暂无板块数据")).toBeVisible()
  })

  test("industry page shows error state when real feed fails", async ({ page }) => {
    await stubPhase1Apis(page, { failIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/industry`, { waitUntil: "domcontentloaded" })

    await expect(page.getByRole("heading", { name: "板块动向工作台" })).toBeVisible()
    await expect(page.locator(".error-state").getByText("板块数据加载失败").first()).toBeVisible()
  })
})
