"""
E2E数据流集成测试 - 使用Playwright验证完整数据流

核心功能：
1. API调用到前端数据接收的完整流程
2. 数据在UI控件中的正确显示
3. 用户交互触发的数据更新
4. 跨页面数据状态同步
"""

import { test, expect, Page } from '@playwright/test'
import { APIContractValidator } from './api_contract_tests'

// 测试配置
const TEST_CONFIG = {
  baseURL: 'http://localhost:3001', // 前端URL
  apiURL: 'http://localhost:8000',   // 后端API URL
  testData: {
    marketOverview: {
      indices: [
        { symbol: '000001', name: '平安银行', current_price: 10.5, change_percent: 2.1 },
        { symbol: '600036', name: '招商银行', current_price: 38.9, change_percent: -0.8 }
      ],
      up_count: 2456,
      down_count: 1234,
      flat_count: 567
    },
    tradingSignals: [
      {
        id: 'SIG001',
        symbol: '600036',
        name: '招商银行',
        type: '买入',
        price: 38.9,
        confidence: 0.85,
        status: '待执行'
      }
    ]
  }
}

// 页面对象模型
class ArtDecoTradingCenterPage {
  constructor(private page: Page) {}

  async goto() {
    await this.page.goto('/artdeco/trading-center')
    await this.page.waitForLoadState('networkidle')
  }

  async waitForDataLoad() {
    // 等待数据加载完成
    await this.page.waitForSelector('.trading-management-content', { timeout: 10000 })
  }

  async getMarketStats() {
    const statsCard = this.page.locator('.overview-card')
    return {
      title: await statsCard.locator('h3').textContent(),
      signalsCount: await statsCard.locator('.count-badge').first().textContent()
    }
  }

  async getRealtimeSignals() {
    const signalsPanel = this.page.locator('.realtime-panel')
    const signalItems = signalsPanel.locator('.trading-signal-item')
    const count = await signalItems.count()

    const signals = []
    for (let i = 0; i < count; i++) {
      const item = signalItems.nth(i)
      signals.push({
        symbol: await item.locator('.signal-symbol').textContent(),
        type: await item.locator('.signal-type').textContent(),
        price: await item.locator('.signal-price').textContent(),
        status: await item.locator('.signal-status').textContent()
      })
    }

    return signals
  }

  async refreshData() {
    const refreshButton = this.page.locator('button:has-text("刷新数据")')
    await refreshButton.click()

    // 等待刷新完成（加载状态消失）
    await this.page.waitForSelector('[loading="false"]', { timeout: 5000 })
  }

  async verifyDataSynchronization(expectedData: any) {
    // 验证市场统计数据
    const marketStats = await this.getMarketStats()
    expect(marketStats.signalsCount).toBe(expectedData.signalsCount.toString())

    // 验证交易信号数据
    const signals = await this.getRealtimeSignals()
    expect(signals.length).toBeGreaterThan(0)

    // 验证信号数据结构
    const firstSignal = signals[0]
    expect(firstSignal).toHaveProperty('symbol')
    expect(firstSignal).toHaveProperty('type')
    expect(firstSignal).toHaveProperty('price')
    expect(firstSignal).toHaveProperty('status')
  }
}

// API Mock工具
class APIMockServer {
  constructor(private baseURL: string) {}

  async mockMarketOverview(data: any) {
    // 这里可以实现API响应的mock
    // 使用Playwright的route API来拦截和模拟API调用
    console.log('Mocking market overview API with:', data)
  }

  async mockTradingSignals(data: any) {
    console.log('Mocking trading signals API with:', data)
  }

  async resetMocks() {
    // 重置所有mock
    console.log('Resetting API mocks')
  }
}

// 数据流验证器
class DataFlowValidator {
  constructor(private page: Page) {}

  async validateAPICall(endpoint: string, expectedData: any) {
    // 监听网络请求
    const [response] = await Promise.all([
      this.page.waitForResponse(resp => resp.url().includes(endpoint)),
      // 触发导致API调用的用户操作
      this.page.click('button:has-text("刷新数据")')
    ])

    expect(response.status()).toBe(200)

    const responseData = await response.json()
    // 验证响应数据结构
    this.validateDataStructure(responseData, expectedData)
  }

  private validateDataStructure(actual: any, expected: any) {
    // 递归验证数据结构
    if (typeof expected === 'object' && expected !== null) {
      for (const key in expected) {
        expect(actual).toHaveProperty(key)

        if (typeof expected[key] === 'object') {
          this.validateDataStructure(actual[key], expected[key])
        } else {
          expect(typeof actual[key]).toBe(typeof expected[key])
        }
      }
    }
  }

  async validateUIDisplay(expectedUIElements: any) {
    // 验证UI元素正确显示
    for (const [selector, expectedText] of Object.entries(expectedUIElements)) {
      const element = this.page.locator(selector)
      await expect(element).toContainText(expectedText as string)
    }
  }

  async validateDataBinding(apiData: any, uiSelectors: any) {
    // 验证API数据是否正确绑定到UI
    for (const [apiField, uiSelector] of Object.entries(uiSelectors)) {
      if (apiData[apiField]) {
        const uiElement = this.page.locator(uiSelector as string)
        await expect(uiElement).toBeVisible()

        // 验证数据值是否正确显示
        const expectedValue = apiData[apiField].toString()
        await expect(uiElement).toContainText(expectedValue)
      }
    }
  }
}

