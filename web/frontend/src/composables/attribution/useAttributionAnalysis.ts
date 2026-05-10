import { ref } from 'vue'

import {
  getBacktestAttribution,
  getPositionAttribution,
  type AttributionAnalysisResponse,
  type PositionAttributionQuery,
} from '@/api/portfolioAttribution.ts'

type AttributionLoadSource =
  | ({ source: 'trade' } & PositionAttributionQuery)
  | { source: 'backtest'; backtestId: number }

export function useAttributionAnalysis() {
  const data = ref<AttributionAnalysisResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const lastRequestId = ref('')

  async function loadAttribution(source: AttributionLoadSource): Promise<AttributionAnalysisResponse | null> {
    loading.value = true
    error.value = null

    try {
      const response = source.source === 'backtest'
        ? await getBacktestAttribution(source.backtestId)
        : await getPositionAttribution({ date: source.date, sessionId: source.sessionId })

      lastRequestId.value = response.request_id || lastRequestId.value
      if (response.success === false) {
        error.value = response.message || '归因分析加载失败'
        data.value = null
        return null
      }

      data.value = response.data ?? null
      return data.value
    } catch (requestError: unknown) {
      error.value = requestError instanceof Error ? requestError.message : '归因分析加载失败'
      data.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  function clearAttribution() {
    data.value = null
    error.value = null
    lastRequestId.value = ''
  }

  return {
    data,
    loading,
    error,
    lastRequestId,
    loadAttribution,
    clearAttribution,
  }
}
