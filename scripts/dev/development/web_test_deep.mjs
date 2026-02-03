import { chromium } from 'playwright';
import fs from 'fs';

const BASE_URL = 'http://localhost:3020';
const OUTPUT_DIR = '/tmp/web-test-results';

// 深度分析的问题页面
const PROBLEM_PAGES = [
  { url: '/stocks', name: '股票管理', issues: ['10个错误元素'] },
  { url: '/market/tdx-market', name: 'TDX行情', issues: ['2个错误元素'] },
  { url: '/market/realtime', name: '实时监控', issues: ['2个错误元素', '8个控制台错误'] },
  { url: '/market-data/fund-flow', name: '资金流向', issues: ['4个错误元素'] },
  { url: '/market-data/etf', name: 'ETF行情', issues: ['2个错误元素'] },
];

async function deepAnalysis() {
  console.log('\n🔍 开始深度分析问题页面...\n');

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });

  for (const pageInfo of PROBLEM_PAGES) {
    console.log(`\n📄 分析: ${pageInfo.name}`);
    console.log(`   URL: ${BASE_URL}${pageInfo.url}`);

    const page = await context.newPage();

    // 收集控制台消息
    const consoleMessages = [];
    page.on('console', msg => {
      consoleMessages.push({
        type: msg.type(),
        text: msg.text(),
        location: msg.location()
      });
    });

    // 收集网络请求
    const networkRequests = [];
    page.on('request', request => {
      networkRequests.push({
        url: request.url(),
        method: request.method(),
        resourceType: request.resourceType()
      });
    });

    // 收集网络响应
    const failedRequests = [];
    page.on('response', response => {
      if (response.status() >= 400) {
        failedRequests.push({
          url: response.url(),
          status: response.status(),
          statusText: response.statusText()
        });
      }
    });

    try {
      await page.goto(BASE_URL + pageInfo.url, {
        waitUntil: 'networkidle',
        timeout: 15000
      });

      // 等待一会儿收集更多信息
      await page.waitForTimeout(2000);

      // 分析错误元素
      const errorElements = await page.locator('.error, .alert-error, [class*="error"], [class*="warning"]').all();

      const errorDetails = [];
      for (const element of errorElements) {
        try {
          const text = await element.textContent();
          const className = await element.getAttribute('class');
          const isVisible = await element.isVisible();

          errorDetails.push({
            text: text?.substring(0, 100),
            className: className?.substring(0, 100),
            isVisible: isVisible
          });
        } catch (e) {
          // 忽略
        }
      }

      // 输出分析结果
      console.log(`\n   ✅ 页面加载成功`);

      // 错误元素详情
      if (errorDetails.length > 0) {
        console.log(`\n   ⚠️  发现 ${errorDetails.length} 个错误/警告元素:`);
        errorDetails.forEach((err, index) => {
          console.log(`      [${index + 1}] ${err.isVisible ? '可见' : '隐藏'}`);
          if (err.className) {
            console.log(`          class: ${err.className}`);
          }
          if (err.text) {
            console.log(`          text: ${err.text}`);
          }
        });
      }

      // 控制台错误
      const errors = consoleMessages.filter(msg => msg.type === 'error');
      const warnings = consoleMessages.filter(msg => msg.type === 'warning');

      if (errors.length > 0) {
        console.log(`\n   🔴 ${errors.length} 个控制台错误:`);
        errors.forEach((err, index) => {
          console.log(`      [${index + 1}] ${err.text}`);
          if (err.location) {
            console.log(`          位置: ${err.location.url}:${err.location.lineNumber}`);
          }
        });
      }

      if (warnings.length > 0) {
        console.log(`\n   🟡 ${warnings.length} 个控制台警告:`);
        warnings.slice(0, 5).forEach((warn, index) => {
          console.log(`      [${index + 1}] ${warn.text}`);
        });
        if (warnings.length > 5) {
          console.log(`      ... 还有 ${warnings.length - 5} 个警告`);
        }
      }

      // 失败的请求
      if (failedRequests.length > 0) {
        console.log(`\n   ❌ ${failedRequests.length} 个失败的网络请求:`);
        failedRequests.forEach((req, index) => {
          console.log(`      [${index + 1}] ${req.status} ${req.statusText}`);
          console.log(`          URL: ${req.url}`);
        });
      }

      // API请求统计
      const apiRequests = networkRequests.filter(req =>
        req.url.includes('/api/') ||
        req.url.includes(':8000')
      );

      if (apiRequests.length > 0) {
        console.log(`\n   📡 API调用统计: ${apiRequests.length} 个请求`);
        const apiCalls = {};
        apiRequests.forEach(req => {
          const url = new URL(req.url);
          const path = url.pathname;
          if (!apiCalls[path]) {
            apiCalls[path] = 0;
          }
          apiCalls[path]++;
        });

        Object.entries(apiCalls).forEach(([path, count]) => {
          console.log(`      - ${path}: ${count} 次`);
        });
      }

    } catch (error) {
      console.log(`\n   ❌ 分析失败: ${error.message}`);
    }

    await page.close();
  }

  await browser.close();

  console.log('\n✅ 深度分析完成!\n');
}

// 运行深度分析
deepAnalysis().catch(error => {
  console.error('深度分析失败:', error);
  process.exit(1);
});
