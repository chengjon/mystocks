<template>
  <div class="strategy-management page-enter">
    <ArtDecoCard class="management-card" variant="bordered">
      <template #header>
        <div class="header-row">
          <h2>策略管理</h2>
          <div class="header-meta">
            <span class="trace-id">REQ_ID: {{ traceRequestId }}</span>
            <span class="trace-id">PROCESS: {{ traceProcessTimeMs }} ms</span>
            <span :class="['source-badge', dataSource]">SOURCE: {{ dataSource.toUpperCase() }}</span>
          </div>
        </div>
      </template>

      <div class="toolbar">
        <input
          v-model.trim="keyword"
          class="toolbar-input"
          type="text"
          placeholder="搜索策略名称 / 类型"
        />
        <select v-model="statusFilter" class="toolbar-select">
          <option value="all">全部状态</option>
          <option value="running">运行中</option>
          <option value="paused">已暂停</option>
          <option value="stopped">已停止</option>
          <option value="error">异常</option>
        </select>
        <button class="toolbar-button" :disabled="loading" @click="refreshStrategies">刷新</button>
        <button class="toolbar-button" :disabled="loading" @click="openCreateForm">
          新建策略
        </button>
      </div>

      <p v-if="error" class="error-tip">{{ error }}</p>
      <div v-if="failedOperation" class="retry-banner">
        <span class="retry-message">{{ failedOperation.message }}</span>
        <div class="retry-actions">
          <button class="toolbar-button" :disabled="retrying" @click="retryFailedOperation">
            {{ retrying ? '重试中...' : '重试' }}
          </button>
          <button class="toolbar-button" :disabled="retrying" @click="dismissFailedOperation">
            忽略
          </button>
        </div>
      </div>

      <div class="table-wrap" v-loading="loading">
        <table class="strategy-table" v-if="pagedStrategies.length">
          <thead>
            <tr>
              <th>策略名称</th>
              <th>类型</th>
              <th>状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="strategy in pagedStrategies" :key="strategy.id">
              <td>
                <div class="name-cell">{{ strategy.name || '-' }}</div>
                <div class="desc-cell">{{ strategy.description || '无描述' }}</div>
              </td>
              <td>{{ strategy.type || '-' }}</td>
              <td>
                <span :class="['status-chip', strategy.status]">
                  {{ formatStatusLabel(strategy.status) }}
                </span>
              </td>
              <td>{{ formatUpdatedTime(strategy.lastRunTime) }}</td>
              <td class="action-cell">
                <button
                  class="action-button start"
                  :disabled="isActionDisabled(strategy, 'start')"
                  @click="handleLifecycleAction(strategy, 'start')"
                >
                  启动
                </button>
                <button
                  class="action-button pause"
                  :disabled="isActionDisabled(strategy, 'pause')"
                  @click="handleLifecycleAction(strategy, 'pause')"
                >
                  暂停
                </button>
                <button
                  class="action-button resume"
                  :disabled="isActionDisabled(strategy, 'resume')"
                  @click="handleLifecycleAction(strategy, 'resume')"
                >
                  恢复
                </button>
                <button
                  class="action-button stop"
                  :disabled="isActionDisabled(strategy, 'stop')"
                  @click="handleLifecycleAction(strategy, 'stop')"
                >
                  停止
                </button>
                <button class="action-button link" :disabled="loading || !strategy.id" @click="navigateToStrategyTab('parameters', strategy.id)">
                  参数
                </button>
                <button class="action-button link" :disabled="loading || !strategy.id" @click="navigateToStrategyTab('signals', strategy.id)">
                  信号
                </button>
                <button class="action-button link" :disabled="loading || !strategy.id" @click="navigateToStrategyTab('backtest', strategy.id)">
                  回测
                </button>
                <button
                  class="action-button quick-backtest"
                  :disabled="loading || !strategy.id || isBacktestRunning(strategy.id)"
                  @click="handleQuickBacktest(strategy)"
                >
                  {{ isBacktestRunning(strategy.id) ? '回测中...' : '快速回测' }}
                </button>
                <button
                  class="action-button edit"
                  :disabled="loading"
                  @click="openEditForm(strategy)"
                >
                  编辑
                </button>
                <button
                  class="action-button delete"
                  :disabled="loading"
                  @click="handleDelete(strategy)"
                >
                  删除
                </button>
                <p v-if="rowFeedback[strategy.id]" class="row-feedback">{{ rowFeedback[strategy.id] }}</p>
                <p
                  v-if="getBacktestStatusLine(strategy.id)"
                  :class="['row-backtest-status', getBacktestStatusClass(strategy.id)]"
                >
                  {{ getBacktestStatusLine(strategy.id) }}
                </p>
                <p v-if="getOptimizationStatusLine(strategy.id)" class="row-optimization-status">
                  {{ getOptimizationStatusLine(strategy.id) }}
                </p>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-else class="empty-state">{{ emptyStateText }}</p>
      </div>

      <div v-if="totalPages > 1" class="pagination-row">
        <button class="toolbar-button" :disabled="currentPage <= 1 || loading" @click="prevPage">上一页</button>
        <span class="pagination-text">第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button class="toolbar-button" :disabled="currentPage >= totalPages || loading" @click="nextPage">下一页</button>
      </div>

      <div v-if="formVisible" class="editor-panel">
        <div class="editor-header">
          <h3>{{ formMode === 'create' ? '创建策略' : '编辑策略' }}</h3>
          <button class="action-button stop" :disabled="submitting" @click="closeForm">关闭</button>
        </div>

        <div class="editor-grid">
          <label class="editor-label">
            <span>策略名称</span>
            <input v-model.trim="formState.name" class="toolbar-input" type="text" placeholder="请输入策略名称" />
          </label>

          <label class="editor-label">
            <span>策略类型</span>
            <select v-model="formState.type" class="toolbar-select">
              <option v-for="item in strategyTypeOptions" :key="item.value" :value="item.value">
                {{ item.label }}
              </option>
            </select>
          </label>
        </div>

        <label class="editor-label">
          <span>描述</span>
          <textarea
            v-model.trim="formState.description"
            class="editor-textarea"
            rows="3"
            placeholder="请输入策略描述"
          />
        </label>

        <div class="parameter-section">
          <div class="parameter-header">
            <span>自定义参数</span>
            <button class="toolbar-button" :disabled="submitting" @click="addParameterRow">添加参数</button>
          </div>

          <div v-if="formState.parameters.length" class="parameter-list">
            <div v-for="(item, index) in formState.parameters" :key="`${index}-${item.key}`" class="parameter-row">
              <input v-model.trim="item.key" class="toolbar-input" type="text" placeholder="参数名" />
              <input v-model.trim="item.value" class="toolbar-input" type="text" placeholder="参数值" />
              <button class="action-button delete" :disabled="submitting" @click="removeParameterRow(index)">
                删除
              </button>
            </div>
          </div>
          <p v-else class="empty-state">暂无参数，点击“添加参数”开始配置。</p>
        </div>

        <div class="editor-actions">
          <button class="toolbar-button" :disabled="submitting" @click="closeForm">取消</button>
          <button class="toolbar-button" :disabled="submitting" @click="submitForm">
            {{ submitting ? '提交中...' : formMode === 'create' ? '创建' : '保存' }}
          </button>
        </div>
      </div>
    </ArtDecoCard>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArtDecoCard } from '@/components/artdeco'
