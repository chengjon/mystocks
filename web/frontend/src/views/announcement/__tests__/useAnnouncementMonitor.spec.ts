import { flushPromises, mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  axiosGetMock,
  axiosPostMock,
  axiosPutMock,
  axiosDeleteMock,
  confirmMock,
  routeMock,
} = vi.hoisted(() => ({
  axiosGetMock: vi.fn(),
  axiosPostMock: vi.fn(),
  axiosPutMock: vi.fn(),
  axiosDeleteMock: vi.fn(),
  confirmMock: vi.fn(),
  routeMock: {
    params: {
      symbol: '600519',
    },
  },
}))

vi.mock('axios', () => ({
  default: {
    get: axiosGetMock,
    post: axiosPostMock,
    put: axiosPutMock,
    delete: axiosDeleteMock,
  },
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    error: vi.fn(),
    success: vi.fn(),
  },
  ElMessageBox: {
    confirm: confirmMock,
  },
}))

vi.mock('vue-router', () => ({
  useRoute: () => routeMock,
}))

import { useAnnouncementMonitor } from '../composables/useAnnouncementMonitor'

let monitorApi: ReturnType<typeof useAnnouncementMonitor>

const Harness = defineComponent({
  setup() {
    monitorApi = useAnnouncementMonitor()
    return () => null
  },
})

