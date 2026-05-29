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
  hangStrategies: boolean
  hangSignals: boolean
  positionsPayload: Record<string, unknown>
  hangPositions: boolean
  tradesPayload: Record<string, unknown>
  tradesRequestCount: number
  failTradesRefreshAfterFirst: boolean
  hangReconciliationAccountId: string | null
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

const POSITIONS_ATTRIBUTION_PAYLOAD = {
  analysis_date: "2026-04-03",
  snapshot_meta: {
    analysis_date: "2026-04-03",
    constituent_count: 2,
    total_market_value: 372664,
    total_return: 0.0187,
    stale: false,
  },
  brinson: {
    allocation_effect: 0.009,
    selection_effect: 0.014,
    interaction_effect: -0.002,
    industry_breakdown: {
      消费: {
        portfolio_weight: 0.54,
        benchmark_weight: 0.4,
        portfolio_return: 0.017,
        benchmark_return: 0.01,
        allocation_effect: 0.004,
        selection_effect: 0.006,
        interaction_effect: 0.001,
      },
    },
  },
  factor_attribution: {
    factor_exposures: {
      value: {
        portfolio_exposure: 0.35,
        benchmark_exposure: 0.18,
        active_exposure: 0.17,
      },
    },
    factor_contributions: { value: 0.011 },
    specific_return: 0.005,
  },
  top_contributors: [{ symbol: "600519", industry: "消费", weight: 0.54, return_rate: 0.017, contribution_value: 0.009 }],
  top_detractors: [],
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

const RECONCILIATION_ACCOUNTS = [
  { account_id: "backtest:7", label: "Backtest #7", account_type: "backtest" },
  { account_id: "backtest:8", label: "Backtest #8", account_type: "backtest" },
]

const RECONCILIATION_STATEMENTS_BY_ACCOUNT: Record<string, Record<string, unknown>> = {
  "backtest:7": {
    status: "available",
    endpoint: "trade",
    resource: "reconciliation_statements",
    account_id: "backtest:7",
    items: [
      {
        account_id: "backtest:7",
        trade_id: "101",
        order_id: "backtest-7-101",
        symbol: "600519.SH",
        direction: "buy",
        trade_time: "2026-05-06T09:31:00",
        price: 1750,
        quantity: 100,
        amount: 175000,
        commission: 52.5,
      },
    ],
    summary: {
      total_count: 1,
      total_amount: 175000,
      total_commission: 52.5,
    },
    total_count: 1,
    page: 1,
    page_size: 20,
    source: "backtest_trades",
  },
  "backtest:8": {
    status: "available",
    endpoint: "trade",
    resource: "reconciliation_statements",
    account_id: "backtest:8",
    items: [
      {
        account_id: "backtest:8",
        trade_id: "202",
        order_id: "backtest-8-202",
        symbol: "300750.SZ",
        direction: "sell",
        trade_time: "2026-05-06T10:15:00",
        price: 212.5,
        quantity: 50,
        amount: 10625,
        commission: 6.2,
      },
    ],
    summary: {
      total_count: 1,
      total_amount: 10625,
      total_commission: 6.2,
    },
    total_count: 1,
    page: 1,
    page_size: 20,
    source: "backtest_trades",
  },
}

const RECONCILIATION_RESULTS_BY_ACCOUNT: Record<string, Record<string, unknown>> = {
  "backtest:7": {
    status: "available",
    endpoint: "trade",
    resource: "reconciliation_results",
    account_id: "backtest:7",
    import_batch_id: "batch-7",
    items: [
      {
        match_status: "matched",
        internal_row: {
          account_id: "backtest:7",
          trade_id: "101",
          order_id: "backtest-7-101",
          symbol: "600519.SH",
          direction: "buy",
          trade_time: "2026-05-06T09:31:00",
          price: 1750,
          quantity: 100,
          amount: 175000,
          commission: 52.5,
        },
        broker_row: {
          account_id: "backtest:7",
          trade_id: "101",
          order_id: "backtest-7-101",
          symbol: "600519.SH",
          direction: "buy",
          trade_time: "2026-05-06T09:31:00",
          price: 1750,
          quantity: 100,
          amount: 175000,
          commission: 52.5,
          source_type: "miniqmt",
          raw_row_number: 2,
        },
        mismatch_fields: [],
      },
      {
        match_status: "mismatched",
        internal_row: {
          account_id: "backtest:7",
          trade_id: "102",
          order_id: "backtest-7-102",
          symbol: "601318.SH",
          direction: "sell",
          trade_time: "2026-05-06T10:01:00",
          price: 55.5,
          quantity: 300,
          amount: 16650,
          commission: 5.1,
        },
        broker_row: {
          account_id: "backtest:7",
          trade_id: "102-broker",
          order_id: "backtest-7-102",
          symbol: "601318.SH",
          direction: "sell",
          trade_time: "2026-05-06T10:01:00",
          price: 55.5,
          quantity: 300,
          amount: 16660,
          commission: 5.5,
          source_type: "miniqmt",
          raw_row_number: 3,
        },
        mismatch_fields: ["amount", "commission"],
      },
      {
        match_status: "missing_broker_record",
        internal_row: {
          account_id: "backtest:7",
          trade_id: "103",
          order_id: "backtest-7-103",
          symbol: "000001.SZ",
          direction: "buy",
          trade_time: "2026-05-06T10:21:00",
          price: 12.5,
          quantity: 1000,
          amount: 12500,
          commission: 4.1,
        },
        broker_row: null,
        mismatch_fields: [],
      },
    ],
    total_count: 3,
    page: 1,
    page_size: 20,
    source: "backtest_trades",
    match_status: null,
  },
  "backtest:8": {
    status: "available",
    endpoint: "trade",
    resource: "reconciliation_results",
    account_id: "backtest:8",
    import_batch_id: "batch-7",
    items: [],
    total_count: 0,
    page: 1,
    page_size: 20,
    source: "backtest_trades",
    match_status: null,
  },
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
    hangStrategies: false,
    hangSignals: false,
    positionsPayload: JSON.parse(JSON.stringify(POSITIONS_PAYLOAD)) as Record<string, unknown>,
    hangPositions: false,
    tradesPayload: JSON.parse(JSON.stringify(TRADES_PAYLOAD)) as Record<string, unknown>,
    tradesRequestCount: 0,
    failTradesRefreshAfterFirst: false,
    hangReconciliationAccountId: null,
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

    if (normalizedPath === "/csrf-token" || normalizedPath === "/auth/csrf") {
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
      if (state.hangStrategies) {
        return
      }

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
      if (state.hangSignals) {
        return
      }

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
      if (state.hangPositions) {
        return
      }

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

    if (normalizedPath === "/v1/positions/attribution" && method === "GET") {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-positions-attribution",
          "x-process-time": "34ms",
        },
        body: JSON.stringify(
          buildUnifiedResponse(POSITIONS_ATTRIBUTION_PAYLOAD, { request_id: "req-phase3-positions-attribution" }),
        ),
      })
      return
    }

    if (normalizedPath === "/v1/trade/trades" && method === "GET") {
      state.tradesRequestCount += 1

      if (state.failTradesRefreshAfterFirst && state.tradesRequestCount > 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-trades-refresh-fail",
          },
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "交易历史接口失败",
            data: null,
            timestamp: "2026-04-03T00:00:00Z",
            request_id: "req-phase3-trades-refresh-fail",
          }),
        })
        return
      }

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

    if (
      (normalizedPath.startsWith("/v1/trade/reconciliation/accounts") ||
        normalizedPath.startsWith("/trade/reconciliation/accounts")) &&
      method === "GET"
    ) {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-reconciliation-accounts",
        },
        body: JSON.stringify(
          buildUnifiedResponse({ items: RECONCILIATION_ACCOUNTS }, { request_id: "req-phase3-reconciliation-accounts" }),
        ),
      })
      return
    }

    if (
      (normalizedPath.startsWith("/v1/trade/reconciliation/statements") ||
        normalizedPath.startsWith("/trade/reconciliation/statements")) &&
      method === "GET"
    ) {
      const accountId = new URL(request.url()).searchParams.get("account_id") ?? "backtest:7"

      if (state.hangReconciliationAccountId === accountId) {
        await new Promise(() => {})
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": `req-phase3-reconciliation-statements-${accountId.replace(/[:]/g, "-")}`,
        },
        body: JSON.stringify(
          buildUnifiedResponse(RECONCILIATION_STATEMENTS_BY_ACCOUNT[accountId], {
            request_id: `req-phase3-reconciliation-statements-${accountId.replace(/[:]/g, "-")}`,
          }),
        ),
      })
      return
    }

    if (
      (normalizedPath.startsWith("/v1/trade/reconciliation/import") ||
        normalizedPath.startsWith("/trade/reconciliation/import")) &&
      method === "POST"
    ) {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-reconciliation-import",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              status: "available",
              endpoint: "trade",
              resource: "reconciliation_import_batch",
              import_batch_id: "batch-7",
              account_id: "backtest:7",
              source_type: "miniqmt",
              row_count: 3,
            },
            { request_id: "req-phase3-reconciliation-import" },
          ),
        ),
      })
      return
    }

    if (
      (normalizedPath.startsWith("/v1/trade/reconciliation/results") ||
        normalizedPath.startsWith("/trade/reconciliation/results")) &&
      method === "GET"
    ) {
      const accountId = new URL(request.url()).searchParams.get("account_id") ?? "backtest:7"

      if (state.hangReconciliationAccountId === accountId) {
        await new Promise(() => {})
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": `req-phase3-reconciliation-results-${accountId.replace(/[:]/g, "-")}`,
        },
        body: JSON.stringify(
          buildUnifiedResponse(RECONCILIATION_RESULTS_BY_ACCOUNT[accountId], {
            request_id: `req-phase3-reconciliation-results-${accountId.replace(/[:]/g, "-")}`,
          }),
        ),
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
  test.use({ serviceWorkers: "block" })

  test("Strategy-Repo renders strategy repository shell and actions", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByText("策略仓库工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["2", "1", "0", "全部状态"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("MATCHED: 2")
    await expect(page.locator(".content-shell-meta")).toContainText("PAGE: 1 / 1")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(2)
    await expect(page.locator(".strategy-table")).toContainText("Momentum Alpha")
    await expect(page.getByRole("button", { name: "新建策略" }).first()).toBeVisible()
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Repo does not present failed first-load repository tallies as faux zero metrics", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "strategy registry unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByText("策略仓库工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "全部状态"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("MATCHED: --")
    await expect(page.locator(".content-shell-meta")).toContainText("PAGE: -- / --")
    await expect(page.locator(".header-meta")).toContainText("MATCHED: --")
    await expect(page.locator(".header-meta")).toContainText("PAGE: -- / --")
    await expect(page.locator(".empty-state")).toContainText("REAL 请求失败，请稍后重试。")
    await expect(page.locator(".strategy-table")).toHaveCount(0)
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Repo keeps honest pending placeholders while the first repository payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.hangStrategies = true

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByText("策略仓库工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "全部状态"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("MATCHED: --")
    await expect(page.locator(".content-shell-meta")).toContainText("PAGE: -- / --")
    await expect(page.locator(".header-meta")).toContainText("MATCHED: --")
    await expect(page.locator(".header-meta")).toContainText("PAGE: -- / --")
    await expect(page.locator(".empty-state")).toContainText("策略仓库同步中，正在等待真实策略返回。")
    await expect(page.locator(".strategy-management")).not.toContainText("REAL 数据为空，请先创建策略。")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Repo does not leak failed first-load repository request metadata before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      await route.fulfill({
        status: 500,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategy-repo-first-fail",
          "x-process-time": "77ms",
        },
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "strategy registry unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByText("策略仓库工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: N/A ms")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-strategy-repo-first-fail")
    await expect(page.locator(".strategy-management")).not.toContainText("req-phase3-strategy-repo-first-fail")
    await expect(page.locator(".strategy-management")).not.toContainText("77")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Repo keeps the last verified request provenance and visible rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let strategyRequestCount = 0

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      strategyRequestCount += 1

      if (strategyRequestCount > 1) {
        await route.fulfill({
          status: 500,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-strategy-repo-refresh-fail",
          },
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            message: "strategy repository refresh unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategy-repo-success",
          "x-process-time": "36ms",
        },
        body: JSON.stringify(buildUnifiedResponse(state.strategies, { request_id: "req-phase3-strategy-repo-success" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/repo`)

    await expect(page.getByText("策略仓库工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategy-repo-success")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 36.00 ms")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(2)

    await page.getByRole("button", { name: "刷新仓库" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategy-repo-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-strategy-repo-refresh-fail")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 36.00 ms")
    await expect(page.locator(".strategy-management")).toContainText("strategy repository refresh unavailable")
    await expect(page.locator(".strategy-management")).toContainText("当前仍显示上次成功同步的策略仓库快照")
    await expect(page.locator(".strategy-table tbody tr")).toHaveCount(2)
    await expect(page.locator(".strategy-table")).toContainText("Momentum Alpha")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Parameters renders parameter cards with strategy context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/parameters?strategyId=101`)

    await expect(page.getByText("策略参数工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["1", "2", "0", "101"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".strategy-card")).toHaveCount(1)
    await expect(page.locator(".strategy-card").first()).toContainText("Momentum Alpha")
    await expect(page.locator(".param-item")).toHaveCount(2)
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Parameters keeps honest placeholder cards when the first strategy payload fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      await route.fulfill({
        status: 500,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategy-parameters-first-fail",
        },
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "strategy registry unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/parameters?strategyId=101`)

    await expect(page.getByText("策略参数工作台").first()).toBeVisible()
    await expect(page.getByText("策略参数加载失败").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: N/A ms")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-strategy-parameters-first-fail")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "101"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".strategy-parameters-tab")).not.toContainText("req-phase3-strategy-parameters-first-fail")
    await expect(page.locator(".strategy-parameters-tab")).not.toContainText("48.50")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Parameters keeps the last verified request provenance and visible cards when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let strategyRequestCount = 0

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      strategyRequestCount += 1

      if (strategyRequestCount > 1) {
        await route.fulfill({
          status: 500,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-strategy-parameters-refresh-fail",
          },
          contentType: "application/json",
          body: JSON.stringify({
            success: false,
            message: "strategy parameters refresh unavailable",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategy-parameters-success",
          "x-process-time": "36ms",
        },
        body: JSON.stringify(buildUnifiedResponse(state.strategies, { request_id: "req-phase3-strategy-parameters-success" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/parameters?strategyId=101`)

    await expect(page.getByText("策略参数工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategy-parameters-success")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 36.00 ms")
    await expect(page.locator(".strategy-card")).toHaveCount(1)

    await page.getByRole("button", { name: "刷新参数" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategy-parameters-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-strategy-parameters-refresh-fail")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 36.00 ms")
    await expect(page.locator(".strategy-parameters-tab")).toContainText("获取策略参数失败")
    await expect(page.locator(".strategy-parameters-tab")).toContainText("当前仍显示上次成功同步的参数快照")
    await expect(page.locator(".strategy-card")).toHaveCount(1)
    await expect(page.locator(".strategy-card").first()).toContainText("Momentum Alpha")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Parameters does not leak a previous strategy snapshot after the route query switched to a new strategy without its own verified context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/parameters?strategyId=101`)

    await expect(page.getByText("策略参数工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategies")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 36.00 ms")
    await expect(page.locator(".strategy-card")).toHaveCount(1)
    await expect(page.locator(".strategy-card").first()).toContainText("Momentum Alpha")

    await page.evaluate(() => {
      window.history.pushState({}, "", "/strategy/parameters?strategyId=202")
      window.dispatchEvent(new PopStateEvent("popstate"))
    })

    await expect(page.locator(".hero-meta")).toContainText("FOCUS: 202")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: N/A ms")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "202"])
    await expect(page.locator(".strategy-card")).toHaveCount(0)
    await expect(page.locator(".strategy-grid")).toContainText("未找到策略 202 的参数配置")
    await expect(page.locator(".strategy-parameters-tab")).not.toContainText("Momentum Alpha")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Signals renders live signal timeline", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals`)

    await expect(page.getByText("策略信号工作台").first()).toBeVisible()
    await expect(page.locator(".signal-item")).toHaveCount(3)
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["3", "1", "1", "1"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".signals-timeline")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Signals keeps honest pending placeholders while the first signal payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.hangSignals = true

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals`)

    await expect(page.getByText("策略信号工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("COUNT: --")
    await expect(page.locator(".state-panel")).toContainText("策略信号同步中")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Signals does not swallow resolved first-load failure envelopes into faux empty signal truth", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/signals**", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-signals-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 500,
          message: "strategy signals unavailable",
          data: null,
          timestamp: "2026-04-03T00:00:00Z",
          request_id: "req-phase3-signals-fail",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals`)

    await expect(page.getByText("策略信号工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("COUNT: --")
    await expect(page.locator(".state-panel")).toContainText("策略信号加载失败")
    await expect(page.locator(".state-panel")).toContainText("strategy signals unavailable")
    await expect(page.locator(".strategy-signals-tab")).not.toContainText("当前暂无策略信号。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Signals keeps the last verified signal snapshot and request provenance when a refresh fails after success", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let signalRequestCount = 0

    await page.route("**/api/v1/trade/signals**", async (route) => {
      signalRequestCount += 1

      if (signalRequestCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-signals-success",
            "x-process-time": "42ms",
          },
          body: JSON.stringify(
            buildUnifiedResponse(
              [
                SIGNAL_ROWS[0],
                SIGNAL_ROWS[1],
              ],
              { request_id: "req-phase3-signals-success" }
            )
          ),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-signals-refresh-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 500,
          message: "strategy signals refresh unavailable",
          data: null,
          timestamp: "2026-04-03T00:00:00Z",
          request_id: "req-phase3-signals-refresh-fail",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals`)

    await expect(page.getByText("策略信号工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-signals-success")
    await expect(page.locator(".content-shell-meta")).toContainText("COUNT: 2")
    await expect(page.locator(".signal-item")).toHaveCount(2)
    await expect(page.locator(".signals-timeline")).toContainText("贵州茅台")
    await expect(page.locator(".signals-timeline")).toContainText("宁德时代")

    await page.getByRole("button", { name: "刷新信号" }).click()

    await expect(page.locator(".state-panel")).toContainText("策略信号刷新失败")
    await expect(page.locator(".state-panel")).toContainText("strategy signals refresh unavailable")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-signals-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-signals-refresh-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("COUNT: 2")
    await expect(page.locator(".signal-item")).toHaveCount(2)
    await expect(page.locator(".strategy-signals-tab")).toContainText("贵州茅台")
    await expect(page.locator(".strategy-signals-tab")).toContainText("宁德时代")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Signals does not leak a previous strategy snapshot after the route query switched to a new strategy without its own verified signal snapshot", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/signals**", async (route) => {
      const strategyId = new URL(route.request().url()).searchParams.get("strategy_id")

      if (strategyId === "202") {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-signals-202-fail",
          },
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "strategy 202 signals unavailable",
            data: null,
            timestamp: "2026-04-03T00:00:00Z",
            request_id: "req-phase3-signals-202-fail",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-signals-101",
          "x-process-time": "42ms",
        },
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              SIGNAL_ROWS[0],
              SIGNAL_ROWS[2],
            ],
            { request_id: "req-phase3-signals-101" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/signals?strategyId=101`)

    await expect(page.getByText("策略信号工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("FOCUS: 101")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-signals-101")
    await expect(page.locator(".content-shell-meta")).toContainText("COUNT: 2")
    await expect(page.locator(".signal-item")).toHaveCount(2)
    await expect(page.locator(".strategy-signals-tab")).toContainText("贵州茅台")
    await expect(page.locator(".strategy-signals-tab")).toContainText("比亚迪")

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/signals?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".hero-meta")).toContainText("FOCUS: 202")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".content-shell-meta")).toContainText("COUNT: --")
    await expect(page.locator(".state-panel")).toContainText("策略信号加载失败")
    await expect(page.locator(".state-panel")).toContainText("strategy 202 signals unavailable")
    await expect(page.locator(".signal-item")).toHaveCount(0)
    await expect(page.locator(".strategy-signals-tab")).not.toContainText("贵州茅台")
    await expect(page.locator(".strategy-signals-tab")).not.toContainText("比亚迪")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest runs mocked backtest chain into result sync", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await page.getByRole("button", { name: "启动回测" }).click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")
    await expect(page.locator(".progress-panel")).toContainText("100%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest keeps freshness metadata honest when the first strategy list load failed", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/strategies**", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-backtest-first-fail",
          "x-process-time": "41ms",
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 503,
            message: "strategy registry unavailable",
            request_id: "req-phase3-backtest-first-fail",
          }),
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest`, { waitUntil: "domcontentloaded" })

    await expect(page.locator(".backtest-analysis-page")).toBeVisible()
    await expect(page.locator(".backtest-header")).toContainText("最后更新")
    await expect(page.locator(".backtest-header")).toContainText("--")
    await expect(page.locator(".state-panel")).toContainText("回测上下文加载失败")
    await expect(page.locator(".state-panel")).toContainText("获取REAL策略数据失败，当前显示空态")
    await expect(page.locator(".backtest-analysis-page")).not.toContainText("req-phase3-backtest-first-fail")

    await page.getByRole("button", { name: "启动回测" }).first().click()

    await expect(page.locator(".state-banner")).toContainText("未绑定有效策略ID，无法启动真实回测。")
    await expect(page.locator(".backtest-header")).toContainText("最后更新")
    await expect(page.locator(".backtest-header")).toContainText("--")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest keeps UPDATED pinned to pending truth while the task is only queued", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/backtest/run", async (route) => {
      await route.fulfill({
        status: 202,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              task_id: "bt-phase3-queued-only",
              status: "queued",
              message: "回测任务已创建，进入排队",
            },
            { request_id: "req-phase3-backtest-queued-only" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    const verifiedFreshness = await page.locator(".backtest-header .status-block").nth(1).textContent()
    await page.waitForTimeout(1200)
    await page.getByRole("button", { name: "启动回测" }).first().click()

    await expect(page.locator(".state-banner")).toContainText("回测任务已创建，进入排队")
    await expect(page.locator(".backtest-header .status-block").nth(1)).toHaveText(verifiedFreshness ?? "")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest degrades report generation time when synced backtest results omitted completion metadata", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/backtest/results/bt-phase3-101", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              total_return: 0.186,
              start_date: "2025-01-01",
              end_date: "2025-12-31",
              performance: {
                max_drawdown: 0.064,
              },
            },
            { request_id: "req-phase3-backtest-result-missing-time" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "启动回测" }).first().click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")

    await page.getByRole("button", { name: "报告中心" }).click()

    await expect(page.locator(".hybrid-table__tbody tr").first()).toContainText("2025-01-01 ~ 2025-12-31")
    await expect(page.locator(".hybrid-table__tbody tr").first()).toContainText("+18.6%")
    await expect(page.locator(".hybrid-table__tbody tr").first()).toContainText("--")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest clears a previous strategy-local generated snapshot hint after the route query switched to a new strategy", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "生成上下文快照" }).click()
    await expect(page.locator(".execution-action-hint")).toContainText("最近快照：")
    await expect(page.locator(".execution-action-hint")).toContainText("参数 0 项")

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/backtest?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".context-strip")).toContainText("ID 202")
    await expect(page.locator(".state-banner")).toContainText("当前任务、KPI 与报告摘要仍基于策略列表派生")
    await expect(page.locator(".execution-action-hint")).not.toContainText("最近快照：策略 101")
    await expect(page.locator(".execution-action-hint")).toContainText("当前任务、KPI 与报告摘要来自策略列表派生视图")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest does not leak a previous strategy report row after the route query switched to a new strategy without its own verified report context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "启动回测" }).first().click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")

    await page.getByRole("button", { name: "报告中心" }).click()
    await expect(page.locator(".hybrid-table__tbody tr")).toHaveCount(1)
    await expect(page.locator(".hybrid-table__tbody tr").first()).toContainText("2025-01-01 ~ 2025-12-31")

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/backtest?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".context-strip")).toContainText("ID 202")
    await expect(page.locator(".hybrid-table__tbody tr")).toHaveCount(0)
    await expect(page.locator(".tab-panel")).not.toContainText("2025-01-01 ~ 2025-12-31")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest does not leak previous execution progress after the route query switched to a new strategy without its own verified task context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "启动回测" }).first().click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")
    await expect(page.locator(".progress-panel")).toContainText("100%")

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/backtest?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".context-strip")).toContainText("ID 202")
    await expect(page.locator(".progress-panel")).toContainText("等待任务")
    await expect(page.locator(".progress-panel")).toContainText("0%")
    await expect(page.locator(".progress-panel")).not.toContainText("100%")
    await expect(page.locator(".log-panel")).not.toContainText("回测结果已同步到报告中心")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest does not leak previous task rows after the route query switched to a new strategy without its own verified task context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "启动回测" }).first().click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")

    await page.getByRole("button", { name: "回测任务" }).click()
    await expect(page.locator(".task-list")).toContainText("回测任务已完成")

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/backtest?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".context-strip")).toContainText("ID 202")
    await expect(page.locator(".task-list")).toHaveCount(0)
    await expect(page.locator(".tab-panel")).not.toContainText("回测任务已完成")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest does not leak previous KPI summary after the route query switched to a new strategy without its own verified task context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/backtest?strategyId=101`)

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["2", "50%", "3.2%", "-2%"])

    await page.getByRole("button", { name: "启动回测" }).first().click()
    await expect(page.locator(".log-panel")).toContainText("回测结果已同步到报告中心")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["3", "50%", "3.2%", "-2%"])

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/backtest?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".context-strip")).toContainText("ID 202")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["2", "50%", "3.2%", "-2%"])
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Backtest does not leak previous optimization candidates after the route query switched to a new strategy without its own verified optimization context", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".optimization-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".optimization-table")).toContainText("Momentum Alpha")

    await page.getByRole("button", { name: "回测" }).first().click()

    await expect(page.getByText("策略回测管理中心").first()).toBeVisible()
    await page.getByRole("button", { name: "参数优化" }).click()
    await expect(page.locator(".context-strip")).toContainText("ID 101")
    await expect(page.locator(".hybrid-table__tbody tr")).toHaveCount(1)
    await expect(page.locator(".hybrid-table__tbody tr").first()).toContainText("Momentum Alpha")
    await expect(page.locator(".hybrid-table__tbody tr").first()).toContainText("90")

    await page.evaluate(() => {
      window.history.pushState({}, '', '/strategy/backtest?strategyId=202')
      window.dispatchEvent(new PopStateEvent('popstate', { state: window.history.state }))
    })

    await expect(page.locator(".context-strip")).toContainText("ID 202")
    await page.getByRole("button", { name: "参数优化" }).click()
    await expect(page.locator(".hybrid-table__tbody tr")).toHaveCount(0)
    await expect(page.locator(".tab-panel")).not.toContainText("90")
    await expect(page.locator(".tab-panel")).toContainText("建议仓位上限")
    await expect(page.locator(".tab-panel")).toContainText("建议止损阈值")
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

  test("Strategy-GPU marks performance-only partial snapshots instead of presenting them as a full recent sync", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/gpu/status", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              note: "missing runtime snapshot",
            },
            { request_id: "req-phase3-gpu-status-missing" }
          )
        ),
      })
    })
    await page.route("**/api/gpu/performance", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              metrics: [
                {
                  matrix_speedup: 64,
                  matrix_gflops: 1350,
                },
              ],
            },
            { request_id: "req-phase3-gpu-performance-only" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/gpu`)

    await expect(page.getByRole("heading", { name: "GPU 加速回测" })).toBeVisible()
    await expect(page.locator(".runtime-banner")).toContainText("部分同步")
    await expect(page.locator(".runtime-banner")).toContainText("GPU 状态待同步")
    await expect(page.locator(".runtime-banner")).not.toContainText("最近同步")
    await expect(page.locator(".gpu-availability")).toContainText("待同步")
    await expect(page.locator(".performance-card")).toContainText("64x")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-GPU stays in monitor-only unknown state when GPU APIs fail", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/gpu/status", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "gpu status unavailable" }),
      })
    })
    await page.route("**/api/gpu/performance", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "gpu performance unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/gpu`)

    await expect(page.getByRole("heading", { name: "GPU 加速回测" })).toBeVisible()
    await expect(page.locator(".runtime-banner")).toContainText("GPU 状态同步失败")
    await expect(page.locator(".gpu-availability")).toContainText("待同步")
    await expect(page.locator(".performance-card")).toContainText("等待后端性能快照")
    await expect(page.locator(".control-panel")).toContainText("当前页面仅接入 GPU 状态与性能快照读取接口")
    await expect(page.locator(".control-panel")).not.toContainText("运行基准测试")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-GPU degrades unverified thermals and missing benchmark metrics instead of fabricating zero runtime truth", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/gpu/status", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              gpus: [
                {
                  name: "NVIDIA GeForce RTX 2080",
                  driver_version: "555.10",
                  gpu_utilization: 6,
                  memory_total: 8192,
                  memory_used: 3194,
                  memory_utilization: 39,
                  temperature: 0,
                  power_usage: 0,
                },
              ],
            },
            { request_id: "req-phase3-gpu-status-partial" }
          )
        ),
      })
    })
    await page.route("**/api/gpu/performance", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              metrics: [
                {
                  gpu_utilization: 6,
                  memory_utilization: 39,
                  temperature: 0,
                  power_usage: 0,
                  health_status: "healthy",
                },
              ],
            },
            { request_id: "req-phase3-gpu-performance-partial" }
          )
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/gpu`)

    await expect(page.getByRole("heading", { name: "GPU 加速回测" })).toBeVisible()
    await expect(page.locator(".gpu-availability")).toContainText("NVIDIA GeForce RTX 2080")
    await expect(page.locator(".temperature")).toContainText("未校验")
    await expect(page.locator(".temperature")).not.toContainText("0°C")
    await expect(page.locator(".performance-card")).toContainText("待接入")
    await expect(page.locator(".performance-card")).toContainText("基准性能待接入")
    await expect(page.locator(".performance-card")).not.toContainText("0x")
    await expect(page.locator(".performance-card")).not.toContainText("-100%")
    await page.getByRole("tab", { name: "性能指标" }).click()
    await expect(page.locator(".metrics-grid")).toContainText("未校验")
    await expect(page.locator(".metrics-grid")).not.toContainText("0 MHz")
    await expect(page.locator(".metrics-grid")).not.toContainText("0%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Opt renders optimization candidates and writeback controls", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["2", "1", "0", "ID 101"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("VISIBLE: 1")
    await expect(page.locator(".header-meta")).toContainText("TOTAL: 2")
    await expect(page.locator(".optimization-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".optimization-table")).toContainText("Momentum Alpha")
    await expect(page.locator(".writeback-cell")).toContainText("参数")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Opt does not fall back to mock candidates on route-level real fetch failure", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      await route.fulfill({
        status: 500,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategy-opt-first-fail",
        },
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "strategy list unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: N/A")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-strategy-opt-first-fail")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "ID 101"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("VISIBLE: --")
    await expect(page.locator(".header-meta")).toContainText("TOTAL: --")
    await expect(page.locator(".source-badge")).toContainText("REAL-OFFLINE")
    await expect(page.locator(".source-notice")).toContainText("当前不注入 mock 行")
    await expect(page.locator(".empty-state")).toContainText("REAL 数据不可用")
    await expect(page.locator(".optimization-table")).toHaveCount(0)
    await expect(page.locator(".strategy-optimization")).not.toContainText("req-phase3-strategy-opt-first-fail")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Opt keeps honest pending placeholders while the first optimization payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.hangStrategies = true

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "ID 101"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("VISIBLE: --")
    await expect(page.locator(".header-meta")).toContainText("TOTAL: --")
    await expect(page.locator(".empty-state")).toContainText("优化候选同步中，正在等待真实候选返回。")
    await expect(page.locator(".optimization-card")).not.toContainText("未找到策略 101 的优化候选")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Opt keeps the last verified request provenance and visible rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let strategyRequestCount = 0

    await page.route("**/api/v1/strategy/strategies", async (route) => {
      strategyRequestCount += 1

      if (strategyRequestCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-strategy-opt-success",
            "x-process-time": "42ms",
          },
          body: JSON.stringify(buildUnifiedResponse(state.strategies, { request_id: "req-phase3-strategy-opt-success" })),
        })
        return
      }

      await route.fulfill({
        status: 500,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-strategy-opt-refresh-fail",
        },
        contentType: "application/json",
        body: JSON.stringify({
          success: false,
          message: "strategy optimization refresh unavailable",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategy-opt-success")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 42.00")
    await expect(page.locator(".optimization-table tbody tr")).toHaveCount(1)

    await page.getByRole("button", { name: "刷新候选" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategy-opt-success")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 42.00")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-strategy-opt-refresh-fail")
    await expect(page.locator(".strategy-optimization")).toContainText("strategy optimization refresh unavailable")
    await expect(page.locator(".strategy-optimization")).toContainText("当前仍显示上次成功同步的优化候选快照")
    await expect(page.locator(".optimization-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".optimization-table")).toContainText("Momentum Alpha")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Strategy-Opt does not leak a previous strategy snapshot after the route query switched to a new strategy without its own verified optimization snapshot", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/strategy/opt?strategyId=101`)

    await expect(page.getByText("策略优化工作台").first()).toBeVisible()
    await expect(page.locator(".content-shell-meta")).toContainText("FOCUS: ID 101")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-strategies")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: 36.00")
    await expect(page.locator(".optimization-table tbody tr")).toHaveCount(1)
    await expect(page.locator(".optimization-table")).toContainText("Momentum Alpha")

    await page.evaluate(() => {
      window.history.pushState({}, "", "/strategy/opt?strategyId=202")
      window.dispatchEvent(new PopStateEvent("popstate"))
    })

    await expect(page.locator(".content-shell-meta")).toContainText("FOCUS: ID 202")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("PROCESS: N/A")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "ID 202"])
    await expect(page.locator(".optimization-table")).toHaveCount(0)
    await expect(page.locator(".optimization-card")).toContainText("未找到策略 202 的优化候选")
    await expect(page.locator(".strategy-optimization")).not.toContainText("Momentum Alpha")
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

  test("Trade-Positions keeps honest pending placeholders while the first positions payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.hangPositions = true

    await page.goto(`${FRONTEND_BASE_URL}/trade/positions`)

    await expect(page.getByText("持仓工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("请求: --")
    await expect(page.locator(".hero-meta")).toContainText("耗时: --")
    await expect(page.locator(".hero-meta")).toContainText("行数: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("0.00")
    await expect(page.locator(".content-shell-meta")).toContainText("市值: --")
    await expect(page.locator(".content-shell-meta")).toContainText("总盈亏: --")
    await expect(page.locator(".artdeco-trading-positions__status")).toContainText("持仓数据同步中...")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Positions does not leak a failed first-load request id into route metadata", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/positions", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-trade-positions-first-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 500,
          message: "positions unavailable",
          data: null,
          timestamp: "2026-04-03T00:00:00Z",
          request_id: "req-phase3-trade-positions-first-fail",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/positions`)

    await expect(page.getByText("持仓工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("请求: N/A")
    await expect(page.locator(".hero-meta")).toContainText("耗时: N/A")
    await expect(page.locator(".hero-meta")).toContainText("行数: --")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-trade-positions-first-fail")
    await expect(page.locator(".content-shell-meta")).toContainText("市值: --")
    await expect(page.locator(".content-shell-meta")).toContainText("总盈亏: --")
    await expect(page.locator(".artdeco-trading-positions")).not.toContainText("req-phase3-trade-positions-first-fail")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Positions keeps the last verified request id and visible rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let positionsRequestCount = 0

    await page.route("**/api/v1/trade/positions", async (route) => {
      positionsRequestCount += 1

      if (positionsRequestCount > 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-trade-positions-refresh-fail",
          },
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "positions refresh unavailable",
            data: null,
            timestamp: "2026-04-03T00:00:00Z",
            request_id: "req-phase3-trade-positions-refresh-fail",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-trade-positions-success",
          "x-process-time": "31ms",
        },
        body: JSON.stringify(buildUnifiedResponse(POSITIONS_PAYLOAD, { request_id: "req-phase3-trade-positions-success" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/positions`)

    await expect(page.locator(".artdeco-trading-positions__row")).toHaveCount(2)
    await expect(page.locator(".hero-meta")).toContainText("请求: req-phase3-trade-positions-success")
    await expect(page.locator(".hero-meta")).toContainText("耗时: 31.00ms")

    await page.getByRole("button", { name: "刷新持仓" }).click()

    await expect(page.locator(".hero-meta")).toContainText("请求: req-phase3-trade-positions-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-trade-positions-refresh-fail")
    await expect(page.locator(".hero-meta")).toContainText("耗时: 31.00ms")
    await expect(page.locator(".hero-meta")).toContainText("行数: 2")
    await expect(page.locator(".artdeco-trading-positions__status")).toContainText("positions refresh unavailable")
    await expect(page.locator(".artdeco-trading-positions__status")).toContainText("当前仍显示上次成功同步的持仓快照")
    await expect(page.locator(".artdeco-trading-positions__row")).toHaveCount(2)
    await expect(page.locator(".artdeco-trading-positions")).toContainText("贵州茅台")
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
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".signal-overview-grid .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".signals-view")).not.toContainText("+0%")
    await expect(page.locator(".signals-view")).not.toContainText("3.00")
    await expect(page.locator(".signals-view")).not.toContainText("1.00")
    await expect(page.locator(".signals-view")).not.toContainText("0.00")
    await expect(page.locator(".signals-view")).toContainText("贵州茅台")
    await expect(page.locator(".signals-view")).toContainText("实时交易信号")
    await expect(page.locator(".signals-view")).toContainText("信号准确率")
    await expect(page.locator(".signals-view")).toContainText("未校验")
    await expect(page.locator(".signals-view")).toContainText("策略来源：Momentum Alpha")
    await expect(page.locator(".signals-view")).toContainText("观望")
    await expect(page.locator(".signals-view")).toContainText("观察")
    await expect(page.locator(".signals-view")).toContainText("暂无已验证执行历史。")
    await expect(page.locator(".signals-view")).not.toContainText("88%")
    await expect(page.locator(".signals-view")).not.toContainText("76%")
    await expect(page.locator(".signals-view")).not.toContainText("Momentum Alpha 信号触发")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Signals keeps honest pending provenance while the first signal payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.hangSignals = true

    await page.goto(`${FRONTEND_BASE_URL}/trade/signals`)

    await expect(page.getByText("交易信号工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("COUNT: --")
    await expect(page.locator(".hero-meta")).toContainText("DATA: PENDING")
    await expect(page.locator(".hero-meta")).not.toContainText("DATA: REAL")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("VISIBLE: --")
    await expect(page.locator(".signals-view")).toContainText("交易信号同步中...")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Signals keeps unavailable provenance when the first signal payload fails before any verified snapshot exists", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/signals**", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "trade signals unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/signals`)

    await expect(page.getByText("交易信号工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("COUNT: --")
    await expect(page.locator(".hero-meta")).toContainText("DATA: UNAVAILABLE")
    await expect(page.locator(".hero-meta")).not.toContainText("DATA: REAL")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".content-shell-meta")).toContainText("VISIBLE: --")
    await expect(page.locator(".signals-view")).toContainText("trade signals unavailable")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Signals keeps the last verified request id and signal rows when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let signalRequestCount = 0

    await page.route("**/api/v1/trade/signals**", async (route) => {
      signalRequestCount += 1

      if (signalRequestCount === 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-signals-success",
            "x-process-time": "42ms",
          },
          body: JSON.stringify(buildUnifiedResponse(state.signals, { request_id: "req-phase3-signals-success" })),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-signals-refresh-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 500,
          message: "trade signals refresh unavailable",
          data: null,
          timestamp: "2026-04-03T00:00:00Z",
          request_id: "req-phase3-signals-refresh-fail",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/signals`)

    await expect(page.getByText("交易信号工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-signals-success")
    await expect(page.locator(".artdeco-trading-signals__row")).toHaveCount(3)

    await page.getByRole("button", { name: "刷新信号" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-signals-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-signals-refresh-fail")
    await expect(page.locator(".signals-view")).toContainText("trade signals refresh unavailable")
    await expect(page.locator(".signals-view")).toContainText("当前仍显示上次成功同步的交易信号快照。")
    await expect(page.locator(".artdeco-trading-signals__row")).toHaveCount(3)
    await expect(page.locator(".signals-view")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Portfolio renders mocked portfolio overview", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`)

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("POSITIONS: 2")
    await expect(page.locator(".hero-meta")).toContainText("REBALANCE: 待接入")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["372,664.00", "+6,844", "2", "待接入"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".portfolio-overview-tab")).toContainText("Top Positions")
    await expect(page.locator(".portfolio-overview-tab")).toContainText("贵州茅台")
    await expect(page.locator(".attribution-panel")).toContainText("绩效归因")
    await expect(page.locator(".attribution-panel")).toContainText("Brinson 归因")
    await expect(page.locator(".attribution-panel")).toContainText("五因子归因")
    await expect(page.locator(".attribution-panel")).toContainText("req-phase3-positions-attribution")
    await expect(page.locator(".rebalance-section")).toContainText("再平衡策略待接入")
    await expect(page.locator(".rebalance-section")).not.toContainText("目标 25%")
    await expect(page.locator(".rebalance-section")).not.toContainText("建议减仓约")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Portfolio keeps honest pending placeholders while the first positions payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.hangPositions = true

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`)

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("POSITIONS: --")
    await expect(page.locator(".hero-meta")).toContainText("REBALANCE: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".assets-hero")).toContainText("Total Assets (CNY)")
    await expect(page.locator(".assets-hero")).toContainText("--")
    await expect(page.locator(".runtime-message")).toContainText("组合资产同步中...")
    await expect(page.locator(".position-list-section")).not.toContainText("暂无持仓数据。")
    await expect(page.locator(".rebalance-section")).not.toContainText("再平衡策略待接入")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Portfolio does not present failed first-load portfolio summary surfaces as faux zero balances", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/positions", async (route) => {
      await route.fulfill({
        status: 500,
        contentType: "application/json",
        body: JSON.stringify({ success: false, message: "positions unavailable" }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`)

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("POSITIONS: --")
    await expect(page.locator(".hero-meta")).toContainText("REBALANCE: --")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".assets-hero")).toContainText("Total Assets (CNY)")
    await expect(page.locator(".assets-hero")).toContainText("--")
    await expect(page.locator(".runtime-message")).toContainText("positions unavailable")
    await expect(page.locator(".position-list-section")).not.toContainText("暂无持仓数据。")
    await expect(page.locator(".rebalance-section")).not.toContainText("再平衡策略待接入")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Portfolio does not leak a failed first-load request id into route metadata", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/positions", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-positions-first-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 500,
          message: "positions unavailable",
          data: null,
          timestamp: "2026-04-03T00:00:00Z",
          request_id: "req-phase3-positions-first-fail",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`)

    await expect(page.getByText("组合资产工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ: N/A")
    await expect(page.locator(".hero-meta")).toContainText("POSITIONS: --")
    await expect(page.locator(".hero-meta")).toContainText("REBALANCE: --")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-positions-first-fail")
    await expect(page.locator(".portfolio-overview-tab")).not.toContainText("req-phase3-positions-first-fail")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Portfolio keeps the last verified request id visible when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    let portfolioRequestCount = 0

    await page.route("**/api/v1/trade/positions", async (route) => {
      portfolioRequestCount += 1

      if (portfolioRequestCount > 1) {
        await route.fulfill({
          status: 200,
          headers: {
            "content-type": "application/json",
            "x-request-id": "req-phase3-positions-refresh-fail",
          },
          body: JSON.stringify({
            success: false,
            code: 500,
            message: "positions refresh unavailable",
            data: null,
            timestamp: "2026-04-03T00:00:00Z",
            request_id: "req-phase3-positions-refresh-fail",
          }),
        })
        return
      }

      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-positions-success",
          "x-process-time": "31ms",
        },
        body: JSON.stringify(buildUnifiedResponse(POSITIONS_PAYLOAD, { request_id: "req-phase3-positions-success" })),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/portfolio`)

    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".hero-meta")).toContainText("REQ: req-phase3-positions-success")

    await page.getByRole("button", { name: "刷新资产" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ: req-phase3-positions-success")
    await expect(page.locator(".hero-meta")).not.toContainText("req-phase3-positions-refresh-fail")
    await expect(page.locator(".runtime-message")).toContainText("positions refresh unavailable")
    await expect(page.locator(".runtime-message")).toContainText("当前仍显示上次成功同步的组合快照")
    await expect(page.locator(".positions-grid .position-item")).toHaveCount(2)
    await expect(page.locator(".portfolio-overview-tab")).toContainText("贵州茅台")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-History renders mocked trade ledger", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/history`)

    await expect(page.getByText("交易历史工作台").first()).toBeVisible()
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".stats-strip")).not.toContainText("+0%")
    await expect(page.locator(".stats-strip")).not.toContainText("2.00")
    await expect(page.locator(".stats-strip")).not.toContainText("1.00")
    await expect(page.locator(".artdeco-trading-history__row")).toHaveCount(2)
    await expect(page.locator(".artdeco-trading-history")).toContainText("600519")
    await expect(page.locator(".artdeco-trading-history")).toContainText("已成交")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-History keeps the last mocked ledger visible when a manual refresh fails", async ({ page }) => {
    const state = await setupPhase3Mock(page)
    state.failTradesRefreshAfterFirst = true

    await page.goto(`${FRONTEND_BASE_URL}/trade/history`)

    await expect(page.locator(".artdeco-trading-history__row")).toHaveCount(2)
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-trades")
    await expect(page.locator(".hero-meta")).toContainText("TIME: 29.00ms")
    await page.getByRole("button", { name: "刷新历史" }).click()

    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-trades")
    await expect(page.locator(".hero-meta")).toContainText("TIME: 29.00ms")
    await expect(page.locator(".hero-meta")).not.toContainText("REQ_ID: req-phase3-trades-refresh-fail")
    await expect(page.locator(".artdeco-trading-history")).toContainText("刷新异常")
    await expect(page.locator(".artdeco-trading-history")).toContainText("当前仍展示上次成功同步的交易历史记录。")
    await expect(page.locator(".artdeco-trading-history__row")).toHaveCount(2)
    await expect(page.locator(".artdeco-trading-history")).toContainText("600519")
    await expect(page.locator(".artdeco-trading-history")).not.toContainText("交易历史拉取失败，当前无法展示真实记录。")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-History keeps pending provenance honest while the first trade-ledger payload is still unresolved", async ({ page }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/trades", async () => {
      await new Promise(() => {})
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/history`)

    await expect(page.getByText("交易历史工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("TIME: N/A")
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".hero-meta")).not.toContainText("ROWS: 0")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".artdeco-trading-history")).toContainText("交易历史同步中...")
    await expect(page.locator(".artdeco-trading-history")).not.toContainText("暂无历史成交记录")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-History keeps unavailable provenance honest when the first trade-ledger payload fails before any verified snapshot exists", async ({
    page,
  }) => {
    const state = await setupPhase3Mock(page)

    await page.route("**/api/v1/trade/trades", async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          "content-type": "application/json",
          "x-request-id": "req-phase3-trades-first-fail",
        },
        body: JSON.stringify({
          success: false,
          code: 500,
          message: "交易历史接口失败",
          data: null,
          timestamp: "2026-04-03T00:00:00Z",
          request_id: "req-phase3-trades-first-fail",
        }),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/trade/history`)

    await expect(page.getByText("交易历史工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("TIME: N/A")
    await expect(page.locator(".hero-meta")).toContainText("ROWS: --")
    await expect(page.locator(".hero-meta")).not.toContainText("ROWS: 0")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--"])
    await expect(page.locator(".stats-strip .artdeco-stat-change")).toHaveCount(0)
    await expect(page.locator(".artdeco-trading-history")).toContainText("交易历史接口失败")
    await expect(page.locator(".artdeco-trading-history")).not.toContainText("暂无历史成交记录")
    expect(state.unhandledRequests).toEqual([])
  })

  test("Trade-Reconciliation clears stale statement and result rows while a newly selected account snapshot is still unresolved", async ({
    page,
  }) => {
    const state = await setupPhase3Mock(page)

    await page.goto(`${FRONTEND_BASE_URL}/trade/reconciliation`)

    await expect(page.getByText("对账单工作台").first()).toBeVisible()
    await expect(page.locator(".hero-meta")).toContainText("ACCOUNT: backtest:7")
    await expect(page.locator(".trade-reconciliation")).toContainText("600519.SH")

    await page.getByTestId("reconciliation-source-select").selectOption("miniqmt")
    await page.getByTestId("reconciliation-file-input").setInputFiles({
      name: "miniqmt.csv",
      mimeType: "text/csv",
      buffer: Buffer.from("symbol,price\n600519.SH,1750\n", "utf8"),
    })
    await page.getByRole("button", { name: "导入并对账" }).click()

    await expect(page.locator(".trade-reconciliation")).toContainText("600519.SH")
    await expect(page.locator(".trade-reconciliation")).toContainText("601318.SH")
    await expect(page.locator(".trade-reconciliation")).toContainText("000001.SZ")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: req-phase3-reconciliation-results-backtest-7")
    await expect(page.locator(".hero-meta")).not.toContainText("UPDATED: --")

    state.hangReconciliationAccountId = "backtest:8"
    await page.getByTestId("reconciliation-account-select").selectOption("backtest:8")

    await expect(page.locator(".hero-meta")).toContainText("ACCOUNT: backtest:8")
    await expect(page.locator(".hero-meta")).toContainText("REQ_ID: N/A")
    await expect(page.locator(".hero-meta")).toContainText("UPDATED: --")
    await expect(page.locator(".hero-meta")).toContainText("IMPORT_BATCH: 未导入")
    await expect(page.locator(".hero-meta")).toContainText("ROWS: 0")
    await expect(page.locator(".hero-meta")).not.toContainText("REQ_ID: req-phase3-reconciliation-results-backtest-7")
    await expect(page.locator(".hero-meta")).not.toContainText("IMPORT_BATCH: batch-7")
    await expect(page.locator(".hero-meta")).not.toContainText("ROWS: 3")
    await expect(page.locator(".trade-reconciliation")).not.toContainText("600519.SH")
    await expect(page.locator(".trade-reconciliation")).not.toContainText("601318.SH")
    await expect(page.locator(".trade-reconciliation")).not.toContainText("000001.SZ")
    await expect(page.locator(".stats-strip .artdeco-stat-value")).toHaveText(["--", "--", "--", "--", "--", "--"])
    await expect(page.getByText("暂无内部账单记录。")).toBeVisible()
    await expect(page.getByText("导入完成后将在这里展示只读对账结果。")).toBeVisible()
    expect(state.unhandledRequests).toEqual([])
  })
})
