import { expect, test } from '@playwright/test'
const { loadPortEnv, resolveFrontendConfig } = require('./helpers/port-env.js')

loadPortEnv(process.cwd())

const FRONTEND_BASE_URL = resolveFrontendConfig().baseUrl

test.use({ serviceWorkers: 'block' })

function buildUnifiedResponse<T>(data: T, requestId: string) {
  return {
    success: true,
    code: 200,
    message: 'ok',
    data,
    timestamp: '2026-05-07T00:00:00Z',
    request_id: requestId,
  }
}

async function setupAuthenticatedSession(page: Parameters<typeof test>[0]['page']) {
  await page.addInitScript(() => {
    const user = {
      id: 1,
      username: 'e2e-admin',
      email: 'e2e-admin@mystocks.local',
      role: 'admin',
      permissions: ['*'],
    }
    localStorage.setItem('auth_token', 'e2e-token')
    localStorage.setItem('auth_user', JSON.stringify(user))
  })
}

test.describe('AI sentiment workbench', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)

    const fulfillAnnouncements = async (route: Parameters<Parameters<typeof page.route>[1]>[0]) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            [
              {
                stock_code: '600519',
                stock_name: '贵州茅台',
                announcement_type: '年度报告',
                announcement_title: '年度报告披露',
                publish_date: '2026-05-07',
                publish_time: '10:30:00',
                importance_level: 4,
                url: 'https://example.com/600519',
              },
              {
                stock_code: '000001',
                stock_name: '平安银行',
                announcement_type: '临时公告',
                announcement_title: '董事会决议',
                publish_date: '2026-05-06',
                publish_time: '09:15:00',
                importance_level: 2,
                url: null,
              },
            ],
            'req-ai-sentiment-workbench-1',
          ),
        ),
      })
    }

    const fulfillMarket = async (route: Parameters<Parameters<typeof page.route>[1]>[0]) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              sentiment: 'positive',
              average_sentiment: 0.67,
              coverage: 18,
              positive_ratio: 0.61,
              negative_ratio: 0.19,
              neutral_ratio: 0.20,
              hot_symbols: ['600519', '000001'],
              updated_at: '2026-05-07T00:00:00Z',
            },
            'req-ai-sentiment-workbench-1',
          ),
        ),
      })
    }

    const fulfillStock = async (route: Parameters<Parameters<typeof page.route>[1]>[0]) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              symbol: '600519',
              days: 7,
              mentions: 12,
              average_sentiment: 0.61,
              trend: 'positive',
              latest_sentiment: 'positive',
              latest_confidence: 0.88,
              timeline: [
                { date: '2026-05-06', sentiment: 'positive', score: 0.58, confidence: 0.82 },
                { date: '2026-05-07', sentiment: 'positive', score: 0.64, confidence: 0.88 },
              ],
            },
            'req-ai-sentiment-workbench-1',
          ),
        ),
      })
    }

    await page.route('**/announcement/list**', fulfillAnnouncements)
    await page.route('**/api/v1/sentiment/market**', fulfillMarket)
    await page.route('**/api/v1/sentiment/stock/**', fulfillStock)
  })

  test('renders the canonical ai sentiment page with news feed and analysis panels', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/ai/sentiment`)

    await expect(page.getByRole('heading', { name: '情感分析工作台' })).toBeVisible({ timeout: 15000 })
    await expect(page.getByTestId('ai-sentiment-page')).toBeVisible()
    await expect(page.getByTestId('ai-sentiment-header')).toBeVisible()
    await expect(page.getByTestId('ai-sentiment-header')).toContainText('REQ_ID: req-ai-sentiment-workbench-1')
    await expect(page.getByTestId('ai-sentiment-header')).toContainText('DOMAIN: AI')
    await expect(page.getByTestId('ai-sentiment-header')).toContainText('ENTRY: sentiment')
    await expect(page.getByTestId('ai-sentiment-header')).toContainText('AI 工作台在线')
    await expect(page.getByTestId('ai-sentiment-header').getByTestId('ai-sentiment-refresh')).toBeVisible()
    await expect(page.getByTestId('ai-sentiment-status-strip')).toBeVisible()
    await expect(page.getByTestId('ai-sentiment-primary-surface')).toBeVisible()
    await expect(page.locator('.content-shell-title')).toContainText('AI 情感工作台')
    await expect(page.locator('.workspace-grid')).toContainText('年度报告披露')
    await expect(page.locator('.workspace-grid')).toContainText('positive')
    await expect(page.getByRole('button', { name: '分析文本' })).toBeVisible()
  })

  test('keeps risk news as a wrapper entry and links back into the canonical ai page', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/risk/news`)

    await expect(page.getByRole('heading', { name: '舆情预警' })).toBeVisible({ timeout: 15000 })
    await expect(page.locator('.hero-meta')).toContainText('FOCUS: risk wrapper')
    await expect(page.locator('.content-shell-meta')).toContainText('LINKED: 1')

    await page.getByRole('button', { name: '前往 AI 工作台' }).click()

    await expect(page).toHaveURL(/\/ai\/sentiment$/)
    await expect(page.getByRole('heading', { name: '情感分析工作台' })).toBeVisible()
  })
})
