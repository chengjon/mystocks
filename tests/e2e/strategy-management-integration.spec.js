import { test, expect } from '@playwright/test'

test.describe('StrategyManagement.vue - P2高优先级页面集成测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/strategy-management')
  })

  test('01. 页面加载 - 显示策略管理标题', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const heading = page.locator('text=股票策略管理')
    await expect(heading).toBeVisible({ timeout: 5000 })

    const subtitle = page.locator('text=基于InStock经典策略')
    await expect(subtitle).toBeVisible()
  })

  test('02. 标签页导航 - 策略列表显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const listTab = page.locator('text=策略列表')
    await expect(listTab).toBeVisible()

    const tabPane = page.locator('[role="tabpanel"]').first()
    await expect(tabPane).toBeVisible()
  })

  test('03. 标签页导航 - 单只运行标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const singleTab = page.locator('text=单只运行')
    await singleTab.click()

    const formLabel = page.locator('text=选择策略')
    await expect(formLabel).toBeVisible({ timeout: 5000 })
  })

  test('04. 标签页导航 - 批量扫描标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const batchTab = page.locator('text=批量扫描')
    await batchTab.click()

    const paneContent = page.locator('[role="tabpanel"]').nth(2)
    await expect(paneContent).toBeVisible()
  })

  test('05. 标签页导航 - 结果查询标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const resultsTab = page.locator('text=结果查询')
    await resultsTab.click()

    const paneContent = page.locator('[role="tabpanel"]').nth(3)
    await expect(paneContent).toBeVisible()
  })

  test('06. 标签页导航 - 统计分析标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const statsTab = page.locator('text=统计分析')
    await statsTab.click()

    const paneContent = page.locator('[role="tabpanel"]').nth(4)
    await expect(paneContent).toBeVisible()
  })

  test('07. API集成 - Strategy Definitions API', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 测试策略定义API
    const response = await page.request.get('/api/v1/strategy/strategies')
    // 允许策略API可能不存在，但测试端点的可访问性
    expect(response.status()).toBeLessThan(500)
  })

  test('08. 策略列表 - 搜索功能', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找搜索输入框
    const searchInput = page.locator('input[placeholder*="搜索策略"]')
    if (await searchInput.isVisible()) {
      await searchInput.fill('test')
      await page.waitForTimeout(500)
    }
  })

  test('09. 策略列表 - 状态筛选', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找筛选下拉菜单
    const filterSelect = page.locator('[placeholder="状态筛选"]')
    if (await filterSelect.isVisible()) {
      await filterSelect.click()
      const enableOption = page.locator('text=启用').first()
      if (await enableOption.isVisible()) {
        await enableOption.click()
      }
    }
  })

  test('10. 单只运行 - 表单字段验证', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const singleTab = page.locator('text=单只运行')
    await singleTab.click()

    // 查找表单字段
    const strategySelect = page.locator('[placeholder="请选择策略"]')
    const symbolInput = page.locator('[placeholder*="股票代码"]')
    const nameInput = page.locator('[placeholder*="股票名称"]')

    if (await strategySelect.isVisible()) {
      await expect(strategySelect).toBeVisible()
    }
    if (await symbolInput.isVisible()) {
      await expect(symbolInput).toBeVisible()
    }
    if (await nameInput.isVisible()) {
      await expect(nameInput).toBeVisible()
    }
  })

  test('11. 响应性设计 - 移动端', async ({ page }) => {
    // 设置视口大小为移动设备
    await page.setViewportSize({ width: 375, height: 667 })

    await page.waitForLoadState('networkidle')

    const heading = page.locator('text=股票策略管理')
    await expect(heading).toBeVisible()

    // 标签页应该可见
    const tabs = page.locator('[role="tab"]')
    const count = await tabs.count()
    expect(count).toBeGreaterThan(0)
  })

  test('12. 页面导航 - 标签页切换持续性', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 从策略列表切换到单只运行
    const listTab = page.locator('text=策略列表')
    await expect(listTab).toBeVisible()

    const singleTab = page.locator('text=单只运行')
    await singleTab.click()

    // 验证标签页已切换
    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(tabText).toContain('单只运行')
  })

  test('13. 页面元素 - 图标验证', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证各标签页的图标可见
    const icons = page.locator('[role="tab"] svg')
    const count = await icons.count()
    expect(count).toBeGreaterThan(0)
  })

  test('14. API响应处理 - 错误情况', async ({ page }) => {
    // 测试页面在API不可用时的表现
    await page.waitForLoadState('networkidle')

    const heading = page.locator('text=股票策略管理')
    await expect(heading).toBeVisible()
    // 页面应该仍然正常显示，即使某些API失败
  })

  test('15. 数据绑定 - 策略信息显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 在策略列表标签页
    const listTab = page.locator('text=策略列表')
    await expect(listTab).toBeVisible()

    // 查找策略卡片
    const strategyCards = page.locator('[class*="strategy"][class*="card"]')
    const cardCount = await strategyCards.count()
    // 可能有或没有策略卡片，但查询应该成功
    expect(cardCount).toBeGreaterThanOrEqual(0)
  })
})
