/**
 * MyStocks E2E测试全局设置
 */

async function globalSetup(config) {
  console.log('🚀 开始MyStocks E2E测试全局设置...');

  // 验证测试环境
  console.log('📡 验证测试环境连接...');

  // Per CLAUDE.md port allocation: Frontend 3020-3029, Backend 8020-8029
  const frontendUrl = process.env.BASE_URL || 'http://localhost:3020';
  const backendUrl = process.env.API_URL || 'http://localhost:8020';

  try {
    // 检查前端服务器
    const frontendResponse = await fetch(frontendUrl);
    console.log(`✅ 前端服务器连接正常: ${frontendResponse.status}`);

    // 检查后端服务器
    const backendResponse = await fetch(backendUrl);
    console.log(`✅ 后端服务器连接正常: ${backendResponse.status}`);

  } catch (error) {
    console.error('❌ 服务器连接检查失败:', error.message);
    throw new Error('测试环境连接失败，请确保服务器正常运行');
  }

  console.log('✅ 全局设置完成');
}

export default globalSetup;
