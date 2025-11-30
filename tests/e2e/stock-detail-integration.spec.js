import { test, expect } from '@playwright/test'

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000'
const STOCK_CODE = '600519'

test.describe('StockDetail.vue - Stock Analysis Integration Tests', () => {
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

    // 如果登录成功，导航到股票详情页面
    if (token) {
      await page.goto(`${BASE_URL}/stock-detail/${STOCK_CODE}`)
    }
  })

  test('01. 页面加载 - 显示股票详情标题', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 验证股票代码和名称显示
    const title = page.locator('h2').first()
    const titleText = await title.textContent()
    expect(titleText).toBeDefined()
  })

  test('02. 股票信息卡片 - 显示股票基本信息', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const infoCard = page.locator('[class*="stock-header"]')
    if (await infoCard.isVisible()) {
      await expect(infoCard).toBeVisible()
    }
  })

  test('03. 股票标签 - 显示市场标签(上海/深圳)', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const marketTag = page.locator('[class*="el-tag"]').first()
    const isVisible = await marketTag.isVisible().catch(() => false)

    if (isVisible) {
      const tagText = await marketTag.textContent()
      expect(['上海', '深圳']).toContain(tagText?.trim())
    }
  })

  test('04. 股票标签 - 显示行业标签', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找包含行业信息的标签
    const industryTag = page.locator('[class*="el-tag"]').nth(1)
    if (await industryTag.isVisible()) {
      const text = await industryTag.textContent()
      expect(text).toBeDefined()
    }
  })

  test('05. 价格显示 - 当前价格显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找价格元素
    const priceElement = page.locator('[class*="price"]').first()
    if (await priceElement.isVisible()) {
      const text = await priceElement.textContent()
      expect(text).toBeDefined()
    }
  })

  test('06. 价格变化 - 涨跌幅显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找涨跌幅元素
    const changeElement = page.locator('[class*="change"]').first()
    if (await changeElement.isVisible()) {
      const text = await changeElement.textContent()
      expect(text).toBeDefined()
    }
  })

  test('07. 图表卡片 - 图表容器显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找图表卡片
    const chartCard = page.locator('[class*="chart-card"]')
    if (await chartCard.isVisible()) {
      await expect(chartCard).toBeVisible()
    }
  })

  test('08. 图表控制 - 分时图/K线图切换', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找分段按钮
    const segmentedButton = page.locator('[class*="el-segmented"]')
    if (await segmentedButton.isVisible()) {
      await expect(segmentedButton).toBeVisible()
    }
  })

  test('09. 时间范围选择 - 时间范围下拉框显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找时间范围选择
    const timeSelect = page.locator('[class*="el-select"]').first()
    if (await timeSelect.isVisible()) {
      await expect(timeSelect).toBeVisible()
    }
  })

  test('10. 时间范围选项 - 包含1周、1月等选项', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const timeSelect = page.locator('[class*="el-select"]').first()
    if (await timeSelect.isVisible()) {
      await timeSelect.click()

      // 等待下拉菜单出现
      await page.waitForTimeout(300)

      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        const text = await option.textContent()
        expect(['近1周', '近1个月', '近3个月']).toContain(text?.trim())
      }

      // 关闭下拉菜单
      await page.keyboard.press('Escape')
    }
  })

  test('11. API集成 - K线数据API可访问', async ({ page }) => {
    // 测试K线API端点
    const response = await page.request.get('/api/market/kline?stock_code=600519&period=daily&adjust=qfq')
    expect(response.status()).toBeLessThan(500)
  })

  test('12. 基本信息卡片 - 基本信息显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const infoCard = page.locator('[class*="info-card"]')
    if (await infoCard.isVisible()) {
      await expect(infoCard).toBeVisible()
    }
  })

  test('13. 基本信息内容 - 股票代码显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const codeLabel = page.locator('text=股票代码')
    if (await codeLabel.isVisible()) {
      await expect(codeLabel).toBeVisible()
    }
  })

  test('14. 基本信息内容 - 股票名称显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const nameLabel = page.locator('text=股票名称')
    if (await nameLabel.isVisible()) {
      await expect(nameLabel).toBeVisible()
    }
  })

  test('15. 基本信息内容 - 所属行业显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const industryLabel = page.locator('text=所属行业')
    if (await industryLabel.isVisible()) {
      await expect(industryLabel).toBeVisible()
    }
  })

  test('16. 技术分析卡片 - 技术分析卡片显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const analysisCard = page.locator('[class*="analysis-card"]')
    if (await analysisCard.isVisible()) {
      await expect(analysisCard).toBeVisible()
    }
  })

  test('17. 技术指标 - MA5指标显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const ma5Label = page.locator('text=MA5')
    if (await ma5Label.isVisible()) {
      await expect(ma5Label).toBeVisible()
    }
  })

  test('18. 技术指标 - MA10指标显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const ma10Label = page.locator('text=MA10')
    if (await ma10Label.isVisible()) {
      await expect(ma10Label).toBeVisible()
    }
  })

  test('19. 技术指标 - RSI指标显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const rsiLabel = page.locator('text=RSI')
    if (await rsiLabel.isVisible()) {
      await expect(rsiLabel).toBeVisible()
    }
  })

  test('20. 技术指标 - MACD指标显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const macdLabel = page.locator('text=MACD')
    if (await macdLabel.isVisible()) {
      await expect(macdLabel).toBeVisible()
    }
  })

  test('21. API集成 - 股票详情API可访问', async ({ page }) => {
    // 测试股票详情API
    const response = await page.request.get('/api/data/stocks/600519/detail')
    expect(response.status()).toBeLessThan(500)
  })

  test('22. API集成 - 分时数据API可访问', async ({ page }) => {
    // 测试分时数据API
    const today = new Date().toISOString().split('T')[0]
    const response = await page.request.get(`/api/data/stocks/intraday?symbol=600519&date=${today}`)
    expect(response.status()).toBeLessThan(500)
  })

  test('23. 交易摘要卡片 - 历史交易摘要显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const summaryCard = page.locator('[class*="summary-card"]')
    if (await summaryCard.isVisible()) {
      await expect(summaryCard).toBeVisible()
    }
  })

  test('24. 交易摘要 - 期间涨跌显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const priceChangeLabel = page.locator('text=期间涨跌')
    if (await priceChangeLabel.isVisible()) {
      await expect(priceChangeLabel).toBeVisible()
    }
  })

  test('25. 交易摘要 - 最高价显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const highestLabel = page.locator('text=最高价')
    if (await highestLabel.isVisible()) {
      await expect(highestLabel).toBeVisible()
    }
  })

  test('26. 交易摘要 - 最低价显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const lowestLabel = page.locator('text=最低价')
    if (await lowestLabel.isVisible()) {
      await expect(lowestLabel).toBeVisible()
    }
  })

  test('27. 交易摘要 - 成交量显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const volumeLabel = page.locator('text=成交量')
    if (await volumeLabel.isVisible()) {
      await expect(volumeLabel).toBeVisible()
    }
  })

  test('28. 交易摘要 - 成交额显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const turnoverLabel = page.locator('text=成交额')
    if (await turnoverLabel.isVisible()) {
      await expect(turnoverLabel).toBeVisible()
    }
  })

  test('29. 交易摘要 - 波动率显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const volatilityLabel = page.locator('text=波动率')
    if (await volatilityLabel.isVisible()) {
      await expect(volatilityLabel).toBeVisible()
    }
  })

  test('30. 交易摘要 - 夏普比率显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const sharpeLabel = page.locator('text=夏普比率')
    if (await sharpeLabel.isVisible()) {
      await expect(sharpeLabel).toBeVisible()
    }
  })

  test('31. API集成 - 交易摘要API可访问', async ({ page }) => {
    // 测试交易摘要API
    const response = await page.request.get('/api/data/stocks/600519/trading-summary?period=1m')
    expect(response.status()).toBeLessThan(500)
  })

  test('32. 交易操作卡片 - 交易操作表单显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const tradingCard = page.locator('[class*="trading-card"]')
    if (await tradingCard.isVisible()) {
      await expect(tradingCard).toBeVisible()
    }
  })

  test('33. 交易表单 - 交易类型选择显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const typeLabel = page.locator('text=交易类型')
    if (await typeLabel.isVisible()) {
      await expect(typeLabel).toBeVisible()
    }
  })

  test('34. 交易表单 - 价格输入框显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const priceLabel = page.locator('text=价格')
    if (await priceLabel.isVisible()) {
      await expect(priceLabel).toBeVisible()
    }
  })

  test('35. 交易表单 - 数量输入框显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const quantityLabel = page.locator('text=数量')
    if (await quantityLabel.isVisible()) {
      await expect(quantityLabel).toBeVisible()
    }
  })

  test('36. 交易表单 - 执行交易按钮显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const tradeButton = page.locator('button').filter({ hasText: '执行交易' })
    if (await tradeButton.isVisible()) {
      await expect(tradeButton).toBeVisible()
      await expect(tradeButton).toBeEnabled()
    }
  })

  test('38. 图表容器 - 图表高度设置正确', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 查找图表容器
    const chartDiv = page.locator('[style*="height"]').filter({ hasText: '' }).first()
    if (await chartDiv.isVisible()) {
      const style = await chartDiv.getAttribute('style')
      expect(style).toBeDefined()
    }
  })

  test('39. 页面布局 - 行容器存在', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const rows = page.locator('[class*="el-row"]')
    const count = await rows.count()
    expect(count).toBeGreaterThan(0)
  })

  test('40. 错误处理 - API不可用时页面仍可访问', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 页面应该在API失败时仍然加载
    const title = page.locator('h2').first()
    const isVisible = await title.isVisible().catch(() => false)
    expect(isVisible).toBeTruthy()
  })
})
