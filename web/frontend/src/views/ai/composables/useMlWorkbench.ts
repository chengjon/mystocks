import { computed, reactive, ref } from 'vue'

import {
  getMlRuntimeStatus,
  listMlWorkbenchModels,
  predictMlWorkbenchModel,
  trainMlWorkbenchModel,
  type MlPredictionResult,
  type MlRuntimeStatus,
  type MlTrainingRequest,
  type MlTrainingResult,
  type MlWorkbenchModelFamily,
  type MlWorkbenchModel,
} from '@/api/mlWorkbench.ts'
import type { UnifiedResponse } from '@/api/types/common.ts'

interface ModelFamilyOption {
  value: MlWorkbenchModelFamily
  label: string
  available: boolean
  status: 'available' | 'unavailable'
}

const defaultTrainingForm = (): MlTrainingRequest => ({
  model_family: 'svm',
  symbol: '600519.SH',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  feature_window: 20,
  prediction_horizon: 5,
  parameters: {},
})

const asRecord = (value: unknown): Record<string, unknown> | null => {
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    return value as Record<string, unknown>
  }
  return null
}

const extractMlResponseMessage = (response: UnifiedResponse<unknown>, fallback: string): string => {
  const errors = asRecord(response.errors)
  const detail = errors ? errors.detail : null
  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  const detailRecord = asRecord(detail)
  const detailMessage = detailRecord?.message
  if (typeof detailMessage === 'string' && detailMessage.trim()) {
    return detailMessage
  }

  if (typeof response.message === 'string' && response.message.trim()) {
    return response.message
  }
  return fallback
}

const requireMlResponseData = <T>(response: UnifiedResponse<T>, fallback: string): T => {
  if (!response.success || response.data === null || response.data === undefined) {
    throw new Error(extractMlResponseMessage(response as UnifiedResponse<unknown>, fallback))
  }
  return response.data
}

