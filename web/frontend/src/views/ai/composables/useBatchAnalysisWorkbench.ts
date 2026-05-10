import { computed, reactive, ref } from 'vue'

import {
  getBatchAnalysisRuntimeStatus,
  getBatchAnalysisTaskDetail,
  listBatchAnalysisTasks,
  submitBatchAnalysisTask,
  type BatchAnalysisRequest,
  type BatchAnalysisRuntimeStatus,
  type BatchAnalysisTask,
} from '@/api/batchAnalysis.ts'

const defaultForm = (): BatchAnalysisRequest => ({
  operation: 'batch_screening',
  symbols: ['600519.SH', '000001.SZ', '510300.SH'],
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  options: {},
})

export function useBatchAnalysisWorkbench() {
  const loading = ref(false)
  const submitting = ref(false)
  const runtimeStatus = ref<BatchAnalysisRuntimeStatus | null>(null)
  const tasks = ref<BatchAnalysisTask[]>([])
  const selectedTask = ref<BatchAnalysisTask | null>(null)
  const runtimeMessage = ref('')
  const symbolInput = ref(defaultForm().symbols.join(', '))
  const form = reactive(defaultForm())

  const readinessLabel = computed(() => {
    if (!runtimeStatus.value) {
      return '运行时待检查'
    }
    return runtimeStatus.value.service_available ? '运行时可用' : '运行时不可用'
  })

  const readinessClass = computed(() => {
    if (!runtimeStatus.value) {
      return 'is-pending'
    }
    return runtimeStatus.value.service_available ? 'is-ready' : 'is-blocked'
  })

  const maxSymbolsLabel = computed(() => runtimeStatus.value?.max_symbols ?? 20)

  const refreshRuntime = async () => {
    loading.value = true
    runtimeMessage.value = ''
    try {
      const [statusResponse, tasksResponse] = await Promise.all([
        getBatchAnalysisRuntimeStatus(),
        listBatchAnalysisTasks(),
      ])
      runtimeStatus.value = statusResponse.data
      tasks.value = tasksResponse.data?.tasks || []
      if (!selectedTask.value && tasks.value.length > 0) {
        await selectTask(tasks.value[0].task_id)
      }
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'Batch analysis runtime request failed'
    } finally {
      loading.value = false
    }
  }

  const submitTask = async () => {
    submitting.value = true
    runtimeMessage.value = ''
    try {
      const symbols = symbolInput.value.split(',').map((item) => item.trim()).filter(Boolean)
      const response = await submitBatchAnalysisTask({ ...form, symbols })
      selectedTask.value = response.data
      await refreshRuntime()
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'Batch analysis submit failed'
    } finally {
      submitting.value = false
    }
  }

  async function selectTask(taskId: string) {
    const response = await getBatchAnalysisTaskDetail(taskId)
    selectedTask.value = response.data
  }

  return {
    loading,
    submitting,
    runtimeStatus,
    tasks,
    selectedTask,
    runtimeMessage,
    symbolInput,
    form,
    readinessLabel,
    readinessClass,
    maxSymbolsLabel,
    refreshRuntime,
    submitTask,
    selectTask,
  }
}
