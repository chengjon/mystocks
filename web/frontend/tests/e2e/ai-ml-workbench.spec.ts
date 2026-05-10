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

test.describe('AI ML workbench', () => {
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
        body: JSON.stringify(buildUnifiedResponse({ csrf_token: 'e2e-csrf' }, 'req-ai-ml-csrf')),
      })
    })

    await page.route('**/api/v1/strategies/ml/runtime-status', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              service_available: true,
              model_backend: 'runtime_registry',
              optional_dependencies: {
                lightgbm: { available: true, package: 'lightgbm' },
              },
              legacy_api_available: true,
              supported_operations: ['train', 'predict', 'models:list', 'models:detail'],
              warnings: [],
              safety: {
                analytical_output_only: true,
                disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.',
              },
            },
            'req-ai-ml-status',
          ),
        ),
      })
    })

    await page.route('**/api/v1/strategies/ml/models', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              models: [
                {
                  model_id: 'svm_600519_abc',
                  model_family: 'svm',
                  symbol: '600519.SH',
                  artifact_status: 'runtime_registered',
                  feature_context: { feature_window: 20, prediction_horizon: 5 },
                  metrics: { training_accuracy: 0.67, validation_score: 0.61 },
                  safety: {
                    analytical_output_only: true,
                    disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.',
                  },
                },
              ],
              total: 1,
            },
            'req-ai-ml-models',
          ),
        ),
      })
    })

    await page.route('**/api/v1/strategies/ml/train', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              model_id: 'svm_600519_abc',
              model_family: 'svm',
              symbol: '600519.SH',
              artifact_status: 'runtime_registered',
              feature_context: { feature_window: 20, prediction_horizon: 5 },
              metrics: { training_accuracy: 0.67, validation_score: 0.61 },
              safety: {
                analytical_output_only: true,
                disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.',
              },
            },
            'req-ai-ml-train',
          ),
        ),
      })
    })

    await page.route('**/api/v1/strategies/ml/predict', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              model_id: 'svm_600519_abc',
              model_family: 'svm',
              symbol: '600519.SH',
              prediction_horizon: 5,
              prediction: { signal: 'buy', expected_return: 0.018, prediction_horizon: 5 },
              confidence: 0.72,
              feature_context: { feature_window: 20, prediction_horizon: 5 },
              safety: {
                analytical_output_only: true,
                disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.',
              },
            },
            'req-ai-ml-predict',
          ),
        ),
      })
    })
  })

  test('renders runtime, trains a model, and runs prediction without trading semantics', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/ai/ml`)

    await expect(page.getByRole('heading', { name: '模型训练 / 预测' })).toBeVisible({ timeout: 15000 })
    await expect(page.locator('.status-band')).toContainText('运行时可用')
    await expect(page.locator('.ai-ml-workbench')).toContainText('not a trade instruction')
    await expect(page.getByTestId('ml-model-family')).toHaveValue('svm')
    await expect(page.getByTestId('ml-model-family')).toContainText('LightGBM · available')
    await expect(page.locator('[data-testid="ml-model-row"]')).toContainText('svm_600519_abc')

    await page.getByTestId('ml-train-submit').click()
    await expect(page.locator('.result-panel')).toContainText('svm_600519_abc')

    await page.getByTestId('ml-predict-submit').click()
    await expect(page.locator('.result-panel')).toContainText('buy')
    await expect(page.locator('.result-panel')).toContainText('0.72')
  })

  test('disables actions when runtime does not advertise train or predict support', async ({ page }) => {
    await page.unroute('**/api/v1/strategies/ml/runtime-status')
    await page.route('**/api/v1/strategies/ml/runtime-status', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              service_available: true,
              model_backend: 'runtime_registry',
              optional_dependencies: {
                lightgbm: { available: true, package: 'lightgbm' },
              },
              legacy_api_available: true,
              supported_operations: ['models:list', 'models:detail'],
              warnings: ['train_unsupported', 'predict_unsupported'],
              safety: {
                analytical_output_only: true,
                disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.',
              },
            },
            'req-ai-ml-status-unsupported-operations',
          ),
        ),
      })
    })

    await page.goto(`${FRONTEND_BASE_URL}/ai/ml`)

    await expect(page.getByRole('heading', { name: '模型训练 / 预测' })).toBeVisible({ timeout: 15000 })
    await expect(page.locator('.ai-ml-workbench')).toContainText('当前 ML 运行时不支持训练')
    await expect(page.locator('.ai-ml-workbench')).toContainText('当前 ML 运行时不支持预测')
    await expect(page.getByTestId('ml-train-submit')).toBeDisabled()
    await expect(page.getByTestId('ml-predict-submit')).toBeDisabled()
  })

  test('disables prediction when manual symbol differs from selected model scope', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/ai/ml`)

    await expect(page.getByRole('heading', { name: '模型训练 / 预测' })).toBeVisible({ timeout: 15000 })
    const predictionPanel = page.locator('.panel').filter({ hasText: '预测推理' })
    await predictionPanel.getByLabel('标的').fill('000001.SZ')

    await expect(page.locator('.ai-ml-workbench')).toContainText('预测标的必须与所选模型一致')
    await expect(page.getByTestId('ml-predict-submit')).toBeDisabled()
  })
})
