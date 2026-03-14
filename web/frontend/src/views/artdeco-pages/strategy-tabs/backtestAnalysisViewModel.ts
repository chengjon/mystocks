import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { strategyApi } from '@/api'
import { StrategyApiService } from '@/api/services/strategyService'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  useStrategyCrossTabContext,
  type StrategyBacktestTaskStatus
} from '@/composables/strategy/useStrategyCrossTabContext'
import {
  createBacktestWorkbenchRealConfig,
  getBacktestWorkbenchConfig,
  type BacktestWorkbenchDataConfig
} from '@/mock/backtestWorkbenchMock'

import {
  createBacktestPayload,
  createDefaultBacktestConfig,
  extractStrategiesFromPayload,
  optimizeColumns,
  reportColumns,
  resolveBacktestTargetStrategyId,
  syncStrategyOptionsWithContext,
  upsertBacktestTaskRows,
  type BacktestTaskRow
} from './backtestAnalysisHelpers'
import {
  extractBacktestTaskId,
  extractBacktestTaskMessage,
  extractBacktestTaskStatus,
  isBacktestTerminalStatus,
  toBacktestStatusMessage
} from '@/composables/strategy/backtestContract'
import { extractQuickRunFlagFromQuery, extractStrategyIdFromQuery } from './strategyCrossTabNavigation'

interface RunBacktestOptions {
  source: 'manual' | 'quick-handoff'
}

const BACKTEST_POLL_INTERVAL_MS = 2000
const BACKTEST_MAX_POLLS = 20

function toRecord(value: unknown): Record<string, unknown> | null {
  if (!value || typeof value !== 'object') {
    return null
  }

  return value as Record<string, unknown>
}

function readString(record: Record<string, unknown> | null, keys: string[]): string | null {
  if (!record) {
    return null
  }

  for (const key of keys) {
    const value = record[key]
    if (typeof value === 'string' && value.trim()) {
      return value.trim()
    }
  }

  return null
}

function readNumber(record: Record<string, unknown> | null, keys: string[]): number | null {
  if (!record) {
    return null
  }

  for (const key of keys) {
    const value = record[key]
    if (typeof value === 'number' && Number.isFinite(value)) {
      return value
    }
  }

  return null
}

function formatRatioAsPercent(value: number | null): string {
  if (value == null) {
    return '--'
  }

  const normalized = Math.abs(value) <= 1 ? value * 100 : value
  const sign = normalized > 0 ? '+' : normalized < 0 ? '-' : ''
  return `${sign}${Math.abs(normalized).toFixed(1)}%`
}

function formatBacktestPeriodLabel(startDate: string | null, endDate: string | null, fallbackPeriod: string): string {
  if (startDate && endDate) {
    return `${startDate} ~ ${endDate}`
  }

  return fallbackPeriod
}

function formatUpdatedAtLabel(rawValue: string | null): string {
  if (!rawValue) {
    return new Date().toLocaleString()
  }

  const parsed = new Date(rawValue)
  if (Number.isNaN(parsed.getTime())) {
    return rawValue
  }

  return parsed.toLocaleString()
}

