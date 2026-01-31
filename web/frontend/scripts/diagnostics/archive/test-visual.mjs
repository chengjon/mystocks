/**
 * 简单的浏览器测试脚本
 * 使用 Puppeteer 访问前端并截图
 */

import puppeteer from 'puppeteer';

async function testFrontend() {
  console.log('🚀 启动浏览器测试...');

  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  // 设置视口大小
  await page.setViewport({ width: 1920, height: 1080 });

  // 监听控制台消息
  page.on('console', msg => {
    console.log(`浏览器控制台 [${msg.type()}]:`, msg.text());
  });

  // 监听页面错误
  page.on('pageerror', error => {
    console.error('❌ 页面错误:', error.message);
  });

  try {
    console.log('📍 访问 http://localhost:3001');
    await page.goto('http://localhost:3001', {
      waitUntil: 'networkidle2',
      timeout: 30000
    });

    console.log('⏳ 等待页面加载...');
    await page.waitForTimeout(5000);

    // 获取页面标题
    const title = await page.title();
    console.log('📄 页面标题:', title);

    // 检查 #app 元素
    const appExists = await page.$('#app');
    console.log('✅ #app 元素存在:', !!appExists);

    // 检查是否有内容
    const appContent = await page.$eval('#app', el => el.innerHTML);
    console.log('📦 #app 内容长度:', appContent.length);
    console.log('📦 #app 前500字符:', appContent.substring(0, 500));

    // 截图1: 完整页面
    const screenshot1 = '/opt/claude/mystocks_spec/web/frontend/test-screenshot-full.png';
    await page.screenshot({
      path: screenshot1,
      fullPage: true
    });
    console.log('📸 截图已保存:', screenshot1);

    // 截图2: 仅视口
    const screenshot2 = '/opt/claude/mystocks_spec/web/frontend/test-screenshot-viewport.png';
    await page.screenshot({
      path: screenshot2,
      fullPage: false
    });
    console.log('📸 视口截图已保存:', screenshot2);

    // 检查是否有错误信息显示在页面上
    const bodyText = await page.evaluate(() => document.body.textContent);
    if (bodyText.includes('Error') || bodyText.includes('error')) {
      console.warn('⚠️ 页面包含错误文本');
      console.log('页面文本:', bodyText.substring(0, 1000));
    }

  } catch (error) {
    console.error('❌ 测试失败:', error);
  } finally {
    await browser.close();
    console.log('✅ 测试完成');
  }
}

testFrontend().catch(console.error);
