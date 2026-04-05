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

const CONCEPT_ROWS = [
  { sector_name: "机器人", change_percent: 4.21, main_net_inflow: 980000000, leading_stock: "汇川技术" },
  { sector_name: "算力租赁", change_percent: 2.83, main_net_inflow: 560000000, leading_stock: "中际旭创" },
]

const HSGT_SUMMARY_ROWS = [
  { 交易日: "2026-04-01", 板块: "沪股通", 资金方向: "北向", 成交净买额: 8.2, 指数涨跌幅: 0.41 },
  { 交易日: "2026-04-01", 板块: "深股通", 资金方向: "北向", 成交净买额: 5.7, 指数涨跌幅: 0.38 },
  { 交易日: "2026-04-02", 板块: "沪股通", 资金方向: "北向", 成交净买额: 10.5, 指数涨跌幅: 0.62 },
  { 交易日: "2026-04-02", 板块: "深股通", 资金方向: "北向", 成交净买额: 6.9, 指数涨跌幅: 0.44 },
]

const BIG_DEAL_ROWS = [
  { symbol: "600519", 股票简称: "贵州茅台", 成交价格: 1688.2, 成交额: 920000000, 大单性质: "买盘", 涨跌幅: 1.42 },
  { symbol: "300750", 股票简称: "宁德时代", 成交价格: 212.6, 成交额: 460000000, 大单性质: "卖盘", 涨跌幅: -0.73 },
]

const INDICATOR_ROWS = [
  { abbreviation: "MA", chinese_name: "移动平均线", category: "trend", panel_type: "overlay", description: "趋势跟踪" },
  { abbreviation: "RSI", chinese_name: "相对强弱指标", category: "momentum", panel_type: "sub", description: "动量观察" },
  { abbreviation: "VOL", chinese_name: "成交量", category: "volume", panel_type: "sub", description: "量能分析" },
]

const STOCK_ROWS = [
  { symbol: "600519", name: "贵州茅台", price: 1688.2, change_pct: 1.42, volume: 320000, turnover: 920000000, pe: 28.6, market_cap: 2120000000000 },
  { symbol: "300750", name: "宁德时代", price: 212.6, change_pct: -0.73, volume: 580000, turnover: 460000000, pe: 24.1, market_cap: 980000000000 },
  { symbol: "002594", name: "比亚迪", price: 258.3, change_pct: 2.11, volume: 410000, turnover: 510000000, pe: 22.8, market_cap: 760000000000 },
]

const SIGNAL_ROWS = [
  { symbol: "600519", name: "贵州茅台", type: "BUY", price: 1688.2, time: "09:35:12", strategy: "Northbound Momentum" },
  { symbol: "300750", name: "宁德时代", type: "SELL", price: 212.6, time: "10:02:45", strategy: "Breakdown Guard" },
]

function normalizePathname(url: string): string {
  const pathname = new URL(url).pathname
  return pathname.startsWith("/api/") ? pathname.slice(4) : pathname
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript(({ user }) => {
    const token = "e2e-phase2-token"
    localStorage.setItem("auth_token", token)
    localStorage.setItem("auth_user", JSON.stringify(user))
    localStorage.setItem("token", token)
    localStorage.setItem("user", JSON.stringify(user))
    localStorage.setItem("access_token", token)
  }, { user: E2E_USER })
}

