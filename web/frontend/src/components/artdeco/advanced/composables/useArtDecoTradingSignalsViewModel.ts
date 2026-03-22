import { computed, ref, toRef } from 'vue'
import { useSignalMonitoring } from '@/composables/artdeco/useSignalMonitoring'

type SignalType = 'buy' | 'sell'
type SignalResult = 'win' | 'loss' | 'pending'

interface TradingSignalItem {
  id: number
  symbol: string
  name: string
  type: SignalType
  strength: number
  reason: string
  price: string
  stopLoss: string
  target: string
  timestamp: string
}

interface SignalHistoryRow {
  id: number
  symbol: string
  type: SignalType
  strength: number
  result: SignalResult
  timestamp: string
}

export interface ArtDecoTradingSignalsProps {
  signals?: TradingSignalItem[]
}

const baseSignals: TradingSignalItem[] = [
  { id: 1, symbol: '600519', name: '贵州茅台', type: 'buy', strength: 82, reason: 'MACD 金叉 + 量能放大', price: '1850.20', stopLoss: '1798.00', target: '1935.00', timestamp: '2026-03-22 09:35:00' },
  { id: 2, symbol: '300750', name: '宁德时代', type: 'sell', strength: 76, reason: '跌破关键支撑位', price: '198.30', stopLoss: '205.00', target: '188.00', timestamp: '2026-03-22 10:12:00' },
]

export function useArtDecoTradingSignalsViewModel(props: ArtDecoTradingSignalsProps) {
  const signalFilter = ref('all')
  const autoRefresh = ref(false)
  const historyPeriod = ref('7d')
  const minSignalStrength = ref(70)
  const confirmationPeriod = ref('2')
  const stopLossRatio = ref(3)
  const targetProfitRatio = ref(8)
  const enabledSignalTypes = ref<Record<string, boolean>>({
    buy: true,
    sell: true,
  })

  const externalSignals = toRef(props, 'signals')
  const { signalHistory: historySource } = useSignalMonitoring()

  const normalizedSignals = computed<TradingSignalItem[]>(() => {
    return externalSignals.value?.length ? externalSignals.value : baseSignals
  })

  const filteredSignals = computed(() => {
    return normalizedSignals.value.filter((signal) => {
      if (!enabledSignalTypes.value[signal.type]) return false
      if (signal.strength < minSignalStrength.value) return false
      if (signalFilter.value !== 'all' && signal.type !== signalFilter.value) return false
      return true
    })
  })

  const signalHistory = computed<SignalHistoryRow[]>(() =>
    historySource.value.map((item) => ({
      id: item.id,
      symbol: item.symbol,
      type: item.type === 'sell' ? 'sell' : 'buy',
      strength: item.strength * 20,
      result: item.outcome === 'loss' ? 'loss' : item.outcome === 'win' ? 'win' : 'pending',
      timestamp: item.time,
    }))
  )

  const signalFilterOptions = [
    { label: '全部信号', value: 'all' },
    { label: '买入信号', value: 'buy' },
    { label: '卖出信号', value: 'sell' },
  ]

  const historyPeriodOptions = [
    { label: '近7日', value: '7d' },
    { label: '近30日', value: '30d' },
    { label: '近90日', value: '90d' },
  ]

  const confirmationPeriodOptions = [
    { label: '1 根K线', value: '1' },
    { label: '2 根K线', value: '2' },
    { label: '3 根K线', value: '3' },
  ]

  const availableSignalTypes = [
    { key: 'buy', label: '买入信号', description: '趋势向上且风险可控的做多机会' },
    { key: 'sell', label: '卖出信号', description: '趋势转弱或风控触发的离场信号' },
  ]

  const getBuySignalsCount = () => filteredSignals.value.filter((signal) => signal.type === 'buy').length
  const getSellSignalsCount = () => filteredSignals.value.filter((signal) => signal.type === 'sell').length
  const getSuccessRate = () => '72%'
  const getAvgHoldingPeriod = () => '4.5天'
  const getSignalClass = (signal: TradingSignalItem) => `signal-${signal.type}`
  const getSignalTypeText = (type: SignalType) => (type === 'buy' ? '买入' : '卖出')
  const getStrengthClass = (strength: number) => (strength >= 80 ? 'strong' : strength >= 65 ? 'medium' : 'weak')
  const getResultClass = (result: SignalResult) => result
  const getResultText = (result: SignalResult) => (result === 'win' ? '盈利' : result === 'loss' ? '亏损' : '待验证')
  const formatTime = (value: string) => value
  const handleSignalAction = (_signal: TradingSignalItem | SignalHistoryRow, _action: string) => undefined

  return {
    signalFilter,
    autoRefresh,
    historyPeriod,
    minSignalStrength,
    confirmationPeriod,
    stopLossRatio,
    targetProfitRatio,
    enabledSignalTypes,
    filteredSignals,
    signalHistory,
    signalFilterOptions,
    historyPeriodOptions,
    confirmationPeriodOptions,
    availableSignalTypes,
    getBuySignalsCount,
    getSellSignalsCount,
    getSuccessRate,
    getAvgHoldingPeriod,
    getSignalClass,
    getSignalTypeText,
    getStrengthClass,
    getResultClass,
    getResultText,
    formatTime,
    handleSignalAction,
  }
}
