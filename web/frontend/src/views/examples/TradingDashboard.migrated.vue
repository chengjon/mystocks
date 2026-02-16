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
          v-for="(config, _idx) in usedConfigs"
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
import { useTradingDashboardMigrated } from './composables/useTradingDashboard.migrated'

const { TRADING_PAGE_CONFIG, getTradingConfig, isRunning, loading, activeTab, configDialogVisible, tradingData, strategyPerformance, marketData, riskData, usedConfigs, loadTradingData, loadStrategyPerformance, loadMarketData, loadRiskData, toggleTradingSession, loadAllData, showConfigInfo, getRiskLevelType, getRiskLevelText } = useTradingDashboardMigrated()
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
