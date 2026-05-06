import { computed, onMounted, ref } from 'vue'
import {
  tradeApi,
  type ReconciliationImportSourceType,
  type ReconciliationResultsPayload,
  type ReconciliationStatementsPayload,
} from '@/api/trade'
import {
  toReconciliationAccountOptions,
  toReconciliationResultMetrics,
  toReconciliationResultRows,
  toReconciliationSummarySnapshot,
} from './reconciliationDataTransform'

const DEFAULT_PAGE_SIZE = 20

export function useTradeReconciliation() {
  const accountOptions = ref<ReturnType<typeof toReconciliationAccountOptions>>([])
  const selectedAccountId = ref('')
  const sourceType = ref<ReconciliationImportSourceType>('normalized_template')
  const startDate = ref('')
  const endDate = ref('')
  const selectedFile = ref<File | null>(null)
  const importBatchId = ref('')
  const importRowCount = ref(0)
  const statementsPayload = ref<ReconciliationStatementsPayload | null>(null)
  const resultsPayload = ref<ReconciliationResultsPayload | null>(null)
  const loading = ref(false)
  const importing = ref(false)
  const exporting = ref(false)
  const errorMessage = ref('')
  const actionMessage = ref('')

  const hasAccounts = computed(() => accountOptions.value.length > 0)
  const hasImportBatch = computed(() => Boolean(importBatchId.value))
  const statementSummary = computed(() => toReconciliationSummarySnapshot(statementsPayload.value))
  const resultMetrics = computed(() => toReconciliationResultMetrics(resultsPayload.value))
  const resultRows = computed(() => toReconciliationResultRows(resultsPayload.value))
  const statementRows = computed(() => statementsPayload.value?.items ?? [])
  const selectedFileName = computed(() => selectedFile.value?.name || '')
  const pageStatusText = computed(() => {
    if (importing.value) {
      return '导入中'
    }
    if (loading.value) {
      return '同步中'
    }
    if (exporting.value) {
      return '导出中'
    }
    if (errorMessage.value) {
      return '操作异常'
    }
    if (hasImportBatch.value) {
      return '对账结果已生成'
    }
    if (statementsPayload.value) {
      return '账单已加载'
    }
    if (hasAccounts.value) {
      return '待选择账期'
    }
    return '暂无账户'
  })
  const pageStatusType = computed(() => {
    if (errorMessage.value) {
      return 'warning'
    }
    if (hasImportBatch.value) {
      return 'success'
    }
    if (hasAccounts.value) {
      return 'info'
    }
    return 'info'
  })

  const normalizedStartDate = computed(() => startDate.value || undefined)
  const normalizedEndDate = computed(() => endDate.value || undefined)

  const loadStatements = async () => {
    if (!selectedAccountId.value) {
      statementsPayload.value = null
      return
    }

    loading.value = true
    errorMessage.value = ''

    try {
      statementsPayload.value = await tradeApi.getReconciliationStatements({
        accountId: selectedAccountId.value,
        startDate: normalizedStartDate.value,
        endDate: normalizedEndDate.value,
        page: 1,
        pageSize: DEFAULT_PAGE_SIZE,
      })
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '账单加载失败'
      statementsPayload.value = null
    } finally {
      loading.value = false
    }
  }

  const loadResults = async () => {
    if (!selectedAccountId.value || !importBatchId.value) {
      resultsPayload.value = null
      return
    }

    loading.value = true
    errorMessage.value = ''

    try {
      resultsPayload.value = await tradeApi.getReconciliationResults({
        accountId: selectedAccountId.value,
        importBatchId: importBatchId.value,
        startDate: normalizedStartDate.value,
        endDate: normalizedEndDate.value,
        page: 1,
        pageSize: DEFAULT_PAGE_SIZE,
      })
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '对账结果加载失败'
      resultsPayload.value = null
    } finally {
      loading.value = false
    }
  }

  const refresh = async () => {
    await loadStatements()
    if (hasImportBatch.value) {
      await loadResults()
    }
  }

  const bootstrap = async () => {
    loading.value = true
    errorMessage.value = ''

    try {
      const accounts = await tradeApi.getReconciliationAccounts()
      accountOptions.value = toReconciliationAccountOptions(accounts)
      if (!selectedAccountId.value && accountOptions.value.length > 0) {
        selectedAccountId.value = accountOptions.value[0].value
      }
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '对账账户加载失败'
      accountOptions.value = []
    } finally {
      loading.value = false
    }

    if (selectedAccountId.value) {
      await loadStatements()
    }
  }

  const handleAccountChange = async (nextAccountId: string) => {
    selectedAccountId.value = nextAccountId
    await refresh()
  }

  const setSelectedFile = (file: File | null) => {
    selectedFile.value = file
  }

  const importCsv = async () => {
    if (!selectedFile.value) {
      errorMessage.value = '请先选择要导入的 CSV 文件'
      return
    }

    importing.value = true
    errorMessage.value = ''
    actionMessage.value = ''

    try {
      const payload = await tradeApi.importReconciliationCsv({
        file: selectedFile.value,
        sourceType: sourceType.value,
        accountId: selectedAccountId.value || undefined,
      })
      importBatchId.value = payload.importBatchId
      importRowCount.value = payload.rowCount
      if (payload.accountId && payload.accountId !== selectedAccountId.value) {
        selectedAccountId.value = payload.accountId
      }
      actionMessage.value = `已导入 ${payload.rowCount} 条 ${payload.sourceType} 记录`
      await refresh()
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '对账导入失败'
    } finally {
      importing.value = false
    }
  }

  const exportResults = async () => {
    if (!selectedAccountId.value || !importBatchId.value) {
      errorMessage.value = '当前没有可导出的对账结果'
      return
    }

    exporting.value = true
    errorMessage.value = ''

    try {
      const blob = await tradeApi.exportReconciliationResults({
        accountId: selectedAccountId.value,
        importBatchId: importBatchId.value,
        startDate: normalizedStartDate.value,
        endDate: normalizedEndDate.value,
      })
      const objectUrl = URL.createObjectURL(blob)
      const anchor = document.createElement('a')
      anchor.href = objectUrl
      anchor.download = `reconciliation-${selectedAccountId.value.replace(':', '_')}-${importBatchId.value}.csv`
      document.body.appendChild(anchor)
      anchor.click()
      document.body.removeChild(anchor)
      URL.revokeObjectURL(objectUrl)
    } catch (error) {
      errorMessage.value = error instanceof Error ? error.message : '对账导出失败'
    } finally {
      exporting.value = false
    }
  }

  onMounted(() => {
    void bootstrap()
  })

  return {
    actionMessage,
    accountOptions,
    errorMessage,
    exportResults,
    exporting,
    handleAccountChange,
    hasAccounts,
    hasImportBatch,
    importBatchId,
    importCsv,
    importRowCount,
    importing,
    loading,
    pageStatusText,
    pageStatusType,
    refresh,
    resultMetrics,
    resultRows,
    selectedAccountId,
    selectedFileName,
    setSelectedFile,
    sourceType,
    startDate,
    endDate,
    statementRows,
    statementSummary,
  }
}
