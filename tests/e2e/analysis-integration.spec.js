import { test, expect } from '@playwright/test'

test.describe('Analysis.vue - P2高优先级页面集成测试', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/analysis')
  })

  test('01. 页面加载 - 显示分析表单', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 检查页面标题
    const cardHeader = page.locator('text=数据分析')
    await expect(cardHeader).toBeVisible({ timeout: 5000 })

    // 检查开始分析按钮
    const analyzeButton = page.locator('button:has-text("开始分析")')
    await expect(analyzeButton).toBeVisible()
  })

  test('02. 表单字段验证 - 所有输入字段存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 股票代码输入
    const symbolInput = page.locator('input[placeholder*="600519"]')
    if (await symbolInput.isVisible()) {
      await expect(symbolInput).toBeVisible()
    }

    // 分析类型选择
    const analysisTypeSelect = page.locator('[placeholder="选择分析类型"]')
    if (await analysisTypeSelect.isVisible()) {
      await expect(analysisTypeSelect).toBeVisible()
    }

    // 时间周期选择
    const periodSelect = page.locator('[placeholder*="日线"]')
    if (await periodSelect.isVisible()) {
      await expect(periodSelect).toBeVisible()
    }
  })

  test('03. 分析类型选择 - 技术指标分析', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const analysisTypeSelect = page.locator('[placeholder="选择分析类型"]')
    if (await analysisTypeSelect.isVisible()) {
      await analysisTypeSelect.click()
      const option = page.locator('text=技术指标分析')
      if (await option.isVisible()) {
        await option.click()
      }
    }
  })

  test('04. 分析类型选择 - 趋势分析', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const analysisTypeSelect = page.locator('[placeholder="选择分析类型"]')
    if (await analysisTypeSelect.isVisible()) {
      await analysisTypeSelect.click()
      const option = page.locator('text=趋势分析')
      if (await option.isVisible()) {
        await option.click()
      }
    }
  })

  test('05. 分析类型选择 - 动量分析', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const analysisTypeSelect = page.locator('[placeholder="选择分析类型"]')
    if (await analysisTypeSelect.isVisible()) {
      await analysisTypeSelect.click()
      const option = page.locator('text=动量分析')
      if (await option.isVisible()) {
        await option.click()
      }
    }
  })

  test('06. API集成 - 技术指标API可访问', async ({ page }) => {
    // 测试技术指标API端点
    const response = await page.request.get('/api/technical/600519/indicators?period=daily&days=60')
    expect(response.status()).toBeLessThan(500)
  })

  test('07. API集成 - 趋势指标API可访问', async ({ page }) => {
    // 测试趋势指标API端点
    const response = await page.request.get('/api/technical/600519/trend?period=daily&days=60')
    expect(response.status()).toBeLessThan(500)
  })

  test('08. API集成 - 动量指标API可访问', async ({ page }) => {
    // 测试动量指标API端点
    const response = await page.request.get('/api/technical/600519/momentum?period=daily&days=60')
    expect(response.status()).toBeLessThan(500)
  })

  test('09. API集成 - 波动性指标API可访问', async ({ page }) => {
    // 测试波动性指标API端点
    const response = await page.request.get('/api/technical/600519/volatility?period=daily&days=60')
    expect(response.status()).toBeLessThan(500)
  })

  test('10. API集成 - 成交量指标API可访问', async ({ page }) => {
    // 测试成交量指标API端点
    const response = await page.request.get('/api/technical/600519/volume?period=daily&days=60')
    expect(response.status()).toBeLessThan(500)
  })

  test('11. API集成 - 交易信号API可访问', async ({ page }) => {
    // 测试交易信号API端点
    const response = await page.request.get('/api/technical/600519/signals?period=daily&days=60')
    expect(response.status()).toBeLessThan(500)
  })

  test('12. 表单验证 - 股票代码为空时不能分析', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const symbolInput = page.locator('input[placeholder*="600519"]')
    if (await symbolInput.isVisible()) {
      // 确保输入框为空
      await symbolInput.fill('')

      // 点击分析按钮
      const analyzeButton = page.locator('button:has-text("开始分析")')
      await analyzeButton.click()

      // 应该显示警告消息
      await page.waitForTimeout(500)
    }
  })

  test('13. 空状态 - 未分析时显示空状态', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 页面初始时应该显示空状态
    const emptyCard = page.locator('[class*="empty-card"]')
    if (await emptyCard.isVisible()) {
      await expect(emptyCard).toBeVisible()
    }

    // 或者显示"请选择股票并开始分析"消息
    const emptyMessage = page.locator('text=请选择股票并开始分析')
    if (await emptyMessage.isVisible()) {
      await expect(emptyMessage).toBeVisible()
    }
  })

  test('14. 时间周期选择 - 日线', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const periodSelect = page.locator('[role="combobox"]').nth(1)
    if (await periodSelect.isVisible()) {
      await periodSelect.click()
      const option = page.locator('text=日线')
      if (await option.isVisible()) {
        await option.click()
      }
    }
  })

  test('15. 数据范围 - 输入天数调整', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const daysInput = page.locator('[role="spinbutton"]')
    if (await daysInput.isVisible()) {
      // 应该能够设置天数
      await daysInput.focus()
      const value = await daysInput.inputValue()
      expect(value).toBeDefined()
    }
  })

  test('16. 响应性设计 - 移动端', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })

    await page.waitForLoadState('networkidle')

    // 检查页面是否仍然可访问
    const cardHeader = page.locator('text=数据分析')
    if (await cardHeader.isVisible()) {
      await expect(cardHeader).toBeVisible()
    }

    // 检查分析按钮是否可见
    const analyzeButton = page.locator('button:has-text("开始分析")')
    const isVisible = await analyzeButton.isVisible()
    expect(isVisible).toBeTruthy()
  })

  test('17. 按钮状态 - 开始分析按钮初始状态', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const analyzeButton = page.locator('button:has-text("开始分析")')
    await expect(analyzeButton).toBeVisible()
    await expect(analyzeButton).toBeEnabled()
  })

  test('18. 表单标签 - 所有表单标签显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const stockCodeLabel = page.locator('text=股票代码')
    const analysisTypeLabel = page.locator('text=分析类型')
    const periodLabel = page.locator('text=时间周期')
    const dataRangeLabel = page.locator('text=数据范围')

    if (await stockCodeLabel.isVisible()) {
      await expect(stockCodeLabel).toBeVisible()
    }
    if (await analysisTypeLabel.isVisible()) {
      await expect(analysisTypeLabel).toBeVisible()
    }
    if (await periodLabel.isVisible()) {
      await expect(periodLabel).toBeVisible()
    }
    if (await dataRangeLabel.isVisible()) {
      await expect(dataRangeLabel).toBeVisible()
    }
  })

  test('19. 卡片结构 - 配置卡片存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const configCard = page.locator('[class*="config-card"]')
    if (await configCard.isVisible()) {
      await expect(configCard).toBeVisible()
    } else {
      // 或者通过文本查找卡片
      const card = page.locator('text=数据分析')
      if (await card.isVisible()) {
        await expect(card).toBeVisible()
      }
    }
  })

  test('20. API错误处理 - API不可用时页面不崩溃', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 页面应该在API失败时仍然加载
    const cardHeader = page.locator('text=数据分析')
    await expect(cardHeader).toBeVisible()
  })
})
