import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getKlineMock } = vi.hoisted(() => ({
  getKlineMock: vi.fn()
}))

vi.mock('@/api/index', () => ({
  dataApi: {
    getKline: getKlineMock
  }
}))

import MarketKLineTab from '../MarketKLineTab.vue'

describe('MarketKLineTab', () => {
  beforeEach(() => {
    getKlineMock.mockReset().mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: {
        data: [
          {
            datetime: '2026-03-10 00:00:00',
            open: 1,
            high: 2,
            low: 0.5,
            close: 1.5,
            volume: 1000
          }
        ]
      },
      timestamp: '2026-03-13T00:00:00Z',
      request_id: 'req-kline',
      errors: null
    })
  })

  it('requests kline data with stock_code instead of symbol', async () => {
    mount(MarketKLineTab as never, {
      global: {
        directives: {
          loading: { mounted() {} }
        }
      }
    })

    await flushPromises()

    expect(getKlineMock).toHaveBeenCalledWith({
      stock_code: '000001',
      period: '1d',
      limit: 100
    })
  })
})
