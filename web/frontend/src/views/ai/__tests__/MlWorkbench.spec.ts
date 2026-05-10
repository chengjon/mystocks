import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const refreshRuntimeMock = vi.fn().mockResolvedValue(undefined)
const submitTrainingMock = vi.fn().mockResolvedValue(undefined)
const submitPredictionMock = vi.fn().mockResolvedValue(undefined)
const selectModelMock = vi.fn()

const loadingMock = ref(false)
const trainingLoadingMock = ref(false)
const predictionLoadingMock = ref(false)
const runtimeStatusMock = ref({
  service_available: true,
  model_backend: 'runtime_registry',
  optional_dependencies: {
    lightgbm: { available: true, package: 'lightgbm' },
  },
  supported_operations: ['train', 'predict'],
  warnings: [],
})
const modelsMock = ref([
  {
    model_id: 'svm_600519_abc',
    model_family: 'svm',
    symbol: '600519.SH',
    artifact_status: 'runtime_registered',
    feature_context: { feature_window: 20, prediction_horizon: 5 },
    metrics: { training_accuracy: 0.67, validation_score: 0.61 },
    safety: { analytical_output_only: true, disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.' },
  },
])
const selectedModelIdMock = ref('svm_600519_abc')
const trainingFormMock = ref({
  model_family: 'svm',
  symbol: '600519.SH',
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  feature_window: 20,
  prediction_horizon: 5,
  parameters: {},
})
const predictionFormMock = ref({
  model_id: 'svm_600519_abc',
  symbol: '600519.SH',
  prediction_horizon: 5,
})
const lastTrainingResultMock = ref({
  model_id: 'svm_600519_abc',
  metrics: { training_accuracy: 0.67, validation_score: 0.61 },
  safety: { disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.' },
})
const lastPredictionResultMock = ref({
  prediction: { signal: 'buy', expected_return: 0.018 },
  confidence: 0.72,
  safety: { disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.' },
})
const runtimeMessageMock = ref('')
const readinessLabelMock = ref('运行时可用')
const readinessClassMock = ref('is-ready')
const modelFamilyOptionsMock = ref([
  { value: 'svm', label: 'SVM', available: true, status: 'available' },
  { value: 'lightgbm', label: 'LightGBM', available: true, status: 'available' },
])
const selectedModelFamilyBlockedMock = ref(false)
const runtimeReadinessPendingMock = ref(false)
const runtimeServiceBlockedMock = ref(false)
const trainingOperationBlockedMock = ref(false)
const predictionOperationBlockedMock = ref(false)
const trainingDateFormatInvalidMock = ref(false)
const trainingDateRangeInvalidMock = ref(false)
const trainingSymbolBlankMock = ref(false)
const trainingFeatureWindowInvalidMock = ref(false)
const trainingPredictionHorizonInvalidMock = ref(false)
const predictionSymbolMismatchMock = ref(false)
const predictionSymbolBlankMock = ref(false)
const predictionModelIdBlankMock = ref(false)
const predictionHorizonRangeInvalidMock = ref(false)
const predictionHorizonMismatchMock = ref(false)

vi.mock('../composables/useMlWorkbench', () => ({
  useMlWorkbench: () => ({
    loading: loadingMock,
    trainingLoading: trainingLoadingMock,
    predictionLoading: predictionLoadingMock,
    runtimeStatus: runtimeStatusMock,
    models: modelsMock,
    selectedModelId: selectedModelIdMock,
    trainingForm: trainingFormMock,
    predictionForm: predictionFormMock,
    lastTrainingResult: lastTrainingResultMock,
    lastPredictionResult: lastPredictionResultMock,
    runtimeMessage: runtimeMessageMock,
    readinessLabel: readinessLabelMock,
    readinessClass: readinessClassMock,
    modelFamilyOptions: modelFamilyOptionsMock,
    selectedModelFamilyBlocked: selectedModelFamilyBlockedMock,
    runtimeReadinessPending: runtimeReadinessPendingMock,
    runtimeServiceBlocked: runtimeServiceBlockedMock,
    trainingOperationBlocked: trainingOperationBlockedMock,
    predictionOperationBlocked: predictionOperationBlockedMock,
    trainingDateFormatInvalid: trainingDateFormatInvalidMock,
    trainingDateRangeInvalid: trainingDateRangeInvalidMock,
    trainingSymbolBlank: trainingSymbolBlankMock,
    trainingFeatureWindowInvalid: trainingFeatureWindowInvalidMock,
    trainingPredictionHorizonInvalid: trainingPredictionHorizonInvalidMock,
    predictionSymbolMismatch: predictionSymbolMismatchMock,
    predictionSymbolBlank: predictionSymbolBlankMock,
    predictionModelIdBlank: predictionModelIdBlankMock,
    predictionHorizonRangeInvalid: predictionHorizonRangeInvalidMock,
    predictionHorizonMismatch: predictionHorizonMismatchMock,
    refreshRuntime: refreshRuntimeMock,
    submitTraining: submitTrainingMock,
    submitPrediction: submitPredictionMock,
    selectModel: selectModelMock,
  }),
}))

import MlWorkbench from '../MlWorkbench.vue'

describe('AI ML workbench page', () => {
  beforeEach(() => {
    refreshRuntimeMock.mockClear()
    submitTrainingMock.mockClear()
    submitPredictionMock.mockClear()
    selectModelMock.mockClear()
    modelsMock.value = [
      {
        model_id: 'svm_600519_abc',
        model_family: 'svm',
        symbol: '600519.SH',
        artifact_status: 'runtime_registered',
        feature_context: { feature_window: 20, prediction_horizon: 5 },
        metrics: { training_accuracy: 0.67, validation_score: 0.61 },
        safety: { analytical_output_only: true, disclaimer: 'ML predictions are analytical outputs, not a trade instruction or execution fact.' },
      },
    ]
    runtimeMessageMock.value = ''
    selectedModelIdMock.value = 'svm_600519_abc'
    trainingFormMock.value.model_family = 'svm'
    predictionFormMock.value.model_id = 'svm_600519_abc'
    predictionFormMock.value.symbol = '600519.SH'
    predictionFormMock.value.prediction_horizon = 5
    modelFamilyOptionsMock.value = [
      { value: 'svm', label: 'SVM', available: true, status: 'available' },
      { value: 'lightgbm', label: 'LightGBM', available: true, status: 'available' },
    ]
    selectedModelFamilyBlockedMock.value = false
    runtimeReadinessPendingMock.value = false
    runtimeServiceBlockedMock.value = false
    trainingOperationBlockedMock.value = false
    predictionOperationBlockedMock.value = false
    trainingDateFormatInvalidMock.value = false
    trainingDateRangeInvalidMock.value = false
    trainingSymbolBlankMock.value = false
    trainingFeatureWindowInvalidMock.value = false
    trainingPredictionHorizonInvalidMock.value = false
    predictionSymbolMismatchMock.value = false
    predictionSymbolBlankMock.value = false
    predictionModelIdBlankMock.value = false
    predictionHorizonRangeInvalidMock.value = false
    predictionHorizonMismatchMock.value = false
  })

  it('loads runtime status on mount and renders canonical safety copy', async () => {
    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(refreshRuntimeMock).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('模型训练 / 预测')
    expect(wrapper.text()).toContain('运行时可用')
    expect(wrapper.text()).toContain('not a trade instruction')
    expect(wrapper.text()).toContain('svm_600519_abc')
  })

  it('wires training, model selection, and prediction actions', async () => {
    const wrapper = mount(MlWorkbench as never)

    await flushPromises()
    await wrapper.get('[data-testid="ml-train-submit"]').trigger('click')
    await wrapper.get('[data-testid="ml-model-row"]').trigger('click')
    await wrapper.get('[data-testid="ml-predict-submit"]').trigger('click')

    expect(submitTrainingMock).toHaveBeenCalledTimes(1)
    expect(selectModelMock).toHaveBeenCalledWith('svm_600519_abc')
    expect(submitPredictionMock).toHaveBeenCalledTimes(1)
  })

  it('renders empty and error states without hiding the safety boundary', async () => {
    modelsMock.value = []
    runtimeMessageMock.value = 'runtime unavailable'
    selectedModelIdMock.value = ''

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('暂无运行时模型')
    expect(wrapper.text()).toContain('runtime unavailable')
    expect(wrapper.text()).toContain('not a trade instruction')
  })

  it('surfaces unavailable LightGBM backend before training submission', async () => {
    modelFamilyOptionsMock.value = [
      { value: 'svm', label: 'SVM', available: true, status: 'available' },
      { value: 'lightgbm', label: 'LightGBM', available: false, status: 'unavailable' },
    ]
    trainingFormMock.value.model_family = 'lightgbm'
    selectedModelFamilyBlockedMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    const lightgbmOption = wrapper.get('[data-testid="ml-model-family-lightgbm"]')
    expect(lightgbmOption.attributes('disabled')).toBeDefined()
    expect(wrapper.text()).toContain('当前模型族后端依赖不可用')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces invalid training date range before training submission', async () => {
    trainingDateRangeInvalidMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('训练开始日期必须早于结束日期')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces invalid training date format before training submission', async () => {
    trainingDateFormatInvalidMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('训练日期格式必须为 YYYY-MM-DD')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces blank training symbol before training submission', async () => {
    trainingSymbolBlankMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('训练标的不能为空')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces invalid training numeric ranges before training submission', async () => {
    trainingFeatureWindowInvalidMock.value = true
    trainingPredictionHorizonInvalidMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('特征窗口必须介于 5 到 120')
    expect(wrapper.text()).toContain('训练预测周期必须介于 1 到 30')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
  })

  it('disables train and predict actions when runtime service is blocked', async () => {
    runtimeServiceBlockedMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces selected model and prediction symbol mismatch before prediction submission', async () => {
    predictionSymbolMismatchMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('预测标的必须与所选模型一致')
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces blank prediction symbol before prediction submission', async () => {
    predictionSymbolBlankMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('预测标的不能为空')
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces blank prediction model id before prediction submission', async () => {
    predictionFormMock.value.model_id = '   '
    predictionModelIdBlankMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('请先选择模型')
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('disables prediction when model id input is cleared even if a model row remains selected', async () => {
    selectedModelIdMock.value = 'svm_600519_abc'
    predictionFormMock.value.model_id = ''
    predictionModelIdBlankMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('请先选择模型')
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces prediction horizon range errors before prediction submission', async () => {
    predictionHorizonRangeInvalidMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('预测周期必须介于 1 到 30')
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('surfaces selected model and prediction horizon mismatch before prediction submission', async () => {
    predictionHorizonMismatchMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('预测周期必须与所选模型一致')
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('disables unsupported runtime operations before submission', async () => {
    trainingOperationBlockedMock.value = true
    predictionOperationBlockedMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('当前 ML 运行时不支持训练')
    expect(wrapper.text()).toContain('当前 ML 运行时不支持预测')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })

  it('disables train and predict actions while runtime readiness is pending', async () => {
    runtimeReadinessPendingMock.value = true

    const wrapper = mount(MlWorkbench as never)

    await flushPromises()

    expect(wrapper.text()).toContain('请先刷新 ML 运行时状态')
    expect(wrapper.get('[data-testid="ml-train-submit"]').attributes('disabled')).toBeDefined()
    expect(wrapper.get('[data-testid="ml-predict-submit"]').attributes('disabled')).toBeDefined()
  })
})
