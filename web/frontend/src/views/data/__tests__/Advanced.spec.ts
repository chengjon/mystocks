import { computed, ref } from 'vue'
import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const analysisState = vi.hoisted(() => ({
  activeTab: null as any,
  activeCategory: null as any,
  loading: null as any,
  error: null as any,
  staleError: null as any,
  hasLoaded: null as any,
  hasExecutedScreening: null as any,
  lastUpdateTime: null as any,
  stats: null as any,
  selectedIndicator: null as any,
  selectedStock: null as any,
  indicatorCategories: null as any,
  indicators: null as any,
  screeningFilters: null as any,
  screeningResults: null as any,
  availableIndicatorsForFilter: null as any,
  switchTab: vi.fn(),
  refreshData: vi.fn(),
  runScreening: vi.fn(),
  resetFilters: vi.fn(),
  setSelectedIndicator: vi.fn(),
  setSelectedStock: vi.fn(),
}))

analysisState.activeTab = ref('indicators')
analysisState.activeCategory = ref('trend')
analysisState.loading = ref(false)
analysisState.error = ref<string | null>(null)
analysisState.staleError = ref('')
analysisState.hasLoaded = ref(true)
analysisState.hasExecutedScreening = ref(false)
analysisState.lastUpdateTime = ref('2026/04/30 13:43:18')
analysisState.stats = ref({
  availableIndicators: 0,
  customIndicators: 0,
  screenedStocks: 0,
  screeningTimes: 0,
  qualifiedStocks: 0,
  qualifiedChange: 0,
})
analysisState.selectedIndicator = ref(null)
analysisState.selectedStock = ref(null)
analysisState.indicatorCategories = ref([{ key: 'trend', label: '趋势', icon: '📈' }])
analysisState.indicators = ref<any[]>([])
analysisState.screeningFilters = ref({ indicators: [] })
analysisState.screeningResults = ref<any[]>([])
analysisState.availableIndicatorsForFilter = ref<any[]>([])

vi.mock('@/composables/market/useDataAnalysis', () => ({
  useDataAnalysis: () => ({
    activeTab: analysisState.activeTab,
    activeCategory: analysisState.activeCategory,
    loading: analysisState.loading,
    error: analysisState.error,
    staleError: analysisState.staleError,
    hasLoaded: analysisState.hasLoaded,
    hasExecutedScreening: analysisState.hasExecutedScreening,
    lastUpdateTime: analysisState.lastUpdateTime,
    stats: analysisState.stats,
    technicalIndicatorScreeningSupported: false,
    technicalIndicatorSupportMessage: '当前股票池数据未包含可执行的技术指标值，技术指标条件暂不支持参与筛选。',
    selectedIndicator: analysisState.selectedIndicator,
    selectedStock: analysisState.selectedStock,
    indicatorCategories: analysisState.indicatorCategories,
    indicators: analysisState.indicators,
    filteredIndicators: computed(() => analysisState.indicators.value.filter((item) => item.category === analysisState.activeCategory.value)),
    screeningFilters: analysisState.screeningFilters,
    screeningResults: analysisState.screeningResults,
    availableIndicatorsForFilter: analysisState.availableIndicatorsForFilter,
    switchTab: analysisState.switchTab,
    refreshData: analysisState.refreshData,
    runScreening: analysisState.runScreening,
    resetFilters: analysisState.resetFilters,
    setSelectedIndicator: analysisState.setSelectedIndicator,
    setSelectedStock: analysisState.setSelectedStock,
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      emits: ['click'],
      template: '<button @click="$emit(\'click\')"><slot /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
    },
    ArtDecoStatCard,
  }
})

import DataAdvancedPage from '@/views/data/Advanced.vue'

function mountAdvancedPage() {
  return mount(DataAdvancedPage as never, {
    global: {
      stubs: {
        AnalysisIndicators: {
          template: '<div class="analysis-indicators-stub" />',
        },
        AnalysisScreener: {
          template: '<div class="analysis-screener-stub" />',
        },
        AnalysisResults: {
          template: '<div class="analysis-results-stub" />',
        },
      },
    },
  })
}

describe('Data indicator summary truth', () => {
  beforeEach(() => {
    analysisState.activeTab.value = 'indicators'
    analysisState.activeCategory.value = 'trend'
    analysisState.loading.value = false
    analysisState.error.value = null
    analysisState.staleError.value = ''
    analysisState.hasLoaded.value = true
    analysisState.hasExecutedScreening.value = false
    analysisState.lastUpdateTime.value = '2026/04/30 13:43:18'
    analysisState.stats.value = {
      availableIndicators: 0,
      customIndicators: 0,
      screenedStocks: 0,
      screeningTimes: 0,
      qualifiedStocks: 0,
      qualifiedChange: 0,
    }
    analysisState.selectedIndicator.value = null
    analysisState.selectedStock.value = null
    analysisState.indicators.value = []
    analysisState.screeningResults.value = []
    analysisState.availableIndicatorsForFilter.value = []
    analysisState.switchTab.mockReset()
    analysisState.refreshData.mockReset()
    analysisState.runScreening.mockReset()
    analysisState.resetFilters.mockReset()
    analysisState.setSelectedIndicator.mockReset()
    analysisState.setSelectedStock.mockReset()
  })

  it('does not present unverified indicator-summary cards and updated-at metadata as faux zero metrics on failed first load', () => {
    analysisState.error.value = 'indicator registry unavailable'
    analysisState.hasLoaded.value = true

    const wrapper = mountAdvancedPage()

    expect(wrapper.get('.header-meta').text()).toContain('STATUS: 同步异常')
    expect(wrapper.get('.header-meta').text()).toContain('UPDATED: --')

    const statsOverview = wrapper.get('.stats-overview')
    expect(statsOverview.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsOverview.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--', '--'])
    expect(statsOverview.text()).not.toContain('+0%')
    expect(statsOverview.text()).not.toContain('0.00')
  })

  it('does not render verified indicator tally cards as faux delta metrics or decimal pseudo precision', () => {
    analysisState.lastUpdateTime.value = '2026/04/30 14:02:00'
    analysisState.indicators.value = Array.from({ length: 9 }, (_, index) => ({
      id: index + 1,
      name: `指标-${index + 1}`,
      key: `ind-${index + 1}`,
      category: 'trend',
      categoryLabel: '趋势',
      type: '主图',
      description: 'desc',
      params: [],
    }))
    analysisState.stats.value = {
      availableIndicators: 23,
      customIndicators: 0,
      screenedStocks: 200,
      screeningTimes: 1,
      qualifiedStocks: 12,
      qualifiedChange: 4,
    }

    const wrapper = mountAdvancedPage()

    expect(wrapper.get('.header-meta').text()).toContain('STATUS: 待执行筛选')
    expect(wrapper.get('.header-meta').text()).toContain('UPDATED: 2026/04/30 14:02:00')

    const statsOverview = wrapper.get('.stats-overview')
    expect(statsOverview.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsOverview.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['23', '9', '200', '1', '12'])
    expect(statsOverview.text()).not.toContain('+0%')
    expect(statsOverview.text()).not.toContain('23.00')
    expect(statsOverview.text()).not.toContain('9.00')
    expect(statsOverview.text()).not.toContain('200.00')
    expect(statsOverview.text()).not.toContain('1.00')
    expect(statsOverview.text()).not.toContain('12.00')
  })
})
