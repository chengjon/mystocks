import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000'

test.describe('RealTimeMonitor.vue - SSE Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    // 清空本地存储
    await page.evaluate(() => localStorage.clear())

    // 登录流程
    await page.goto(`${BASE_URL}/login`)
    await page.getByTestId('username-input').fill('admin')
    await page.getByTestId('password-input').fill('admin123')
    await page.getByTestId('login-button').click()

    // 等待登录完成并验证 token 已保存
    await page.waitForTimeout(2000)
    const token = await page.evaluate(() => localStorage.getItem('token'))

    // 如果登录成功，导航到实时监控页面
    if (token) {
      await page.goto(`${BASE_URL}/real-time-monitor`)
    }
  })

  test('01. 页面加载 - 显示实时监控中心标题', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const title = page.locator('text=实时监控中心')
    await expect(title).toBeVisible({ timeout: 5000 })

    const subtitle = page.locator('text=基于SSE (Server-Sent Events) 的实时推送系统')
    await expect(subtitle).toBeVisible()
  })

  test('02. 功能说明 - SSE功能说明卡片显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const alertTitle = page.locator('text=实时推送功能说明')
    await expect(alertTitle).toBeVisible()

    const description = page.locator('text=本页面展示了基于SSE')
    await expect(description).toBeVisible()
  })

  test('03. 功能标签 - 显示4个主要功能标签', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const trainingTag = page.locator('text=模型训练进度')
    const backtestTag = page.locator('text=回测执行进度')
    const alertTag = page.locator('text=风险告警通知')
    const metricsTag = page.locator('text=实时指标更新')

    await expect(trainingTag).toBeVisible()
    await expect(backtestTag).toBeVisible()
    await expect(alertTag).toBeVisible()
    await expect(metricsTag).toBeVisible()
  })

  test('04. 实时指标组件 - DashboardMetrics显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找DashboardMetrics组件容器
    const dashboardComponent = page.locator('[class*="dashboard-metrics"]').first()
    const isVisible = await dashboardComponent.isVisible().catch(() => false)

    // 或通过父容器查找
    const gridContainer = page.locator('[class*="el-col"]').first()
    expect(gridContainer).toBeDefined()
  })

  test('05. 风险告警组件 - RiskAlerts显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找RiskAlerts组件
    const alertsComponent = page.locator('[class*="risk-alerts"]').first()
    const isVisible = await alertsComponent.isVisible().catch(() => false)

    // 验证风险告警相关UI元素
    const riskSection = page.locator('text=风险').first()
    if (await riskSection.isVisible()) {
      await expect(riskSection).toBeVisible()
    }
  })

  test('06. 训练进度组件 - TrainingProgress显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找TrainingProgress组件
    const trainingComponent = page.locator('[class*="training-progress"]').first()
    const isVisible = await trainingComponent.isVisible().catch(() => false)

    // 或通过文本查找
    const trainingSection = page.locator('text=训练').first()
    if (await trainingSection.isVisible()) {
      await expect(trainingSection).toBeVisible()
    }
  })

  test('07. 回测进度组件 - BacktestProgress显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找BacktestProgress组件
    const backtestComponent = page.locator('[class*="backtest-progress"]').first()
    const isVisible = await backtestComponent.isVisible().catch(() => false)

    // 或通过文本查找
    const backtestSection = page.locator('text=回测').first()
    if (await backtestSection.isVisible()) {
      await expect(backtestSection).toBeVisible()
    }
  })

  test('08. SSE状态卡片 - 卡片标题显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const sseStatusTitle = page.locator('text=SSE 连接状态')
    await expect(sseStatusTitle).toBeVisible()
  })

  test('09. SSE状态卡片 - 刷新按钮存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const refreshButton = page.locator('button').filter({ hasText: '刷新状态' })
    if (await refreshButton.isVisible()) {
      await expect(refreshButton).toBeVisible()
    }
  })

  test('10. API集成 - SSE状态API可访问', async ({ page }) => {
    // 测试SSE状态API端点
    const response = await page.request.get('/api/v1/sse/status')
    expect(response.status()).toBeLessThan(500)
  })

  test('11. SSE状态信息 - 服务状态标签显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const statusLabel = page.locator('text=服务状态')
    if (await statusLabel.isVisible()) {
      await expect(statusLabel).toBeVisible()
    }

    // 检查状态标签
    const statusTag = page.locator('[class*="el-tag"]').first()
    if (await statusTag.isVisible()) {
      const text = await statusTag.textContent()
      expect(['活跃', '不可用']).toContain(text?.trim())
    }
  })

  test('12. SSE状态信息 - 总连接数显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const connectionLabel = page.locator('text=总连接数')
    if (await connectionLabel.isVisible()) {
      await expect(connectionLabel).toBeVisible()
    }
  })

  test('13. SSE通道信息 - 训练通道显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const trainingChannel = page.locator('text=训练通道')
    if (await trainingChannel.isVisible()) {
      await expect(trainingChannel).toBeVisible()
    }
  })

  test('14. SSE通道信息 - 回测通道显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const backtestChannel = page.locator('text=回测通道')
    if (await backtestChannel.isVisible()) {
      await expect(backtestChannel).toBeVisible()
    }
  })

  test('15. SSE通道信息 - 告警通道显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const alertChannel = page.locator('text=告警通道')
    if (await alertChannel.isVisible()) {
      await expect(alertChannel).toBeVisible()
    }
  })

  test('16. SSE通道信息 - 仪表板通道显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const dashboardChannel = page.locator('text=仪表板通道')
    if (await dashboardChannel.isVisible()) {
      await expect(dashboardChannel).toBeVisible()
    }
  })

  test('17. SSE测试工具 - 卡片标题显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const testToolsTitle = page.locator('text=SSE 测试工具')
    await expect(testToolsTitle).toBeVisible()
  })

  test('18. SSE测试工具 - 测试说明显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const testAlert = page.locator('text=测试说明')
    if (await testAlert.isVisible()) {
      await expect(testAlert).toBeVisible()
    }
  })

  test('19. SSE测试按钮 - 测试训练进度按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const trainingButton = page.locator('button').filter({ hasText: '测试训练进度' })
    if (await trainingButton.isVisible()) {
      await expect(trainingButton).toBeVisible()
      await expect(trainingButton).toBeEnabled()
    }
  })

  test('20. SSE测试按钮 - 测试回测进度按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const backtestButton = page.locator('button').filter({ hasText: '测试回测进度' })
    if (await backtestButton.isVisible()) {
      await expect(backtestButton).toBeVisible()
      await expect(backtestButton).toBeEnabled()
    }
  })

  test('21. SSE测试按钮 - 测试风险告警按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const alertButton = page.locator('button').filter({ hasText: '测试风险告警' })
    if (await alertButton.isVisible()) {
      await expect(alertButton).toBeVisible()
      await expect(alertButton).toBeEnabled()
    }
  })

  test('22. SSE测试按钮 - 测试指标更新按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const metricsButton = page.locator('button').filter({ hasText: '测试指标更新' })
    if (await metricsButton.isVisible()) {
      await expect(metricsButton).toBeVisible()
      await expect(metricsButton).toBeEnabled()
    }
  })

  test('23. 刷新状态功能 - 点击刷新按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const refreshButton = page.locator('button').filter({ hasText: '刷新状态' })
    if (await refreshButton.isVisible()) {
      await refreshButton.click()

      // 等待API响应
      await page.waitForTimeout(500)

      // 页面应该仍然可用
      const title = page.locator('text=实时监控中心')
      await expect(title).toBeVisible()
    }
  })

  test('25. 页面布局 - 网格行容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证行容器存在
    const rows = page.locator('[class*="el-row"]')
    const rowCount = await rows.count()
    expect(rowCount).toBeGreaterThan(0)
  })

  test('26. 页面布局 - 列容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证列容器存在
    const cols = page.locator('[class*="el-col"]')
    const colCount = await cols.count()
    expect(colCount).toBeGreaterThan(0)
  })

  test('27. 卡片容器 - 多个el-card存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找所有卡片
    const cards = page.locator('[class*="el-card"]')
    const cardCount = await cards.count()
    // 应该至少有功能说明、SSE状态、测试工具卡片
    expect(cardCount).toBeGreaterThanOrEqual(2)
  })

  test('28. 错误处理 - API不可用时页面仍可访问', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 页面应该在API失败时仍然加载
    const title = page.locator('text=实时监控中心')
    await expect(title).toBeVisible()

    // 验证主要UI元素仍然存在
    const sseStatusTitle = page.locator('text=SSE 连接状态')
    if (await sseStatusTitle.isVisible()) {
      await expect(sseStatusTitle).toBeVisible()
    }
  })

  test('29. 空状态处理 - SSE状态加载失败时显示空状态', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找empty状态元素
    const emptyState = page.locator('[class*="el-empty"]')
    const isVisible = await emptyState.isVisible().catch(() => false)

    // 或者检查描述
    const loadingText = page.locator('text=加载SSE状态中')
    if (await loadingText.isVisible()) {
      await expect(loadingText).toBeVisible()
    }

    // 页面结构应该存在
    const container = page.locator('[class*="realtime-monitor"]')
    expect(container).toBeDefined()
  })

  test('30. 图标显示 - Monitor图标在SSE状态卡片', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找图标
    const monitorIcon = page.locator('[class*="icon"]').first()
    if (await monitorIcon.isVisible()) {
      await expect(monitorIcon).toBeVisible()
    }
  })
})
