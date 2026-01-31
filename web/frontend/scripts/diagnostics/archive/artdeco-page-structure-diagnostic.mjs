#!/usr/bin/env node
/**
 * ArtDeco页面结构深度诊断
 * 分析每个页面的实际DOM结构
 */

import { chromium } from 'playwright';

const pages = [
  { path: '/#/dashboard', name: '仪表盘', expected: 'ArtDecoDashboard' },
  { path: '/#/market/data', name: '市场数据', expected: 'ArtDecoMarketData' },
  { path: '/#/market/quotes', name: '市场行情', expected: 'ArtDecoMarketQuotes' },
  { path: '/#/stocks/management', name: '股票管理', expected: 'ArtDecoStockManagement' },
  { path: '/#/analysis/data', name: '投资分析', expected: 'ArtDecoDataAnalysis' },
  { path: '/#/risk/management', name: '风险管理', expected: 'ArtDecoRiskManagement' },
  { path: '/#/strategy/trading', name: '策略和交易管理', expected: 'ArtDecoTradingManagement' },
  { path: '/#/system/monitoring', name: '系统监控', expected: 'ArtDecoSettings' }
];

const BASE_URL = 'http://localhost:3001';

async function diagnosePage(browser, pageInfo) {
  const page = await browser.newPage();

  try {
    console.log(`\n🔍 诊断: ${pageInfo.name}`);
    console.log(`   路径: ${pageInfo.path}`);
    console.log(`   预期组件: ${pageInfo.expected}`);
    console.log(`   ${'='.repeat(60)}`);

    await page.goto(`${BASE_URL}${pageInfo.path}`, {
      waitUntil: 'domcontentloaded',
      timeout: 10000
    });

    await page.waitForTimeout(2000);

    // 获取页面标题
    const title = await page.title();
    console.log(`   📄 标题: ${title}`);

    // 检查Vue应用是否挂载
    const vueApp = await page.locator('#app').count();
    console.log(`   ✅ Vue应用挂载: ${vueApp > 0 ? '是' : '否'}`);

    // 检查ArtDecoLayout
    const artdecoLayout = await page.locator('.artdeco-layout, .layout-container').count();
    console.log(`   📐 ArtDecoLayout: ${artdecoLayout > 0 ? '发现' : '未发现'}`);

    // 检查侧边栏
    const sidebar = await page.locator('.layout-sidebar, aside').count();
    console.log(`   📋 侧边栏: ${sidebar > 0 ? '发现' : '未发现'}`);

    // 检查菜单链接
    const navLinks = await page.locator('.nav-link').count();
    console.log(`   🔗 菜单链接: ${navLinks} 个`);

    // 检查Header
    const header = await page.locator('.artdeco-header, header').count();
    console.log(`   🎨 Header: ${header > 0 ? '发现' : '未发现'}`);

    // 检查主内容区域
    const mainContent = await page.locator('.main-content, .content-area, main').count();
    console.log(`   📊 主内容区: ${mainContent > 0 ? '发现' : '未发现'}`);

    // 检查是否有Dashboard特定元素（仅Dashboard页面）
    if (pageInfo.expected === 'ArtDecoDashboard') {
      const dashboard = await page.locator('.artdeco-dashboard').count();
      console.log(`   🎯 Dashboard容器: ${dashboard > 0 ? '发现' : '未发现'}`);

      const statCards = await page.locator('.artdeco-stat-card, .stat-card').count();
      console.log(`   📈 统计卡片: ${statCards} 个`);
    }

    // 检查是否有内容卡片（ArtDecoCard）
    const cards = await page.locator('.artdeco-card, .card').count();
    console.log(`   🃏 内容卡片: ${cards} 个`);

    // 检查JavaScript错误
    const jsErrors = [];
    page.on('pageerror', error => {
      jsErrors.push(error.message);
    });

    await page.waitForTimeout(1000);

    if (jsErrors.length > 0) {
      console.log(`   ⚠️  JavaScript错误: ${jsErrors.length} 个`);
      jsErrors.slice(0, 3).forEach(err => console.log(`      - ${err.substring(0, 100)}...`));
    } else {
      console.log(`   ✅ 无JavaScript错误`);
    }

    // 获取页面HTML结构片段（前500字符）
    const bodyHTML = await page.locator('body').innerHTML();
    const cleanHTML = bodyHTML.replace(/\s+/g, ' ').substring(0, 500);
    console.log(`   🔍 HTML结构预览:`);
    console.log(`      ${cleanHTML}...`);

    // 判断页面是否正常工作
    const hasLayout = artdecoLayout > 0 || sidebar > 0;
    const hasMenu = navLinks > 0;
    const hasContent = mainContent > 0 || cards > 0;
    const noErrors = jsErrors.length === 0;

    const isHealthy = hasLayout && hasMenu && hasContent && noErrors;

    console.log(`   ${'='.repeat(60)}`);
    console.log(`   ${isHealthy ? '✅ 页面健康' : '⚠️  页面可能有问题'}`);

    return {
      name: pageInfo.name,
      path: pageInfo.path,
      expected: pageInfo.expected,
      title,
      isHealthy,
      hasLayout,
      hasMenu,
      hasContent,
      noErrors,
      jsErrors: jsErrors.length
    };
  } catch (error) {
    console.log(`   ❌ 错误: ${error.message}`);
    return {
      name: pageInfo.name,
      path: pageInfo.path,
      expected: pageInfo.expected,
      isHealthy: false,
      error: error.message
    };
  } finally {
    await page.close();
  }
}

async function main() {
  console.log('🔍 ArtDeco页面结构深度诊断');
  console.log(`基础URL: ${BASE_URL}`);
  console.log(`诊断时间: ${new Date().toISOString()}`);

  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
  } catch (error) {
    console.error('❌ 无法启动浏览器:', error.message);
    process.exit(1);
  }

  const results = [];

  for (const pageInfo of pages) {
    const result = await diagnosePage(browser, pageInfo);
    results.push(result);
    await new Promise(resolve => setTimeout(resolve, 500));
  }

  await browser.close();

  // 生成总结报告
  console.log('\n\n' + '='.repeat(70));
  console.log('📊 诊断总结报告');
  console.log('='.repeat(70));

  const healthy = results.filter(r => r.isHealthy).length;
  const unhealthy = results.filter(r => !r.isHealthy).length;

  console.log(`\n✅ 健康页面: ${healthy}/${results.length}`);
  console.log(`⚠️  问题页面: ${unhealthy}/${results.length}`);
  console.log(`📈 健康率: ${Math.round((healthy / results.length) * 100)}%`);

  console.log('\n📋 详细状态:');
  results.forEach(r => {
    const status = r.isHealthy ? '✅' : '⚠️';
    const details = r.isHealthy
      ? '正常运行'
      : r.error || '结构不完整';
    console.log(`  ${status} ${r.name}: ${details}`);
  });

  if (healthy === results.length) {
    console.log('\n🎉 所有ArtDeco页面诊断通过！系统运行正常。');
  } else {
    console.log('\n⚠️  部分页面需要进一步检查。');
  }

  process.exit(unhealthy > 0 ? 1 : 0);
}

main().catch(error => {
  console.error('❌ 诊断脚本执行失败:', error);
  process.exit(1);
});
