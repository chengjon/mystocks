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

type StrategyRecord = {
  strategy_id: number
  strategy_name: string
  strategy_type: string
  description: string
  status: string
  updated_at: string
  parameters?: Array<{ name: string; value: unknown; data_type: string }>
}

type TradeSignalRecord = {
  symbol: string
  name: string
  type: "BUY" | "SELL" | "HOLD"
  price: number
  time: string
  strategy: string
}

type Phase3State = {
  strategies: StrategyRecord[]
  signals: TradeSignalRecord[]
  positionsPayload: Record<string, unknown>
  tradesPayload: Record<string, unknown>
  tradingRunning: boolean
  backtestStatusCalls: number
  unhandledRequests: string[]
}

const STRATEGY_ROWS: StrategyRecord[] = [
  {
    strategy_id: 101,
    strategy_name: "Momentum Alpha",
    strategy_type: "momentum",
    description: "northbound momentum",
    status: "active",
    updated_at: "2026-04-03T09:30:00Z",
    parameters: [
      { name: "lookback", value: 20, data_type: "number" },
      { name: "risk_limit", value: 0.05, data_type: "number" },
    ],
  },
  {
    strategy_id: 102,
    strategy_name: "Reversion Beta",
    strategy_type: "mean_reversion",
    description: "pullback re-entry",
    status: "paused",
    updated_at: "2026-04-03T09:45:00Z",
    parameters: [
      { name: "z_score", value: 2.1, data_type: "number" },
      { name: "holding_days", value: 5, data_type: "number" },
    ],
  },
]

const SIGNAL_ROWS: TradeSignalRecord[] = [
  {
    symbol: "600519",
    name: "贵州茅台",
    type: "BUY",
    price: 1688.2,
    time: "09:35:12",
    strategy: "Momentum Alpha",
  },
  {
    symbol: "300750",
    name: "宁德时代",
    type: "SELL",
    price: 212.6,
    time: "10:02:45",
    strategy: "Reversion Beta",
  },
  {
    symbol: "002594",
    name: "比亚迪",
    type: "HOLD",
    price: 258.3,
    time: "10:18:08",
    strategy: "Momentum Alpha",
  },
]

const POSITIONS_PAYLOAD = {
  positions: [
    {
      symbol: "600519",
      symbol_name: "贵州茅台",
      quantity: 120,
      cost_price: 1660.5,
      current_price: 1688.2,
      market_value: 202584,
      profit_loss: 3324,
      profit_loss_percent: 1.67,
    },
    {
      symbol: "300750",
      symbol_name: "宁德时代",
      quantity: 800,
      cost_price: 208.2,
      current_price: 212.6,
      market_value: 170080,
      profit_loss: 3520,
      profit_loss_percent: 2.11,
    },
  ],
  total_market_value: 372664,
  total_profit_loss: 6844,
  total_profit_loss_percent: 1.87,
}

const TRADES_PAYLOAD = {
  trades: [
    {
      trade_id: "trade-001",
      symbol: "600519",
      direction: "buy",
      price: 1688.2,
      quantity: 20,
      amount: 33764,
      commission: 16.8,
      trade_time: "2026-04-03T09:41:05Z",
      status: "completed",
    },
    {
      trade_id: "trade-002",
      symbol: "300750",
      direction: "sell",
      price: 212.6,
      quantity: 50,
      amount: 10630,
      commission: 5.3,
      trade_time: "2026-04-03T10:18:40Z",
      status: "pending",
    },
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
    timestamp: "2026-04-03T00:00:00Z",
    request_id: "req-phase3-default",
    ...(overrides ?? {}),
  }
}

function createPhase3State(): Phase3State {
  return {
    strategies: STRATEGY_ROWS.map((row) => ({
      ...row,
      parameters: row.parameters?.map((parameter) => ({ ...parameter })),
    })),
    signals: SIGNAL_ROWS.map((row) => ({ ...row })),
    positionsPayload: JSON.parse(JSON.stringify(POSITIONS_PAYLOAD)) as Record<string, unknown>,
    tradesPayload: JSON.parse(JSON.stringify(TRADES_PAYLOAD)) as Record<string, unknown>,
    tradingRunning: false,
    backtestStatusCalls: 0,
    unhandledRequests: [],
  }
}