// 测试套件
test.describe('数据同步E2E测试', () => {
  let tradingPage: ArtDecoTradingCenterPage
  let apiMock: APIMockServer
  let dataValidator: DataFlowValidator
  let apiContractValidator: APIContractValidator

  test.beforeEach(async ({ page }) => {
    tradingPage = new ArtDecoTradingCenterPage(page)
    apiMock = new APIMockServer(TEST_CONFIG.apiURL)
    dataValidator = new DataFlowValidator(page)
    apiContractValidator = new APIContractValidator(TEST_CONFIG.apiURL)

    // 设置API mock
    await apiMock.mockMarketOverview(TEST_CONFIG.testData.marketOverview)
    await apiMock.mockTradingSignals(TEST_CONFIG.testData.tradingSignals)
  })

  test.afterEach(async () => {
    await apiMock.resetMocks()
  })

  test('完整数据流 - API到UI显示', async ({ page }) => {
    // 1. 访问页面
    await tradingPage.goto()
    await tradingPage.waitForDataLoad()

    // 2. 验证初始数据加载
    const initialStats = await tradingPage.getMarketStats()
    expect(initialStats.title).toContain('交易概览')

    // 3. 验证API调用和数据结构
    await dataValidator.validateAPICall('/api/market/overview', TEST_CONFIG.testData.marketOverview)

    // 4. 验证UI数据绑定
    await dataValidator.validateDataBinding(
      TEST_CONFIG.testData.marketOverview,
      {
        up_count: '.stats-up-count',
        down_count: '.stats-down-count',
        total_volume: '.stats-volume'
      }
    )

    // 5. 验证用户交互触发数据更新
    await tradingPage.refreshData()

    // 6. 验证数据更新后的UI状态
    const updatedSignals = await tradingPage.getRealtimeSignals()
    expect(updatedSignals.length).toBeGreaterThan(0)
  })

  test('实时数据同步', async ({ page }) => {
    await tradingPage.goto()
    await tradingPage.waitForDataLoad()

    // 模拟实时数据更新
    const initialSignals = await tradingPage.getRealtimeSignals()
    const initialCount = initialSignals.length

    // 触发数据刷新
    await tradingPage.refreshData()

    // 验证数据是否更新
    const updatedSignals = await tradingPage.getRealtimeSignals()
    expect(updatedSignals.length).toBe(initialCount) // 数据结构保持一致
  })

  test('错误处理和降级', async ({ page }) => {
    // 模拟API错误
    await page.route('**/api/market/overview', route => route.abort())

    await tradingPage.goto()

    // 验证错误状态的UI显示
    await expect(page.locator('.error-message')).toBeVisible()
    await expect(page.locator('.retry-button')).toBeVisible()

    // 验证重试功能
    await page.click('.retry-button')
    await expect(page.locator('.loading-indicator')).toBeVisible()
  })

  test('跨页面数据一致性', async ({ page }) => {
    // 访问交易中心页面
    await tradingPage.goto()
    await tradingPage.waitForDataLoad()

    const tradingSignals = await tradingPage.getRealtimeSignals()

    // 导航到仪表盘页面
    await page.goto('/artdeco/dashboard')
    await page.waitForLoadState('networkidle')

    // 验证数据在不同页面的一致性
    const dashboardSignals = await page.locator('.dashboard-signals').allTextContents()
    expect(dashboardSignals.length).toBe(tradingSignals.length)
  })

  test('性能和响应时间', async ({ page }) => {
    await tradingPage.goto()

    // 测量页面加载时间
    const startTime = Date.now()
    await tradingPage.waitForDataLoad()
    const loadTime = Date.now() - startTime

    // 验证加载时间在合理范围内
    expect(loadTime).toBeLessThan(5000) // 5秒内加载完成

    // 测量数据刷新时间
    const refreshStartTime = Date.now()
    await tradingPage.refreshData()
    const refreshTime = Date.now() - refreshStartTime

    expect(refreshTime).toBeLessThan(3000) // 3秒内刷新完成
  })

  test('API契约一致性验证', async () => {
    // 运行API契约测试
    const contractResults = await apiContractValidator.validate_api_contract('/api/market/overview')

    expect(contractResults.success).toBe(true)
    expect(contractResults.compatibility_score).toBeGreaterThan(0.8)
  })
})

// 集成测试报告生成器
export class E2ETestReporter {
  static generateReport(results: any) {
    return {
      summary: {
        total_tests: results.length,
        passed_tests: results.filter((r: any) => r.status === 'passed').length,
        failed_tests: results.filter((r: any) => r.status === 'failed').length,
        skipped_tests: results.filter((r: any) => r.status === 'skipped').length
      },
      details: results,
      recommendations: this.generateRecommendations(results)
    }
  }

  static generateRecommendations(results: any) {
    const recommendations = []

    const failedTests = results.filter((r: any) => r.status === 'failed')

    if (failedTests.some((t: any) => t.title.includes('API'))) {
      recommendations.push('检查API端点响应格式和数据结构')
    }

    if (failedTests.some((t: any) => t.title.includes('UI'))) {
      recommendations.push('验证UI组件的数据绑定和渲染逻辑')
    }

    if (failedTests.some((t: any) => t.title.includes('性能'))) {
      recommendations.push('优化数据加载和渲染性能')
    }

    return recommendations
  }
}

// 导出测试配置
export { TEST_CONFIG, ArtDecoTradingCenterPage, APIMockServer, DataFlowValidator }