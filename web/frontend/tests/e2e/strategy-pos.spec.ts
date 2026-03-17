import { expect, test } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const POSITION_ENDPOINTS = [
  '**/api/v1/trade/positions**',
  '**/api/api/v1/trade/positions**'
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
          request_id: 'req-strategy-pos-ready'
        })
      })
    })
  }
}

test.describe('Strategy Position Page', () => {
  test.describe.configure({ mode: 'serial', timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockSupportEndpoints(page)
  })

  test('loads the route through the v1 trade positions public root', async ({ page }) => {
    const requestUrls: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('/trade/positions')) {
        requestUrls.push(request.url())
      }
    })

    const positionResponsePromise = page.waitForResponse((response) => {
      return response.url().includes('/api/v1/trade/positions') && response.ok()
    })

    for (const endpoint of POSITION_ENDPOINTS) {
      await page.route(endpoint, async (route) => {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            positions: [
              {
                symbol: '600519',
                name: '贵州茅台',
                quantity: 100,
                average_cost: 1800,
                current_price: 1850,
                market_value: 185000,
                unrealized_pnl: 5000,
                weight: 0.35
              }
            ],
            total_value: 185000,
            total: 1
          })
        })
      })
    }

    await page.goto(`${FRONTEND_BASE_URL}/strategy/pos`, { waitUntil: 'networkidle' })
    await positionResponsePromise

    await expect(page.locator('.strategy-position-page')).toBeVisible({ timeout: 10000 })
    await expect(page.getByText('Strategy Position Board')).toBeVisible()
    await expect(page.getByText('贵州茅台')).toBeVisible()

    expect(requestUrls.some((url) => url.includes('/api/v1/trade/positions'))).toBeTruthy()
    expect(requestUrls.some((url) => url.includes('/api/strategy/pos'))).toBeFalsy()
    expect(requestUrls.some((url) => url.includes('/api/trade/portfolio'))).toBeFalsy()
  })
})
