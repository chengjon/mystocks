import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const pushMock = vi.fn()
const refreshWorkbenchMock = vi.fn().mockResolvedValue(undefined)
const openAnnouncementMock = vi.fn()

const announcementsMock = ref([
  {
    stock_code: '600519',
    stock_name: '贵州茅台',
    announcement_type: '年度报告',
    announcement_title: '年度报告披露',
    publish_date: '2026-05-07',
    publish_time: '10:30:00',
    importance_level: 4,
    url: 'https://example.com/600519',
  },
  {
    stock_code: '000001',
    stock_name: '平安银行',
    announcement_type: '临时公告',
    announcement_title: '董事会决议',
    publish_date: '2026-01-01',
    publish_time: null,
    importance_level: 2,
    url: null,
  },
])

const summaryCardsMock = ref([
  { label: '公告总数', value: '2', variant: 'gold' },
  { label: '今日公告', value: '1', variant: 'rise' },
  { label: '重要公告', value: '1', variant: 'fall' },
  { label: '热点标的', value: '600519 / 000001', variant: 'gold' },
])

const loadingMock = ref(false)
const hasStartedSyncMock = ref(true)
const hasVerifiedSnapshotMock = ref(true)
const displayRequestIdMock = ref('req-risk-news-success')
const contentShellDescriptionMock = ref('保留风险域公告/舆情入口，同时复用 AI 情感工作台的统一数据编排。')
const pageStatusTextMock = ref('风险视角在线')
const pageStatusTypeMock = ref('success')
const runtimeMessageMock = ref('')

vi.mock('vue-router', () => ({
  useRouter: () => ({
    push: pushMock,
  }),
}))

vi.mock('@/views/ai/composables/useAiSentimentWorkbench', () => ({
  useAiSentimentWorkbench: () => ({
    announcements: announcementsMock,
    contentShellDescription: contentShellDescriptionMock,
    displayRequestId: displayRequestIdMock,
    formatPublishDate: (date?: string, time?: string | null) => (time ? `${date} ${time}` : date || '-'),
    hasStartedSync: hasStartedSyncMock,
    hasVerifiedSnapshot: hasVerifiedSnapshotMock,
    loading: loadingMock,
    pageStatusText: pageStatusTextMock,
    pageStatusType: pageStatusTypeMock,
    refreshWorkbench: refreshWorkbenchMock,
    runtimeMessage: runtimeMessageMock,
    summaryCards: summaryCardsMock,
    openAnnouncement: openAnnouncementMock,
  }),
}))

vi.mock('@/components/artdeco', async () => {
  const { default: ArtDecoStatCard } = await import('@/components/artdeco/base/ArtDecoStatCard.vue')

  return {
    ArtDecoButton: {
      props: ['loading'],
      emits: ['click'],
      template: '<button :data-loading="loading" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
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
    ArtDecoStatCard,
  }
})

import RiskNewsPage from '../News.vue'

function mountNewsPage() {
  return mount(RiskNewsPage as never, {
    global: {
      stubs: {
        ArtDecoCard: {
          props: ['title'],
          template: '<section><h2 v-if="title">{{ title }}</h2><slot /></section>',
        },
        'el-button': {
          props: ['disabled'],
          emits: ['click'],
          template: '<button :disabled="disabled" @click="$emit(\'click\')"><slot /></button>',
        },
        'el-table': {
          props: ['data'],
          template: '<div class="el-table-stub">{{ JSON.stringify(data) }}</div>',
        },
        'el-table-column': {
          template: '<div />',
        },
        'el-tag': {
          template: '<span><slot /></span>',
        },
      },
      directives: {
        loading: {},
      },
    },
  })
}

describe('RiskNews wrapper page', () => {
  beforeEach(() => {
    pushMock.mockReset()
    refreshWorkbenchMock.mockClear()
    openAnnouncementMock.mockReset()
    announcementsMock.value = announcementsMock.value.map((item, index) =>
      index === 0 ? { ...item, publish_date: new Date().toISOString().slice(0, 10) } : item
    )
    loadingMock.value = false
    hasStartedSyncMock.value = true
    hasVerifiedSnapshotMock.value = true
    displayRequestIdMock.value = 'req-risk-news-success'
    pageStatusTextMock.value = '风险视角在线'
    pageStatusTypeMock.value = 'success'
    runtimeMessageMock.value = ''
  })

  it('reuses the shared AI workbench while keeping risk wrapper copy and linked announcement counts', async () => {
    const wrapper = mountNewsPage()

    await flushPromises()

    expect(refreshWorkbenchMock).toHaveBeenCalledTimes(1)
    expect(wrapper.get('.hero-meta').text()).toContain('REQ_ID: req-risk-news-success')
    expect(wrapper.get('.hero-meta').text()).toContain('FOCUS: risk wrapper')
    expect(wrapper.text()).toContain('前往 AI 工作台')
    expect(wrapper.text()).toContain('年度报告披露')
    expect(wrapper.get('.content-shell-meta').text()).toContain('ANNOUNCEMENTS: 2')
    expect(wrapper.get('.content-shell-meta').text()).toContain('LINKED: 1')
    expect(wrapper.findAll('.stats-strip .artdeco-stat-value').map((node) => node.text())).toEqual(['2', '1', '1', '1'])
    expect(wrapper.text()).not.toContain('600519 / 000001')
  })

  it('routes users into the canonical ai sentiment page from the risk wrapper', async () => {
    const wrapper = mountNewsPage()

    await flushPromises()

    const aiEntryButton = wrapper
      .findAll('button')
      .find((button) => button.text().includes('前往 AI 工作台'))

    expect(aiEntryButton).toBeDefined()

    await aiEntryButton!.trigger('click')

    expect(pushMock).toHaveBeenCalledWith('/ai/sentiment')
  })
})
