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

type Phase2StubOptions = {
  emptyConcept?: boolean
  failConcept?: boolean
  failConceptRefreshOnly?: boolean
  hangConcept?: boolean
  emptyFundFlow?: boolean
  failFundFlow?: boolean
  failFundFlowRankingOnly?: boolean
  failIndicatorRegistry?: boolean
  failIndicatorRegistryRefreshOnly?: boolean
  failStocksBasic?: boolean
  failStocksBasicRefreshOnly?: boolean
  hangStocksBasic?: boolean
  failWatchlists?: boolean
  hangWatchlists?: boolean
  hangWatchlistStocks?: boolean
  failWatchlistStocksRefreshOnly?: boolean
}

async function stubPhase2Apis(page: Page, options: Phase2StubOptions = {}): Promise<void> {
  const context = page.context()
  let hasServedVerifiedConceptSnapshot = false
  let indicatorRegistryRequestCount = 0
  let stocksBasicRequestCount = 0
  let watchlistStocksRequestCount = 0
  const watchlists = [
    { id: "wl-core", name: "核心组合" },
    { id: "wl-growth", name: "成长跟踪" },
  ]
  const watchlistStocks = new Map<string, Array<Record<string, unknown>>>([
    ["wl-core", [
      { symbol: "600519", stock_code: "600519", stock_name: "贵州茅台", entry_price: 1680, weight: 0.25 },
      { symbol: "300750", stock_code: "300750", stock_name: "宁德时代", entry_price: 210, weight: 0.18 },
    ]],
    ["wl-growth", [
      { symbol: "002594", stock_code: "002594", stock_name: "比亚迪", entry_price: 250, weight: 0.16 },
    ]],
  ])

  await context.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
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
      if (sectorType === "概念" && options.failConcept) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-concept-first-fail",
            message: "concept feed unavailable",
          }),
        })
        return
      }

      if (sectorType === "概念" && options.failConceptRefreshOnly && hasServedVerifiedConceptSnapshot) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-concept-refresh-fail",
            message: "concept refresh unavailable",
          }),
        })
        return
      }

      if (sectorType === "概念" && options.hangConcept) {
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-concept",
          data: sectorType === "概念" ? (options.emptyConcept ? [] : CONCEPT_ROWS) : [],
        }),
      })
      if (sectorType === "概念") {
        hasServedVerifiedConceptSnapshot = true
      }
      return
    }

    if (normalizedPath === "/akshare/market/fund-flow/hsgt-summary") {
      if (options.failFundFlow) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-fund-summary-fail",
            message: "fund flow summary unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-fund-summary",
          data: options.emptyFundFlow ? [] : HSGT_SUMMARY_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/akshare/market/fund-flow/big-deal") {
      if (options.failFundFlow || options.failFundFlowRankingOnly) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-fund-ranking-fail",
            message: "big deal feed unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-fund-ranking",
          data: options.emptyFundFlow ? [] : BIG_DEAL_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v1/indicators/registry") {
      indicatorRegistryRequestCount += 1

      if (options.failIndicatorRegistry) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            message: "indicator registry unavailable",
          }),
        })
        return
      }

      if (options.failIndicatorRegistryRefreshOnly && indicatorRegistryRequestCount > 1) {
        await route.fulfill({
          status: 500,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            message: "indicator registry refresh unavailable",
          }),
        })
        return
      }

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
      stocksBasicRequestCount += 1

      if (options.failStocksBasic) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-stocks-first-fail",
            message: "stocks basic unavailable",
          }),
        })
        return
      }

      if (options.failStocksBasicRefreshOnly && stocksBasicRequestCount > 1) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-stocks-refresh-fail",
            message: "stocks basic refresh unavailable",
          }),
        })
        return
      }

      if (options.hangStocksBasic) {
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "e2e-phase2-stocks-success",
          data: STOCK_ROWS,
        }),
      })
      return
    }

    if (normalizedPath === "/v1/trade/signals" || normalizedPath === "/trading/signals") {
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
      if (options.failWatchlists) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-watchlists-first-fail",
            message: "watchlists unavailable",
          }),
        })
        return
      }

      if (options.hangWatchlists) {
        return
      }

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
      watchlistStocksRequestCount += 1
      const watchlistId = watchlistStocksMatch[1]

      if (options.hangWatchlistStocks) {
        return
      }

      if (options.failWatchlistStocksRefreshOnly && watchlistId === "wl-growth" && watchlistStocksRequestCount > 1) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            request_id: "e2e-phase2-watchlist-stocks-refresh-fail",
            message: "watchlist stocks refresh unavailable",
          }),
        })
        return
      }

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
  test.use({ serviceWorkers: "block" })

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

  test("data concept shows error state when concept feed fails", async ({ page }) => {
    await stubPhase2Apis(page, { failConcept: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("概念板块工作台")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("概念板块数据加载失败")
    await expect(page.getByRole("button", { name: "重试刷新" })).toBeVisible()
  })

  test("data concept does not leak a failed first-load request id into route metadata", async ({ page }) => {
    await stubPhase2Apis(page, { failConcept: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("概念板块工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).toContainText("SECTORS: --")
    await expect(page.locator(".hero-meta")).toContainText("LEADER: --")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase2-concept-first-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("POSITIVE: --")
    await expect(page.locator(".content-shell-meta")).toContainText("NEGATIVE: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
  })

  test("data concept keeps previous rows visible when a manual refresh fails", async ({ page }) => {
    await stubPhase2Apis(page, { failConceptRefreshOnly: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".artdeco-table")).toContainText("机器人")
    await page.getByRole("button", { name: "刷新板块" }).click()
    await expect(page.locator(".warning-panel")).toContainText("部分刷新失败")
    await expect(page.locator(".warning-panel")).toContainText("当前仍展示上次成功同步的概念板块数据")
    await expect(page.locator(".artdeco-table")).toContainText("机器人")
    await expect(page.locator(".content-shell")).not.toContainText("概念板块数据加载失败")
  })

  test("data concept keeps the last verified request id when a manual refresh fails", async ({ page }) => {
    await stubPhase2Apis(page, { failConceptRefreshOnly: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase2-concept")
    await page.getByRole("button", { name: "刷新板块" }).click()
    await expect(page.locator(".warning-panel")).toContainText("当前仍展示上次成功同步的概念板块数据")
    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase2-concept")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase2-concept-refresh-fail")
    await expect(page.locator(".artdeco-table")).toContainText("机器人")
  })

  test("data concept keeps honest pending placeholders while the first concept payload is still unresolved", async ({ page }) => {
    await stubPhase2Apis(page, { hangConcept: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("概念板块工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("SECTORS: --")
    await expect(page.locator(".hero-meta")).toContainText("LEADER: --")
    await expect(page.locator(".content-shell-meta")).toContainText("POSITIVE: --")
    await expect(page.locator(".content-shell-meta")).toContainText("NEGATIVE: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".stats-strip")).not.toContainText("N/A")
    await expect(page.locator(".state-panel")).toContainText("概念板块同步中")
  })

  test("data fund flow renders trend panel and ranking table under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".fund-flow-analysis")).toBeVisible()
    await expect(page.getByText("资金流向工作台")).toBeVisible()
    await expect(page.getByText("今日资金流向趋势")).toBeVisible()
    await expect(page.getByText("个股资金流向排行")).toBeVisible()
    await expect(page.getByRole("button", { name: "刷新资金流" })).toBeVisible()
    await expect(page.locator(".fund-ranking-card")).toContainText("贵州茅台")
    await expect(page.locator(".hybrid-table__content")).toContainText("1")
    await expect(page.locator(".hybrid-table__content")).toContainText("2")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("1.00")
    await expect(page.locator(".hybrid-table__content")).not.toContainText("2.00")
  })

  test("data fund flow shows empty state when summary and ranking are empty", async ({ page }) => {
    await stubPhase2Apis(page, { emptyFundFlow: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("资金流向工作台")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("暂无资金流向数据")
  })

  test("data fund flow keeps trend content visible while flagging ranking partial failure", async ({ page }) => {
    await stubPhase2Apis(page, { failFundFlowRankingOnly: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("资金流向工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".warning-panel")).toContainText("部分数据同步失败")
    await expect(page.locator(".warning-panel")).toContainText("个股排行刷新失败")
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase2-fund-ranking-fail")
    await expect(page.locator(".fund-chart-card")).toContainText("今日资金流向趋势")
    await expect(page.locator(".fund-ranking-card")).toContainText("0 条排行")
    await expect(page.locator(".content-shell")).not.toContainText("资金流向加载失败")
  })

  test("data fund flow keeps pending hero rows honest while the first summary payload is still unresolved", async ({ page }) => {
    await stubPhase2Apis(page)
    await page.route("**/api/akshare/market/fund-flow/hsgt-summary**", async () => {
      await new Promise(() => {})
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".fund-flow-analysis")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("ROWS: 0")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".state-panel")).toContainText("资金流向同步中")
    await expect(page.locator(".content-shell")).not.toContainText("0 条排行")
  })

  test("data fund flow keeps failed first-load hero rows out of faux zero ranking truth", async ({ page }) => {
    await stubPhase2Apis(page, { failFundFlow: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".fund-flow-analysis")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("ROWS: 0")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".state-panel")).toContainText("资金流向加载失败")
    await expect(page.locator(".content-shell")).not.toContainText("暂无资金流向数据")
  })

  test("data indicator keeps screening idle until the user runs it, then shows results", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".artdeco-data-analysis")).toBeVisible()
    await expect(page.getByText("数据分析中心")).toBeVisible()
    await expect(page.getByText("可用指标")).toBeVisible()
    await expect(page.locator(".header-meta")).toContainText("待执行筛选")
    await expect(page.locator(".stats-overview")).toContainText("筛选股票数0")
    await expect(page.locator(".stats-overview")).toContainText("符合条件0")

    await page.getByRole("tab", { name: "📈 筛选结果" }).click()
    await expect(page.locator(".tab-content")).toContainText("尚未执行筛选")
    await expect(page.locator(".tab-content")).not.toContainText("暂无筛选结果")

    await page.getByRole("button", { name: "执行筛选" }).click()
    await expect(page.locator(".header-meta")).toContainText("筛选已就绪")
    await expect(page.locator(".tab-content")).toContainText("贵州茅台")
    await expect(page.locator(".stats-overview")).toContainText("筛选股票数3")
    await expect(page.locator(".stats-overview")).toContainText("符合条件3")
  })

  test("data indicator shows selected indicator context after indicator-card click", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    const indicatorPanel = page.locator("#data-analysis-panel-indicators")
    await expect(indicatorPanel).toBeVisible()
    const indicatorCard = indicatorPanel.locator(".indicator-card").filter({ hasText: "移动平均线" }).first()
    await expect(indicatorCard).toBeVisible()
    await indicatorCard.click()
    await expect(page.locator("#data-analysis-panel-editor")).toBeVisible()
    await expect(page.locator("#data-analysis-panel-editor")).toContainText("指标详情")
    await expect(page.locator("#data-analysis-panel-editor")).toContainText("selected indicator")
    await expect(page.locator("#data-analysis-panel-editor")).toContainText("移动平均线")
    await expect(page.locator("#data-analysis-panel-editor")).toContainText("MA")
    await expect(page.locator("#data-analysis-panel-editor")).not.toContainText("公式编辑器升级中")
  })

  test("data indicator clears the previous selected indicator context when the active category changes before the editor is reopened", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    const indicatorPanel = page.locator("#data-analysis-panel-indicators")
    await expect(indicatorPanel).toBeVisible()
    await indicatorPanel.locator(".indicator-card").filter({ hasText: "移动平均线" }).first().click()

    const editorPanel = page.locator("#data-analysis-panel-editor")
    await expect(editorPanel).toContainText("selected indicator")
    await expect(editorPanel).toContainText("移动平均线")
    await expect(editorPanel).toContainText("MA")

    await page.getByRole("button", { name: "返回指标库" }).click()
    await expect(indicatorPanel).toBeVisible()

    await page.locator(".category-item").filter({ hasText: "动量指标" }).first().click()
    await expect(indicatorPanel).toContainText("相对强弱指标")
    await expect(indicatorPanel).not.toContainText("移动平均线")

    await page.getByRole("tab", { name: "📘 指标详情" }).click()
    await expect(editorPanel).toContainText("从指标库选择一个指标")
    await expect(editorPanel).not.toContainText("selected indicator")
    await expect(editorPanel).not.toContainText("移动平均线")
    await expect(editorPanel).not.toContainText("MA")
  })

  test("data indicator clears the previous selected indicator context when a verified refresh replaces the registry universe", async ({ page }) => {
    await stubPhase2Apis(page)

    let indicatorRegistryRequestCount = 0
    await page.route("**/api/v1/indicators/registry**", async (route) => {
      indicatorRegistryRequestCount += 1

      if (indicatorRegistryRequestCount === 1) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            data: {
              indicators: [
                {
                  abbreviation: "MA",
                  chinese_name: "移动平均线",
                  category: "trend",
                  panel_type: "overlay",
                  description: "趋势跟踪",
                  parameters: [{ name: "timeperiod", default: 20 }],
                },
              ],
            },
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          data: {
            indicators: [
              {
                abbreviation: "RSI",
                chinese_name: "相对强弱指标",
                category: "momentum",
                panel_type: "sub",
                description: "动量观察",
                parameters: [{ name: "timeperiod", default: 14 }],
              },
            ],
          },
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    const indicatorPanel = page.locator("#data-analysis-panel-indicators")
    await expect(indicatorPanel).toBeVisible()
    const indicatorCard = indicatorPanel.locator(".indicator-card").filter({ hasText: "移动平均线" }).first()
    await expect(indicatorCard).toBeVisible()
    await indicatorCard.click()

    const editorPanel = page.locator("#data-analysis-panel-editor")
    await expect(editorPanel).toContainText("selected indicator")
    await expect(editorPanel).toContainText("移动平均线")
    await expect(editorPanel).toContainText("MA")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(editorPanel).not.toContainText("selected indicator")
    await expect(editorPanel).not.toContainText("移动平均线")
    await expect(editorPanel).toContainText("从指标库选择一个指标")
  })

  test("data indicator shows selected stock context after results-row click", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await page.getByRole("button", { name: "执行筛选" }).click()
    await expect(page.locator("#data-analysis-panel-results")).toBeVisible()
    const resultRow = page.getByRole("row", { name: /600519\s+贵州茅台/ }).first()
    await expect(resultRow).toBeVisible()
    await resultRow.click()
    await expect(page.locator(".context-panel")).toContainText("selected stock")
    await expect(page.locator(".context-panel")).toContainText("贵州茅台")
    await expect(page.locator(".context-panel")).toContainText("600519")
  })

  test("data indicator clears the previous selected stock context when a verified refresh replaces the screening universe", async ({ page }) => {
    await stubPhase2Apis(page)

    let stocksBasicRequestCount = 0
    await page.route("**/api/v1/data/stocks/basic**", async (route) => {
      stocksBasicRequestCount += 1

      if (stocksBasicRequestCount === 1) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            success: true,
            request_id: "req-phase2-indicator-stock-context-success",
            data: [
              {
                symbol: "600519",
                name: "贵州茅台",
                price: 1688.2,
                change_pct: 1.42,
                volume: 320000,
                turnover: 920000000,
                pe: 28.6,
                market_cap: 2120000000000,
              },
              {
                symbol: "300750",
                name: "宁德时代",
                price: 212.6,
                change_pct: -0.73,
                volume: 580000,
                turnover: 460000000,
                pe: 24.1,
                market_cap: 980000000000,
              },
            ],
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          success: true,
          request_id: "req-phase2-indicator-stock-context-refresh",
          data: [
            {
              symbol: "002594",
              name: "比亚迪",
              price: 258.3,
              change_pct: 2.11,
              volume: 410000,
              turnover: 510000000,
              pe: 22.8,
              market_cap: 760000000000,
            },
          ],
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await page.getByRole("button", { name: "执行筛选" }).click()
    await expect(page.locator("#data-analysis-panel-results")).toBeVisible()

    const resultRow = page.getByRole("row", { name: /600519\s+贵州茅台/ }).first()
    await expect(resultRow).toBeVisible()
    await resultRow.click()

    const selectedStockPanel = page.locator(".context-panel").filter({ hasText: "selected stock" })
    await expect(selectedStockPanel).toContainText("贵州茅台")
    await expect(selectedStockPanel).toContainText("600519")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator("#data-analysis-panel-results")).toContainText("比亚迪")
    await expect(selectedStockPanel).toHaveCount(0)
    await expect(page.locator(".tab-content")).not.toContainText("贵州茅台")
  })

  test("data indicator shows error state when registry load fails", async ({ page }) => {
    await stubPhase2Apis(page, { failIndicatorRegistry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await expect(page.getByText("数据分析中心")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("数据分析数据加载失败", { timeout: 20000 })
    await expect(page.locator(".header-meta")).toContainText("STATUS: 同步异常")
    await expect(page.locator(".header-meta")).toContainText("UPDATED: --")
    await expect(page.locator(".stats-overview .artdeco-stat-value")).toHaveText(["--", "--", "--", "--", "--"])
    await expect(page.locator(".stats-overview .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-overview")).not.toContainText("+0%")
    await expect(page.locator(".stats-overview")).not.toContainText("0.00")
    await expect(page.getByRole("button", { name: "重新加载" })).toBeVisible()
  })

  test("data indicator does not promote local screening actions into verified summary truth after the first load failed", async ({ page }) => {
    await stubPhase2Apis(page, { failIndicatorRegistry: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".artdeco-data-analysis")).toBeVisible()
    await expect(page.locator(".state-panel")).toContainText("数据分析数据加载失败", { timeout: 20000 })
    await expect(page.locator(".header-meta")).toContainText("STATUS: 同步异常")
    await expect(page.locator(".header-meta")).toContainText("UPDATED: --")
    await expect(page.locator(".stats-overview .artdeco-stat-value")).toHaveText(["--", "--", "--", "--", "--"])

    await page.getByRole("button", { name: "执行筛选" }).click()

    await expect(page.locator(".header-meta")).toContainText("STATUS: 同步异常")
    await expect(page.locator(".header-meta")).toContainText("UPDATED: --")
    await expect(page.locator(".stats-overview .artdeco-stat-value")).toHaveText(["--", "--", "--", "--", "--"])
    await expect(page.locator(".state-panel")).toContainText("数据分析数据加载失败")
    await expect(page.locator(".tab-content")).not.toContainText("筛选已就绪")
    await expect(page.locator("#data-analysis-panel-results")).toHaveCount(0)
  })

  test("data indicator keeps the last verified updated-at metadata and visible indicator workspace when refresh fails", async ({ page }) => {
    await stubPhase2Apis(page, { failIndicatorRegistryRefreshOnly: true })

    await page.goto(`${FRONTEND_BASE_URL}/data/indicator`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".artdeco-data-analysis")).toBeVisible()
    await expect(page.getByText("数据分析中心")).toBeVisible()
    await expect(page.locator("#data-analysis-panel-indicators")).toBeVisible()
    await expect(page.locator("#data-analysis-panel-indicators")).toContainText("移动平均线")

    const initialHeaderMeta = (await page.locator(".header-meta").textContent()) ?? ""
    const initialUpdatedMatch = initialHeaderMeta.match(/UPDATED:\s*(.+)$/)
    const initialUpdatedValue = initialUpdatedMatch?.[1]?.trim() ?? ""

    expect(initialUpdatedValue.length).toBeGreaterThan(0)
    expect(initialUpdatedValue).not.toBe("--")

    await page.getByRole("button", { name: "刷新数据" }).click()

    await expect(page.locator(".warning-panel")).toContainText("部分刷新失败", { timeout: 20000 })
    await expect(page.locator(".warning-panel")).toContainText("当前仍显示上次成功同步的数据分析快照。")
    await expect(page.locator(".header-meta")).toContainText(`UPDATED: ${initialUpdatedValue}`)
    await expect(page.locator(".header-meta")).toContainText("STATUS: 刷新异常")
    await expect(page.locator("#data-analysis-panel-indicators")).toContainText("移动平均线")
    await expect(page.locator(".tab-content")).not.toContainText("数据分析数据加载失败")
  })

  test("watchlist manage supports create and remove flows under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-manager")).toBeVisible()
    await expect(page.getByText("组合持仓明细")).toBeVisible()
    await expect(page.getByRole("button", { name: "导入" })).toBeVisible()
    await expect(page.getByRole("button", { name: "导出" })).toBeVisible()
    await expect(page.locator(".watchlist-tabs")).toContainText("核心组合")
    await expect(page.locator(".overview-grid .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".overview-grid")).not.toContainText("+0%")
    await expect(page.locator(".overview-grid")).not.toContainText("2.00")
    await expect(page.locator(".overview-grid")).not.toContainText("1.00")

    page.once("dialog", async (dialog) => {
      await dialog.accept("短线观察")
    })
    await page.locator(".add-list-btn").click()
    await expect(page.locator(".watchlist-tabs")).toContainText("短线观察")

    const firstStockRow = page.getByRole("row", { name: /600519\s+贵州茅台/ })
    await firstStockRow.getByRole("button", { name: "删除" }).click()
    await expect(page.locator(".watchlist-manager")).not.toContainText("贵州茅台")
  })

  test("watchlist manage keeps summary placeholders honest when the first watchlist payload reports failure", async ({ page }) => {
    await stubPhase2Apis(page, { failWatchlists: true })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-manager")).toBeVisible()
    await expect(page.locator(".overview-grid .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".overview-grid .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".overview-grid")).not.toContainText("+0%")
    await expect(page.locator(".overview-grid")).not.toContainText("0.00")
    await expect(page.locator(".state-panel")).toContainText("自选列表加载失败")
    await expect(page.locator(".watchlist-manager")).not.toContainText("暂无自选组合")
  })

  test("watchlist manage keeps stock summary cards pending while the first stock slice is still unresolved", async ({ page }) => {
    await stubPhase2Apis(page, { hangWatchlistStocks: true })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-manager")).toBeVisible()
    await expect(page.locator(".overview-grid .artdeco-stat-value")).toHaveText(["2", "--", "--", "--"])
    await expect(page.locator(".overview-grid .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".state-panel")).toContainText("自选列表同步中")
    await expect(page.locator(".watchlist-tabs")).toContainText("核心组合")
    await expect(page.locator(".watchlist-manager")).not.toContainText("当前股票数0")
  })

  test("watchlist manage does not keep previous rows visible while a newly selected watchlist is still unresolved", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.context().route("**/api/v1/monitoring/watchlists/wl-growth/stocks**", async () => {
      return
    })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-manager")).toBeVisible()
    await expect(page.locator(".watchlist-manager")).toContainText("贵州茅台")

    await page.getByRole("button", { name: /成长跟踪/ }).click()

    await expect(page.locator(".watchlist-tab.active")).toContainText("成长跟踪")
    await expect(page.locator(".overview-grid .artdeco-stat-value")).toHaveText(["2", "--", "--", "--"])
    await expect(page.locator(".state-panel")).toContainText("自选列表同步中")
    await expect(page.locator("tbody tr")).toHaveCount(0)
    await expect(page.locator(".watchlist-manager")).not.toContainText("贵州茅台")
  })

  test("watchlist manage keeps the last verified tab and rows when a later watchlist stock refresh fails", async ({ page }) => {
    await stubPhase2Apis(page, { failWatchlistStocksRefreshOnly: true })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-manager")).toBeVisible()
    await expect(page.locator(".watchlist-manager")).toContainText("贵州茅台")

    await page.getByRole("button", { name: /成长跟踪/ }).click()

    await expect(page.locator(".watchlist-tab.active")).toContainText("核心组合")
    await expect(page.locator(".state-panel")).toContainText("自选列表刷新异常")
    await expect(page.locator(".state-panel")).toContainText("当前仍显示上次成功同步的自选组合快照。")
    await expect(page.locator(".watchlist-manager")).toContainText("贵州茅台")
    await expect(page.locator(".watchlist-manager")).not.toContainText("比亚迪")
  })

  test("watchlist signals renders timeline and stats under mock data", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/signals`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".strategy-signals-tab")).toBeVisible()
    await expect(page.getByText("自选信号雷达")).toBeVisible()
    await expect(page.getByText("自选信号时间轴")).toBeVisible()
    await expect(page.getByText("当前复用全局交易信号流，自选组合联动与范围过滤待接入。")).toBeVisible()
    await expect(page.getByText("策略信号工作台")).toHaveCount(0)
    await expect(page.getByRole("button", { name: "刷新信号" })).toBeVisible()
    await expect(page.locator(".signals-timeline")).toContainText("贵州茅台")
    await expect(page.locator(".signals-timeline")).toContainText("宁德时代")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID:")
  })

  test("watchlist screener applies draft filters only after explicit apply", async ({ page }) => {
    await stubPhase2Apis(page)

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/screener`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-screener")).toBeVisible()
    await expect(page.getByText("策略选股工作台")).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["3", "3", "2", "6.30亿"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.getByText("筛选条件与候选名单")).toBeVisible()
    await expect(page.getByText("命中结果")).toBeVisible()
    const applyButton = page.getByRole("button", { name: "应用筛选" })
    await expect(applyButton).toBeVisible()
    await expect(applyButton).toBeDisabled()
    await expect(page.getByRole("button", { name: "清空条件" })).toBeVisible()
    await expect(page.locator(".artdeco-table")).toContainText("贵州茅台")

    const filterSummary = page.locator(".filter-summary")
    await expect(filterSummary).toContainText("MATCHED: 3")

    const priceMinInput = page.locator(".filter-card").first().locator("input").first()
    await priceMinInput.fill("1000")
    await expect(filterSummary).toContainText("PENDING CHANGES")
    await expect(applyButton).toBeEnabled()
    await expect(filterSummary).toContainText("MATCHED: 3")

    await applyButton.click()
    await expect(filterSummary).not.toContainText("PENDING CHANGES")
    await expect(filterSummary).toContainText("MATCHED: 1")
    await expect(page.locator(".state-banner")).toContainText("本次筛选命中 1 只股票")
    await expect(page.locator(".artdeco-table")).toContainText("贵州茅台")
    await expect(page.locator(".artdeco-table")).not.toContainText("宁德时代")
  })

  test("watchlist screener keeps honest pending placeholders while the first stock-universe payload is still unresolved", async ({ page }) => {
    await stubPhase2Apis(page, { hangStocksBasic: true })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/screener`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-screener")).toBeVisible()
    await expect(page.getByText("策略选股工作台")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("UNIVERSE: --")
    await expect(page.locator(".hero-meta")).toContainText("FILTERS: 0")
    await expect(page.locator(".hero-meta")).toContainText("RUNS: 0")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".state-panel")).toContainText("股票池同步中")
  })

  test("watchlist screener does not leak failed request ids or fake an empty universe when the first stock-universe payload reports failure", async ({ page }) => {
    await stubPhase2Apis(page, { failStocksBasic: true })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/screener`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-screener")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase2-stocks-first-fail")
    await expect(page.locator(".hero-meta")).toContainText("UNIVERSE: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".state-panel")).toContainText("股票池加载失败")
    await expect(page.locator(".content-shell")).not.toContainText("暂无可筛选标的")
  })

  test("watchlist screener keeps the last verified request id and rows when refresh fails after success", async ({ page }) => {
    await stubPhase2Apis(page, { failStocksBasicRefreshOnly: true })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/screener`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".watchlist-screener")).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase2-stocks-success")
    await expect(page.locator(".artdeco-table")).toContainText("贵州茅台")

    await page.getByRole("button", { name: "刷新股票池" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ: e2e-phase2-stocks-success")
    await expect(page.locator(".hero-meta")).not.toContainText("e2e-phase2-stocks-refresh-fail")
    await expect(page.locator(".state-banner")).toContainText("当前仍展示上次成功同步的股票池")
    await expect(page.locator(".artdeco-table")).toContainText("贵州茅台")
  })
})
