import { chromium } from 'playwright';
import fs from 'fs';

const BASE_URL = 'http://localhost:3020';
const outputDir = '/tmp/mystocks_screenshots';

// 创建输出目录
if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const pages = [
  { name: '01-login', path: '/login', title: '登录页' },
  { name: '02-dashboard', path: '/dashboard', title: '仪表盘' },
  { name: '03-market-realtime', path: '/market/realtime', title: '实时行情' },
  { name: '04-stocks-management', path: '/stocks/management', title: '股票管理' },
  { name: '05-risk-overview', path: '/risk/overview', title: '风险概览' },
  { name: '06-trading-signals', path: '/trading/signals', title: '交易信号' },
  { name: '07-strategy-management', path: '/strategy/management', title: '策略管理' },
  { name: '08-system-monitoring', path: '/system/monitoring', title: '系统监控' },
];

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();
  
  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║         MyStocks Web 应用截图展示                          ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');
  
  // 先登录
  console.log('📝 步骤 1: 用户登录...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(1000);
  
  const usernameInput = page.locator('input[placeholder*="username" i], input[type="text"]').first();
  const passwordInput = page.locator('input[type="password"]').first();
  const submitButton = page.locator('button[type="submit"]').first();
  
  await usernameInput.fill('admin');
  await passwordInput.fill('admin123');
  await submitButton.click();
  await page.waitForTimeout(3000);
  
  const loginUrl = page.url();
  console.log(`   登录后URL: ${loginUrl}`);
  console.log(`   登录状态: ${loginUrl.includes('/login') ? '❌ 失败' : '✅ 成功'}\n`);
  
  // 截取各页面
  console.log('📸 步骤 2: 截取各功能页面...\n');
  console.log('┌─────────────────────────────────────────────────────────────┐');
  console.log('│ 页面名称              │ 路径                        │ 状态  │');
  console.log('├─────────────────────────────────────────────────────────────┤');
  
  for (const pageInfo of pages) {
    try {
      await page.goto(`${BASE_URL}${pageInfo.path}`, { waitUntil: 'domcontentloaded', timeout: 15000 });
      await page.waitForTimeout(2000);
      
      const title = await page.title();
      const url = page.url();
      const screenshotPath = `${outputDir}/${pageInfo.name}.png`;
      
      await page.screenshot({ path: screenshotPath, fullPage: false });
      
      const name = pageInfo.title.padEnd(18, ' ');
      const path = pageInfo.path.padEnd(26, ' ');
      console.log(`│ ${name} │ ${path} │ ✅    │`);
      console.log(`│   标题: ${title.substring(0, 50).padEnd(51, ' ')}│`);
    } catch (err) {
      const name = pageInfo.title.padEnd(18, ' ');
      const path = pageInfo.path.padEnd(26, ' ');
      console.log(`│ ${name} │ ${path} │ ❌    │`);
      console.log(`│   错误: ${err.message.substring(0, 48).padEnd(49, ' ')}│`);
    }
  }
  
  console.log('└─────────────────────────────────────────────────────────────┘');
  
  await browser.close();
  console.log(`\n✅ 截图已保存到: ${outputDir}/`);
  console.log('\n🔗 访问地址:');
  console.log(`   前端: http://localhost:3020`);
  console.log(`   后端: http://localhost:8000`);
  console.log(`   API文档: http://localhost:8000/docs`);
}

main().catch(console.error);
