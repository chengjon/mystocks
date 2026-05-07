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

test.describe('System resources page', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 900 })
    await setupAuthenticatedSession(page)

    const fulfillResources = async (route: Parameters<Parameters<typeof page.route>[1]>[0]) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(
          buildUnifiedResponse(
            {
              node: {
                node_id: 'local-runtime',
                scope: 'single-node',
                sampled_at: '2026-05-07T00:00:00+00:00',
                window_minutes: 60,
                polling_interval_seconds: 15,
                overall_status: 'warning',
              },
              host: {
                cpu: {
                  metric_key: 'cpu_percent',
                  label: 'CPU',
                  unit: '%',
                  current_value: 82.5,
                  status: 'warning',
                  warning_threshold: 70,
                  critical_threshold: 90,
                  series: [
                    { timestamp: '2026-05-06T23:59:45+00:00', value: 80.0 },
                    { timestamp: '2026-05-07T00:00:00+00:00', value: 82.5 },
                  ],
                  meta: { cpu_count: 8 },
                },
                memory: {
                  metric_key: 'memory_percent',
                  label: '内存',
                  unit: '%',
                  current_value: 64.2,
                  status: 'normal',
                  warning_threshold: 75,
                  critical_threshold: 90,
                  series: [{ timestamp: '2026-05-07T00:00:00+00:00', value: 64.2 }],
                  meta: { used_gb: 8, total_gb: 16 },
                },
                disk: {
                  metric_key: 'disk_percent',
                  label: '磁盘',
                  unit: '%',
                  current_value: 91.2,
                  status: 'critical',
                  warning_threshold: 80,
                  critical_threshold: 90,
                  series: [{ timestamp: '2026-05-07T00:00:00+00:00', value: 91.2 }],
                  meta: { used_gb: 910, total_gb: 1000 },
                },
                load: {
                  metric_key: 'load_percent',
                  label: '负载',
                  unit: '%',
                  current_value: 24.0,
                  status: 'normal',
                  warning_threshold: 70,
                  critical_threshold: 90,
                  series: [{ timestamp: '2026-05-07T00:00:00+00:00', value: 24.0 }],
                  meta: { load_average_1m: 1.92, cpu_count: 8 },
                },
              },
              processes: [
                {
                  process_key: 'mystocks-backend',
                  display_name: 'mystocks-backend',
                  status: 'normal',
                  pid: 1234,
                  cpu_percent: 12.4,
                  memory_mb: 512.0,
                  memory_percent: 5.0,
                  sampled_at: '2026-05-07T00:00:00+00:00',
                  started_at: '2026-05-06T23:00:00+00:00',
                  thresholds: {},
                  summary: 'cpu=12.4% memory=5.0%',
                },
              ],
              dependencies: [
                {
                  dependency_key: 'postgresql',
                  display_name: 'PostgreSQL',
                  status: 'normal',
                  summary: 'pool healthy',
                  sampled_at: '2026-05-07T00:00:00+00:00',
                  warning_threshold: 70,
                  critical_threshold: 90,
                  metrics: { active_connections: 2, usage_percentage: 20.0 },
                },
              ],
              thresholds: {
                'host.cpu_percent': { warning: 70, critical: 90, unit: '%' },
              },
            },
            'req-system-resources-1',
          ),
        ),
      })
    }

    await page.route('**/api/v1/system/resources**', fulfillResources)
    await page.route('**/v1/system/resources**', fulfillResources)
  })

  test('renders resource usage deck from the unified v1 system resources contract', async ({ page }) => {
    await page.goto(`${FRONTEND_BASE_URL}/system/resources`)

    await expect(page.getByRole('heading', { name: '资源使用工作台' })).toBeVisible({ timeout: 15000 })
    await expect(page.locator('.hero-meta')).toContainText('REQ_ID: req-system-resources-1')
    await expect(page.locator('.hero-meta')).toContainText('STATUS: WARNING')
    await expect(page.locator('.host-grid')).toContainText('CPU')
    await expect(page.locator('.host-grid')).toContainText('82.5%')
    await expect(page.locator('.host-grid')).toContainText('CRITICAL')
    await expect(page.locator('.resource-lower-grid')).toContainText('mystocks-backend')
    await expect(page.locator('.resource-lower-grid')).toContainText('PostgreSQL')
    await expect(page.getByRole('button', { name: '暂停轮询' })).toBeVisible()
  })
})
