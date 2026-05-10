import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const refreshRuntimeMock = vi.fn().mockResolvedValue(undefined)
const submitTaskMock = vi.fn().mockResolvedValue(undefined)
const selectTaskMock = vi.fn().mockResolvedValue(undefined)

const loadingMock = ref(false)
const submittingMock = ref(false)
const runtimeStatusMock = ref({
  service_available: true,
  runtime_backend: 'runtime_batch_registry',
  max_symbols: 20,
  supported_operations: ['batch_backtest', 'batch_screening', 'batch_monitoring'],
  evidence_modules: ['src/ml_strategy/backtest/backtest_engine.py'],
  warnings: [],
  safety: {
    analytical_output_only: true,
    disclaimer: 'Batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.',
  },
})
const taskMock = {
  task_id: 'batch_abc',
  operation: 'batch_screening',
  symbols: ['600519.SH', '000001.SZ'],
  status: 'completed',
  summary: {
    total_symbols: 2,
    completed_symbols: 2,
    failed_symbols: 0,
    candidate_count: 1,
    average_score: 0.66,
  },
  results: [
    { symbol: '600519.SH', status: 'completed', score: 0.72, signal: 'candidate', metrics: {} },
    { symbol: '000001.SZ', status: 'completed', score: 0.58, signal: 'watch', metrics: {} },
  ],
  warnings: [],
  safety: {
    analytical_output_only: true,
    disclaimer: 'Batch analysis outputs are analytical evidence, not automated trading or scheduler mutation.',
  },
}
const tasksMock = ref([taskMock])
const selectedTaskMock = ref(taskMock)
const runtimeMessageMock = ref('')
const symbolInputMock = ref('600519.SH, 000001.SZ')
const formMock = ref({
  operation: 'batch_screening',
  symbols: ['600519.SH', '000001.SZ'],
  start_date: '2024-01-01',
  end_date: '2024-12-31',
  options: {},
})
const readinessLabelMock = ref('运行时可用')
const readinessClassMock = ref('is-ready')
const maxSymbolsLabelMock = ref(20)

vi.mock('../composables/useBatchAnalysisWorkbench', () => ({
  useBatchAnalysisWorkbench: () => ({
    loading: loadingMock,
    submitting: submittingMock,
    runtimeStatus: runtimeStatusMock,
    tasks: tasksMock,
    selectedTask: selectedTaskMock,
    runtimeMessage: runtimeMessageMock,
    symbolInput: symbolInputMock,
    form: formMock,
    readinessLabel: readinessLabelMock,
    readinessClass: readinessClassMock,
    maxSymbolsLabel: maxSymbolsLabelMock,
    refreshRuntime: refreshRuntimeMock,
    submitTask: submitTaskMock,
    selectTask: selectTaskMock,
  }),
}))

import BatchAnalysis from '../BatchAnalysis.vue'

describe('AI batch analysis workbench page', () => {
  beforeEach(() => {
    refreshRuntimeMock.mockClear()
    submitTaskMock.mockClear()
    selectTaskMock.mockClear()
    tasksMock.value = [taskMock]
    selectedTaskMock.value = taskMock
    runtimeMessageMock.value = ''
  })

  it('loads runtime status on mount and renders safety copy', async () => {
    const wrapper = mount(BatchAnalysis as never)

    await flushPromises()

    expect(refreshRuntimeMock).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('批量分析')
    expect(wrapper.text()).toContain('运行时可用')
    expect(wrapper.text()).toContain('not automated trading')
    expect(wrapper.text()).toContain('batch_abc')
    expect(wrapper.text()).toContain('600519.SH')
  })

  it('wires submit and task selection actions', async () => {
    const wrapper = mount(BatchAnalysis as never)

    await flushPromises()
    await wrapper.get('[data-testid="batch-analysis-submit"]').trigger('click')
    await wrapper.get('[data-testid="batch-analysis-task-row"]').trigger('click')

    expect(submitTaskMock).toHaveBeenCalledTimes(1)
    expect(selectTaskMock).toHaveBeenCalledWith('batch_abc')
  })

  it('renders empty and error states without hiding the safety boundary', async () => {
    tasksMock.value = []
    selectedTaskMock.value = null
    runtimeMessageMock.value = 'runtime unavailable'

    const wrapper = mount(BatchAnalysis as never)

    await flushPromises()

    expect(wrapper.text()).toContain('暂无批量分析任务')
    expect(wrapper.text()).toContain('runtime unavailable')
    expect(wrapper.text()).toContain('not automated trading')
  })
})
