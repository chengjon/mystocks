import { chromium } from 'playwright';
import fs from 'fs';
import path from 'path';

// 测试配置
const FRONTEND_PORT = process.env.FRONTEND_PORT || '3020';
const BASE_URL = process.env.FRONTEND_URL || `http://localhost:${FRONTEND_PORT}`;
const OUTPUT_DIR = '/tmp/web-test-results';

// 创建输出目录
if (!fs.existsSync(OUTPUT_DIR)) {
  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
}

// 要测试的页面列表
const PAGES = [
  // MainLayout - 主要页面
  { url: '/', name: '首页-仪表盘', category: 'MainLayout' },
  { url: '/analysis', name: '数据分析', category: 'MainLayout' },
  { url: '/stocks', name: '股票管理', category: 'MainLayout' },
  { url: '/technical', name: '技术分析', category: 'MainLayout' },
  { url: '/settings', name: '系统设置', category: 'MainLayout' },

  // MarketLayout - 市场行情
  { url: '/market/list', name: '市场行情', category: 'MarketLayout' },
  { url: '/market/tdx-market', name: 'TDX行情', category: 'MarketLayout' },
  { url: '/market/realtime', name: '实时监控', category: 'MarketLayout' },

  // DataLayout - 市场数据
  { url: '/market-data/fund-flow', name: '资金流向', category: 'DataLayout' },
  { url: '/market-data/etf', name: 'ETF行情', category: 'DataLayout' },

  // RiskLayout - 风险监控
  { url: '/risk-monitor/overview', name: '风险监控', category: 'RiskLayout' },

  // StrategyLayout - 策略中心
  { url: '/strategy-hub/management', name: '策略管理', category: 'StrategyLayout' },
  { url: '/strategy-hub/backtest', name: '回测分析', category: 'StrategyLayout' },

  // ArtDeco - 装饰艺术风格
  { url: '/artdeco/dashboard', name: 'ArtDeco主控仪表盘', category: 'ArtDeco' },
  { url: '/artdeco/market-center', name: 'ArtDeco市场中心', category: 'ArtDeco' },
];

// 测试结果存储
const testResults = {
  summary: {
    total: PAGES.length,
    passed: 0,
    failed: 0,
    skipped: 0
  },
  pages: [],
  issues: []
};

// 格式化时间戳
function getTimestamp() {
  return new Date().toISOString().replace('T', ' ').substring(0, 19);
}