import { useStrategy } from '@/composables/useStrategy'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import type { StrategyListItemVM } from '@/utils/strategy-adapters'
import type {
  CreateStrategyRequestVM as CreateStrategyRequest,
  UpdateStrategyRequestVM as UpdateStrategyRequest,
  StrategyTypeVM
} from '@/api/types/extensions'
import {
  buildStrategyCrossTabRoute,
  buildQuickBacktestRoute,
  type StrategyCrossTabTarget
} from './strategyCrossTabNavigation'

type LifecycleAction = 'start' | 'stop' | 'pause' | 'resume'
type StrategyStatusFilter = 'all' | StrategyListItemVM['status']
type FormMode = 'create' | 'edit'
type FailedOperationType = 'lifecycle' | 'create' | 'update' | 'delete'

interface ParameterFormItem {
  key: string
  value: string
}

interface StrategyFormState {
  id: string
  name: string
  description: string
  type: StrategyTypeVM
  parameters: ParameterFormItem[]
}

interface FailedOperation {
  type: FailedOperationType
  message: string
  strategyId?: string
  action?: LifecycleAction
}

const PAGE_SIZE = 8
const router = useRouter()
const {
  upsertFromStrategyList,
  setParametersSnapshot,
  setStatusSnapshot,
  setBacktestTaskSnapshot,
  removeSnapshot,
  setActiveStrategy,
  getSnapshot
} = useStrategyCrossTabContext()

