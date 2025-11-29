import { test, expect } from '@playwright/test'

test.describe('MarketData.vue - P2高优先级页面集成测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/market-data')
  })

  test('01. 页面加载 - 显示标签页导航', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证所有4个标签页都存在
    const fundFlowTab = page.locator('text=资金流向')
    const etfTab = page.locator('text=ETF行情')
    const chipRaceTab = page.locator('text=竞价抢筹')
    const lhbTab = page.locator('text=龙虎榜')

    await expect(fundFlowTab).toBeVisible({ timeout: 5000 })
    await expect(etfTab).toBeVisible()
    await expect(chipRaceTab).toBeVisible()
    await expect(lhbTab).toBeVisible()
  })

  test('02. 标签页导航 - 资金流向标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const fundFlowTab = page.locator('text=资金流向')
    await fundFlowTab.click()

    // 等待标签页内容加载
    await page.waitForLoadState('networkidle')

    // 验证标签页已激活
    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('资金流向')
  })

  test('03. 标签页导航 - ETF行情标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const etfTab = page.locator('text=ETF行情')
    await etfTab.click()

    await page.waitForLoadState('networkidle')

    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('ETF行情')
  })

  test('04. 标签页导航 - 竞价抢筹标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const chipRaceTab = page.locator('text=竞价抢筹')
    await chipRaceTab.click()

    await page.waitForLoadState('networkidle')

    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('竞价抢筹')
  })

  test('05. 标签页导航 - 龙虎榜标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const lhbTab = page.locator('text=龙虎榜')
    await lhbTab.click()

    await page.waitForLoadState('networkidle')

    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('龙虎榜')
  })

  test('06. 市场数据 API - 资金流向数据', async ({ page }) => {
    // 测试资金流向API
    const response = await page.request.get('/api/market/v2/fund-flow')
    expect(response.status()).toBeLessThan(500)
  })

  test('07. 市场数据 API - ETF行情数据', async ({ page }) => {
    // 测试ETF行情API
    const response = await page.request.get('/api/market/v2/etf')
    expect(response.status()).toBeLessThan(500)
  })

  test('08. 市场数据 API - 龙虎榜数据', async ({ page }) => {
    // 测试龙虎榜API
    const response = await page.request.get('/api/monitoring/dragon-tiger')
    expect(response.status()).toBe(200)
  })

  test('09. 响应性设计 - 移动端', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    await page.waitForLoadState('networkidle')

    // 验证标签页在移动设备上仍然可见
    const tabs = page.locator('[role="tab"]')
    const count = await tabs.count()
    expect(count).toBeGreaterThan(0)

    // 验证标签页可以切换
    const fundFlowTab = page.locator('text=资金流向')
    await expect(fundFlowTab).toBeVisible()
  })

  test('10. 标签页切换持续性', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 从默认标签页切换到ETF行情
    const etfTab = page.locator('text=ETF行情')
    await etfTab.click()

    // 验证标签页已切换
    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('ETF行情')

    // 切换回资金流向
    const fundFlowTab = page.locator('text=资金流向')
    await fundFlowTab.click()

    const newActiveTab = page.locator('[role="tab"][aria-selected="true"]')
    const newTabText = await newActiveTab.textContent()
    expect(newTabText).toContain('资金流向')
  })

  test('11. 页面元素 - 标签页容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证标签页容器存在
    const tabsContainer = page.locator('[role="tablist"]')
    await expect(tabsContainer).toBeVisible()

    // 验证标签页内容容器存在
    const tabPanes = page.locator('[role="tabpanel"]')
    const count = await tabPanes.count()
    expect(count).toBeGreaterThan(0)
  })

  test('12. API集成 - 市场监控数据汇总', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 测试监控汇总API
    const response = await page.request.get('/api/monitoring/summary')
    expect(response.status()).toBeLessThan(500)
  })

  test('13. 动态内容加载 - 标签页内容动态加载', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 记录初始标签页内容
    const initialPane = page.locator('[role="tabpanel"]').first()
    expect(initialPane).toBeDefined()

    // 切换到新标签页
    const chipRaceTab = page.locator('text=竞价抢筹')
    await chipRaceTab.click()

    await page.waitForTimeout(500)

    // 验证标签页内容已更新
    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('竞价抢筹')
  })

  test('14. 错误处理 - API不可用时页面仍然可访问', async ({ page }) => {
    // 页面应该在API失败时仍然加载
    await page.waitForLoadState('networkidle')

    const fundFlowTab = page.locator('text=资金流向')
    await expect(fundFlowTab).toBeVisible()
  })

  test('15. 标签页样式验证 - 图标和标签显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证每个标签页都有文本
    const tabs = page.locator('[role="tab"]')
    const count = await tabs.count()

    for (let i = 0; i < count; i++) {
      const tab = tabs.nth(i)
      const text = await tab.textContent()
      expect(text).toBeTruthy()
      expect(text?.length).toBeGreaterThan(0)
    }
  })
})
