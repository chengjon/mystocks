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
  const { default: ArtDecoTable } = await import('@/components/artdeco/trading/ArtDecoTable.vue')

  return {
    ArtDecoButton: {
      props: ['loading', 'disabled'],
      emits: ['click'],
      template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
    },
    ArtDecoCard: {
      props: ['title', 'hoverable'],
      template: '<section class="artdeco-card-stub" :data-hoverable="String(hoverable)"><h2 v-if="title">{{ title }}</h2><slot /></section>',
    },
    ArtDecoHeader: {
      props: ['title', 'subtitle', 'statusText'],
      template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
    },
    ArtDecoIcon: {
      template: '<span />',
    },
    ArtDecoSelect: {
      props: ['modelValue', 'options', 'label'],
      emits: ['update:modelValue'],
      template: '<label><span>{{ label }}</span><select :value="modelValue" @change="$emit(\'update:modelValue\', $event.target.value)"><option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option></select></label>',
    },
    ArtDecoStatCard,
    ArtDecoTable,
  }
})

import RealtimePage from '@/views/market/Realtime.vue'

const REALTIME_QUOTES_PAYLOAD = {
  quotes: [
    {
      symbol: '000001',
      name: '平安银行',
      current_price: 10.52,
      change_percent: 1.28,
      amount: 128000000,
    },
    {
      symbol: '600519',
      name: '贵州茅台',
      current_price: 1620.35,
      change_percent: -0.42,
      amount: 386000000,
    },
  ],
}

function mountRealtimePage() {
  return mount(RealtimePage as never, {
    global: {
      config: {
        warnHandler: () => {},
      },
    },
  })
}

describe('Market realtime unresolved first-load truth', () => {
  beforeEach(() => {
    apiGetMock.mockReset()
  })

  it('does not present unresolved first-load metrics as faux zero values before the first quote snapshot resolves', async () => {
    apiGetMock.mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mountRealtimePage()

    await nextTick()
    await nextTick()

    const statsStrip = wrapper.get('.stats-strip')
    expect(statsStrip.findAll('.artdeco-stat-change')).toHaveLength(0)
    expect(statsStrip.findAll('.artdeco-stat-value').map((node) => node.text())).toEqual(['--', '--', '核心蓝筹样本', '--'])
    expect(wrapper.get('.hero-meta').text()).toContain('SAMPLE: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('MOOD: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('UP: --')
    expect(wrapper.get('.content-shell-meta').text()).toContain('DOWN: --')
    expect(wrapper.text()).toContain('首份样本快照同步中，涨跌分布待接入。')
    expect(wrapper.text()).not.toContain('0亿')
    expect(wrapper.text()).not.toContain('0%')
    expect(wrapper.text()).not.toContain('0只')
  })

  it('does not leak a failed first-load quote request id before any verified snapshot exists', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: false,
      request_id: 'realtime-first-fail',
      message: 'quotes unavailable',
    })

    const wrapper = mountRealtimePage()

    await nextTick()
    await nextTick()

    expect(wrapper.get('.hero-meta').text()).toContain('TRACE_ID: N/A')
    expect(wrapper.get('.hero-meta').text()).not.toContain('realtime-first-fail')
    expect(wrapper.text()).toContain('当前暂无已验证样本快照。')
    expect(wrapper.text()).not.toContain('已保留上一份有效样本快照')
  })

  it('keeps the last verified quote request id visible when a refresh fails after a successful sync', async () => {
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'realtime-success',
        data: REALTIME_QUOTES_PAYLOAD,
      })
      .mockResolvedValueOnce({
        success: false,
        request_id: 'realtime-refresh-fail',
        message: 'quotes refresh unavailable',
      })

    const wrapper = mountRealtimePage()

    await nextTick()
    await nextTick()
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('TRACE_ID: realtime-success')

    await wrapper.get('button').trigger('click')
    await nextTick()
    await nextTick()
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('TRACE_ID: realtime-success')
    expect(wrapper.get('.hero-meta').text()).not.toContain('realtime-refresh-fail')
  })

  it('labels service-worker cached quote snapshots as retained cache data', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: true,
      request_id: 'realtime-sw-cache',
      data: {
        ...REALTIME_QUOTES_PAYLOAD,
        cache_source: 'service-worker-cache',
      },
    })

    const wrapper = mountRealtimePage()

    await nextTick()
    await nextTick()
    await flushPromises()

    expect(wrapper.get('.hero-meta').text()).toContain('TRACE_ID: realtime-sw-cache')
    expect(wrapper.text()).toContain('缓存快照')
    expect(wrapper.text()).toContain('当前行情来自本地缓存快照，非实时网络刷新。')
  })

  it('does not expose hover affordance on informational snapshot cards', async () => {
    apiGetMock.mockResolvedValueOnce({
      success: true,
      request_id: 'realtime-success',
      data: REALTIME_QUOTES_PAYLOAD,
    })

    const wrapper = mountRealtimePage()

    await nextTick()
    await nextTick()
    await flushPromises()

    const snapshotCards = wrapper.findAll('.artdeco-card-stub').filter((card) => {
      const text = card.text()
      return text.includes('样本报价快照') || text.includes('样本涨跌分布')
    })

    expect(snapshotCards).toHaveLength(2)
    expect(snapshotCards.every((card) => card.attributes('data-hoverable') === 'false')).toBe(true)
  })

  it('does not leak the previous preset rows into a new preset while that preset is still on its first unresolved load', async () => {
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'realtime-core-success',
        data: REALTIME_QUOTES_PAYLOAD,
      })
      .mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mountRealtimePage()

    await nextTick()
    await nextTick()
    await flushPromises()

    expect(wrapper.text()).toContain('核心蓝筹样本')
    expect(wrapper.text()).toContain('平安银行')
    expect(wrapper.text()).toContain('贵州茅台')

    await wrapper.get('select').setValue('finance')
    await nextTick()
    await nextTick()

    expect(wrapper.text()).toContain('金融权重样本')
    expect(wrapper.get('.hero-meta').text()).toContain('PRESET: 金融权重样本')
    expect(wrapper.findAll('tbody tr')).toHaveLength(0)
    expect(wrapper.text()).not.toContain('平安银行')
    expect(wrapper.text()).not.toContain('贵州茅台')
  })
})