const DEFAULT_RISK_LIMITS: CreateStrategyRequest['risk_limits'] = {
  daily_pnl_limit: 0.05,
  single_stock_loss_limit: 0.03,
  total_drawdown_limit: 0.15,
  max_holding_period_days: 30,
  max_consecutive_losses: 3,
  max_loss_per_trade: 0.02
}

const DEFAULT_CONSTRAINTS: CreateStrategyRequest['constraints'] = {
  allowed_symbols: [],
  allowed_sectors: [],
  forbidden_symbols: [],
  trading_hours: {
    start: '09:30',
    end: '15:00'
  },
  market_conditions: []
}

const strategyTypeOptions: Array<{ label: string; value: StrategyTypeVM }> = [
  { label: '趋势跟踪', value: 'trend_following' },
  { label: '均值回归', value: 'mean_reversion' },
  { label: '动量策略', value: 'momentum' },
  { label: '突破策略', value: 'breakout' },
  { label: '套利策略', value: 'arbitrage' },
  { label: '统计套利', value: 'statistical_arbitrage' },
  { label: '配对交易', value: 'pairs_trading' },
  { label: '市场中性', value: 'market_neutral' }
]

const {
  strategies,
  loading,
  error,
  dataSource,
  lastRequestId,
  lastProcessTimeMs,
  fetchStrategies,
  startStrategy,
  stopStrategy,
  pauseStrategy,
  resumeStrategy,
  createStrategy,
  updateStrategy,
  deleteStrategy
} = useStrategy(true)

const keyword = ref('')
const statusFilter = ref<StrategyStatusFilter>('all')
const currentPage = ref(1)
const actionKey = ref<string>('')
const formVisible = ref(false)
const formMode = ref<FormMode>('create')
const submitting = ref(false)
const formState = ref<StrategyFormState>(createDefaultForm())
const retrying = ref(false)
const failedOperation = ref<FailedOperation | null>(null)
const rowFeedback = ref<Record<string, string>>({})

const traceRequestId = computed(() => lastRequestId.value || 'N/A')
const traceProcessTimeMs = computed(() => lastProcessTimeMs.value || 'N/A')

