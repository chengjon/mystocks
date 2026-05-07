import { flushPromises, mount } from '@vue/test-utils'
import { ref } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const refreshWorkbenchMock = vi.fn().mockResolvedValue(undefined)
const runTextAnalysisMock = vi.fn().mockResolvedValue(undefined)

const analysisSourceMock = ref('ai-workbench')
const analysisTextMock = ref('公司基本面改善，市场预期积极。')
const announcementsMock = ref([
  {
    stock_code: '600519',
    stock_name: '贵州茅台',
    announcement_type: '年度报告',
    announcement_title: '年度报告披露',
    publish_date: '2026-05-07',
    importance_level: 4,
    url: 'https://example.com/600519',
  },
])
const contentShellDescriptionMock = ref('把公告监控与文本情感、个股趋势、市场概览整合到同一 AI 主入口。')
const displayRequestIdMock = ref('req-ai-sentiment')
const loadingMock = ref(false)
const marketAverageScoreMock = ref('0.67')
const marketOverviewMock = ref({
  sentiment: 'positive',
  average_sentiment: 0.67,
  hot_symbols: ['600519', '000001'],
})
const marketSentimentLabelMock = ref('POSITIVE')
const pageStatusTextMock = ref('AI 工作台在线')
const pageStatusTypeMock = ref<'info' | 'success' | 'warning'>('success')
const runtimeMessageMock = ref('')
const selectedSymbolMock = ref('600519')
const stockAverageScoreMock = ref('0.61')
const stockTrendMock = ref({
  symbol: '600519',
  trend: 'positive',
  average_sentiment: 0.61,
  timeline: [],
})
const stockTrendLabelMock = ref('POSITIVE')
const summaryCardsMock = ref([
  { label: '公告总数', value: '1', variant: 'gold' as const },
  { label: '今日公告', value: '1', variant: 'rise' as const },
  { label: '重要公告', value: '1', variant: 'fall' as const },
  { label: '热点标的', value: '600519 / 000001', variant: 'gold' as const },
])
const lastAnalysisMock = ref({
  sentiment: 'positive',
  confidence: 0.91,
  positiveScore: 0.82,
  negativeScore: 0.05,
  neutralScore: 0.13,
  keyPhrases: ['增长', '回报'],
  analyzedAt: '2026-05-07T12:00:00Z',
  source: 'ai-workbench',
})

vi.mock('../composables/useAiSentimentWorkbench', () => ({
  useAiSentimentWorkbench: () => ({
    analysisSource: analysisSourceMock,
    analysisText: analysisTextMock,
    announcements: announcementsMock,
    contentShellDescription: contentShellDescriptionMock,
    displayRequestId: displayRequestIdMock,
    formatPublishDate: (date?: string, time?: string | null) => (time ? `${date} ${time}` : date || '-'),
    lastAnalysis: lastAnalysisMock,
    loading: loadingMock,
    marketAverageScore: marketAverageScoreMock,
    marketOverview: marketOverviewMock,
    marketSentimentLabel: marketSentimentLabelMock,
    openAnnouncement: vi.fn(),
    pageStatusText: pageStatusTextMock,
    pageStatusType: pageStatusTypeMock,
    refreshWorkbench: refreshWorkbenchMock,
    runTextAnalysis: runTextAnalysisMock,
    runtimeMessage: runtimeMessageMock,
    selectedSymbol: selectedSymbolMock,
    stockAverageScore: stockAverageScoreMock,
    stockTrend: stockTrendMock,
    stockTrendLabel: stockTrendLabelMock,
    summaryCards: summaryCardsMock,
  }),
}))

vi.mock('../components/AiSentimentHero.vue', () => ({
  default: {
    props: ['title', 'subtitle', 'requestId', 'statusText'],
    template: `
      <section class="hero-stub">
        <h1>{{ title }}</h1>
        <p>{{ subtitle }}</p>
        <span class="hero-request-id">{{ requestId }}</span>
        <span class="hero-status">{{ statusText }}</span>
        <slot name="actions" />
      </section>
    `,
  },
}))

vi.mock('../components/AiSentimentSummaryCards.vue', () => ({
  default: {
    props: ['cards'],
    template: '<section class="summary-cards-stub">{{ cards.map((card) => card.value).join(" | ") }}</section>',
  },
}))

vi.mock('../components/AiSentimentWorkbenchPanels.vue', () => ({
  default: {
    props: ['analysisText', 'analysisSource', 'selectedSymbol'],
    emits: ['analyze', 'refresh', 'update:analysisText', 'update:analysisSource', 'update:selectedSymbol'],
    template: `
      <section class="panels-stub">
        <span class="selected-symbol">{{ selectedSymbol }}</span>
        <span class="analysis-source">{{ analysisSource }}</span>
        <span class="analysis-text">{{ analysisText }}</span>
        <button class="emit-refresh" @click="$emit('refresh')">refresh</button>
        <button class="emit-analyze" @click="$emit('analyze')">analyze</button>
        <button class="emit-symbol" @click="$emit('update:selectedSymbol', '000001')">symbol</button>
        <button class="emit-source" @click="$emit('update:analysisSource', 'risk-wrapper')">source</button>
        <button class="emit-text" @click="$emit('update:analysisText', '市场情绪转弱')">text</button>
      </section>
    `,
  },
}))

vi.mock('@/components/artdeco', () => ({
  ArtDecoButton: {
    props: ['loading'],
    emits: ['click'],
    template: '<button :data-loading="loading" @click="$emit(\'click\')"><slot /><slot name="icon" /></button>',
  },
  ArtDecoIcon: {
    template: '<span />',
  },
}))

import SentimentPage from '../Sentiment.vue'

describe('AiSentiment canonical page', () => {
  beforeEach(() => {
    refreshWorkbenchMock.mockClear()
    runTextAnalysisMock.mockClear()
    analysisSourceMock.value = 'ai-workbench'
    analysisTextMock.value = '公司基本面改善，市场预期积极。'
    selectedSymbolMock.value = '600519'
  })

  it('refreshes the shared workbench on mount and renders canonical ai copy', async () => {
    const wrapper = mount(SentimentPage as never)

    await flushPromises()

    expect(refreshWorkbenchMock).toHaveBeenCalledTimes(1)
    expect(wrapper.get('h1').text()).toBe('情感分析工作台')
    expect(wrapper.get('.hero-request-id').text()).toBe('req-ai-sentiment')
    expect(wrapper.get('.summary-cards-stub').text()).toContain('600519 / 000001')
  })

  it('wires panel events back into the canonical workbench state and actions', async () => {
    const wrapper = mount(SentimentPage as never)

    await flushPromises()

    await wrapper.get('.emit-symbol').trigger('click')
    await wrapper.get('.emit-source').trigger('click')
    await wrapper.get('.emit-text').trigger('click')
    await wrapper.get('.emit-analyze').trigger('click')
    await wrapper.get('.emit-refresh').trigger('click')

    expect(selectedSymbolMock.value).toBe('000001')
    expect(analysisSourceMock.value).toBe('risk-wrapper')
    expect(analysisTextMock.value).toBe('市场情绪转弱')
    expect(runTextAnalysisMock).toHaveBeenCalledTimes(1)
    expect(refreshWorkbenchMock).toHaveBeenCalledTimes(2)
  })
})
