#!/usr/bin/env node

/**
 * Web 端访问验证脚本
 * 遵循 docs/guides/WEB_ACCESS_VERIFICATION_STANDARD.md v2.0
 *
 * 使用方法：
 *   node scripts/dev/verify_web_access.mjs
 *   # 或
 *   npm run verify:web-access
 */

import { chromium } from 'playwright';
import { readFileSync, existsSync } from 'fs';
import { globSync } from 'glob';
import path from 'path';

const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const FRONTEND_BACKUP_PORT = process.env.FRONTEND_BACKUP_PORT || '3021';
const BACKEND_PORT = process.env.BACKEND_PORT || '8020';

// 配置
const CONFIG = {
  frontendUrl: process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`,
  backendUrl: process.env.BACKEND_URL || `http://localhost:${BACKEND_PORT}`,
  timeout: 30000, 
  loadTimeThreshold: 3000, 
};

/**
 * 智能探测前端端口
 */
async function probeFrontend(browser) {
  const ports = [Number(FRONTEND_PORT), Number(FRONTEND_BACKUP_PORT)];
  // 优先使用环境变量
  if (process.env.FRONTEND_URL) return process.env.FRONTEND_URL;

  console.log('📡 正在探测前端服务端口...');
  for (const port of ports) {
    try {
      const url = `http://localhost:${port}`;
      const page = await browser.newPage();
      const response = await page.goto(url, { timeout: 2000 });
      await page.close();
      if (response && response.status() < 500) {
        console.log(`🎯 发现前端服务运行在: ${url}`);
        return url;
      }
    } catch (e) {
      // 继续探测
    }
  }
  return CONFIG.frontendUrl;
}

// 结果收集
const results = {
  timestamp: new Date().toISOString(),
  frontendUrl: CONFIG.frontendUrl,
  backendUrl: CONFIG.backendUrl,
  dataMode: 'unknown',
  backendHealth: { status: 'unknown', latency: 0 },
  routes: [],
  passed: [],
  failed: [],
  errors: {},
  summary: {
    total: 0,
    passed: 0,
    failed: 0,
    avgLoadTime: 0,
  },
};

/**
 * 动态发现路由
 */
function discoverRoutes() {
  const projectRoot = path.resolve(process.cwd());
  const routes = [];

  // 1. 尝试从架构规划文档读取
  const planPath = path.join(projectRoot, 'docs/architecture/ROUTING_OPTIMIZATION_PLAN.md');
  if (existsSync(planPath)) {
    console.log(`📖 正在从架构文档解析: ${planPath}`);
    const content = readFileSync(planPath, 'utf-8');
    
    // 匹配任何在 | | 之间的以 / 开头的字符串，忽略反引号
    const pathRegex = /\|\s*[`]?(\/[a-zA-Z0-9\/\-_]+)[`]?\s*\|/g;
    let match;
    while ((match = pathRegex.exec(content)) !== null) {
      routes.push(match[1]);
    }
  }

  // 2. 核心路由（确保不遗漏关键页面）
  const coreRoutes = [
    '/', '/login', '/dashboard',
    '/market/realtime', '/market/overview', '/market/analysis', '/market/industry',
    '/market/technical', '/market/fund-flow', '/market/etf', '/market/concept',
    '/market/auction', '/market/longhubang', '/market/institution', '/market/wencai', '/market/screener',
    '/stocks/management', '/stocks/portfolio',
    '/trading/signals', '/trading/history', '/trading/positions', '/trading/performance', '/trading/attribution',
    '/strategy/design', '/strategy/management', '/strategy/backtest', '/strategy/gpu-backtest', '/strategy/optimization',
    '/risk/overview', '/risk/alerts', '/risk/indicators', '/risk/sentiment', '/risk/announcement',
    '/system/monitoring', '/system/settings', '/system/data-update', '/system/data-quality', '/system/api-health'
  ];
  routes.push(...coreRoutes);

  // 3. 补充高级分析页面
  const advancedAnalysisRoutes = [
    '/analysis/fundamental', '/analysis/technical', '/analysis/chip', '/analysis/valuation'
  ];
  routes.push(...advancedAnalysisRoutes);

  // 去重并排序
  const uniqueRoutes = [...new Set(routes)].sort();
  console.log(`✅ 最终确定验证 ${uniqueRoutes.length} 个核心路由`);
  return uniqueRoutes;
}

/**
 * 检查后端健康状态
 */
async function checkBackendHealth() {
  const startTime = Date.now();
  try {
    const response = await fetch(`${CONFIG.backendUrl}/health`, {
      signal: AbortSignal.timeout(5000),
    });
    const latency = Date.now() - startTime;
    const data = await response.json();

    results.backendHealth = {
      status: data.success && data.data?.status === 'healthy' ? 'healthy' : 'unhealthy',
      code: data.code,
      latency,
    };

    return results.backendHealth.status === 'healthy';
  } catch (error) {
    results.backendHealth = {
      status: 'error',
      error: error.message,
      latency: Date.now() - startTime,
    };
    return false;
  }
}

