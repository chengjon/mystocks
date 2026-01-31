#!/usr/bin/env node
/**
 * ArtDeco页面快速验证脚本
 */

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

async function checkPage(page, pageInfo) {
  try {
    const response = await fetch(`${BASE_URL}${pageInfo.path}`);

    if (response.ok) {
      const html = await response.text();

      // 检查关键ArtDeco元素
      const hasDashboard = html.includes('artdeco-dashboard');
      const hasHeader = html.includes('artdeco-header');
      const hasLayout = html.includes('layout-sidebar');
      const hasMenu = html.includes('nav-link') || html.includes('nav-item');

      const allPresent = hasDashboard && hasHeader && hasLayout && hasMenu;

      return {
        name: pageInfo.name,
        status: allPresent ? '✅ PASS' : '⚠️ PARTIAL',
        hasDashboard,
        hasHeader,
        hasLayout,
        hasMenu,
        httpStatus: response.status
      };
    } else {
      return {
        name: pageInfo.name,
        status: '❌ FAIL',
        httpStatus: response.status,
        error: response.statusText
      };
    }
  } catch (error) {
    return {
      name: pageInfo.name,
      status: '❌ ERROR',
      error: error.message
    };
  }
}

async function main() {
  console.log('🔍 ArtDeco页面验证开始...\n');
  console.log(`基础URL: ${BASE_URL}\n`);

  const results = [];

  for (const pageInfo of pages) {
    const result = await checkPage(pageInfo, pageInfo);
    results.push(result);

    const status = result.status.padEnd(8);
    const details = result.hasDashboard ? 'Dashboard' :
                    result.hasHeader ? 'Header' :
                    result.hasLayout ? 'Layout' :
                    result.hasMenu ? 'Menu' : 'Unknown';

    console.log(`${status} ${result.name}`);
    if (result.error) {
      console.log(`       错误: ${result.error}`);
    }
  }

  console.log('\n📊 验证结果汇总:');
  const passed = results.filter(r => r.status === '✅ PASS').length;
  const failed = results.filter(r => r.status.includes('❌')).length;
  const partial = results.filter(r => r.status.includes('⚠️')).length;

  console.log(`  ✅ 通过: ${passed}`);
  console.log(`  ⚠️  部分通过: ${partial}`);
  console.log(`  ❌ 失败: ${failed}`);
  console.log(`  📈 通过率: ${Math.round((passed / results.length) * 100)}%`);

  if (passed === results.length) {
    console.log('\n🎉 所有ArtDeco页面验证通过！系统运行正常。');
  } else if (failed > 0) {
    console.log('\n⚠️  部分页面验证失败，建议检查服务器状态。');
  }

  process.exit(failed > 0 ? 1 : 0);
}

main().catch(error => {
  console.error('❌ 验证脚本执行失败:', error);
  process.exit(1);
});
