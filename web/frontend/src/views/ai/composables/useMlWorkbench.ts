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

  const refreshRuntime = async () => {
    loading.value = true
    runtimeMessage.value = ''
    try {
      const [statusResponse, modelsResponse] = await Promise.all([
        getMlRuntimeStatus(),
        listMlWorkbenchModels(),
      ])
      runtimeStatus.value = statusResponse.data
      models.value = modelsResponse.data?.models || []
      if (!selectedModelId.value && models.value.length > 0) {
        selectModel(models.value[0].model_id)
      }
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'ML runtime request failed'
    } finally {
      loading.value = false
    }
  }

  const submitTraining = async () => {
    trainingLoading.value = true
    runtimeMessage.value = ''
    try {
      const response = await trainMlWorkbenchModel({ ...trainingForm })
      lastTrainingResult.value = response.data
      await refreshRuntime()
      selectModel(response.data.model_id)
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'ML training failed'
    } finally {
      trainingLoading.value = false
    }
  }

  const submitPrediction = async () => {
    predictionLoading.value = true
    runtimeMessage.value = ''
    try {
      const modelId = predictionForm.model_id || selectedModelId.value
      const response = await predictMlWorkbenchModel({
        ...predictionForm,
        model_id: modelId,
      })
      lastPredictionResult.value = response.data
    } catch (error) {
      runtimeMessage.value = error instanceof Error ? error.message : 'ML prediction failed'
    } finally {
      predictionLoading.value = false
    }
  }

  function selectModel(modelId: string) {
    selectedModelId.value = modelId
    predictionForm.model_id = modelId
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
    refreshRuntime,
    submitTraining,
    submitPrediction,
    selectModel,
  }
}
