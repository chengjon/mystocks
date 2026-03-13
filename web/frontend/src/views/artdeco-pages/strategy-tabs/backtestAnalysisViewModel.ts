import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { strategyApi } from '@/api'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import type { StrategyConfig } from '@/api/types/common'
import {
  createBacktestWorkbenchRealConfig,
  getBacktestWorkbenchConfig,
  type BacktestWorkbenchDataConfig
} from '@/mock/backtestWorkbenchMock'
import { extractStrategyConfigs } from './strategyParametersData'
import { extractQuickRunFlagFromQuery, extractStrategyIdFromQuery } from './strategyCrossTabNavigation'

interface BacktestConfigState {
  strategy: string
  period: string
  capital: string
  benchmark: string
}

function createDefaultConfig(): BacktestConfigState {
  return {
    strategy: '',
    period: '1y',
    capital: '1000000',
    benchmark: 'csi300'
  }
}

export function useBacktestAnalysisViewModel() {
  const route = useRoute()
  const { getSnapshot, setActiveStrategy, setBacktestTaskSnapshot } = useStrategyCrossTabContext()

  const activeTab = ref('designer')
  const refreshing = ref(false)
  const workbench = ref<BacktestWorkbenchDataConfig>(getBacktestWorkbenchConfig('real'))
  const config = ref<BacktestConfigState>(createDefaultConfig())

  const selectedStrategyId = computed(() => extractStrategyIdFromQuery(route.query as Record<string, unknown>))
  const selectedStrategySnapshot = computed(() => {
    if (!selectedStrategyId.value) {
      return null
    }
    return getSnapshot(selectedStrategyId.value)
  })

  const tabs = computed(() => workbench.value.tabs)
  const systemStatus = computed(() => workbench.value.systemStatus)
  const lastUpdated = computed(() => workbench.value.lastUpdated)
  const opsOverview = computed(() => workbench.value.opsOverview)
  const strategyOptions = computed(() => workbench.value.strategyOptions)
  const periodOptions = computed(() => workbench.value.periodOptions)
  const benchmarkOptions = computed(() => workbench.value.benchmarkOptions)
  const strategyMetrics = computed(() => workbench.value.strategyMetrics)
  const signalFlow = computed(() => workbench.value.signalFlow)
  const strategyLibrary = computed(() => workbench.value.strategyLibrary)
  const backtestTasks = computed(() => workbench.value.backtestTasks)
  const progress = computed(() => workbench.value.progress)
  const runLogs = computed(() => workbench.value.runLogs)
  const optimizeRows = computed(() => workbench.value.optimizeRows)
  const optimizeHints = computed(() => workbench.value.optimizeHints)
  const reportRows = computed(() => workbench.value.reportRows)
  const reportSummary = computed(() => workbench.value.reportSummary)
  const optimizeColumns = computed(() => [
    { key: 'name', label: '策略' },
    { key: 'score', label: '评分' },
    { key: 'annual', label: '年化收益' },
    { key: 'drawdown', label: '回撤' }
  ])
  const reportColumns = computed(() => [
    { key: 'name', label: '报告名' },
    { key: 'period', label: '周期' },
    { key: 'return', label: '收益' },
    { key: 'drawdown', label: '回撤' },
    { key: 'updatedAt', label: '更新时间' }
  ])

  const kpiItems = computed(() => {
    const summary = workbench.value.summary
    return [
      { label: '累计回测', value: summary.totalRuns, variant: 'gold' as const },
      { label: '胜率', value: `${summary.winRate}%`, variant: summary.winRate >= 50 ? 'rise' as const : 'fall' as const },
      { label: '年化收益', value: `${summary.annualReturn}%`, variant: summary.annualReturn >= 0 ? 'rise' as const : 'fall' as const },
      { label: '最大回撤', value: `${summary.maxDrawdown}%`, variant: summary.maxDrawdown >= 0 ? 'rise' as const : 'fall' as const }
    ]
  })

  function applyWorkbench(next: BacktestWorkbenchDataConfig) {
    workbench.value = next

    if (!config.value.strategy) {
      config.value.strategy = next.strategyOptions[0]?.value || selectedStrategyId.value || ''
    }
  }

  async function loadWorkbench() {
    refreshing.value = true
    try {
      const payload = await strategyApi.getStrategies({})
      const strategies = extractStrategyConfigs(payload)
      if (strategies && strategies.length > 0) {
        applyWorkbench(createBacktestWorkbenchRealConfig(strategies as StrategyConfig[]))
      } else {
        applyWorkbench(getBacktestWorkbenchConfig('real'))
      }
    } catch {
      applyWorkbench(getBacktestWorkbenchConfig('real'))
    } finally {
      refreshing.value = false
    }
  }

  function handleRunBacktest() {
    const now = new Date()
    const taskId = `bt-${now.getTime()}`
    const next = {
      ...workbench.value,
      lastUpdated: now.toLocaleString('zh-CN'),
      progress: {
        phase: '回测任务排队中',
        percent: 18,
        steps: [
          { name: '行情载入', status: 'queued', statusClass: 'queued' as const },
          { name: '信号回放', status: 'queued', statusClass: 'queued' as const },
          { name: '撮合执行', status: 'queued', statusClass: 'queued' as const },
          { name: '绩效计算', status: 'queued', statusClass: 'queued' as const }
        ]
      },
      runLogs: [
        {
          ts: now.toTimeString().slice(0, 8),
          msg: `已提交回测任务 ${taskId}${selectedStrategyId.value ? `（策略 ${selectedStrategyId.value}）` : ''}`
        },
        ...workbench.value.runLogs
      ]
    }

    workbench.value = next

    if (selectedStrategyId.value) {
      setBacktestTaskSnapshot(selectedStrategyId.value, {
        status: 'queued',
        taskId,
        message: '回测任务排队中',
        updatedAt: now.toISOString()
      })
    }
  }

  function resetConfig() {
    config.value = {
      ...createDefaultConfig(),
      strategy: workbench.value.strategyOptions[0]?.value || selectedStrategyId.value || ''
    }
  }

  watch(selectedStrategyId, (value) => {
    setActiveStrategy(value)
    if (value) {
      config.value.strategy = value
    }
  }, { immediate: true })

  onMounted(async () => {
    await loadWorkbench()
    if (extractQuickRunFlagFromQuery(route.query as Record<string, unknown>)) {
      activeTab.value = 'execution'
      handleRunBacktest()
    }
  })

  return {
    activeTab,
    backtestTasks,
    benchmarkOptions,
    config,
    handleRunBacktest,
    kpiItems,
    lastUpdated,
    opsOverview,
    optimizeColumns,
    optimizeRows,
    optimizeHints,
    periodOptions,
    progress,
    reportColumns,
    reportRows,
    reportSummary,
    resetConfig,
    runLogs,
    selectedStrategyId,
    selectedStrategySnapshot,
    signalFlow,
    strategyLibrary,
    strategyMetrics,
    strategyOptions,
    systemStatus,
    tabs
  }
}
