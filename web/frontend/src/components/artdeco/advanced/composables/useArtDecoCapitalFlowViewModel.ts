import { computed, toRef, type Ref } from 'vue'
import { useArtDecoCapitalFlow } from './useArtDecoCapitalFlow'

export interface ArtDecoCapitalFlowProps {
  data?: Record<string, unknown>
  symbol?: string
  loading?: boolean
}

interface SectorFlowViewModel {
  name: string
  flow: number
}

interface ClusteredStockViewModel {
  code: string
  name: string
  volume: number
  flow: number
  cluster: number
}

interface ClusterViewModel {
  id: number
  stocks: unknown[]
  totalFlow: number
  avgFlow: number
  avgVolume: number
  representative: string
}

interface MainForceRankingViewModel {
  code: string
  rank: number
  name: string
  controlLevel: number
  mainPosition: number
}

interface HotSectorViewModel {
  name: string
  opportunityScore: number
  flow: number
  leadingStock: string
  duration: number
  opportunityReason: string
}

interface InvestmentInsightViewModel {
  id: string | number
  type: string
  title: string
  description: string
  recommendation?: string
  confidence?: string | number
}

function toSectorFlowViewModel(items: unknown[]): SectorFlowViewModel[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>
    return {
      name: typeof record.name === 'string' && record.name.trim() ? record.name : `板块${index + 1}`,
      flow: typeof record.flow === 'number' ? record.flow : 0,
    }
  })
}

function toClusteredStockViewModel(items: unknown[]): ClusteredStockViewModel[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>
    return {
      code: typeof record.code === 'string' ? record.code : `S${index + 1}`,
      name: typeof record.name === 'string' && record.name.trim() ? record.name : `股票${index + 1}`,
      volume: typeof record.volume === 'number' ? record.volume : 0,
      flow: typeof record.flow === 'number' ? record.flow : 0,
      cluster: typeof record.cluster === 'number' ? record.cluster : 0,
    }
  })
}

function toClusterViewModel(items: unknown[]): ClusterViewModel[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>
    return {
      id: typeof record.id === 'number' ? record.id : index + 1,
      stocks: Array.isArray(record.stocks) ? record.stocks : [],
      totalFlow: typeof record.totalFlow === 'number' ? record.totalFlow : 0,
      avgFlow: typeof record.avgFlow === 'number' ? record.avgFlow : 0,
      avgVolume: typeof record.avgVolume === 'number' ? record.avgVolume : 0,
      representative: typeof record.representative === 'string' ? record.representative : 'N/A',
    }
  })
}

function toMainForceRankingViewModel(items: unknown[]): MainForceRankingViewModel[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>
    return {
      code: typeof record.code === 'string' ? record.code : `S${index + 1}`,
      rank: typeof record.rank === 'number' ? record.rank : index + 1,
      name: typeof record.name === 'string' && record.name.trim() ? record.name : `股票${index + 1}`,
      controlLevel: typeof record.controlLevel === 'number' ? record.controlLevel : 0,
      mainPosition: typeof record.mainPosition === 'number' ? record.mainPosition : 0,
    }
  })
}

function toHotSectorViewModel(items: unknown[]): HotSectorViewModel[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>
    return {
      name: typeof record.name === 'string' && record.name.trim() ? record.name : `板块${index + 1}`,
      opportunityScore: typeof record.opportunityScore === 'number' ? record.opportunityScore : 0,
      flow: typeof record.flow === 'number' ? record.flow : 0,
      leadingStock: typeof record.leadingStock === 'string' ? record.leadingStock : 'N/A',
      duration: typeof record.duration === 'number' ? record.duration : 0,
      opportunityReason: typeof record.opportunityReason === 'string' ? record.opportunityReason : '暂无说明',
    }
  })
}

function toInvestmentInsightViewModel(items: unknown[]): InvestmentInsightViewModel[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>
    return {
      id: typeof record.id === 'string' || typeof record.id === 'number' ? record.id : index + 1,
      type: typeof record.type === 'string' ? record.type : 'neutral',
      title: typeof record.title === 'string' ? record.title : `洞察 ${index + 1}`,
      description: typeof record.description === 'string' ? record.description : '暂无说明',
      recommendation: typeof record.recommendation === 'string' ? record.recommendation : undefined,
      confidence: typeof record.confidence === 'string' || typeof record.confidence === 'number' ? record.confidence : undefined,
    }
  })
}

export function useArtDecoCapitalFlowViewModel(props: ArtDecoCapitalFlowProps) {
  const viewModel = useArtDecoCapitalFlow({
    data: toRef(props, 'data') as Ref<Record<string, unknown>>,
    symbol: toRef(props, 'symbol') as unknown as Ref<string>,
    loading: toRef(props, 'loading') as unknown as Ref<boolean>,
  })

  return {
    ...viewModel,
    typedSectorFlows: computed(() => toSectorFlowViewModel(viewModel.sectorFlows.value as unknown[])),
    typedClusteredStocks: computed(() => toClusteredStockViewModel(viewModel.clusteredStocks.value as unknown[])),
    typedClusters: computed(() => toClusterViewModel(viewModel.clusters.value as unknown[])),
    typedMainForceRanking: computed(() => toMainForceRankingViewModel(viewModel.mainForceRanking.value as unknown[])),
    typedHotSectors: computed(() => toHotSectorViewModel(viewModel.hotSectors.value as unknown[])),
    typedInvestmentInsights: computed(() => toInvestmentInsightViewModel(viewModel.investmentInsights.value as unknown[])),
  }
}
