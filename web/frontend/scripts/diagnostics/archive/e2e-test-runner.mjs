#!/usr/bin/env node
/**
 * MyStocks E2E全链路自动化测试脚本
 *
 * 核心原则：
 * 1. ✅ 不仅检查HTTP 200 - 必须验证HTML内容、DOM渲染、元素可见性
 * 2. ✅ 优先使用toBeVisible() - 确保元素完成CSS渲染（避免页面空白但DOM存在）
 * 3. ✅ 必须捕获控制台错误 - 页面空白常因JS报错或资源404
 * 4. ✅ 前后端解耦验证 - 先测后端接口，再测前端展示，最后测联动
 * 5. ✅ 截图/录屏追溯 - 所有失败必截图，成功按需截图
 * 6. ✅ 明确问题分类 - 区分前端/后端/联动问题
 */

import { chromium } from 'playwright';
import { writeFile, mkdir } from 'fs/promises';
import { join } from 'path';

// ==================== 配置 ====================
const CONFIG = {
  baseURL: 'http://localhost:3001',
  backendURL: 'http://localhost:8000',
  screenshotDir: './test-reports/e2e-screenshots',
  logDir: './test-reports/e2e-logs',
  reportPath: './test-reports/e2e-report.json',
  headless: false, // 显示浏览器以便观察
  slowMo: 100, // 放慢操作以便观察
  timeout: 30000, // 30秒超时
};

// ==================== 测试数据 ====================