/**
 * 检测数据源模式
 */
function detectDataMode() {
  try {
    const envPath = path.resolve(process.cwd(), 'web/frontend/.env');
    if (existsSync(envPath)) {
      const envContent = readFileSync(envPath, 'utf-8');
      const modeMatch = envContent.match(/VITE_APP_MODE\s*=\s*(\w+)/);
      results.dataMode = modeMatch ? modeMatch[1] : 'unknown';
    }
  } catch (error) {
    results.dataMode = 'unknown';
  }
  return results.dataMode;
}

/**
 * 测试单个页面
 */
async function testPage(browser, route) {
  const page = await browser.newPage();
  const startTime = Date.now();

  const pageResult = {
    route,
    status: 200,
    finalUrl: route,
    issues: [],
    pageErrors: [],
    consoleErrors: [],
    hasContent: false,
    hasViteError: false,
    loadTime: 0,
  };

  try {
    // 收集控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        pageResult.consoleErrors.push(msg.text());
      }
    });

    // 收集页面错误
    page.on('pageerror', error => {
      pageResult.pageErrors.push(error.message);
    });

    // 访问页面
    const response = await page.goto(`${CONFIG.frontendUrl}${route}`, {
      waitUntil: 'networkidle',
      timeout: CONFIG.timeout,
    });

    pageResult.status = response.status();
    pageResult.finalUrl = page.url().replace(CONFIG.frontendUrl, '');
    pageResult.loadTime = Date.now() - startTime;

    // 检查是否有 Vite 错误
    const content = await page.content();
    pageResult.hasViteError = content.includes('Error') && content.includes('vite');

    // 检查是否有实际内容
    const mainElement = await page.$('main, #app, [role="main"]');
    if (mainElement) {
      const textContent = await mainElement.textContent();
      pageResult.hasContent = textContent && textContent.trim().length > 50;
    }

    // 判断问题
    if (!pageResult.hasContent) {
      pageResult.issues.push('WHITE_SCREEN');
    }
    if (pageResult.hasViteError) {
      pageResult.issues.push('VITE_ERROR');
    }
    if (pageResult.pageErrors.length > 0) {
      pageResult.issues.push(`PAGE_ERRORS(${pageResult.pageErrors.length})`);
    }
    if (pageResult.consoleErrors.length > 0) {
      pageResult.issues.push(`CONSOLE_ERRORS(${pageResult.consoleErrors.length})`);
    }
    if (pageResult.loadTime > CONFIG.loadTimeThreshold) {
      pageResult.issues.push(`SLOW_LOAD(${pageResult.loadTime}ms)`);
    }

  } catch (error) {
    pageResult.issues.push('NAVIGATION_ERROR');
    pageResult.pageErrors.push(error.message);
    pageResult.loadTime = Date.now() - startTime;
  } finally {
    await page.close();
  }

  return pageResult;
}

/**
 * 生成报告
 */
function generateReport() {
  const { total, passed, failed } = results.summary;
  const passRate = total > 0 ? ((passed / total) * 100).toFixed(1) : 0;

  // 计算平均加载时间
  const allResults = [...results.passed.map(r => ({ ...r, pass: true })),
                      ...results.failed.map(r => ({ ...r, pass: false }))];
  const totalLoadTime = allResults.reduce((sum, r) => sum + (r.loadTime || 0), 0);
  results.summary.avgLoadTime = allResults.length > 0 ?
    (totalLoadTime / allResults.length).toFixed(0) : 0;

  // 确定结论
  let conclusion = '✅ 服务正常';
  if (passRate < 100 && passRate >= 70) {
    conclusion = '⚠️ 部分可用';
  } else if (passRate < 70) {
    conclusion = '❌ 服务异常';
  }

  // 输出 Markdown 报告
  console.log('\n' + '='.repeat(60));
  console.log('## Web 端访问验证报告');
  console.log('='.repeat(60));
  console.log(`\n**验证时间**: ${results.timestamp}`);
  console.log(`**前端端口**: ${CONFIG.frontendUrl.replace('http://localhost:', '')}`);
  console.log(`**后端端口**: ${CONFIG.backendUrl.replace('http://localhost:', '')}`);
  console.log(`**数据源**: ${results.dataMode.toUpperCase()}`);

  console.log('\n### 服务状态');
  console.log(`- 后端健康检查: ${results.backendHealth.status === 'healthy' ? '✅' : '❌'} (延迟: ${results.backendHealth.latency}ms)`);
  console.log(`- 前端编译状态: ${results.failed.some(r => r.issues.includes('VITE_ERROR')) ? '❌' : '✅'}`);

  console.log('\n### 页面测试结果');
  console.log(`- 总路由数: ${total} (动态发现)`);
  console.log(`- 通过: ${passed}/${total} (${passRate}%)`);
  console.log(`- 失败: ${failed}/${total}`);
  console.log(`- 平均加载时间: ${results.summary.avgLoadTime}ms`);

  if (results.failed.length > 0) {
    console.log('\n### 失败页面详情');
    console.log('| 页面 | 问题类型 | 加载时间 |');
    console.log('|------|---------|---------|');
    for (const page of results.failed.slice(0, 10)) {
      console.log(`| ${page.route} | ${page.issues.join(', ')} | ${page.loadTime}ms |`);
    }
    if (results.failed.length > 10) {
      console.log(`| ... | 还有 ${results.failed.length - 10} 个 | |`);
    }
  }

  console.log(`\n### 结论`);
  console.log(conclusion);
  console.log('\n' + '='.repeat(60));

  return passRate === '100.0' ? 0 : 1;
}

