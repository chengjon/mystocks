import { expect, test } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const WATCHLIST_ENDPOINTS = [
  '**/api/v1/monitoring/watchlists',
  '**/api/api/v1/monitoring/watchlists'
]
const WATCHLIST_STOCK_ENDPOINTS = [
  '**/api/v1/monitoring/watchlists/*/stocks',
  '**/api/api/v1/monitoring/watchlists/*/stocks'
]

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: 'ok',
    data,
    timestamp: '2026-03-11T00:00:00Z',
    request_id: 'req-watchlist-manage-default',
    ...(overrides ?? {})
  }
}

async function setupAuthenticatedSession(page: Parameters<typeof test>[0]['page']) {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: 'e2e-admin',
      email: 'e2e-admin@mystocks.local',
      role: 'admin',
      permissions: ['*']
    }
    localStorage.setItem('auth_token', 'e2e-token')
    localStorage.setItem('auth_user', JSON.stringify(user))
  })
}

async function mockSupportEndpoints(page: Parameters<typeof test>[0]['page']) {
  for (const endpoint of ['**/api/health/ready', '**/health/ready']) {
    await page.route(endpoint, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            { status: 'ready' },
            { request_id: 'req-watchlist-ready', message: 'backend ready' }
          )
        )
      })
    })
  }
}

async function routeWatchlists(
  page: Parameters<typeof test>[0]['page'],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of WATCHLIST_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

async function routeWatchlistStocks(
  page: Parameters<typeof test>[0]['page'],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of WATCHLIST_STOCK_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

test.describe('Watchlist Manage Page', () => {
  test.describe.configure({ mode: 'serial', timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockSupportEndpoints(page)
  })

  test('loads the route through the v1 monitoring watchlists public root', async ({ page }) => {
    const requestUrls: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('/monitoring/watchlists')) {
        requestUrls.push(request.url())
      }
    })

    await routeWatchlists(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          'content-type': 'application/json',
          'x-request-id': 'req-watchlist-list'
        },
        body: JSON.stringify(
          buildUnifiedResponse([
            {
              id: 7,
              name: '核心观察池',
              watchlist_type: 'manual',
              is_active: true,
              stocks_count: 2,
              risk_profile: { risk_tolerance: 60 }
            }
          ])
        )
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`)

    await expect(page.locator('.watchlist-page')).toBeVisible()
    await expect(page.getByText('MONITORING PORTFOLIOS')).toBeVisible()
    await expect(page.getByText('核心观察池')).toBeVisible()

    expect(requestUrls.some((url) => url.includes('/api/v1/monitoring/watchlists'))).toBeTruthy()
    expect(requestUrls.some((url) => url.includes('/api/watchlist'))).toBeFalsy()
    expect(requestUrls.some((url) => url.includes('/api/monitoring/watchlists'))).toBeFalsy()
  })

  test('loads stock rows from the nested v1 monitoring watchlists path', async ({ page }) => {
    await routeWatchlists(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          'content-type': 'application/json',
          'x-request-id': 'req-watchlist-list'
        },
        body: JSON.stringify(
          buildUnifiedResponse([
            {
              id: 7,
              name: '核心观察池',
              watchlist_type: 'manual',
              is_active: true,
              stocks_count: 1,
              risk_profile: { risk_tolerance: 60 }
            }
          ])
        )
      })
    })

    const stockRequestUrls: string[] = []
    page.on('request', (request) => {
      if (request.url().includes('/monitoring/watchlists/7/stocks')) {
        stockRequestUrls.push(request.url())
      }
    })

    await routeWatchlistStocks(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          'content-type': 'application/json',
          'x-request-id': 'req-watchlist-stocks'
        },
        body: JSON.stringify(
          buildUnifiedResponse([
            {
              id: 17,
              watchlist_id: 7,
              stock_code: '000001.SZ',
              entry_price: 12.3,
              entry_reason: 'manual_pick',
              weight: 0.2,
              is_active: true
            }
          ])
        )
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/watchlist/manage`)
    await page.getByText('核心观察池').click()

    await expect(page.getByText('STOCK MANAGEMENT - 核心观察池')).toBeVisible()
    await expect(page.getByText('000001.SZ')).toBeVisible()
    expect(stockRequestUrls.some((url) => url.includes('/api/v1/monitoring/watchlists/7/stocks'))).toBeTruthy()
  })
})
