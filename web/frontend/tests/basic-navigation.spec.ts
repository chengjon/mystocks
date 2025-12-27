/**
 * 基础导航测试
 * 验证前端基本功能
 */

import { test, expect } from '@playwright/test'

test.describe('基础导航测试', () => {
  test.beforeEach(async ({ page }) => {
    // 导航到首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('首页正常加载', async ({ page }) => {
    // 验证页面标题
    await expect(page).toHaveTitle(/MyStocks/)

    // 验证主要元素存在
    await expect(page.locator('.navbar')).toBeVisible()
    await expect(page.locator('.sidebar')).toBeVisible()
    await expect(page.locator('.main-content')).toBeVisible()
  })

  test('能够导航到仪表盘', async ({ page }) => {
    // 点击仪表盘菜单项 (使用文本选择器)
    await page.click('text=仪表盘')

    // 验证URL变化
    await expect(page.url()).toContain('/dashboard')

    // 验证页面内容
    await expect(page.locator('h1')).toContainText('仪表盘')
  })

  test('能够切换侧边栏', async ({ page }) => {
    // 获取侧边栏
    const sidebar = page.locator('.sidebar')

    // 点击折叠按钮
    await page.click('.hamburger')

    // 等待动画完成
    await page.waitForTimeout(500)

    // 验证侧边栏样式改变（检查宽度）
    const collapsedWidth = await sidebar.evaluate(el => getComputedStyle(el).width)
    expect(parseInt(collapsedWidth)).toBeLessThan(100) // 折叠后应该很窄
  })

  test('显示用户信息', async ({ page }) => {
    // 验证用户下拉菜单显示
    await expect(page.locator('.user-info')).toBeVisible()
    await expect(page.locator('.username')).toContainText('Demo User')
  })
})