export function useBacktestAnalysisViewModel() {
  const { exec } = useArtDecoApi()
  const route = useRoute()
  const router = useRouter()
  const strategyService = new StrategyApiService()
  const { getSnapshot, setActiveStrategy, setBacktestTaskSnapshot } = useStrategyCrossTabContext()
  const initialConfig = getBacktestWorkbenchConfig('real')

  const activeTab = ref('execution')
  const systemStatus = ref(initialConfig.systemStatus)
  const lastUpdated = ref(initialConfig.lastUpdated)

  const tabs = ref(initialConfig.tabs)
  const opsOverview = ref(initialConfig.opsOverview)
  const strategyOptions = ref(initialConfig.strategyOptions)
  const periodOptions = ref(initialConfig.periodOptions)
  const benchmarkOptions = ref(initialConfig.benchmarkOptions)
  const strategyMetrics = ref(initialConfig.strategyMetrics)
  const signalFlow = ref(initialConfig.signalFlow)
  const strategyLibrary = ref(initialConfig.strategyLibrary)
  const backtestTasks = ref<BacktestTaskRow[]>(initialConfig.backtestTasks as BacktestTaskRow[])
  const optimizeRows = ref(initialConfig.optimizeRows)
  const optimizeHints = ref(initialConfig.optimizeHints)
  const reportRows = ref(initialConfig.reportRows)
  const reportSummary = ref(initialConfig.reportSummary)

  const summary = reactive({ ...initialConfig.summary })
  const defaultConfig = reactive(createDefaultBacktestConfig(initialConfig))
  const config = reactive({ ...defaultConfig })
  const progress = reactive({ ...initialConfig.progress })
  const runLogs = ref(initialConfig.runLogs)
  const selectedStrategyId = ref<string | null>(extractStrategyIdFromQuery(route.query as Record<string, unknown>))
  const latestRunToken = ref(0)
  const quickRunConsumedKey = ref<string | null>(null)

  const selectedStrategySnapshot = computed(() => {
    if (!selectedStrategyId.value) {
      return null
    }

    return getSnapshot(selectedStrategyId.value)
  })

  function applyWorkbenchConfig(nextConfig: BacktestWorkbenchDataConfig) {
    systemStatus.value = nextConfig.systemStatus
    lastUpdated.value = nextConfig.lastUpdated
    tabs.value = nextConfig.tabs
    opsOverview.value = nextConfig.opsOverview
    strategyOptions.value = nextConfig.strategyOptions
    periodOptions.value = nextConfig.periodOptions
    benchmarkOptions.value = nextConfig.benchmarkOptions
    strategyMetrics.value = nextConfig.strategyMetrics
    signalFlow.value = nextConfig.signalFlow
    strategyLibrary.value = nextConfig.strategyLibrary
    backtestTasks.value = nextConfig.backtestTasks as BacktestTaskRow[]
    optimizeRows.value = nextConfig.optimizeRows
    optimizeHints.value = nextConfig.optimizeHints
    reportRows.value = nextConfig.reportRows
    reportSummary.value = nextConfig.reportSummary
    Object.assign(summary, nextConfig.summary)
    Object.assign(progress, nextConfig.progress)
    runLogs.value = nextConfig.runLogs

    const nextDefaultConfig = createDefaultBacktestConfig(nextConfig)
    Object.assign(defaultConfig, nextDefaultConfig)
    resetConfig()
    syncSelectedStrategyContext()
  }

  async function loadRealConfig() {
    const payload = await exec(() => strategyApi.getStrategies({}), {
      silent: true,
      errorMsg: '获取REAL策略数据失败，当前显示空态'
    })

    if (!payload) {
      return
    }

    applyWorkbenchConfig(createBacktestWorkbenchRealConfig(extractStrategiesFromPayload(payload)))
  }

  function pushRunLog(message: string) {
    runLogs.value = [
      { ts: new Date().toTimeString().slice(0, 8), msg: message },
      ...runLogs.value.slice(0, 19)
    ]
  }

  function syncProgressByStatus(status: StrategyBacktestTaskStatus) {
    if (status === 'queued') {
      progress.phase = '任务排队中'
      progress.percent = Math.max(progress.percent, 15)
      return
    }

    if (status === 'running') {
      progress.phase = '回测执行中'
      progress.percent = Math.max(progress.percent, 60)
      return
    }

    if (status === 'completed') {
      progress.phase = '回测完成'
      progress.percent = 100
      return
    }

    progress.phase = '回测失败'
  }

  function applyBacktestTaskSnapshot(
    strategyId: string,
    status: StrategyBacktestTaskStatus,
    message: string,
    taskId?: string
  ) {
    setBacktestTaskSnapshot(strategyId, {
      status,
      taskId,
      message,
      updatedAt: new Date().toISOString()
    })
    backtestTasks.value = upsertBacktestTaskRows(backtestTasks.value, {
      strategyId,
      strategyName: getSnapshot(strategyId)?.name,
      status,
      message,
      taskId
    })
    syncProgressByStatus(status)
    lastUpdated.value = new Date().toLocaleString()
  }

  function wait(ms: number): Promise<void> {
    return new Promise((resolve) => {
      window.setTimeout(resolve, ms)
    })
  }

  function finalizeBacktest(status: StrategyBacktestTaskStatus, message?: string) {
    if (status === 'failed') {
      pushRunLog(message ? `回测任务失败：${message}` : '回测任务失败，请检查策略参数与后端任务状态。')
    }
  }

  function syncReportSummaryCount() {
    if (!reportSummary.value.length) {
      return
    }

    const [firstItem, ...restItems] = reportSummary.value
    reportSummary.value = [
      {
        ...firstItem,
        value: `${reportRows.value.length} 份`,
        variant: reportRows.value.length > 0 ? 'rise' : firstItem.variant
      },
      ...restItems
    ]
  }

  async function syncBacktestResultReport(strategyId: string, taskId: string): Promise<boolean> {
    try {
      const response = await strategyService.getBacktestResult(taskId)
      const payload = toRecord(response?.data) ?? toRecord(response)
      const performance = toRecord(payload?.performance)
      const strategyLabel = strategyOptions.value.find((item) => item.value === strategyId)?.label
      const snapshotName = getSnapshot(strategyId)?.name
      const resolvedSnapshotName = snapshotName && snapshotName !== strategyId ? snapshotName : null
      const selectedSnapshotName = selectedStrategySnapshot.value?.name
      const resolvedSelectedSnapshotName = selectedSnapshotName && selectedSnapshotName !== strategyId ? selectedSnapshotName : null
      const reportName = strategyLabel || resolvedSnapshotName || resolvedSelectedSnapshotName || `策略 ${strategyId}`
      const row = {
        name: reportName,
        period: formatBacktestPeriodLabel(
          readString(payload, ['start_date', 'startDate']),
          readString(payload, ['end_date', 'endDate']),
          config.period
        ),
        return: formatRatioAsPercent(
          readNumber(payload, ['total_return', 'totalReturn']) ??
            readNumber(performance, ['total_return', 'annualized_return'])
        ),
        drawdown: formatRatioAsPercent(
          readNumber(performance, ['max_drawdown']) ??
            readNumber(payload, ['max_drawdown', 'maxDrawdown'])
        ),
        updatedAt: formatUpdatedAtLabel(
          readString(payload, ['completed_at', 'completedAt', 'updated_at', 'updatedAt'])
        )
      }

      reportRows.value = [row, ...reportRows.value.filter((item) => item.name !== row.name)].slice(0, 10)
      syncReportSummaryCount()
      return true
    } catch (error) {
      const message = error instanceof Error ? error.message : '获取回测结果失败'
      pushRunLog(`回测结果获取失败：${message}`)
      return false
    }
  }

  async function finalizeCompletedBacktest(strategyId: string, taskId?: string) {
    if (!taskId) {
      pushRunLog('回测任务完成，结果待同步。')
      return
    }

    const reportSynced = await syncBacktestResultReport(strategyId, taskId)
    pushRunLog(reportSynced ? '回测结果已同步到报告中心。' : '回测任务完成，但报告同步失败。')
  }

  async function pollBacktestStatusUntilDone(strategyId: string, taskId: string, runToken: number) {
    for (let index = 0; index < BACKTEST_MAX_POLLS; index += 1) {
      if (runToken !== latestRunToken.value) {
        return
      }

      await wait(BACKTEST_POLL_INTERVAL_MS)

      if (runToken !== latestRunToken.value) {
        return
      }

      try {
        const response = await strategyService.getBacktestStatus(taskId)
        const status = extractBacktestTaskStatus(response) ?? 'running'
        const message = extractBacktestTaskMessage(response) ?? toBacktestStatusMessage(status)
        applyBacktestTaskSnapshot(strategyId, status, message, taskId)

        if (isBacktestTerminalStatus(status)) {
          if (status === 'completed') {
            await finalizeCompletedBacktest(strategyId, taskId)
            return
          }
          finalizeBacktest(status, message)
          return
        }
      } catch (error) {
        if (index < BACKTEST_MAX_POLLS - 1) {
          continue
        }

        const message = error instanceof Error ? error.message : '轮询回测状态失败'
        applyBacktestTaskSnapshot(strategyId, 'failed', `轮询失败：${message}`, taskId)
        finalizeBacktest('failed', message)
        return
      }
    }

    applyBacktestTaskSnapshot(strategyId, 'failed', '回测状态轮询超时，请稍后刷新。', taskId)
    finalizeBacktest('failed', '回测状态轮询超时，请稍后刷新。')
  }

  function handleRunBacktest() {
    void runBacktest({ source: 'manual' })
  }

  async function runBacktest(options: RunBacktestOptions = { source: 'manual' }) {
    const configuredStrategyId = strategyOptions.value.some((item) => item.value === config.strategy)
      ? config.strategy
      : null
    const strategyId = resolveBacktestTargetStrategyId(selectedStrategyId.value, configuredStrategyId)
    if (!strategyId) {
      progress.phase = '等待选择策略'
      progress.percent = 0
      lastUpdated.value = new Date().toLocaleString()
      pushRunLog('未绑定有效策略ID，无法启动真实回测。')
      return
    }

    setActiveStrategy(strategyId)
    summary.totalRuns += 1
    const runToken = latestRunToken.value + 1
    latestRunToken.value = runToken
    const payload = createBacktestPayload({
      strategyId,
      period: config.period,
      capital: config.capital,
      benchmark: config.benchmark,
      optimizationParameters: selectedStrategySnapshot.value?.optimization?.recommendedParameters ?? null
    })

    const queuedMessage = options.source === 'quick-handoff'
      ? '已接收快速回测指令，任务排队中'
      : '回测任务已创建，进入排队'
    applyBacktestTaskSnapshot(strategyId, 'queued', queuedMessage)

    try {
      const response = await strategyService.startBacktest(strategyId, payload)
      const taskId = extractBacktestTaskId(response)
      const status = extractBacktestTaskStatus(response) ?? 'queued'
      const message = extractBacktestTaskMessage(response) ?? toBacktestStatusMessage(status)

      applyBacktestTaskSnapshot(strategyId, status, message, taskId ?? undefined)

      if (isBacktestTerminalStatus(status)) {
        if (status === 'completed') {
          await finalizeCompletedBacktest(strategyId, taskId ?? undefined)
          return
        }
        finalizeBacktest(status, message)
        return
      }

      if (!taskId) {
        applyBacktestTaskSnapshot(strategyId, 'failed', '回测接口未返回 taskId，无法继续轮询。')
        finalizeBacktest('failed', '回测接口未返回 taskId，无法继续轮询。')
        return
      }

      await pollBacktestStatusUntilDone(strategyId, taskId, runToken)
    } catch (error) {
      const message = error instanceof Error ? error.message : '启动回测失败'
      applyBacktestTaskSnapshot(strategyId, 'failed', `启动失败：${message}`)
      finalizeBacktest('failed', message)
    }
  }

  function resetConfig() {
    config.strategy = defaultConfig.strategy
    config.period = defaultConfig.period
    config.capital = defaultConfig.capital
    config.benchmark = defaultConfig.benchmark
    syncSelectedStrategyContext()
  }

  function syncSelectedStrategyContext() {
    const currentStrategyId = selectedStrategyId.value
    if (!currentStrategyId) {
      return
    }

    const contextLabel = selectedStrategySnapshot.value?.name || `策略 ${currentStrategyId}`
    strategyOptions.value = syncStrategyOptionsWithContext(strategyOptions.value, currentStrategyId, contextLabel)
    config.strategy = currentStrategyId
  }

  async function consumeQuickRunQueryFlag() {
    const nextQuery = { ...route.query }
    if (!Object.prototype.hasOwnProperty.call(nextQuery, 'quickRun')) {
      return
    }

    delete nextQuery.quickRun
    await router.replace({ query: nextQuery })
  }

  async function handleQuickRunHandoff() {
    const strategyId = selectedStrategyId.value
    const quickRun = extractQuickRunFlagFromQuery(route.query as Record<string, unknown>)

    if (!quickRun) {
      quickRunConsumedKey.value = null
      return
    }

    if (!strategyId) {
      return
    }

    const handoffKey = `${strategyId}:quick-run`
    if (quickRunConsumedKey.value === handoffKey) {
      return
    }

    quickRunConsumedKey.value = handoffKey
    activeTab.value = 'execution'
    await consumeQuickRunQueryFlag()
    await runBacktest({ source: 'quick-handoff' })
  }

  onMounted(() => {
    void loadRealConfig()
    setActiveStrategy(selectedStrategyId.value)
    syncSelectedStrategyContext()
    void handleQuickRunHandoff()
  })

  onBeforeUnmount(() => {
    latestRunToken.value += 1
  })

  watch(
    () => route.query,
    (query) => {
      selectedStrategyId.value = extractStrategyIdFromQuery(query as Record<string, unknown>)
      setActiveStrategy(selectedStrategyId.value)
      syncSelectedStrategyContext()
      void handleQuickRunHandoff()
    }
  )

  const kpiItems = computed(() => [
    { label: '总回测次数', value: summary.totalRuns, variant: 'gold' as const },
    { label: '策略胜率', value: `${summary.winRate}%`, variant: 'rise' as const },
    { label: '年化收益', value: `${summary.annualReturn}%`, variant: 'gold' as const },
    { label: '最大回撤', value: `${summary.maxDrawdown}%`, variant: 'fall' as const }
  ])

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
    optimizeHints,
    optimizeRows,
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
