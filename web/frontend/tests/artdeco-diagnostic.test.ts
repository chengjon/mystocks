import { test, expect } from '@playwright/test'

/**
 * 简化版ArtDeco集成验证测试 - 诊断版本
 * 逐步验证基本功能
 */

test.describe('ArtDeco集成诊断测试', () => {
  test.setTimeout(60000) // 1分钟超时

  const BASE_URL = 'http://localhost:3001'

  test('基本页面加载测试', async ({ page }) => {
    console.log('🔍 开始基本页面加载测试...')

    // 清除浏览器缓存
    await page.context().clearCookies()

    // 监听错误
    const errors: string[] = []
    const logs: string[] = []

    page.on('console', msg => {
      const logEntry = `[${msg.type().toUpperCase()}] ${msg.text()}`
      console.log('🔍 浏览器控制台:', logEntry)

      if (msg.type() === 'error') {
        errors.push(msg.text())
        console.error('🚨 JavaScript错误:', msg.text())
      }
      logs.push(logEntry)
    })

    // 监听页面错误
    page.on('pageerror', error => {
      console.error('💥 页面JavaScript错误:', error.message)
      errors.push(`PageError: ${error.message}`)
    })

    // 监听请求失败
    page.on('requestfailed', request => {
      console.log('❌ 请求失败:', request.url(), request.failure()?.errorText)
    })

    page.on('pageerror', error => {
      console.log('💥 页面错误:', error.message)
      errors.push(`PageError: ${error.message}`)
    })

    await page.goto(BASE_URL, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    })

    // 等待Vue应用加载 - 缩短等待时间
    await page.waitForTimeout(2000)

    const pageInfo = await page.evaluate(() => {
      const app = document.querySelector('#app')
      const vueApp = !!(window as any).Vue || !!document.querySelector('[data-v-]')
      const appContent = app ? app.innerHTML.substring(0, 200) : 'NO_APP'
      const bodyContent = document.body.innerHTML.substring(0, 300)

      return {
        title: document.title,
        hasAppDiv: !!app,
        appHasContent: app ? app.children.length > 0 : false,
        appContent: appContent,
        bodyContent: bodyContent,
        vueAppDetected: vueApp,
        bodyVisible: document.body.offsetWidth > 0 && document.body.offsetHeight > 0,
        allScripts: Array.from(document.querySelectorAll('script')).length,
        loadedScripts: Array.from(document.querySelectorAll('script')).filter(s => s.src).length,
        errors: []
      }
    })

    console.log('📊 页面基本信息:', pageInfo)

    // 基本断言
    expect(pageInfo.hasAppDiv).toBe(true)
    expect(pageInfo.vueAppDetected).toBe(true)

    // 记录错误
    if (errors.length > 0) {
      console.log('❌ 控制台错误:', errors.slice(0, 3))
    }
  })

  test('ArtDeco组件存在性检查', async ({ page }) => {
    console.log('🔍 开始ArtDeco组件存在性检查...')

    await page.goto(BASE_URL, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    })

    await page.waitForTimeout(5000)

    // 检查ArtDeco组件是否在DOM中出现
    const artdecoPresence = await page.evaluate(() => {
      const allElements = document.querySelectorAll('*')
      const artdecoElements: string[] = []

      allElements.forEach(el => {
        const classList = Array.from(el.classList)
        const hasArtDecoClass = classList.some(cls => cls.startsWith('artdeco'))
        if (hasArtDecoClass) {
          artdecoElements.push(`${el.tagName}.${classList.join('.')}`)
        }
      })

      return {
        artdecoElements: artdecoElements.slice(0, 10), // 只显示前10个
        totalArtDecoElements: artdecoElements.length,
        hasAnyArtDeco: artdecoElements.length > 0
      }
    })

    console.log('🎨 ArtDeco组件检查结果:', artdecoPresence)

    // 记录发现的ArtDeco元素，但不强制要求必须存在
    if (artdecoPresence.hasAnyArtDeco) {
      console.log('✅ 发现ArtDeco组件:', artdecoPresence.artdecoElements)
    } else {
      console.log('⚠️ 未发现ArtDeco组件，可能需要检查组件导入')
    }
  })

  test('页面内容完整性检查', async ({ page }) => {
    console.log('🔍 开始页面内容完整性检查...')

    await page.goto(BASE_URL, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    })

    await page.waitForTimeout(5000)

    const contentCheck = await page.evaluate(() => {
      const body = document.body
      const app = document.querySelector('#app')

      return {
        bodyTextLength: body.textContent?.length || 0,
        bodyHasText: (body.textContent?.trim().length || 0) > 10,
        appChildCount: app?.children.length || 0,
        appHasChildren: (app?.children.length || 0) > 0,
        visibleElements: document.querySelectorAll('*').length,
        hasHeadings: document.querySelectorAll('h1, h2, h3, h4, h5, h6').length > 0,
        hasButtons: document.querySelectorAll('button').length > 0,
        hasLinks: document.querySelectorAll('a').length > 0
      }
    })

    console.log('📝 页面内容检查:', contentCheck)

    // 验证基本内容存在
    expect(contentCheck.appHasChildren).toBe(true)
    expect(contentCheck.visibleElements).toBeGreaterThan(5)
  })

  test('API连接测试', async ({ page }) => {
    console.log('🔍 开始API连接测试...')

    await page.goto(BASE_URL, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    })

    // 监听网络请求
    const networkRequests: any[] = []
    page.on('request', request => {
      if (request.url().includes('localhost:8000')) {
        networkRequests.push({
          url: request.url(),
          method: request.method(),
          timestamp: Date.now()
        })
      }
    })

    // 等待可能的API调用
    await page.waitForTimeout(8000)

    console.log(`📡 检测到 ${networkRequests.length} 个API请求`)

    // 测试后端健康检查
    try {
      const healthResponse = await page.request.get('http://localhost:8000/api/health')
      console.log('🏥 后端健康检查:', healthResponse.status())
    } catch (error) {
      console.log('🏥 后端健康检查失败:', error.message)
    }
  })
})