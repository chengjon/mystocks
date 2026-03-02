<template>
  <div class="backtest-analysis-page">
    <BacktestHeader
      subtitle="面向策略设计、参数编排、任务调度与结果复盘的一体化工作台"
      :status-text="systemStatus"
      :last-updated="lastUpdated"
      @reset="resetConfig"
      @run="handleRunBacktest"
    />

    <BacktestKpiGrid :items="kpiItems" />

    <section v-if="selectedStrategyId" class="context-strip artdeco-card">
      <span class="context-label">当前策略上下文</span>
      <strong class="context-value">ID {{ selectedStrategyId }}</strong>
      <span v-if="selectedStrategySnapshot" class="context-meta">
        {{ selectedStrategySnapshot.status.toUpperCase() }} · 参数 {{ Object.keys(selectedStrategySnapshot.parameters).length }} 项
      </span>
      <span
        v-if="selectedStrategySnapshot?.backtest"
        :class="['context-backtest', selectedStrategySnapshot.backtest.status]"
      >
        回测 {{ selectedStrategySnapshot.backtest.status.toUpperCase() }}
      </span>
      <span v-if="selectedStrategySnapshot?.optimization" class="context-meta">
        优化评分 {{ selectedStrategySnapshot.optimization.score }}
      </span>
    </section>

    <section class="ops-strip">
      <article v-for="item in opsOverview" :key="item.label" class="ops-item artdeco-card">
        <span class="label">{{ item.label }}</span>
        <strong class="value" :class="item.variant">{{ item.value }}</strong>
        <span class="meta">{{ item.meta }}</span>
      </article>
    </section>

    <BacktestWorkbenchTabs v-model:active-tab="activeTab" :tabs="tabs">
      <section v-if="activeTab === 'designer'" class="tab-panel">
        <div class="panel-grid">
          <ArtDecoCard title="策略骨架" hoverable>
            <div class="metric-list">
              <div v-for="item in strategyMetrics" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.variant">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>

          <ArtDecoCard title="信号流程" hoverable>
            <div class="metric-list">
              <div v-for="item in signalFlow" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>
        </div>
      </section>

      <section v-else-if="activeTab === 'library'" class="tab-panel">
        <ArtDecoCard title="策略库" hoverable>
          <div class="strat-library">
            <div v-for="strategy in strategyLibrary" :key="strategy.name" class="strategy-item">
              <strong class="name">{{ strategy.name }}</strong>
              <span class="meta">{{ strategy.meta }}</span>
            </div>
          </div>
        </ArtDecoCard>
      </section>

      <section v-else-if="activeTab === 'tasks'" class="tab-panel">
        <ArtDecoCard title="回测任务" hoverable>
          <div class="task-list">
            <div v-for="task in backtestTasks" :key="task.name" class="task-item">
              <div class="task-meta">
                <strong class="name">{{ task.name }}</strong>
                <span class="detail">{{ task.detail }}</span>
              </div>
              <span class="status-chip" :class="task.statusClass">{{ task.status }}</span>
            </div>
          </div>
        </ArtDecoCard>
      </section>

      <section v-else-if="activeTab === 'execution'" class="tab-panel">
        <div class="action-row">
          <ArtDecoButton variant="outline" size="sm">生成参数快照</ArtDecoButton>
          <ArtDecoButton variant="outline" size="sm">分配 GPU 资源</ArtDecoButton>
          <ArtDecoButton variant="solid" size="sm" @click="handleRunBacktest">立即执行</ArtDecoButton>
        </div>

        <div class="hub-grid">
          <ArtDecoCard title="配置面板" hoverable>
            <div class="form-grid">
              <div class="field">
                <label class="label">策略模板</label>
                <ArtDecoSelect v-model="config.strategy" :options="strategyOptions" placeholder="选择策略" />
              </div>
              <div class="field">
                <label class="label">回测周期</label>
                <ArtDecoSelect v-model="config.period" :options="periodOptions" placeholder="选择周期" />
              </div>
              <div class="field">
                <label class="label">初始资金</label>
                <ArtDecoInput v-model="config.capital" placeholder="例如 1000000" />
              </div>
              <div class="field">
                <label class="label">对比基准</label>
                <ArtDecoSelect v-model="config.benchmark" :options="benchmarkOptions" placeholder="选择基准" />
              </div>
            </div>
          </ArtDecoCard>

          <ArtDecoCard title="进度面板" hoverable>
            <div class="progress-panel">
              <div class="progress-main">
                <span class="label">当前阶段</span>
                <span class="value">{{ progress.phase }}</span>
              </div>
              <progress class="bar" :value="progress.percent" max="100" />
              <div class="progress-main">
                <span class="label">总体完成</span>
                <span class="value">{{ progress.percent }}%</span>
              </div>
              <div class="step-list">
                <div v-for="step in progress.steps" :key="step.name" class="step-row">
                  <span class="name">{{ step.name }}</span>
                  <span class="status-chip" :class="step.statusClass">{{ step.status }}</span>
                </div>
              </div>
            </div>
          </ArtDecoCard>

          <ArtDecoCard title="日志面板" hoverable class="log-panel">
            <ul class="log-list">
              <li v-for="log in runLogs" :key="log.ts + log.msg" class="log-item">
                <span class="ts">{{ log.ts }}</span>
                <span class="msg">{{ log.msg }}</span>
              </li>
            </ul>
          </ArtDecoCard>
        </div>
      </section>

      <section v-else-if="activeTab === 'optimize'" class="tab-panel">
        <div class="panel-grid">
          <ArtDecoCard title="优化候选" hoverable>
            <ArtDecoTable :columns="optimizeColumns" :data="optimizeRows" />
          </ArtDecoCard>
          <ArtDecoCard title="优化建议" hoverable>
            <div class="metric-list">
              <div v-for="item in optimizeHints" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.variant">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>
        </div>
      </section>

      <section v-else class="tab-panel">
        <div class="panel-grid">
          <ArtDecoCard title="回测报告" hoverable>
            <ArtDecoTable :columns="reportColumns" :data="reportRows" />
          </ArtDecoCard>
          <ArtDecoCard title="报告摘要" hoverable>
            <div class="metric-list">
              <div v-for="item in reportSummary" :key="item.label" class="metric-row">
                <span class="label">{{ item.label }}</span>
                <span class="value" :class="item.variant">{{ item.value }}</span>
              </div>
            </div>
          </ArtDecoCard>
        </div>
      </section>
    </BacktestWorkbenchTabs>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { strategyApi } from '@/api'
