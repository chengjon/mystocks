import { computed, toRef } from 'vue'

import { useArtDecoCapitalFlow } from './useArtDecoCapitalFlow'

interface SectorFlowItem {
  name: string
  flow: number
}

interface ClusteredStockItem {
  code: string
  name: string
  volume: number
  flow: number
  cluster: number
}

interface ClusterItem {
  id: number
  stocks: { length: number }
  totalFlow: number
  avgFlow: number
  avgVolume: number
  representative: string
}

interface RankingItem {
  rank: number
  code: string
  name: string
  controlLevel: number
  mainPosition: number
}

interface HotSectorItem {
  name: string
  opportunityScore: number
  flow: number
  leadingStock: string
  duration: number
  opportunityReason: string
}

interface InsightItem {
  id: number
  type: string
  title: string
  description: string
}

export interface ArtDecoCapitalFlowProps {
  data: Record<string, unknown>
  symbol?: string
  loading?: boolean
}

export function useArtDecoCapitalFlowViewModel(props: Readonly<ArtDecoCapitalFlowProps>) {
  const capitalFlow = useArtDecoCapitalFlow({
    data: toRef(props, 'data'),
    symbol: computed(() => props.symbol || ''),
    loading: computed(() => props.loading || false)
  })

  const typedSectorFlows = computed((): SectorFlowItem[] => {
    return capitalFlow.sectorFlows.value.map((sector) => ({
      name: String((sector as Record<string, unknown>).name || ''),
      flow: Number((sector as Record<string, unknown>).flow || 0)
    }))
  })

  const typedClusteredStocks = computed((): ClusteredStockItem[] => {
    return capitalFlow.clusteredStocks.value.map((stock, index) => ({
      code: String((stock as Record<string, unknown>).code || `S${index + 1}`),
      name: String((stock as Record<string, unknown>).name || ''),
      volume: Number((stock as Record<string, unknown>).volume || 0),
      flow: Number((stock as Record<string, unknown>).flow || 0),
      cluster: Number((stock as Record<string, unknown>).cluster || 0)
    }))
  })

  const typedClusters = computed((): ClusterItem[] => {
    return capitalFlow.clusters.value.map((cluster, index) => ({
      id: Number((cluster as Record<string, unknown>).id || index),
      stocks: {
        length: Array.isArray((cluster as Record<string, unknown>).stocks)
          ? ((cluster as Record<string, unknown>).stocks as unknown[]).length
          : 0
      },
      totalFlow: Number((cluster as Record<string, unknown>).totalFlow || 0),
      avgFlow: Number((cluster as Record<string, unknown>).avgFlow || 0),
      avgVolume: Number((cluster as Record<string, unknown>).avgVolume || 0),
      representative: String((cluster as Record<string, unknown>).representative || '')
    }))
  })

  const typedMainForceRanking = computed((): RankingItem[] => {
    return capitalFlow.mainForceRanking.value as RankingItem[]
  })

  const typedHotSectors = computed((): HotSectorItem[] => {
    return capitalFlow.hotSectors.value as HotSectorItem[]
  })

  const typedInvestmentInsights = computed((): InsightItem[] => {
    return capitalFlow.investmentInsights.value as InsightItem[]
  })

  return {
    ...capitalFlow,
    typedSectorFlows,
    typedClusteredStocks,
    typedClusters,
    typedMainForceRanking,
    typedHotSectors,
    typedInvestmentInsights
  }
}
