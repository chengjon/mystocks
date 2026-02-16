import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { ElMessage } from 'element-plus'
import echarts from '@/utils/echarts'
import { artDecoTheme } from '@/utils/echarts'
import ArtDecoCardCompact from '@/components/artdeco/base/ArtDecoCardCompact.vue'
import { TrendCharts } from '@element-plus/icons-vue'

interface StrategyTemplate {
  id: string
  name: string
  description: string
  defaultParams: Record<string, unknown>
}

interface BacktestHistoryItem {
  id: string
  name: string
  strategyName: string
  totalReturn: number
  sharpeRatio: number
  maxDrawdown: number
  winRate: number
  runAt: string
  params: Record<string, number>
}

interface BacktestComparison {
  backtest1: string
  backtest2: string
  diffData: Array<{
    param: string
    backtest1Value: number
    backtest2Value: number
    difference: number
    highlight: boolean
  }>
}

export function useBacktestWizard() {

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
const comparisonData = computed<BacktestComparison | null>(() => {
  if (!selectedBacktest1.value || !selectedBacktest2.value) {
    return null
  }

  const bt1 = backtestHistory.value.find(bt => bt.id === selectedBacktest1.value)
  const bt2 = backtestHistory.value.find(bt => bt.id === selectedBacktest2.value)

  if (!bt1 || !bt2) {
    return null
  }

  return {
    backtest1: bt1.id,
    backtest2: bt2.id,
    diffData: [
      {
        param: '短期MA周期',
        backtest1Value: bt1?.params.shortMA || 0,
        backtest2Value: bt2?.params.shortMA || 0,
        difference: (bt1?.params.shortMA || 0) - (bt2?.params.shortMA || 0),
        highlight: bt1?.params.shortMA !== bt2?.params.shortMA
      },
      {
        param: '长期MA周期',
        backtest1Value: bt1?.params.longMA || 0,
        backtest2Value: bt2?.params.longMA || 0,
        difference: (bt1?.params.longMA || 0) - (bt2?.params.longMA || 0),
        highlight: bt1?.params.longMA !== bt2?.params.longMA
      }
    ]
  }
})

// Chart reference
const backtestChartRef = ref<HTMLElement>()
let backtestChart: ReturnType<typeof echarts.init> | null = null

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
          color: 'rgb(212 175 55 / 10%)'
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

  return {
    wizardSteps,
    currentStep,
    selectedStrategy,
    quickTemplates,
    customTemplates,
    showSaveTemplateDialog,
    strategyTemplates,
    backtestParams,
    backtestResults,
    backtestHistory,
    selectedBacktest1,
    selectedBacktest2,
    comparisonData,
    backtestChartRef,
    backtestChart,
    canProceed,
    selectStrategy,
    nextStep,
    prevStep,
    resetWizard,
    getSelectedStrategyName,
    formatDate,
    initBacktestChart,
  }
}