import { StrategyApiService } from '@/api/services/strategyService'
import type { BacktestRequestVM } from '@/api/types/extensions'
import { ArtDecoButton, ArtDecoCard, ArtDecoInput, ArtDecoSelect, ArtDecoTable } from '@/components/artdeco'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'
import {
  useStrategyCrossTabContext,
  type StrategyBacktestTaskStatus
} from '@/composables/strategy/useStrategyCrossTabContext'
import {
  createBacktestWorkbenchRealConfig,
  getBacktestWorkbenchConfig,
  type BacktestDataMode,
  type BacktestWorkbenchDataConfig
} from '@/mock/backtestWorkbenchMock'
import {
  extractBacktestTaskId,
  extractBacktestTaskMessage,
  extractBacktestTaskStatus,
  isBacktestTerminalStatus,
  toBacktestStatusMessage
} from './backtestQuickRun'
import { extractQuickRunFlagFromQuery, extractStrategyIdFromQuery } from './strategyCrossTabNavigation'
import BacktestHeader from './components/BacktestHeader.vue'
import BacktestKpiGrid from './components/BacktestKpiGrid.vue'
import BacktestWorkbenchTabs from './components/BacktestWorkbenchTabs.vue'

interface RunBacktestOptions {
  source: 'manual' | 'quick-handoff'
}

interface BacktestTaskRow {
  name: string
  detail: string
  status: string
  statusClass: 'running' | 'queued' | 'done' | 'failed'
}

const BACKTEST_POLL_INTERVAL_MS = 2000
const BACKTEST_MAX_POLLS = 20

