import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  onMountedMock,
  listWatchlistsMock,
  listWatchlistStocksMock,
  createWatchlistMock,
  updateWatchlistMock,
  deleteWatchlistMock,
  addStockToWatchlistMock,
  removeStockFromWatchlistMock,
  successMock,
  warningMock,
  errorMock,
  randomSpy,
} = vi.hoisted(() => ({
  onMountedMock: vi.fn(),
  listWatchlistsMock: vi.fn(),
  listWatchlistStocksMock: vi.fn(),
  createWatchlistMock: vi.fn(),
  updateWatchlistMock: vi.fn(),
  deleteWatchlistMock: vi.fn(),
  addStockToWatchlistMock: vi.fn(),
  removeStockFromWatchlistMock: vi.fn(),
  successMock: vi.fn(),
  warningMock: vi.fn(),
  errorMock: vi.fn(),
  randomSpy: vi.spyOn(Math, 'random'),
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: onMountedMock,
  }
})

vi.mock('element-plus', () => ({
  ElMessage: {
    success: successMock,
    warning: warningMock,
    error: errorMock,
    info: vi.fn(),
  },
}))

vi.mock('@/api/services/watchlistService', () => ({
  watchlistService: {
    listWatchlists: listWatchlistsMock,
    listWatchlistStocks: listWatchlistStocksMock,
    createWatchlist: createWatchlistMock,
    updateWatchlist: updateWatchlistMock,
    deleteWatchlist: deleteWatchlistMock,
    addStockToWatchlist: addStockToWatchlistMock,
    removeStockFromWatchlist: removeStockFromWatchlistMock,
  },
}))

import { useWatchlistManagement } from '@/views/monitoring/composables/useWatchlistManagement'

describe('watchlist management alert summary', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    randomSpy.mockReturnValue(0.9)
    listWatchlistsMock.mockResolvedValue({ success: true, data: [] })
    updateWatchlistMock.mockResolvedValue({
      success: true,
      data: {
        id: 7,
        name: '更新后的组合',
        watchlist_type: 'strategy',
        risk_profile: { risk_tolerance: 70 },
        stocks_count: 2,
      },
    })
    listWatchlistStocksMock.mockResolvedValue({
      success: true,
      data: [
        {
          id: 1,
          stock_code: '600519.SH',
          entry_price: 1680,
          current_price: 1800.5,
          weight: 0.35,
          alerts_count: 2,
        },
        {
          id: 2,
          stock_code: '000001.SZ',
          entry_price: 12.2,
          current_price: 12.34,
          weight: 0.2,
          alerts_count: 1,
        },
      ],
    })
  })

  it('derives active alerts from loaded watchlist stocks instead of a random placeholder', async () => {
    const model = useWatchlistManagement()

    model.manageStocks({
      id: 7,
      name: '核心观察',
      watchlist_type: 'manual',
      risk_profile: {},
      stocks_count: 2,
    })

    await vi.waitFor(() => {
      expect(listWatchlistStocksMock).toHaveBeenCalledWith(7)
      expect(model.activeAlerts.value).toBe(3)
    })
  })

  it('sums portfolio stock counts from fetched watchlists into the monitoring overview', async () => {
    listWatchlistsMock.mockResolvedValueOnce({
      success: true,
      data: [
        {
          id: 7,
          name: '核心观察',
          watchlist_type: 'manual',
          risk_profile: {},
          stocks_count: 3,
        },
        {
          id: 8,
          name: '趋势跟踪',
          watchlist_type: 'strategy',
          risk_profile: {},
          stocks_count: 2,
        },
      ],
    })

    const model = useWatchlistManagement()

    await model.refreshData()

    expect(listWatchlistsMock).toHaveBeenCalled()
    expect(model.totalStocks.value).toBe(5)
  })

  it('prefills the edit modal from the selected watchlist instead of keeping the create defaults', () => {
    const model = useWatchlistManagement()

    model.editWatchlist({
      id: 7,
      name: '核心观察',
      watchlist_type: 'benchmark',
      risk_profile: { risk_tolerance: 80 },
      stocks_count: 2,
    })

    expect(model.editingWatchlist.value?.id).toBe(7)
    expect(model.createModalVisible.value).toBe(true)
    expect(model.watchlistForm.name).toBe('核心观察')
    expect(model.watchlistForm.watchlist_type).toBe('benchmark')
    expect(model.riskTolerance.value).toBe(80)
    expect(warningMock).not.toHaveBeenCalled()
  })

  it('submits watchlist edits through the update path and patches the local summary', async () => {
    const model = useWatchlistManagement()
    model.watchlists.value = [
      {
        id: 7,
        name: '核心观察',
        watchlist_type: 'manual',
        risk_profile: { risk_tolerance: 50 },
        stocks_count: 2,
      },
    ]

    model.editWatchlist({
      id: 7,
      name: '核心观察',
      watchlist_type: 'manual',
      risk_profile: { risk_tolerance: 50 },
      stocks_count: 2,
    })
    model.watchlistForm.name = '更新后的组合'
    model.watchlistForm.watchlist_type = 'strategy'
    model.riskTolerance.value = 70

    await model.handleCreateOrUpdate()

    expect(updateWatchlistMock).toHaveBeenCalledWith(7, {
      name: '更新后的组合',
      watchlist_type: 'strategy',
      risk_profile: { risk_tolerance: 70 },
    })
    expect(successMock).toHaveBeenCalledWith('更新成功')
    expect(model.createModalVisible.value).toBe(false)
    expect(model.editingWatchlist.value).toBeNull()
    expect(model.watchlists.value[0]).toMatchObject({
      id: 7,
      name: '更新后的组合',
      watchlist_type: 'strategy',
      risk_profile: { risk_tolerance: 70 },
      stocks_count: 2,
    })
  })
})
