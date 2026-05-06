import { expect, test } from '@playwright/test'
const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

function buildUnifiedResponse<T>(data: T, requestId: string) {
  return {
    success: true,
    code: 200,
    message: 'ok',
    data,
    timestamp: '2026-04-25T00:00:00Z',
    request_id: requestId
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

test.describe('System API store governance', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)

    await page.route('**/api/health/ready', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse({ status: 'ready' }, 'req-ready-1'))
      })
    })

    await page.route('**/api/health', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              status: 'healthy',
              service: 'mystocks-backend',
              version: '2.0.0'
            },
            'req-health-1'
          )
        )
      })
    })

    await page.route('**/trade/signals**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse([{ id: 'signal-1', symbol: '000001' }], 'req-signals-1'))
      })
    })

    await page.route('**/risk/alerts**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse([{ id: 'risk-1', level: 'medium' }], 'req-risk-1'))
      })
    })

    await page.route('**/monitoring/watchlists**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse([{ id: 'wl-1', name: 'Core Holdings', stocks_count: 1 }], 'req-watchlist-1'))
      })
    })
  })

  test('surfaces standardized store runtime metrics in the governance inspector', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/system/api`)

    await expect(page.getByRole('heading', { name: '系统监控工作台' })).toBeVisible({ timeout: 15000 })
    await expect(page.getByText('Readiness: ready')).toBeVisible()
    await expect(page.getByText('Backend: ready')).toBeVisible()
    await expect(page.getByText('Request ID: req-ready-1')).toBeVisible()

    const tradingSignalsResponse = page.waitForResponse((response) => response.url().includes('/trade/signals'))
    const riskAlertsResponse = page.waitForResponse((response) => response.url().includes('/risk/alerts'))
    const watchlistsResponse = page.waitForResponse((response) => response.url().includes('/monitoring/watchlists'))

    await page.getByRole('button', { name: '刷新试点 Store' }).click()
    await Promise.all([tradingSignalsResponse, riskAlertsResponse, watchlistsResponse])
    await expect(page.getByText('试点 Store 已触发刷新。')).toBeVisible()

    const runtimeSection = page.locator('.governance-section').filter({
      has: page.getByRole('heading', { name: 'Store Runtime' })
    })

    const tradingSignalsRow = runtimeSection.locator('.governance-row', { hasText: 'trading-signals' })
    const riskAlertsRow = runtimeSection.locator('.governance-row', { hasText: 'risk-alerts' })
    const watchlistsRow = runtimeSection.locator('.governance-row', { hasText: 'monitoring-watchlists' })
    const indicatorsRow = runtimeSection.locator('.governance-row', { hasText: 'technical-indicators' })

    await expect(tradingSignalsRow).toContainText('1')
    await expect(tradingSignalsRow).toContainText(/ms/)
    await expect(riskAlertsRow).toContainText('1')
    await expect(riskAlertsRow).toContainText(/ms/)
    await expect(watchlistsRow).toContainText('1')
    await expect(watchlistsRow).toContainText(/ms/)

    await expect(indicatorsRow).toContainText('0')
    await expect(indicatorsRow).toContainText('n/a')
  })
})
