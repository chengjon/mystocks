import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  apiGetMock,
  getBacktestResultMock,
  getBacktestStatusMock,
  getSnapshotMock,
  getStrategiesMock,
  loadingMock,
  routeMock,
  routerReplaceMock,
  setActiveStrategyMock,
  setBacktestTaskSnapshotMock,
  startBacktestMock,
} = vi.hoisted(() => ({
  apiGetMock: vi.fn(),
  getBacktestResultMock: vi.fn(),
  getBacktestStatusMock: vi.fn(),
  getSnapshotMock: vi.fn(),
  getStrategiesMock: vi.fn(),
  loadingMock: require('vue').ref(false),
  routeMock: require('vue').reactive({ query: {} as Record<string, unknown> }),
  routerReplaceMock: vi.fn(),
  setActiveStrategyMock: vi.fn(),
  setBacktestTaskSnapshotMock: vi.fn(),
  startBacktestMock: vi.fn(),
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
  useRouter: () => ({ replace: routerReplaceMock }),
}))

vi.mock('@/api', () => ({
  strategyApi: {
    getStrategies: getStrategiesMock,
  },
}))

vi.mock('@/api/apiClient.ts', () => ({
  apiClient: {
    get: apiGetMock,
  },
}))

vi.mock('@/api/services/strategyService', () => ({
  StrategyApiService: class StrategyApiService {
    startBacktest = startBacktestMock
    getBacktestStatus = getBacktestStatusMock
    getBacktestResult = getBacktestResultMock
  },
}))

vi.mock('@/composables/strategy/useStrategyCrossTabContext', () => ({
  useStrategyCrossTabContext: () => ({
    getSnapshot: getSnapshotMock,
    setActiveStrategy: setActiveStrategyMock,
    setBacktestTaskSnapshot: setBacktestTaskSnapshotMock,
  }),
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => ({
    loading: loadingMock,
    error: require('vue').ref(null),
    exec: async (apiCall: () => Promise<unknown>) => {
      loadingMock.value = true
      try {
        const response = await apiCall()
        return (response as { data?: unknown })?.data ?? response
      } finally {
        loadingMock.value = false
      }
    },
  }),
}))

vi.mock('@/components/artdeco', () => ({
  ArtDecoBadge: {
    props: ['text'],
    template: '<span>{{ text }}</span>',
  },
  ArtDecoButton: {
    props: ['disabled'],
    emits: ['click'],
    template: '<button v-bind="$attrs" :disabled="disabled" @click="$emit(\'click\', $event)"><slot /></button>',
  },
  ArtDecoCard: {
    template: '<section><slot /></section>',
  },
  ArtDecoInput: {
    props: ['modelValue'],
    emits: ['update:modelValue'],
    template: '<input :value="modelValue" @input="$emit(\'update:modelValue\', $event.target.value)" />',
  },
  ArtDecoSelect: {
    props: ['modelValue', 'options'],
    emits: ['update:modelValue'],
    template: `
      <select :value="modelValue" @change="$emit('update:modelValue', $event.target.value)">
        <option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option>
      </select>
    `,
  },
  ArtDecoTable: {
    props: ['data'],
    template: `
      <div>
        <div v-for="row in data" :key="row.name">{{ row.name }}</div>
      </div>
    `,
  },
}))

import ArtDecoBacktestAnalysis from '../ArtDecoBacktestAnalysis.vue'

function mountPage() {
  return mount(ArtDecoBacktestAnalysis as never, {
    global: {
      stubs: {
        BacktestHeader: {
          emits: ['run'],
          template: '<section><button class="run-backtest" @click="$emit(\'run\')">启动回测</button></section>',
        },
        BacktestKpiGrid: true,
        BacktestWorkbenchTabs: {
          props: ['activeTab'],
          emits: ['update:activeTab'],
          template: `
            <section>
              <button class="switch-reports-tab" @click="$emit('update:activeTab', 'reports')">报告中心</button>
              <slot />
            </section>
          `,
        },
      },
    },
  })
}

describe('ArtDecoBacktestAnalysis attribution bridge', () => {
  beforeEach(() => {
    apiGetMock.mockReset()
    getBacktestResultMock.mockReset()
    getBacktestStatusMock.mockReset()
    getSnapshotMock.mockReset().mockReturnValue(null)
    getStrategiesMock.mockReset()
    loadingMock.value = false
    routeMock.query = {}
    routerReplaceMock.mockReset()
    setActiveStrategyMock.mockReset()
    setBacktestTaskSnapshotMock.mockReset()
    startBacktestMock.mockReset()
  })

  it('loads attribution from the selected backtest report row', async () => {
    getStrategiesMock.mockResolvedValue({
      success: true,
      data: [{ id: 101, name: '均线突破策略', status: 'active', parameters: { lookback: 20 } }],
    })
    startBacktestMock.mockResolvedValue({
      success: true,
      data: { task_id: 'bt-task-42', status: 'completed', message: '回测完成' },
    })
    getBacktestResultMock.mockResolvedValue({
      success: true,
      data: {
        id: 42,
        backtest_id: 42,
        strategy_name: '均线突破策略',
        start_date: '2026-01-01',
        end_date: '2026-02-01',
        total_return: 0.128,
        completed_at: '2026-02-02T09:30:00',
        performance: { max_drawdown: -0.041 },
      },
    })
    apiGetMock.mockResolvedValue({
      success: true,
      request_id: 'req-backtest-attribution-42',
      data: {
        analysis_date: '2026-02-02',
        brinson: {
          allocation_effect: 0.011,
          selection_effect: 0.017,
          interaction_effect: -0.002,
        },
        factor_attribution: {
          factor_exposures: { value: { portfolio_exposure: 0.4, benchmark_exposure: 0.2, active_exposure: 0.2 } },
          factor_contributions: { value: 0.012 },
          specific_return: 0.006,
        },
      },
    })

    const wrapper = mountPage()

    await flushPromises()
    await wrapper.find('.run-backtest').trigger('click')
    await flushPromises()
    await wrapper.find('.switch-reports-tab').trigger('click')
    await flushPromises()

    const attributionButton = wrapper.get('[data-testid="backtest-attribution-42"]')
    await attributionButton.trigger('click')
    await flushPromises()

    expect(apiGetMock).toHaveBeenCalledWith('/v1/backtest/42/attribution')
    expect(wrapper.text()).toContain('回测归因')
    expect(wrapper.text()).toContain('Brinson 归因')
    expect(wrapper.text()).toContain('五因子归因')
    expect(wrapper.text()).toContain('req-backtest-attribution-42')
  })
})
