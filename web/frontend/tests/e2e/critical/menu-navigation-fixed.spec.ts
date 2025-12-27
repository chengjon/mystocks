/**
 * 菜单导航测试 - 修复版
 * 使用ApiMockManager解决路由处理器优先级问题
 */

import { test, expect } from '@playwright/test'
import { setupApiMocks, ApiMockManager } from '@/tests/utils/api-mock-manager'

test.describe('Critical Menu Navigation - Fixed', { tag: '@critical' }, () => {
  test.beforeEach(async ({ page }) => {
    // 设置完全Mock模式，避免真实API依赖
    const manager = new ApiMockManager(page)
    manager.setMockMode('all')

    // 注册必要的API Mock
    manager.registerMocks([
      {
        method: 'GET',
        url: '/api/user/info',
        status: 200,
        response: {
          id: 1,
          username: 'testuser',
          roles: ['user']
        }
      },
      {
        method: 'GET',
        url: '/api/system/database/health',
        status: 200,
        response: {
          status: 'healthy',
          connection_count: 5
        }
      }
    ])

    // 应用所有Mock
    await manager.applyMocks()

    // 导航到首页
    await page.goto('/')
    await page.waitForLoadState('networkidle')
  })

  test('should navigate to dashboard without errors', async ({ page }) => {
    // 点击仪表盘菜单
    await page.click('[data-testid="menu-dashboard"]')
    await page.waitForURL('**/dashboard')

    // 验证页面加载成功
    await expect(page.locator('h1')).toContainText('仪表盘')

    // 检查控制台没有错误
    const errors = await page.evaluate(() => {
      return console.error.mock.calls.map(call => call[0])
    })
    expect(errors.filter(e => e.toString().includes('Error'))).toHaveLength(0)
  })

  test('should navigate to market data and load correctly', async ({ page }) => {
    // Mock市场数据API
    const manager = new ApiMockManager(page)
    manager.registerMock({
      method: 'GET',
      url: '/api/market/overview',
      status: 200,
      response: {
        market_cap: 1000000,
        volume: 500000,
        change: '+2.5%'
      }
    })
    await manager.applyMocks()

    // 点击市场数据菜单
    await page.click('[data-testid="menu-market"]')
    await page.waitForURL('**/market')

    // 验证数据加载
    await expect(page.locator('[data-testid="market-overview"]')).toBeVisible()
  })

  test('should handle missing API gracefully', async ({ page }) => {
    // 不Mock /api/data-quality/health，测试默认处理
    await page.goto('/system/database-monitor')

    // 应该显示404错误提示，而不是挂起
    await expect(page.locator('.error-message')).toContainText('API endpoint not mocked')
  })
})

// 全局测试设置
test.beforeAll(async () => {
  console.log('🚀 Starting Critical Menu Navigation Tests')
  console.log('✅ Using API Mock Manager to avoid backend dependency')
})

test.afterAll(async () => {
  console.log('✅ All Critical Menu Navigation Tests Completed')
})
