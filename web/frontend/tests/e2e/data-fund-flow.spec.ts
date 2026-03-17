import { expect, test } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const FUND_FLOW_ENDPOINTS = [
  '**/api/akshare/market/fund-flow/hsgt-summary**',
  '**/api/api/akshare/market/fund-flow/hsgt-summary**'
]
const BIG_DEAL_ENDPOINTS = [
  '**/api/akshare/market/fund-flow/big-deal**',
  '**/api/api/akshare/market/fund-flow/big-deal**'
]

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
        body: JSON.stringify({
          success: true,
          code: 200,
          message: 'ok',
          data: { status: 'ready' },
          timestamp: '2026-03-11T00:00:00Z',
          request_id: 'req-data-fund-flow-ready'
        })
      })
    })
  }
}

test.describe('Data Fund Flow Page', () => {
  test.describe.configure({ mode: 'serial', timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockSupportEndpoints(page)
  })

  test('loads the route through the akshare fund-flow public root', async ({ page }) => {
    const requestUrls: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('/fund-flow/')) {
        requestUrls.push(request.url())
      }
    })

    for (const endpoint of FUND_FLOW_ENDPOINTS) {
      await page.route(endpoint, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            code: 200,
            message: 'ok',
            data: {
              data: [
                { date: '2026-03-09', north_money: 12.4, south_money: -8.2 },
                { date: '2026-03-10', north_money: 18.6, south_money: -3.1 },
                { date: '2026-03-11', north_money: 25.2, south_money: 4.8 }
              ]
            },
            timestamp: '2026-03-11T00:00:00Z',
            request_id: 'req-data-fund-flow-summary'
          })
        })
      })
    }

    for (const endpoint of BIG_DEAL_ENDPOINTS) {
      await page.route(endpoint, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            success: true,
            code: 200,
            message: 'ok',
            data: {
              data: [
                {
                  symbol: '600000',
                  name: '浦发银行',
                  big_deal_amount: 9800000,
                  big_deal_buy_amount: 5300000,
                  big_deal_sell_amount: 4500000,
                  big_deal_net_inflow: 800000
                }
              ]
            },
            timestamp: '2026-03-11T00:00:00Z',
            request_id: 'req-data-fund-flow-ranking'
          })
        })
      })
    }

    await page.goto(`${FRONTEND_BASE_URL}/data/fund-flow`)

    await expect(page.locator('.data-fund-flow-page')).toBeVisible()
    await expect(page.getByText('Capital Flow Monitor')).toBeVisible()
    await expect(page.getByText('浦发银行')).toBeVisible()

    expect(requestUrls.some((url) => url.includes('/api/akshare/market/fund-flow/hsgt-summary'))).toBeTruthy()
    expect(requestUrls.some((url) => url.includes('/api/akshare/market/fund-flow/big-deal'))).toBeTruthy()
    expect(requestUrls.some((url) => url.includes('/api/v1/market/fund-flow'))).toBeFalsy()
    expect(requestUrls.some((url) => url.includes('/api/v2/market/fund-flow'))).toBeFalsy()
  })
})