function buildTradingStatusPayload(running: boolean) {
  if (running) {
    return {
      session_id: "mock-session-running",
      current_drawdown: 0.018,
      daily_pnl: 3450.5,
      total_pnl: 12890.4,
      active_positions: 2,
      win_rate: 0.67,
    }
  }

  return {
    session_id: "mock-session-idle",
    current_drawdown: 0,
    daily_pnl: 0,
    total_pnl: 0,
    active_positions: 0,
    win_rate: 0,
  }
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript(({ user }) => {
    const token = "e2e-phase3-token"
    localStorage.setItem("auth_token", token)
    localStorage.setItem("auth_user", JSON.stringify(user))
    localStorage.setItem("token", token)
    localStorage.setItem("user", JSON.stringify(user))
    localStorage.setItem("access_token", token)
  }, { user: E2E_USER })
}

async function setupPhase3Mock(page: Page): Promise<Phase3State> {
  const state = createPhase3State()
  await page.setViewportSize({ width: 1440, height: 900 })
  await seedAuth(page)
  await stubPhase3Apis(page, state)
  return state
}

async function stubPhase3Apis(page: Page, state: Phase3State): Promise<void> {
  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
    const request = route.request()
    const normalizedPath = normalizePathname(request.url())
    const method = request.method()

    if (normalizedPath === "/health/ready") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "ready" }, { request_id: "req-phase3-ready" })),
      })
      return
    }

    if (normalizedPath === "/health") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "healthy" }, { request_id: "req-phase3-health" })),
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
              csrf_token: "e2e-phase3-csrf",
              token_type: "bearer",
              expires_in: 3600,
            },
            { request_id: "req-phase3-csrf" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/strategy/strategies" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategies",
          "x-process-time": "36ms",
        },
        body: JSON.stringify(buildUnifiedResponse(state.strategies, { request_id: "req-phase3-strategies" })),
      })
      return
    }

    if (normalizedPath === "/v1/trade/signals" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-signals",
          "x-process-time": "42ms",
        },
        body: JSON.stringify(buildUnifiedResponse(state.signals, { request_id: "req-phase3-signals" })),
      })
      return
    }

    if (normalizedPath === "/v1/trade/positions" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-positions",
          "x-process-time": "31ms",
        },
        body: JSON.stringify(buildUnifiedResponse(state.positionsPayload, { request_id: "req-phase3-positions" })),
      })
      return
    }

    if (normalizedPath === "/v1/trade/trades" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-trades",
          "x-process-time": "29ms",
        },
        body: JSON.stringify(buildUnifiedResponse(state.tradesPayload, { request_id: "req-phase3-trades" })),
      })
      return
    }

    if (normalizedPath === "/v1/strategy/backtest/run" && method === "POST") {
      await route.fulfill({
        status: 202,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              task_id: "bt-phase3-101",
              status: "completed",
              message: "回测任务已完成",
            },
            { request_id: "req-phase3-backtest-run" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/strategy/backtest/status/bt-phase3-101" && method === "GET") {
      state.backtestStatusCalls += 1
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              task_id: "bt-phase3-101",
              status: "completed",
              message: "回测任务已完成",
            },
            { request_id: "req-phase3-backtest-status" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/v1/strategy/backtest/results/bt-phase3-101" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              total_return: 0.186,
              start_date: "2025-01-01",
              end_date: "2025-12-31",
              completed_at: "2026-04-03T10:00:00Z",
              performance: {
                max_drawdown: 0.064,
              },
            },
            { request_id: "req-phase3-backtest-result" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/gpu/status" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              gpus: [
                {
                  name: "NVIDIA RTX 6000 Ada",
                  driver_version: "550.54.15",
                  gpu_utilization: 64,
                  memory_total: 49140,
                  memory_used: 12288,
                  memory_utilization: 25,
                  temperature: 58,
                  sm_clock: 2520,
                  memory_clock: 1313,
                  fan_speed: 44,
                  power_usage: 212,
                },
              ],
            },
            { request_id: "req-phase3-gpu-status" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/gpu/performance" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              metrics: [
                {
                  matrix_speedup: 57,
                  matrix_gflops: 912,
                },
              ],
            },
            { request_id: "req-phase3-gpu-performance" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/trading/status" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(buildTradingStatusPayload(state.tradingRunning), { request_id: "req-phase3-terminal-status" })
        ),
      })
      return
    }

    if (normalizedPath === "/trading/strategies/performance" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              {
                id: "strat-101",
                name: "Momentum Alpha",
                strategy_name: "Momentum Alpha",
                status: "active",
                performance_metrics: {
                  expected_return: 0.182,
                  sharpe_ratio: 1.94,
                  win_rate: 0.67,
                },
              },
            ],
            { request_id: "req-phase3-terminal-performance" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/trading/market/snapshot" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              timestamp: "2026-04-03T10:15:00Z",
              data: {
                "600519": { price: 1688.2, change: 12.4, change_percent: 0.74 },
                "300750": { price: 212.6, change: -1.3, change_percent: -0.61 },
              },
            },
            { request_id: "req-phase3-terminal-market" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/trading/risk/metrics" && method === "GET") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              risk_status: "normal",
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              active_positions: 2,
              last_updated: "2026-04-03T10:15:00Z",
            },
            { request_id: "req-phase3-terminal-risk" }
          )
        ),
      })
      return
    }

    if (normalizedPath === "/trading/start" && method === "POST") {
      state.tradingRunning = true
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "started" }, { request_id: "req-phase3-terminal-start" })),
      })
      return
    }

    if (normalizedPath === "/trading/stop" && method === "POST") {
      state.tradingRunning = false
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(buildUnifiedResponse({ status: "stopped" }, { request_id: "req-phase3-terminal-stop" })),
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
        message: `Unhandled phase3 mock route: ${method} ${normalizedPath}`,
      }),
    })
  })
}

