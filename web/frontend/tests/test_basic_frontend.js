import { test, expect } from '@playwright/test'

test('MyStocks frontend loads successfully', async ({ page }) => {
  await page.goto('http://localhost:3020')
  await page.waitForLoadState('networkidle')

  const title = await page.title()
  console.log('Page title:', title)

  expect(page.url()).toContain('localhost:3020')

  const bodyText = await page.locator('body').textContent()
  expect(bodyText?.length).toBeGreaterThan(0)
})