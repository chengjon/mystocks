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
    timestamp: '2026-05-10T00:00:00Z',
    request_id: requestId,
  }
}

const safety = {
  analytical_output_only: true,
  disclaimer: 'Batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.',
}

const task = {
  task_id: 'batch_abc',
  operation: 'batch_screening',
  symbols: ['600519.SH', '000001.SZ'],
  status: 'completed',
  summary: {
    total_symbols: 2,
    completed_symbols: 2,
    failed_symbols: 0,
    candidate_count: 1,
    average_score: 0.66,
  },
  results: [
    { symbol: '600519.SH', status: 'completed', score: 0.72, signal: 'candidate', metrics: {} },
    { symbol: '000001.SZ', status: 'completed', score: 0.58, signal: 'watch', metrics: {} },
  ],
  warnings: [],
  safety,
}

test.describe('AI batch analysis workbench', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
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

    await page.route('**/api/csrf-token', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse({ csrf_token: 'e2e-csrf' }, 'req-ai-batch-csrf')),
      })
    })

    await page.route('**/api/v1/strategies/batch-analysis/runtime-status', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              service_available: true,
              runtime_backend: 'runtime_batch_registry',
              max_symbols: 20,
              supported_operations: ['batch_backtest', 'batch_screening', 'batch_monitoring'],
              evidence_modules: ['src/ml_strategy/backtest/backtest_engine.py'],
              warnings: [],
              safety,
            },
            'req-ai-batch-status',
          ),
        ),
      })
    })

    await page.route('**/api/v1/strategies/batch-analysis/tasks', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse({ tasks: [task], total: 1 }, 'req-ai-batch-tasks')),
      })
    })

    await page.route('**/api/v1/strategies/batch-analysis/tasks/batch_abc', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse(task, 'req-ai-batch-detail')),
      })
    })

    await page.route('**/api/v1/strategies/batch-analysis/submit', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(buildUnifiedResponse(task, 'req-ai-batch-submit')),
      })
    })
  })

  test('renders runtime, submits batch analysis, and displays analytical evidence', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/ai/batch`)

    await expect(page.getByRole('heading', { name: '批量分析' })).toBeVisible({ timeout: 15000 })
    await expect(page.locator('.status-band')).toContainText('运行时可用')
    await expect(page.locator('.ai-batch-workbench')).toContainText('not automated trading')
    await expect(page.locator('[data-testid="batch-analysis-task-row"]')).toContainText('batch_abc')

    await page.getByTestId('batch-analysis-submit').click()
    await expect(page.locator('.summary-panel')).toContainText('batch_abc')
    await expect(page.locator('.summary-panel')).toContainText('0.66')
    await expect(page.locator('[data-testid="batch-analysis-result-row"]').first()).toContainText('600519.SH')
  })
})
