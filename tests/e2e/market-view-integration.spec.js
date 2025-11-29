import { test, expect } from '@playwright/test'

test.describe('Market.vue - P2高优先级页面集成测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/market')
  })

  test('01. 页面加载 - 显示市场概览卡片', async ({ page }) => {
    // 等待页面加载
    await page.waitForLoadState('networkidle')

    // 检查标题
    const heading = page.locator('text=市场数据')
    await expect(heading).toBeVisible({ timeout: 5000 })

    // 检查概览统计卡片
    const totalAssets = page.locator('text=总资产')
    await expect(totalAssets).toBeVisible()

    const availableCash = page.locator('text=可用资金')
    await expect(availableCash).toBeVisible()

    const positionValue = page.locator('text=持仓市值')
    await expect(positionValue).toBeVisible()

    const totalProfit = page.locator('text=总盈亏')
    await expect(totalProfit).toBeVisible()
  })

  test('02. API集成 - 加载投资组合数据', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 检查是否显示资产数据
    const totalAssetsValue = page.locator('[class*="statistic"]').first()
    const text = await totalAssetsValue.textContent()

    // 资产值应该是数字
    expect(text).toMatch(/[\d,]+/)
  })

  test('03. 标签页导航 - 市场统计', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 点击市场统计标签页
    const statsTab = page.locator('text=市场统计')
    await expect(statsTab).toBeVisible()

    // 检查统计数据卡片
    const tradingStats = page.locator('text=交易统计')
    await expect(tradingStats).toBeVisible({ timeout: 5000 })

    const assetDistribution = page.locator('text=资产分布')
    await expect(assetDistribution).toBeVisible()
  })

  test('04. 标签页导航 - 持仓信息', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 点击持仓信息标签页
    const positionsTab = page.locator('text=持仓信息')
    await positionsTab.click()

    // 等待表格加载
    await page.waitForLoadState('networkidle')

    // 检查表格列
    const codeColumn = page.locator('text=代码')
    await expect(codeColumn).toBeVisible()

    const nameColumn = page.locator('text=名称')
    await expect(nameColumn).toBeVisible()

    const quantityColumn = page.locator('text=数量')
    await expect(quantityColumn).toBeVisible()
  })

  test('05. 标签页导航 - 交易历史', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 点击交易历史标签页
    const historyTab = page.locator('text=交易历史')
    await historyTab.click()

    // 等待表格加载
    await page.waitForLoadState('networkidle')

    // 检查表格列
    const typeColumn = page.locator('text=类型')
    await expect(typeColumn).toBeVisible()

    const dateColumn = page.locator('text=日期')
    await expect(dateColumn).toBeVisible()

    const amountColumn = page.locator('text=金额')
    await expect(amountColumn).toBeVisible()
  })

  test('06. 刷新按钮功能', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 找到刷新按钮
    const refreshButton = page.locator('button:has-text("刷新")')
    await expect(refreshButton).toBeVisible()

    // 点击刷新
    await refreshButton.click()

    // 应该显示加载状态或成功消息
    // 等待网络请求完成
    await page.waitForLoadState('networkidle')

    // 页面应该仍然显示数据
    const heading = page.locator('text=市场数据')
    await expect(heading).toBeVisible()
  })

  test('07. 数据显示准确性 - Trade Portfolio API', async ({ page }) => {
    // 直接测试API
    const response = await page.request.get('/api/trade/portfolio')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.data).toHaveProperty('total_assets')
    expect(data.data).toHaveProperty('available_cash')
    expect(data.data).toHaveProperty('position_value')
    expect(data.data).toHaveProperty('total_profit')
  })

  test('08. 数据显示准确性 - Trade Positions API', async ({ page }) => {
    // 直接测试API
    const response = await page.request.get('/api/trade/positions')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
    // 位置数据应该是数组或对象
    expect(data.data).toBeDefined()
  })

  test('09. 数据显示准确性 - Trade Statistics API', async ({ page }) => {
    // 直接测试API
    const response = await page.request.get('/api/trade/statistics')
    expect(response.status()).toBe(200)

    const data = await response.json()
    expect(data.success).toBe(true)
    expect(data.data).toBeDefined()
  })

  test('10. 响应性设计 - 移动端', async ({ page }) => {
    // 设置视口大小为移动设备
    await page.setViewportSize({ width: 375, height: 667 })

    // 页面应该仍然加载
    await page.waitForLoadState('networkidle')

    // 检查元素是否可见
    const heading = page.locator('text=市场数据')
    await expect(heading).toBeVisible()

    // 卡片应该堆叠
    const cards = page.locator('[class*="el-card"]')
    await expect(cards.first()).toBeVisible()
  })
})
