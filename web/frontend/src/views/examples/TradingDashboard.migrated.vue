<!--
  TradingDashboard.migrated.vue - 迁移示例

  这是一个迁移示例，展示如何将硬编码的API端点迁移到使用统一配置。

  原始文件: src/views/TradingDashboard.vue
  迁移方法: 参考本文件的注释和代码

  ⚠️ 这是一个示例文件，用于演示迁移方法
  实际迁移时，应该修改原始的 TradingDashboard.vue
-->
<template>
  <div class="trading-dashboard-migrated">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>交易仪表板（迁移示例）</span>
          <el-tag type="success" size="small">使用统一配置</el-tag>
        </div>
      </template>

      <!-- 控制面板 -->
      <div class="control-panel">
        <el-space>
          <el-button
            :type="isRunning ? 'danger' : 'primary'"
            @click="toggleTradingSession"
            :loading="loading"
          >
            {{ isRunning ? '停止交易' : '启动交易' }}
          </el-button>

          <el-button @click="loadAllData" :loading="loading">
            刷新数据
          </el-button>

          <el-button @click="showConfigInfo">
            查看配置
          </el-button>
        </el-space>
      </div>

      <!-- 状态显示 -->
      <div class="status-display">
        <el-descriptions :column="3" border>
          <el-descriptions-item label="交易状态">
            <el-tag :type="isRunning ? 'success' : 'info'">
              {{ isRunning ? '运行中' : '已停止' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="策略数量">
            {{ strategyPerformance?.length || 0 }}
          </el-descriptions-item>
          <el-descriptions-item label="风险等级">
            <el-tag :type="getRiskLevelType()">
              {{ getRiskLevelText() }}
            </el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </div>

      <!-- 数据展示区域 -->
      <el-tabs v-model="activeTab" class="data-tabs">
        <!-- 交易状态 -->
        <el-tab-pane label="交易状态" name="status">
          <el-card v-if="tradingData">
            <pre>{{ JSON.stringify(tradingData, null, 2) }}</pre>
          </el-card>
          <el-empty v-else description="暂无数据" />
        </el-tab-pane>

        <!-- 策略表现 -->
        <el-tab-pane label="策略表现" name="performance">
          <el-table :data="strategyPerformance" stripe>
            <el-table-column prop="strategy_id" label="策略ID" />
            <el-table-column prop="return_rate" label="收益率" />
            <el-table-column prop="sharpe_ratio" label="夏普比率" />
            <el-table-column prop="max_drawdown" label="最大回撤" />
          </el-table>
        </el-tab-pane>

        <!-- 市场快照 -->
        <el-tab-pane label="市场快照" name="market">
          <el-card v-if="marketData">
            <pre>{{ JSON.stringify(marketData, null, 2) }}</pre>
          </el-card>
          <el-empty v-else description="暂无数据" />
        </el-tab-pane>

        <!-- 风险指标 -->
        <el-tab-pane label="风险指标" name="risk">
          <el-card v-if="riskData">
            <pre>{{ JSON.stringify(riskData, null, 2) }}</pre>
          </el-card>
          <el-empty v-else description="暂无数据" />
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 配置信息对话框 -->
    <el-dialog v-model="configDialogVisible" title="统一配置信息" width="600px">
      <el-descriptions :column="1" border>
        <el-descriptions-item
          v-for="config in usedConfigs"
          :key="config.key"
          :label="config.key"
        >
          <div class="config-detail">
            <p><strong>端点:</strong> {{ config.endpoint }}</p>
            <p><strong>WebSocket:</strong> {{ config.wsChannel || '无需' }}</p>
            <p><strong>描述:</strong> {{ config.description }}</p>
          </div>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

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
type TradingRouteName = keyof typeof TRADING_PAGE_CONFIG
type TradingPageConfig = typeof TRADING_PAGE_CONFIG[TradingRouteName]

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
const tradingData = ref<any>(null)
const strategyPerformance = ref<any[]>([])
const marketData = ref<any>(null)
const riskData = ref<any>(null)

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
</script>

<style scoped>
.trading-dashboard-migrated {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.control-panel {
  margin-bottom: 20px;
}

.status-display {
  margin: 20px 0;
}

.data-tabs {
  margin-top: 20px;
}

pre {
  background-color: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  max-height: 400px;
}

.config-detail {
  margin-top: 10px;
}

.config-detail p {
  margin: 5px 0;
  font-size: 13px;
  color: #606266;
}
</style>

<!--
  ============================================================================
  迁移对比总结
  ============================================================================

  ❌ 迁移前（硬编码）:
  -----------------------
  const response = await axios.get('/api/trading/status')
  const perfResponse = await axios.get('/api/trading/strategies/performance')
  const marketResponse = await axios.get('/api/trading/market/snapshot')
  const riskResponse = await axios.get('/api/trading/risk/metrics')

  问题：
  - API端点硬编码在代码中
  - 修改端点需要搜索所有文件
  - 容易出现拼写错误
  - 无法集中管理

  ✅ 迁移后（统一配置）:
  -----------------------
  const config = getTradingConfig('trading-status')
  const response = await axios.get(config.apiEndpoint)

  优势：
  - API端点在配置中统一管理
  - 修改端点仅需更新配置文件
  - 类型安全，编译时检查错误
  - 易于维护和扩展

  ============================================================================
  迁移步骤
  ============================================================================

  步骤1: 扩展 PAGE_CONFIG
  ---------------------
  在 src/config/pageConfig.ts 中添加：

  export const PAGE_CONFIG = {
    // ... 现有8个路由

    // 新增：交易管理
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

  步骤2: 更新组件导入
  ---------------------
  import { getPageConfig, type RouteName } from '@/config/pageConfig'

  步骤3: 替换硬编码调用
  ---------------------
  // 从
  const response = await axios.get('/api/trading/status')

  // 改为
  const config = getPageConfig('trading-status')
  if (config) {
    const response = await axios.get(config.apiEndpoint)
  }

  步骤4: 验证
  -----------
  - 运行 TypeScript 编译检查
  - 手动测试所有功能
  - 确认无控制台错误

  ============================================================================
-->
