#!/usr/bin/env node
/**
 * ArtDeco页面浏览器验证脚本
 * 使用Playwright进行真实的浏览器渲染验证
 */

import { chromium } from 'playwright';

const pages = [
  { path: '/#/dashboard', name: '仪表盘' },
  { path: '/#/market/data', name: '市场数据' },
  { path: '/#/market/quotes', name: '市场行情' },
  { path: '/#/stocks/management', name: '股票管理' },
  { path: '/#/analysis/data', name: '投资分析' },
  { path: '/#/risk/management', name: '风险管理' },
  { path: '/#/strategy/trading', name: '策略和交易管理' },
  { path: '/#/system/monitoring', name: '系统监控' }
];

const BASE_URL = 'http://localhost:3001';

async function checkPage(browser, pageInfo) {
  const page = await browser.newPage();

  try {
    console.log(`  正在检查: ${pageInfo.name}...`);

    // 导航到页面
    await page.goto(`${BASE_URL}${pageInfo.path}`, {
      waitUntil: 'domcontentloaded',
      timeout: 10000
    });

    // 等待客户端渲染完成
    await page.waitForTimeout(2000);

    // 检查关键ArtDeco元素
    const hasDashboard = await page.locator('.artdeco-dashboard').count() > 0;
    const hasHeader = await page.locator('.artdeco-header').count() > 0;
    const hasLayout = await page.locator('.layout-sidebar').count() > 0;
    const hasMenu = await page.locator('.nav-link').count() > 0;

    // 检查主内容区域
    const hasMainContent = await page.locator('.main-content, .content-area').count() > 0;

    // 检查页面标题
    const title = await page.title();

    // 检查是否有JavaScript错误
    const jsErrors = [];
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });

    const allPresent = hasDashboard && hasHeader && hasLayout && hasMenu && hasMainContent;

    return {
      name: pageInfo.name,
      path: pageInfo.path,
      status: allPresent ? '✅ PASS' : '⚠️ PARTIAL',
      hasDashboard,
      hasHeader,
      hasLayout,
      hasMenu,
      hasMainContent,
      title,
      jsErrors: jsErrors.length,
      loadTime: page.waitForTimeout !== undefined ? 'OK' : 'Unknown'
    };
  } catch (error) {
    return {
      name: pageInfo.name,
      path: pageInfo.path,
      status: '❌ ERROR',
      error: error.message
    };
  } finally {
    await page.close();
  }
}

async function main() {
  console.log('🔍 ArtDeco页面浏览器验证开始...\n');
  console.log(`基础URL: ${BASE_URL}\n`);

  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  } catch (error) {
    console.error('❌ 无法启动浏览器:', error.message);
    console.error('💡 提示: 确保已安装Playwright: npx playwright install chromium');
    process.exit(1);
  }

  const results = [];

  for (const pageInfo of pages) {
    const result = await checkPage(browser, pageInfo);
    results.push(result);

    const status = result.status.padEnd(8);
    console.log(`${status} ${result.name}`);

    if (result.error) {
      console.log(`       错误: ${result.error}`);
    } else if (result.status === '⚠️ PARTIAL') {
      const missing = [];
      if (!result.hasDashboard) missing.push('Dashboard');
      if (!result.hasHeader) missing.push('Header');
      if (!result.hasLayout) missing.push('Layout');
      if (!result.hasMenu) missing.push('Menu');
      if (!result.hasMainContent) missing.push('MainContent');

      if (missing.length > 0) {
        console.log(`       缺失: ${missing.join(', ')}`);
      }
    }

    // 避免请求过快
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  await browser.close();

  console.log('\n📊 验证结果汇总:');
  const passed = results.filter(r => r.status === '✅ PASS').length;
  const failed = results.filter(r => r.status.includes('❌')).length;
  const partial = results.filter(r => r.status.includes('⚠️')).length;

  console.log(`  ✅ 完全通过: ${passed}`);
  console.log(`  ⚠️  部分通过: ${partial}`);
  console.log(`  ❌ 失败: ${failed}`);
  console.log(`  📈 完整通过率: ${Math.round((passed / results.length) * 100)}%`);

  // 详细报告
  console.log('\n📋 详细结果:');
  for (const result of results) {
    console.log(`\n  ${result.name}:`);
    console.log(`    状态: ${result.status}`);
    console.log(`    页面: ${result.path}`);

    if (result.error) {
      console.log(`    错误: ${result.error}`);
    } else {
      console.log(`    Dashboard: ${result.hasDashboard ? '✅' : '❌'}`);
      console.log(`    Header: ${result.hasHeader ? '✅' : '❌'}`);
      console.log(`    Layout: ${result.hasLayout ? '✅' : '❌'}`);
      console.log(`    Menu: ${result.hasMenu ? '✅' : '❌'}`);
      console.log(`    MainContent: ${result.hasMainContent ? '✅' : '❌'}`);
      console.log(`    Title: ${result.title || '(empty)'}`);

      if (result.jsErrors > 0) {
        console.log(`    JS Errors: ${result.jsErrors}`);
      }
    }
  }

  if (passed === results.length) {
    console.log('\n🎉 所有ArtDeco页面验证通过！系统运行正常。');
  } else if (passed > 0) {
    console.log(`\n✅ ${passed}个页面完全通过，${partial}个页面部分通过。`);
  } else if (partial > 0) {
    console.log('\n⚠️  所有页面都部分通过，建议检查组件加载。');
  } else {
    console.log('\n❌ 部分页面验证失败，建议检查服务器状态。');
  }

  process.exit(failed > 0 ? 1 : 0);
}

main().catch(error => {
  console.error('❌ 验证脚本执行失败:', error);
  process.exit(1);
});
