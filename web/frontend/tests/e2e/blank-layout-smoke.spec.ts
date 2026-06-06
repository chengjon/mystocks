import { expect, test } from '@playwright/test'
const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

test.use({ serviceWorkers: 'block' })

test.describe('Blank-layout shell routes', () => {
  test.beforeEach(async ({ page }) => {
    await page.route('**/api/health/ready**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          success: true,
          code: 200,
          message: '后端已就绪',
          data: {
            status: 'ready',
          },
          request_id: 'req-blank-layout-ready',
          timestamp: '2026-05-07T00:00:00Z',
        }),
      })
    })
  })

  test('keeps login and 404 inside the blank shell without shared summary chrome or stale page leakage', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/login`, { waitUntil: 'domcontentloaded' })

    await expect(page.locator('.app-shell[data-layout="blank"]')).toBeVisible()
    await expect(page.locator('.login-card')).toBeVisible()
    await expect(page.locator('.app-readiness-banner')).toHaveCount(0)
    await expect(page.locator('.stats-strip')).toHaveCount(0)
    await expect(page.locator('.error-card')).toHaveCount(0)

    await page.goto(`${FRONTEND_BASE_URL}/__blank-layout-missing-route__`, { waitUntil: 'domcontentloaded' })

    await expect(page.locator('.app-shell[data-layout="blank"]')).toBeVisible()
    await expect(page.locator('.error-card')).toBeVisible()
    await expect(page.locator('.app-readiness-banner')).toHaveCount(0)
    await expect(page.locator('.stats-strip')).toHaveCount(0)
    await expect(page.locator('.login-card')).toHaveCount(0)

    await page.getByRole('button', { name: '返回首页' }).click()
    await expect(page).toHaveURL(/\/login(?:\?redirect=\/dashboard)?$/)
    await expect(page.locator('.login-card')).toBeVisible()
    await expect(page.locator('.error-card')).toHaveCount(0)
  })
})
