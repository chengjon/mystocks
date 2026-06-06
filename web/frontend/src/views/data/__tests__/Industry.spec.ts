import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { ref } from 'vue'
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
      lastProcessTime: ref(''),
      exec: async (
        apiCall: () => Promise<{ success?: boolean; data?: unknown; message?: string; request_id?: string; process_time_ms?: number }>
      ) => {
        state.loading.value = true
        state.error.value = null

        try {
          const response = await apiCall()
          state.lastRequestId.value = response?.request_id ?? ''
          state.lastProcessTime.value = response?.process_time_ms ? String(response.process_time_ms) : ''

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
  const { default: ArtDecoTable } = await import('@/components/artdeco/trading/ArtDecoTable.vue')

  return {
    ArtDecoButton: {
      props: ['loading', 'disabled'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title'],
      template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText', 'statusType'],
      template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
    ArtDecoTable,
  }
})

import DataIndustryPage from '@/views/data/Industry.vue'

function mountIndustryPage() {
  return mount(DataIndustryPage as never)
}

describe('Data industry routed numeric truth', () => {
  beforeEach(() => {
    apiGetMock.mockReset().mockResolvedValue({
      success: true,
      request_id: 'industry-routed-ok',
      process_time_ms: 12,
      data: [
        {
          rank: 1,
          sector_name: '半导体',
          change_percent: 3.28,
          main_net_inflow: 1280000000,
          main_net_inflow_rate: 14.2,
        },
        {
          rank: 2,
          sector_name: '算力',
          change_percent: 2.16,
          main_net_inflow: 860000000,
          main_net_inflow_rate: 9.7,
        },
      ],
    })
  })

  it('does not render board tally cards as faux delta metrics with fabricated decimal precision', async () => {
    const wrapper = mountIndustryPage()

    await flushPromises()

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['2', '2', '3.28%', '0'])
    expect(statsStrip.text()).not.toContain('+0%')
    expect(statsStrip.text()).not.toContain('2.00')
    expect(statsStrip.text()).not.toContain('0.00')
  })

  it('renders board ranks as ordinal integers instead of fabricated decimal precision', async () => {
    const wrapper = mountIndustryPage()

    await flushPromises()

    const table = wrapper.get('.hybrid-table__content')
    expect(table.text()).toContain('半导体')
    expect(table.text()).toContain('算力')
    expect(table.text()).toContain('1')
    expect(table.text()).toContain('2')
    expect(table.text()).not.toContain('1.00')
    expect(table.text()).not.toContain('2.00')
  })

  it('does not present the industry route as REAL while the first board payload is still unresolved', async () => {
    apiGetMock.mockReset().mockImplementation(() => new Promise(() => {}))

    const wrapper = mountIndustryPage()

    await nextTick()

    expect(wrapper.get('.hero-meta').text()).toContain('DATA: PENDING')
    expect(wrapper.get('.hero-meta').text()).not.toContain('DATA: REAL')
    expect(wrapper.text()).toContain('板块数据同步中')
  })

  it('does not present the industry route as REAL when the first board payload failed before any verified snapshot exists', async () => {
    apiGetMock.mockReset().mockResolvedValue({
      success: false,
      request_id: 'industry-first-fail',
      message: '板块数据加载失败',
    })

    const wrapper = mountIndustryPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('DATA: UNAVAILABLE')
    expect(wrapper.get('.hero-meta').text()).not.toContain('DATA: REAL')
    expect(wrapper.text()).toContain('板块数据加载失败')
  })

  it('does not leak a failed first-load board request id before any verified snapshot exists', async () => {
    apiGetMock.mockReset().mockResolvedValue({
      success: false,
      request_id: 'industry-first-fail',
      message: '板块数据加载失败',
    })

    const wrapper = mountIndustryPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).not.toContain('industry-first-fail')
  })

  it('keeps the last verified board request id visible when a manual refresh fails', async () => {
    apiGetMock
      .mockReset()
      .mockResolvedValueOnce({
        success: true,
        request_id: 'industry-success',
        process_time_ms: 12,
        data: [
          {
            rank: 1,
            sector_name: '半导体',
            change_percent: 3.28,
            main_net_inflow: 1280000000,
            main_net_inflow_rate: 14.2,
          },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        request_id: 'industry-refresh-fail',
        message: '板块数据加载失败',
      })

    const wrapper = mountIndustryPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: industry-success')

    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: industry-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('industry-refresh-fail')
  })
})
