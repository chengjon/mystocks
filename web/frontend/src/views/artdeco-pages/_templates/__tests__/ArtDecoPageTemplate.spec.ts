import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { getDataMock, postDataMock, mockValues } = vi.hoisted(() => ({
  getDataMock: vi.fn(),
  postDataMock: vi.fn(),
  mockValues: {
    loading: false,
    error: null as unknown,
  },
}))

vi.mock('@/composables/useApiService', async () => {
  const { ref } = await import('vue')

  return {
    useApiService: () => ({
      loading: ref(mockValues.loading),
      error: ref(mockValues.error),
      getData: getDataMock,
      postData: postDataMock,
    }),
  }
})

import ArtDecoPageTemplate from '../ArtDecoPageTemplate.vue'

const basePageConfig = {
  title: '风险管理中心',
  subtitle: '测试页面骨架',
  permission: '',
}

const tabs = [
  { key: 'overview', label: '概览', icon: 'activity' },
  { key: 'detail', label: '详情', icon: 'list' },
]

const mountPageTemplate = (options?: {
  pageConfig?: Record<string, unknown>
  tabs?: Array<{ key: string; label: string; icon?: string }>
  defaultTab?: string
  slots?: Record<string, string>
}) =>
  mount(ArtDecoPageTemplate as never, {
    props: {
      pageConfig: {
        ...basePageConfig,
        ...(options?.pageConfig ?? {}),
      },
      tabs: options?.tabs ?? [],
      defaultTab: options?.defaultTab ?? '',
    },
    slots: options?.slots,
    global: {
      stubs: {
        ArtDecoHeader: {
          props: ['title', 'subtitle', 'showStatus', 'statusText', 'statusType'],
          template: `
            <header class="header-stub">
              <h1>{{ title }}</h1>
              <p v-if="subtitle">{{ subtitle }}</p>
              <div class="status-copy">{{ statusText }}</div>
              <div class="header-actions"><slot name="actions" /></div>
            </header>
          `,
        },
        ArtDecoButton: {
          props: ['loading', 'variant', 'priority', 'motion', 'size'],
          emits: ['click'],
          template: `
            <button
              class="artdeco-button-stub"
              :data-loading="loading ? 'true' : 'false'"
              @click="$emit('click', $event)"
            >
              <slot name="icon" />
              <slot />
            </button>
          `,
        },
        ArtDecoIcon: {
          props: ['name', 'size'],
          template: '<span class="icon-stub">{{ name }}</span>',
        },
        ArtDecoSkeleton: {
          props: ['columns', 'rows'],
          template: '<div class="skeleton-stub">Skeleton {{ columns }}x{{ rows }}</div>',
        },
        ArtDecoStatCard: {
          props: ['label', 'value'],
          template: '<div class="stat-card-stub">{{ label }} {{ value }}</div>',
        },
      },
    },
  })

