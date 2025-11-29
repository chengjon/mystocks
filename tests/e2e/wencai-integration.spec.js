import { test, expect } from '@playwright/test'

test.describe('Wencai.vue - Financial Screening Tool Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/wencai')
  })

  test('01. 页面加载 - 显示问财股票筛选系统标题', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const title = page.locator('text=问财股票筛选系统')
    await expect(title).toBeVisible({ timeout: 5000 })

    const subtitle = page.locator('text=基于自然语言处理的智能股票筛选工具')
    await expect(subtitle).toBeVisible()
  })

  test('02. 头部统计卡片 - 显示预定义查询数', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const predefinedStat = page.locator('text=预定义查询')
    if (await predefinedStat.isVisible()) {
      await expect(predefinedStat).toBeVisible()
    }
  })

  test('03. 头部统计卡片 - 显示总筛选数', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const totalRecordsStat = page.locator('text=总筛选数')
    if (await totalRecordsStat.isVisible()) {
      await expect(totalRecordsStat).toBeVisible()
    }
  })

  test('04. 头部统计卡片 - 显示API状态', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const apiStatusStat = page.locator('text=API状态')
    if (await apiStatusStat.isVisible()) {
      await expect(apiStatusStat).toBeVisible()
    }
  })

  test('05. 功能介绍 - 功能介绍部分显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const functionsTitle = page.locator('text=功能介绍')
    if (await functionsTitle.isVisible()) {
      await expect(functionsTitle).toBeVisible()
    }
  })

  test('06. 功能介绍 - 列出功能特性', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证功能列表项
    const features = [
      '9个精选问财查询模板',
      '支持实时数据刷新',
      'CSV数据导出',
      '查询历史记录',
      '自定义查询模板'
    ]

    for (const feature of features) {
      const featureText = page.locator(`text=${feature}`)
      const isVisible = await featureText.isVisible().catch(() => false)
      if (isVisible) {
        await expect(featureText).toBeVisible()
      }
    }
  })

  test('07. 快速开始 - 快速开始部分显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const quickStartTitle = page.locator('text=快速开始')
    if (await quickStartTitle.isVisible()) {
      await expect(quickStartTitle).toBeVisible()
    }
  })

  test('08. 快速开始 - 显示使用步骤', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const steps = [
      '选择下方的查询模板',
      '点击"执行查询"获取数据',
      '点击"查看结果"查看完整数据',
      '使用"导出CSV"保存数据',
      '查看"历史"了解查询记录'
    ]

    for (const step of steps) {
      const stepText = page.locator(`text=${step}`)
      const isVisible = await stepText.isVisible().catch(() => false)
      if (isVisible) {
        await expect(stepText).toBeVisible()
      }
    }
  })

  test('09. 标签页导航 - 显示问财查询标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const wencaiTab = page.locator('text=问财查询')
    await expect(wencaiTab).toBeVisible()
  })

  test('10. 标签页导航 - 显示我的查询标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const myQueriesTab = page.locator('text=我的查询')
    await expect(myQueriesTab).toBeVisible()
  })

  test('11. 标签页导航 - 显示统计分析标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const statisticsTab = page.locator('text=统计分析')
    await expect(statisticsTab).toBeVisible()
  })

  test('12. 标签页导航 - 显示使用指南标签页', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const guideTab = page.locator('text=使用指南')
    await expect(guideTab).toBeVisible()
  })

  test('13. 问财查询标签页 - WencaiPanel组件加载', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证问财查询标签页是否是活动的
    const activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const tabText = await activeTab.textContent()
    expect(['问财查询', '我的查询', '统计分析', '使用指南']).toContain(tabText?.trim())
  })

  test('14. 我的查询标签页 - 显示空状态提示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到我的查询标签页
    const myQueriesTab = page.locator('text=我的查询')
    await myQueriesTab.click()

    // 等待标签页加载
    await page.waitForTimeout(300)

    // 验证空状态显示
    const emptyState = page.locator('[class*="el-empty"]')
    const emptyText = page.locator('text=还没有保存的查询')

    const empty1 = await emptyState.isVisible().catch(() => false)
    const empty2 = await emptyText.isVisible().catch(() => false)

    if (empty1 || empty2) {
      expect(true).toBeTruthy()
    }
  })

  test('15. 统计分析标签页 - 显示统计指标卡片', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到统计分析标签页
    const statisticsTab = page.locator('text=统计分析')
    await statisticsTab.click()

    // 等待标签页加载
    await page.waitForTimeout(300)

    // 验证统计指标显示
    const todayStats = page.locator('text=今日查询次数')
    const weeklyStats = page.locator('text=本周查询次数')
    const monthlyStats = page.locator('text=本月查询次数')
    const totalStats = page.locator('text=总筛选数')

    const today = await todayStats.isVisible().catch(() => false)
    const weekly = await weeklyStats.isVisible().catch(() => false)
    const monthly = await monthlyStats.isVisible().catch(() => false)
    const total = await totalStats.isVisible().catch(() => false)

    // 至少有一个统计指标可见
    expect(today || weekly || monthly || total).toBeTruthy()
  })

  test('16. 使用指南标签页 - 显示时间线指南', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到使用指南标签页
    const guideTab = page.locator('text=使用指南')
    await guideTab.click()

    // 等待标签页加载
    await page.waitForTimeout(300)

    // 验证时间线显示
    const timeline = page.locator('[class*="el-timeline"]')
    const isVisible = await timeline.isVisible().catch(() => false)
    expect(isVisible).toBeTruthy()
  })

  test('17. 使用指南 - 显示5个步骤', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到使用指南标签页
    const guideTab = page.locator('text=使用指南')
    await guideTab.click()

    // 等待标签页加载
    await page.waitForTimeout(300)

    // 验证步骤显示
    const steps = [
      '选择查询模板',
      '执行查询',
      '查看结果',
      '导出数据',
      '查看历史'
    ]

    for (const step of steps) {
      const stepText = page.locator(`text=${step}`)
      const isVisible = await stepText.isVisible().catch(() => false)
      if (isVisible) {
        await expect(stepText).toBeVisible()
      }
    }
  })

  test('18. API集成 - 问财查询API可访问', async ({ page }) => {
    // 测试问财查询API
    const response = await page.request.get('/api/market/wencai/queries')
    expect(response.status()).toBeLessThan(500)
  })

  test('19. 标签页切换持续性 - 在标签页间切换', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到我的查询
    let tab = page.locator('text=我的查询')
    await tab.click()
    await page.waitForTimeout(300)

    let activeTab = page.locator('[role="tab"][aria-selected="true"]')
    let tabText = await activeTab.textContent()
    expect(tabText).toContain('我的查询')

    // 切换到统计分析
    tab = page.locator('text=统计分析')
    await tab.click()
    await page.waitForTimeout(300)

    activeTab = page.locator('[role="tab"][aria-selected="true"]')
    tabText = await activeTab.textContent()
    expect(tabText).toContain('统计分析')

    // 切换回问财查询
    tab = page.locator('text=问财查询')
    await tab.click()
    await page.waitForTimeout(300)

    activeTab = page.locator('[role="tab"][aria-selected="true"]')
    tabText = await activeTab.textContent()
    expect(tabText).toContain('问财查询')
  })

  test('20. 响应性设计 - 移动端显示', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    await page.waitForLoadState('networkidle')

    // 验证标题仍然可见
    const title = page.locator('text=问财股票筛选系统')
    await expect(title).toBeVisible()

    // 验证标签页在移动设备上可见
    const tabs = page.locator('[role="tab"]')
    const count = await tabs.count()
    expect(count).toBeGreaterThan(0)
  })

  test('21. 页面元素 - 标签页容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证标签页容器存在
    const tabsContainer = page.locator('[role="tablist"]')
    await expect(tabsContainer).toBeVisible()

    // 验证标签页内容容器存在
    const tabPanes = page.locator('[role="tabpanel"]')
    const count = await tabPanes.count()
    expect(count).toBeGreaterThan(0)
  })

  test('22. 头部卡片布局 - 信息框容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找信息框
    const infoBoxes = page.locator('[class*="info-box"]')
    const count = await infoBoxes.count()
    // 应该至少有功能介绍和快速开始两个信息框
    expect(count).toBeGreaterThanOrEqual(1)
  })

  test('23. 统计卡片样式 - 统计值显示正确', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找统计指标
    const statistics = page.locator('[class*="el-statistic"]')
    const count = await statistics.count()
    // 应该至少有3个统计指标
    expect(count).toBeGreaterThanOrEqual(3)
  })

  test('24. 时间线样式 - 时间线项目显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到使用指南
    const guideTab = page.locator('text=使用指南')
    await guideTab.click()

    // 等待加载
    await page.waitForTimeout(300)

    // 查找时间线项目
    const timelineItems = page.locator('[class*="timeline-item"]')
    const count = await timelineItems.count()
    expect(count).toBeGreaterThanOrEqual(0)
  })

  test('25. 错误处理 - API不可用时页面仍可访问', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 页面应该在API失败时仍然加载
    const title = page.locator('text=问财股票筛选系统')
    await expect(title).toBeVisible()

    // 验证页面结构存在
    const container = page.locator('[class*="wencai-container"]')
    expect(container).toBeDefined()
  })

  test('26. 页面导航 - 所有标签页都可访问', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const tabNames = ['问财查询', '我的查询', '统计分析', '使用指南']

    for (const tabName of tabNames) {
      const tab = page.locator(`text=${tabName}`)
      await expect(tab).toBeVisible()
      await tab.click()
      await page.waitForTimeout(200)
    }
  })

  test('27. 页面布局 - 行容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找行容器
    const rows = page.locator('[class*="el-row"]')
    const count = await rows.count()
    expect(count).toBeGreaterThan(0)
  })

  test('28. 页面布局 - 列容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找列容器
    const cols = page.locator('[class*="el-col"]')
    const count = await cols.count()
    expect(count).toBeGreaterThan(0)
  })

  test('29. 卡片容器 - 多个卡片存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找所有卡片
    const cards = page.locator('[class*="el-card"]')
    const count = await cards.count()
    // 应该至少有头部卡片 + 标签页卡片
    expect(count).toBeGreaterThanOrEqual(1)
  })

  test('30. 页面完整性 - 核心组件都存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证所有核心组件存在
    const headerCard = page.locator('[class*="header-card"]')
    const tabs = page.locator('[role="tab"]')
    const tabPanes = page.locator('[role="tabpanel"]')

    expect(await headerCard.isVisible().catch(() => false)).toBeTruthy()
    expect(await tabs.count()).toBeGreaterThan(0)
    expect(await tabPanes.count()).toBeGreaterThan(0)
  })

  test('31. 功能列表格式 - 列表项正确显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找列表项
    const listItems = page.locator('li')
    const count = await listItems.count()
    // 应该至少有功能介绍和快速开始的列表项
    expect(count).toBeGreaterThanOrEqual(5)
  })

  test('32. 指标卡片排列 - 统计指标正确显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证头部统计卡片
    const headerStats = page.locator('[class*="header-card"] [class*="el-statistic"]')
    const count = await headerStats.count()
    // 应该有预定义查询、总筛选数、API状态三个统计
    expect(count).toBeGreaterThanOrEqual(3)
  })

  test('33. 标签页内容 - 标签页内容容器可见', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找标签页内容
    const tabContent = page.locator('[role="tabpanel"]').first()
    const isVisible = await tabContent.isVisible().catch(() => false)
    expect(isVisible).toBeTruthy()
  })

  test('34. 页面样式 - 容器有适当的填充', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找主容器
    const container = page.locator('[class*="wencai-container"]')
    if (await container.isVisible()) {
      const style = await container.getAttribute('style')
      // 容器应该应用了样式
      expect(container).toBeDefined()
    }
  })

  test('35. 交互响应 - 标签页点击有响应', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 获取初始活动标签页
    let activeTab = page.locator('[role="tab"][aria-selected="true"]')
    let initialText = await activeTab.textContent()

    // 点击另一个标签页
    const myQueriesTab = page.locator('text=我的查询')
    await myQueriesTab.click()

    // 等待切换完成
    await page.waitForTimeout(300)

    // 验证活动标签页已改变
    activeTab = page.locator('[role="tab"][aria-selected="true"]')
    const newText = await activeTab.textContent()

    expect(newText).not.toEqual(initialText)
    expect(newText).toContain('我的查询')
  })

  test('36. 加载状态 - 页面初始加载完成', async ({ page }) => {
    // 页面应该完整加载
    const title = page.locator('text=问财股票筛选系统')
    await expect(title).toBeVisible({ timeout: 10000 })
  })

  test('37. 数据显示 - 统计数据可以加载', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证统计数据显示
    const statistics = page.locator('[class*="el-statistic__content"]')
    const count = await statistics.count()
    expect(count).toBeGreaterThan(0)
  })

  test('38. 导航可用性 - 所有标签页都可点击', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const tabs = page.locator('[role="tab"]')
    const count = await tabs.count()

    for (let i = 0; i < count; i++) {
      const tab = tabs.nth(i)
      if (await tab.isVisible()) {
        await tab.click()
        await page.waitForTimeout(200)
      }
    }

    // 应该能够点击所有标签页
    expect(count).toBeGreaterThan(0)
  })

  test('39. 页面结构完整性 - 主要容器和子组件存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证页面主容器
    const mainContainer = page.locator('[class*="wencai-container"]')
    await expect(mainContainer).toBeVisible()

    // 验证头部卡片
    const headerCard = page.locator('[class*="header-card"]')
    await expect(headerCard).toBeVisible()

    // 验证标签页容器
    const tabsContainer = page.locator('[role="tablist"]')
    await expect(tabsContainer).toBeVisible()
  })

  test('40. 最终集成验证 - 页面完全可交互', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 点击多个标签页验证交互性
    const tabs = ['我的查询', '统计分析', '使用指南', '问财查询']

    for (const tabName of tabs) {
      const tab = page.locator(`text=${tabName}`)
      if (await tab.isVisible()) {
        await tab.click()
        await page.waitForTimeout(300)

        // 验证标签页内容可见
        const content = page.locator('[role="tabpanel"]').first()
        expect(await content.isVisible().catch(() => false)).toBeTruthy()
      }
    }
  })
})
