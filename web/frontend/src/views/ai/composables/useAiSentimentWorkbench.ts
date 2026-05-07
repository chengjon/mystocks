import { computed, ref } from 'vue'

import { aiSentimentApi, type SentimentMarketOverviewResponse, type SentimentNewsItem, type SentimentStockTrendResponse } from '@/api/aiSentiment'
import { useArtDecoApi } from '@/composables/artdeco/useArtDecoApi'

export type AiSentimentWorkbenchVariant = 'ai' | 'risk'

interface SentimentSummaryCard {
  label: string
  value: string
  variant: 'gold' | 'rise' | 'fall'
}

function normalizeNewsRows(payload: unknown): SentimentNewsItem[] {
  if (Array.isArray(payload)) {
    return payload as SentimentNewsItem[]
  }
  if (!payload || typeof payload !== 'object') {
    return []
  }

  const dictionary = payload as Record<string, unknown>
  for (const key of ['announcements', 'items', 'records', 'data']) {
    const candidate = dictionary[key]
    if (Array.isArray(candidate)) {
      return candidate as SentimentNewsItem[]
    }
  }

  return []
}

export function useAiSentimentWorkbench(variant: AiSentimentWorkbenchVariant) {
  const { exec, loading, error, lastRequestId } = useArtDecoApi()

  const announcements = ref<SentimentNewsItem[]>([])
  const marketOverview = ref<SentimentMarketOverviewResponse | null>(null)
  const stockTrend = ref<SentimentStockTrendResponse | null>(null)
  const lastAnalysis = ref<{
    sentiment: string
    confidence: number
    positiveScore: number
    negativeScore: number
    neutralScore: number
    keyPhrases: string[]
    analyzedAt: string
    source: string | null
  } | null>(null)

  const selectedSymbol = ref('600519')
  const trendDays = ref(7)
  const analysisSource = ref('ai-workbench')
  const analysisText = ref('公司基本面改善，市场对后续增长和回报预期保持积极。')
  const staleError = ref<string | null>(null)
  const hasStartedSync = ref(false)
  const hasVerifiedSnapshot = ref(false)
  const lastVerifiedRequestId = ref('')

  const displayRequestId = computed(() => (hasVerifiedSnapshot.value ? (lastVerifiedRequestId.value || 'N/A') : 'N/A'))
  const totalAnnouncements = computed(() => announcements.value.length)
  const todayAnnouncements = computed(() => {
    const today = new Date().toISOString().slice(0, 10)
    return announcements.value.filter((item) => (item.publish_date || '').startsWith(today)).length
  })
  const importantAnnouncements = computed(
    () => announcements.value.filter((item) => Number(item.importance_level || 0) >= 4).length,
  )
  const linkedAnnouncements = computed(() => announcements.value.filter((item) => Boolean(item.url)).length)
  const hotSymbolsLabel = computed(() => {
    const symbols = marketOverview.value?.hot_symbols ?? []
    return symbols.length ? symbols.slice(0, 3).join(' / ') : '--'
  })

  const summaryCards = computed<SentimentSummaryCard[]>(() => {
    if (!hasVerifiedSnapshot.value) {
      return [
        { label: '公告总数', value: '--', variant: 'gold' },
        { label: '今日公告', value: '--', variant: 'gold' },
        { label: '重要公告', value: '--', variant: 'gold' },
        { label: '热点标的', value: '--', variant: 'gold' },
      ]
    }

    return [
      { label: '公告总数', value: `${totalAnnouncements.value}`, variant: 'gold' },
      { label: '今日公告', value: `${todayAnnouncements.value}`, variant: todayAnnouncements.value > 0 ? 'rise' : 'gold' },
      {
        label: '重要公告',
        value: `${importantAnnouncements.value}`,
        variant: importantAnnouncements.value > 0 ? 'fall' : 'gold',
      },
      { label: '热点标的', value: hotSymbolsLabel.value, variant: 'gold' },
    ]
  })

  const pageStatusText = computed(() => {
    if (staleError.value) return '刷新异常'
    if (error.value) return '同步异常'
    if (loading.value) return hasVerifiedSnapshot.value ? '刷新中' : '同步中'
    if (!hasVerifiedSnapshot.value) return '等待快照'
    return variant === 'risk' ? '风险视角在线' : 'AI 工作台在线'
  })

  const pageStatusType = computed(() => {
    if (staleError.value || error.value) return 'warning'
    if (!hasVerifiedSnapshot.value) return 'info'
    return marketOverview.value?.sentiment === 'negative' ? 'warning' : 'success'
  })

  const runtimeMessage = computed(() => {
    if (staleError.value) return `${staleError.value}，当前仍显示上次成功同步的工作台快照。`
    if (error.value) return `${error.value}，当前暂无已验证工作台快照。`
    if (loading.value) return hasVerifiedSnapshot.value ? '工作台数据刷新中...' : '工作台数据同步中...'
    if (!hasVerifiedSnapshot.value) return '当前暂无可展示的 AI 情感工作台数据。'
    return ''
  })

  const contentShellDescription = computed(() =>
    variant === 'risk'
      ? '保留风险域公告/舆情入口，同时复用 AI 情感工作台的统一数据编排。'
      : '把公告监控与文本情感、个股趋势、市场概览整合到同一 AI 主入口。',
  )

  const marketSentimentLabel = computed(() => marketOverview.value?.sentiment?.toUpperCase() || 'N/A')
  const marketAverageScore = computed(() => {
    const value = marketOverview.value?.average_sentiment
    return typeof value === 'number' ? value.toFixed(2) : '--'
  })
  const stockTrendLabel = computed(() => stockTrend.value?.trend?.toUpperCase() || 'N/A')
  const stockAverageScore = computed(() => {
    const value = stockTrend.value?.average_sentiment
    return typeof value === 'number' ? value.toFixed(2) : '--'
  })

  function markVerifiedRequest(): void {
    if (lastRequestId.value) {
      lastVerifiedRequestId.value = lastRequestId.value
    }
  }

  async function refreshWorkbench(): Promise<void> {
    hasStartedSync.value = true
    staleError.value = null

    const newsData = await exec(() => aiSentimentApi.getSentimentNews({ page: 1, page_size: 50 }), {
      errorMsg: '公告与舆情流同步失败',
      silent: true,
    })
    if (newsData === null) {
      if (hasVerifiedSnapshot.value) {
        staleError.value = error.value || '公告与舆情流同步失败'
      }
      return
    }
    announcements.value = normalizeNewsRows(newsData)
    markVerifiedRequest()

    const marketData = await exec(() => aiSentimentApi.getMarketSentiment(), {
      errorMsg: '市场情绪概览同步失败',
      silent: true,
    })
    if (marketData === null) {
      if (hasVerifiedSnapshot.value) {
        staleError.value = error.value || '市场情绪概览同步失败'
      }
      return
    }
    marketOverview.value = marketData
    markVerifiedRequest()

    const stockData = await exec(() => aiSentimentApi.getStockSentiment(selectedSymbol.value, trendDays.value), {
      errorMsg: '个股情绪趋势同步失败',
      silent: true,
    })
    if (stockData === null) {
      if (hasVerifiedSnapshot.value) {
        staleError.value = error.value || '个股情绪趋势同步失败'
      }
      return
    }
    stockTrend.value = stockData
    markVerifiedRequest()
    hasVerifiedSnapshot.value = true
  }

  async function runTextAnalysis(): Promise<void> {
    staleError.value = null

    const response = await exec(
      () =>
        aiSentimentApi.analyzeSentiment({
          symbol: selectedSymbol.value,
          source: analysisSource.value,
          text: analysisText.value,
        }),
      {
        errorMsg: '文本情感分析失败',
        silent: true,
      },
    )

    if (response === null) {
      if (hasVerifiedSnapshot.value) {
        staleError.value = error.value || '文本情感分析失败'
      }
      return
    }

    lastAnalysis.value = {
      sentiment: response.sentiment || 'neutral',
      confidence: Number(response.confidence || 0),
      positiveScore: Number(response.positive_score || 0),
      negativeScore: Number(response.negative_score || 0),
      neutralScore: Number(response.neutral_score || 0),
      keyPhrases: response.key_phrases || [],
      analyzedAt: response.analyzed_at || '',
      source: response.source || null,
    }
    markVerifiedRequest()

    const stockData = await exec(() => aiSentimentApi.getStockSentiment(selectedSymbol.value, trendDays.value), {
      errorMsg: '个股情绪趋势同步失败',
      silent: true,
    })

    if (stockData) {
      stockTrend.value = stockData
      hasVerifiedSnapshot.value = true
      markVerifiedRequest()
    }
  }

  function openAnnouncement(url?: string | null): void {
    if (!url) return
    window.open(url, '_blank', 'noopener,noreferrer')
  }

  function formatPublishDate(date?: string, time?: string | null): string {
    if (!date) return '-'
    return time ? `${date} ${time}` : date
  }

  return {
    analysisSource,
    analysisText,
    announcements,
    contentShellDescription,
    displayRequestId,
    formatPublishDate,
    hasStartedSync,
    hasVerifiedSnapshot,
    hotSymbolsLabel,
    importantAnnouncements,
    lastAnalysis,
    linkedAnnouncements,
    loading,
    marketAverageScore,
    marketOverview,
    marketSentimentLabel,
    openAnnouncement,
    pageStatusText,
    pageStatusType,
    refreshWorkbench,
    runTextAnalysis,
    runtimeMessage,
    selectedSymbol,
    staleError,
    stockAverageScore,
    stockTrend,
    stockTrendLabel,
    summaryCards,
    todayAnnouncements,
    totalAnnouncements,
    trendDays,
    variant,
  }
}
