import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  watchlistActionMocks,
  watchlistsStoreState,
  watchlistStocksStoreState,
} = vi.hoisted(() => ({
  watchlistActionMocks: {
    createWatchlist: vi.fn(),
    deleteWatchlist: vi.fn(),
    addStock: vi.fn(),
    removeStock: vi.fn(),
  },
  watchlistsStoreState: {
    data: [] as Array<Record<string, unknown>>,
    loading: false,
    error: null as string | null,
    lastRequestId: 'req-watchlists',
    refresh: vi.fn(async () => watchlistsStoreState.data),
  },
  watchlistStocksStoreState: {
    data: [] as Array<Record<string, unknown>>,
    loading: false,
    error: null as string | null,
    lastRequestId: 'req-watchlist-stocks',
    refresh: vi.fn(async () => watchlistStocksStoreState.data),
    clear: vi.fn(),
  },
}))

vi.mock('@/stores/apiStores', () => ({
  useWatchlistsStore: () => watchlistsStoreState,
  useWatchlistStocksStore: () => watchlistStocksStoreState,
  createMonitoringWatchlistActions: () => watchlistActionMocks,
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['disabled'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
    },
    ArtDecoStatCard,
    ArtDecoTable: {
      props: ['columns', 'data'],
      template: `
        <table>
          <tbody>
            <tr v-for="(row, rowIndex) in data" :key="rowIndex">
              <td v-for="column in columns" :key="column.key">{{ row[column.key] }}</td>
            </tr>
          </tbody>
        </table>
      `,
    },
  }
})

import WatchlistManagerPage from '@/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue'

function mountManagePage() {
  return mount(WatchlistManagerPage as never, {
    props: {
      watchlists: [
        { id: 'core', name: '核心组合', stocks: [{}, {}] },
        { id: 'swing', name: '波段观察', stocks: [{}] },
      ],
      activeWatchlistId: 'core',
      currentStocks: [
        {
          symbol: '600519',
          name: '贵州茅台',
          change: '2.1%',
          price: 1688.2,
        },
        {
          symbol: '000001',
          name: '平安银行',
          change: '-0.8%',
          price: 12.34,
        },
      ],
    },
    global: {
      stubs: {
        ArtDecoCard: {
          props: ['title'],
          template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
        },
      },
    },
  })
}

function mountStoreBackedManagePage() {
  return mount(WatchlistManagerPage as never, {
    props: {
      watchlists: [],
      activeWatchlistId: '',
      currentStocks: [],
    },
    global: {
      stubs: {
        ArtDecoCard: {
          props: ['title'],
          template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
        },
      },
    },
  })
}

