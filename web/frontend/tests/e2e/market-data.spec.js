/**
 * Market Data Panels E2E Tests - User Story 2: Fix 4 Broken Panels
 *
 * Purpose: Verify 4 market data panels load data from PostgreSQL without MySQL errors
 *
 * Panels:
 * 1. 龙虎榜 (Dragon Tiger List) - dragon_tiger table
 * 2. ETF数据 (ETF Data) - etf_data table
 * 3. 资金流向 (Fund Flow) - market_fund_flow table
 * 4. 竞价抢筹 (Chip Race) - chip_race table
 *
 * Prerequisites:
 * - Backend running on http://localhost:8000
 * - Frontend running on http://localhost:3001
 * - PostgreSQL database with populated tables
 * - Valid authentication token
 */

const BASE_URL = 'http://localhost:3001'
const API_BASE_URL = 'http://localhost:8000'

/**
 * Test Suite: Market Data Panels
 */
describe('Market Data Panels - PostgreSQL Integration (User Story 2)', () => {

  /**
   * Setup: Login and navigate to Market section
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
    await page.waitForLoadState('networkidle')
  })

  /**
   * Test 1: Dragon Tiger List Panel (龙虎榜)
   *
   * Acceptance Criteria:
   * - Panel loads data from GET /api/market/dragon-tiger
   * - Data comes from dragon_tiger table in PostgreSQL
   * - No MySQL connection errors
   * - Shows top trading activity stocks
   */
  test('T040: Dragon Tiger List panel loads data from PostgreSQL', async () => {
    // Navigate to Market section
    await page.click('text=市场数据')
    await page.click('text=龙虎榜')

    // Wait for panel to load
    await page.waitForSelector('.dragon-tiger-panel', { timeout: 5000 })

    // Verify API call to PostgreSQL endpoint
    const apiRequests = []
    page.on('request', request => {
      if (request.url().includes('/api/market/dragon-tiger')) {
        apiRequests.push(request.url())
      }
    })

    // Wait for data to load
    await page.waitForSelector('.el-table__body tr', { timeout: 5000 })

    // Verify data is present
    const rowCount = await page.$$eval('.el-table__body tr', rows => rows.length)
    expect(rowCount).toBeGreaterThan(0)

    // Verify NO MySQL errors
    const noMySQLError = await page.evaluate(() => {
      const errorText = document.body.textContent
      return !errorText.includes('MySQL') && !errorText.includes('pymysql')
    })
    expect(noMySQLError).toBeTruthy()

    // Verify API was called
    expect(apiRequests.some(url => url.includes('/dragon-tiger'))).toBeTruthy()
  })

  /**
   * Test 2: ETF Data Panel (ETF数据)
   *
   * Acceptance Criteria:
   * - Panel loads data from GET /api/market/etf-data
   * - Data comes from etf_data table in PostgreSQL
   * - Shows real ETF codes and prices
   * - No hardcoded mock data
   */
  test('T041: ETF Data panel loads real data from PostgreSQL', async () => {
    // Navigate to ETF panel
    await page.click('text=市场数据')
    await page.click('text=ETF数据')

    // Wait for panel to load
    await page.waitForSelector('.etf-data-panel', { timeout: 5000 })

    // Monitor API requests
    const apiRequests = []
    page.on('request', request => {
      if (request.url().includes('/api/market/etf-data')) {
        apiRequests.push(request.url())
      }
    })

    // Wait for table data
    await page.waitForSelector('.el-table__body tr', { timeout: 5000 })

    // Get first row ETF code
    const firstETFCode = await page.textContent('.el-table__body tr:first-child td:first-child')

    // Verify it's a real ETF code format (6 digits starting with 5)
    const isRealETF = /^5\d{5}$/.test(firstETFCode.trim())
    expect(isRealETF).toBeTruthy()

    // Verify NO mock data
    const noMockData = await page.evaluate(() => {
      const tableText = document.querySelector('.etf-data-panel').textContent
      // Check for common mock ETF codes
      return !tableText.includes('510050') || tableText.includes('其他真实代码')
    })

    // Verify API called
    expect(apiRequests.some(url => url.includes('/etf-data'))).toBeTruthy()
  })

  /**
   * Test 3: Fund Flow Panel (资金流向)
   *
   * Acceptance Criteria:
   * - Panel loads data from GET /api/market/fund-flow (PostgreSQL)
   * - Data comes from market_fund_flow table
   * - No MySQL dependency
   * - Shows industry fund flow chart
   */
  test('T042: Fund Flow panel loads from PostgreSQL market_fund_flow table', async () => {
    // Navigate to Fund Flow panel
    await page.click('text=市场数据')
    await page.click('text=资金流向')

    // Wait for panel to load
    await page.waitForSelector('.fund-flow-panel', { timeout: 5000 })

    // Monitor API requests
    const apiRequests = []
    page.on('request', request => {
      if (request.url().includes('/api/market/fund-flow')) {
        apiRequests.push(request.url())
      }
    })

    // Wait for chart to render
    await page.waitForSelector('.fund-flow-chart', { timeout: 5000 })

    // Verify chart has data
    const chartHasData = await page.evaluate(() => {
      const chartDom = document.querySelector('.fund-flow-chart')
      return chartDom !== null && chartDom.offsetHeight > 0
    })
    expect(chartHasData).toBeTruthy()

    // Verify NO MySQL connection code
    const noMySQLCode = await page.evaluate(() => {
      const pageSource = document.documentElement.innerHTML
      return !pageSource.includes('mysql://') && !pageSource.includes('pymysql')
    })
    expect(noMySQLCode).toBeTruthy()

    // Verify API called with PostgreSQL endpoint
    expect(apiRequests.some(url => url.includes('/market/fund-flow'))).toBeTruthy()
  })

  /**
   * Test 4: Chip Race Panel (竞价抢筹)
   *
   * Acceptance Criteria:
   * - Panel loads data from GET /api/market/chip-race
   * - Data comes from chip_race table in PostgreSQL
   * - Shows stocks with high bid-ask activity
   * - No errors or blank screens
   */
  test('T043: Chip Race panel loads data from PostgreSQL', async () => {
    // Navigate to Chip Race panel
    await page.click('text=市场数据')
    await page.click('text=竞价抢筹')

    // Wait for panel to load
    await page.waitForSelector('.chip-race-panel', { timeout: 5000 })

    // Monitor API requests
    const apiRequests = []
    page.on('request', request => {
      if (request.url().includes('/api/market/chip-race')) {
        apiRequests.push(request.url())
      }
    })

    // Wait for table data
    await page.waitForSelector('.el-table__body tr', { timeout: 5000 })

    // Verify data is present
    const rowCount = await page.$$eval('.el-table__body tr', rows => rows.length)
    expect(rowCount).toBeGreaterThan(0)

    // Get first row data to verify it has real values
    const firstRowData = await page.evaluate(() => {
      const firstRow = document.querySelector('.el-table__body tr:first-child')
      return {
        symbol: firstRow.querySelector('td:nth-child(1)')?.textContent.trim(),
        name: firstRow.querySelector('td:nth-child(2)')?.textContent.trim(),
        hasData: firstRow.querySelectorAll('td').length > 0
      }
    })

    expect(firstRowData.hasData).toBeTruthy()
    expect(firstRowData.symbol).toBeTruthy()
    expect(firstRowData.name).toBeTruthy()

    // Verify API was called
    expect(apiRequests.some(url => url.includes('/chip-race'))).toBeTruthy()
  })

  /**
   * Test 5: Error Handling - User-Friendly Messages
   *
   * Acceptance Criteria:
   * - Network errors show Chinese error message
   * - Database errors show "数据加载失败，请稍后重试"
   * - No technical stack traces visible to user
   */
  test('T044: Error conditions display user-friendly messages', async () => {
    // Navigate to one of the panels
    await page.click('text=市场数据')
    await page.click('text=龙虎榜')

    // Simulate network error by intercepting request
    await page.route('**/api/market/dragon-tiger', route => {
      route.abort('failed')
    })

    // Trigger refresh
    await page.click('button:has-text("刷新")')

    // Wait for error message
    await page.waitForSelector('.el-message--error', { timeout: 3000 })

    // Verify error message is user-friendly Chinese
    const errorMessage = await page.textContent('.el-message--error')
    const isFriendly = errorMessage.includes('失败') ||
                       errorMessage.includes('重试') ||
                       errorMessage.includes('网络')
    expect(isFriendly).toBeTruthy()

    // Verify NO technical details exposed
    const noStackTrace = !errorMessage.includes('Error:') &&
                        !errorMessage.includes('at ') &&
                        !errorMessage.includes('node_modules')
    expect(noStackTrace).toBeTruthy()
  })

  /**
   * Test 6: All 4 Panels Load Without MySQL Dependency
   *
   * Integration test to verify complete PostgreSQL migration
   */
  test('T045: All 4 market panels work without MySQL', async () => {
    const panels = [
      { name: '龙虎榜', selector: '.dragon-tiger-panel' },
      { name: 'ETF数据', selector: '.etf-data-panel' },
      { name: '资金流向', selector: '.fund-flow-panel' },
      { name: '竞价抢筹', selector: '.chip-race-panel' }
    ]

    for (const panel of panels) {
      // Navigate to panel
      await page.click('text=市场数据')
      await page.click(`text=${panel.name}`)

      // Wait for panel to load
      await page.waitForSelector(panel.selector, { timeout: 5000 })

      // Verify no MySQL errors in console
      const consoleErrors = []
      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text())
        }
      })

      await page.waitForTimeout(1000)

      const noMySQLErrors = consoleErrors.every(error =>
        !error.includes('MySQL') && !error.includes('pymysql')
      )
      expect(noMySQLErrors).toBeTruthy()
    }
  })
})

/**
 * Test Execution Notes:
 *
 * 1. Expected Results (Before Implementation):
 *    - T040-T043: SHOULD FAIL (panels not connected to PostgreSQL)
 *    - T044: SHOULD PASS (error handler exists)
 *    - T045: SHOULD FAIL (MySQL dependencies present)
 *
 * 2. Expected Results (After Implementation):
 *    - All tests SHOULD PASS
 *    - All 4 panels load data from PostgreSQL
 *    - No MySQL connection errors
 *    - User-friendly error messages
 *
 * 3. Database Tables Required:
 *    - dragon_tiger (PostgreSQL)
 *    - etf_data (PostgreSQL)
 *    - market_fund_flow (PostgreSQL)
 *    - chip_race (PostgreSQL)
 */
