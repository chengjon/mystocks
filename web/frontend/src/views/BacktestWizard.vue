<template>
  <div class="backtest-wizard layout-compact">
    <!-- ArtDeco Header -->
    <div class="wizard-header">
      <h1 class="page-title">STRATEGY BACKTESTING WIZARD</h1>
      <p class="page-subtitle">向导式策略回测流程</p>
    </div>

    <!-- Progress Indicator -->
    <div class="wizard-progress">
      <div
        v-for="(step, index) in wizardSteps"
        :key="step.id"
        :class="['step-item', { active: currentStep === index, completed: currentStep > index }]"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-label">{{ step.label }}</div>
      </div>
    </div>

    <!-- Step Content -->
    <div class="wizard-content">
        <!-- Step 1: Select Strategy Template -->
      <div v-if="currentStep === 0" class="step-content">
        <ArtDecoCardCompact>
          <template #header>
            <h3>选择策略模板</h3>
          </template>
          <div class="strategy-selection-container">
            <!-- Quick Templates -->
            <div class="quick-templates-section">
              <h4 class="section-title">快速模板</h4>
              <div class="strategy-grid">
                <div
                  v-for="template in quickTemplates"
                  :key="template.id"
                  :class="['strategy-card', { selected: selectedStrategy === template.id }]"
                  @click="selectStrategy(template.id)"
                >
                  <div class="strategy-icon">
                    <el-icon size="32"><TrendCharts /></el-icon>
                  </div>
                  <div class="strategy-info">
                    <div class="strategy-name">{{ template.name }}</div>
                    <div class="strategy-desc">{{ template.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- My Templates -->
            <div v-if="customTemplates.length > 0" class="my-templates-section">
              <h4 class="section-title">历史模板</h4>
              <div class="strategy-grid">
                <div
                  v-for="template in customTemplates"
                  :key="template.id"
                  :class="['strategy-card', { selected: selectedStrategy === template.id }]"
                  @click="selectStrategy(template.id)"
                >
                  <div class="strategy-icon">
                    <el-icon size="32"><FolderOpened /></el-icon>
                  </div>
                  <div class="strategy-info">
                    <div class="strategy-name">{{ template.name }}</div>
                    <div class="strategy-desc">{{ template.description }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Save Template Button -->
            <el-button @click="showSaveTemplateDialog" class="artdeco-gold-cta">
              <el-icon><Plus /> 保存模板
            </el-button>
          </div>
        </ArtDecoCardCompact>
      </div>
              <div class="strategy-info">
                <div class="strategy-name">{{ template.name }}</div>
                <div class="strategy-desc">{{ template.description }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Step 2.5: Compare Parameters -->
    <div v-if="currentStep === 2.5" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>参数对比与选择</h3>
        </template>
        <div class="compare-selection">
          <div class="selection-item">
            <label>选择回测1：</label>
            <el-select v-model="selectedBacktest1" placeholder="请选择回测1" filterable>
              <el-option
                v-for="bt in backtestHistory"
                :key="bt.id"
                :label="bt.name"
                :value="bt.id"
              >
                {{ bt.name }}
              </el-option>
            </el-select>
          </div>

          <div class="selection-item">
            <label>选择回测2：</label>
            <el-select v-model="selectedBacktest2" placeholder="请选择回测2" filterable>
              <el-option
                v-for="bt in backtestHistory"
                :key="bt.id"
                :label="bt.name"
                :value="bt.id"
              >
                {{ bt.name }}
              </el-option>
              <el-option
                v-for="template in strategyTemplates"
                :key="template.id"
                :label="template.name"
                :value="template.id"
              >
                {{ template.name }}
              </el-option>
              </el-select>
          </div>
        </div>
      </ArtDecoCardCompact>
    </div>
  </div>

    <!-- Step 2.5: Compare Parameters -->
    <div v-if="currentStep === 2.5" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>参数对比与选择</h3>
        </template>
        <div class="compare-selection">
          <div class="selection-item">
            <label>选择回测1：</label>
            <el-select v-model="selectedBacktest1" placeholder="请选择回测1" filterable>
              <el-option
                v-for="bt in backtestHistory"
                :key="bt.id"
                :label="bt.name"
                :value="bt.id"
              >
                {{ bt.name }}
              </el-option>
            </el-select>
          </div>
          <div class="selection-item">
            <label>选择回测2：</label>
            <el-select v-model="selectedBacktest2" placeholder="请选择回测2" filterable>
              <el-option
                v-for="bt in backtestHistory"
                :key="bt.id"
                :label="bt.name"
                :value="bt.id"
              >
                {{ bt.name }}
              </el-option>
          </div>
        </div>

        <!-- Comparison Table -->
        <div class="comparison-table-container">
          <el-table :data="comparisonData" border stripe>
            <el-table-column prop="param" label="参数" width="180" />
            <el-table-column prop="backtest1Value" label="回测1" width="120" />
            <el-table-column prop="backtest2Value" label="回测2" width="120" />
            <el-table-column prop="difference" label="差异" width="100">
              <template #default="scope">
                <span :class="['diff-value', { 'diff-better': row.highlight && row.difference > 0, 'diff-worse': row.difference < 0 }]">
                  {{ row.value }}
                </span>
              </template>
          </el-table-column>
        </el-table>
      </div>
      </ArtDecoCardCompact>
    </div>

    <!-- Step 3: Review and Run -->
    <div v-if="currentStep === 2" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>确认回测配置</h3>
        </template>
        <div class="review-content">
          <div class="review-item">
            <span class="review-label">策略模板：</span>
            <span class="review-value">{{ getSelectedStrategyName() }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">短期MA周期：</span>
            <span class="review-value">{{ backtestParams.shortMA }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">长期MA周期：</span>
            <span class="review-value">{{ backtestParams.longMA }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">开始日期：</span>
            <span class="review-value">{{ formatDate(backtestParams.startDate) }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">结束日期：</span>
            <span class="review-value">{{ formatDate(backtestParams.endDate) }}</span>
          </div>
          <div class="review-item">
            <span class="review-label">股票代码：</span>
            <span class="review-value">{{ backtestParams.symbols }}</span>
          </div>
        </div>
      </ArtDecoCardCompact>
    </div>

    <!-- Step 4: Results -->
    <div v-if="currentStep === 3" class="step-content">
      <ArtDecoCardCompact>
        <template #header>
          <h3>回测结果</h3>
        </template>
        <div class="results-content">
          <!-- Metrics -->
          <div class="results-metrics">
            <div class="metric-card">
              <div class="metric-label">总收益率</div>
              <div class="metric-value change-up">{{ backtestResults.totalReturn }}%</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">夏普比率</div>
              <div class="metric-value">{{ backtestResults.sharpeRatio }}</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">最大回撤</div>
              <div class="metric-value change-down">{{ backtestResults.maxDrawdown }}%</div>
            </div>
            <div class="metric-card">
              <div class="metric-label">胜率</div>
              <div class="metric-value">{{ backtestResults.winRate }}%</div>
            </div>
          </div>

          <!-- Chart -->
          <div ref="backtestChartRef" class="backtest-chart"></div>
        </div>
      </ArtDecoCardCompact>
    </div>

    <!-- Navigation Buttons -->
    <div class="wizard-navigation">
      <el-button
        v-if="currentStep > 0"
        @click="prevStep"
        class="artdeco-gold-cta"
        plain
      >
        上一步
      </el-button>
      <el-button
        v-if="currentStep < 4"
        @click="nextStep"
        class="artdeco-gold-cta"
        :disabled="!canProceed"
      >
        {{ currentStep === 2.5 ? '开始对比' : '下一步' }}
      </el-button>
      <el-button
        v-if="currentStep === 3"
        @click="resetWizard"
        class="artdeco-gold-cta"
        plain
      >
        重新开始
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { artDecoTheme } from '@/utils/echarts'
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'
import { TrendCharts } from '@element-plus/icons-vue'

// Wizard steps
const wizardSteps = [
  { id: 'select', label: '选择策略' },
  { id: 'configure', label: '配置参数' },
  { id: 'review', label: '确认配置' },
  { id: 'compare', label: '参数对比' },
  { id: 'results', label: '查看结果' }
]

const currentStep = ref(0)
const selectedStrategy = ref('')

// Quick templates (system built-in)
const quickTemplates = ref<StrategyTemplate[]>([
  {
    id: 'ma_cross',
    name: '均线交叉策略',
    description: '基于短期和长期均线的交叉信号进行买卖',
    defaultParams: { shortMA: 5, longMA: 20 }
  },
  {
    id: 'rsi',
    name: 'RSI策略',
    description: '基于相对强弱指标的买卖信号',
    defaultParams: { rsiPeriod: 14, overbought: 70, oversold: 30 }
  },
  {
    id: 'bollinger',
    name: '布林带策略',
    description: '基于价格与布林带的关系进行交易',
    defaultParams: { period: 20, stdDev: 2 }
  },
  {
    id: 'volume',
    name: '量价策略',
    description: '结合成交量和价格变化进行交易',
    defaultParams: { volumeThreshold: 1.5, priceChange: 2 }
  }
])

// Custom templates (user saved)
const customTemplates = ref<StrategyTemplate[]>([])

// Save template dialog
const showSaveTemplateDialog = ref(false)

// Strategy templates
interface StrategyTemplate {
  id: string
  name: string
  description: string
  defaultParams: Record<string, any>
}

const strategyTemplates: StrategyTemplate[] = [
  {
    id: 'ma_cross',
    name: '均线交叉策略',
    description: '基于短期和长期均线的交叉信号进行买卖',
    defaultParams: { shortMA: 5, longMA: 20 }
  },
  {
    id: 'rsi',
    name: 'RSI策略',
    description: '基于相对强弱指标的买卖信号',
    defaultParams: { rsiPeriod: 14, overbought: 70, oversold: 30 }
  },
  {
    id: 'bollinger',
    name: '布林带策略',
    description: '基于价格与布林带的关系进行交易',
    defaultParams: { period: 20, stdDev: 2 }
  },
  {
    id: 'volume',
    name: '量价策略',
    description: '结合成交量和价格变化进行交易',
    defaultParams: { volumeThreshold: 1.5, priceChange: 2 }
  },
  {
    id: 'macd',
    name: 'MACD策略',
    description: 'MACD指标与信号线的金叉策略',
    defaultParams: { shortMA: 12, longMA: 26, signalMA: 9 }
  },
  {
    id: 'kdj',
    name: 'KDJ策略',
    description: '随机指标与慢速线的金叉策略',
    defaultParams: { k: 9, d: 3, j: 3 }
  },
  {
    id: 'stochastic',
    name: 'StochRSI策略',
    description: '随机指标与KD线的金叉策略',
    defaultParams: { k: 14, d: 3, j: 3 }
  },
  {
    id: 'cci',
    name: 'CCI策略',
    description: '顺势指标与正负区间的交叉策略',
    defaultParams: { period: 20, overbought: 100, oversold: -100 }
  },
  {
    id: 'atr',
    name: 'ATR策略',
    description: '基于平均真实波幅的止损策略',
    defaultParams: { period: 14, multiplier: 2 }
  }
]

// Backtest parameters
const backtestParams = ref({
  shortMA: 5,
  longMA: 20,
  startDate: new Date('2024-01-01'),
  endDate: new Date(),
  symbols: '600000'
})

// Backtest results
const backtestResults = ref({
  totalReturn: 15.5,
  sharpeRatio: 1.8,
  maxDrawdown: -8.5,
  winRate: 62.5
})

// Comparison backtests history
interface BacktestHistoryItem {
  id: string
  name: string
  strategyName: string
  totalReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  runAt: string
  params: Record<string, any>
}

const backtestHistory = ref<BacktestHistoryItem[]>([
  {
    id: 'bt-001',
    name: '当前策略',
    strategyName: '均线交叉策略',
    totalReturn: 15.5,
    sharpeRatio: 1.8,
    maxDrawdown: -8.5,
    winRate: 62.5,
    runAt: '2025-01-25 10:00:00',
    params: { shortMA: 5, longMA: 20 }
  }
])

// Selected backtests for comparison
const selectedBacktest1 = ref('')
const selectedBacktest2 = ref('')

// Comparison backtests interface
interface BacktestComparison {
  backtest1: string
  backtest2: string
  diffData: Array<{
    param: string
    value1: number
    value2: number
    difference: number
    highlight: boolean
  }>
}

const comparisonData = computed<BacktestComparison>(() => {
  if (!selectedBacktest1.value || !selectedBacktest2.value) {
    return []
  }

  const bt1 = backtestHistory.value.find(bt => bt.id === selectedBacktest1.value)
  const bt2 = backtestHistory.value.find(bt => bt.id === selectedBacktest2.value)

  if (!bt1 || !bt2) {
    return []
  }

  return [
    {
      param: '短期MA周期',
      value1: bt1?.params.shortMA || 0,
      value2: bt2?.params.shortMA || 0,
      difference: (bt1?.params.shortMA || 0) - (bt2?.params.shortMA || 0),
      highlight: bt1?.params.shortMA !== bt2?.params.shortMA
    },
    {
      param: '长期MA周期',
      value1: bt1?.params.longMA || 0,
      value2: bt2?.params.longMA || 0,
      difference: (bt1?.params.longMA || 0) - (bt2?.params.longMA || 0),
      highlight: bt1?.params.longMA !== bt2?.params.longMA
    },
    {
      param: '开始日期',
      value1: new Date(bt1?.runAt).toLocaleDateString('zh-CN'),
      value2: new Date(bt2?.runAt).toLocaleDateString('zh-CN'),
      difference: 'N/A',
      highlight: false
    },
    {
      param: '结束日期',
      value1: new Date(bt1?.runAt).toLocaleDateString('zh-CN'),
      value2: new Date(bt2?.runAt).toLocaleDateString('zh-CN'),
      difference: 'N/A',
      highlight: false
    },
    {
      param: '总收益率',
      value1: bt1?.totalReturn || 0,
      value2: bt2?.totalReturn || 0,
      difference: (bt1?.totalReturn || 0) - (bt2?.totalReturn || 0),
      highlight: bt1?.totalReturn > bt2?.totalReturn
    },
    {
      param: '夏普比率',
      value1: bt1?.sharpeRatio || 0,
      value2: bt2?.sharpeRatio || 0,
      difference: (bt1?.sharpeRatio || 0) - (bt2?.sharpeRatio || 0),
      highlight: bt1?.sharpeRatio > bt2?.sharpeRatio
    },
    {
      param: '最大回撤',
      value1: bt1?.maxDrawdown || 0,
      value2: bt2?.maxDrawdown || 0,
      difference: (bt1?.maxDrawdown || 0) - (bt2?.maxDrawdown || 0),
      highlight: bt1?.maxDrawdown < bt2?.maxDrawdown
    },
    {
      param: '胜率',
      value1: bt1?.winRate || 0,
      value2: bt2?.winRate || 0,
      difference: (bt1?.winRate || 0) - (bt2?.winRate || 0),
      highlight: bt1?.winRate > bt2?.winRate
    }
  ]
})

// Chart reference
const backtestChartRef = ref<HTMLElement>()
let backtestChart: any = null

// Computed: can proceed to next step
const canProceed = computed(() => {
  if (currentStep.value === 0) {
    return selectedStrategy.value !== ''
  }
  if (currentStep.value === 1) {
    return backtestParams.value.startDate && backtestParams.value.endDate
  }
  if (currentStep.value === 2) {
    return selectedBacktest1.value && selectedBacktest2.value
  }
  if (currentStep.value === 3) {
    return true
  }
  return false
})

// Actions
const selectStrategy = (strategyId: string) => {
  selectedStrategy.value = strategyId
  const template = strategyTemplates.find(t => t.id === strategyId)
  if (template) {
    backtestParams.value = {
      ...backtestParams.value,
      ...template.defaultParams
    }
  }
}

const nextStep = async () => {
  if (currentStep.value === 2) {
    // Run backtest
    ElMessage.info('正在运行回测...')
    await new Promise(resolve => setTimeout(resolve, 2000)) // Simulate
    ElMessage.success('回测完成')
    initBacktestChart()
  }
  currentStep.value++
}

const prevStep = () => {
  if (currentStep.value > 0) {
    currentStep.value--
  }
}

const resetWizard = () => {
  currentStep.value = 0
  selectedStrategy.value = ''
  backtestResults.value = {
    totalReturn: 15.5,
    sharpeRatio: 1.8,
    maxDrawdown: -8.5,
    winRate: 62.5
  }
}

const getSelectedStrategyName = () => {
  const template = strategyTemplates.find(t => t.id === selectedStrategy.value)
  return template ? template.name : ''
}

const formatDate = (date: Date) => {
  return date.toLocaleDateString('zh-CN')
}

const initBacktestChart = () => {
  if (backtestChartRef.value) {
    backtestChart = echarts.init(backtestChartRef.value, artDecoTheme)
    const option = {
      backgroundColor: 'transparent',
      xAxis: {
        type: 'category',
        data: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05']
      },
      yAxis: {
        type: 'value',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        type: 'line',
        name: '累计收益率',
        data: [0, 5, 8, 12, 15.5],
        lineStyle: {
          width: 2,
          color: '#D4AF37'
        },
        areaStyle: {
          color: 'rgba(212, 175, 55, 0.1)'
        }
      }]
    }
    backtestChart.setOption(option)
  }
}

onMounted(() => {
  if (currentStep.value === 3) {
    initBacktestChart()
  }
})

onBeforeUnmount(() => {
  if (backtestChart) {
    backtestChart.dispose()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/artdeco-tokens.scss';

.backtest-wizard {
  min-height: 100vh;
  padding: var(--artdeco-spacing-4);
  background-color: var(--artdeco-bg-global);
}

.wizard-header {
  text-align: center;
  padding: var(--artdeco-spacing-4) 0;
  border-bottom: 2px solid var(--artdeco-border-gold);
  margin-bottom: var(--artdeco-spacing-4);
  background: var(--artdeco-bg-elevated);

  .page-title {
    font-family: var(--font-display);
    font-weight: 700;
    color: var(--artdeco-gold-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0 0 var(--artdeco-spacing-2) 0;
    font-size: var(--artdeco-text-3xl);
  }

  .page-subtitle {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    margin: 0;
  }
}

.wizard-progress {
  display: flex;
  justify-content: center;
  gap: var(--artdeco-spacing-4);
  padding: var(--artdeco-spacing-4);
  margin-bottom: var(--artdeco-spacing-4);
  border-bottom: 1px solid var(--artdeco-border-default);

  .step-item {
    display: flex;
    align-items: center;
    gap: var(--artdeco-spacing-2);

    .step-number {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      background: var(--artdeco-bg-elevated);
      border: 2px solid var(--artdeco-border-default);
      display: flex;
      align-items: center;
      justify-content: center;
      font-family: var(--font-display);
      font-weight: 700;
      color: var(--artdeco-fg-muted);
      transition: all var(--artdeco-transition-base);
    }

    .step-label {
      font-family: var(--font-body);
      font-size: var(--artdeco-text-sm);
      color: var(--artdeco-fg-muted);
    }

    &.active {
      .step-number {
        background: var(--artdeco-gold-primary);
        border-color: var(--artdeco-border-gold);
        color: var(--artdeco-bg-global);
      }

      .step-label {
        color: var(--artdeco-gold-primary);
        font-weight: 600;
      }
    }

    &.completed {
      .step-number {
        background: var(--artdeco-eco-green);
        border-color: var(--artdeco-eco-green);
        color: white;
      }
    }
  }
}

.wizard-content {
  min-height: 500px;
  padding: var(--artdeco-spacing-4);
}

.wizard-navigation {
  display: flex;
  justify-content: center;
  gap: var(--artdeco-spacing-2);
  padding: var(--artdeco-spacing-4);
  border-top: 1px solid var(--artdeco-border-default);
}

// Strategy Grid
.strategy-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: var(--artdeco-spacing-3);
}

.strategy-card {
  padding: var(--artdeco-spacing-3);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  cursor: pointer;
  transition: all var(--artdeco-transition-base);

  &:hover {
    border-color: var(--artdeco-border-gold);
    box-shadow: var(--artdeco-shadow-md), var(--artdeco-glow-subtle);
    transform: translateY(-4px);
  }

  &.selected {
    border-color: var(--artdeco-border-gold);
    background: rgba(212, 175, 55, 0.05);
  }

  .strategy-icon {
    font-size: var(--artdeco-text-2xl);
    color: var(--artdeco-gold-primary);
    margin-bottom: var(--artdeco-spacing-2);
  }

  .strategy-name {
    font-family: var(--font-display);
    font-weight: 600;
    color: var(--artdeco-fg-default);
    margin-bottom: var(--artdeco-spacing-1);
  }

  .strategy-desc {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-compact-sm);
    color: var(--artdeco-fg-muted);
  }
}

// Parameter Form
.parameter-form {
  .form-section {
    margin-bottom: var(--artdeco-spacing-4);

    h4 {
      font-family: var(--font-display);
      font-weight: 600;
      color: var(--artdeco-gold-primary);
      margin-bottom: var(--artdeco-spacing-2);
    }

    .form-row {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: var(--artdeco-spacing-3);
    }
  }
}

// Review Content
.review-content {
  .review-item {
    display: flex;
    justify-content: space-between;
    padding: var(--artdeco-spacing-2) 0;
    border-bottom: 1px solid var(--artdeco-border-subtle);

    .review-label {
      font-family: var(--font-body);
      color: var(--artdeco-fg-muted);
    }

    .review-value {
      font-family: var(--font-display);
      font-weight: 600;
      color: var(--artdeco-fg-default);
    }
  }
}

// Results Metrics
.results-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--artdeco-spacing-3);
  margin-bottom: var(--artdeco-spacing-4);
}

.metric-card {
  text-align: center;

  .metric-label {
    font-family: var(--font-body);
    font-size: var(--artdeco-text-sm);
    color: var(--artdeco-fg-muted);
    margin-bottom: var(--artdeco-spacing-1);
  }

  .metric-value {
    font-family: var(--font-display);
    font-size: var(--artdeco-text-2xl);
    font-weight: 700;
    color: var(--artdeco-fg-default);

    &.change-up {
      color: var(--artdeco-eco-green);
    }

    &.change-down {
      color: var(--artdeco-alert-red);
    }
  }
}

.backtest-chart {
  min-height: 400px;
  background: var(--artdeco-bg-card);
  border: 1px solid var(--artdeco-border-default);
  border-radius: var(--artdeco-radius-md);
  padding: var(--artdeco-spacing-3);
}
</style>
