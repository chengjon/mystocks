import { flushPromises, mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

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
      loading: { value: false },
      error: { value: null as string | null },
      lastRequestId: { value: '' },
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

import FundFlowPage from '@/views/data/FundFlow.vue'

describe('Data fund flow partial-success truthfulness', () => {
  it('keeps successful summary content visible while surfacing a partial failure warning', async () => {
    apiGetMock.mockReset()
    apiGetMock
      .mockResolvedValueOnce({
        success: true,
        request_id: 'fund-summary-ok',
        data: [
          { 交易日: '2026-04-01', 板块: '沪股通', 资金方向: '北向', 成交净买额: 8.2, 指数涨跌幅: 0.41 },
          { 交易日: '2026-04-01', 板块: '深股通', 资金方向: '北向', 成交净买额: 5.7, 指数涨跌幅: 0.38 },
        ],
      })
      .mockResolvedValueOnce({
        success: false,
        message: '个股资金排行加载失败',
      })

    const wrapper = mount(FundFlowPage as never, {
      global: {
        stubs: {
          ArtDecoButton: {
            emits: ['click'],
            template: '<button @click="$emit(\'click\')"><slot /></button>',
          },
          ArtDecoCard: {
            props: ['title'],
            template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
          },
          ArtDecoHeader: {
            props: ['title', 'subtitle', 'statusText'],
            template: '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
          },
          ArtDecoIcon: {
            template: '<span />',
          },
          ArtDecoSelect: {
            props: ['modelValue', 'options'],
            emits: ['update:modelValue'],
            template: '<select :value="modelValue"><option v-for="option in options" :key="option.value" :value="option.value">{{ option.label }}</option></select>',
          },
          ArtDecoStatCard: {
            props: ['label', 'value'],
            template: '<div>{{ label }}:{{ value }}</div>',
          },
          ArtDecoTable: {
            props: ['data'],
            template: '<div class="fund-table">{{ JSON.stringify(data) }}</div>',
          },
          ArtDecoChart: {
            template: '<div class="fund-chart-stub">chart</div>',
          },
        },
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('部分数据同步失败')
    expect(wrapper.text()).toContain('个股排行刷新失败')
    expect(wrapper.text()).toContain('当前仅展示已成功同步的北向概览与趋势')
    expect(wrapper.text()).toContain('今日资金流向趋势')
    expect(wrapper.find('.fund-chart-stub').exists()).toBe(true)
    expect(wrapper.get('.hero-meta').text()).toContain('REQ: N/A')
    expect(wrapper.get('.hero-meta').text()).not.toContain('fund-summary-ok')
    expect(wrapper.text()).not.toContain('资金流向加载失败')
  })
})
