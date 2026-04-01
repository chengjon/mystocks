<template>
  <div class="strategy-builder">
    <el-card class="builder-card">
      <template #header>
        <div class="card-header">
          <span class="title">📊 策略构建器</span>
          <el-button type="primary" @click="handleRunStrategy" :loading="running">
            {{ running ? '运行中...' : '运行策略' }}
          </el-button>
        </div>
      </template>

      <!-- 策略配置 -->
      <el-form :model="strategyConfig" label-width="120px" class="config-form">
        <!-- 策略类型 -->
        <el-form-item label="策略类型">
          <el-select v-model="strategyConfig.type" placeholder="选择策略类型">
            <el-option label="动量策略" value="momentum"></el-option>
            <el-option label="均值回归" value="mean_reversion"></el-option>
            <el-option label="机器学习" value="ml"></el-option>
            <el-option label="自定义" value="custom"></el-option>
          </el-select>
        </el-form-item>

        <!-- 股票池 -->
        <el-form-item label="股票池">
          <el-select
            v-model="strategyConfig.universe"
            multiple
            filterable
            allow-create
            placeholder="输入或选择股票代码"
            class="full-width"
          >
            <el-option
              v-for="(symbol, _idx) in popularSymbols"
              :key="symbol"
              :label="symbol"
              :value="symbol"
            ></el-option>
          </el-select>
        </el-form-item>

        <!-- 参数配置 -->
        <el-form-item label="参数配置">
          <el-card shadow="never" class="params-card">
            <div v-if="strategyConfig.type === 'momentum'">
              <el-form-item label="短期均线">
                <el-input-number v-model="strategyConfig.params.ma_short" :min="1" :max="100"></el-input-number>
              </el-form-item>
              <el-form-item label="长期均线">
                <el-input-number v-model="strategyConfig.params.ma_long" :min="1" :max="200"></el-input-number>
              </el-form-item>
              <el-form-item label="RSI周期">
                <el-input-number v-model="strategyConfig.params.rsi_period" :min="1" :max="100"></el-input-number>
              </el-form-item>
            </div>

            <div v-else-if="strategyConfig.type === 'ml'">
              <el-form-item label="模型类型">
                <el-select v-model="strategyConfig.params.model_type">
                  <el-option label="随机森林" value="random_forest"></el-option>
                  <el-option label="梯度提升" value="gradient_boosting"></el-option>
                </el-select>
              </el-form-item>
              <el-form-item label="预测天数">
                <el-input-number v-model="strategyConfig.params.forward_days" :min="1" :max="30"></el-input-number>
              </el-form-item>
            </div>

            <div v-else>
              <el-alert
                title="请先选择策略类型"
                type="info"
                :closable="false"
                show-icon
              ></el-alert>
            </div>
          </el-card>
        </el-form-item>

        <!-- 回测配置 -->
        <el-form-item label="回测设置">
          <el-card shadow="never" class="params-card">
            <el-form-item label="起始资金">
              <el-input-number
                v-model="strategyConfig.backtest.initial_capital"
                :min="10000"
                :max="10000000"
                :step="10000"
              ></el-input-number>
            </el-form-item>
            <el-form-item label="手续费率">
              <el-input-number
                v-model="strategyConfig.backtest.commission"
                :min="0"
                :max="0.01"
                :step="0.0001"
                :precision="4"
              ></el-input-number>
            </el-form-item>
            <el-form-item label="滑点率">
              <el-input-number
                v-model="strategyConfig.backtest.slippage"
                :min="0"
                :max="0.01"
                :step="0.0001"
                :precision="4"
              ></el-input-number>
            </el-form-item>
          </el-card>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 结果展示 -->
    <el-card v-if="hasResults" class="results-card strategy-results-offset">
      <template #header>
        <span class="title">📈 回测结果</span>
      </template>

      <el-tabs v-model="activeTab">
        <!-- 性能指标 -->
        <el-tab-pane label="性能指标" name="performance">
          <el-row :gutter="20">
            <el-col :span="6" v-for="(metric, key) in performanceMetrics" :key="key">
              <el-statistic
                :title="metric.label"
                :value="metric.value"
                :precision="2"
                :suffix="metric.suffix"
              >
                <template #prefix>
                  <el-icon :class="metric.value > 0 ? 'strategy-state-positive' : 'strategy-state-negative'">
                    <component :is="metric.icon"></component>
                  </el-icon>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </el-tab-pane>

        <!-- 风险指标 -->
        <el-tab-pane label="风险指标" name="risk">
          <el-descriptions :column="2" border>
            <el-descriptions-item
              v-for="(metric, key) in riskMetrics"
              :key="key"
              :label="metric.label"
            >
              {{ metric.value }}{{ metric.suffix }}
            </el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>

        <!-- 交易记录 -->
        <el-tab-pane label="交易记录" name="trades">
          <el-table :data="trades" stripe class="strategy-trades-table">
            <el-table-column prop="date" label="日期" width="120"></el-table-column>
            <el-table-column prop="symbol" label="股票" width="100"></el-table-column>
            <el-table-column prop="action" label="操作" width="80">
              <template #default="scope">
                <el-tag :type="scope.row.action === 'buy' ? 'success' : 'danger'">
                  {{ scope.row.action === 'buy' ? '买入' : '卖出' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="price" label="价格" width="100"></el-table-column>
            <el-table-column prop="shares" label="数量" width="100"></el-table-column>
            <el-table-column prop="pnl" label="盈亏">
              <template #default="scope">
                <span :class="scope.row.pnl >= 0 ? 'strategy-state-positive' : 'strategy-state-negative'">
                  {{ scope.row.pnl >= 0 ? '+' : '' }}{{ scope.row.pnl.toFixed(2) }}%
                </span>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>

        <!-- 图表 -->
        <el-tab-pane label="可视化" name="charts">
          <div ref="chartContainer" class="strategy-chart-container"></div>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { _TrendChartUp, _TrendChartDown } from '@element-plus/icons-vue'
import axios from 'axios'

// 策略配置
const strategyConfig = reactive({
  type: 'momentum',
  universe: ['sh600000', 'sh600016', 'sh600036'],
  params: {
    ma_short: 5,
    ma_long: 20,
    rsi_period: 14,
    model_type: 'random_forest',
    forward_days: 1
  },
  backtest: {
    initial_capital: 1000000,
    commission: 0.0003,
    slippage: 0.0001
  }
})

// 常用股票列表
const popularSymbols = ref([
  'sh600000', 'sh600016', 'sh600036', 'sh600050',
  'sz000001', 'sz000002', 'sz000333', 'sz000651'
])

// 运行状态
const running = ref(false)
const hasResults = ref(false)
const activeTab = ref('performance')

// 结果数据
const backtest_results = ref(null)

// 性能指标
const performanceMetrics = computed(() => {
  if (!backtest_results.value) return {}

  const perf = backtest_results.value.performance || {}

  return {
    total_return: {
      label: '总收益率',
      value: (perf.total_return || 0) * 100,
      suffix: '%',
      icon: perf.total_return > 0 ? 'TrendChartUp' : 'TrendChartDown'
    },
    sharpe_ratio: {
      label: 'Sharpe比率',
      value: perf.sharpe_ratio || 0,
      suffix: '',
      icon: 'TrendChartUp'
    },
    max_drawdown: {
      label: '最大回撤',
      value: (perf.max_drawdown || 0) * 100,
      suffix: '%',
      icon: 'TrendChartDown'
    },
    win_rate: {
      label: '胜率',
      value: (perf.win_rate || 0) * 100,
      suffix: '%',
      icon: 'TrendChartUp'
    }
  }
})

// 风险指标
const riskMetrics = computed(() => {
  if (!backtest_results.value) return {}

  const risk = backtest_results.value.risk || {}

  return {
    var_95: {
      label: 'VaR (95%)',
      value: ((risk.var_95 || 0) * 100).toFixed(2),
      suffix: '%'
    },
    cvar_95: {
      label: 'CVaR (95%)',
      value: ((risk.cvar_95 || 0) * 100).toFixed(2),
      suffix: '%'
    },
    downside_deviation: {
      label: '下行偏差',
      value: ((risk.downside_deviation || 0) * 100).toFixed(2),
      suffix: '%'
    }
  }
})

// 交易记录
const trades = computed(() => {
  if (!backtest_results.value || !backtest_results.value.backtest) return []

  return backtest_results.value.backtest.trades || []
})

// 运行策略
const handleRunStrategy = async () => {
  running.value = true

  try {
    // 调用API运行策略
    const response = await axios.post('/api/quant/run-strategy', strategyConfig)

    backtest_results.value = response.data
    hasResults.value = true

    ElMessage.success('策略运行完成！')

  } catch (error) {
    console.error('运行策略失败:', error)
    ElMessage.error(error.response?.data?.message || '运行失败，请稍后重试')
  } finally {
    running.value = false
  }
}

</script>

<style scoped>
.strategy-builder {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.title {
  font-size: 18px;
  font-weight: bold;
}

.full-width {
  width: 100%;
}

.params-card {
  background-color: #f9f9f9;
}

.config-form {
  margin-top: 20px;
}

.results-card {
  animation: fade-in 0.5s;
}

.strategy-results-offset {
  margin-top: calc(var(--spacing-md) + var(--spacing-xs));
}

.strategy-trades-table {
  width: 100%;
}

.strategy-chart-container {
  width: 100%;
  height: calc(var(--spacing-3xl) * 7 + var(--spacing-xl) + var(--spacing-md) + var(--spacing-xs));
}

.strategy-state-positive {
  color: var(--color-success);
}

.strategy-state-negative {
  color: var(--color-danger);
}

@keyframes fade-in {
  from {
    opacity: 0%;
    transform: translateY(20px);
  }
  to {
    opacity: 100%;
    transform: translateY(0);
  }
}
</style>
