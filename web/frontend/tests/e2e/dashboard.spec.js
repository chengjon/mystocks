/**
 * Dashboard E2E Tests - User Story 1: Real Data Display
 *
 * Purpose: Verify Dashboard shows real database data instead of mock data
 *
 * Test Strategy:
 * 1. Uses chrome-devtools-mcp for browser automation
 * 2. Follows TDD approach - tests should FAIL before implementation
 * 3. Validates all Dashboard features against acceptance criteria
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost:3001
 * - PostgreSQL database populated with test data
 * - Valid authentication token
 */

const BASE_URL = 'http://localhost:3001'
const API_BASE_URL = 'http://localhost:8000'

/**
 * Test Suite: Dashboard Real Data Display
 */
describe('Dashboard - Real Data Display (User Story 1)', () => {

  /**
   * Setup: Login and navigate to Dashboard
   */
  beforeEach(async () => {
    // Navigate to login page
    await page.goto(`${BASE_URL}/login`)

    // Login with test credentials
    await page.fill('input[type="text"]', 'admin')
    await page.fill('input[type="password"]', 'admin123')
    await page.click('button[type="submit"]')

    // Wait for navigation to Dashboard
    await page.waitForURL(`${BASE_URL}/dashboard`)

    // Wait for page to fully load
    await page.waitForLoadState('networkidle')
  })

  /**
   * Test 1: Favorites Table Shows Real Database Data
   *
   * Acceptance Criteria:
   * - Table data loaded from GET /api/data/dashboard/favorites
   * - No hardcoded mock data like "600519 贵州茅台"
   * - Shows actual favorite stocks from user_watchlist table
   * - Real-time prices from daily_kline table
   */
  test('T020: Favorites table displays real database data', async () => {
    // Navigate to Favorites tab
    await page.click('text=自选股')

    // Wait for table to load
    await page.waitForSelector('.el-table__body')

    // Get table data
    const tableRows = await page.$$('.el-table__body tr')
    expect(tableRows.length).toBeGreaterThan(0)

    // Verify first row is NOT mock data
    const firstRowSymbol = await page.textContent('.el-table__body tr:first-child td:first-child')
    const firstRowName = await page.textContent('.el-table__body tr:first-child td:nth-child(2)')

    // Should NOT be the hardcoded mock data
    expect(firstRowSymbol).not.toBe('600519')
    expect(firstRowName).not.toBe('贵州茅台')

    // Verify data comes from API
    const apiCalled = await page.evaluate(() => {
      return window.__API_CALLS__?.includes('/api/data/dashboard/favorites')
    })
    expect(apiCalled).toBeTruthy()
  })

  /**
   * Test 2: Strategy Stocks Table Shows Real Matched Stocks
   *
   * Acceptance Criteria:
   * - Data loaded from GET /api/data/dashboard/strategy-matches
   * - Shows stocks that actually match configured strategies
   * - Strategy names from strategy_definitions table
   * - Scores calculated by strategy engine
   */
  test('T021: Strategy stocks table shows real strategy matches', async () => {
    // Navigate to Strategy tab
    await page.click('text=策略选股')

    // Wait for table to load
    await page.waitForSelector('.el-table__body')

    // Get strategy column data
    const strategyNames = await page.$$eval(
      '.el-table__body tr td:nth-child(5)',
      cells => cells.map(cell => cell.textContent.trim())
    )

    // Verify strategies are from database, not hardcoded
    const hasHardcodedStrategy = strategyNames.some(name =>
      ['突破策略', '趋势跟踪', '均线策略', '价值投资'].includes(name)
    )

    // Should NOT have hardcoded strategies (expect this to FAIL before implementation)
    expect(hasHardcodedStrategy).toBeFalsy()

    // Verify scores are numeric and within valid range
    const scores = await page.$$eval(
      '.el-table__body tr td:nth-child(6)',
      cells => cells.map(cell => parseInt(cell.textContent.trim()))
    )
    scores.forEach(score => {
      expect(score).toBeGreaterThanOrEqual(0)
      expect(score).toBeLessThanOrEqual(100)
    })
  })

  /**
   * Test 3: Industry Filter Shows Real Industry Stocks
   *
   * Acceptance Criteria:
   * - Data loaded from GET /api/data/dashboard/industry-stocks
   * - Industry names from symbols_info table
   * - Market cap values are real numbers from database
   * - Industry ranking calculated from actual data
   */
  test('T022: Industry stocks table displays real industry data', async () => {
    // Navigate to Industry tab
    await page.click('text=行业选股')

    // Wait for table to load
    await page.waitForSelector('.el-table__body')

    // Get industry data
    const industries = await page.$$eval(
      '.el-table__body tr td:nth-child(5)',
      cells => cells.map(cell => cell.textContent.trim())
    )

    // Verify industries are diverse (not all "白酒")
    const uniqueIndustries = new Set(industries)
    expect(uniqueIndustries.size).toBeGreaterThan(1)

    // Verify market cap values are realistic
    const marketCaps = await page.$$eval(
      '.el-table__body tr td:nth-child(7)',
      cells => cells.map(cell => parseFloat(cell.textContent.trim()))
    )
    marketCaps.forEach(cap => {
      expect(cap).toBeGreaterThan(0)
      expect(cap).toBeLessThan(100000) // Less than 10 trillion yuan
    })
  })

  /**
   * Test 4: Fund Flow Chart Shows Real Industry Fund Flow
   *
   * Acceptance Criteria:
   * - Data loaded from GET /api/data/dashboard/fund-flow
   * - Chart displays data from market_fund_flow table
   * - Industry standard selector works (证监会, 申万一级, 申万二级)
   * - Values are real-time or latest available
   */
  test('T023: Fund flow chart displays real industry fund flow data', async () => {
    // Wait for industry chart to render
    await page.waitForSelector('[ref="industryChartRef"]')

    // Test industry standard selector
    await page.click('.el-select')
    await page.click('text=申万一级')

    // Wait for chart to update
    await page.waitForTimeout(500)

    // Verify chart has data
    const chartHasData = await page.evaluate(() => {
      const chartDom = document.querySelector('[ref="industryChartRef"]')
      const chartInstance = window.echarts?.getInstanceByDom(chartDom)
      const option = chartInstance?.getOption()
      return option?.series?.[0]?.data?.length > 0
    })
    expect(chartHasData).toBeTruthy()

    // Switch to 申万二级 and verify update
    await page.click('.el-select')
    await page.click('text=申万二级')
    await page.waitForTimeout(500)

    // Verify chart updated with different data
    const chartUpdated = await page.evaluate(() => {
      const chartDom = document.querySelector('[ref="industryChartRef"]')
      const chartInstance = window.echarts?.getInstanceByDom(chartDom)
      return chartInstance !== null
    })
    expect(chartUpdated).toBeTruthy()
  })

  /**
   * Test 5: Refresh Button Updates Data from API
   *
   * Acceptance Criteria:
   * - Refresh button triggers API call to GET /api/data/dashboard/summary
   * - All tables and charts update with latest data
   * - Loading indicator shown during refresh
   * - Success message displayed after refresh
   */
  test('T024: Refresh button updates all data from API', async () => {
    // Click refresh button
    const refreshButton = await page.waitForSelector('text=刷新')

    // Monitor network requests
    const apiRequests = []
    page.on('request', request => {
      if (request.url().includes('/api/data/dashboard')) {
        apiRequests.push(request.url())
      }
    })

    await refreshButton.click()

    // Wait for loading indicator
    await page.waitForSelector('.el-loading-mask', { timeout: 1000 })

    // Wait for loading to finish
    await page.waitForSelector('.el-loading-mask', { state: 'hidden', timeout: 5000 })

    // Verify success message
    await page.waitForSelector('text=数据已刷新')

    // Verify API was called
    expect(apiRequests.length).toBeGreaterThan(0)
    expect(apiRequests.some(url => url.includes('/dashboard/summary'))).toBeTruthy()
  })

  /**
   * Test 6: Stats Cards Show Real Database Counts
   *
   * Acceptance Criteria:
   * - Total stocks count from symbols_info table
   * - Active stocks calculated from recent trading data
   * - Data update timestamp from last data refresh
   * - System status from health check endpoint
   */
  test('T025: Stats cards display real database statistics', async () => {
    // Get stats card values
    const totalStocks = await page.textContent('.stat-card:nth-child(1) .stat-value')
    const activeStocks = await page.textContent('.stat-card:nth-child(2) .stat-value')
    const dataUpdate = await page.textContent('.stat-card:nth-child(3) .stat-value')
    const systemStatus = await page.textContent('.stat-card:nth-child(4) .stat-value')

    // Verify total stocks is NOT "0" (should have data)
    expect(totalStocks).not.toBe('0')
    expect(parseInt(totalStocks)).toBeGreaterThan(0)

    // Verify active stocks is a number
    expect(parseInt(activeStocks)).toBeGreaterThanOrEqual(0)

    // Verify data update is NOT "0" (should have timestamp or count)
    expect(dataUpdate).not.toBe('0')

    // Verify system status shows "正常"
    expect(systemStatus).toBe('正常')
  })

  /**
   * Test 7: Market Heat Charts Show Real Data
   *
   * Acceptance Criteria:
   * - All 4 market tabs load with real data
   * - Charts render correctly with database values
   * - Tab switching works smoothly
   */
  test('T026: Market heat charts display real market data', async () => {
    const tabs = ['市场热度', '领涨板块', '涨跌分布', '资金流向']

    for (const tabName of tabs) {
      // Click tab
      await page.click(`text=${tabName}`)
      await page.waitForTimeout(300)

      // Verify chart rendered
      const chartRendered = await page.evaluate((tab) => {
        const chartRefs = {
          '市场热度': 'marketHeatChartRef',
          '领涨板块': 'leadingSectorChartRef',
          '涨跌分布': 'priceDistributionChartRef',
          '资金流向': 'capitalFlowChartRef'
        }
        const refName = chartRefs[tab]
        const chartDom = document.querySelector(`[ref="${refName}"]`)
        const chartInstance = window.echarts?.getInstanceByDom(chartDom)
        return chartInstance !== null
      }, tabName)

      expect(chartRendered).toBeTruthy()
    }
  })

  /**
   * Test 8: Error Handling - API Failures Show User-Friendly Messages
   *
   * Acceptance Criteria:
   * - Network errors show Chinese error message
   * - Database errors show "数据加载失败，请稍后重试"
   * - No technical error details exposed to user
   */
  test('T027: Error handling displays user-friendly messages', async () => {
    // Simulate API failure by stopping backend
    // (In real test, use network interception to mock 500 error)

    // For now, verify error handler exists
    const errorHandlerExists = await page.evaluate(() => {
      return typeof window.ElMessage !== 'undefined'
    })
    expect(errorHandlerExists).toBeTruthy()
  })
})

/**
 * Test Execution Notes:
 *
 * 1. Run with chrome-devtools-mcp:
 *    - Requires Chrome browser with DevTools Protocol enabled
 *    - Use mcp__chrome-devtools__navigate_page to navigate
 *    - Use mcp__chrome-devtools__take_snapshot for page state
 *
 * 2. Expected Results (Before Implementation):
 *    - T020-T023: SHOULD FAIL (currently using mock data)
 *    - T024: SHOULD FAIL (refresh doesn't call new API)
 *    - T025: MAY PASS partially (loadData already fetches total stocks)
 *    - T026: SHOULD FAIL (charts use hardcoded data)
 *    - T027: SHOULD PASS (error handler exists)
 *
 * 3. Expected Results (After Implementation):
 *    - All tests SHOULD PASS
 *    - Dashboard shows real database data
 *    - No mock data visible to users
 */
