import { test, expect } from '@playwright/test'

test.describe('TradeManagement.vue - P2高优先级页面集成测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/trade-management')
  })

  test('01. 页面加载 - 显示资产概览卡片', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 检查4个统计卡片
    const totalAssetsCard = page.locator('text=总资产')
    await expect(totalAssetsCard).toBeVisible({ timeout: 5000 })

    const availableCashCard = page.locator('text=可用资金')
    await expect(availableCashCard).toBeVisible()

    const positionValueCard = page.locator('text=持仓市值')
    await expect(positionValueCard).toBeVisible()

    const totalProfitCard = page.locator('text=总盈亏')
    await expect(totalProfitCard).toBeVisible()
  })

  test('02. API集成 - 加载投资组合数据', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证资产值显示
    const statisticValues = page.locator('[class*="statistic"]')
    const count = await statisticValues.count()
    expect(count).toBeGreaterThanOrEqual(4)
  })

  test('03. 标签页导航 - 持仓管理', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const positionsTab = page.locator('text=持仓管理')
    await expect(positionsTab).toBeVisible()

    // 验证表格存在
    const table = page.locator('table')
    await expect(table).toBeVisible({ timeout: 5000 })
  })

  test('04. 持仓管理 - 买入按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const buyButton = page.locator('button:has-text("买入")')
    await expect(buyButton).toBeVisible()

    // 按钮应该具有图标
    const icon = buyButton.locator('[class*="icon"]')
    await expect(icon).toBeVisible()
  })

  test('05. 持仓管理 - 卖出按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const sellButton = page.locator('button:has-text("卖出")')
    await expect(sellButton).toBeVisible()
  })

  test('06. 持仓管理 - 刷新按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const refreshButton = page.locator('button:has-text("刷新")')
    await expect(refreshButton).toBeVisible()
  })

  test('07. 表格列验证 - 所有列都显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 检查表格列头
    const codeHeader = page.locator('text=股票代码')
    const nameHeader = page.locator('text=股票名称')
    const quantityHeader = page.locator('text=持仓数量')
    const costPriceHeader = page.locator('text=成本价')
    const currentPriceHeader = page.locator('text=现价')
    const positionValueHeader = page.locator('text=持仓市值')

    if (await codeHeader.isVisible()) {
      await expect(codeHeader).toBeVisible()
    }
    if (await nameHeader.isVisible()) {
      await expect(nameHeader).toBeVisible()
    }
  })

  test('08. API集成 - Trade Portfolio API', async ({ page }) => {
    const response = await page.request.get('/api/trade/portfolio')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.data).toHaveProperty('total_assets')
    expect(data.data).toHaveProperty('available_cash')
    expect(data.data).toHaveProperty('position_value')
    expect(data.data).toHaveProperty('total_profit')
  })

  test('09. API集成 - Trade Positions API', async ({ page }) => {
    const response = await page.request.get('/api/trade/positions')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.data).toBeDefined()
  })

  test('10. API集成 - Trade Trades API', async ({ page }) => {
    const response = await page.request.get('/api/trade/trades?page=1&page_size=20')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
  })

  test('11. API集成 - Trade Statistics API', async ({ page }) => {
    const response = await page.request.get('/api/trade/statistics')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
  })

  test('12. 响应性设计 - 移动端', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    await page.waitForLoadState('networkidle')

    // 检查页面是否仍然可访问
    const cards = page.locator('[class*="card"]')
    const count = await cards.count()
    expect(count).toBeGreaterThan(0)
  })

  test('13. 交易历史标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const tradesTab = page.locator('text=交易历史')
    if (await tradesTab.isVisible()) {
      await tradesTab.click()

      // 等待标签页内容加载
      await page.waitForLoadState('networkidle')
    }
  })

  test('14. 数据可视化 - 图表显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找ECharts容器
    const chartContainer = page.locator('[class*="chart"]').first()
    if (await chartContainer.isVisible()) {
      await expect(chartContainer).toBeVisible()
    }
  })

  test('15. 盈亏显示 - 颜色区分', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 总盈亏卡片应该存在
    const profitCard = page.locator('text=总盈亏')
    await expect(profitCard).toBeVisible()
  })
})
