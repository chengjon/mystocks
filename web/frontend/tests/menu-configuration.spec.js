/**
 * 菜单配置自动化测试
 * 验证基于配置文件的动态菜单功能
 */

import { test, expect } from '@playwright/test'

// 测试基础URL
const BASE_URL = 'http://localhost:3000'

test.describe('菜单配置功能测试', () => {
  test.beforeEach(async ({ page }) => {
    // 确保页面加载完成
    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')
  })

  test('页面正常加载', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/MyStocks/)

    // 验证logo存在
    await expect(page.locator('.logo')).toBeVisible()
    await expect(page.locator('.logo span')).toContainText('MyStocks')
  })

  test('菜单项正确渲染', async ({ page }) => {
    // 等待菜单加载
    await page.waitForSelector('.el-menu', { state: 'visible' })

    // 验证主菜单项
    const mainMenus = [
      '仪表盘',
      '市场行情',
      '市场数据',
      '股票管理',
      '数据分析',
      '技术分析',
      '风险监控',
      '交易管理',
      '量化策略',
      '功能演示',
      '系统设置'
    ]

    for (const menu of mainMenus) {
      const menuElement = page.locator(`.el-menu-item:has-text("${menu}")`)
      await expect(menuElement).toBeVisible({ timeout: 5000 })
    }
  })

  test('子菜单展开和收起', async ({ page }) => {
    // 测试市场行情子菜单
    const marketMenu = page.locator('.el-sub-menu:has-text("市场行情")')
    await marketMenu.click()

    // 验证子菜单项显示
    await expect(page.locator('.el-menu-item:has-text("实时行情")')).toBeVisible()
    await expect(page.locator('.el-menu-item:has-text("TDX行情")')).toBeVisible()

    // 再次点击收起
    await marketMenu.click()

    // 验证子菜单项隐藏
    await expect(page.locator('.el-menu-item:has-text("实时行情")')).not.toBeVisible()
  })

  test('菜单导航功能', async ({ page }) => {
    // 点击仪表盘菜单
    await page.click('.el-menu-item:has-text("仪表盘")')
    await page.waitForURL('**/dashboard')
    await expect(page.url()).toContain('/dashboard')

    // 点击股票管理
    await page.click('.el-menu-item:has-text("股票管理")')
    await page.waitForURL('**/stocks')
    await expect(page.url()).toContain('/stocks')

    // 点击数据分析
    await page.click('.el-menu-item:has-text("数据分析")')
    await page.waitForURL('**/analysis')
    await expect(page.url()).toContain('/analysis')
  })

  test('侧边栏折叠功能', async ({ page }) => {
    // 获取初始宽度
    const sidebar = page.locator('.el-aside')
    const initialWidth = await sidebar.evaluate(el => getComputedStyle(el).width)

    // 点击折叠按钮
    await page.click('.hamburger')

    // 验证宽度变化
    const collapsedWidth = await sidebar.evaluate(el => getComputedStyle(el).width)
    expect(parseInt(collapsedWidth)).toBeLessThan(parseInt(initialWidth))

    // 验证logo文字隐藏
    await expect(page.locator('.logo span')).not.toBeVisible()

    // 再次点击展开
    await page.click('.hamburger')

    // 验证logo文字显示
    await expect(page.locator('.logo span')).toBeVisible()
  })

  test('多级菜单导航', async ({ page }) => {
    // 展开市场数据菜单
    await page.click('.el-sub-menu:has-text("市场数据")')

    // 点击资金流向
    await page.click('.el-menu-item:has-text("资金流向")')
    await page.waitForURL('**/market-data/fund-flow')
    await expect(page.url()).toContain('/market-data/fund-flow')

    // 验证页面标题或内容
    await expect(page.locator('h1, .page-title')).toBeVisible()
  })

  test('功能演示菜单', async ({ page }) => {
    // 展开功能演示菜单
    await page.click('.el-sub-menu:has-text("功能演示")')

    // 验证所有演示子菜单
    const demoMenus = [
      'OpenStock',
      'PyProfiling',
      'Freqtrade',
      'Stock-Analysis',
      'pytdx',
      'Phase 4 Dashboard',
      'Wencai'
    ]

    for (const menu of demoMenus) {
      await expect(page.locator(`.el-menu-item:has-text("${menu}")`)).toBeVisible()
    }

    // 测试点击Wencai
    await page.click('.el-menu-item:has-text("Wencai")')
    await page.waitForURL('**/demo/wencai')
    await expect(page.url()).toContain('/demo/wencai')
  })

  test('菜单激活状态', async ({ page }) => {
    // 导航到仪表盘
    await page.goto(`${BASE_URL}/dashboard`)
    await page.waitForLoadState('networkidle')

    // 验证仪表盘菜单是激活状态
    const dashboardMenu = page.locator('.el-menu-item[index="/dashboard"]')
    await expect(dashboardMenu).toHaveClass(/is-active/)

    // 导航到股票管理
    await page.goto(`${BASE_URL}/stocks`)
    await page.waitForLoadState('networkidle')

    // 验证股票管理菜单是激活状态
    const stocksMenu = page.locator('.el-menu-item[index="/stocks"]')
    await expect(stocksMenu).toHaveClass(/is-active/)
  })

  test('用户下拉菜单', async ({ page }) => {
    // 点击用户下拉菜单
    await page.click('.user-info')

    // 验证下拉菜单项
    await expect(page.locator('.el-dropdown-menu:has-text("个人信息")')).toBeVisible()
    await expect(page.locator('.el-dropdown-menu:has-text("退出登录")')).toBeVisible()
  })

  test('角色切换器（开发环境）', async ({ page }) => {
    // 检查是否有角色切换器（仅在开发环境显示）
    const roleSwitcher = page.locator('.role-switcher')
    const isDev = await page.evaluate(() => process.env.NODE_ENV === 'development')

    if (isDev) {
      await expect(roleSwitcher).toBeVisible()

      // 测试角色切换
      await roleSwitcher.locator('.el-select').click()
      await expect(page.locator('.el-select-dropdown')).toBeVisible()

      // 选择admin角色
      await page.click('.el-select-dropdown [value="admin"]')

      // 验证系统管理菜单出现
      await expect(page.locator('.el-sub-menu:has-text("系统管理")')).toBeVisible()
    }
  })
})

test.describe('菜单权限控制测试', () => {
  test('禁用菜单项处理', async ({ page }) => {
    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 展开技术分析菜单
    await page.click('.el-sub-menu:has-text("技术分析")')

    // 验证K线图是禁用状态
    const klineMenu = page.locator('.el-menu-item:has-text("K线图")')
    await expect(klineMenu).toHaveClass(/is-disabled/)

    // 尝试点击禁用项
    await klineMenu.click()

    // 验证显示提示信息
    const message = page.locator('.el-message')
    if (await message.count() > 0) {
      await expect(message).toContainText('暂未开放')
    }
  })
})

test.describe('菜单响应式测试', () => {
  test('小屏幕适配', async ({ page }) => {
    // 设置小屏幕尺寸
    await page.setViewportSize({ width: 768, height: 1024 })

    await page.goto(BASE_URL)
    await page.waitForLoadState('networkidle')

    // 验证侧边栏自动折叠
    const sidebar = page.locator('.el-aside')
    const width = await sidebar.evaluate(el => getComputedStyle(el).width)
    expect(parseInt(width)).toBeLessThanOrEqual(64)

    // 验证只显示图标
    await expect(page.locator('.logo span')).not.toBeVisible()
  })
})