export function useMlWorkbench() {
  const loading = ref(false)
  const trainingLoading = ref(false)
  const predictionLoading = ref(false)
  const runtimeStatus = ref<MlRuntimeStatus | null>(null)
  const models = ref<MlWorkbenchModel[]>([])
  const selectedModelId = ref('')
  const trainingForm = reactive(defaultTrainingForm())
  const predictionForm = reactive({
    model_id: '',
    symbol: '600519.SH',
    prediction_horizon: 5,
  })
  const lastTrainingResult = ref<MlTrainingResult | null>(null)
  const lastPredictionResult = ref<MlPredictionResult | null>(null)
  const runtimeMessage = ref('')

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

  const modelFamilyOptions = computed<ModelFamilyOption[]>(() => {
    const lightgbmAvailable =
      runtimeStatus.value?.optional_dependencies?.lightgbm?.available === true

    return [
      {
        value: 'svm',
        label: 'SVM',
        available: true,
        status: 'available',
      },
      {
        value: 'lightgbm',
        label: 'LightGBM',
        available: lightgbmAvailable,
        status: lightgbmAvailable ? 'available' : 'unavailable',
      },
    ]
  })

  const selectedModelFamilyBlocked = computed(() => {
    const selectedOption = modelFamilyOptions.value.find(
      (option) => option.value === trainingForm.model_family,
    )
    return selectedOption?.available === false
  })

  const runtimeReadinessPending = computed(() => !runtimeStatus.value)
  const runtimeServiceBlocked = computed(() => runtimeStatus.value?.service_available === false)
  const runtimeSupportsOperation = (operation: string) =>
    !runtimeStatus.value || runtimeStatus.value.supported_operations.includes(operation)
  const trainingOperationBlocked = computed(() => !runtimeSupportsOperation('train'))
  const predictionOperationBlocked = computed(() => !runtimeSupportsOperation('predict'))
  const trainingDateRangeInvalid = computed(() => {
    const startTime = Date.parse(trainingForm.start_date)
    const endTime = Date.parse(trainingForm.end_date)
    return Number.isFinite(startTime) && Number.isFinite(endTime) && startTime >= endTime
  })
  const trainingSymbolBlank = computed(() => trainingForm.symbol.trim().length === 0)
  const selectedPredictionModel = computed(() =>
    models.value.find(
      (model) => model.model_id === predictionForm.model_id.trim(),
    ),
  )
  const predictionSymbolMismatch = computed(() => {
    const selectedModel = selectedPredictionModel.value
    return Boolean(selectedModel && predictionForm.symbol !== selectedModel.symbol)
  })
  const predictionSymbolBlank = computed(() => predictionForm.symbol.trim().length === 0)
  const predictionModelIdBlank = computed(() => predictionForm.model_id.trim().length === 0)
  const predictionHorizonMismatch = computed(() => {
    const selectedModel = selectedPredictionModel.value
    const trainedHorizon = selectedModel?.feature_context?.prediction_horizon
    return Boolean(trainedHorizon && predictionForm.prediction_horizon !== trainedHorizon)
  })

  const refreshRuntime = async () => {
    loading.value = true
    runtimeMessage.value = ''
    let nextRuntimeStatus: MlRuntimeStatus | null = null
    try {
      const [statusResponse, modelsResponse] = await Promise.all([
        getMlRuntimeStatus(),
        listMlWorkbenchModels(),
      ])
      nextRuntimeStatus = requireMlResponseData(statusResponse, 'ML runtime request failed')
      runtimeStatus.value = nextRuntimeStatus
      const modelList = requireMlResponseData(modelsResponse, 'ML model list request failed')
      models.value = modelList.models || []
      syncModelSelection()
    } catch (error) {
      if (!nextRuntimeStatus) {
        runtimeStatus.value = null
      }
      models.value = []
      clearSelectedModel()
      runtimeMessage.value = error instanceof Error ? error.message : 'ML runtime request failed'
    } finally {
      loading.value = false
    }
  }

  const submitTraining = async () => {
    trainingLoading.value = true
    runtimeMessage.value = ''
    lastTrainingResult.value = null
    try {
      if (runtimeReadinessPending.value) {
        throw new Error('请先刷新 ML 运行时状态，再提交训练或预测任务。')
      }
      if (runtimeServiceBlocked.value) {
        throw new Error('ML runtime is unavailable. Please refresh runtime status before submitting work.')
      }
      if (trainingOperationBlocked.value) {
        throw new Error('当前 ML 运行时不支持训练，请刷新运行时状态或检查后端能力。')
      }
      if (trainingDateRangeInvalid.value) {
        throw new Error('训练开始日期必须早于结束日期。')
      }
      if (trainingSymbolBlank.value) {
        throw new Error('训练标的不能为空。')
      }
      if (selectedModelFamilyBlocked.value) {
        throw new Error('当前模型族后端依赖不可用，请先切换模型族或安装对应运行时依赖。')
      }
      const response = await trainMlWorkbenchModel({
        ...trainingForm,
        symbol: trainingForm.symbol.trim(),
      })
      const trainingResult = requireMlResponseData(response, 'ML training failed')
      lastTrainingResult.value = trainingResult
      await refreshRuntime()
      selectModel(trainingResult.model_id)
      predictionForm.symbol = trainingResult.symbol
      if (trainingResult.feature_context?.prediction_horizon) {
        predictionForm.prediction_horizon = trainingResult.feature_context.prediction_horizon
      }
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'ML training failed'
    } finally {
      trainingLoading.value = false
    }
  }

  const submitPrediction = async () => {
    predictionLoading.value = true
    runtimeMessage.value = ''
    lastPredictionResult.value = null
    try {
      if (runtimeReadinessPending.value) {
        throw new Error('请先刷新 ML 运行时状态，再提交训练或预测任务。')
      }
      if (runtimeServiceBlocked.value) {
        throw new Error('ML runtime is unavailable. Please refresh runtime status before submitting work.')
      }
      if (predictionOperationBlocked.value) {
        throw new Error('当前 ML 运行时不支持预测，请刷新运行时状态或检查后端能力。')
      }
      const modelId = predictionForm.model_id.trim()
      if (!modelId) {
        throw new Error('请先选择模型后再执行预测。')
      }
      if (predictionSymbolBlank.value) {
        throw new Error('预测标的不能为空。')
      }
      if (predictionSymbolMismatch.value) {
        throw new Error('预测标的必须与所选模型一致，请重新选择模型或刷新模型列表。')
      }
      if (predictionHorizonMismatch.value) {
        throw new Error('预测周期必须与所选模型一致，请重新选择模型或刷新模型列表。')
      }
      const response = await predictMlWorkbenchModel({
        ...predictionForm,
        model_id: modelId,
        symbol: predictionForm.symbol.trim(),
      })
      lastPredictionResult.value = requireMlResponseData(response, 'ML prediction failed')
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'ML prediction failed'
    } finally {
      predictionLoading.value = false
    }
  }

  function selectModel(modelId: string) {
    selectedModelId.value = modelId
    predictionForm.model_id = modelId
    const selectedModel = models.value.find((model) => model.model_id === modelId)
    if (selectedModel?.symbol) {
      predictionForm.symbol = selectedModel.symbol
    }
    if (selectedModel?.feature_context?.prediction_horizon) {
      predictionForm.prediction_horizon = selectedModel.feature_context.prediction_horizon
    }
  }

  function clearSelectedModel() {
    selectedModelId.value = ''
    predictionForm.model_id = ''
  }

  function syncModelSelection() {
    if (models.value.length === 0) {
      clearSelectedModel()
      return
    }

    const selectedModelStillExists = models.value.some(
      (model) => model.model_id === selectedModelId.value,
    )
    if (!selectedModelStillExists) {
      selectModel(models.value[0].model_id)
    }
  }

  return {
    loading,
    trainingLoading,
    predictionLoading,
    runtimeStatus,
    models,
    selectedModelId,
    trainingForm,
    predictionForm,
    lastTrainingResult,
    lastPredictionResult,
    runtimeMessage,
    readinessLabel,
    readinessClass,
    modelFamilyOptions,
    selectedModelFamilyBlocked,
    runtimeReadinessPending,
    runtimeServiceBlocked,
    trainingOperationBlocked,
    predictionOperationBlocked,
    trainingDateRangeInvalid,
    trainingSymbolBlank,
    predictionSymbolMismatch,
    predictionSymbolBlank,
    predictionModelIdBlank,
    predictionHorizonMismatch,
    refreshRuntime,
    submitTraining,
    submitPrediction,
    selectModel,
  }
}
