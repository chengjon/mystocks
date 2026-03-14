import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { apiGetMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn()
}))

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: apiGetMock
  }
}))

import MarketConceptTab from '../MarketConceptTab.vue'

describe('MarketConceptTab', () => {
  beforeEach(() => {
    apiGetMock.mockReset().mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: [
        {
          sector_name: '互联金融',
          change_percent: 1.75,
          main_net_inflow: 5900209920,
          leading_stock: '东方财富'
        }
      ],
      timestamp: '2026-03-13T00:00:00Z',
      request_id: 'req-concept',
      errors: null
    })
  })

  it('uses sector fund-flow endpoint for concept ranking and renders real rows', async () => {
    const wrapper = mount(MarketConceptTab as never, {
      global: {
        directives: {
          loading: { mounted() {} }
        }
      }
    })

    await flushPromises()

    expect(apiGetMock).toHaveBeenCalledWith('/v2/market/sector/fund-flow', {
      params: {
        sector_type: '概念',
        timeframe: '今日',
        limit: 20
      }
    })
    expect(wrapper.text()).toContain('互联金融')
    expect(wrapper.text()).toContain('东方财富')
  })
})
