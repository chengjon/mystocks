import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { useStrategy } from '@/composables/useStrategy'
import { useStrategyCrossTabContext } from '@/composables/strategy/useStrategyCrossTabContext'
import type { StrategyListItemVM } from '@/utils/strategy-adapters'

import {
  buildStrategyCrossTabRoute,
  buildQuickBacktestRoute,
  type StrategyCrossTabTarget
} from './strategyCrossTabNavigation'
import {
  PAGE_SIZE,
  buildCreateStrategyPayload,
  buildCustomParameters,
  buildUpdateStrategyPayload,
  createDefaultStrategyForm,
  createEditStrategyForm,
  filterStrategies,
  formatBacktestStatusLabel as formatBacktestStatusLabelHelper,
  formatStrategyStatusLabel,
  formatStrategyUpdatedTime,
  getLifecycleActionLabel as getLifecycleActionLabelHelper,
  getStrategyManagementEmptyStateText,
  getTotalPages,
  mapLifecycleActionToStatus as mapLifecycleActionToStatusHelper,
  paginateStrategies,
  strategyTypeOptions,
  type FailedOperation,
  type FormMode,
  type LifecycleAction,
  type StrategyFormState,
  type StrategyStatusFilter
} from './strategyManagementHelpers'

export function useStrategyManagementViewModel() {
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

  const {
    strategies,
    loading,
    error,
    listError,
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
  const formState = ref<StrategyFormState>(createDefaultStrategyForm())
  const retrying = ref(false)
  const failedOperation = ref<FailedOperation | null>(null)
  const rowFeedback = ref<Record<string, string>>({})

  const traceRequestId = computed(() => lastRequestId.value || 'N/A')
  const traceProcessTimeMs = computed(() => lastProcessTimeMs.value || 'N/A')
  const filteredStrategies = computed(() => filterStrategies(strategies.value, keyword.value, statusFilter.value))
  const totalPages = computed(() => getTotalPages(filteredStrategies.value.length, PAGE_SIZE))
  const pagedStrategies = computed(() => paginateStrategies(filteredStrategies.value, currentPage.value, PAGE_SIZE))
  const emptyStateText = computed(() =>
    getStrategyManagementEmptyStateText({
      error: listError.value,
      dataSource: dataSource.value
    })
  )

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
    return formatStrategyStatusLabel(status)
  }

  function formatUpdatedTime(timestamp: string): string {
    return formatStrategyUpdatedTime(timestamp)
  }

  function refreshStrategies() {
    rowFeedback.value = {}
    failedOperation.value = null
    void fetchStrategies()
  }

  function openCreateForm() {
    formMode.value = 'create'
    formState.value = createDefaultStrategyForm()
    formVisible.value = true
    failedOperation.value = null
    setActiveStrategy(null)
  }

  function openEditForm(strategy: StrategyListItemVM) {
    formMode.value = 'edit'
    formState.value = createEditStrategyForm(strategy)
    formVisible.value = true
    failedOperation.value = null
    setActiveStrategy(strategy.id)
  }

  function closeForm() {
    if (submitting.value) {
      return
    }
    formVisible.value = false
    formState.value = createDefaultStrategyForm()
    failedOperation.value = null
  }

  function addParameterRow() {
    formState.value.parameters.push({ key: '', value: '' })
  }

  function removeParameterRow(index: number) {
    formState.value.parameters.splice(index, 1)
  }

  async function submitForm() {
    if (!formState.value.name) {
      ElMessage.warning('策略名称不能为空')
      return
    }

    submitting.value = true
    try {
      const customParameters = buildCustomParameters(formState.value.parameters)

      if (formMode.value === 'create') {
        const payload = buildCreateStrategyPayload(formState.value)
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

      const payload = buildUpdateStrategyPayload(formState.value)
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
    return getLifecycleActionLabelHelper(action)
  }

  function mapActionToStatus(action: LifecycleAction): StrategyListItemVM['status'] {
    return mapLifecycleActionToStatusHelper(action)
  }

  function isBacktestRunning(strategyId: string): boolean {
    const status = getSnapshot(strategyId)?.backtest?.status
    return status === 'queued' || status === 'running'
  }

  function formatBacktestStatusLabel(status: 'queued' | 'running' | 'completed' | 'failed'): string {
    return formatBacktestStatusLabelHelper(status)
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

  return {
    strategies,
    loading,
    error,
    dataSource,
    strategyTypeOptions,
    keyword,
    statusFilter,
    currentPage,
    actionKey,
    formVisible,
    formMode,
    submitting,
    formState,
    retrying,
    failedOperation,
    rowFeedback,
    traceRequestId,
    traceProcessTimeMs,
    filteredStrategies,
    totalPages,
    pagedStrategies,
    emptyStateText,
    formatStatusLabel,
    formatUpdatedTime,
    refreshStrategies,
    openCreateForm,
    openEditForm,
    closeForm,
    addParameterRow,
    removeParameterRow,
    submitForm,
    handleDelete,
    nextPage,
    prevPage,
    isActionDisabled,
    navigateToStrategyTab,
    handleLifecycleAction,
    getLifecycleActionLabel,
    mapActionToStatus,
    isBacktestRunning,
    formatBacktestStatusLabel,
    getBacktestStatusClass,
    getBacktestStatusLine,
    getOptimizationStatusLine,
    handleQuickBacktest,
    dismissFailedOperation,
    retryFailedOperation
  }
}
