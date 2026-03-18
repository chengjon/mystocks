import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { pushMock, getStocksBasicMock, getStocksIndustriesMock, getStocksConceptsMock } = vi.hoisted(() => ({
  pushMock: vi.fn(),
  getStocksBasicMock: vi.fn(),
  getStocksIndustriesMock: vi.fn(),
  getStocksConceptsMock: vi.fn()
}))

vi.mock('@/api', () => ({
  dataApi: {
    getStocksBasic: getStocksBasicMock,
    getStocksIndustries: getStocksIndustriesMock,
    getStocksConcepts: getStocksConceptsMock
  }
}))

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: pushMock
  })
}))

vi.mock('element-plus', async () => {
  const actual = await vi.importActual<typeof import('element-plus')>('element-plus')
  return {
    ...actual,
    ElMessage: {
      error: vi.fn(),
      info: vi.fn()
    }
  }
})

import Stocks from '@/views/Stocks.vue'

const FilterBarStub = defineComponent({
  emits: ['change', 'reset'],
  template: `
    <div>
      <button data-test="filter-change" @click="$emit('change', { market: 'SH' })">change</button>
      <button data-test="filter-reset" @click="$emit('reset')">reset</button>
      <slot />
    </div>
  `
})

describe('Stocks.vue', () => {
  beforeEach(() => {
    pushMock.mockReset()
    getStocksIndustriesMock.mockReset().mockResolvedValue({
      success: true,
      data: [{ industry_name: '白酒' }]
    })
    getStocksConceptsMock.mockReset().mockResolvedValue({
      success: true,
      data: [{ concept_name: '消费' }]
    })
    getStocksBasicMock.mockReset().mockResolvedValue({
      success: true,
      message: 'ok',
      data: {
        data: [
          {
            symbol: '600519.SH',
            name: '贵州茅台',
            price: 1678.5,
            change_pct: 3.25,
            volume: 2350000
          }
        ]
      }
    })
  })

  it('reloads stock data when the filter bar emits change', async () => {
    const wrapper = mount(Stocks, {
      global: {
        stubs: {
          ArtDecoHeader: true,
          ArtDecoFilterBar: FilterBarStub,
          ArtDecoTable: { template: '<div><slot name="columns" /><slot name="actions" :row="{}" /></div>' },
          ArtDecoTableColumn: true,
          ArtDecoButton: { template: '<button><slot /></button>' },
          ArtDecoBadge: { template: '<span><slot /></span>' },
          ArtDecoCard: { template: '<div><slot name="header" /><slot /><slot name="footer" /></div>' },
          ElPagination: true
        }
      }
    })

    await flushPromises()
    expect(getStocksBasicMock).toHaveBeenCalledTimes(1)

    await wrapper.get('[data-test="filter-change"]').trigger('click')
    await flushPromises()

    expect(getStocksBasicMock).toHaveBeenCalledTimes(2)
  })
})
