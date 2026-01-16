/**
 * Playwright 测试脚本 - 访问前端并截图
 */

import { chromium } from 'playwright';

async function testFrontend() {
  console.log('🚀 启动 Playwright 测试...');

  const browser = await chromium.launch({
    headless: true
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 监听控制台
  page.on('console', msg => {
    console.log(`🖥️  [${msg.type()}] ${msg.text()}`);
  });

  // 监听页面错误
  page.on('pageerror', error => {
    console.error('❌ 页面错误:', error.message);
  });

  try {
    console.log('📍 访问 http://localhost:3001');
    await page.goto('http://localhost:3001', {
      waitUntil: 'networkidle',
      timeout: 30000
    });

    console.log('⏳ 等待页面加载完成...');
    await page.waitForTimeout(5000);

    // 获取页面信息
    const title = await page.title();
    console.log('📄 页面标题:', title);

    // 检查 #app
    const appExists = await page.locator('#app').count();
    console.log('✅ #app 元素存在:', appExists > 0);

    // 获取 #app 的 HTML
    const appHTML = await page.locator('#app').innerHTML();
    console.log('📦 #app HTML 长度:', appHTML.length);
    console.log('📦 #app 内容预览:', appHTML.substring(0, 300));

    // 检查加载屏
    const loadingExists = await page.locator('.app-loading-screen').count();
    console.log('⏳ 加载屏存在:', loadingExists > 0);

    // 截图1: 完整页面
    const screenshot1 = '/opt/claude/mystocks_spec/web/frontend/screenshots/test-fullpage.png';
    await page.screenshot({
      path: screenshot1,
      fullPage: true
    });
    console.log('📸 完整页面截图:', screenshot1);

    // 截图2: 视口
    const screenshot2 = '/opt/claude/mystocks_spec/web/frontend/screenshots/test-viewport.png';
    await page.screenshot({
      path: screenshot2,
      fullPage: false
    });
    console.log('📸 视口截图:', screenshot2);

    // 保存页面 HTML
    const htmlContent = await page.content();
    require('fs').writeFileSync(
      '/opt/claude/mystocks_spec/web/frontend/screenshots/test-page.html',
      htmlContent
    );
    console.log('💾 页面 HTML 已保存');

  } catch (error) {
    console.error('❌ 测试失败:', error);
  } finally {
    await browser.close();
    console.log('✅ 测试完成');
  }
}

testFrontend().catch(console.error);