test.describe("Phase 3 Mainline Matrix", () => {
  test.describe.configure({ timeout: 180000 })

  test("Strategy-Repo renders strategy repository shell and actions", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByText("策略仓库工作台").first()).toBeVisible()
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(2)
    await expect(page.locator(".strategy-table")).toContainText("Momentum Alpha")
    await expect(page.getByRole("button", { name: "新建策略" }).first()).toBeVisible()
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Parameters renders parameter cards with strategy context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/parameters?strategyId=101`)

    await expect(page.getByText("策略参数工作台").first()).toBeVisible()
    await expect(page.locator(".strategy-card")).toHaveCount(1)
    await expect(page.locator(".strategy-card").first()).toContainText("Momentum Alpha")
    await expect(page.locator(".param-item")).toHaveCount(2)
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Signals renders live signal timeline", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals`)

    await expect(page.getByText("策略信号工作台").first()).toBeVisible()
    await expect(page.locator(".signal-item")).toHaveCount(3)
    await expect(page.locator(".signals-timeline")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest runs mocked backtest chain into result sync", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "启动回测" }).click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")
    await expect(page.locator(".progress-panel")).toContainText("100%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-GPU consumes mocked GPU status and performance snapshots", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/gpu`)

    await expect(page.getByRole("heading", { name: "GPU 加速回测" })).toBeVisible()
    await page.getByRole("button", { name: "刷新" }).click()
    await expect(page.locator(".gpu-availability")).toContainText("NVIDIA RTX 6000 Ada")
    await expect(page.locator(".performance-card")).toContainText("57x")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Opt renders optimization candidates and writeback controls", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".optimization-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".optimization-table")).toContainText("Momentum Alpha")
    await expect(page.locator(".writeback-cell")).toContainText("参数")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Pos renders mocked position ledger via strategy route", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/pos`)

    await expect(page.getByText("持仓工作台").first()).toBeVisible()
    await expect(page.locator(".artdeco-trading-positions__row")).toHaveCount(2)
    await expect(page.locator(".artdeco-trading-positions")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Positions renders mocked position ledger via trade route", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/positions`)

    await expect(page.getByText("持仓工作台").first()).toBeVisible()
    await expect(page.locator(".artdeco-trading-positions__row")).toHaveCount(2)
    await expect(page.locator(".artdeco-trading-positions")).toContainText("宁德时代")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Terminal renders read chains and supports start action", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/terminal`)

    await expect(page.locator(".page-title")).toContainText("实时交易监控仪表板")
    await expect(page.locator(".strategy-performance")).toContainText("Momentum Alpha")
    await page.getByRole("button", { name: "启动交易" }).click()
    await expect(page.getByRole("button", { name: "停止交易" })).toBeVisible()
    await expect(page.locator(".trading-details")).toContainText("mock-session-running")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Signals renders mocked signal execution workspace", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/signals`)

    await expect(page.getByText("交易信号工作台").first()).toBeVisible()
    await expect(page.locator(".signals-view")).toContainText("贵州茅台")
    await expect(page.locator(".signals-view")).toContainText("实时交易信号")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Portfolio renders mocked portfolio overview", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`)

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".portfolio-overview-tab")).toContainText("Top Positions")
    await expect(page.locator(".portfolio-overview-tab")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-History renders mocked trade ledger", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/history`)

    await expect(page.getByText("交易历史工作台").first()).toBeVisible()
    await expect(page.locator(".artdeco-trading-history__row")).toHaveCount(2)
    await expect(page.locator(".artdeco-trading-history")).toContainText("600519")
    await expect(page.locator(".artdeco-trading-history")).toContainText("已成交")
    expect(state.unhandledRequests).toEqual([])
  })
})