describe('WatchlistManage routed count-kpi truth', () => {
  beforeEach(() => {
    watchlistsStoreState.loading = false
    watchlistsStoreState.error = null
    watchlistsStoreState.lastRequestId = 'req-watchlists'
    watchlistsStoreState.data = []
    watchlistsStoreState.refresh.mockClear()
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)

    watchlistStocksStoreState.loading = false
    watchlistStocksStoreState.error = null
    watchlistStocksStoreState.lastRequestId = 'req-watchlist-stocks'
    watchlistStocksStoreState.data = []
    watchlistStocksStoreState.refresh.mockClear()
    watchlistStocksStoreState.refresh.mockImplementation(async () => watchlistStocksStoreState.data)
    watchlistStocksStoreState.clear.mockClear()

    watchlistActionMocks.createWatchlist.mockClear()
    watchlistActionMocks.createWatchlist.mockResolvedValue(undefined)
    watchlistActionMocks.deleteWatchlist.mockClear()
    watchlistActionMocks.deleteWatchlist.mockResolvedValue(undefined)
    watchlistActionMocks.addStock.mockClear()
    watchlistActionMocks.addStock.mockResolvedValue(undefined)
    watchlistActionMocks.removeStock.mockClear()
    watchlistActionMocks.removeStock.mockResolvedValue(undefined)

    vi.unstubAllGlobals()
  })

  it('does not render watchlist count cards as precise-decimal delta stats when the route only provides counts', async () => {
    const wrapper = mountManagePage()

    await flushPromises()

    expect(watchlistsStoreState.refresh).toHaveBeenCalledTimes(1)
    expect(wrapper.findAll('.overview-grid .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.overview-grid .artdeco-stat-value').map((node) => node.text())).toEqual(['2', '2', '1', '1'])
    expect(wrapper.text()).not.toContain('+0%')
    expect(wrapper.text()).not.toContain('2.00')
    expect(wrapper.text()).not.toContain('1.00')
  })

  it('keeps watchlist overview cards in placeholder state when the first store-backed load failed', async () => {
    watchlistsStoreState.refresh.mockImplementation(async () => {
      watchlistsStoreState.error = '获取自选列表失败'
      watchlistsStoreState.data = []
      throw new Error('获取自选列表失败')
    })

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()

    expect(watchlistsStoreState.refresh).toHaveBeenCalledTimes(1)
    expect(watchlistStocksStoreState.clear).toHaveBeenCalledTimes(0)
    expect(wrapper.find('.state-panel').text()).toContain('自选列表加载失败')
    expect(wrapper.text()).not.toContain('暂无自选组合')
    expect(wrapper.findAll('.overview-grid .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.overview-grid .artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
  })

  it('keeps stock-summary cards pending while watchlists are verified but stock rows are still unresolved', async () => {
    watchlistsStoreState.data = [
      { id: 'core', name: '核心组合', stocks: [{}, {}] },
      { id: 'growth', name: '成长跟踪', stocks: [{}] },
    ]
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)
    watchlistStocksStoreState.loading = true
    watchlistStocksStoreState.refresh.mockImplementation(async () => {
      await new Promise(() => {})
      return watchlistStocksStoreState.data
    })

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()

    expect(watchlistsStoreState.refresh).toHaveBeenCalledTimes(1)
    expect(watchlistStocksStoreState.refresh).toHaveBeenCalledTimes(1)
    expect(wrapper.find('.state-panel').text()).toContain('自选列表同步中')
    expect(wrapper.findAll('.overview-grid .artdeco-stat-change')).toHaveLength(0)
    expect(wrapper.findAll('.overview-grid .artdeco-stat-value').map((node) => node.text())).toEqual(['2', '--', '--', '--'])
  })

  it('does not rebind stale stock rows to a newly selected watchlist when the later stock refresh failed', async () => {
    watchlistsStoreState.data = [
      { id: 'wl-core', name: '核心组合', stocks: [{}, {}] },
      { id: 'wl-growth', name: '成长跟踪', stocks: [{}] },
    ]
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)
    watchlistStocksStoreState.data = [
      {
        symbol: '600519',
        name: '贵州茅台',
        change: '2.1%',
        price: 1688.2,
      },
      {
        symbol: '300750',
        name: '宁德时代',
        change: '-0.8%',
        price: 210.55,
      },
    ]
    watchlistStocksStoreState.refresh.mockImplementation(async ({ watchlistId }: { watchlistId: string }) => {
      if (watchlistId === 'wl-growth') {
        watchlistStocksStoreState.error = '成长跟踪持仓暂不可用'
        throw new Error('成长跟踪持仓暂不可用')
      }

      watchlistStocksStoreState.error = null
      return watchlistStocksStoreState.data
    })

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()

    expect(wrapper.find('.watchlist-tab.active').text()).toContain('核心组合')
    expect(wrapper.text()).toContain('贵州茅台')

    await wrapper.get('button.watchlist-tab:nth-of-type(2)').trigger('click')
    await flushPromises()

    expect(watchlistStocksStoreState.refresh).toHaveBeenLastCalledWith({ watchlistId: 'wl-growth' })
    expect(wrapper.find('.watchlist-tab.active').text()).toContain('核心组合')
    expect(wrapper.find('.state-panel').text()).toContain('自选列表刷新异常')
    expect(wrapper.find('.state-panel').text()).toContain('当前仍显示上次成功同步的自选组合快照。')
    expect(wrapper.text()).toContain('贵州茅台')
    expect(wrapper.text()).not.toContain('比亚迪')
  })

  it('does not keep the previous watchlist rows visible while a newly selected watchlist is still unresolved', async () => {
    watchlistsStoreState.data = [
      { id: 'wl-core', name: '核心组合', stocks: [{}, {}] },
      { id: 'wl-growth', name: '成长跟踪', stocks: [{}] },
    ]
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)
    watchlistStocksStoreState.data = [
      {
        symbol: '600519',
        name: '贵州茅台',
        change: '2.1%',
        price: 1688.2,
      },
      {
        symbol: '300750',
        name: '宁德时代',
        change: '-0.8%',
        price: 210.55,
      },
    ]
    watchlistStocksStoreState.refresh.mockImplementation(async ({ watchlistId }: { watchlistId: string }) => {
      if (watchlistId === 'wl-growth') {
        return await new Promise(() => {})
      }

      watchlistStocksStoreState.error = null
      return watchlistStocksStoreState.data
    })

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()

    expect(wrapper.find('.watchlist-tab.active').text()).toContain('核心组合')
    expect(wrapper.text()).toContain('贵州茅台')

    await wrapper.get('button.watchlist-tab:nth-of-type(2)').trigger('click')
    await flushPromises()

    expect(watchlistStocksStoreState.refresh).toHaveBeenLastCalledWith({ watchlistId: 'wl-growth' })
    expect(wrapper.find('.watchlist-tab.active').text()).toContain('成长跟踪')
    expect(wrapper.findAll('tbody tr')).toHaveLength(0)
    expect(wrapper.findAll('.overview-grid .artdeco-stat-value').map((node) => node.text())).toEqual(['2', '--', '--', '--'])
    expect(wrapper.text()).not.toContain('贵州茅台')
  })

  it('deletes the active watchlist through the canonical route action and refreshes verified state', async () => {
    watchlistsStoreState.data = [
      { id: 'wl-core', name: '核心组合', stocks: [{}, {}] },
      { id: 'wl-growth', name: '成长跟踪', stocks: [{}] },
    ]
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)
    watchlistStocksStoreState.data = [
      {
        symbol: '600519',
        name: '贵州茅台',
        change: '2.1%',
        price: 1688.2,
      },
    ]
    vi.stubGlobal('confirm', vi.fn(() => true))

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()
    const deleteButton = wrapper.findAll('button').find((button) => button.text().includes('删除组合'))
    expect(deleteButton).toBeTruthy()

    await deleteButton!.trigger('click')
    await flushPromises()

    expect(watchlistActionMocks.deleteWatchlist).toHaveBeenCalledWith('wl-core')
    expect(watchlistsStoreState.refresh).toHaveBeenCalledTimes(2)
  })

  it('adds a stock with the minimal symbol input instead of recreating the legacy rich form', async () => {
    watchlistsStoreState.data = [
      { id: 'wl-core', name: '核心组合', stocks: [{}, {}] },
    ]
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)
    watchlistStocksStoreState.data = []
    vi.stubGlobal('prompt', vi.fn(() => ' 600519 '))

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()
    const addStockButton = wrapper.findAll('button').find((button) => button.text().includes('添加股票'))
    expect(addStockButton).toBeTruthy()

    await addStockButton!.trigger('click')
    await flushPromises()

    expect(watchlistActionMocks.addStock).toHaveBeenCalledWith('wl-core', '600519')
    expect(wrapper.text()).not.toContain('止损价')
    expect(wrapper.text()).not.toContain('目标价')
  })

  it('disables active-watchlist actions when no watchlist is verified', async () => {
    watchlistsStoreState.data = []
    watchlistsStoreState.refresh.mockImplementation(async () => watchlistsStoreState.data)

    const wrapper = mountStoreBackedManagePage()

    await flushPromises()

    const addStockButton = wrapper.findAll('button').find((button) => button.text().includes('添加股票'))
    const deleteButton = wrapper.findAll('button').find((button) => button.text().includes('删除组合'))

    expect(addStockButton?.attributes('disabled')).toBeDefined()
    expect(deleteButton?.attributes('disabled')).toBeDefined()
  })
})
