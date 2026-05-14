import { apiClient } from '@/api/apiClient.ts'

import type { UnifiedResponse } from '@/api/types/common.ts'
import type { SentimentRequest, SentimentResponse } from '@/api/types/analysis.ts'

export interface SentimentNewsItem {
  stock_code?: string
  stock_name?: string
  announcement_type?: string
  announcement_title?: string
  publish_date?: string
  publish_time?: string | null
  importance_level?: number | null
  url?: string | null
  sentiment?: string | null
}

export interface SentimentStockTrendPoint {
  date?: string
  sentiment?: string
  score?: number
  confidence?: number
}

export interface SentimentStockTrendResponse {
  symbol?: string
  days?: number
  mentions?: number
  average_sentiment?: number
  trend?: string
  latest_sentiment?: string
  latest_confidence?: number
  timeline?: SentimentStockTrendPoint[]
}

export interface SentimentMarketOverviewResponse {
  sentiment?: string
  average_sentiment?: number
  coverage?: number
  positive_ratio?: number
  negative_ratio?: number
  neutral_ratio?: number
  hot_symbols?: string[]
  updated_at?: string
}

export interface SentimentWorkbenchNewsResponse {
  announcements?: SentimentNewsItem[]
  items?: SentimentNewsItem[]
  records?: SentimentNewsItem[]
  data?: SentimentNewsItem[]
}

export function getSentimentNews(params: Record<string, unknown> = {}): Promise<UnifiedResponse<SentimentWorkbenchNewsResponse>> {
  return apiClient.get('/announcement/list', { params })
}

export function analyzeSentiment(payload: SentimentRequest): Promise<UnifiedResponse<SentimentResponse>> {
  return apiClient.post('/v1/sentiment/analyze', payload)
}

export function getStockSentiment(
  symbol: string,
  days: number,
): Promise<UnifiedResponse<SentimentStockTrendResponse>> {
  return apiClient.get(`/v1/sentiment/stock/${encodeURIComponent(symbol)}`, {
    params: { days },
  })
}

export function getMarketSentiment(): Promise<UnifiedResponse<SentimentMarketOverviewResponse>> {
  return apiClient.get('/v1/sentiment/market')
}

export const aiSentimentApi = {
  analyzeSentiment,
  getSentimentNews,
  getStockSentiment,
  getMarketSentiment,
}
