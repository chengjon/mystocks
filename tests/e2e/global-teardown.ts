/**
 * MyStocks E2E测试全局清理
 */

async function globalTeardown(config) {
  console.log('🧹 开始MyStocks E2E测试全局清理...');

  // 清理测试资源
  console.log('✅ 全局清理完成');
}

export default globalTeardown;
