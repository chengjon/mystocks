/**
 * API版本协商功能测试
 */

// 测试版本协商器
async function testVersionNegotiation() {
  console.log('🧪 开始测试API版本协商功能...')

  try {
    // 动态导入版本协商器（模拟前端环境）
    const { versionNegotiator, checkApiCompatibility, getEndpointVersion } = await import('./services/versionNegotiator.js')

    // 测试1: 检查兼容性
    console.log('\n1️⃣ 测试版本兼容性检查...')
    const compatibility = checkApiCompatibility('/api/v1/market', '1.0.0')
    console.log('兼容性结果:', compatibility)

    // 测试2: 获取端点版本
    console.log('\n2️⃣ 测试端点版本获取...')
    const endpointVersion = getEndpointVersion('/api/v1/market')
    console.log('端点版本:', endpointVersion)

    // 测试3: 执行版本协商
    console.log('\n3️⃣ 测试版本协商...')
    const negotiationResult = await versionNegotiator.negotiateVersion('/api/v1/market', '1.0.0')
    console.log('协商结果:', negotiationResult)

    // 测试4: 获取版本摘要
    console.log('\n4️⃣ 测试版本摘要...')
    const summary = versionNegotiator.getVersionSummary()
    console.log('版本摘要:', summary)

    console.log('\n✅ API版本协商功能测试完成!')
    return true

  } catch (error) {
    console.error('❌ API版本协商功能测试失败:', error)
    return false
  }
}

// 如果直接运行此文件，执行测试
if (typeof window === 'undefined') {
  // Node.js环境
  testVersionNegotiation().then(success => {
    process.exit(success ? 0 : 1)
  })
} else {
  // 浏览器环境
  window.testVersionNegotiation = testVersionNegotiation
}