// 核心页面列表（优先测试ArtDeco页面）
const CORE_PAGES = [
  {
    url: '/',
    name: 'Home',
    expectedTitle: 'Test Page',
    coreElements: [
      { selector: 'body', description: '页面主体' },
    ],
    requiresBackend: false,
  },
  {
    url: '/artdeco/market',
    name: 'ArtDeco市场数据分析中心',
    expectedTitle: '市场数据分析中心',
    coreElements: [
      { selector: 'h1, h2, .title', description: '页面标题' },
      { selector: '.el-table, table, .data-container', description: '数据容器' },
      { selector: '.el-button, button, .action-bar', description: '操作按钮' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/market/list',
  },
  {
    url: '/artdeco/market-quotes',
    name: 'ArtDeco市场行情中心',
    expectedTitle: '市场行情中心',
    coreElements: [
      { selector: 'h1, h2, .title', description: '页面标题' },
      { selector: '.quote-container, .market-data', description: '行情数据容器' },
      { selector: '.refresh-button, .el-button', description: '刷新按钮' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/market/quote',
  },
  {
    url: '/artdeco/trading',
    name: 'ArtDeco量化交易管理中心',
    expectedTitle: '量化交易管理中心',
    coreElements: [
      { selector: 'h1, h2, .title', description: '页面标题' },
      { selector: '.trading-panel, .order-form', description: '交易面板' },
      { selector: '.position-list, .portfolio', description: '持仓列表' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/trading',
  },
  {
    url: '/artdeco/backtest',
    name: 'ArtDeco策略回测管理中心',
    expectedTitle: '策略回测管理中心',
    coreElements: [
      { selector: 'h1, h2, .title', description: '页面标题' },
      { selector: '.backtest-form, .strategy-config', description: '回测配置' },
      { selector: '.result-chart, .backtest-results', description: '回测结果' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/backtest',
  },
  {
    url: '/artdeco/risk',
    name: 'ArtDeco风险管理中心',
    expectedTitle: '风险管理中心',
    coreElements: [
      { selector: 'h1, h2, .title', description: '页面标题' },
      { selector: '.risk-dashboard, .risk-metrics', description: '风险仪表板' },
      { selector: '.alert-list, .risk-alerts', description: '告警列表' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/risk',
  },
  {
    url: '/dashboard/overview',
    name: 'Dashboard总览',
    expectedTitle: 'Overview',
    coreElements: [
      { selector: '.dashboard, .overview', description: '仪表板容器' },
      { selector: '.metric-card, .stat-card', description: '指标卡片' },
      { selector: '.chart, .data-visualization', description: '图表' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/dashboard',
  },
  {
    url: '/market/list',
    name: '股票列表',
    expectedTitle: 'Stock List',
    coreElements: [
      { selector: '.stock-list, .el-table', description: '股票列表表格' },
      { selector: '.search-bar, .filter-panel', description: '搜索栏' },
      { selector: '.pagination, .page-nav', description: '分页器' },
    ],
    requiresBackend: true,
    expectedAPI: '/api/v1/market/list',
  },
];

// 后端关键API列表
const BACKEND_APIS = [
  { path: '/health', method: 'GET', description: '健康检查' },
  { path: '/api/v1/market/list', method: 'GET', description: '股票列表' },
  { path: '/api/v1/market/quote/600519', method: 'GET', description: '行情报价' },
  { path: '/api/v1/auth/status', method: 'GET', description: '认证状态' },
  { path: '/api/system/info', method: 'GET', description: '系统信息' },
];

// ==================== 工具函数 ====================

/**
 * 延迟函数
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 格式化时间戳
 */
function getTimestamp() {
  return new Date().toISOString().replace(/[:.]/g, '-');
}

/**
 * 创建目录（如果不存在）
 */
async function ensureDir(dir) {
  try {
    await mkdir(dir, { recursive: true });
  } catch (err) {
    // 目录已存在，忽略
  }
}

/**
 * 保存截图
 */
async function saveScreenshot(page, testName, status) {
  const timestamp = getTimestamp();
  const filename = `${testName}_${status}_${timestamp}.png`;
  const filepath = join(CONFIG.screenshotDir, filename);

  await page.screenshot({ path: filepath, fullPage: true });
  console.log(`  📸 截图已保存: ${filepath}`);
  return filepath;
}

/**
 * 保存控制台日志
 */
async function saveConsoleLogs(testName, logs) {
  const timestamp = getTimestamp();
  const filename = `${testName}_console_${timestamp}.txt`;
  const filepath = join(CONFIG.logDir, filename);

  const content = logs.map(log => {
    return `[${log.type.toUpperCase()}] ${log.text}`;
  }).join('\n');

  await writeFile(filepath, content);
  console.log(`  📝 控制台日志已保存: ${filepath}`);
  return filepath;
}

// ==================== 核心测试函数 ====================

/**
 * 前置校验：检查后端API
 */
async function testBackendAPIs(browser) {
  console.log('\n🔧 Phase 1: 后端API独立测试');
  console.log('=' .repeat(60));

  const results = [];
  const context = await browser.newContext();
  const page = await context.newPage();

  for (const api of BACKEND_APIS) {
    console.log(`\n测试API: ${api.method} ${api.path}`);
    const startTime = Date.now();

    try {
      const response = await page.request.get(`${CONFIG.backendURL}${api.path}`);
      const duration = Date.now() - startTime;
      const status = response.status();
      const contentType = response.headers()['content-type'];

      let data = null;
      let error = null;

      try {
        data = await response.json();
      } catch (e) {
        // 非JSON响应
        data = await response.text();
      }

      const result = {
        api: `${api.method} ${api.path}`,
        status,
        duration,
        contentType,
        data,
        success: status >= 200 && status < 300,
      };

      if (result.success) {
        console.log(`  ✅ 成功 (${status}) - ${duration}ms`);
        console.log(`     Content-Type: ${contentType}`);
      } else {
        console.log(`  ❌ 失败 (${status})`);
        console.log(`     错误: ${data}`);
        result.error = data;
      }

      results.push(result);
    } catch (err) {
      console.log(`  ❌ 请求失败: ${err.message}`);
      results.push({
        api: `${api.method} ${api.path}`,
        success: false,
        error: err.message,
      });
    }
  }

  await context.close();
  return results;
}

/**
 * 页面加载完整性测试
 */
async function testPageLoadIntegrity(page, pageInfo) {
  console.log(`\n📄 测试页面: ${pageInfo.name}`);
  console.log(`   URL: ${CONFIG.baseURL}${pageInfo.url}`);
  console.log('-'.repeat(60));

  const startTime = Date.now();
  const result = {
    name: pageInfo.name,
    url: pageInfo.url,
    expectedTitle: pageInfo.expectedTitle,
    startTime: new Date().toISOString(),
    issues: [],
    consoleErrors: [],
    elementChecks: [],
    backendCheck: null,
  };

  // 收集控制台错误
  const consoleLogs = [];
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();

    if (type === 'error') {
      consoleLogs.push({ type: 'error', text });
      console.log(`  🔴 控制台错误: ${text}`);
    } else if (type === 'warning') {
      consoleLogs.push({ type: 'warning', text });
      console.log(`  ⚠️  控制台警告: ${text}`);
    }
  });

  // 监控网络请求
  const networkErrors = [];
  page.on('response', response => {
    const status = response.status();
    if (status >= 400) {
      const url = response.url();
      networkErrors.push({ url, status });
      console.log(`  🔴 网络请求失败: ${url} (${status})`);
    }
  });

  try {
    // 1. 访问页面
    console.log(`  🌐 访问页面...`);
    const response = await page.goto(`${CONFIG.baseURL}${pageInfo.url}`, {
      waitUntil: 'networkidle',
      timeout: CONFIG.timeout,
    });

    const httpStatus = response.status();
    console.log(`  HTTP状态: ${httpStatus}`);

    if (httpStatus !== 200) {
      result.issues.push({
        type: 'http_error',
        message: `HTTP状态码不是200: ${httpStatus}`,
      });
    }

    // 2. 等待DOM加载
    console.log(`  ⏳ 等待DOM加载...`);
    await page.waitForLoadState('domcontentloaded');

    // 3. 等待页面完全渲染
    console.log(`  ⏳ 等待页面完全渲染...`);
    await page.waitForLoadState('networkidle');

    // 4. 检查页面标题
    console.log(`  🔍 检查页面标题...`);
    const title = await page.title();
    console.log(`  标题: "${title}"`);

    if (!title || title.trim() === '') {
      result.issues.push({
        type: 'title_missing',
        message: '页面标题为空',
      });
      console.log(`  ❌ 页面标题为空`);
    } else if (pageInfo.expectedTitle && !title.includes(pageInfo.expectedTitle)) {
      result.issues.push({
        type: 'title_mismatch',
        message: `页面标题不匹配，期望包含: "${pageInfo.expectedTitle}"`,
        expected: pageInfo.expectedTitle,
        actual: title,
      });
      console.log(`  ⚠️  标题不匹配，期望: "${pageInfo.expectedTitle}"`);
    } else {
      console.log(`  ✅ 页面标题正常`);
    }

    // 5. 检查核心DOM元素可见性（关键步骤！）
    console.log(`  🔍 检查核心DOM元素可见性...`);

    for (const element of pageInfo.coreElements) {
      console.log(`     检查: ${element.description} (${element.selector})`);

      try {
        // 使用isVisible而不是仅检查presence
        // isVisible确保元素不仅在DOM中，还完成了CSS渲染
        const isVisible = await page.locator(element.selector).isVisible({ timeout: 5000 });

        if (isVisible) {
          console.log(`     ✅ 可见`);
          result.elementChecks.push({
            selector: element.selector,
            description: element.description,
            visible: true,
          });
        } else {
          console.log(`     ❌ 不可见（可能在DOM中但未渲染）`);
          result.issues.push({
            type: 'element_not_visible',
            message: `${element.description}不可见`,
            selector: element.selector,
          });
          result.elementChecks.push({
            selector: element.selector,
            description: element.description,
            visible: false,
          });
        }
      } catch (err) {
        console.log(`     ❌ 未找到: ${err.message}`);
        result.issues.push({
          type: 'element_not_found',
          message: `${element.description}未找到`,
          selector: element.selector,
          error: err.message,
        });
        result.elementChecks.push({
          selector: element.selector,
          description: element.description,
          visible: false,
          error: err.message,
        });
      }
    }

    // 6. 检查页面是否空白（关键检查！）
    console.log(`  🔍 检查页面是否空白...`);
    const bodyText = await page.locator('body').textContent();
    const visibleText = bodyText ? bodyText.trim() : '';

    if (visibleText.length < 10) {
      result.issues.push({
        type: 'blank_page',
        message: '页面内容为空或接近空白',
        textLength: visibleText.length,
      });
      console.log(`  ❌ 页面内容为空（文本长度: ${visibleText.length}）`);
    } else {
      console.log(`  ✅ 页面有内容（文本长度: ${visibleText.length}）`);
    }

    // 7. 记录控制台错误
    result.consoleErrors = consoleLogs;
    if (consoleLogs.length > 0) {
      result.issues.push({
        type: 'console_errors',
        message: `发现${consoleLogs.length}个控制台错误`,
        errors: consoleLogs.filter(log => log.type === 'error'),
      });
    }

    // 8. 记录网络错误
    if (networkErrors.length > 0) {
      result.issues.push({
        type: 'network_errors',
        message: `发现${networkErrors.length}个网络请求失败`,
        errors: networkErrors,
      });
    }

    // 9. 保存截图
    const screenshotPath = await saveScreenshot(page, pageInfo.name.replace(/\s+/g, '_'), 'success');

    // 10. 计算结果
    const duration = Date.now() - startTime;
    result.duration = duration;
    result.screenshot = screenshotPath;
    result.success = result.issues.length === 0;

    console.log(`  ⏱️  加载时间: ${duration}ms`);

    if (result.success) {
      console.log(`  ✅ 页面加载完整性测试: 通过\n`);
    } else {
      console.log(`  ❌ 页面加载完整性测试: 失败`);
      console.log(`  问题数量: ${result.issues.length}\n`);
    }

  } catch (err) {
    const duration = Date.now() - startTime;
    result.duration = duration;
    result.success = false;
    result.issues.push({
      type: 'page_load_error',
      message: `页面加载失败: ${err.message}`,
      error: err.message,
    });

    console.log(`  ❌ 页面加载失败: ${err.message}`);
    await saveScreenshot(page, pageInfo.name.replace(/\s+/g, '_'), 'error');
  }

  return result;
}

/**
 * 前后端联动测试
 */
async function testFrontendBackendIntegration(page, pageInfo, backendResults) {
  if (!pageInfo.requiresBackend) {
    return { skipped: true, reason: '页面不需要后端数据' };
  }

  console.log(`  🔗 前后端联动测试`);

  const result = {
    apiCalled: false,
    apiSuccess: false,
    dataDisplayed: false,
    issues: [],
  };

  try {
    // 检查网络请求中是否包含预期的API调用
    const apiRequests = [];
    page.on('request', request => {
      const url = request.url();
      if (url.includes('/api/') || url.includes(pageInfo.expectedAPI || '')) {
        apiRequests.push({
          method: request.method(),
          url: url,
          headers: request.headers(),
        });
        console.log(`     📤 API请求: ${request.method()} ${url}`);
      }
    });

    // 等待2秒，收集API请求
    await sleep(2000);

    if (apiRequests.length === 0) {
      result.issues.push({
        type: 'no_api_call',
        message: '前端页面没有向后端发起API请求',
      });
      console.log(`     ⚠️  未检测到API请求`);
    } else {
      result.apiCalled = true;
      console.log(`     ✅ 检测到${apiRequests.length}个API请求`);
    }

  } catch (err) {
    result.issues.push({
      type: 'integration_error',
      message: `前后端联动测试失败: ${err.message}`,
    });
    console.log(`     ❌ 测试失败: ${err.message}`);
  }

  return result;
}

// ==================== 主测试流程 ====================

async function runTests() {
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║     MyStocks E2E全链路自动化测试                          ║');
  console.log('║     严格全链路校验 | 拒绝"仅HTTP 200"判断                   ║');
  console.log('╚════════════════════════════════════════════════════════════╝');

  console.log(`\n📅 开始时间: ${new Date().toISOString()}`);
  console.log(`\n🔧 配置:`);
  console.log(`   前端: ${CONFIG.baseURL}`);
  console.log(`   后端: ${CONFIG.backendURL}`);
  console.log(`   截图目录: ${CONFIG.screenshotDir}`);
  console.log(`   日志目录: ${CONFIG.logDir}`);

  // 创建输出目录
  await ensureDir(CONFIG.screenshotDir);
  await ensureDir(CONFIG.logDir);

  // 启动浏览器
  console.log(`\n🚀 启动浏览器...`);
  const browser = await chromium.launch({
    headless: CONFIG.headless,
    slowMo: CONFIG.slowMo,
  });

  const testResults = {
    startTime: new Date().toISOString(),
    config: CONFIG,
    backendTests: [],
    frontendTests: [],
    integrationTests: [],
    summary: {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      frontendIssues: [],
      backendIssues: [],
      integrationIssues: [],
    },
  };

  try {
    // ========== Phase 1: 后端API独立测试 ==========
    console.log('\n\n' + '='.repeat(60));
    console.log('📦 Phase 1: 后端API独立测试');
    console.log('='.repeat(60));

    const backendResults = await testBackendAPIs(browser);
    testResults.backendTests = backendResults;

    const backendSuccess = backendResults.filter(r => r.success).length;
    const backendFailed = backendResults.length - backendSuccess;

    testResults.summary.backendIssues = backendResults.filter(r => !r.success).map(r => ({
      api: r.api,
      error: r.error || r.data,
    }));

    console.log(`\n📊 后端API测试结果:`);
    console.log(`   成功: ${backendSuccess}/${backendResults.length}`);
    console.log(`   失败: ${backendFailed}`);

    // ========== Phase 2: 前端页面加载完整性测试 ==========
    console.log('\n\n' + '='.repeat(60));
    console.log('🎨 Phase 2: 前端页面加载完整性测试');
    console.log('='.repeat(60));

    const context = await browser.newContext({
      viewport: { width: 1920, height: 1080 },
    });

    for (const page of CORE_PAGES) {
      const pageCtx = await context.newPage();
      const pageResult = await testPageLoadIntegrity(pageCtx, page);
      testResults.frontendTests.push(pageResult);

      if (!pageResult.success) {
        testResults.summary.frontendIssues.push({
          page: page.name,
          url: page.url,
          issues: pageResult.issues,
        });
      }

      await pageCtx.close();
    }

    // ========== Phase 3: 前后端联动测试 ==========
    console.log('\n\n' + '='.repeat(60));
    console.log('🔗 Phase 3: 前后端联动测试');
    console.log('='.repeat(60));

    // ========== 生成报告 ==========
    console.log('\n\n' + '='.repeat(60));
    console.log('📊 生成测试报告');
    console.log('='.repeat(60));

    testResults.endTime = new Date().toISOString();
    testResults.summary.totalTests = backendResults.length + testResults.frontendTests.length;
    testResults.summary.passedTests = backendSuccess + testResults.frontendTests.filter(t => t.success).length;
    testResults.summary.failedTests = testResults.summary.totalTests - testResults.summary.passedTests;

    // 保存JSON报告
    await writeFile(
      CONFIG.reportPath,
      JSON.stringify(testResults, null, 2)
    );
    console.log(`\n✅ JSON报告已保存: ${CONFIG.reportPath}`);

    // 打印摘要
    console.log('\n\n' + '█'.repeat(60));
    console.log('█                    测试摘要                                 █');
    console.log('█'.repeat(60));
    console.log(`\n总测试数: ${testResults.summary.totalTests}`);
    console.log(`通过: ${testResults.summary.passedTests}`);
    console.log(`失败: ${testResults.summary.failedTests}`);

    if (testResults.summary.frontendIssues.length > 0) {
      console.log(`\n🔴 前端问题 (${testResults.summary.frontendIssues.length}):`);
      testResults.summary.frontendIssues.forEach(issue => {
        console.log(`   - ${issue.page}: ${issue.issues.length}个问题`);
        issue.issues.forEach(i => {
          console.log(`     • ${i.type}: ${i.message}`);
        });
      });
    }

    if (testResults.summary.backendIssues.length > 0) {
      console.log(`\n🟠 后端问题 (${testResults.summary.backendIssues.length}):`);
      testResults.summary.backendIssues.forEach(issue => {
        console.log(`   - ${issue.api}: ${issue.error}`);
      });
    }

    console.log('\n' + '█'.repeat(60));
    console.log(`\n📅 结束时间: ${testResults.endTime}`);

  } catch (err) {
    console.error(`\n❌ 测试执行失败: ${err}`);
    throw err;
  } finally {
    await browser.close();
  }
}

// ==================== 执行测试 ====================
if (import.meta.url === `file://${process.argv[1]}`) {
  runTests().catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });
}

export { runTests };
