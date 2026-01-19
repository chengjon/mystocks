import { test, expect } from '@playwright/test'

/**
 * ESM Dayjs兼容性专项验证测试
 * 验证dayjs ESM导入是否正常工作
 */

test.describe('ESM Dayjs兼容性验证', () => {
  test.setTimeout(20000)

  test('dayjs ESM导入验证', async ({ page }) => {
    const errors: string[] = []

    // 监听JavaScript错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text())
      }
    })

    page.on('pageerror', error => {
      errors.push(`PageError: ${error.message}`)
    })

    // 访问首页触发Vue应用加载
    await page.goto('http://localhost:3001', {
      waitUntil: 'domcontentloaded',
      timeout: 10000
    })

    // 等待Vue应用初始化
    await page.waitForTimeout(3000)

    // 检查是否有ESM相关的错误
    const esmErrors = errors.filter(error =>
      error.includes('does not provide an export named \'default\'') ||
      error.includes('dayjs') ||
      error.includes('ESM')
    )

    // 验证无ESM导入错误
    expect(esmErrors).toHaveLength(0)

    // 验证页面基本功能
    const title = await page.title()
    expect(title).toContain('MyStocks')

    console.log('✅ dayjs ESM导入验证通过')
  })
})