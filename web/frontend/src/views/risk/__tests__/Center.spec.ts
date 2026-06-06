import { flushPromises, mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { errorMock, getDataMock, loadingMock, postDataMock } = vi.hoisted(() => ({
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  ...(() => {
    const { ref } = require('vue')
    return {
      errorMock: ref<string | null>(null),
      loadingMock: ref(false),
    }
  })(),
  getDataMock: vi.fn(),
  postDataMock: vi.fn(),
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    info: vi.fn(),
  },
}))

vi.mock('@/composables/useApiService', () => ({
  useApiService: () => ({
    loading: loadingMock,
    error: errorMock,
    getData: async (...args: unknown[]) => {
      loadingMock.value = true
      errorMock.value = null

      try {
        return await getDataMock(...args)
      } catch (error: unknown) {
        errorMock.value = error instanceof Error ? error.message : '请求失败'
        throw error
      } finally {
        loadingMock.value = false
      }
    },
    postData: async (...args: unknown[]) => {
      loadingMock.value = true
      errorMock.value = null

      try {
        return await postDataMock(...args)
      } catch (error: unknown) {
        errorMock.value = error instanceof Error ? error.message : '请求失败'
        throw error
      } finally {
        loadingMock.value = false
      }
    },
  }),
}))

import RiskCenterPage from '../Center.vue'

function mountRiskCenterPage() {
  return mount(RiskCenterPage as never, {
    global: {
      directives: {
        loading: {},
      },
      stubs: {
        ArtDecoButton: {
          props: ['loading', 'disabled'],
          emits: ['click'],
          template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
        },
        ArtDecoHeader: {
          props: ['title', 'subtitle', 'showStatus', 'statusText', 'statusType'],
          template:
            '<header><h1>{{ title }}</h1><p>{{ subtitle }}</p><span>{{ statusText }}</span><slot name="actions" /></header>',
        },
        ArtDecoIcon: {
          template: '<span />',
        },
        ArtDecoRiskOverviewPanel: {
          template: '<div class="risk-overview-panel-stub" />',
        },
        ArtDecoRiskStatsGrid: {
          template: '<div class="risk-stats-grid-stub" />',
        },
        ArtDecoRiskStockPanel: {
          template: '<div class="risk-stock-panel-stub" />',
        },
        ArtDecoSkeleton: {
          template: '<div class="artdeco-skeleton-stub" />',
        },
        ArtDecoStatCard: {
          template: '<div class="artdeco-stat-card-stub" />',
        },
        Transition: false,
      },
    },
  })
}

describe('RiskCenter routed freshness truth', () => {
  beforeEach(() => {
    loadingMock.value = false
    errorMock.value = null
    getDataMock.mockReset()
    postDataMock.mockReset()
  })

  it('does not seed footer freshness with local current time while the first positions snapshot is still pending', async () => {
    getDataMock.mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mountRiskCenterPage()

    await nextTick()
    await nextTick()

    expect(wrapper.find('.loading-state').exists()).toBe(true)
    expect(wrapper.get('.risk-footer').text()).toContain('最后一次更新：--')
  })

  it('does not claim a fixed five-minute auto-refresh cadence when the canonical route has no owned scheduler', async () => {
    getDataMock.mockImplementationOnce(() => new Promise(() => {}))

    const wrapper = mountRiskCenterPage()

    await nextTick()
    await nextTick()

    expect(wrapper.get('.risk-footer').text()).not.toContain('每5分钟自动更新')
    expect(wrapper.get('.risk-footer').text()).toContain('按当前页同步结果更新')
  })

  it('does not seed footer freshness with local current time when the first positions snapshot failed before any verified data exists', async () => {
    getDataMock.mockRejectedValueOnce(new Error('positions unavailable'))

    const wrapper = mountRiskCenterPage()

    await flushPromises()

    expect(wrapper.find('.error-boundary').exists()).toBe(true)
    expect(wrapper.text()).toContain('数据请求失败，请稍后重试')
    expect(wrapper.get('.risk-footer').text()).toContain('最后一次更新：--')
  })

})
