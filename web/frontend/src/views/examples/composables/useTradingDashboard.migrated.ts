import { ref, _computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
type TradingRouteName = keyof typeof TRADING_PAGE_CONFIG
type TradingPageConfig = typeof TRADING_PAGE_CONFIG[TradingRouteName]

export function useTradingDashboard.migrated() {

// ====================================================================
// ❌ 迁移前：硬编码API端点（不推荐）
// ====================================================================
/*
const HARDCODED_API = {
  START: '/api/trading/start',
  STOP: '/api/trading/stop',
  STATUS: '/api/trading/status',
  PERFORMANCE: '/api/trading/strategies/performance',
  MARKET: '/api/trading/market/snapshot',
  RISK: '/api/trading/risk/metrics',
  ADD_STRATEGY: '/api/trading/strategies/add'
}

// 使用硬编码的代码：
// const response = await axios.post(HARDCODED_API.START)
*/

// ====================================================================
// ✅ 迁移后：使用统一配置（推荐）
// ====================================================================

/**
 * 交易路由配置（模拟扩展后的PAGE_CONFIG）
 *
 * 实际使用时，这些配置应该在 src/config/pageConfig.ts 中
 * 这里为了示例完整性，定义在本地
 */
const TRADING_PAGE_CONFIG = {
  'trading-status': {
    apiEndpoint: '/api/trading/status',
    wsChannel: 'trading:status',
    realtime: true,
    description: '交易状态查询'
  },
  'trading-performance': {
    apiEndpoint: '/api/trading/strategies/performance',
    wsChannel: 'trading:performance',
    realtime: true,
    description: '策略表现分析'
  },
  'trading-market': {
    apiEndpoint: '/api/trading/market/snapshot',
    wsChannel: 'trading:market',
    realtime: true,
    description: '交易市场快照'
  },
  'trading-risk': {
    apiEndpoint: '/api/trading/risk/metrics',
    wsChannel: 'trading:risk',
    realtime: true,
    description: '交易风险指标'
  }
} as const

// 类型定义

/**
 * 获取交易配置（类型安全）
 */
function getTradingConfig(routeName: TradingRouteName): TradingPageConfig {
  return TRADING_PAGE_CONFIG[routeName]
}

// ====================================================================
// 组件逻辑
// ====================================================================

// 状态
const isRunning = ref(false)
const loading = ref(false)
const activeTab = ref('status')
const configDialogVisible = ref(false)

// 数据
const tradingData = ref<unknown>(null)
const strategyPerformance = ref<unknown[]>([])
const marketData = ref<unknown>(null)
const riskData = ref<unknown>(null)

// 记录使用的配置（用于展示）
const usedConfigs = ref<Array<{
  key: string
  endpoint: string
  wsChannel: string | null
  description: string
}>>([])

/**
 * ✅ 迁移后：使用统一配置获取交易状态
 */
const loadTradingData = async () => {
  loading.value = true

  try {
    // ✅ 使用统一配置（无硬编码）
    const config = getTradingConfig('trading-status')
    const response = await axios.get(config.apiEndpoint)

    tradingData.value = response.data
    usedConfigs.value.push({
      key: 'trading-status',
      endpoint: config.apiEndpoint,
      wsChannel: config.wsChannel,
      description: config.description
    })

    console.log(`✅ 使用配置加载: ${config.description}`)
  } catch (error) {
    console.error('加载交易状态失败:', error)
    ElMessage.error('加载交易状态失败')
  } finally {
    loading.value = false
  }
}

/**
 * ✅ 迁移后：使用统一配置获取策略表现
 */
const loadStrategyPerformance = async () => {
  loading.value = true

  try {
    // ✅ 使用统一配置
    const config = getTradingConfig('trading-performance')
    const response = await axios.get(config.apiEndpoint)

    strategyPerformance.value = response.data.strategies || []
    usedConfigs.value.push({
      key: 'trading-performance',
      endpoint: config.apiEndpoint,
      wsChannel: config.wsChannel,
      description: config.description
    })

    console.log(`✅ 使用配置加载: ${config.description}`)
  } catch (error) {
    console.error('加载策略表现失败:', error)
    ElMessage.error('加载策略表现失败')
  } finally {
    loading.value = false
  }
}

/**
 * ✅ 迁移后：使用统一配置获取市场快照
 */
const loadMarketData = async () => {
  loading.value = true

  try {
    // ✅ 使用统一配置
    const config = getTradingConfig('trading-market')
    const response = await axios.get(config.apiEndpoint)

    marketData.value = response.data
    usedConfigs.value.push({
      key: 'trading-market',
      endpoint: config.apiEndpoint,
      wsChannel: config.wsChannel,
      description: config.description
    })

    console.log(`✅ 使用配置加载: ${config.description}`)
  } catch (error) {
    console.error('加载市场快照失败:', error)
    ElMessage.error('加载市场快照失败')
  } finally {
    loading.value = false
  }
}

/**
 * ✅ 迁移后：使用统一配置获取风险指标
 */
const loadRiskData = async () => {
  loading.value = true

  try {
    // ✅ 使用统一配置
    const config = getTradingConfig('trading-risk')
    const response = await axios.get(config.apiEndpoint)

    riskData.value = response.data
    usedConfigs.value.push({
      key: 'trading-risk',
      endpoint: config.apiEndpoint,
      wsChannel: config.wsChannel,
      description: config.description
    })

    console.log(`✅ 使用配置加载: ${config.description}`)
  } catch (error) {
    console.error('加载风险指标失败:', error)
    ElMessage.error('加载风险指标失败')
  } finally {
    loading.value = false
  }
}

/**
 * 切换交易会话状态
 */
const toggleTradingSession = async () => {
  loading.value = true

  try {
    if (isRunning.value) {
      // 停止交易（API不在配置中，这是操作而非查询）
      await axios.post('/api/trading/stop')
      ElMessage.success('交易会话已停止')
      isRunning.value = false
    } else {
      // 启动交易
      await axios.post('/api/trading/start')
      ElMessage.success('交易会话已启动')
      isRunning.value = true
    }

    // 重新加载数据
    await loadAllData()
  } catch (error) {
    console.error('切换交易会话失败:', error)
    ElMessage.error('操作失败')
  } finally {
    loading.value = false
  }
}

/**
 * 加载所有数据
 */
const loadAllData = async () => {
  await Promise.all([
    loadTradingData(),
    loadStrategyPerformance(),
    loadMarketData(),
    loadRiskData()
  ])
}

/**
 * 显示配置信息
 */
const showConfigInfo = () => {
  configDialogVisible.value = true
}

/**
 * 获取风险等级类型
 */
const getRiskLevelType = () => {
  if (!riskData.value) return 'info'

  const riskScore = riskData.value.risk_score || 0
  if (riskScore < 30) return 'success'
  if (riskScore < 70) return 'warning'
  return 'danger'
}

/**
 * 获取风险等级文本
 */
const getRiskLevelText = () => {
  if (!riskData.value) return '未知'

  const riskScore = riskData.value.risk_score || 0
  if (riskScore < 30) return '低风险'
  if (riskScore < 70) return '中等风险'
  return '高风险'
}

// 组件挂载时加载数据
onMounted(() => {
  console.log('🚀 交易仪表板（迁移示例）已挂载')
  console.log('📋 使用统一配置管理API端点')
})

  return {
    HARDCODED_API,
    TRADING_PAGE_CONFIG,
    getTradingConfig,
    isRunning,
    loading,
    activeTab,
    configDialogVisible,
    tradingData,
    strategyPerformance,
    marketData,
    riskData,
    usedConfigs,
    loadTradingData,
    config,
    response,
    loadStrategyPerformance,
    config,
    response,
    loadMarketData,
    config,
    response,
    loadRiskData,
    config,
    response,
    toggleTradingSession,
    loadAllData,
    showConfigInfo,
    getRiskLevelType,
    riskScore,
    getRiskLevelText,
    riskScore,
  }
}
