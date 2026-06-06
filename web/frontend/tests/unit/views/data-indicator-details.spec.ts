import { computed, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import DataAdvancedPage from '@/views/data/Advanced.vue'

const detailIndicator = {
  id: 1,
  name: '移动平均线',
  key: 'ma',
  category: 'trend',
  categoryLabel: '趋势',
  type: '主图',
  description: '用于观察价格趋势与支撑阻力。',
  params: [
    { name: 'timeperiod', default: 5 },
    { name: 'slowperiod', default: 10 },
    { name: 'signalperiod', default: 20 },
  ],
}

vi.mock('@/composables/market/useDataAnalysis', () => ({
  useDataAnalysis: () => ({
    activeTab: ref('editor'),
    activeCategory: ref('trend'),
    loading: ref(false),
    error: ref(null),
    staleError: ref(''),
    hasLoaded: ref(true),
    hasExecutedScreening: ref(false),
    lastUpdateTime: ref('2026/04/27 09:30:00'),
    stats: ref({
      availableIndicators: 23,
      customIndicators: 0,
      screenedStocks: 0,
      screeningTimes: 0,
      qualifiedStocks: 0,
      qualifiedChange: 0,
    }),
    technicalIndicatorScreeningSupported: false,
    technicalIndicatorSupportMessage: '当前股票池数据未包含可执行的技术指标值，技术指标条件暂不支持参与筛选。',
    selectedIndicator: ref(detailIndicator),
    selectedStock: ref(null),
    indicatorCategories: ref([
      { key: 'trend', label: '趋势', icon: '📈' },
    ]),
    indicators: ref([detailIndicator]),
    filteredIndicators: computed(() => [detailIndicator]),
    screeningFilters: ref({ indicators: [] }),
    screeningResults: ref([]),
    availableIndicatorsForFilter: ref([{ label: 'MA', value: 'ma' }]),
    switchTab: vi.fn(),
    refreshData: vi.fn(),
    runScreening: vi.fn(),
    resetFilters: vi.fn(),
    setSelectedIndicator: vi.fn(),
    setSelectedStock: vi.fn(),
  }),
}))

describe('Data indicator detail workspace', () => {
  it('renders a real indicator detail panel instead of upgrade-placeholder copy', () => {
    const wrapper = mount(DataAdvancedPage as never, {
      global: {
        stubs: {
          ArtDecoButton: {
            emits: ['click'],
            template: '<button @click="$emit(\'click\')"><slot /></button>',
          },
          ArtDecoCard: {
            props: ['title'],
            template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
          },
          ArtDecoStatCard: {
            props: ['label', 'value'],
            template: '<div>{{ label }}:{{ value }}</div>',
          },
          AnalysisIndicators: {
            template: '<div />',
          },
          AnalysisScreener: {
            template: '<div />',
          },
          AnalysisResults: {
            template: '<div />',
          },
        },
      },
    })

    expect(wrapper.text()).toContain('指标详情')
    expect(wrapper.text()).toContain('移动平均线')
    expect(wrapper.text()).toContain('MA')
    expect(wrapper.text()).toContain('参数')
    expect(wrapper.text()).toContain('当前分类指标:1')
    expect(wrapper.text()).toContain('timeperiod(5)')
    expect(wrapper.text()).not.toContain('自定义指标')
    expect(wrapper.text()).not.toContain('公式编辑器升级中')
    expect(wrapper.text()).not.toContain('[object Object]')
  })
})
