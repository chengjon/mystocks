import { flushPromises, mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { apiGetMock } = vi.hoisted(() => ({
  apiGetMock: vi.fn(),
}))

vi.mock('@/api/apiClient', () => ({
  apiClient: {
    get: apiGetMock,
  },
}))

vi.mock('@/composables/artdeco/useArtDecoApi', () => ({
  useArtDecoApi: () => {
    const state = {
      loading: ref(false),
      error: ref<string | null>(null),
      lastRequestId: ref(''),
      exec: async (
        apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string }>
      ) => {
        state.loading.value = true
        state.error.value = null

        try {
          const response = await apiCall()
          state.lastRequestId.value = response?.request_id ?? ''

          if (response?.success === false) {
            state.error.value = response.message ?? '请求失败'
            return null
          }

          return response?.data ?? response
        } catch (error: unknown) {
          state.error.value = error instanceof Error ? error.message : '请求失败'
          return null
        } finally {
          state.loading.value = false
        }
      },
    }

    return state
  },
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['loading', 'disabled'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText', 'statusType'],
      template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
  }
})

import DataConceptsPage from '@/views/data/Concepts.vue'

function mountConceptsPage() {
  return mount(DataConceptsPage as never, {
    global: {
      directives: {
        loading: {},
      },
    },
  })
}

describe('Data concept routed first-load truth', () => {
  beforeEach(() => {
    apiGetMock.mockReset()
  })

  it('does not present unresolved first-load concept counts and leader surfaces as faux zero values or fallback labels', async () => {
    apiGetMock.mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mountConceptsPage()

    await nextTick()
    await nextTick()

    expect(wrapper.get('.hero-meta').text()).toContain('SECTORS: --')
    expect(wrapper.get('.hero-meta').text()).toContain('LEADER: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('POSITIVE: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('NEGATIVE: --')

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(statsStrip.text()).not.toContain('+0%')
    expect(statsStrip.text()).not.toContain('0.00')
    expect(statsStrip.text()).not.toContain('N/A')
  })

  it('does not leak a failed first-load request id or collapse concept summary surfaces into faux empty truth', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: false,
      message: 'concept first load unavailable',
      request_id: 'concept-first-fail',
    })

    const wrapper = mountConceptsPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('SECTORS: --')
    expect(wrapper.get('.hero-meta').text()).toContain('LEADER: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('POSITIVE: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('NEGATIVE: --')
    expect(wrapper.text()).not.toContain('concept-first-fail')

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '--', '--'])
    expect(statsStrip.text()).not.toContain('0')
    expect(statsStrip.text()).not.toContain('N/A')
  })

  it('keeps the last verified request id visible when a manual refresh fails after a successful concept sync', async () => {
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'concept-success-snapshot',
        data: [
          { sector_name: '机器人', change_percent: 6.2, main_net_inflow: 1230000000, leader_stock_name: '绿的谐波' },
          { sector_name: '卫星互联网', change_percent: -1.8, main_net_inflow: -320000000, leader_stock_name: '中国卫通' },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'concept refresh unavailable',
        request_id: 'concept-refresh-fail',
      })

    const wrapper = mountConceptsPage()

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ: concept-success-snapshot')
    expect(wrapper.get('.hero-meta').text()).not.toContain('concept-refresh-fail')
    expect(wrapper.get('.hero-meta').text()).toContain('SECTORS: 2')
    expect(wrapper.text()).toContain('当前仍展示上次成功同步的概念板块数据')
    expect(wrapper.text()).toContain('机器人')
    expect(wrapper.text()).toContain('卫星互联网')
  })
})
