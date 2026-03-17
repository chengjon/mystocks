import { expect, test } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const LHB_ENDPOINTS = [
  '**/api/v1/market/lhb**',
  '**/api/api/v1/market/lhb**'
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
          request_id: 'req-market-lhb-ready'
        })
      })
    })
  }
}

async function routeDragonTiger(
  page: Parameters<typeof test>[0]['page'],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of LHB_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

test.describe('Market LHB Page', () => {
  test.describe.configure({ mode: 'serial', timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockSupportEndpoints(page)
  })

  test('loads the route through the v1 market lhb public root', async ({ page }) => {
    const requestUrls: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('/market/lhb')) {
        requestUrls.push(request.url())
      }
    })

    await routeDragonTiger(page, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 464,
            symbol: '000638',
            name: '*ST万方',
            trade_date: '2026-01-06',
            reason: '1家机构买入，成功率46.87%',
            buy_amount: 15025484,
            sell_amount: 6230906,
            net_amount: 8794578,
            turnover_rate: 0.2912,
            institution_buy: 15025484,
            institution_sell: null
          }
        ])
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`)

    await expect(page.locator('.market-lhb-page')).toBeVisible()
    await expect(page.getByText('Dragon Tiger Board')).toBeVisible()
    await expect(page.getByText('*ST万方')).toBeVisible()

    expect(requestUrls.some((url) => url.includes('/api/v1/market/lhb'))).toBeTruthy()
    expect(requestUrls.some((url) => url.includes('/api/data/lhb'))).toBeFalsy()
    expect(requestUrls.some((url) => url.includes('/api/market/longhubang'))).toBeFalsy()
  })

  test('filters the route to institution rows without fallback fake data', async ({ page }) => {
    await routeDragonTiger(page, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: 464,
            symbol: '000638',
            name: '*ST万方',
            trade_date: '2026-01-06',
            reason: '1家机构买入，成功率46.87%',
            buy_amount: 15025484,
            sell_amount: 6230906,
            net_amount: 8794578,
            turnover_rate: 0.2912,
            institution_buy: 15025484,
            institution_sell: null
          },
          {
            id: 465,
            symbol: '600000',
            name: '浦发银行',
            trade_date: '2026-01-06',
            reason: '游资博弈',
            buy_amount: 9800000,
            sell_amount: 7600000,
            net_amount: 2200000,
            turnover_rate: 0.182,
            institution_buy: null,
            institution_sell: null
          }
        ])
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/market/lhb`)
    await page.getByRole('button', { name: '机构榜' }).click()

    await expect(page.getByText('*ST万方')).toBeVisible()
    await expect(page.getByText('浦发银行')).toHaveCount(0)
  })
})