/**
 * 主函数
 */
async function main() {
  console.log('🔍 Web 端访问验证工具 v2.0');
  console.log('遵循标准: docs/guides/WEB_ACCESS_VERIFICATION_STANDARD.md\n');

  // 1. 检查后端健康
  console.log('📡 检查后端健康状态...');
  const backendHealthy = await checkBackendHealth();
  if (!backendHealthy) {
    console.log('❌ 后端不健康，请先启动后端服务');
    process.exit(1);
  }
  console.log(`✅ 后端健康 (延迟: ${results.backendHealth.latency}ms)\n`);

  // 2. 检测数据源模式
  console.log('🔎 检测数据源模式...');
  detectDataMode();
  console.log(`📊 数据源模式: ${results.dataMode.toUpperCase()}\n`);

  // 3. 动态发现路由
  console.log('🔍 动态发现路由...');
  results.routes = discoverRoutes();
  results.summary.total = results.routes.length;
  console.log('');

  // 4. 启动浏览器
  console.log('🌐 启动 Playwright 浏览器...');
  
  // 自动检测本地已有的浏览器路径
  const possiblePaths = [
    '/root/.cache/ms-playwright/chromium-1200/chrome-linux64/chrome',
    '/root/.cache/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-linux64/chrome-headless-shell',
    '/usr/bin/google-chrome',
    '/usr/bin/chromium-browser'
  ];
  
  let executablePath = null;
  for (const p of possiblePaths) {
    if (existsSync(p)) {
      executablePath = p;
      console.log(`  📍 使用浏览器路径: ${p}`);
      break;
    }
  }

  let browser;
  try {
    const launchOptions = { headless: true };
    if (executablePath) {
      launchOptions.executablePath = executablePath;
    }
    browser = await chromium.launch(launchOptions);
  } catch (e) {
    console.log(`  ⚠️ 无法启动指定浏览器，尝试默认启动...`);
    browser = await chromium.launch({ headless: true });
  }
  
  // 智能探测端口
  CONFIG.frontendUrl = await probeFrontend(browser);
  results.frontendUrl = CONFIG.frontendUrl;
  console.log('');

  // 5. 测试每个页面
  console.log('📋 开始测试页面...\n');

  for (let i = 0; i < results.routes.length; i++) {
    const route = results.routes[i];
    process.stdout.write(`[${i + 1}/${results.routes.length}] 测试 ${route}... `);

    const pageResult = await testPage(browser, route);

    if (pageResult.issues.length === 0) {
      results.passed.push(pageResult);
      results.summary.passed++;
      console.log('✅ OK');
    } else {
      results.failed.push(pageResult);
      results.summary.failed++;
      results.errors[route] = pageResult;
      console.log(`❌ ${pageResult.issues.join(', ')}`);
      // Print first 3 console errors for debugging
      if (pageResult.consoleErrors.length > 0) {
        console.log('    Console Errors (First 3):');
        pageResult.consoleErrors.slice(0, 3).forEach(e => console.log(`      🔴 ${e.substring(0, 100)}...`));
      }
    }
  }

  await browser.close();

  // 6. 生成报告
  const exitCode = generateReport();

  // 保存结果到文件
  const outputPath = path.resolve(process.cwd(), 'scripts/dev/page_test_results.json');
  const outputData = {
    timestamp: results.timestamp,
    dataMode: results.dataMode,
    backendHealth: results.backendHealth,
    pass: results.passed.map(r => r.route),
    fail: results.failed.map(r => r.route),
    errors: results.errors,
    summary: results.summary,
  };

  import('fs').then(fs => {
    fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2));
    console.log(`\n📄 详细报告已保存到: ${outputPath}`);
  });

  process.exit(exitCode);
}

main().catch(error => {
  console.error('❌ 验证失败:', error.message);
  process.exit(1);
});
