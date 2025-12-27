/**
 * 菜单功能端到端测试
 * 简化版本，专注核心功能验证
 */

import { test, expect } from '@playwright/test'

test.describe('菜单功能E2E测试', () => {
  test.beforeAll(async ({ page }) => {
    // 确保页面加载
    await page.goto('/')
    await page.waitForTimeout(2000)
  })

  test('基础页面加载', async ({ page }) => {
    // 验证页面标题
    const title = await page.title()
    expect(title).toContain('MyStocks')

    // 验证应用容器
    await expect(page.locator('#app')).toBeVisible()
  })

  test('主导航存在', async ({ page }) => {
    // 验证导航栏
    const navbar = page.locator('.navbar')
    await expect(navbar).toBeVisible()

    // 验证logo
    await expect(page.locator('.logo')).toBeVisible()
  })

  test('侧边栏存在', async ({ page }) => {
    // 验证侧边栏
    const sidebar = page.locator('.sidebar')
    await expect(sidebar).toBeVisible()

    // 验证菜单容器
    await expect(page.locator('.el-menu')).toBeVisible()
  })

  test('菜单项可见性', async ({ page }) => {
    // 等待菜单加载
    await page.waitForSelector('.el-menu-item', { state: 'visible', timeout: 5000 })

    // 检查几个主要菜单项
    const menuItems = ['仪表盘', '市场行情', '股票管理']
    for (const item of menuItems) {
      const element = page.locator(`text=${item}`)
      await expect(element).toBeVisible()
    }
  })

  test('菜单点击导航', async ({ page }) => {
    // 点击仪表盘
    const dashboardLink = page.locator('text=仪表盘')
    await dashboardLink.click()
    await page.waitForTimeout(1000)

    // 验证URL变化
    expect(page.url()).toContain('/dashboard')

    // 点击股票管理
    const stocksLink = page.locator('text=股票管理')
    await stocksLink.click()
    await page.waitForTimeout(1000)

    // 验证URL变化
    expect(page.url()).toContain('/stocks')
  })

  test('侧边栏折叠功能', async ({ page }) => {
    // 获取初始侧边栏
    const sidebar = page.locator('.el-aside')
    const initialWidth = await sidebar.evaluate(el => el.offsetWidth)

    // 点击折叠按钮
    const hamburger = page.locator('.hamburger')
    await hamburger.click()
    await page.waitForTimeout(300)

    // 验证宽度减少
    const collapsedWidth = await sidebar.evaluate(el => el.offsetWidth)
    expect(collapsedWidth).toBeLessThan(initialWidth)
  })

  test('子菜单展开', async ({ page }) => {
    // 展开市场数据菜单
    const marketDataMenu = page.locator('text=市场数据')
    await marketDataMenu.click()
    await page.waitForTimeout(500)

    // 验证子菜单可见
    const subMenus = ['资金流向', 'ETF行情', '问财筛选']
    for (const menu of subMenus) {
      const element = page.locator(`text=${menu}`)
      await expect(element).toBeVisible()
    }
  })
})

test.describe('菜单状态测试', () => {
  test('当前页面高亮', async ({ page }) => {
    // 导航到仪表盘
    await page.goto('/dashboard')
    await page.waitForTimeout(2000)

    // 验证仪表盘菜单高亮
    const dashboardMenuItem = page.locator('.el-menu-item[index="/dashboard"]')
    await expect(dashboardMenuItem).toHaveClass(/is-active/)
  })
})
