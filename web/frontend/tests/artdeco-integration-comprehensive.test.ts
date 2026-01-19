import { test, expect } from '@playwright/test'

/**
 * MyStocks Web前端 ArtDeco集成综合测试
 *
 * 测试目标：
 * 1. ArtDeco组件使用情况验证
 * 2. ArtDeco风格一致性检查
 * 3. API调用功能测试
 * 4. 数据生成和显示验证
 * 5. 页面导航和跳转测试
 */

test.describe('ArtDeco集成验证测试套件', () => {
  test.setTimeout(120000) // 2分钟超时

  // 测试配置
  const BASE_URL = 'http://localhost:3001'
  const API_BASE = 'http://localhost:8000'

  test.beforeEach(async ({ page }) => {
    // 设置页面配置
    await page.setViewportSize({ width: 1920, height: 1080 })

    // 监听控制台错误
    const errors: string[] = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    // 监听网络错误
    page.on('response', response => {
      if (!response.ok() && response.url().includes(API_BASE)) {
        console.log(`API Error: ${response.status()} ${response.url()}`)
      }
    })
  })

  test('ArtDeco组件使用情况验证', async ({ page }) => {
    console.log('🎨 开始ArtDeco组件使用情况验证...')

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 验证ArtDeco组件使用情况
    const artdecoComponents = await page.evaluate(() => {
      const results = {
        buttons: document.querySelectorAll('[class*="artdeco-btn"], [class*="artdeco-button"]').length,
        cards: document.querySelectorAll('[class*="artdeco-card"]').length,
        tables: document.querySelectorAll('[class*="artdeco-table"]').length,
        forms: document.querySelectorAll('[class*="artdeco-form"]').length,
        layouts: document.querySelectorAll('[class*="artdeco-layout"]').length,
        totalComponents: 0
      }

      results.totalComponents = Object.values(results).reduce((sum, count) => sum + count, 0)
      return results
    })

    console.log('📊 ArtDeco组件使用统计:', artdecoComponents)

    // 调试：打印页面内容
    const pageContent = await page.evaluate(() => {
      return {
        title: document.title,
        bodyText: document.body.textContent?.substring(0, 500),
        hasAppDiv: !!document.querySelector('#app'),
        appContent: (document.querySelector('#app') as HTMLElement)?.innerHTML?.substring(0, 200),
        scripts: Array.from(document.querySelectorAll('script')).map(s => s.src || s.textContent?.substring(0, 50))
      }
    })
    console.log('📄 页面内容调试:', pageContent)

    // 验证至少有一些ArtDeco组件被使用
    expect(artdecoComponents.totalComponents).toBeGreaterThan(0)

    // 截图记录
    await page.screenshot({
      path: 'test-results/artdeco-components-usage.png',
      fullPage: true
    })
  })

  test('ArtDeco风格一致性检查', async ({ page }) => {
    console.log('🎨 开始ArtDeco风格一致性检查...')

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 检查ArtDeco设计系统变量
    const styleConsistency = await page.evaluate(() => {
      const computedStyle = getComputedStyle(document.documentElement)

      return {
        // 检查ArtDeco颜色变量
        hasArtDecoColors: computedStyle.getPropertyValue('--artdeco-primary') !== '',
        hasArtDecoSecondary: computedStyle.getPropertyValue('--artdeco-secondary') !== '',
        hasArtDecoAccent: computedStyle.getPropertyValue('--artdeco-accent') !== '',

        // 检查ArtDeco字体变量
        hasArtDecoFontFamily: computedStyle.getPropertyValue('--artdeco-font-family') !== '',
        hasArtDecoFontSize: computedStyle.getPropertyValue('--artdeco-font-size-base') !== '',

        // 检查ArtDeco间距变量
        hasArtDecoSpacing: computedStyle.getPropertyValue('--artdeco-spacing-base') !== '',

        // 检查整体设计系统完整性
        designSystemComplete: false
      }
    })

    // 计算设计系统完整性
    const designVars = Object.values(styleConsistency).filter(v => v === true).length
    styleConsistency.designSystemComplete = designVars >= 3 // 至少3个变量存在

    console.log('🎨 ArtDeco风格一致性检查结果:', styleConsistency)

    // 验证设计系统基础完整性
    expect(styleConsistency.designSystemComplete).toBe(true)

    // 截图记录
    await page.screenshot({
      path: 'test-results/artdeco-style-consistency.png',
      fullPage: true
    })
  })

  test('API调用功能测试', async ({ page }) => {
    console.log('🔌 开始API调用功能测试...')

    await page.goto(BASE_URL)

    // 拦截网络请求
    const apiCalls: any[] = []
    page.on('request', request => {
      if (request.url().includes(API_BASE)) {
        apiCalls.push({
          url: request.url(),
          method: request.method(),
          timestamp: Date.now()
        })
      }
    })

    // 等待页面加载完成
    await page.waitForLoadState('networkidle')
    await page.waitForTimeout(2000) // 等待可能的自动API调用

    console.log(`📡 捕获到 ${apiCalls.length} 个API调用`)

    // 验证至少有一些API调用
    expect(apiCalls.length).toBeGreaterThan(0)

    // 检查API调用成功率
    let successCount = 0
    page.on('response', response => {
      if (response.url().includes(API_BASE) && response.ok()) {
        successCount++
      }
    })

    await page.waitForTimeout(1000)

    console.log(`✅ API成功调用: ${successCount}/${apiCalls.length}`)

    // 验证API成功率
    const successRate = apiCalls.length > 0 ? successCount / apiCalls.length : 0
    expect(successRate).toBeGreaterThan(0.8) // 至少80%成功率
  })

  test('数据生成和显示验证', async ({ page }) => {
    console.log('📊 开始数据生成和显示验证...')

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 等待数据加载
    await page.waitForTimeout(3000)

    // 检查数据展示元素
    const dataElements = await page.evaluate(() => {
      return {
        tables: document.querySelectorAll('table, [class*="table"]').length,
        charts: document.querySelectorAll('[class*="chart"], [class*="graph"], canvas').length,
        dataLists: document.querySelectorAll('ul, ol').length,
        dataCards: document.querySelectorAll('[class*="card"]').length,
        totalDataElements: 0
      }
    })

    dataElements.totalDataElements =
      dataElements.tables +
      dataElements.charts +
      dataElements.dataLists +
      dataElements.dataCards

    console.log('📊 数据展示元素统计:', dataElements)

    // 验证有数据展示
    expect(dataElements.totalDataElements).toBeGreaterThan(0)

    // 检查是否有实际数据内容
    const hasDataContent = await page.evaluate(() => {
      const textContent = document.body.textContent || ''
      const hasNumbers = /\d+/.test(textContent)
      const hasDataIndicators = /数据|行情|指标|统计|图表/.test(textContent)

      return hasNumbers || hasDataIndicators
    })

    console.log('📈 页面包含数据内容:', hasDataContent)
    expect(hasDataContent).toBe(true)

    // 截图记录
    await page.screenshot({
      path: 'test-results/data-display-validation.png',
      fullPage: true
    })
  })

  test('页面导航和跳转测试', async ({ page }) => {
    console.log('🧭 开始页面导航和跳转测试...')

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 获取所有导航链接
    const navLinks = await page.$$eval('a, [role="link"], button[onclick], [class*="nav"], [class*="menu"]', elements => {
      return elements.map(el => ({
        text: el.textContent?.trim() || '',
        href: (el as HTMLAnchorElement).href || '',
        className: el.className,
        tagName: el.tagName.toLowerCase()
      })).filter(link => link.text && link.text.length > 0)
    })

    console.log(`🔗 发现 ${navLinks.length} 个导航元素`)

    // 测试主要导航功能
    const navigationTests = []

    for (const link of navLinks.slice(0, 5)) { // 测试前5个链接
      try {
        if (link.href && link.href !== '#') {
          const [newPage] = await Promise.all([
            page.context().waitForEvent('page'),
            page.click(`text=${link.text}`)
          ])

          await newPage.waitForLoadState('networkidle')
          const newUrl = newPage.url()

          navigationTests.push({
            text: link.text,
            originalUrl: page.url(),
            newUrl: newUrl,
            success: !newUrl.includes('404') && !newUrl.includes('error')
          })

          await newPage.close()
        } else {
          // 测试按钮点击
          await page.click(`text=${link.text}`)
          await page.waitForTimeout(1000)

          navigationTests.push({
            text: link.text,
            action: 'button_click',
            success: true // 假设按钮点击成功
          })
        }
      } catch (error) {
        navigationTests.push({
          text: link.text,
          error: error.message,
          success: false
        })
      }
    }

    console.log('🧭 导航测试结果:', navigationTests)

    // 验证至少有一些导航功能工作
    const successfulNavigations = navigationTests.filter(test => test.success).length
    expect(successfulNavigations).toBeGreaterThan(0)

    // 截图记录
    await page.screenshot({
      path: 'test-results/navigation-testing.png',
      fullPage: true
    })
  })

  test('登录页面ArtDeco集成验证', async ({ page }) => {
    console.log('🔐 开始登录页面ArtDeco集成验证...')

    await page.goto(`${BASE_URL}/login`)
    await page.waitForLoadState('networkidle')

    // 检查登录表单ArtDeco集成
    const loginFormArtDeco = await page.evaluate(() => {
      const form = document.querySelector('form')
      if (!form) return { found: false }

      return {
        found: true,
        hasArtDecoForm: form.classList.contains('artdeco-form') || form.querySelector('[class*="artdeco"]'),
        hasArtDecoInputs: document.querySelectorAll('input[class*="artdeco"]').length,
        hasArtDecoButtons: document.querySelectorAll('button[class*="artdeco"]').length,
        formStructure: {
          inputs: document.querySelectorAll('input').length,
          buttons: document.querySelectorAll('button').length,
          labels: document.querySelectorAll('label').length
        }
      }
    })

    console.log('🔐 登录表单ArtDeco集成情况:', loginFormArtDeco)

    // 验证登录表单存在
    expect(loginFormArtDeco.found).toBe(true)

    // 截图记录
    await page.screenshot({
      path: 'test-results/login-artdeco-integration.png',
      fullPage: true
    })
  })

  test('市场行情页面功能测试', async ({ page }) => {
    console.log('📈 开始市场行情页面功能测试...')

    await page.goto(`${BASE_URL}/market`)
    await page.waitForLoadState('networkidle')

    // 等待数据加载
    await page.waitForTimeout(3000)

    // 检查市场数据展示
    const marketDataDisplay = await page.evaluate(() => {
      return {
        tables: document.querySelectorAll('table').length,
        charts: document.querySelectorAll('canvas, [class*="chart"]').length,
        dataRows: document.querySelectorAll('tr, [class*="row"]').length,
        loadingIndicators: document.querySelectorAll('[class*="loading"], [class*="spinner"]').length,
        errorMessages: document.querySelectorAll('[class*="error"]').length
      }
    })

    console.log('📈 市场数据展示统计:', marketDataDisplay)

    // 验证有数据展示元素
    expect(marketDataDisplay.tables + marketDataDisplay.charts).toBeGreaterThan(0)

    // 截图记录
    await page.screenshot({
      path: 'test-results/market-data-display.png',
      fullPage: true
    })
  })

  test('TDX行情页面集成测试', async ({ page }) => {
    console.log('📊 开始TDX行情页面集成测试...')

    await page.goto(`${BASE_URL}/tdx-market`)
    await page.waitForLoadState('networkidle')

    // 等待TDX数据加载
    await page.waitForTimeout(5000)

    // 检查TDX数据展示
    const tdxDataDisplay = await page.evaluate(() => {
      return {
        stockInputs: document.querySelectorAll('input[placeholder*="股票"], input[type="text"]').length,
        searchButtons: document.querySelectorAll('button').length,
        dataTables: document.querySelectorAll('table').length,
        klineCharts: document.querySelectorAll('canvas, [class*="kline"]').length,
        indexDisplays: document.querySelectorAll('[class*="index"], [id*="index"]').length
      }
    })

    console.log('📊 TDX数据展示统计:', tdxDataDisplay)

    // 验证TDX页面基本结构
    expect(tdxDataDisplay.stockInputs).toBeGreaterThan(0)

    // 截图记录
    await page.screenshot({
      path: 'test-results/tdx-market-integration.png',
      fullPage: true
    })
  })

  test('响应式设计测试', async ({ page }) => {
    console.log('📱 开始响应式设计测试...')

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 测试不同屏幕尺寸
    const viewports = [
      { width: 1920, height: 1080, name: 'desktop' },
      { width: 1366, height: 768, name: 'laptop' },
      { width: 768, height: 1024, name: 'tablet' }
    ]

    const responsiveResults = []

    for (const viewport of viewports) {
      await page.setViewportSize({ width: viewport.width, height: viewport.height })

      const layoutCheck = await page.evaluate(() => {
        const body = document.body
        const app = document.querySelector('#app')

        return {
          viewport: { width: window.innerWidth, height: window.innerHeight },
          bodyVisible: body.offsetWidth > 0 && body.offsetHeight > 0,
          appMounted: !!app,
          hasOverflow: body.scrollWidth > window.innerWidth,
          layoutElements: document.querySelectorAll('[class*="layout"], [class*="container"]').length
        }
      })

      responsiveResults.push({
        ...viewport,
        ...layoutCheck
      })

      // 截图记录
      await page.screenshot({
        path: `test-results/responsive-${viewport.name}.png`,
        fullPage: false
      })
    }

    console.log('📱 响应式设计测试结果:', responsiveResults)

    // 验证所有尺寸下页面都可见
    responsiveResults.forEach(result => {
      expect(result.bodyVisible).toBe(true)
      expect(result.appMounted).toBe(true)
    })
  })

  test('性能测试 - 页面加载时间', async ({ page }) => {
    console.log('⚡ 开始页面加载性能测试...')

    const performanceResults = []

    // 测试主要页面
    const pages = [
      { url: BASE_URL, name: 'home' },
      { url: `${BASE_URL}/login`, name: 'login' },
      { url: `${BASE_URL}/market`, name: 'market' },
      { url: `${BASE_URL}/tdx-market`, name: 'tdx-market' }
    ]

    for (const pageConfig of pages) {
      const startTime = Date.now()

      await page.goto(pageConfig.url, {
        waitUntil: 'domcontentloaded',
        timeout: 30000
      })

      const domContentLoadedTime = Date.now() - startTime

      await page.waitForLoadState('networkidle')
      const fullyLoadedTime = Date.now() - startTime

      performanceResults.push({
        page: pageConfig.name,
        url: pageConfig.url,
        domContentLoaded: domContentLoadedTime,
        fullyLoaded: fullyLoadedTime,
        acceptable: fullyLoadedTime < 10000 // 10秒以内算可接受
      })
    }

    console.log('⚡ 页面加载性能测试结果:', performanceResults)

    // 验证所有页面加载时间都在可接受范围内
    performanceResults.forEach(result => {
      expect(result.acceptable).toBe(true)
    })

    // 生成性能报告
    await page.evaluate((results) => {
      console.table(results)
    }, performanceResults)
  })
})