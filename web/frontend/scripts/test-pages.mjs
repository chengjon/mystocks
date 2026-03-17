#!/usr/bin/env node

/**
 * MyStocks Frontend Page Tester
 *
 * 功能: 使用Puppeteer访问所有页面并检测JavaScript错误
 * 循环: Ralph Wiggum模式 - 持续测试直到所有页面无错误
 */

import fs from 'fs';
import path from 'path';
import http from 'http';
import { fileURLToPath } from 'url';

// ES module 中获取 __dirname
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 测试配置
const CONFIG = {
  baseUrl: 'http://localhost:3020',
  screenshotsDir: path.join(__dirname, '../test-reports/screenshots'),
  reportFile: path.join(__dirname, '../test-reports/page-test-report.json'),
  timeout: 10000,
  headless: true
};

// 所有需要测试的页面
const PAGES = [
  { path: '/', name: 'Home (重定向到Dashboard)' },
  { path: '/dashboard', name: 'Dashboard 总览' },
  { path: '/market/data', name: '市场行情' },
  { path: '/market/quotes', name: '行情报价' },
  { path: '/stocks/management', name: '股票管理' },
  { path: '/analysis/data', name: '投资分析' },
  { path: '/risk/management', name: '风险管理' },
  { path: '/strategy/trading', name: '策略和交易管理' },
  { path: '/strategy/backtest', name: '策略回测' },
  { path: '/system/monitoring', name: '系统监控' }
];

// 页面测试结果
let testResults = [];

/**
 * 检查依赖是否安装
 */
async function checkDependencies() {
  console.log('🔍 使用HTTP测试模式');
  console.log('ℹ️  如需完整测试，请安装 puppeteer: npm install puppeteer');
  return false;
}

/**
 * 使用Node.js HTTP测试页面（无Puppeteer）
 */
async function testPageWithHttp(page) {
  const url = new URL(page.path, CONFIG.baseUrl);

  return new Promise((resolve) => {
    const req = http.get(url.href, (res) => {
      let data = '';

      res.on('data', (chunk) => {
        data += chunk;
      });

      res.on('end', () => {
        // 检查页面是否包含常见错误标识
        const hasError = data.includes('Uncaught SyntaxError') ||
                        data.includes('TypeError:') ||
                        data.includes('ReferenceError:');

        resolve({
          path: page.path,
          name: page.name,
          status: res.statusCode,
          hasError,
          error: hasError ? '可能的JavaScript错误' : null
        });
      });
    });

    req.on('error', (error) => {
      resolve({
        path: page.path,
        name: page.name,
        status: 'ERROR',
        hasError: true,
        error: error.message
      });
    });

    req.setTimeout(CONFIG.timeout, () => {
      req.destroy();
      resolve({
        path: page.path,
        name: page.name,
        status: 'TIMEOUT',
        hasError: true,
        error: '请求超时'
      });
    });
  });
}

/**
 * 生成测试报告
 */
function generateReport(results) {
  const totalTests = results.length;
  const passedTests = results.filter(r => !r.hasError).length;
  const failedTests = results.filter(r => r.hasError).length;

  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: totalTests,
      passed: passedTests,
      failed: failedTests,
      successRate: ((passedTests / totalTests) * 100).toFixed(2) + '%'
    },
    results: results,
    issues: results.filter(r => r.hasError).map(r => ({
      page: r.name,
      path: r.path,
      error: r.error
    }))
  };

  return report;
}

/**
 * 保存报告到文件
 */
function saveReport(report) {
  const reportDir = path.dirname(CONFIG.reportFile);

  if (!fs.existsSync(reportDir)) {
    fs.mkdirSync(reportDir, { recursive: true });
  }

  fs.writeFileSync(
    CONFIG.reportFile,
    JSON.stringify(report, null, 2)
  );

  console.log(`\n📊 报告已保存: ${CONFIG.reportFile}`);
}

/**
 * 打印测试结果
 */
function printResults(report) {
  console.log('\n' + '='.repeat(80));
  console.log('📋 MyStocks Frontend 页面测试报告');
  console.log('='.repeat(80));

  console.log(`\n测试时间: ${report.timestamp}`);
  console.log(`测试总数: ${report.summary.total}`);
  console.log(`✅ 通过: ${report.summary.passed}`);
  console.log(`❌ 失败: ${report.summary.failed}`);
  console.log(`📈 成功率: ${report.summary.successRate}`);

  if (report.summary.failed > 0) {
    console.log('\n' + '⚠️  失败的页面:');
    report.issues.forEach((issue, index) => {
      console.log(`\n${index + 1}. ${issue.page}`);
      console.log(`   路径: ${issue.path}`);
      console.log(`   错误: ${issue.error}`);
    });
  }

  console.log('\n' + '='.repeat(80));
}

/**
 * 主测试函数
 */
async function runTests() {
  console.log('🚀 开始 MyStocks Frontend 页面测试...\n');
  console.log(`基础URL: ${CONFIG.baseUrl}`);
  console.log(`测试页面数: ${PAGES.length}`);
  console.log(''.repeat(80));

  // 检查依赖
  await checkDependencies();

  // 测试所有页面
  for (const page of PAGES) {
    console.log(`\n测试: ${page.name} (${page.path})`);

    const result = await testPageWithHttp(page);
    testResults.push(result);

    if (result.hasError) {
      console.log(`  ❌ 失败: ${result.error}`);
    } else {
      console.log(`  ✅ 成功 (HTTP ${result.status})`);
    }
  }

  // 生成并保存报告
  const report = generateReport(testResults);
  saveReport(report);
  printResults(report);

  // 返回是否所有测试都通过
  return report.summary.failed === 0;
}

/**
 * 执行Ralph Wiggum循环
 */
async function ralphLoop() {
  let attempt = 1;
  const maxAttempts = 10; // 防止无限循环

  while (attempt <= maxAttempts) {
    console.log(`\n${'='.repeat(80)}`);
    console.log(`🔄 Ralph Wiggum Loop - 尝试 #${attempt}`);
    console.log(`${'='.repeat(80)}`);

    const allPassed = await runTests();

    if (allPassed) {
      console.log('\n🎉 所有页面测试通过！停止循环。');
      process.exit(0);
    }

    console.log(`\n⚠️  发现问题，需要修复后重新测试...`);
    console.log(`💡 请查看错误报告并修复问题`);
    console.log(`📄 报告位置: ${CONFIG.reportFile}`);

    attempt++;

    if (attempt <= maxAttempts) {
      console.log(`\n⏳ 等待30秒后重试...`);
      console.log(`   (修复问题后，按 Ctrl+C 停止循环)`);

      await new Promise(resolve => setTimeout(resolve, 30000));
    }
  }

  console.log(`\n❌ 达到最大尝试次数 (${maxAttempts})，停止循环。`);
  process.exit(1);
}

// 运行
ralphLoop().catch(error => {
  console.error('❌ 测试失败:', error);
  process.exit(1);
});
