import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getDataSourceConfigMock, updateDataSourceConfigMock } = vi.hoisted(() => ({
  getDataSourceConfigMock: vi.fn(),
  updateDataSourceConfigMock: vi.fn()
}))

vi.mock('@/api/index', () => ({
  monitoringApi: {
    getDataSourceConfig: getDataSourceConfigMock,
    updateDataSourceConfig: updateDataSourceConfigMock
  }
}))

import ArtDecoDataManagement from '../ArtDecoDataManagement.vue'

describe('ArtDecoDataManagement', () => {
  beforeEach(() => {
    getDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: {
        endpoints: [
          {
            endpoint_name: 'akshare.stock_zh_a_hist',
            source_name: 'akshare',
            status: 'active',
            url: 'https://ak.example/api'
          }
        ]
      },
      timestamp: '2026-03-13T00:00:00Z',
      request_id: 'req-ds',
      errors: null
    })
    updateDataSourceConfigMock.mockReset().mockResolvedValue({
      success: true,
      code: 200,
      message: 'ok',
      data: {},
      timestamp: '2026-03-13T00:00:00Z',
      request_id: 'req-ds-save',
      errors: null
    })
  })

  it('renders config rows from endpoints payload', async () => {
    const wrapper = mount(ArtDecoDataManagement as never, {
      global: {
        directives: {
          loading: { mounted() {} }
        },
        stubs: {
          ArtDecoCard: { template: '<div><slot name="header" /><slot /></div>' },
          ArtDecoButton: { template: '<button><slot /></button>' }
        }
      }
    })

    await flushPromises()

    expect(getDataSourceConfigMock).toHaveBeenCalled()
    expect(wrapper.text()).toContain('akshare')
    expect(wrapper.text()).toContain('https://ak.example/api')
  })

  it('saves toggled items through batch status updates', async () => {
    const wrapper = mount(ArtDecoDataManagement as never, {
      global: {
        directives: {
          loading: { mounted() {} }
        },
        stubs: {
          ArtDecoCard: { template: '<div><slot name="header" /><slot /></div>' },
          ArtDecoButton: { template: '<button @click="$emit(\'click\')"><slot /></button>' }
        }
      }
    })

    await flushPromises()

    const buttons = wrapper.findAll('button')
    await buttons[0].trigger('click')
    await buttons[2].trigger('click')
    await flushPromises()

    expect(updateDataSourceConfigMock).toHaveBeenCalledWith({
      operations: [
        {
          action: 'update',
          endpoint_name: 'akshare.stock_zh_a_hist',
          updates: {
            status: 'maintenance'
          }
        }
      ]
    })
  })
})
