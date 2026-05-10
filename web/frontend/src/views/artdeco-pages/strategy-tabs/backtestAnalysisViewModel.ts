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

interface GeneratedParameterSnapshot {
  strategyId: string
  strategyLabel: string
  generatedAt: string
  parameterCount: number
  optimizationParameterCount: number
}

type BacktestReportRow = BacktestWorkbenchDataConfig['reportRows'][number]
type BacktestOptimizeRow = BacktestWorkbenchDataConfig['optimizeRows'][number]
type BacktestOptimizeHint = BacktestWorkbenchDataConfig['optimizeHints'][number]
type BacktestProgressState = BacktestWorkbenchDataConfig['progress']
type BacktestRunLog = BacktestWorkbenchDataConfig['runLogs'][number]
type BacktestSummarySnapshot = BacktestWorkbenchDataConfig['summary']
type BacktestExecutionSnapshot = {
  progress: BacktestProgressState
  runLogs: BacktestRunLog[]
}

const BACKTEST_POLL_INTERVAL_MS = 2000
const BACKTEST_MAX_POLLS = 20
const STRATEGY_CONTEXT_SYNC_NOTICE = '策略上下文已同步；当前任务、KPI 与报告摘要仍基于策略列表派生，待真实回测结果回填。'
const STRATEGY_CONTEXT_SWITCH_NOTICE = '策略上下文已切换；当前任务、KPI 与报告摘要仍基于策略列表派生，待真实回测结果回填。'

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
    return '--'
  }

  const parsed = new Date(rawValue)
  if (Number.isNaN(parsed.getTime())) {
    return rawValue
  }

  return parsed.toLocaleString()
}

function cloneBacktestProgressState(progress: BacktestProgressState): BacktestProgressState {
  return {
    phase: progress.phase,
    percent: progress.percent,
    steps: progress.steps.map((step) => ({ ...step }))
  }
}

function cloneBacktestRunLogs(logs: BacktestRunLog[]): BacktestRunLog[] {
  return logs.map((log) => ({ ...log }))
}

function cloneBacktestSummary(summary: BacktestSummarySnapshot): BacktestSummarySnapshot {
  return {
    totalRuns: summary.totalRuns,
    winRate: summary.winRate,
    annualReturn: summary.annualReturn,
    maxDrawdown: summary.maxDrawdown
  }
}

function cloneBacktestOptimizeRows(rows: BacktestOptimizeRow[]): BacktestOptimizeRow[] {
  return rows.map((row) => ({ ...row }))
}

function cloneBacktestOptimizeHints(hints: BacktestOptimizeHint[]): BacktestOptimizeHint[] {
  return hints.map((hint) => ({ ...hint }))
}

function readOptimizationParameterValue(
  parameters: Record<string, unknown>,
  keys: string[]
): string | null {
  for (const key of keys) {
    const value = parameters[key]
    if (typeof value === 'string' && value.trim().length > 0) {
      return value.trim()
    }
    if (typeof value === 'number' && Number.isFinite(value)) {
      return String(value)
    }
  }

  return null
}