describe('useAnnouncementMonitor stats refresh truth', () => {
  beforeEach(() => {
    axiosGetMock.mockReset()
    axiosPostMock.mockReset()
    axiosPutMock.mockReset()
    axiosDeleteMock.mockReset()
    confirmMock.mockReset()
    routeMock.params.symbol = '600519'
  })

  it('does not silently preserve stale announcement stats after the stats slice refresh failed', async () => {
    let statsFetchCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url.endsWith('/api/announcement/stats')) {
        statsFetchCount += 1

        if (statsFetchCount === 1) {
          return {
            data: {
              success: true,
              total_count: 2,
              today_count: 2,
              important_count: 1,
              triggered_count: 0,
            },
          }
        }

        throw new Error('announcement stats unavailable')
      }

      if (url.endsWith('/api/announcement/list')) {
        return {
          data: {
            success: true,
            data: [
              {
                id: 1,
                stock_code: '600519',
                title: '2026 年第一季度经营数据公告',
              },
            ],
            total: 1,
          },
        }
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        return { data: [] }
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return {
          data: {
            success: true,
            data: [],
          },
        }
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    expect(monitorApi.stats.value).toMatchObject({
      total_count: 2,
      today_count: 2,
      important_count: 1,
      triggered_count: 0,
    })
    expect(monitorApi.announcements.value).toHaveLength(1)

    await monitorApi.fetchStats()
    await flushPromises()

    expect(monitorApi.stats.value).toEqual({})
    expect(monitorApi.announcements.value).toHaveLength(1)
  })

  it('normalizes announcement rows so announcement_title is still available as title for detail/news rendering', async () => {
    axiosGetMock.mockImplementation(async (url: string) => {
      if (url.endsWith('/api/announcement/stats')) {
        return {
          data: {
            success: true,
            total_count: 2,
            today_count: 2,
            important_count: 1,
            triggered_count: 0,
          },
        }
      }

      if (url.endsWith('/api/announcement/list')) {
        return {
          data: {
            success: true,
            data: [
              {
                id: 1,
                stock_code: '600519',
                stock_name: '贵州茅台',
                announcement_title: '2026 年第一季度经营数据公告',
                announcement_type: '年度报告',
                importance_level: 5,
                publish_date: '2026-04-05',
                data_source: 'cninfo',
                url: 'https://example.com/announcements/600519-q1',
              },
            ],
            total: 1,
          },
        }
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        return { data: [] }
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return {
          data: {
            success: true,
            data: [],
          },
        }
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    expect(monitorApi.announcements.value).toHaveLength(1)
    expect(monitorApi.announcements.value[0]).toMatchObject({
      title: '2026 年第一季度经营数据公告',
      type: '年度报告',
      stock_code: '600519',
      stock_name: '贵州茅台',
      importance_level: 5,
      publish_date: '2026-04-05',
      data_source: 'cninfo',
      url: 'https://example.com/announcements/600519-q1',
    })
  })

  it('clears the previous selector stats while a newly selected detail symbol stats slice is still unresolved', async () => {
    axiosGetMock.mockImplementation((url: string) => {
      if (url.endsWith('/api/announcement/stats')) {
        if (routeMock.params.symbol === '000001') {
          return new Promise(() => {})
        }

        return Promise.resolve({
          data: {
            success: true,
            total_count: 2,
            today_count: 2,
            important_count: 1,
            triggered_count: 0,
          },
        })
      }

      if (url.endsWith('/api/announcement/list')) {
        return Promise.resolve({
          data: {
            success: true,
            data: [
              {
                id: 1,
                stock_code: '600519',
                title: '2026 年第一季度经营数据公告',
              },
            ],
            total: 1,
          },
        })
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        return Promise.resolve({ data: [] })
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return Promise.resolve({
          data: {
            success: true,
            data: [],
          },
        })
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    expect(monitorApi.stats.value).toMatchObject({
      total_count: 2,
      today_count: 2,
      important_count: 1,
      triggered_count: 0,
    })

    routeMock.params.symbol = '000001'
    void monitorApi.fetchStats()
    await Promise.resolve()

    expect(monitorApi.stats.value).toEqual({})
  })

  it('marks monitor-rules slice unavailable instead of silently presenting an empty rules table when the first rules request failed', async () => {
    axiosGetMock.mockImplementation(async (url: string) => {
      if (url.endsWith('/api/announcement/stats')) {
        return {
          data: {
            success: true,
            total_count: 1,
            today_count: 1,
            important_count: 1,
            triggered_count: 0,
          },
        }
      }

      if (url.endsWith('/api/announcement/list')) {
        return {
          data: {
            success: true,
            data: [
              {
                id: 1,
                stock_code: '600519',
                title: '2026 年第一季度经营数据公告',
              },
            ],
            total: 1,
          },
        }
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        throw new Error('monitor rules unavailable')
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return {
          data: {
            success: true,
            data: [],
          },
        }
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    expect(monitorApi.monitorRules.value).toEqual([])
    expect(monitorApi.monitorRulesSliceState.value).toBe('unavailable')
    expect(monitorApi.announcements.value).toHaveLength(1)
  })

  it('keeps the last verified monitor-rules snapshot when a later rules refresh failed', async () => {
    let rulesFetchCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url.endsWith('/api/announcement/stats')) {
        return {
          data: {
            success: true,
            total_count: 1,
            today_count: 1,
            important_count: 1,
            triggered_count: 0,
          },
        }
      }

      if (url.endsWith('/api/announcement/list')) {
        return {
          data: {
            success: true,
            data: [
              {
                id: 1,
                stock_code: '600519',
                title: '2026 年第一季度经营数据公告',
              },
            ],
            total: 1,
          },
        }
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        rulesFetchCount += 1

        if (rulesFetchCount === 1) {
          return {
            data: [
              {
                id: 11,
                rule_name: '高重要性公告',
                stock_codes: ['600519'],
                keywords: ['经营数据'],
                min_importance_level: 4,
                notify_enabled: true,
                is_active: true,
              },
            ],
          }
        }

        throw new Error('monitor rules refresh unavailable')
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return {
          data: {
            success: true,
            data: [],
          },
        }
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    expect(monitorApi.monitorRules.value).toHaveLength(1)
    expect(monitorApi.monitorRulesSliceState.value).toBe('ready')

    await monitorApi.fetchMonitorRules()
    await flushPromises()

    expect(monitorApi.monitorRules.value).toHaveLength(1)
    expect(monitorApi.monitorRulesSliceState.value).toBe('stale')
  })

  it('keeps the last verified triggered-records snapshot when a later records refresh failed', async () => {
    let recordsFetchCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url.endsWith('/api/announcement/stats')) {
        return {
          data: {
            success: true,
            total_count: 1,
            today_count: 1,
            important_count: 1,
            triggered_count: 1,
          },
        }
      }

      if (url.endsWith('/api/announcement/list')) {
        return {
          data: {
            success: true,
            data: [
              {
                id: 1,
                stock_code: '600519',
                title: '2026 年第一季度经营数据公告',
              },
            ],
            total: 1,
          },
        }
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        return { data: [] }
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        recordsFetchCount += 1

        if (recordsFetchCount === 1) {
          return {
            data: {
              success: true,
              data: [
                {
                  rule_name: '高重要性公告',
                  stock_code: '600519',
                  announcement_title: '2026 年第一季度经营数据公告',
                  matched_keywords: ['经营数据'],
                  triggered_at: '2026-05-05 10:00:00',
                },
              ],
            },
          }
        }

        throw new Error('triggered records refresh unavailable')
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    expect(monitorApi.triggeredRecords.value).toHaveLength(1)
    expect(monitorApi.triggeredRecordsSliceState.value).toBe('ready')

    await monitorApi.fetchTriggeredRecords()
    await flushPromises()

    expect(monitorApi.triggeredRecords.value).toHaveLength(1)
    expect(monitorApi.triggeredRecordsSliceState.value).toBe('stale')
  })

  it('clears the previously verified announcement rows when the selector changed and the new selector failed before any verified snapshot existed', async () => {
    axiosGetMock.mockImplementation(async (url: string, config?: { params?: Record<string, unknown> }) => {
      if (url.endsWith('/api/announcement/stats')) {
        return {
          data: {
            success: true,
            total_count: 0,
            today_count: 0,
            important_count: 0,
            triggered_count: 0,
          },
        }
      }

      if (url.endsWith('/api/announcement/list')) {
        const stockCode = typeof config?.params?.stock_code === 'string'
          ? config.params.stock_code
          : ''

        if (!stockCode) {
          return {
            data: {
              success: true,
              data: [],
              total: 0,
            },
          }
        }

        if (stockCode === '600519') {
          return {
            data: {
              success: true,
              data: [
                {
                  id: 1,
                  stock_code: '600519',
                  title: '2026 年第一季度经营数据公告',
                },
              ],
              total: 1,
            },
          }
        }

        throw new Error(`announcement list unavailable for ${stockCode}`)
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        return { data: [] }
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return {
          data: {
            success: true,
            data: [],
          },
        }
      }

      throw new Error(`Unhandled GET ${url}`)
    })

    mount(Harness)
    await flushPromises()

    monitorApi.searchForm.stock_code = '600519'
    await monitorApi.fetchAnnouncements()
    await flushPromises()

    expect(monitorApi.announcements.value).toHaveLength(1)
    expect((monitorApi as { announcementSliceState?: { value?: string } }).announcementSliceState?.value).toBe('ready')

    monitorApi.searchForm.stock_code = '000001'
    await monitorApi.fetchAnnouncements()
    await flushPromises()

    expect(monitorApi.announcements.value).toEqual([])
    expect(monitorApi.pagination.total).toBe(0)
    expect((monitorApi as { announcementSliceState?: { value?: string } }).announcementSliceState?.value).toBe('unavailable')
  })

  it('clears the previous selector rows while a newly selected detail symbol is still unresolved without its own verified snapshot', async () => {
    axiosGetMock.mockImplementation((url: string, config?: { params?: Record<string, unknown> }) => {
      if (url.endsWith('/api/announcement/stats')) {
        return Promise.resolve({
          data: {
            success: true,
            total_count: 0,
            today_count: 0,
            important_count: 0,
            triggered_count: 0,
          },
        })
      }

      if (url.endsWith('/api/announcement/list')) {
        const stockCode = typeof config?.params?.stock_code === 'string'
          ? config.params.stock_code
          : ''

        if (!stockCode) {
          return Promise.resolve({
            data: {
              success: true,
              data: [],
              total: 0,
            },
          })
        }

        if (stockCode === '600519') {
          return Promise.resolve({
            data: {
              success: true,
              data: [
                {
                  id: 1,
                  stock_code: '600519',
                  title: '2026 年第一季度经营数据公告',
                },
              ],
              total: 1,
            },
          })
        }

        if (stockCode === '000001') {
          return new Promise(() => {})
        }
      }

      if (url.endsWith('/api/announcement/monitor-rules')) {
        return Promise.resolve({ data: [] })
      }

      if (url.endsWith('/api/announcement/triggered-records')) {
        return Promise.resolve({
          data: {
            success: true,
            data: [],
          },
        })
      }

      return Promise.reject(new Error(`Unhandled GET ${url}`))
    })

    mount(Harness)
    await flushPromises()

    monitorApi.searchForm.stock_code = '600519'
    await monitorApi.fetchAnnouncements()
    await flushPromises()

    expect(monitorApi.announcements.value).toHaveLength(1)
    expect(monitorApi.pagination.total).toBe(1)

    monitorApi.searchForm.stock_code = '000001'
    void monitorApi.fetchAnnouncements()
    await Promise.resolve()

    expect(monitorApi.loading.announcements).toBe(true)
    expect(monitorApi.announcements.value).toEqual([])
    expect(monitorApi.pagination.total).toBe(0)
  })
})
