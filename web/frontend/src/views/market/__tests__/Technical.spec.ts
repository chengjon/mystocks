import { flushPromises, mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getKlineMock } = vi.hoisted(() => ({
  getKlineMock: vi.fn(),
}))

vi.mock('@/api/index', () => ({
  dataApi: {
    getKline: getKlineMock,
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
      props: ['title', 'subtitle', 'statusText'],
      template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoStatCard,
  }
})

vi.mock('@/components/market/ProKLineChart.vue', () => ({
  default: {
    template: '<div class="pro-kline-chart-stub" />',
  },
}))

import TechnicalPage from '@/views/market/Technical.vue'

function mountTechnicalPage() {
  return mount(TechnicalPage as never, {
    global: {
      config: {
        warnHandler: () => {},
      },
    },
  })
}

describe('Market technical unresolved first-load truth', () => {
  beforeEach(() => {
    getKlineMock.mockReset()
  })

  it('does not present unresolved first-load point counters as faux zero values before the first k-line snapshot resolves', async () => {
    getKlineMock.mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mountTechnicalPage()

    await nextTick()
    await nextTick()

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['000001', '--', '--', '--'])
    expect(wrapper.get('.hero-meta').text()).toContain('POINTS: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('POINTS: --')
    expect(wrapper.text()).toContain('Synchronizing K-Line Sample')
    expect(wrapper.text()).not.toContain('POINTS: 0')
    expect(wrapper.text()).not.toContain('Waiting For K-Line Sample')
  })

  it('does not leak a failed first-load request id as if it produced the visible k-line snapshot', async () => {
    getKlineMock.mockResolvedValueOnce({
      success: false,
      message: 'kline first load unavailable',
      request_id: 'kline-first-fail',
    })

    const wrapper = mountTechnicalPage()

    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ: N/A')
    expect(wrapper.get('.hero-meta').text()).toContain('POINTS: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('POINTS: --')
    expect(wrapper.text()).toContain('K线数据加载失败，已保留上一份有效样本。')
    expect(wrapper.text()).not.toContain('kline-first-fail')
    expect(wrapper.text()).not.toContain('POINTS: 0')
  })

  it('keeps the last verified request id visible when a refresh fails after a successful k-line sync', async () => {
    getKlineMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'kline-success-snapshot',
        data: {
          data: [
            { datetime: '2026-04-01 15:00:00', open: 100, high: 102, low: 99, close: 101, volume: 1000000 },
            { datetime: '2026-04-02 15:00:00', open: 101, high: 103, low: 100, close: 102, volume: 1005000 },
          ],
        },
      })
      .mockResolvedValueOnce({
        success: false,
        message: 'kline refresh unavailable',
        request_id: 'kline-refresh-fail',
      })

    const wrapper = mountTechnicalPage()

    await flushPromises()
    await wrapper.get('button').trigger('click')
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('REQ: kline-success-snapshot')
    expect(wrapper.get('.hero-meta').text()).not.toContain('kline-refresh-fail')
    expect(wrapper.get('.hero-meta').text()).toContain('POINTS: 2')
    expect(wrapper.text()).toContain('K线数据加载失败，已保留上一份有效样本。')
    expect(wrapper.text()).toContain('2026-04-02')
  })
})