export function useBacktestAnalysisViewModel() {
  const { loading, error, exec } = useArtDecoApi()
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
  const baselineBacktestTasks = ref<BacktestTaskRow[]>([...initialConfig.backtestTasks] as BacktestTaskRow[])
  const baselineOptimizeRows = ref<BacktestOptimizeRow[]>(cloneBacktestOptimizeRows(initialConfig.optimizeRows))
  const baselineOptimizeHints = ref<BacktestOptimizeHint[]>(cloneBacktestOptimizeHints(initialConfig.optimizeHints))

  const summary = reactive({ ...initialConfig.summary })
  const defaultConfig = reactive(createDefaultBacktestConfig(initialConfig))
  const config = reactive({ ...defaultConfig })
  const progress = reactive({ ...initialConfig.progress })
  const runLogs = ref(initialConfig.runLogs)
  const selectedStrategyId = ref<string | null>(extractStrategyIdFromQuery(route.query as Record<string, unknown>))
  const latestRunToken = ref(0)
  const quickRunConsumedKey = ref<string | null>(null)
  const hasLoaded = ref(false)
  const isRunningBacktest = ref(false)
  const lastGeneratedSnapshot = ref<GeneratedParameterSnapshot | null>(null)
  const verifiedReportRowsByStrategyId = ref<Map<string, BacktestReportRow[]>>(new Map())
  const verifiedExecutionStateByStrategyId = ref<Map<string, BacktestExecutionSnapshot>>(new Map())
  const verifiedTaskRowsByStrategyId = ref<Map<string, BacktestTaskRow[]>>(new Map())
  const verifiedKpiSummaryByStrategyId = ref<Map<string, BacktestSummarySnapshot>>(new Map())
  const baselineSummary = ref<BacktestSummarySnapshot>(cloneBacktestSummary(initialConfig.summary))
  const baselineProgress = ref<BacktestProgressState>(cloneBacktestProgressState(initialConfig.progress))
  const baselineRunLogs = ref<BacktestRunLog[]>(cloneBacktestRunLogs(initialConfig.runLogs))
  const runtimeNotice = ref('等待策略上下文同步。')
  const runtimeNoticeTone = ref<'neutral' | 'success' | 'warning' | 'error'>('neutral')

  const selectedStrategySnapshot = computed(() => {
    if (!selectedStrategyId.value) {
      return null
    }

    return getSnapshot(selectedStrategyId.value)
  })
  const activeGeneratedSnapshot = computed(() => {
    if (!selectedStrategyId.value) {
      return null
    }

    if (lastGeneratedSnapshot.value?.strategyId !== selectedStrategyId.value) {
      return null
    }

    return lastGeneratedSnapshot.value
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
    baselineBacktestTasks.value = [...(nextConfig.backtestTasks as BacktestTaskRow[])]
    baselineOptimizeRows.value = cloneBacktestOptimizeRows(nextConfig.optimizeRows)
    baselineOptimizeHints.value = cloneBacktestOptimizeHints(nextConfig.optimizeHints)
    Object.assign(summary, nextConfig.summary)
    baselineSummary.value = cloneBacktestSummary(nextConfig.summary)
    Object.assign(progress, nextConfig.progress)
    runLogs.value = nextConfig.runLogs
    baselineProgress.value = cloneBacktestProgressState(nextConfig.progress)
    baselineRunLogs.value = cloneBacktestRunLogs(nextConfig.runLogs)

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
      runtimeNotice.value = error.value || '获取REAL策略数据失败，当前显示空态'
      runtimeNoticeTone.value = 'error'
      hasLoaded.value = true
      return
    }

    applyWorkbenchConfig(createBacktestWorkbenchRealConfig(extractStrategiesFromPayload(payload)))
    runtimeNotice.value = STRATEGY_CONTEXT_SYNC_NOTICE
    runtimeNoticeTone.value = 'success'
    hasLoaded.value = true
  }

  function resolveCurrentStrategyId(): string | null {
    const configuredStrategyId = strategyOptions.value.some((item) => item.value === config.strategy)
      ? config.strategy
      : null

    return resolveBacktestTargetStrategyId(selectedStrategyId.value, configuredStrategyId)
  }

  function resolveCurrentStrategyLabel(strategyId: string): string {
    return (
      strategyOptions.value.find((item) => item.value === strategyId)?.label ||
      selectedStrategySnapshot.value?.name ||
      `策略 ${strategyId}`
    )
  }

  function pushRunLog(message: string) {
    runLogs.value = [
      { ts: new Date().toTimeString().slice(0, 8), msg: message },
      ...runLogs.value.slice(0, 19)
    ]
    persistVisibleExecutionState()
  }

  function persistExecutionState(strategyId: string) {
    verifiedExecutionStateByStrategyId.value = new Map(verifiedExecutionStateByStrategyId.value).set(strategyId, {
      progress: cloneBacktestProgressState(progress),
      runLogs: cloneBacktestRunLogs(runLogs.value)
    })
  }

  function persistVisibleExecutionState() {
    if (!selectedStrategyId.value) {
      return
    }

    persistExecutionState(selectedStrategyId.value)
  }

  function syncProgressByStatus(status: StrategyBacktestTaskStatus) {
    if (status === 'queued') {
      progress.phase = '任务排队中'
      progress.percent = 15
      progress.steps = [
        { name: '行情载入', status: 'queued', statusClass: 'queued' },
        { name: '信号回放', status: 'queued', statusClass: 'queued' },
        { name: '撮合执行', status: 'queued', statusClass: 'queued' },
        { name: '绩效计算', status: 'queued', statusClass: 'queued' }
      ]
      persistVisibleExecutionState()
      return
    }

    if (status === 'running') {
      progress.phase = '回测执行中'
      progress.percent = 60
      progress.steps = [
        { name: '行情载入', status: 'done', statusClass: 'done' },
        { name: '信号回放', status: 'running', statusClass: 'running' },
        { name: '撮合执行', status: 'queued', statusClass: 'queued' },
        { name: '绩效计算', status: 'queued', statusClass: 'queued' }
      ]
      persistVisibleExecutionState()
      return
    }

    if (status === 'completed') {
      progress.phase = '回测完成'
      progress.percent = 100
      progress.steps = [
        { name: '行情载入', status: 'done', statusClass: 'done' },
        { name: '信号回放', status: 'done', statusClass: 'done' },
        { name: '撮合执行', status: 'done', statusClass: 'done' },
        { name: '绩效计算', status: 'done', statusClass: 'done' }
      ]
      persistVisibleExecutionState()
      return
    }

    progress.phase = '回测失败'
    progress.percent = 100
    progress.steps = [
      { name: '行情载入', status: 'done', statusClass: 'done' },
      { name: '信号回放', status: 'done', statusClass: 'done' },
      { name: '撮合执行', status: 'failed', statusClass: 'failed' },
      { name: '绩效计算', status: 'failed', statusClass: 'failed' }
    ]
    persistVisibleExecutionState()
  }

  function resetProgressForRun() {
    progress.phase = '任务排队中'
    progress.percent = 15
    progress.steps = [
      { name: '行情载入', status: 'queued', statusClass: 'queued' },
      { name: '信号回放', status: 'queued', statusClass: 'queued' },
      { name: '撮合执行', status: 'queued', statusClass: 'queued' },
      { name: '绩效计算', status: 'queued', statusClass: 'queued' }
    ]
    persistVisibleExecutionState()
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
    const currentTaskRows = verifiedTaskRowsByStrategyId.value.get(strategyId) ?? []
    const nextTaskRows = upsertBacktestTaskRows(currentTaskRows, {
      strategyId,
      strategyName: getSnapshot(strategyId)?.name,
      status,
      message,
      taskId
    })
    verifiedTaskRowsByStrategyId.value = new Map(verifiedTaskRowsByStrategyId.value).set(strategyId, nextTaskRows)
    syncVisibleTaskRows()
    syncProgressByStatus(status)
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

  function persistKpiSummary(strategyId: string) {
    verifiedKpiSummaryByStrategyId.value = new Map(verifiedKpiSummaryByStrategyId.value).set(
      strategyId,
      cloneBacktestSummary(summary)
    )
  }

  function persistVisibleKpiSummary() {
    if (!selectedStrategyId.value) {
      return
    }

    persistKpiSummary(selectedStrategyId.value)
  }

  function syncVisibleKpiSummary() {
    const strategyId = selectedStrategyId.value

    if (!strategyId) {
      Object.assign(summary, cloneBacktestSummary(baselineSummary.value))
      return
    }

    const snapshot = verifiedKpiSummaryByStrategyId.value.get(strategyId)
    if (!snapshot) {
      Object.assign(summary, cloneBacktestSummary(baselineSummary.value))
      return
    }

    Object.assign(summary, cloneBacktestSummary(snapshot))
  }

  function syncVisibleReportRows() {
    const strategyId = selectedStrategyId.value
    if (!strategyId) {
      reportRows.value = Array.from(verifiedReportRowsByStrategyId.value.values()).flat().slice(0, 10)
      syncReportSummaryCount()
      return
    }

    reportRows.value = [...(verifiedReportRowsByStrategyId.value.get(strategyId) ?? [])]
    syncReportSummaryCount()
  }

  function syncVisibleTaskRows() {
    const strategyId = selectedStrategyId.value

    if (!strategyId) {
      backtestTasks.value = [...baselineBacktestTasks.value]
      return
    }

    backtestTasks.value = [...(verifiedTaskRowsByStrategyId.value.get(strategyId) ?? [])]
  }

  function syncVisibleExecutionState() {
    const strategyId = selectedStrategyId.value

    if (!strategyId) {
      Object.assign(progress, cloneBacktestProgressState(baselineProgress.value))
      runLogs.value = cloneBacktestRunLogs(baselineRunLogs.value)
      return
    }

    const snapshot = verifiedExecutionStateByStrategyId.value.get(strategyId)
    if (!snapshot) {
      Object.assign(progress, cloneBacktestProgressState(baselineProgress.value))
      runLogs.value = cloneBacktestRunLogs(baselineRunLogs.value)
      return
    }

    Object.assign(progress, cloneBacktestProgressState(snapshot.progress))
    runLogs.value = cloneBacktestRunLogs(snapshot.runLogs)
  }

  function buildOptimizationRowsFromSnapshot(strategyId: string): BacktestOptimizeRow[] {
    const snapshot = selectedStrategySnapshot.value
    const optimization = snapshot?.optimization
    if (!snapshot || !optimization) {
      return cloneBacktestOptimizeRows(baselineOptimizeRows.value)
    }

    return [
      {
        name: resolveCurrentStrategyLabel(strategyId),
        score: String(optimization.score),
        annual: '--',
        drawdown: '--'
      }
    ]
  }

  function buildOptimizationHintsFromSnapshot(): BacktestOptimizeHint[] {
    const optimization = selectedStrategySnapshot.value?.optimization
    if (!optimization) {
      return cloneBacktestOptimizeHints(baselineOptimizeHints.value)
    }

    const recommendedParameters = optimization.recommendedParameters ?? {}
    return [
      {
        label: '建议仓位上限',
        value: readOptimizationParameterValue(recommendedParameters, ['position_limit', 'positionLimit', 'max_position', 'maxPosition']) ?? '--',
        variant: 'gold'
      },
      {
        label: '建议止损阈值',
        value: readOptimizationParameterValue(recommendedParameters, ['stop_loss', 'stopLoss', 'stop_loss_pct', 'stopLossPct']) ?? '--',
        variant: 'fall'
      },
      {
        label: '建议调仓频率',
        value: readOptimizationParameterValue(recommendedParameters, ['rebalance_frequency', 'rebalanceFrequency', 'rebalance_interval', 'rebalanceInterval']) ?? '--',
        variant: ''
      }
    ]
  }

  function syncVisibleOptimizationState() {
    const strategyId = selectedStrategyId.value
    if (!strategyId) {
      optimizeRows.value = cloneBacktestOptimizeRows(baselineOptimizeRows.value)
      optimizeHints.value = cloneBacktestOptimizeHints(baselineOptimizeHints.value)
      return
    }

    optimizeRows.value = buildOptimizationRowsFromSnapshot(strategyId)
    optimizeHints.value = buildOptimizationHintsFromSnapshot()
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
        ),
        backtestId: readNumber(payload, ['backtest_id', 'backtestId', 'id']) ?? undefined
      }

      const existingRows = verifiedReportRowsByStrategyId.value.get(strategyId) ?? []
      const nextRows = [row, ...existingRows.filter((item) => item.name !== row.name)].slice(0, 10)
      verifiedReportRowsByStrategyId.value = new Map(verifiedReportRowsByStrategyId.value).set(strategyId, nextRows)
      syncVisibleReportRows()
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
            isRunningBacktest.value = false
            runtimeNotice.value = '回测执行完成，结果已同步到报告中心。'
            runtimeNoticeTone.value = 'success'
            return
          }
          finalizeBacktest(status, message)
          isRunningBacktest.value = false
          runtimeNotice.value = message
          runtimeNoticeTone.value = 'error'
          return
        }
      } catch (error) {
        if (index < BACKTEST_MAX_POLLS - 1) {
          continue
        }

        const message = error instanceof Error ? error.message : '轮询回测状态失败'
        applyBacktestTaskSnapshot(strategyId, 'failed', `轮询失败：${message}`, taskId)
        finalizeBacktest('failed', message)
        isRunningBacktest.value = false
        runtimeNotice.value = `轮询失败：${message}`
        runtimeNoticeTone.value = 'error'
        return
      }
    }

    applyBacktestTaskSnapshot(strategyId, 'failed', '回测状态轮询超时，请稍后刷新。', taskId)
    finalizeBacktest('failed', '回测状态轮询超时，请稍后刷新。')
    isRunningBacktest.value = false
    runtimeNotice.value = '回测状态轮询超时，请稍后刷新。'
    runtimeNoticeTone.value = 'error'
  }

  function handleRunBacktest() {
    if (loading.value || isRunningBacktest.value) {
      return
    }
    void runBacktest({ source: 'manual' })
  }

  function handleGenerateParameterSnapshot() {
    if (loading.value || isRunningBacktest.value) {
      return
    }

    const strategyId = resolveCurrentStrategyId()
    if (!strategyId) {
      runtimeNotice.value = '未绑定有效策略ID，无法生成参数快照。'
      runtimeNoticeTone.value = 'warning'
      pushRunLog('未绑定有效策略ID，参数快照生成已跳过。')
      return
    }

    const snapshotParameters = selectedStrategySnapshot.value?.parameters ?? {}
    const optimizationParameters = selectedStrategySnapshot.value?.optimization?.recommendedParameters ?? {}
    const nextSnapshot: GeneratedParameterSnapshot = {
      strategyId,
      strategyLabel: resolveCurrentStrategyLabel(strategyId),
      generatedAt: new Date().toLocaleString(),
      parameterCount: Object.keys(snapshotParameters).length,
      optimizationParameterCount: Object.keys(optimizationParameters).length
    }

    lastGeneratedSnapshot.value = nextSnapshot
    setActiveStrategy(strategyId)
    runtimeNotice.value = `已生成 ${nextSnapshot.strategyLabel} 的上下文快照；仅包含当前策略参数与推荐优化参数，不会创建后端任务。`
    runtimeNoticeTone.value = 'success'
    pushRunLog(
      `参数快照已生成：${nextSnapshot.strategyLabel} · 参数 ${nextSnapshot.parameterCount} 项 · 推荐优化 ${nextSnapshot.optimizationParameterCount} 项。`
    )
  }

  function handleInspectGpuAllocation() {
    if (loading.value || isRunningBacktest.value) {
      return
    }

    runtimeNotice.value = '当前页面未接入 GPU 资源分配 API；如需资源调度，请转到 GPU 调度/监控链路处理，当前只保留真实回测启动入口。'
    runtimeNoticeTone.value = 'warning'
    pushRunLog('GPU 资源分配未在当前页面接入，未执行任何资源调度。')
  }

  async function runBacktest(options: RunBacktestOptions = { source: 'manual' }) {
    if (loading.value || isRunningBacktest.value) {
      return
    }

    const strategyId = resolveCurrentStrategyId()
    if (!strategyId) {
      progress.phase = '等待选择策略'
      progress.percent = 0
      pushRunLog('未绑定有效策略ID，无法启动真实回测。')
      runtimeNotice.value = '未绑定有效策略ID，无法启动真实回测。'
      runtimeNoticeTone.value = 'warning'
      return
    }

    isRunningBacktest.value = true
    if (selectedStrategyId.value !== strategyId) {
      selectedStrategyId.value = strategyId
    }
    setActiveStrategy(strategyId)
    syncSelectedStrategyContext()
    summary.totalRuns += 1
    persistVisibleKpiSummary()
    resetProgressForRun()
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
    runtimeNotice.value = queuedMessage
    runtimeNoticeTone.value = 'warning'

    try {
      const response = await strategyService.startBacktest(strategyId, payload)
      const taskId = extractBacktestTaskId(response)
      const status = extractBacktestTaskStatus(response) ?? 'queued'
      const message = extractBacktestTaskMessage(response) ?? toBacktestStatusMessage(status)

      applyBacktestTaskSnapshot(strategyId, status, message, taskId ?? undefined)
      runtimeNotice.value = message
      runtimeNoticeTone.value = status === 'completed' ? 'success' : status === 'failed' ? 'error' : 'warning'

      if (isBacktestTerminalStatus(status)) {
        if (status === 'completed') {
          await finalizeCompletedBacktest(strategyId, taskId ?? undefined)
          isRunningBacktest.value = false
          runtimeNotice.value = '回测执行完成，结果已进入报告中心。'
          runtimeNoticeTone.value = 'success'
          return
        }
        finalizeBacktest(status, message)
        isRunningBacktest.value = false
        runtimeNotice.value = message
        runtimeNoticeTone.value = 'error'
        return
      }

      if (!taskId) {
        applyBacktestTaskSnapshot(strategyId, 'failed', '回测接口未返回 taskId，无法继续轮询。')
        finalizeBacktest('failed', '回测接口未返回 taskId，无法继续轮询。')
        isRunningBacktest.value = false
        runtimeNotice.value = '回测接口未返回 taskId，无法继续轮询。'
        runtimeNoticeTone.value = 'error'
        return
      }

      await pollBacktestStatusUntilDone(strategyId, taskId, runToken)
    } catch (error) {
      const message = error instanceof Error ? error.message : '启动回测失败'
      applyBacktestTaskSnapshot(strategyId, 'failed', `启动失败：${message}`)
      finalizeBacktest('failed', message)
      isRunningBacktest.value = false
      runtimeNotice.value = `启动失败：${message}`
      runtimeNoticeTone.value = 'error'
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
    syncVisibleKpiSummary()
    syncVisibleTaskRows()
    syncVisibleReportRows()
    syncVisibleExecutionState()
    syncVisibleOptimizationState()

    if (!currentStrategyId) {
      return
    }

    const existingOptionLabel = strategyOptions.value.find((item) => item.value === currentStrategyId)?.label
    const contextLabel = existingOptionLabel || selectedStrategySnapshot.value?.name || `策略 ${currentStrategyId}`
    strategyOptions.value = syncStrategyOptionsWithContext(strategyOptions.value, currentStrategyId, contextLabel)
    config.strategy = currentStrategyId

    if (hasLoaded.value && !activeGeneratedSnapshot.value) {
      runtimeNotice.value = STRATEGY_CONTEXT_SWITCH_NOTICE
      runtimeNoticeTone.value = 'success'
    }
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
    isRunningBacktest.value = false
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

  const executionActionHint = computed(() => {
    if (activeGeneratedSnapshot.value) {
      return `最近快照：${activeGeneratedSnapshot.value.strategyLabel} · ${activeGeneratedSnapshot.value.generatedAt} · 参数 ${activeGeneratedSnapshot.value.parameterCount} 项`
    }

    return '当前任务、KPI 与报告摘要来自策略列表派生视图；只有“立即执行”会调用真实回测接口。'
  })

  return {
    activeTab,
    backtestTasks,
    benchmarkOptions,
    config,
    executionActionHint,
    handleGenerateParameterSnapshot,
    handleInspectGpuAllocation,
    handleRunBacktest,
    hasLoaded,
    loading,
    error,
    isRunningBacktest,
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
    runtimeNotice,
    runtimeNoticeTone,
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