const filteredStrategies = computed(() => {
  const search = keyword.value.trim().toLowerCase()
  return strategies.value.filter((strategy) => {
    const matchedStatus = statusFilter.value === 'all' || strategy.status === statusFilter.value
    const matchedKeyword =
      search.length === 0 ||
      strategy.name.toLowerCase().includes(search) ||
      strategy.type.toLowerCase().includes(search)
    return matchedStatus && matchedKeyword
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredStrategies.value.length / PAGE_SIZE)))

const pagedStrategies = computed(() => {
  const offset = (currentPage.value - 1) * PAGE_SIZE
  return filteredStrategies.value.slice(offset, offset + PAGE_SIZE)
})

const emptyStateText = computed(() => {
  return 'REAL 数据为空，请先创建策略。'
})

watch([keyword, statusFilter], () => {
  currentPage.value = 1
})

watch(totalPages, (value) => {
  if (currentPage.value > value) {
    currentPage.value = value
  }
})

watch(
  strategies,
  (items) => {
    upsertFromStrategyList(items as StrategyListItemVM[])
  },
  { immediate: true }
)

function formatStatusLabel(status: StrategyListItemVM['status']): string {
  if (status === 'running') return 'RUNNING'
  if (status === 'paused') return 'PAUSED'
  if (status === 'error') return 'ERROR'
  return 'STOPPED'
}

function formatUpdatedTime(timestamp: string): string {
  if (!timestamp || timestamp === '-') {
    return '-'
  }

  const date = new Date(timestamp)
  if (Number.isNaN(date.getTime())) {
    return timestamp
  }

  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function refreshStrategies() {
  rowFeedback.value = {}
  failedOperation.value = null
  void fetchStrategies()
}

function createDefaultForm(): StrategyFormState {
  return {
    id: '',
    name: '',
    description: '',
    type: 'trend_following',
    parameters: []
  }
}

function openCreateForm() {
  formMode.value = 'create'
  formState.value = createDefaultForm()
  formVisible.value = true
  failedOperation.value = null
  setActiveStrategy(null)
}

function openEditForm(strategy: StrategyListItemVM) {
  formMode.value = 'edit'
  formState.value = {
    id: strategy.id,
    name: strategy.name,
    description: strategy.description || '',
    type: normalizeType(strategy.type),
    parameters: []
  }
  formVisible.value = true
  failedOperation.value = null
  setActiveStrategy(strategy.id)
}

function closeForm() {
  if (submitting.value) {
    return
  }
  formVisible.value = false
  formState.value = createDefaultForm()
  failedOperation.value = null
}

function normalizeType(type: string): StrategyTypeVM {
  const normalized = type as StrategyTypeVM
  if (strategyTypeOptions.some((item) => item.value === normalized)) {
    return normalized
  }
  return 'trend_following'
}

function addParameterRow() {
  formState.value.parameters.push({ key: '', value: '' })
}

function removeParameterRow(index: number) {
  formState.value.parameters.splice(index, 1)
}

function parseParameterValue(value: string): unknown {
  const trimmed = value.trim()
  if (trimmed.length === 0) {
    return ''
  }

  if (trimmed === 'true') {
    return true
  }
  if (trimmed === 'false') {
    return false
  }

  const asNumber = Number(trimmed)
  if (!Number.isNaN(asNumber) && trimmed === String(asNumber)) {
    return asNumber
  }

  if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'))) {
    try {
      return JSON.parse(trimmed)
    } catch {
      return trimmed
    }
  }

  return trimmed
}

function toCustomParameters(): Record<string, unknown> {
  const custom: Record<string, unknown> = {}
  for (const item of formState.value.parameters) {
    if (!item.key) {
      continue
    }
    custom[item.key] = parseParameterValue(item.value)
  }
  return custom
}

async function submitForm() {
  if (!formState.value.name) {
    ElMessage.warning('策略名称不能为空')
    return
  }

  submitting.value = true
  try {
    const customParameters = toCustomParameters()

    if (formMode.value === 'create') {
      const payload: CreateStrategyRequest = {
        name: formState.value.name,
        description: formState.value.description,
        type: formState.value.type,
        parameters: {
          custom: customParameters
        },
        constraints: DEFAULT_CONSTRAINTS,
        risk_limits: DEFAULT_RISK_LIMITS
      }
      const success = await createStrategy(payload)
      if (success) {
        ElMessage.success('策略创建成功')
        failedOperation.value = null
        closeForm()
        await fetchStrategies()
      } else {
        const message = error.value || '策略创建失败'
        ElMessage.error(message)
        failedOperation.value = {
          type: 'create',
          message: `创建策略失败：${message}`
        }
      }
      return
    }

    const payload: UpdateStrategyRequest = {
      id: formState.value.id,
      name: formState.value.name,
      description: formState.value.description,
      parameters: {
        custom: customParameters
      }
    }
    const success = await updateStrategy(formState.value.id, payload)
    if (success) {
      ElMessage.success('策略更新成功')
      failedOperation.value = null
      rowFeedback.value[formState.value.id] = '保存成功'
      setParametersSnapshot(formState.value.id, customParameters)
      setActiveStrategy(formState.value.id)
      closeForm()
      await fetchStrategies()
    } else {
      const message = error.value || '策略更新失败'
      ElMessage.error(message)
      failedOperation.value = {
        type: 'update',
        strategyId: formState.value.id,
        message: `更新策略失败：${message}`
      }
      rowFeedback.value[formState.value.id] = `保存失败：${message}`
    }
  } finally {
    submitting.value = false
  }
}

async function handleDelete(strategy: StrategyListItemVM, skipConfirm = false) {
  const confirmed = skipConfirm ? true : window.confirm(`确认删除策略「${strategy.name}」吗？`)
  if (!confirmed) {
    return
  }

  const success = await deleteStrategy(strategy.id)
  if (success) {
    ElMessage.success('策略删除成功')
    failedOperation.value = null
    delete rowFeedback.value[strategy.id]
    removeSnapshot(strategy.id)
    await fetchStrategies()
  } else {
    const message = error.value || '策略删除失败'
    ElMessage.error(message)
    rowFeedback.value[strategy.id] = `删除失败：${message}`
    failedOperation.value = {
      type: 'delete',
      strategyId: strategy.id,
      message: `删除策略「${strategy.name}」失败：${message}`
    }
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value += 1
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value -= 1
  }
}

function isActionDisabled(strategy: StrategyListItemVM, action: LifecycleAction): boolean {
  if (!strategy.id || loading.value) {
    return true
  }

  if (actionKey.value === `${strategy.id}:${action}`) {
    return true
  }

  if (action === 'start') {
    return strategy.status === 'running'
  }
  if (action === 'pause') {
    return strategy.status === 'paused' || strategy.status === 'stopped'
  }
  if (action === 'resume') {
    return strategy.status !== 'paused'
  }
  if (action === 'stop') {
    return strategy.status === 'stopped'
  }
  return false
}

async function navigateToStrategyTab(target: StrategyCrossTabTarget, strategyId: string) {
  const routeLocation = buildStrategyCrossTabRoute(target, strategyId)
  if (!routeLocation) {
    ElMessage.warning('未找到有效策略ID，无法跳转。')
    return
  }

  setActiveStrategy(strategyId)
  await router.push(routeLocation)
}

async function handleLifecycleAction(strategy: StrategyListItemVM, action: LifecycleAction) {
  if (isActionDisabled(strategy, action)) {
    return
  }

  actionKey.value = `${strategy.id}:${action}`

  try {
    let success = false
    if (action === 'start') {
      success = await startStrategy(strategy.id)
    } else if (action === 'stop') {
      success = await stopStrategy(strategy.id)
    } else if (action === 'pause') {
      success = await pauseStrategy(strategy.id)
    } else {
      success = await resumeStrategy(strategy.id)
    }

    if (success) {
      const actionLabel = getLifecycleActionLabel(action)
      const message = `策略「${strategy.name}」${actionLabel}成功`
      ElMessage.success(message)
      rowFeedback.value[strategy.id] = `${actionLabel}成功`
      failedOperation.value = null
      setStatusSnapshot(strategy.id, mapActionToStatus(action))
      await fetchStrategies()
    } else {
      const actionLabel = getLifecycleActionLabel(action)
      const message = error.value || `策略${actionLabel}失败`
      ElMessage.error(message)
      rowFeedback.value[strategy.id] = `${actionLabel}失败：${message}`
      failedOperation.value = {
        type: 'lifecycle',
        strategyId: strategy.id,
        action,
        message: `策略「${strategy.name}」${actionLabel}失败：${message}`
      }
    }
  } finally {
    actionKey.value = ''
  }
}

function getLifecycleActionLabel(action: LifecycleAction): string {
  if (action === 'start') return '启动'
  if (action === 'stop') return '停止'
  if (action === 'pause') return '暂停'
  return '恢复'
}

function mapActionToStatus(action: LifecycleAction): StrategyListItemVM['status'] {
  if (action === 'start' || action === 'resume') return 'running'
  if (action === 'pause') return 'paused'
  return 'stopped'
}

function isBacktestRunning(strategyId: string): boolean {
  const status = getSnapshot(strategyId)?.backtest?.status
  return status === 'queued' || status === 'running'
}

function formatBacktestStatusLabel(status: 'queued' | 'running' | 'completed' | 'failed'): string {
  if (status === 'queued') {
    return '回测状态：排队中'
  }
  if (status === 'running') {
    return '回测状态：执行中'
  }
  if (status === 'completed') {
    return '回测状态：已完成'
  }
  return '回测状态：失败'
}

function getBacktestStatusClass(strategyId: string): string {
  const status = getSnapshot(strategyId)?.backtest?.status
  if (status === 'queued') return 'queued'
  if (status === 'running') return 'running'
  if (status === 'completed') return 'completed'
  if (status === 'failed') return 'failed'
  return ''
}

function getBacktestStatusLine(strategyId: string): string {
  const backtest = getSnapshot(strategyId)?.backtest
  if (!backtest) {
    return ''
  }

  const statusText = formatBacktestStatusLabel(backtest.status)
  if (backtest.message) {
    return `${statusText} · ${backtest.message}`
  }

  return statusText
}

function getOptimizationStatusLine(strategyId: string): string {
  const optimization = getSnapshot(strategyId)?.optimization
  if (!optimization) {
    return ''
  }

  const timestamp = formatUpdatedTime(optimization.updatedAt)
  return `优化评分：${optimization.score} · 最近回写：${timestamp}`
}

async function handleQuickBacktest(strategy: StrategyListItemVM) {
  if (!strategy.id || loading.value) {
    return
  }

  if (isBacktestRunning(strategy.id)) {
    ElMessage.info('该策略已有回测任务正在执行。')
    return
  }

  const routeLocation = buildQuickBacktestRoute(strategy.id)
  if (!routeLocation) {
    ElMessage.warning('未找到有效策略ID，无法发起快速回测。')
    return
  }

  setActiveStrategy(strategy.id)
  setBacktestTaskSnapshot(strategy.id, {
    status: 'queued',
    message: '已从策略管理发起快速回测',
    updatedAt: new Date().toISOString()
  })
  rowFeedback.value[strategy.id] = '已提交快速回测，正在跳转回测页...'
  await router.push(routeLocation)
}

function dismissFailedOperation() {
  failedOperation.value = null
}

async function retryFailedOperation() {
  if (!failedOperation.value || retrying.value) {
    return
  }

  retrying.value = true
  const currentOperation = failedOperation.value
  try {
    if (currentOperation.type === 'create' || currentOperation.type === 'update') {
      await submitForm()
      return
    }

    if (!currentOperation.strategyId) {
      failedOperation.value = null
      return
    }

    const target = strategies.value.find((item) => item.id === currentOperation.strategyId)
    if (!target) {
      ElMessage.warning('目标策略不存在，已刷新列表。')
      failedOperation.value = null
      await fetchStrategies()
      return
    }

    if (currentOperation.type === 'delete') {
      await handleDelete(target, true)
      return
    }

    if (currentOperation.type === 'lifecycle' && currentOperation.action) {
      await handleLifecycleAction(target, currentOperation.action)
      return
    }

    failedOperation.value = null
  } finally {
    retrying.value = false
  }
}
</script>

<style scoped lang="scss">
@import './styles/ArtDecoStrategyManagement';
</style>
