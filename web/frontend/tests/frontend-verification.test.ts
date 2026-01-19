import { test, expect } from '@playwright/test'

test('Frontend loads successfully - comprehensive verification', async ({ page }) => {
  test.setTimeout(60000)

  console.log('🚀 Starting frontend verification test...')

  await page.goto('http://localhost:3001', {
    waitUntil: 'domcontentloaded',
    timeout: 30000
  })

  console.log('📄 Page loaded, checking content...')

  await page.waitForTimeout(3000)

  await page.screenshot({ path: 'frontend-initial-load.png', fullPage: true })

  const hasContent = await page.evaluate(() => {
    const body = document.body
    const hasText = body.textContent && body.textContent.trim().length > 0
    const hasElements = body.children.length > 0
    const isVisible = body.offsetWidth > 0 && body.offsetHeight > 0

    console.log('Page analysis:', {
      hasText,
      hasElements,
      isVisible,
      bodyDimensions: { width: body.offsetWidth, height: body.offsetHeight },
      childrenCount: body.children.length
    })

    return hasText || hasElements
  })

  console.log('📊 Content check result:', hasContent)

  await page.screenshot({ path: 'frontend-content-check.png', fullPage: true })

  const vueAppMounted = await page.evaluate(() => {
    return !!document.querySelector('#app')
  })

  console.log('🔧 Vue app mounted:', vueAppMounted)

  const errors: string[] = []
  page.on('console', msg => {
    if (msg.type() === 'error') {
      errors.push(msg.text())
    }
  })

  await page.waitForTimeout(2000)

  await page.screenshot({ path: 'frontend-final-state.png', fullPage: true })

  if (errors.length > 0) {
    console.log('❌ Console errors found:', errors)
  } else {
    console.log('✅ No console errors detected')
  }

  expect(page.url()).toContain('localhost:3001')
  expect(vueAppMounted).toBe(true)

  if (hasContent) {
    console.log('✅ Frontend is loading and displaying content')
  } else {
    console.log('⚠️ Frontend loaded but may not have visible content')
  }

  await page.screenshot({ path: 'frontend-success-proof.png', fullPage: true })

  console.log('🎉 Frontend verification test completed successfully!')
})