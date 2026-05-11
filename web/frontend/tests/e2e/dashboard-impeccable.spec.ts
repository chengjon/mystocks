import { expect, test, type Page } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

const E2E_USER = {
  id: 1,
  username: 'admin',
  email: 'admin@example.com',
  role: 'admin',
  permissions: []
}

const DASHBOARD_QUOTES = [
  { symbol: '000001.SH', latest_price: 3321.08, change_percent: 0.65, volume: 9123 },
  { symbol: '399001.SZ', latest_price: 10214.2, change_percent: 0.71, volume: 8450 },
  { symbol: '399006.SZ', latest_price: 1988.66, change_percent: -0.22, volume: 6012 }
]

const FUND_FLOW_SUMMARY = [
  { 板块: '沪股通', 资金方向: '北向', 成交净买额: 18.5, 指数涨跌幅: 0.82 },
  { 板块: '深股通', 资金方向: '北向', 成交净买额: 9.3, 指数涨跌幅: 0.45 }
]

const BIG_DEAL_ROWS = [
  { 股票简称: '贵州茅台', 成交额: 980000000, 大单性质: '买盘', 涨跌幅: 1.2 },
  { 股票简称: '宁德时代', 成交额: 420000000, 大单性质: '卖盘', 涨跌幅: -0.8 }
]

const INDUSTRY_ROWS = [
  {
    rank: 1,
    sector_name: '半导体',
    change_percent: 3.28,
    main_net_inflow: 1280000000,
    main_net_inflow_rate: 14.2
  },
  {
    rank: 2,
    sector_name: '算力',
    change_percent: 2.16,
    main_net_inflow: 860000000,
    main_net_inflow_rate: 9.7
  }
]

const KLINE_ROWS = Array.from({ length: 6 }).map((_, index) => ({
  datetime: `2026-04-${String(index + 1).padStart(2, '0')} 15:00:00`,
  open: 100 + index,
  high: 102 + index,
  low: 99 + index,
  close: 101 + index,
  volume: 1000000 + index * 5000
}))

function normalizePathname(url: string): string {
  const parsedUrl = new URL(url)
  return parsedUrl.pathname.replace(/^\/api/, '')
}

async function seedAuth(page: Page): Promise<void> {
  await page.addInitScript((user) => {
    window.localStorage.setItem('auth_token', 'e2e-dashboard-token')
    window.localStorage.setItem('user', JSON.stringify(user))
  }, E2E_USER)
}

async function stubDashboardApis(page: Page, options: { failIndustry?: boolean } = {}): Promise<void> {
  await page.route(/https?:\/\/[^/]+\/(?:api\/.*|health(?:\/.*)?)/, async (route) => {
    const normalizedPath = normalizePathname(route.request().url())

    if (normalizedPath === '/health/ready') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'ready', ready: true })
      })
      return
    }

    if (normalizedPath === '/health') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-health',
          process_time: '12',
          data: { status: 'healthy', service: 'mystocks-backend' }
        })
      })
      return
    }

    if (normalizedPath === '/v1/market/quotes') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-quotes',
          process_time: '11',
          data: DASHBOARD_QUOTES
        })
      })
      return
    }

    if (normalizedPath === '/akshare/market/fund-flow/hsgt-summary') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-fund-flow',
          process_time: '22',
          data: FUND_FLOW_SUMMARY
        })
      })
      return
    }

    if (normalizedPath === '/akshare/market/fund-flow/big-deal') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-ranking',
          process_time: '44',
          data: BIG_DEAL_ROWS
        })
      })
      return
    }

    if (normalizedPath === '/v2/market/sector/fund-flow') {
      if (options.failIndustry) {
        await route.fulfill({
          status: 500,
          contentType: 'application/json',
          body: JSON.stringify({
            success: false,
            request_id: 'e2e-dashboard-industry-first-fail',
            message: '行业热度数据暂不可用'
          })
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-industry',
          process_time: '33',
          data: INDUSTRY_ROWS
        })
      })
      return
    }

    if (normalizedPath === '/v1/market/kline') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-kline',
          data: { data: KLINE_ROWS }
        })
      })
      return
    }

    if (normalizedPath === '/v1/technical-indicators') {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          request_id: 'e2e-dashboard-indicators',
          process_time: '88',
          data: { name: 'RSI', value: '61.2', trend: 'rise', signal: '偏强' }
        })
      })
      return
    }

    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify({ success: true, data: [] })
    })
  })
}

test.describe('Dashboard Impeccable audit regressions', () => {
  test.beforeEach(async ({ page }) => {
    await seedAuth(page)
  })

  test('renders structured degraded alerts without hiding dashboard cards', async ({ page }) => {
    await stubDashboardApis(page, { failIndustry: true })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: 'domcontentloaded' })

    await expect(page.getByRole('button', { name: '刷新数据' })).toBeVisible()
    await expect(page.locator('.request-meta-bar')).toContainText('DATA: MIXED')
    await expect(page.locator('.request-meta-bar')).toContainText('SYNC: DEGRADED')
    await expect(page.locator('.dashboard-alerts')).toContainText('FAILED')
    await expect(page.locator('.dashboard-alerts')).toContainText('行业热度数据暂不可用')
    await expect(page.locator('.dashboard-alerts')).toContainText('行业热度无可用快照，相关图表已暂停。')
    await expect(page.getByText('市场资金流向概览')).toBeVisible()
    await expect(page.getByText('主要市场指标')).toBeVisible()
  })

  test('tablists support keyboard focus and selection semantics', async ({ page }) => {
    await stubDashboardApis(page)

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`, { waitUntil: 'domcontentloaded' })

    const oneDayTab = page.getByRole('tab', { name: '1日' })
    const threeDayTab = page.getByRole('tab', { name: '3日' })
    const fiveDayTab = page.getByRole('tab', { name: '5日' })

    await oneDayTab.focus()
    await expect(oneDayTab).toBeFocused()
    await page.keyboard.press('ArrowRight')

    await expect(threeDayTab).toBeFocused()
    await expect(threeDayTab).toHaveAttribute('aria-selected', 'true')
    await expect(page.locator('.capital-flow-card .flow-tab.active')).toContainText('3日')

    await page.keyboard.press('ArrowLeft')
    await expect(oneDayTab).toBeFocused()
    await expect(oneDayTab).toHaveAttribute('aria-selected', 'true')

    await page.keyboard.press('ArrowLeft')
    await expect(fiveDayTab).toBeFocused()
    await expect(fiveDayTab).toHaveAttribute('aria-selected', 'true')

    const watchlistTab = page.getByRole('tab', { name: '自选' })
    const positionTab = page.getByRole('tab', { name: '持仓' })
    const focusTab = page.getByRole('tab', { name: '重点' })

    await watchlistTab.focus()
    await expect(watchlistTab).toBeFocused()
    await page.keyboard.press('ArrowRight')

    await expect(positionTab).toBeFocused()
    await expect(positionTab).toHaveAttribute('aria-selected', 'true')
    await expect(page.locator('.stock-pool-card .pool-tab.active')).toContainText('持仓')

    await page.keyboard.press('ArrowLeft')
    await expect(watchlistTab).toBeFocused()
    await expect(watchlistTab).toHaveAttribute('aria-selected', 'true')

    await page.keyboard.press('ArrowLeft')
    await expect(focusTab).toBeFocused()
    await expect(focusTab).toHaveAttribute('aria-selected', 'true')
  })
})
