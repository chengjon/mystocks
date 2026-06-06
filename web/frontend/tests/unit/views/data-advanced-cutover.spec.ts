import { describe, expect, it, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { computed, ref } from 'vue'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import DataAdvancedPage from '@/views/data/Advanced.vue'

const {
  refreshDataMock,
  runScreeningMock,
  resetFiltersMock,
  switchTabMock
} = vi.hoisted(() => ({
  refreshDataMock: vi.fn(),
  runScreeningMock: vi.fn(),
  resetFiltersMock: vi.fn(),
  switchTabMock: vi.fn()
}))

vi.mock('@/composables/market/useDataAnalysis', () => ({
  useDataAnalysis: () => {
    const indicators = ref([
      { name: 'MACD', category: 'trend' },
      { name: 'RSI', category: 'momentum' }
    ])

    return {
      activeTab: ref('indicators'),
      activeCategory: ref('all'),
      loading: ref(false),
      error: ref(null),
      staleError: ref(''),
      hasLoaded: ref(true),
      hasExecutedScreening: ref(true),
      lastUpdateTime: ref('2026/04/24 18:30:00'),
      stats: ref({
        availableIndicators: 128,
        customIndicators: 12,
        screenedStocks: 36,
        screeningTimes: 5,
        qualifiedStocks: 8,
        qualifiedChange: 2
      }),
      indicatorCategories: ref([
        { key: 'all', label: '全部' },
        { key: 'trend', label: '趋势' }
      ]),
      indicators,
      filteredIndicators: computed(() => indicators.value),
      screeningFilters: ref({ indicators: [] }),
      screeningResults: ref([{ symbol: '600519', name: '贵州茅台', price: '1600.00', change: '+1.2%' }]),
      availableIndicatorsForFilter: ref([{ label: 'MACD', value: 'MACD' }]),
      switchTab: switchTabMock,
      refreshData: refreshDataMock,
      runScreening: runScreeningMock,
      resetFilters: resetFiltersMock
    }
  }
}))

function readSource(pathFromFrontendRoot: string): string {
  return readFileSync(resolve(process.cwd(), pathFromFrontendRoot), 'utf8')
}

describe('Data-Indicator cutover guards', () => {
  beforeEach(() => {
    refreshDataMock.mockReset()
    runScreeningMock.mockReset()
    resetFiltersMock.mockReset()
    switchTabMock.mockReset()
  })

  it('renders the canonical Advanced data analysis shell and delegates core actions', async () => {
    const wrapper = mount(DataAdvancedPage as never, {
      global: {
        stubs: {
          ArtDecoButton: {
            emits: ['click'],
            template: '<button @click="$emit(\'click\')"><slot /></button>'
          },
          ArtDecoCard: {
            template: '<section><slot name="header" /><slot /></section>'
          },
          ArtDecoStatCard: {
            props: ['label', 'value'],
            template: '<div>{{ label }}:{{ value }}</div>'
          },
          AnalysisIndicators: {
            template: '<div data-testid="analysis-indicators">Indicators</div>'
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>'
          },
          AnalysisResults: {
            template: '<div data-testid="analysis-results">Results</div>'
          }
        }
      }
    })

    expect(wrapper.text()).toContain('数据分析中心')
    expect(wrapper.text()).toContain('可用指标:128')
    expect(wrapper.get('[data-testid="analysis-indicators"]').isVisible()).toBe(true)

    refreshDataMock.mockClear()
    runScreeningMock.mockClear()
    switchTabMock.mockClear()

    const actionButtons = wrapper.findAll('.header-actions button')
    const mainTabs = wrapper.findAll('.main-tab')
    const refreshButton = actionButtons.find((button) => button.text().includes('刷新数据'))
    const screeningButton = actionButtons.find((button) => button.text().includes('执行筛选'))

    expect(refreshButton).toBeTruthy()
    expect(screeningButton).toBeTruthy()

    await refreshButton!.trigger('click')
    await screeningButton!.trigger('click')
    await mainTabs[2].trigger('click')

    expect(refreshDataMock).toHaveBeenCalledTimes(1)
    expect(runScreeningMock).toHaveBeenCalledTimes(1)
    expect(switchTabMock).toHaveBeenCalledWith('screener')
  })

  it('keeps the legacy ArtDecoDataAnalysis wrapper pointed at the canonical Advanced page', () => {
    const wrapperSource = readSource('src/views/artdeco-pages/ArtDecoDataAnalysis.vue')

    expect(wrapperSource).toContain("import DataAdvancedPage from '@/views/data/Advanced.vue'")
    expect(wrapperSource).toContain('<DataAdvancedPage v-bind="attrs" />')
  })
})
