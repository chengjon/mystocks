import { test, expect } from '@playwright/test';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;

test.use({
  baseURL: FRONTEND_URL
});

test.describe('MyStocks - Existing Dashboard Style Check', () => {
  test.setTimeout(15000);

  test('Check if fintech styles are applied to existing Dashboard page', async ({ page }) => {
    console.log('🧪 Checking existing Dashboard page for fintech styles...');

    // 访问现有的仪表盘页面
    await page.goto('/dashboard');
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(3000);

    // 检查页面是否有内容
    const bodyText = await page.locator('body').textContent();
    console.log(`📄 Dashboard page content length: ${bodyText?.length || 0}`);

    // 截图看看实际渲染了什么
    await page.screenshot({
      path: 'test-results/screenshots/dashboard-actual-content.png',
      fullPage: true
    });

    // 检查页面标题
    const title = await page.title();
    console.log(`📋 Page title: "${title}"`);

    // 检查是否有Vue渲染的内容（不是空的div#app）
    const appDiv = page.locator('#app');
    const appContent = await appDiv.textContent();
    console.log(`📱 App div content length: ${appContent?.length || 0}`);

    // 检查是否有任何可见的元素
    const visibleElements = page.locator(':visible');
    const visibleCount = await visibleElements.count();
    console.log(`👁️ Visible elements: ${visibleCount}`);

    // 查找可能的Vue组件
    const vueComponents = page.locator('[class*="vue"], [class*="component"]');
    const vueCount = await vueComponents.count();
    console.log(`🔧 Vue components found: ${vueCount}`);

    // 检查是否有Element Plus组件
    const elComponents = page.locator('[class*="el-"]');
    const elCount = await elComponents.count();
    console.log(`🎨 Element Plus components: ${elCount}`);

    // 检查CSS变量是否仍然有效
    const cssVars = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement);
      return {
        bgPrimary: styles.getPropertyValue('--fintech-bg-primary'),
        textPrimary: styles.getPropertyValue('--fintech-text-primary'),
        accentPrimary: styles.getPropertyValue('--fintech-accent-primary')
      };
    });

    console.log('🎨 CSS Variables:');
    console.log(`  --fintech-bg-primary: ${cssVars.bgPrimary}`);
    console.log(`  --fintech-text-primary: ${cssVars.textPrimary}`);
    console.log(`  --fintech-accent-primary: ${cssVars.accentPrimary}`);

    console.log('✅ Dashboard style check completed');
  });

  test('Check if any fintech styles are visible anywhere', async ({ page }) => {
    console.log('🧪 Searching for any fintech styles in the entire app...');

    // 检查整个应用的HTML
    const htmlContent = await page.evaluate(() => document.documentElement.outerHTML);
    const hasFintechClasses = htmlContent.includes('fintech-');
    const hasBloombergClasses = htmlContent.includes('bloomberg');

    console.log(`💼 Has fintech classes in HTML: ${hasFintechClasses}`);
    console.log(`🏢 Has bloomberg classes in HTML: ${hasBloombergClasses}`);

    // 查找所有包含fintech的元素
    const allFintechElements = await page.locator('[class*="fintech"]').all();
    console.log(`🔍 Found ${allFintechElements.length} elements with fintech classes`);

    // 查找所有样式类
    const allClasses = await page.evaluate(() => {
      const elements = document.querySelectorAll('*');
      const classes = new Set();
      for (const el of elements) {
        if (el.className) {
          el.className.split(' ').forEach(cls => classes.add(cls));
        }
      }
      return Array.from(classes).filter(cls => cls.includes('fintech') || cls.includes('bloomberg'));
    });

    console.log(`🎨 Found fintech/bloomberg classes: ${allClasses.join(', ')}`);

    console.log('✅ Global fintech style search completed');
  });
});