async function stubPhase2Apis(page: Page): Promise<void> {
  const watchlists = [
    { id: "wl-core", name: "核心组合" },
    { id: "wl-growth", name: "成长跟踪" },
  ]
  const watchlistStocks = new Map<string, Array<Record<string, unknown>>>([
    ["wl-core", [
      { stock_code: "600519", stock_name: "贵州茅台", entry_price: 1680, weight: 0.25 },
      { stock_code: "300750", stock_name: "宁德时代", entry_price: 210, weight: 0.18 },
    ]],
    ["wl-growth", [
      { stock_code: "002594", stock_name: "比亚迪", entry_price: 250, weight: 0.16 },
    ]],
  ])

  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    const normalizedPath = normalizePathname(request.url())
    const method = request.method()

    if (normalizedPath === "/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-ready",
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
          data: { status: "healthy" },
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
          data: { csrf_token: "e2e-phase2-csrf" },
        }),
      })
      return
    }

    if (normalizedPath === "/v2/market/sector/fund-flow") {
      const sectorType = url.searchParams.get("sector_type")
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-concept",
          data: sectorType === "概念" ? CONCEPT_ROWS : [],
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
          data: HSGT_SUMMARY_ROWS,
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

    if (normalizedPath === "/v1/indicators/registry") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            indicators: INDICATOR_ROWS,
          },
        }),
      })
      return
    }

    if (normalizedPath === "/v1/data/stocks/basic") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: STOCK_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v1/trade/signals") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-signals",
          data: SIGNAL_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/watchlists" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: watchlists.map((list) => ({
            id: list.id,
            name: list.name,
            stocks_count: watchlistStocks.get(list.id)?.length ?? 0,
          })),
        }),
      })
      return
    }

    if (normalizedPath === "/v1/monitoring/watchlists" && method === "POST") {
      const payload = JSON.parse(request.postData() || "{}") as { name?: string }
      const nextId = `wl-${watchlists.length + 1}`
      watchlists.push({
        id: nextId,
        name: payload.name || `新建组合-${watchlists.length + 1}`,
      })
      watchlistStocks.set(nextId, [])

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: { id: nextId },
        }),
      })
      return
    }

    const watchlistStocksMatch = normalizedPath.match(/^\/v1\/monitoring\/watchlists\/([^/]+)\/stocks(?:\/([^/]+))?$/)
    if (watchlistStocksMatch && method === "GET") {
      const watchlistId = watchlistStocksMatch[1]
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: watchlistStocks.get(watchlistId) || [],
        }),
      })
      return
    }

    if (watchlistStocksMatch && method === "DELETE") {
      const watchlistId = watchlistStocksMatch[1]
      const symbol = watchlistStocksMatch[2]
      const nextRows = (watchlistStocks.get(watchlistId) || []).filter((row) => row.stock_code !== symbol)
      watchlistStocks.set(watchlistId, nextRows)

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: null,
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

test.describe("Phase 2 Mainline Matrix", () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
  })

  test("data concept renders concept board shell and rows under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".market-concept-tab")).toBeVisible()
    await expect(page.getByText("概念板块工作台")).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新板块" })).toBeVisible()
    await expect(page.locator(".artdeco-table")).toContainText("机器人")
    await expect(page.locator(".hero-meta")).toContainText("REQ:")
  })

  test("data fund flow renders trend panel and ranking table under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".fund-flow-analysis")).toBeVisible()
    await expect(page.getByText("资金流向工作台")).toBeVisible()
    await expect(page.getByText("近30日资金流向趋势")).toBeVisible()
    await expect(page.getByText("个股资金流向排行")).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新资金流" })).toBeVisible()
    await expect(page.locator(".fund-ranking-card")).toContainText("贵州茅台")
  })

  test("data indicator renders stats and screening results under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".artdeco-data-analysis")).toBeVisible()
    await expect(page.getByText("数据分析中心")).toBeVisible()
    await expect(page.getByText("可用指标")).toBeVisible()
    await page.getByRole("button", { name: "执行筛选" }).click()
    await expect(page.locator(".tab-content")).toContainText("贵州茅台")
    await expect(page.locator(".stats-overview")).toContainText("3")
  })

  test("watchlist manage supports create and remove flows under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-manager")).toBeVisible()
    await expect(page.getByText("组合持仓明细")).toBeVisible()
    await expect(page.getByRole("button", { name: "导入" })).toBeVisible()
    await expect(page.getByRole("button", { name: "导出" })).toBeVisible()
    await expect(page.locator(".watchlist-tabs")).toContainText("核心组合")

    page.once("dialog", async (dialog) => {
      await dialog.accept("短线观察")
    })
    await page.locator(".add-list-btn").click()
    await expect(page.locator(".watchlist-tabs")).toContainText("短线观察")

    const firstDeleteButton = page.getByRole("button", { name: "删除" }).first()
    await firstDeleteButton.click()
    await expect(page.locator(".watchlist-manager")).not.toContainText("贵州茅台")
  })

  test("watchlist signals renders timeline and stats under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/signals`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".strategy-signals-tab")).toBeVisible()
    await expect(page.getByText("策略信号工作台")).toBeVisible()
    await expect(page.getByText("实时信号时间轴")).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新信号" })).toBeVisible()
    await expect(page.locator(".signals-timeline")).toContainText("贵州茅台")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
  })

  test("watchlist screener renders filters and results under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/screener`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".screener-container")).toBeVisible()
    await expect(page.getByText("STOCK SCREENER")).toBeVisible()
    await expect(page.getByText("SCREENING CRITERIA")).toBeVisible()
    await expect(page.getByText("SCREENING RESULTS")).toBeVisible()
    await expect(page.getByRole("button", { name: "RUN SCREENING" })).toBeVisible()
    await expect(page.getByRole("button", { name: "CLEAR FILTERS" })).toBeVisible()
    await expect(page.locator(".results-table")).toContainText("贵州茅台")
  })
})
