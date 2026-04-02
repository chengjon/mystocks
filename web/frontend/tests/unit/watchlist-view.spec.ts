import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  successMock,
  errorMock,
  loadWatchlistMock,
  removeFromWatchlistMock,
  watchlistStocksRef,
  loadingRef,
} = vi.hoisted(() => ({
  successMock: vi.fn(),
  errorMock: vi.fn(),
  loadWatchlistMock: vi.fn(),
  removeFromWatchlistMock: vi.fn(),
  watchlistStocksRef: {
    value: [
      { symbol: '600519', name: '贵州茅台', price: 1800, change: 20, volume: 1000 },
      { symbol: '000001', name: '平安银行', price: 12, change: -0.5, volume: 500 },
    ],
  },
  loadingRef: { value: false },
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual<typeof import('element-plus')>('element-plus')
  return {
    ...actual,
    ElMessage: {
      success: successMock,
      error: errorMock,
      info: vi.fn(),
      warning: vi.fn(),
    },
  }
})

vi.mock('@/composables/useDashboardWatchlist', () => ({
  useDashboardWatchlist: () => ({
    loading: loadingRef,
    watchlistStocks: watchlistStocksRef,
    loadWatchlist: loadWatchlistMock,
    removeFromWatchlist: removeFromWatchlistMock,
  }),
}))

import WatchlistView from '@/views/stocks/Watchlist.vue'

describe('Watchlist view data bridge', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    loadingRef.value = false
    watchlistStocksRef.value = [
      { symbol: '600519', name: '贵州茅台', price: 1800, change: 20, volume: 1000 },
      { symbol: '000001', name: '平安银行', price: 12, change: -0.5, volume: 500 },
    ]
    loadWatchlistMock.mockResolvedValue(undefined)
    removeFromWatchlistMock.mockResolvedValue(undefined)
  })

  it('loads real watchlist data on mount and derives overview stats from it', async () => {
    const wrapper = mount(WatchlistView as never, {
      global: {
        stubs: {
          'el-card': { template: '<div><slot name="header" /><slot /></div>' },
          'el-button': { template: '<button @click="$emit(`click`)"><slot name="icon" /><slot /></button>' },
          'el-table': { template: '<div><slot /></div>' },
          'el-table-column': { template: '<div><slot :row="{ symbol: `600519`, name: `贵州茅台`, price: 1800, change: 20, changePercent: 1.12, volume: 1000, marketCap: 1, pe: 10, favorite: false }" /></div>' },
          'el-input': { template: '<input />' },
          'el-select': { template: '<select><slot /></select>' },
          'el-option': { template: '<option />' },
          'el-radio-group': { template: '<div><slot /></div>' },
          'el-radio-button': { template: '<button><slot /></button>' },
          'el-pagination': true,
          'el-icon': { template: '<i><slot /></i>' },
        },
      },
    })

    await flushPromises()

    expect(loadWatchlistMock).toHaveBeenCalledTimes(1)
    expect(wrapper.text()).toContain('2')
    expect(wrapper.text()).toContain('1')
    expect(successMock).toHaveBeenCalledWith('Data refreshed successfully')
  })
})
