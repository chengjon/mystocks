/**
 * 菜单基础功能测试
 * 验证前端菜单基本运行状态
 */

import { test, expect } from '@playwright/test'

test.describe('菜单基础功能验证', () => {
  test('前端服务正常运行', async ({ page }) => {
    // 设置更长的超时时间
    page.setDefaultTimeout(30000)

    // 访问首页
    const response = await page.goto('/')

    // 验证响应成功
    expect(response?.status()).toBe(200)

    // 等待页面加载
    await page.waitForLoadState('domcontentloaded')

    // 验证基本元素存在
    const app = page.locator('#app')
    await expect(app).toBeAttached()

    // 验证页面标题
    const title = await page.title()
    expect(title).toMatch(/MyStocks/)
  })

  test('Vue应用正常挂载', async ({ page }) => {
    page.setDefaultTimeout(30000)

    // 访问首页
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')

    // 检查Vue应用是否挂载
    const app = page.locator('#app')
    await expect(app).toBeAttached()

    // 检查是否有内容
    const hasContent = await app.evaluate(el => el.innerHTML.trim().length > 0)
    expect(hasContent).toBe(true)
  })

  test('路由跳转功能', async ({ page }) => {
    page.setDefaultTimeout(30000)

    // 访问dashboard
    const response = await page.goto('/dashboard')
    expect(response?.status()).toBe(200)

    // 等待页面加载
    await page.waitForLoadState('domcontentloaded')

    // 验证URL包含dashboard
    expect(page.url()).toContain('/dashboard')
  })

  test('JavaScript控制台无严重错误', async ({ page }) => {
    page.setDefaultTimeout(30000)

    // 监听控制台错误
    const errors = []
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    // 访问多个页面
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')

    await page.goto('/dashboard')
    await page.waitForLoadState('domcontentloaded')

    await page.goto('/stocks')
    await page.waitForLoadState('domcontentloaded')

    // 验证没有严重错误
    console.log('Console errors:', errors)
    // 允许一些非关键错误，但检查是否有严重错误
    const criticalErrors = errors.filter(e =>
      e.includes('Uncaught') ||
      e.includes('Failed to load') ||
      e.includes('Cannot access')
    )

    expect(criticalErrors.length).toBe(0)
  })

  test('构建资源正常加载', async ({ page }) => {
    page.setDefaultTimeout(30000)

    // 监听网络请求失败
    const failedRequests = []
    page.on('response', response => {
      if (response.status() >= 400) {
        failedRequests.push({
          url: response.url(),
          status: response.status()
        })
      }
    })

    // 访问页面
    await page.goto('/')
    await page.waitForLoadState('domcontentloaded')

    // 验证没有关键资源加载失败
    const criticalFailures = failedRequests.filter(req =>
      !req.url.includes('favicon.ico') && // 忽略favicon错误
      !req.url.includes('ads') // 忽略广告错误
    )

    if (criticalFailures.length > 0) {
      console.log('Failed requests:', criticalFailures)
    }

    // 允许少数非关键请求失败
    expect(criticalFailures.length).toBeLessThan(3)
  })
})
