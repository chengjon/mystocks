import { expect, test } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: 'ok',
    data,
    timestamp: '2026-03-11T00:00:00Z',
    request_id: 'req-dashboard-default',
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

test.describe('Dashboard Page', () => {
  test.describe.configure({ mode: 'serial', timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)

    await page.route('**/*', async (route) => {
      const url = route.request().url()
      const pathname = new URL(url).pathname

      if (!pathname.startsWith('/api/') && pathname !== '/health/ready') {
        await route.continue()
        return
      }

      if (url.includes('/api/health/ready') || url.endsWith('/health/ready')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(
            buildUnifiedResponse(
              {
                status: 'ready'
              },
              { request_id: 'req-dashboard-ready', message: 'backend ready' }
            )
          )
        })
        return
      }

      if (url.includes('/api/dashboard/market-overview')) {
        await route.fulfill({
          status: 200,
          headers: {
            'content-type': 'application/json',
            'x-request-id': 'req-dashboard-overview',
            'x-process-time': '42'
          },
          body: JSON.stringify(
            buildUnifiedResponse({
              indices: [
                { symbol: '000001.SH', name: '上证指数', current_price: 3210.55, change_percent: 1.23 },
                { symbol: '399001.SZ', name: '深证成指', current_price: 10012.67, change_percent: -0.45 },
                { symbol: '399006.SZ', name: '创业板指', current_price: 2055.12, change_percent: 0.67 }
              ],
              up_count: 3120,
              down_count: 1456,
              flat_count: 210,
              total_turnover: 128960000000
            })
          )
        })
        return
      }

      if (url.includes('/api/akshare/market/fund-flow/hsgt-summary')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(
            buildUnifiedResponse({
              hgt: { amount: 12.5, change: 1.2 },
              sgt: { amount: 8.3, change: -0.4 },
              northTotal: { amount: 20.8, monthly: 186.2 },
              mainForce: { amount: 15.4, percentage: 11.2 }
            })
          )
        })
        return
      }

      if (url.includes('/api/v2/market/sector/fund-flow')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(
            buildUnifiedResponse([
              { name: '算力', change: 2.56, amount: 36.5 },
              { name: '机器人', change: 1.78, amount: 22.4 }
            ])
          )
        })
        return
      }

      if (url.includes('/api/akshare/market/fund-flow/big-deal')) {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify(
            buildUnifiedResponse([
              { name: '东方财富', code: '300059', amount: 12.4, change: 3.1 }
            ])
          )
        })
        return
      }

      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse([]))
      })
    })
  })

  test('loads the dashboard root page from the dashboard market-overview contract only', async ({ page }) => {
    const requestUrls: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('/dashboard/market-overview') || request.url().includes('/v1/market/overview')) {
        requestUrls.push(request.url())
      }
    })

    await page.goto(`${FRONTEND_BASE_URL}/dashboard`)

    await expect(page.getByText('主要市场指标')).toBeVisible()
    await expect(page.getByText('3210.55')).toBeVisible()
    await expect(page.getByText('3120↑/1456↓')).toBeVisible()
    await expect(page.getByText('1289.6亿')).toBeVisible()
    await expect(page.getByText('REQ: req-dashboard-overview')).toBeVisible()
    await expect(page.getByText('策略状态待接入真实接口')).toBeVisible()
    await expect(page.getByText('当前页面仅保留真实生产链路，股票池表现待接入独立持仓/自选接口。')).toBeVisible()

    expect(requestUrls.some((url) => url.includes('/api/dashboard/market-overview'))).toBeTruthy()
    expect(requestUrls.some((url) => url.includes('/api/v1/market/overview'))).toBeFalsy()
  })
})
