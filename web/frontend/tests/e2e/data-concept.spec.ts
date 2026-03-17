import { expect, test } from '@playwright/test'

const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl
const CONCEPT_ENDPOINTS = [
  '**/api/v2/market/sector/fund-flow**',
  '**/api/api/v2/market/sector/fund-flow**'
]

function buildUnifiedResponse<T>(data: T, overrides?: Partial<Record<string, unknown>>) {
  return {
    success: true,
    code: 200,
    message: 'ok',
    data,
    timestamp: '2026-03-11T00:00:00Z',
    request_id: 'req-data-concept-default',
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
            {
              status: 'ready'
            },
            { request_id: 'req-data-concept-ready', message: 'backend ready' }
          )
        )
      })
    })
  }
}

async function routeConceptFlow(
  page: Parameters<typeof test>[0]['page'],
  handler: Parameters<typeof page.route>[1]
) {
  for (const endpoint of CONCEPT_ENDPOINTS) {
    await page.route(endpoint, handler)
  }
}

test.describe('Data Concept Page', () => {
  test.describe.configure({ mode: 'serial', timeout: 120000 })

  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)
    await mockSupportEndpoints(page)
  })

  test('loads real concept flow rows from the v2 sector contract', async ({ page }) => {
    const requestUrls: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('/v2/market/sector/fund-flow')) {
        requestUrls.push(request.url())
      }
    })

    await routeConceptFlow(page, async (route) => {
      await route.fulfill({
        status: 200,
        headers: {
          'content-type': 'application/json',
          'x-request-id': 'req-data-concept-success',
          'x-process-time': '42ms'
        },
        body: JSON.stringify(
          buildUnifiedResponse([
            {
              sector_code: 'BK0637',
              sector_name: '互联金融',
              sector_type: '概念',
              change_percent: 1.75,
              main_net_inflow: 5900209920,
              leading_stock: '东方财富'
            }
          ])
        )
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`)

    await expect(page.getByRole('heading', { name: 'Concept Sectors' })).toBeVisible()
    await expect(page.getByText('互联金融')).toBeVisible()
    await expect(page.getByText('+1.75%')).toBeVisible()
    await expect(page.getByText('+59.0亿')).toBeVisible()
    expect(requestUrls.some((url) => url.includes('sector_type=%E6%A6%82%E5%BF%B5'))).toBeTruthy()
  })

  test('shows an explicit empty state instead of fake fallback rows when the real call fails', async ({ page }) => {
    await routeConceptFlow(page, async (route) => {
      await route.fulfill({
        status: 500,
        headers: {
          'content-type': 'application/json',
          'x-request-id': 'req-data-concept-failed'
        },
        body: JSON.stringify(
          buildUnifiedResponse(null, {
            success: false,
            code: 500,
            message: '概念接口失败'
          })
        )
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/data/concept`)

    await expect(page.getByText('概念数据加载失败')).toBeVisible()
    await expect(page.getByText('暂无概念资金流向数据')).toBeVisible()
    await expect(page.getByText('低空经济')).toHaveCount(0)
  })
})