// 主测试函数
async function runTests() {
  console.log(`\n🚀 开始 Web 应用测试`);
  console.log(`📅 时间: ${getTimestamp()}`);
  console.log(`🌐 基础 URL: ${BASE_URL}`);
  console.log(`📊 测试页面数: ${PAGES.length}\n`);

  const browser = await chromium.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });

  const page = await context.newPage();

  // 设置超时和错误处理
  page.setDefaultTimeout(10000);

  for (let i = 0; i < PAGES.length; i++) {
    const pageInfo = PAGES[i];
    const pageId = i + 1;

    console.log(`\n[${pageId}/${PAGES.length}] 测试: ${pageInfo.name}`);
    console.log(`   URL: ${BASE_URL}${pageInfo.url}`);
    console.log(`   分类: ${pageInfo.category}`);

    const pageResult = {
      ...pageInfo,
      timestamp: getTimestamp(),
      success: false,
      loadTime: 0,
      issues: [],
      screenshot: null
    };

    try {
      const startTime = Date.now();

      // 访问页面 - 对SSE页面使用domcontentloaded
      const waitStrategy = pageInfo.url.includes('realtime') ? 'domcontentloaded' : 'networkidle';
      const response = await page.goto(BASE_URL + pageInfo.url, {
        waitUntil: waitStrategy,
        timeout: pageInfo.url.includes('realtime') ? 30000 : 15000
      });

      const loadTime = Date.now() - startTime;
      pageResult.loadTime = loadTime;
      pageResult.httpStatus = response?.status();

      console.log(`   ✅ 页面加载成功 (${loadTime}ms)`);

      // 检查页面元素
      const bodyVisible = await page.locator('body').isVisible();
      const hasContent = await page.locator('body').textContent() !== '';

      // 检查错误提示
      const errorElements = await page.locator('.error, .alert-error, [class*="error"]').count();
      const consoleErrors = [];

      page.on('console', msg => {
        if (msg.type() === 'error') {
          consoleErrors.push(msg.text());
        }
      });

      // 截图
      const screenshotPath = path.join(OUTPUT_DIR, `${pageId}-${pageInfo.name.replace(/\s+/g, '_')}.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      pageResult.screenshot = screenshotPath;

      console.log(`   📸 截图已保存: ${screenshotPath}`);

      // 检查控制台错误
      await page.waitForTimeout(1000); // 等待一秒收集控制台错误

      if (errorElements > 0) {
        const errorMsg = `发现 ${errorElements} 个错误元素`;
        pageResult.issues.push(errorMsg);
        console.log(`   ⚠️  ${errorMsg}`);
      }

      if (consoleErrors.length > 0) {
        pageResult.issues.push(`控制台错误: ${consoleErrors.length}个`);
        console.log(`   ⚠️  控制台错误: ${consoleErrors.length}个`);
      }

      // 检查页面标题
      const title = await page.title();
      pageResult.pageTitle = title;
      console.log(`   📄 页面标题: ${title}`);

      pageResult.success = true;
      testResults.summary.passed++;

    } catch (error) {
      const errorMsg = error.message;
      pageResult.issues.push(errorMsg);

      console.log(`   ❌ 测试失败: ${errorMsg.substring(0, 100)}`);

      // 失败时也截图
      try {
        const screenshotPath = path.join(OUTPUT_DIR, `${pageId}-${pageInfo.name.replace(/\s+/g, '_')}-ERROR.png`);
        await page.screenshot({ path: screenshotPath, fullPage: true });
        pageResult.screenshot = screenshotPath;
      } catch (screenshotError) {
        // 忽略截图错误
      }

      testResults.summary.failed++;
      testResults.issues.push({
        page: pageInfo.name,
        url: pageInfo.url,
        error: errorMsg.substring(0, 200)
      });
    }

    testResults.pages.push(pageResult);
  }

  await browser.close();

  // 生成测试报告
  generateReport();

  console.log('\n✅ 测试完成!\n');
}

// 生成测试报告
function generateReport() {
  const reportPath = path.join(OUTPUT_DIR, 'test-report.json');
  fs.writeFileSync(reportPath, JSON.stringify(testResults, null, 2));

  // 生成 Markdown 报告
  const mdReport = generateMarkdownReport();
  const mdPath = path.join(OUTPUT_DIR, 'TEST_REPORT.md');
  fs.writeFileSync(mdPath, mdReport);

  console.log(`\n📊 测试报告已生成:`);
  console.log(`   - JSON: ${reportPath}`);
  console.log(`   - Markdown: ${mdPath}`);

  // 打印摘要
  printSummary();
}

// 生成 Markdown 报告
function generateMarkdownReport() {
  const { summary, pages, issues } = testResults;

  let md = `# Web 应用测试报告\n\n`;
  md += `**测试时间**: ${getTimestamp()}\n`;
  md += `**基础 URL**: ${BASE_URL}\n`;
  md += `**测试页面数**: ${summary.total}\n\n`;

  // 摘要
  md += `## 📊 测试摘要\n\n`;
  md += `| 指标 | 数值 |\n`;
  md += `|------|------|\n`;
  md += `| 总测试数 | ${summary.total} |\n`;
  md += `| ✅ 通过 | ${summary.passed} |\n`;
  md += `| ❌ 失败 | ${summary.failed} |\n`;
  md += `| ⏭️  跳过 | ${summary.skipped} |\n`;
  md += `| 通过率 | ${((summary.passed / summary.total) * 100).toFixed(1)}% |\n\n`;

  // 页面测试结果
  md += `## 📄 页面测试结果\n\n`;

  pages.forEach((page, index) => {
    const status = page.success ? '✅' : '❌';
    md += `### ${status} ${index + 1}. ${page.name}\n\n`;
    md += `- **URL**: \`${BASE_URL}${page.url}\`\n`;
    md += `- **分类**: ${page.category}\n`;
    md += `- **加载时间**: ${page.loadTime}ms\n`;

    if (page.pageTitle) {
      md += `- **页面标题**: ${page.pageTitle}\n`;
    }

    if (page.httpStatus) {
      md += `- **HTTP状态**: ${page.httpStatus}\n`;
    }

    if (page.issues.length > 0) {
      md += `- **问题**:\n`;
      page.issues.forEach(issue => {
        md += `  - ${issue}\n`;
      });
    }

    if (page.screenshot) {
      md += `- **截图**: ${page.screenshot}\n`;
    }

    md += `\n`;
  });

  // 问题列表
  if (issues.length > 0) {
    md += `## ⚠️ 发现的问题\n\n`;
    issues.forEach((issue, index) => {
      md += `### ${index + 1}. ${issue.page}\n\n`;
      md += `- **URL**: \`${BASE_URL}${issue.url}\`\n`;
      md += `- **错误**: ${issue.error}\n\n`;
    });
  }

  // 按分类统计
  md += `## 📈 分类统计\n\n`;
  const categories = {};
  pages.forEach(page => {
    if (!categories[page.category]) {
      categories[page.category] = { total: 0, passed: 0, failed: 0 };
    }
    categories[page.category].total++;
    if (page.success) {
      categories[page.category].passed++;
    } else {
      categories[page.category].failed++;
    }
  });

  Object.keys(categories).forEach(category => {
    const stats = categories[category];
    const passRate = ((stats.passed / stats.total) * 100).toFixed(1);
    md += `- **${category}**: ${stats.passed}/${stats.total} (${passRate}%)\n`;
  });

  md += `\n---\n`;
  md += `**生成时间**: ${getTimestamp()}\n`;

  return md;
}

// 打印摘要
function printSummary() {
  const { summary, issues } = testResults;

  console.log('\n' + '='.repeat(60));
  console.log('📊 测试摘要');
  console.log('='.repeat(60));
  console.log(`总测试数: ${summary.total}`);
  console.log(`✅ 通过: ${summary.passed} (${((summary.passed / summary.total) * 100).toFixed(1)}%)`);
  console.log(`❌ 失败: ${summary.failed}`);
  console.log(`⏭️  跳过: ${summary.skipped}`);

  if (issues.length > 0) {
    console.log('\n⚠️  发现的问题:');
    issues.forEach((issue, index) => {
      console.log(`\n${index + 1}. ${issue.page}`);
      console.log(`   URL: ${BASE_URL}${issue.url}`);
      console.log(`   错误: ${issue.error.substring(0, 100)}...`);
    });
  }

  console.log('\n' + '='.repeat(60));
}

// 运行测试
runTests().catch(error => {
  console.error('测试执行失败:', error);
  process.exit(1);
});
