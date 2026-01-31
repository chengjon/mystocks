const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// 配置
const BASE_URL = 'http://localhost:3020'; // 确保使用正确的端口 3020
const REPORT_DIR = path.join(__dirname, '../reports/diagnosis');
const SCREENSHOT_DIR = path.join(REPORT_DIR, 'screenshots');

// 确保目录存在
if (!fs.existsSync(SCREENSHOT_DIR)) {
  fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
}

const PAGES = [
  { name: 'Dashboard', path: '/dashboard' },
  { name: 'Market', path: '/market/data' },
  { name: 'Analysis', path: '/analysis/data' }
];

async function diagnose() {
  console.log('🚀 开始前端-API联动状态摸底...');
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const report = {
    timestamp: new Date().toISOString(),
    pages: []
  };

  for (const pageConfig of PAGES) {
    const pageReport = {
      name: pageConfig.name,
      url: `${BASE_URL}${pageConfig.path}`,
      status: 'pending',
      errors: [],
      failedRequests: [],
      visualStatus: ''
    };

    console.log(`\n🔍 正在诊断页面: ${pageConfig.name} (${pageReport.url})`);

    const page = await browser.newPage();

    // 1. 捕获控制台错误
    page.on('console', msg => {
      if (msg.type() === 'error') {
        const text = msg.text();
        // 过滤掉非关键的样式警告
        if (!text.includes('deprecated')) {
          pageReport.errors.push(`[Console Error] ${text}`);
        }
      }
    });

    page.on('pageerror', err => {
      pageReport.errors.push(`[Page Error] ${err.message}`);
    });

    // 2. 捕获网络请求失败
    page.on('requestfailed', request => {
      pageReport.failedRequests.push({
        url: request.url(),
        method: request.method(),
        error: request.failure()?.errorText || 'Unknown error'
      });
    });

    page.on('response', response => {
      const status = response.status();
      if (status >= 400) {
        pageReport.failedRequests.push({
          url: response.url(),
          method: response.request().method(),
          status: status,
          statusText: response.statusText()
        });
      }
    });

    try {
      // 设置视口大小为桌面标准
      await page.setViewport({ width: 1920, height: 1080 });

      // 访问页面，等待网络空闲
      await page.goto(pageReport.url, { waitUntil: 'networkidle0', timeout: 30000 });

      // 等待额外的渲染时间 (Vue 组件挂载)
      await new Promise(r => setTimeout(r, 2000));

      // 3. 截图证据
      const screenshotPath = path.join(SCREENSHOT_DIR, `${pageConfig.name.toLowerCase()}_state.png`);
      await page.screenshot({ path: screenshotPath, fullPage: true });
      pageReport.visualStatus = `截图已保存: ${screenshotPath}`;

      // 简单判断页面内容 (是否有数据表格或图表)
      const hasContent = await page.evaluate(() => {
        // 检查常见的无数据指示器
        const emptyText = document.body.innerText.includes('No Data') || document.body.innerText.includes('暂无数据');
        // 检查是否有表格行 (除了表头)
        const hasTableRows = document.querySelectorAll('tr').length > 1;
        // 检查是否有图表 canvas
        const hasCanvas = document.querySelectorAll('canvas').length > 0;

        return { emptyText, hasTableRows, hasCanvas };
      });

      pageReport.contentAnalysis = hasContent;
      pageReport.status = (pageReport.errors.length === 0 && pageReport.failedRequests.length === 0) ? 'healthy' : 'issues_found';

    } catch (error) {
      pageReport.status = 'failed';
      pageReport.errors.push(`[Navigation Error] ${error.message}`);
    } finally {
      await page.close();
    }

    report.pages.push(pageReport);

    // 输出即时摘要
    console.log(`   - 状态: ${pageReport.status}`);
    console.log(`   - 控制台错误: ${pageReport.errors.length}`);
    console.log(`   - 失败请求: ${pageReport.failedRequests.length}`);
    if (pageReport.failedRequests.length > 0) {
      console.log(`     首个失败API: ${pageReport.failedRequests[0].url} (${pageReport.failedRequests[0].status || 'Failed'})`);
    }
  }

  await browser.close();

  // 保存完整报告
  const reportPath = path.join(REPORT_DIR, 'diagnosis_report.json');
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
  console.log(`\n📋 完整诊断报告已生成: ${reportPath}`);
}

diagnose().catch(console.error);