const { exec } = useArtDecoApi()
const route = useRoute()
const router = useRouter()
const strategyService = new StrategyApiService()
const { getSnapshot, setActiveStrategy, setBacktestTaskSnapshot } = useStrategyCrossTabContext()
const dataMode: BacktestDataMode = import.meta.env.VITE_USE_MOCK_DATA ? 'mock' : 'real'
const initialConfig = getBacktestWorkbenchConfig(dataMode)

function createDefaultConfig(source: BacktestWorkbenchDataConfig) {
  return {
    strategy: source.strategyOptions[0]?.value ?? 'momentum',
    period: source.periodOptions[1]?.value ?? source.periodOptions[0]?.value ?? '1y',
    capital: '1000000',
    benchmark: source.benchmarkOptions[0]?.value ?? 'csi300'
  }
}

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
const defaultConfig = reactive(createDefaultConfig(initialConfig))
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

  const nextDefaultConfig = createDefaultConfig(nextConfig)
  Object.assign(defaultConfig, nextDefaultConfig)
  resetConfig()
  syncSelectedStrategyContext()
}

async function loadRealConfig() {
  if (dataMode !== 'real') {
    return
  }

  const strategies = await exec(() => strategyApi.getStrategies({}), {
    silent: true,
    errorMsg: '获取REAL策略数据失败，已保留MOCK配置'
  })

  if (!strategies) {
    return
  }

  applyWorkbenchConfig(createBacktestWorkbenchRealConfig(strategies))
}

function toTaskStatusClass(status: StrategyBacktestTaskStatus): BacktestTaskRow['statusClass'] {
  if (status === 'queued') {
    return 'queued'
  }
  if (status === 'running') {
    return 'running'
  }
  if (status === 'completed') {
    return 'done'
  }
  return 'failed'
}

function toTaskStatusLabel(status: StrategyBacktestTaskStatus): string {
  if (status === 'queued') {
    return 'QUEUED'
  }
  if (status === 'running') {
    return 'RUNNING'
  }
  if (status === 'completed') {
    return 'COMPLETED'
  }
  return 'FAILED'
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

function upsertBacktestTaskRow(
  strategyId: string,
  status: StrategyBacktestTaskStatus,
  message: string,
  taskId?: string
) {
  const strategyName = selectedStrategySnapshot.value?.name || `策略 ${strategyId}`
  const detailParts = [message]
  if (taskId) {
    detailParts.unshift(`TASK ${taskId}`)
  }

  const row: BacktestTaskRow = {
    name: strategyName,
    detail: detailParts.filter(Boolean).join(' · '),
    status: toTaskStatusLabel(status),
    statusClass: toTaskStatusClass(status)
  }

  const index = backtestTasks.value.findIndex((item) => item.name === strategyName)
  if (index === -1) {
    backtestTasks.value = [row, ...backtestTasks.value].slice(0, 10)
    return
  }

  backtestTasks.value[index] = row
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
  upsertBacktestTaskRow(strategyId, status, message, taskId)
  syncProgressByStatus(status)
  lastUpdated.value = new Date().toLocaleString()
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

function formatDate(date: Date): string {
  return date.toISOString().slice(0, 10)
}

function resolveBacktestDateRange(period: string): { startDate: string; endDate: string } {
  const endDate = new Date()
  const startDate = new Date(endDate)
  const normalizedPeriod = period.trim().toLowerCase()

  if (normalizedPeriod.endsWith('m')) {
    const monthOffset = Number.parseInt(normalizedPeriod, 10)
    startDate.setMonth(startDate.getMonth() - (Number.isFinite(monthOffset) ? monthOffset : 12))
  } else if (normalizedPeriod.endsWith('y')) {
    const yearOffset = Number.parseInt(normalizedPeriod, 10)
    startDate.setFullYear(startDate.getFullYear() - (Number.isFinite(yearOffset) ? yearOffset : 1))
  } else {
    startDate.setFullYear(startDate.getFullYear() - 1)
  }

  return {
    startDate: formatDate(startDate),
    endDate: formatDate(endDate)
  }
}

function normalizeInitialCapital(raw: string): number {
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return 1_000_000
  }
  return parsed
}

function createBacktestPayload(strategyId: string): BacktestRequestVM {
  const { startDate, endDate } = resolveBacktestDateRange(config.period)
  const optimizationParameters = selectedStrategySnapshot.value?.optimization?.recommendedParameters
  return {
    strategy_id: strategyId,
    symbol: 'ALL',
    start_date: startDate,
    end_date: endDate,
    initial_capital: normalizeInitialCapital(config.capital),
    parameters: {
      benchmark: config.benchmark,
      period: config.period,
      ...(optimizationParameters
        ? {
            optimization_parameters: optimizationParameters
          }
        : {})
    }
  }
}

function getBacktestTargetStrategyId(): string | null {
  if (selectedStrategyId.value) {
    return selectedStrategyId.value
  }

  if (config.strategy && typeof config.strategy === 'string') {
    return config.strategy
  }

  return null
}

function finalizeBacktest(status: StrategyBacktestTaskStatus) {
  if (status === 'completed') {
    pushRunLog('回测任务完成，结果已回写上下文。')
    return
  }

  if (status === 'failed') {
    pushRunLog('回测任务失败，请检查策略参数与后端任务状态。')
  }
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
        finalizeBacktest(status)
        return
      }
    } catch (error) {
      if (index < BACKTEST_MAX_POLLS - 1) {
        continue
      }

      const message = error instanceof Error ? error.message : '轮询回测状态失败'
      applyBacktestTaskSnapshot(strategyId, 'failed', `轮询失败：${message}`, taskId)
      finalizeBacktest('failed')
      return
    }
  }

  applyBacktestTaskSnapshot(strategyId, 'failed', '回测状态轮询超时，请稍后刷新。', taskId)
  finalizeBacktest('failed')
}

