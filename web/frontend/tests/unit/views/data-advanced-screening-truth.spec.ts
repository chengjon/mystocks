import { flushPromises, mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

const { axiosGetMock, indicatorRegistryMock } = vi.hoisted(() => ({
  axiosGetMock: vi.fn(),
  indicatorRegistryMock: vi.fn(),
}))

vi.mock('axios', () => {
  const axiosInstance = {
    get: axiosGetMock,
    interceptors: {
      request: {
        use: vi.fn(),
      },
      response: {
        use: vi.fn(),
      },
    },
  }

  const isAxiosError = (value: unknown) => {
    return typeof value === 'object' && value !== null && 'isAxiosError' in value
  }

  return {
    default: {
      get: axiosGetMock,
      create: vi.fn(() => axiosInstance),
      isAxiosError,
    },
    get: axiosGetMock,
    create: vi.fn(() => axiosInstance),
    isAxiosError,
  }
})

vi.mock('@/services/indicatorService', () => ({
  indicatorService: {
    getRegistry: indicatorRegistryMock,
  },
}))

import DataAdvancedPage from '@/views/data/Advanced.vue'

function extractUpdatedValue(headerMetaText: string): string {
  const match = headerMetaText.match(/UPDATED:\s*(.+)$/)
  return match?.[1]?.trim() ?? ''
}

describe('Data indicator screening workflow truthfulness', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('does not present default stock-pool data as executed screening results before the user runs screening', async () => {
    indicatorRegistryMock.mockReset()
    axiosGetMock.mockReset()

    indicatorRegistryMock.mockResolvedValue({
      indicators: [
        {
          abbreviation: 'MA',
          chinese_name: '移动平均线',
          full_name: 'Moving Average',
          category: 'trend',
          panel_type: 'overlay',
          description: '趋势跟踪',
          parameters: [{ name: 'timeperiod', default: 20 }],
        },
      ],
    })

    axiosGetMock.mockResolvedValue({
      data: {
        data: [
          {
            symbol: '600519',
            name: '贵州茅台',
            price: 1820.5,
            change_pct: 1.86,
            volume: 1000000,
            turnover: 1820500000,
            pe: 28.3,
            market_cap: 2300000000000,
          },
          {
            symbol: '300750',
            name: '宁德时代',
            price: 201.2,
            change_pct: -0.45,
            volume: 800000,
            turnover: 640000000,
            pe: 22.1,
            market_cap: 890000000000,
          },
        ],
      },
    })

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
            template: '<div data-testid="analysis-indicators">Indicators</div>',
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>',
          },
          AnalysisResults: {
            props: ['data'],
            template: '<div data-testid="analysis-results">Results:{{ data.length }}</div>',
          },
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('数据分析中心')
    expect(wrapper.text()).toContain('待执行筛选')
    expect(wrapper.text()).toContain('筛选股票数:0')
    expect(wrapper.text()).toContain('符合条件:0')
    expect(wrapper.find('[data-testid="analysis-results"]').exists()).toBe(false)

    const mainTabs = wrapper.findAll('.main-tab')
    await mainTabs[3]!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('尚未执行筛选')
    expect(wrapper.text()).not.toContain('暂无筛选结果')
    expect(wrapper.find('[data-testid="analysis-results"]').exists()).toBe(false)

    const actionButtons = wrapper.findAll('.header-actions button')
    const screeningButton = actionButtons.find((button) => button.text().includes('执行筛选'))
    expect(screeningButton).toBeTruthy()

    await screeningButton!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('筛选已就绪')
    expect(wrapper.text()).toContain('筛选股票数:2')
    expect(wrapper.text()).toContain('符合条件:2')
    expect(wrapper.find('[data-testid="analysis-results"]').exists()).toBe(true)
    expect(wrapper.get('[data-testid="analysis-results"]').text()).toContain('Results:2')
  })

  it('keeps the last verified updated-at timestamp and indicator workspace visible when a manual refresh fails', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-05-03T09:00:00.000+08:00'))

    indicatorRegistryMock.mockReset()
    axiosGetMock.mockReset()

    indicatorRegistryMock
      .mockResolvedValueOnce({
        indicators: [
          {
            abbreviation: 'MA',
            chinese_name: '移动平均线',
            full_name: 'Moving Average',
            category: 'trend',
            panel_type: 'overlay',
            description: '趋势跟踪',
            parameters: [{ name: 'timeperiod', default: 20 }],
          },
        ],
      })
      .mockRejectedValueOnce(new Error('indicator registry refresh unavailable'))

    axiosGetMock
      .mockResolvedValueOnce({
        data: {
          data: [
            {
              symbol: '600519',
              name: '贵州茅台',
              price: 1820.5,
              change_pct: 1.86,
              volume: 1000000,
              turnover: 1820500000,
              pe: 28.3,
              market_cap: 2300000000000,
            },
            {
              symbol: '300750',
              name: '宁德时代',
              price: 201.2,
              change_pct: -0.45,
              volume: 800000,
              turnover: 640000000,
              pe: 22.1,
              market_cap: 890000000000,
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          data: [
            {
              symbol: '600519',
              name: '贵州茅台',
              price: 1820.5,
              change_pct: 1.86,
              volume: 1000000,
              turnover: 1820500000,
              pe: 28.3,
              market_cap: 2300000000000,
            },
          ],
        },
      })

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
            template: '<div data-testid="analysis-indicators">Indicators</div>',
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>',
          },
          AnalysisResults: {
            props: ['data'],
            template: '<div data-testid="analysis-results">Results:{{ data.length }}</div>',
          },
        },
      },
    })

    await flushPromises()

    const initialHeaderMeta = wrapper.get('.header-meta').text()
    const initialUpdatedValue = extractUpdatedValue(initialHeaderMeta)
    expect(initialUpdatedValue).not.toBe('')
    expect(wrapper.find('[data-testid="analysis-indicators"]').exists()).toBe(true)

    vi.setSystemTime(new Date('2026-05-03T10:15:00.000+08:00'))

    const refreshButton = wrapper.findAll('.header-actions button').find((button) => button.text().includes('刷新数据'))
    expect(refreshButton).toBeTruthy()

    await refreshButton!.trigger('click')
    await flushPromises()

    expect(wrapper.get('.header-meta').text()).toContain(`UPDATED: ${initialUpdatedValue}`)
    expect(wrapper.text()).toContain('当前仍显示上次成功同步的数据分析快照。')
    expect(wrapper.find('[data-testid="analysis-indicators"]').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('数据分析数据加载失败')
  })

  it('does not promote local screening actions into verified updated-at or results after the first load failed', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-05-03T11:20:00.000+08:00'))

    indicatorRegistryMock.mockReset()
    axiosGetMock.mockReset()

    indicatorRegistryMock.mockRejectedValueOnce(new Error('indicator registry unavailable'))

    axiosGetMock.mockResolvedValueOnce({
      data: {
        data: [
          {
            symbol: '600519',
            name: '贵州茅台',
            price: 1820.5,
            change_pct: 1.86,
            volume: 1000000,
            turnover: 1820500000,
            pe: 28.3,
            market_cap: 2300000000000,
          },
          {
            symbol: '300750',
            name: '宁德时代',
            price: 201.2,
            change_pct: -0.45,
            volume: 800000,
            turnover: 640000000,
            pe: 22.1,
            market_cap: 890000000000,
          },
        ],
      },
    })

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
            template: '<div data-testid="analysis-indicators">Indicators</div>',
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>',
          },
          AnalysisResults: {
            props: ['data'],
            template: '<div data-testid="analysis-results">Results:{{ data.length }}</div>',
          },
        },
      },
    })

    await flushPromises()

    expect(wrapper.get('.header-meta').text()).toContain('STATUS: 同步异常')
    expect(wrapper.get('.header-meta').text()).toContain('UPDATED: --')
    expect(wrapper.text()).toContain('数据分析数据加载失败')

    const screeningButton = wrapper.findAll('.header-actions button').find((button) => button.text().includes('执行筛选'))
    expect(screeningButton).toBeTruthy()

    await screeningButton!.trigger('click')
    await flushPromises()

    expect(wrapper.get('.header-meta').text()).toContain('STATUS: 同步异常')
    expect(wrapper.get('.header-meta').text()).toContain('UPDATED: --')
    expect(wrapper.text()).toContain('数据分析数据加载失败')
    expect(wrapper.find('[data-testid="analysis-results"]').exists()).toBe(false)
    expect(wrapper.text()).not.toContain('筛选已就绪')
  })

  it('clears the previous selected stock context when a verified refresh replaces the screening result set with a different universe', async () => {
    indicatorRegistryMock.mockReset()
    axiosGetMock.mockReset()

    indicatorRegistryMock.mockResolvedValue({
      indicators: [
        {
          abbreviation: 'MA',
          chinese_name: '移动平均线',
          full_name: 'Moving Average',
          category: 'trend',
          panel_type: 'overlay',
          description: '趋势跟踪',
          parameters: [{ name: 'timeperiod', default: 20 }],
        },
      ],
    })

    axiosGetMock
      .mockResolvedValueOnce({
        data: {
          data: [
            {
              symbol: '600519',
              name: '贵州茅台',
              price: 1820.5,
              change_pct: 1.86,
              volume: 1000000,
              turnover: 1820500000,
              pe: 28.3,
              market_cap: 2300000000000,
            },
            {
              symbol: '300750',
              name: '宁德时代',
              price: 201.2,
              change_pct: -0.45,
              volume: 800000,
              turnover: 640000000,
              pe: 22.1,
              market_cap: 890000000000,
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          data: [
            {
              symbol: '002594',
              name: '比亚迪',
              price: 258.3,
              change_pct: 2.11,
              volume: 410000,
              turnover: 510000000,
              pe: 22.8,
              market_cap: 760000000000,
            },
          ],
        },
      })

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
            template: '<div data-testid="analysis-indicators">Indicators</div>',
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>',
          },
          AnalysisResults: {
            props: ['data'],
            emits: ['row-click'],
            template: `
              <div data-testid="analysis-results">
                <button
                  v-for="row in data"
                  :key="row.symbol"
                  type="button"
                  @click="$emit('row-click', row)"
                >
                  {{ row.symbol }} {{ row.name }}
                </button>
              </div>
            `,
          },
        },
      },
    })

    await flushPromises()

    const screeningButton = wrapper.findAll('.header-actions button').find((button) => button.text().includes('执行筛选'))
    expect(screeningButton).toBeTruthy()

    await screeningButton!.trigger('click')
    await flushPromises()

    const selectedRowButton = wrapper.get('[data-testid="analysis-results"] button')
    expect(selectedRowButton.text()).toContain('600519')
    await selectedRowButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('selected stock')
    expect(wrapper.text()).toContain('贵州茅台')

    const refreshButton = wrapper.findAll('.header-actions button').find((button) => button.text().includes('刷新数据'))
    expect(refreshButton).toBeTruthy()

    await refreshButton!.trigger('click')
    await flushPromises()

    expect(wrapper.get('[data-testid="analysis-results"]').text()).toContain('002594 比亚迪')
    expect(wrapper.text()).not.toContain('selected stock')
    expect(wrapper.text()).not.toContain('贵州茅台')
  })

  it('clears the previous selected indicator context when the user switches the active category before reopening the editor', async () => {
    indicatorRegistryMock.mockReset()
    axiosGetMock.mockReset()

    indicatorRegistryMock.mockResolvedValue({
      indicators: [
        {
          abbreviation: 'MA',
          chinese_name: '移动平均线',
          full_name: 'Moving Average',
          category: 'trend',
          panel_type: 'overlay',
          description: '趋势跟踪',
          parameters: [{ name: 'timeperiod', default: 20 }],
        },
        {
          abbreviation: 'RSI',
          chinese_name: '相对强弱指标',
          full_name: 'Relative Strength Index',
          category: 'momentum',
          panel_type: 'indicator',
          description: '动量强弱',
          parameters: [{ name: 'timeperiod', default: 14 }],
        },
      ],
    })

    axiosGetMock.mockResolvedValue({
      data: {
        data: [
          {
            symbol: '600519',
            name: '贵州茅台',
            price: 1820.5,
            change_pct: 1.86,
            volume: 1000000,
            turnover: 1820500000,
            pe: 28.3,
            market_cap: 2300000000000,
          },
        ],
      },
    })

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
            props: ['indicators'],
            emits: ['select', 'update:activeCategory'],
            template: `
              <div data-testid="analysis-indicators">
                <button
                  type="button"
                  data-testid="select-trend-indicator"
                  @click="$emit('select', indicators[0])"
                >
                  {{ indicators[0]?.name }}
                </button>
                <button
                  type="button"
                  data-testid="switch-to-momentum"
                  @click="$emit('update:activeCategory', 'momentum')"
                >
                  切换到动量
                </button>
              </div>
            `,
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>',
          },
          AnalysisResults: {
            props: ['data'],
            template: '<div data-testid="analysis-results">Results:{{ data.length }}</div>',
          },
        },
      },
    })

    await flushPromises()

    await wrapper.get('[data-testid="analysis-indicators"] [data-testid="select-trend-indicator"]').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('selected indicator')
    expect(wrapper.text()).toContain('移动平均线')
    expect(wrapper.text()).toContain('MA')

    const backToLibraryButton = wrapper
      .get('#data-analysis-panel-editor')
      .findAll('button')
      .find((button) => button.text().includes('返回指标库'))
    expect(backToLibraryButton).toBeTruthy()

    await backToLibraryButton!.trigger('click')
    await flushPromises()

    await wrapper.get('[data-testid="analysis-indicators"] [data-testid="switch-to-momentum"]').trigger('click')
    await flushPromises()

    const editorTab = wrapper.findAll('.main-tab').find((button) => button.text().includes('指标详情'))
    expect(editorTab).toBeTruthy()

    await editorTab!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('selected indicator')
    expect(wrapper.text()).not.toContain('移动平均线')
    expect(wrapper.text()).not.toContain('MA')
    expect(wrapper.text()).toContain('从指标库选择一个指标')
  })

  it('clears the previous selected indicator context when a verified refresh replaces the indicator registry with a different universe', async () => {
    indicatorRegistryMock.mockReset()
    axiosGetMock.mockReset()

    indicatorRegistryMock
      .mockResolvedValueOnce({
        indicators: [
          {
            abbreviation: 'MA',
            chinese_name: '移动平均线',
            full_name: 'Moving Average',
            category: 'trend',
            panel_type: 'overlay',
            description: '趋势跟踪',
            parameters: [{ name: 'timeperiod', default: 20 }],
          },
        ],
      })
      .mockResolvedValueOnce({
        indicators: [
          {
            abbreviation: 'RSI',
            chinese_name: '相对强弱指标',
            full_name: 'Relative Strength Index',
            category: 'momentum',
            panel_type: 'indicator',
            description: '动量强弱',
            parameters: [{ name: 'timeperiod', default: 14 }],
          },
        ],
      })

    axiosGetMock
      .mockResolvedValueOnce({
        data: {
          data: [
            {
              symbol: '600519',
              name: '贵州茅台',
              price: 1820.5,
              change_pct: 1.86,
              volume: 1000000,
              turnover: 1820500000,
              pe: 28.3,
              market_cap: 2300000000000,
            },
          ],
        },
      })
      .mockResolvedValueOnce({
        data: {
          data: [
            {
              symbol: '002594',
              name: '比亚迪',
              price: 258.3,
              change_pct: 2.11,
              volume: 410000,
              turnover: 510000000,
              pe: 22.8,
              market_cap: 760000000000,
            },
          ],
        },
      })

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
            props: ['indicators'],
            emits: ['select', 'update:activeCategory'],
            template: `
              <div data-testid="analysis-indicators">
                <button
                  v-for="indicator in indicators"
                  :key="indicator.key"
                  type="button"
                  @click="$emit('select', indicator)"
                >
                  {{ indicator.name }}
                </button>
              </div>
            `,
          },
          AnalysisScreener: {
            template: '<div data-testid="analysis-screener">Screener</div>',
          },
          AnalysisResults: {
            props: ['data'],
            template: '<div data-testid="analysis-results">Results:{{ data.length }}</div>',
          },
        },
      },
    })

    await flushPromises()

    const indicatorButton = wrapper.get('[data-testid="analysis-indicators"] button')
    expect(indicatorButton.text()).toContain('移动平均线')
    await indicatorButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('selected indicator')
    expect(wrapper.text()).toContain('移动平均线')
    expect(wrapper.text()).toContain('MA')

    const refreshButton = wrapper.findAll('.header-actions button').find((button) => button.text().includes('刷新数据'))
    expect(refreshButton).toBeTruthy()

    await refreshButton!.trigger('click')
    await flushPromises()

    expect(wrapper.text()).not.toContain('selected indicator')
    expect(wrapper.text()).not.toContain('移动平均线')
    expect(wrapper.text()).toContain('从指标库选择一个指标')
  })
})
