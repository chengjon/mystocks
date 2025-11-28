import { test, expect } from '@playwright/test'
import { setPageTimeouts, smartWaitForElement } from './test-helpers'

test.describe('Phase 9 P2 Pages Integration Tests', () => {
  // 测试配置
  const BASE_URL = process.env.PLAYWRIGHT_TEST_BASE_URL || 'http://localhost:3001'
  const API_BASE = 'http://localhost:8000'

  test.beforeEach(async ({ page, browserName }) => {
    // 设置浏览器特定超时
    setPageTimeouts(page, browserName)

    // 预热后端服务 - 发送初始请求以唤醒服务
    try {
      await page.request.get(`${API_BASE}/health`)
    } catch (e) {
      // 忽略预热请求的失败
    }
  })

  // ==================== AnnouncementMonitor Tests ====================
  test.describe('AnnouncementMonitor.vue', () => {
    test('should load announcement monitor page', async ({ page, browserName }) => {
      await page.goto(`${BASE_URL}/#/demo/announcement`, { waitUntil: 'domcontentloaded' })
      await expect(page).toHaveTitle(/MyStocks/)
      // 用 domcontentloaded 代替 networkidle，避免 Firefox 长时间等待
      await page.waitForLoadState('domcontentloaded')
      // 额外等待确保组件加载完成
      if (browserName === 'firefox') {
        await page.waitForTimeout(2000)
      } else if (browserName === 'webkit') {
        await page.waitForTimeout(1500)
      }
    })

    test('should display announcement statistics', async ({ page }) => {
      // 直接测试API
      const response = await page.request.get(`${API_BASE}/api/announcement/stats`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.total_count).toBeGreaterThanOrEqual(0)
    })

    test('should fetch announcement list with pagination', async ({ page }) => {
      const response = await page.request.get(
        `${API_BASE}/api/announcement/list?page=1&page_size=20`
      )
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(Array.isArray(data.data)).toBe(true)
    })

    test('should get today announcements', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/announcement/today`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.date).toBeDefined()
    })

    test('should get important announcements', async ({ page }) => {
      const response = await page.request.get(
        `${API_BASE}/api/announcement/important?days=7&min_importance=3`
      )
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
    })

    test('should fetch monitor rules', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/announcement/monitor-rules`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(Array.isArray(data)).toBe(true)
    })

    test('should get triggered records', async ({ page }) => {
      const response = await page.request.get(
        `${API_BASE}/api/announcement/triggered-records?page=1&page_size=20`
      )
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(Array.isArray(data.data)).toBe(true)
    })
  })

  // ==================== DatabaseMonitor Tests ====================
  test.describe('DatabaseMonitor.vue', () => {
    test('should load database monitor page', async ({ page, browserName }) => {
      await page.goto(`${BASE_URL}/#/demo/database-monitor`, { waitUntil: 'domcontentloaded' })
      await expect(page).toHaveTitle(/MyStocks/)
      // 用 domcontentloaded 代替 networkidle，避免 Firefox 长时间等待
      await page.waitForLoadState('domcontentloaded')
      // 额外等待确保组件加载完成
      if (browserName === 'firefox') {
        await page.waitForTimeout(2000)
      } else if (browserName === 'webkit') {
        await page.waitForTimeout(1500)
      }
    })

    test('should fetch database health status', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/system/database/health`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.data).toHaveProperty('tdengine')
      expect(data.data).toHaveProperty('postgresql')
    })

    test('should fetch database statistics', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/system/database/stats`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.data).toHaveProperty('connections')
      expect(data.data).toHaveProperty('tables')
    })

    test('database health check shows connection status', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/system/database/health`)
      const data = await response.json()
      expect(data.data.summary).toHaveProperty('total_databases')
      expect(data.data.summary).toHaveProperty('healthy')
    })
  })

  // ==================== TradeManagement Tests ====================
  test.describe('TradeManagement.vue', () => {
    test('should load trade management page', async ({ page, browserName }) => {
      await page.goto(`${BASE_URL}/#/trade`, { waitUntil: 'domcontentloaded' })
      await expect(page).toHaveTitle(/MyStocks/)
      // 用 domcontentloaded 代替 networkidle，避免 Firefox 长时间等待
      await page.waitForLoadState('domcontentloaded')
      // 额外等待确保组件加载完成
      if (browserName === 'firefox') {
        await page.waitForTimeout(2000)
      } else if (browserName === 'webkit') {
        await page.waitForTimeout(1500)
      }
    })

    test('should fetch portfolio overview', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/trade/portfolio`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.data).toHaveProperty('total_assets')
      expect(data.data).toHaveProperty('available_cash')
      expect(data.data).toHaveProperty('position_value')
      expect(data.data).toHaveProperty('total_profit')
      expect(data.data.total_assets).toBeGreaterThan(0)
    })

    test('should fetch positions list', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/trade/positions`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(Array.isArray(data.data)).toBe(true)
      if (data.data.length > 0) {
        const position = data.data[0]
        expect(position).toHaveProperty('symbol')
        expect(position).toHaveProperty('stock_name')
        expect(position).toHaveProperty('quantity')
        expect(position).toHaveProperty('cost_price')
        expect(position).toHaveProperty('current_price')
      }
    })

    test('should fetch trade history with pagination', async ({ page }) => {
      const response = await page.request.get(
        `${API_BASE}/api/trade/trades?page=1&page_size=20`
      )
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(Array.isArray(data.data)).toBe(true)
      expect(data).toHaveProperty('page')
      expect(data).toHaveProperty('page_size')
      expect(data).toHaveProperty('total')
    })

    test('should filter trades by type', async ({ page }) => {
      const response = await page.request.get(
        `${API_BASE}/api/trade/trades?trade_type=buy&page=1&page_size=20`
      )
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(Array.isArray(data.data)).toBe(true)
    })

    test('should fetch trade statistics', async ({ page }) => {
      const response = await page.request.get(`${API_BASE}/api/trade/statistics`)
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.data).toHaveProperty('total_trades')
      expect(data.data).toHaveProperty('buy_count')
      expect(data.data).toHaveProperty('sell_count')
      expect(data.data).toHaveProperty('realized_profit')
      expect(data.data.total_trades).toBeGreaterThanOrEqual(0)
    })

    test('should execute a buy trade', async ({ page }) => {
      const tradeData = {
        type: 'buy',
        symbol: '000001',
        quantity: 100,
        price: 10.5,
        remark: 'E2E test buy'
      }
      const response = await page.request.post(`${API_BASE}/api/trade/execute`, {
        data: tradeData
      })
      expect(response.ok()).toBeTruthy()
      const data = await response.json()
      expect(data.success).toBe(true)
      expect(data.data).toHaveProperty('trade_id')
      expect(data.data).toHaveProperty('status')
      expect(data.data.trade_amount).toBe(1050)
    })

    test('should reject invalid trade (missing fields)', async ({ page }) => {
      const invalidTrade = {
        type: 'buy',
        symbol: '000001'
        // Missing quantity and price
      }
      const response = await page.request.post(`${API_BASE}/api/trade/execute`, {
        data: invalidTrade
      })
      expect(response.status()).toBe(400)
    })
  })

  // ==================== MarketDataView Tests ====================
  test.describe('MarketDataView.vue', () => {
    test('should load market data view page', async ({ page, browserName }) => {
      await page.goto(`${BASE_URL}/#/market-data`, { waitUntil: 'domcontentloaded' })
      await expect(page).toHaveTitle(/MyStocks/)
      // 用 domcontentloaded 代替 networkidle，避免 Firefox 长时间等待
      await page.waitForLoadState('domcontentloaded')
      // 额外等待确保组件加载完成
      if (browserName === 'firefox') {
        await page.waitForTimeout(2000)
      } else if (browserName === 'webkit') {
        await page.waitForTimeout(1500)
      }
    })

    test('should display market data tabs', async ({ page, browserName }) => {
      await page.goto(`${BASE_URL}/#/market-data`, { waitUntil: 'domcontentloaded' })
      // 额外等待确保组件加载完成
      if (browserName === 'firefox') {
        await page.waitForTimeout(2000)
      } else if (browserName === 'webkit') {
        await page.waitForTimeout(1500)
      }
      // 使用智能等待处理Firefox/WebKit的延迟
      await smartWaitForElement(page, '.el-tabs', browserName)

      // 检查标签页是否存在 - 通过el-tab-pane标签查找
      const tabPanes = page.locator('.el-tab-pane')
      const paneCount = await tabPanes.count()

      // 应该至少有1个标签页
      expect(paneCount).toBeGreaterThanOrEqual(1)
    })
  })

  // ==================== Integration Tests ====================
  test.describe('Cross-Page Integration', () => {
    test('should navigate between all P2 pages without errors', async ({ page }) => {
      const pages = [
        `${BASE_URL}/#/demo/announcement`,
        `${BASE_URL}/#/demo/database-monitor`,
        `${BASE_URL}/#/trade`,
        `${BASE_URL}/#/market-data`
      ]

      for (const pageUrl of pages) {
        const response = await page.goto(pageUrl, { waitUntil: 'domcontentloaded' })
        if (response) {
          expect(response.status()).toBeLessThan(400)
        }
      }
    })

    test('should verify all backend services are healthy', async ({ page }) => {
      const endpoints = [
        `${API_BASE}/health`,
        `${API_BASE}/api/announcement/health`,
        `${API_BASE}/api/trade/health`,
        `${API_BASE}/api/system/health`
      ]

      for (const endpoint of endpoints) {
        const response = await page.request.get(endpoint)
        expect(response.ok()).toBeTruthy()
      }
    })

    test('should handle concurrent API requests', async ({ page }) => {
      const requests = [
        page.request.get(`${API_BASE}/api/announcement/stats`),
        page.request.get(`${API_BASE}/api/trade/portfolio`),
        page.request.get(`${API_BASE}/api/system/database/health`),
        page.request.get(`${API_BASE}/api/trade/statistics`)
      ]

      const responses = await Promise.all(requests)
      responses.forEach(response => {
        expect(response.ok()).toBeTruthy()
      })
    })
  })

  // ==================== Performance Tests ====================
  test.describe('Performance Metrics', () => {
    test('announcement API should respond within 500ms', async ({ page }) => {
      const startTime = Date.now()
      await page.request.get(`${API_BASE}/api/announcement/stats`)
      const duration = Date.now() - startTime
      expect(duration).toBeLessThan(500)
    })

    test('trade API should respond within 500ms', async ({ page }) => {
      const startTime = Date.now()
      await page.request.get(`${API_BASE}/api/trade/portfolio`)
      const duration = Date.now() - startTime
      expect(duration).toBeLessThan(500)
    })

    test('database API should respond within 1000ms', async ({ page }) => {
      const startTime = Date.now()
      await page.request.get(`${API_BASE}/api/system/database/health`)
      const duration = Date.now() - startTime
      expect(duration).toBeLessThan(1000)
    })
  })
})