function handleRunBacktest() {
  void runBacktest({ source: 'manual' })
}

async function runBacktest(options: RunBacktestOptions = { source: 'manual' }) {
  const strategyId = getBacktestTargetStrategyId()
  if (!strategyId) {
    summary.totalRuns += 1
    progress.percent = Math.min(100, progress.percent + 3)
    lastUpdated.value = new Date().toLocaleString()
    pushRunLog('未绑定有效策略ID，已执行演示态回测。')
    return
  }

  setActiveStrategy(strategyId)
  summary.totalRuns += 1
  const runToken = latestRunToken.value + 1
  latestRunToken.value = runToken
  const payload = createBacktestPayload(strategyId)

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
      finalizeBacktest(status)
      return
    }

    if (!taskId) {
      applyBacktestTaskSnapshot(strategyId, 'failed', '回测接口未返回 taskId，无法继续轮询。')
      finalizeBacktest('failed')
      return
    }

    await pollBacktestStatusUntilDone(strategyId, taskId, runToken)
  } catch (error) {
    const message = error instanceof Error ? error.message : '启动回测失败'
    applyBacktestTaskSnapshot(strategyId, 'failed', `启动失败：${message}`)
    finalizeBacktest('failed')
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
  const hasOption = strategyOptions.value.some((option) => option.value === currentStrategyId)
  if (!hasOption) {
    strategyOptions.value = [
      { label: contextLabel, value: currentStrategyId },
      ...strategyOptions.value
    ]
  } else {
    strategyOptions.value = strategyOptions.value.map((option) => {
      if (option.value !== currentStrategyId) {
        return option
      }
      return { ...option, label: contextLabel }
    })
  }

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

const optimizeColumns = [
  { key: 'name', label: '参数组' },
  { key: 'score', label: '评分' },
  { key: 'annual', label: '年化' },
  { key: 'drawdown', label: '回撤' }
]

const reportColumns = [
  { key: 'name', label: '报告名称' },
  { key: 'period', label: '区间' },
  { key: 'return', label: '收益率' },
  { key: 'drawdown', label: '最大回撤' },
  { key: 'updatedAt', label: '生成时间' }
]
</script>

<style scoped lang="scss">
@import './styles/ArtDecoBacktestAnalysis';
</style>
