import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  successMock,
  warningMock,
  errorMock,
  listWatchlistsMock,
  createWatchlistMock,
  addStockToWatchlistMock,
} = vi.hoisted(() => ({
  successMock: vi.fn(),
  warningMock: vi.fn(),
  errorMock: vi.fn(),
  listWatchlistsMock: vi.fn(),
  createWatchlistMock: vi.fn(),
  addStockToWatchlistMock: vi.fn(),
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: successMock,
    warning: warningMock,
    error: errorMock,
    info: vi.fn(),
  },
}))

vi.mock('@/api/services/watchlistService.ts', () => ({
  watchlistService: {
    listWatchlists: listWatchlistsMock,
    createWatchlist: createWatchlistMock,
    addStockToWatchlist: addStockToWatchlistMock,
  },
}))

import WencaiQueryTable from '@/components/market/WencaiQueryTable.vue'

const TableStub = {
  props: ['data'],
  template: `
    <table>
      <tbody>
        <tr v-for="row in data" :key="row.code">
          <slot :row="row" />
        </tr>
      </tbody>
    </table>
  `,
}

const TableColumnStub = {
  template: '<div><slot :row="{ code: `000001`, name: `平安银行` }" /></div>',
}

describe('WencaiQueryTable watchlist actions', () => {
  const fetchMock = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: [{ code: '000001', name: '平安银行' }],
        total: 1,
      }),
    })
    vi.stubGlobal('fetch', fetchMock)
    listWatchlistsMock.mockResolvedValue({
      success: true,
      data: [{ id: 7, name: '默认自选', watchlist_type: 'manual', risk_profile: {}, stocks_count: 0 }],
    })
    createWatchlistMock.mockResolvedValue({
      success: true,
      data: { id: 11, name: '问财自选', watchlist_type: 'manual', risk_profile: {}, stocks_count: 0 },
    })
    addStockToWatchlistMock.mockResolvedValue({ success: true, data: null })
  })

  it('adds a stock into the first existing watchlist', async () => {
    const wrapper = mount(WencaiQueryTable as never, {
      props: {
        queryName: '银行股',
        queryDescription: '银行板块筛选',
      },
      global: {
        stubs: {
          'el-button': { template: '<button @click="$emit(`click`)"><slot name="icon" /><slot /></button>' },
          'el-icon': { template: '<i><slot /></i>' },
          'el-pagination': true,
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
          'el-table': TableStub,
          'el-table-column': TableColumnStub,
        },
        directives: {
          loading: { mounted() {}, updated() {} },
        },
      },
    })

    await flushPromises()

    await (wrapper.vm as any).addToWatchlist({ code: '000001', name: '平安银行' })

    expect(listWatchlistsMock).toHaveBeenCalledTimes(1)
    expect(createWatchlistMock).not.toHaveBeenCalled()
    expect(addStockToWatchlistMock).toHaveBeenCalledWith(7, {
      stock_code: '000001',
      entry_reason: '来自问财条件：银行股',
    })
    expect(successMock).toHaveBeenCalledWith('已将 平安银行 加入自选')
  })

  it('creates a default watchlist before adding when none exists', async () => {
    listWatchlistsMock.mockResolvedValueOnce({
      success: true,
      data: [],
    })

    const wrapper = mount(WencaiQueryTable as never, {
      props: {
        queryName: '高股息',
        queryDescription: '高股息筛选',
      },
      global: {
        stubs: {
          'el-button': { template: '<button @click="$emit(`click`)"><slot name="icon" /><slot /></button>' },
          'el-icon': { template: '<i><slot /></i>' },
          'el-pagination': true,
          'el-dialog': { template: '<div><slot /><slot name="footer" /></div>' },
          'el-table': TableStub,
          'el-table-column': TableColumnStub,
        },
        directives: {
          loading: { mounted() {}, updated() {} },
        },
      },
    })

    await flushPromises()

    await (wrapper.vm as any).addToWatchlist({ code: '600000', name: '浦发银行' })

    expect(createWatchlistMock).toHaveBeenCalledWith({
      name: '问财自选',
      watchlist_type: 'manual',
      risk_profile: {},
    })
    expect(addStockToWatchlistMock).toHaveBeenCalledWith(11, {
      stock_code: '600000',
      entry_reason: '来自问财条件：高股息',
    })
    expect(successMock).toHaveBeenCalledWith('已将 浦发银行 加入自选')
  })
})
