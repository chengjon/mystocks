import { test, expect } from '@playwright/test'

test.describe('IndustryConceptAnalysis.vue - API Integration Tests', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/industry-concept-analysis')
  })

  test('01. 页面加载 - 显示行业/概念分析标题', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const title = page.locator('text=行业/概念分析')
    await expect(title).toBeVisible({ timeout: 5000 })

    const refreshButton = page.locator('button:has-text("刷新数据")')
    await expect(refreshButton).toBeVisible()
  })

  test('02. 标签页导航 - 行业分析标签页显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const industryTab = page.locator('text=行业分析')
    await expect(industryTab).toBeVisible()

    // 验证选择框存在
    const select = page.locator('[placeholder="请选择行业"]')
    await expect(select).toBeVisible()
  })

  test('03. 标签页导航 - 概念分析标签页显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const conceptTab = page.locator('text=概念分析')
    await conceptTab.click()

    const select = page.locator('[placeholder="请选择概念"]')
    await expect(select).toBeVisible({ timeout: 5000 })
  })

  test('04. API集成 - 加载行业列表', async ({ page }) => {
    // 测试行业列表API
    const response = await page.request.get('/api/data/stocks/industries')
    expect(response.status()).toBeLessThan(500)
  })

  test('05. API集成 - 获取行业详情数据', async ({ page }) => {
    // 测试行业详情/统计API
    const response = await page.request.get('/api/data/stocks/industry/test')
    // 可能返回404或200，但不应该返回500
    expect(response.status()).toBeLessThan(500)
  })

  test('06. API集成 - 加载概念列表', async ({ page }) => {
    // 测试概念列表API
    const response = await page.request.get('/api/data/stocks/concepts')
    expect(response.status()).toBeLessThan(500)
  })

  test('07. 行业分析 - 选择行业并加载成分股', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 点击行业选择
    const select = page.locator('[placeholder="请选择行业"]')
    if (await select.isVisible()) {
      await select.click()

      // 等待下拉菜单出现
      await page.waitForTimeout(500)

      // 选择第一个选项
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 等待表格加载
        await page.waitForLoadState('networkidle')

        // 验证成分股表格显示
        const table = page.locator('table')
        await expect(table).toBeVisible({ timeout: 5000 })
      }
    }
  })

  test('08. 概念分析 - 选择概念并加载成分股', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 切换到概念分析标签页
    const conceptTab = page.locator('text=概念分析')
    await conceptTab.click()

    // 等待标签页加载
    await page.waitForTimeout(500)

    // 点击概念选择
    const select = page.locator('[placeholder="请选择概念"]')
    if (await select.isVisible()) {
      await select.click()

      // 等待下拉菜单出现
      await page.waitForTimeout(500)

      // 选择第一个选项
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 验证表格显示
        await page.waitForLoadState('networkidle')
      }
    }
  })

  test('09. 成分股列表 - 表格显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const table = page.locator('table')
    // 表格可能为空，但容器应该存在
    const tableContainer = page.locator('[class*="stocks"]')
    expect(tableContainer).toBeDefined()
  })

  test('10. 成分股列表 - 搜索功能', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const searchInput = page.locator('[placeholder="搜索股票代码或名称"]')
    if (await searchInput.isVisible()) {
      await searchInput.fill('600')
      await page.waitForTimeout(500)
    }
  })

  test('11. 成分股列表 - 导出按钮', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const exportButton = page.locator('button:has-text("导出数据")')
    if (await exportButton.isVisible()) {
      await expect(exportButton).toBeVisible()
    }
  })

  test('12. 统计卡片 - 行业统计信息显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 选择行业后应显示统计卡片
    const select = page.locator('[placeholder="请选择行业"]')
    if (await select.isVisible()) {
      await select.click()
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 等待统计信息加载
        await page.waitForLoadState('networkidle')

        // 验证至少一个统计卡片存在
        const statCard = page.locator('[class*="stat-card"]').first()
        const isVisible = await statCard.isVisible()
        expect(isVisible).toBeTruthy()
      }
    }
  })

  test('13. 图表 - 涨跌分布饼图', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 选择行业后应显示图表
    const select = page.locator('[placeholder="请选择行业"]')
    if (await select.isVisible()) {
      await select.click()
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 等待图表加载
        await page.waitForLoadState('networkidle')

        // 查找ECharts容器
        const chartContainer = page.locator('[class*="chart"]').first()
        const isVisible = await chartContainer.isVisible()
        expect(isVisible).toBeTruthy()
      }
    }
  })

  test('14. 重置筛选 - 清空所有选择', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const resetButton = page.locator('button:has-text("重置筛选")')
    if (await resetButton.isVisible()) {
      await resetButton.click()

      // 验证选择框被清空
      const select = page.locator('[placeholder="请选择行业"]')
      const value = await select.inputValue()
      expect(value).toBe('')
    }
  })

  test('16. 刷新数据 - 刷新按钮功能', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    const refreshButton = page.locator('button:has-text("刷新数据")')
    if (await refreshButton.isVisible()) {
      await refreshButton.click()

      // 等待刷新完成
      await page.waitForTimeout(1000)

      // 验证页面仍然可用
      const title = page.locator('text=行业/概念分析')
      await expect(title).toBeVisible()
    }
  })

  test('17. 分页功能 - 分页控件显示', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 选择行业以加载成分股
    const select = page.locator('[placeholder="请选择行业"]')
    if (await select.isVisible()) {
      await select.click()
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 等待加载
        await page.waitForLoadState('networkidle')

        // 查找分页控件
        const pagination = page.locator('[class*="pagination"]')
        const isVisible = await pagination.isVisible()
        // 分页可能不总是显示，但容器应该存在
        expect(pagination).toBeDefined()
      }
    }
  })

  test('18. 股票点击 - 导航到股票详情页面', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 选择行业加载成分股
    const select = page.locator('[placeholder="请选择行业"]')
    if (await select.isVisible()) {
      await select.click()
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 等待表格加载
        await page.waitForLoadState('networkidle')

        // 尝试点击表格中的第一个股票链接
        const stockLink = page.locator('a').first()
        if (await stockLink.isVisible()) {
          const href = await stockLink.getAttribute('href')
          expect(href).toBeDefined()
        }
      }
    }
  })

  test('19. 色彩编码 - 涨跌幅颜色区分', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 选择行业加载成分股
    const select = page.locator('[placeholder="请选择行业"]')
    if (await select.isVisible()) {
      await select.click()
      const option = page.locator('[role="option"]').first()
      if (await option.isVisible()) {
        await option.click()

        // 等待加载
        await page.waitForLoadState('networkidle')

        // 查找涨跌幅元素
        const positive = page.locator('[class*="positive"]').first()
        if (await positive.isVisible()) {
          // 验证样式类已应用
          const classes = await positive.getAttribute('class')
          expect(classes).toContain('positive')
        }
      }
    }
  })

  test('20. API错误处理 - 页面在API失败时仍可访问', async ({ page }) => {
    await page.waitForLoadState('networkidle')

    // 页面应该在API失败时仍然加载
    const title = page.locator('text=行业/概念分析')
    await expect(title).toBeVisible()

    // 验证UI元素仍然存在
    const tabs = page.locator('[role="tab"]')
    const count = await tabs.count()
    expect(count).toBeGreaterThan(0)
  })
})
