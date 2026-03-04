import { chromium } from 'playwright';
import fs from 'fs';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const BACKEND_PORT = process.env.BACKEND_PORT || '8020';
const BASE_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;
const PAGE_URL = '/market/realtime';
const OUTPUT_DIR = '/tmp/web-test-results';

async function debugRealtimePage() {
  console.log('\n🔍 开始调试实时监控页面 SSE 连接问题...\n');
  console.log(`📅 时间: ${new Date().toISOString()}`);
  console.log(`🌐 URL: ${BASE_URL}${PAGE_URL}\n`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 收集所有网络请求
  const networkRequests = [];
  page.on('request', request => {
    networkRequests.push({
      url: request.url(),
      method: request.method(),
      type: request.resourceType(),
      timestamp: new Date().toISOString()
    });
  });

  // 收集所有响应
  const networkResponses = [];
  page.on('response', response => {
    networkResponses.push({
      url: response.url(),
      status: response.status(),
      statusText: response.statusText(),
      timestamp: new Date().toISOString()
    });
  });

  // 收集控制台消息（详细）
  const consoleMessages = [];
  page.on('console', msg => {
    consoleMessages.push({
      type: msg.type(),
      text: msg.text(),
      location: msg.location()
    });
  });

  // 收集所有错误
  const pageErrors = [];
  page.on('pageerror', error => {
    pageErrors.push({
      message: error.message,
      stack: error.stack
    });
  });

  try {
    console.log('⏳ 步骤1: 开始加载页面...');
    const startTime = Date.now();

    // 尝试不同的加载策略
    await page.goto(BASE_URL + PAGE_URL, {
      waitUntil: 'domcontentloaded', // 先等待DOM加载完成
      timeout: 30000 // 增加超时到30秒
    });

    const loadTime = Date.now() - startTime;
    console.log(`✅ 页面DOM加载完成 (${loadTime}ms)`);

    // 等待网络空闲（最多15秒）
    console.log('⏳ 步骤2: 等待网络空闲...');
    try {
      await page.waitForLoadState('networkidle', { timeout: 15000 });
      console.log('✅ 网络已空闲');
    } catch (e) {
      console.log(`⚠️  网络未完全空闲: ${e.message.substring(0, 100)}`);
    }

    // 额外等待SSE连接
    console.log('⏳ 步骤3: 等待SSE连接建立（5秒）...');
    await page.waitForTimeout(5000);

    console.log('⏳ 步骤4: 分析收集的数据...\n');

    // 分析网络请求
    const sseRequests = networkRequests.filter(req =>
      req.url.includes('/api/v1/sse/') || req.url.includes(`:${BACKEND_PORT}`)
    );

    const failedRequests = networkResponses.filter(res =>
      res.status >= 400
    );

    const sseResponses = networkResponses.filter(res =>
      res.url.includes('/api/v1/sse/')
    );

    console.log('=' .repeat(80));
    console.log('📊 网络请求分析');
    console.log('=' .repeat(80));

    console.log(`\n总请求数: ${networkRequests.length}`);
    console.log(`SSE相关请求: ${sseRequests.length}`);
    console.log(`失败响应: ${failedRequests.length}`);

    if (sseRequests.length > 0) {
      console.log(`\n🔌 SSE 请求详情:`);
      sseRequests.forEach((req, index) => {
        console.log(`  [${index + 1}] ${req.method} ${req.url}`);
        console.log(`      时间: ${req.timestamp}`);
      });
    }

    if (failedRequests.length > 0) {
      console.log(`\n❌ 失败的请求:`);
      failedRequests.forEach((req, index) => {
        console.log(`  [${index + 1}] ${req.status} ${req.statusText}`);
        console.log(`      URL: ${req.url}`);
        console.log(`      时间: ${req.timestamp}`);
      });
    }

    if (sseResponses.length > 0) {
      console.log(`\n📡 SSE 响应分析:`);
      sseResponses.forEach((res, index) => {
        console.log(`  [${index + 1}] ${res.status} ${res.statusText}`);
        console.log(`      URL: ${res.url}`);
        console.log(`      时间: ${res.timestamp}`);
      });
    }

    // 分析控制台消息
    console.log(`\n${'='.repeat(80)}`);
    console.log('🖥️  控制台消息分析');
    console.log('=' .repeat(80));

    const errors = consoleMessages.filter(msg => msg.type === 'error');
    const warnings = consoleMessages.filter(msg => msg.type === 'warning');
    const sseMessages = consoleMessages.filter(msg =>
      msg.text.includes('SSE') || msg.text.includes('sse')
    );

    console.log(`\n总消息数: ${consoleMessages.length}`);
    console.log(`错误: ${errors.length}`);
    console.log(`警告: ${warnings.length}`);
    console.log(`SSE相关: ${sseMessages.length}`);

    if (errors.length > 0) {
      console.log(`\n🔴 错误详情 (前10个):`);
      errors.slice(0, 10).forEach((err, index) => {
        console.log(`\n  [${index + 1}] ${err.text}`);
        if (err.location && !err.location.url.includes('node_modules')) {
          console.log(`      位置: ${err.location.url}:${err.location.lineNumber}`);
        }
      });
    }

    if (sseMessages.length > 0) {
      console.log(`\n📡 SSE相关消息:`);
      sseMessages.forEach((msg, index) => {
        console.log(`  [${index + 1}] [${msg.type.toUpperCase()}] ${msg.text}`);
      });
    }

    // 分析页面错误
    if (pageErrors.length > 0) {
      console.log(`\n${'='.repeat(80)}`);
      console.log('💥 页面错误分析');
      console.log('=' .repeat(80));
      console.log(`\n页面错误数: ${pageErrors.length}`);
      pageErrors.forEach((err, index) => {
        console.log(`\n  [${index + 1}] ${err.message}`);
        if (err.stack) {
          const stackLines = err.stack.split('\n').slice(0, 3);
          stackLines.forEach(line => console.log(`      ${line}`));
        }
      });
    }

    // 截图保存
    console.log(`\n${'='.repeat(80)}`);
    console.log('📸 保存页面截图...');
    const screenshotPath = `${OUTPUT_DIR}/realtime-monitor-debug.png`;
    await page.screenshot({
      path: screenshotPath,
      fullPage: true
    });
    console.log(`✅ 截图已保存: ${screenshotPath}`);

    // 检查页面状态
    console.log(`\n${'='.repeat(80)}`);
    console.log('🔍 页面元素检查');
    console.log('=' .repeat(80));

    const errorElements = await page.locator('.error, .error-state, [class*="error"]').count();
    const sseElements = await page.locator('[class*="sse"], [id*="sse"]').count();
    const loadingElements = await page.locator('.loading, [class*="loading"]').count();

    console.log(`\n错误元素: ${errorElements}`);
    console.log(`SSE相关元素: ${sseElements}`);
    console.log(`加载中元素: ${loadingElements}`);

    // 尝试获取页面标题
    const title = await page.title();
    console.log(`\n页面标题: ${title}`);

    // 检查body元素
    const bodyVisible = await page.locator('body').isVisible();
    console.log(`Body可见: ${bodyVisible}`);

  } catch (error) {
    console.error(`\n❌ 测试失败: ${error.message}`);

    // 即使失败也保存截图
    try {
      const errorScreenshotPath = `${OUTPUT_DIR}/realtime-monitor-error.png`;
      await page.screenshot({
        path: errorScreenshotPath,
        fullPage: true
      });
      console.log(`📸 错误截图已保存: ${errorScreenshotPath}`);
    } catch (screenshotError) {
      // 忽略截图错误
    }
  }

  await browser.close();

  // 保存详细日志
  const debugLog = {
    timestamp: new Date().toISOString(),
    url: BASE_URL + PAGE_URL,
    networkRequests: networkRequests,
    networkResponses: networkResponses,
    consoleMessages: consoleMessages,
    pageErrors: pageErrors
  };

  const logPath = `${OUTPUT_DIR}/realtime-monitor-debug.json`;
  fs.writeFileSync(logPath, JSON.stringify(debugLog, null, 2));
  console.log(`\n📄 详细调试日志已保存: ${logPath}`);

  console.log('\n✅ 调试完成!\n');
}

debugRealtimePage().catch(error => {
  console.error('调试失败:', error);
  process.exit(1);
});