describe('ArtDecoPageTemplate', () => {
  beforeEach(() => {
    localStorage.clear()
    vi.clearAllMocks()
    vi.useRealTimers()
    mockValues.loading = false
    mockValues.error = null
    getDataMock.mockResolvedValue({
      success: true,
      data: { count: 1 },
      request_id: 'req-default',
    })
    postDataMock.mockResolvedValue({
      success: true,
      data: { ok: true },
      request_id: 'req-post',
    })
  })

  it('renders title and default refresh action when no custom header slot is provided', async () => {
    const wrapper = mountPageTemplate()

    await flushPromises()

    expect(wrapper.text()).toContain('风险管理中心')
    expect(wrapper.text()).toContain('刷新')
  })

  it('uses custom header-actions slot instead of the default refresh button', async () => {
    const wrapper = mountPageTemplate({
      slots: {
        'header-actions': '<button class="custom-header-action">自定义动作</button>',
      },
    })

    await flushPromises()

    expect(wrapper.find('.custom-header-action').exists()).toBe(true)
    expect(wrapper.text()).not.toContain('刷新')
  })

  it('renders placeholder content when no apiUrl is configured', async () => {
    const wrapper = mountPageTemplate()

    await flushPromises()

    expect(wrapper.text()).toContain('页面内容区域')
    expect(wrapper.find('.empty-state').exists()).toBe(false)
  })

  it('renders permission denied state when auth store lacks the required permission', async () => {
    localStorage.setItem('auth-store', JSON.stringify({ permissions: ['risk:view-basic'] }))

    const wrapper = mountPageTemplate({
      pageConfig: {
        permission: 'risk:admin',
      },
    })

    await flushPromises()

    expect(wrapper.find('.permission-denied').exists()).toBe(true)
    expect(wrapper.text()).toContain('访问受限')
  })

  it('renders loading state while api request is pending', async () => {
    mockValues.loading = true
    getDataMock.mockImplementation(() => new Promise(() => {}))

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/loading',
      },
    })

    await flushPromises()

    expect(getDataMock).toHaveBeenCalledWith('/api/risk/loading', {})
    expect(wrapper.find('.loading-state').exists()).toBe(true)
    expect(wrapper.text()).toContain('Skeleton')
  })

  it('emits data-error and renders error state when data request fails', async () => {
    getDataMock.mockRejectedValue(new Error('network failed'))

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/error',
      },
    })

    await flushPromises()

    expect(wrapper.find('.error-boundary').exists()).toBe(true)
    expect(wrapper.text()).toContain('加载失败')
    expect(wrapper.emitted('data-error')).toHaveLength(1)
  })

  it('emits data-loaded and displays request id trace for successful data responses', async () => {
    const payload = { positions: 3 }
    getDataMock.mockResolvedValue({
      success: true,
      request_id: 'req-success-001',
      data: payload,
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/success',
        showTabs: true,
      },
      tabs,
      defaultTab: 'overview',
    })

    await flushPromises()

    expect(wrapper.emitted('data-loaded')).toEqual([[payload]])
    expect(wrapper.text()).toContain('REQ_ID: req-success-001')
  })

  it('renders empty state when api returns an empty array payload', async () => {
    getDataMock.mockResolvedValue({
      success: true,
      request_id: 'req-empty-001',
      data: [],
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/empty',
        emptyMessage: '暂无风险记录',
      },
    })

    await flushPromises()

    expect(wrapper.find('.empty-state').exists()).toBe(true)
    expect(wrapper.text()).toContain('暂无风险记录')
  })

  it('emits tab-change when switching tabs', async () => {
    const wrapper = mountPageTemplate({
      pageConfig: {
        showTabs: true,
      },
      tabs,
      defaultTab: 'overview',
    })

    await flushPromises()

    const detailTab = wrapper.findAll('.tab-button').find((tab) => tab.text().includes('详情'))
    expect(detailTab).toBeTruthy()

    await detailTab!.trigger('click')

    expect(wrapper.emitted('tab-change')).toEqual([['detail']])
  })

  it('prefers nested data.request_id when response uses wrapped payload shape', async () => {
    getDataMock.mockResolvedValue({
      success: true,
      request_id: 'req-root-001',
      data: {
        success: true,
        request_id: 'req-nested-001',
        data: {
          positions: 8,
        },
      },
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/nested-request-id',
        showTabs: true,
      },
      tabs,
      defaultTab: 'overview',
    })

    await flushPromises()

    expect(wrapper.emitted('data-loaded')).toEqual([[{ positions: 8 }]])
    expect(wrapper.text()).toContain('REQ_ID: req-nested-001')
  })

  it('extracts request id from response headers when top-level request_id is missing', async () => {
    getDataMock.mockResolvedValue({
      success: true,
      headers: {
        'x-request-id': 'req-header-001',
      },
      data: {
        positions: 5,
      },
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/header-request-id',
        showTabs: true,
      },
      tabs,
      defaultTab: 'overview',
    })

    await flushPromises()

    expect(wrapper.text()).toContain('REQ_ID: req-header-001')
  })

  it('renders error state when api returns success false', async () => {
    getDataMock.mockResolvedValue({
      success: false,
      message: 'upstream validation failed',
      request_id: 'req-fail-001',
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/success-false',
      },
    })

    await flushPromises()

    expect(wrapper.find('.error-boundary').exists()).toBe(true)
    expect(wrapper.text()).toContain('加载失败')
    expect(wrapper.emitted('data-error')).toHaveLength(1)
  })

  it('uses postData when apiMethod is POST', async () => {
    postDataMock.mockResolvedValue({
      success: true,
      request_id: 'req-post-001',
      data: {
        positions: 11,
      },
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/post',
        apiMethod: 'POST',
        apiParams: {
          market: 'cn',
        },
      },
    })

    await flushPromises()

    expect(postDataMock).toHaveBeenCalledWith('/api/risk/post', { market: 'cn' })
    expect(getDataMock).not.toHaveBeenCalled()
    expect(wrapper.emitted('data-loaded')).toEqual([[{ positions: 11 }]])
  })

  it('respects cacheTime and avoids duplicate requests while cache is still valid', async () => {
    vi.useFakeTimers()
    vi.setSystemTime(new Date('2026-01-01T00:00:00.000Z'))

    getDataMock.mockResolvedValue({
      success: true,
      request_id: 'req-cache-001',
      data: {
        cached: true,
      },
    })

    const wrapper = mountPageTemplate({
      pageConfig: {
        apiUrl: '/api/risk/cache',
        apiParams: {
          page: 1,
        },
        cacheTime: 10_000,
      },
    })

    await flushPromises()
    expect(getDataMock).toHaveBeenCalledTimes(1)

    await wrapper.setProps({
      pageConfig: {
        ...basePageConfig,
        apiUrl: '/api/risk/cache',
        apiParams: {
          page: 1,
        },
        cacheTime: 10_000,
      },
    })

    await flushPromises()
    expect(getDataMock).toHaveBeenCalledTimes(1)
  })
})
