import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

type SignalType = 'buy' | 'sell'
type SignalResult = 'profit' | 'loss' | 'pending'

interface TradingSignal {
  id: string | number
  type: SignalType
  strength: number
  symbol: string
  name: string
  reason: string
  price: string
  stopLoss: string
  target: string
  timestamp: string
}

interface SignalHistoryItem {
  id: string | number
  symbol: string
  type: SignalType
  strength: number
  result: SignalResult
  timestamp: string
  holdingPeriod?: number
}

interface TradingSignalsData {
  signals?: Record<string, unknown>[]
  history?: Record<string, unknown>[]
}

const SIGNAL_FILTER_OPTIONS = [
  { label: '全部信号', value: 'all' },
  { label: '买入信号', value: 'buy' },
  { label: '卖出信号', value: 'sell' },
  { label: '强信号', value: 'strong' }
]

const HISTORY_PERIOD_OPTIONS = [
  { label: '1天', value: '1d' },
  { label: '3天', value: '3d' },
  { label: '1周', value: '1w' },
  { label: '1月', value: '1M' }
]

const CONFIRMATION_PERIOD_OPTIONS = [
  { label: '5分钟', value: '5m' },
  { label: '15分钟', value: '15m' },
  { label: '1小时', value: '1h' },
  { label: '4小时', value: '4h' }
]

const AVAILABLE_SIGNAL_TYPES = [
  { key: 'ma_cross', label: '均线交叉', description: '移动平均线金叉/死叉信号' },
  { key: 'macd_signal', label: 'MACD信号', description: 'MACD指标买卖信号' },
  { key: 'rsi_divergence', label: 'RSI背离', description: 'RSI指标与价格背离信号' },
  { key: 'bollinger_break', label: '布林带突破', description: '价格突破布林带上下轨' },
  { key: 'volume_surge', label: '成交量激增', description: '成交量异常放大信号' },
  { key: 'pattern_recognition', label: '形态识别', description: '经典技术形态识别' }
]

const DEFAULT_ENABLED_SIGNAL_TYPES: Record<string, boolean> = {
  ma_cross: true,
  macd_signal: true,
  rsi_divergence: true,
  bollinger_break: true,
  volume_surge: true,
  pattern_recognition: false
}

export interface ArtDecoTradingSignalsProps {
  data: TradingSignalsData
  symbol?: string
  loading?: boolean
}

export function useArtDecoTradingSignalsViewModel(props: Readonly<ArtDecoTradingSignalsProps>) {
  const signalFilter = ref('all')
  const autoRefresh = ref(true)
  const historyPeriod = ref('1d')
  const minSignalStrength = ref(70)
  const confirmationPeriod = ref('1h')
  const stopLossRatio = ref(3)
  const targetProfitRatio = ref(8)
  const enabledSignalTypes = ref({ ...DEFAULT_ENABLED_SIGNAL_TYPES })

  const tradingSignals = computed<TradingSignal[]>(() => {
    const signals = props.data?.signals || []
    return signals.map((signal, index) => {
      const item = signal as Record<string, unknown>
      const type: SignalType = item.type === 'sell' ? 'sell' : 'buy'

      return {
        id: (item.id as string | number | undefined) ?? index,
        type,
        strength: Number(item.strength || 0),
        symbol: String(item.symbol || ''),
        name: String(item.name || ''),
        reason: String(item.reason || ''),
        price: String(item.price || '--'),
        stopLoss: String(item.stopLoss || '--'),
        target: String(item.target || '--'),
        timestamp: String(item.timestamp || '')
      }
    })
  })

  const filteredSignals = computed<TradingSignal[]>(() => {
    if (signalFilter.value === 'all') return tradingSignals.value
    if (signalFilter.value === 'buy') return tradingSignals.value.filter(signal => signal.type === 'buy')
    if (signalFilter.value === 'sell') return tradingSignals.value.filter(signal => signal.type === 'sell')
    return tradingSignals.value.filter(signal => signal.strength >= 80)
  })

  const signalHistory = computed<SignalHistoryItem[]>(() => {
    const history = props.data?.history || []
    return history.map((record, index) => {
      const item = record as Record<string, unknown>
      const type: SignalType = item.type === 'sell' ? 'sell' : 'buy'
      const result: SignalResult = item.result === 'profit' || item.result === 'loss' ? item.result : 'pending'

      return {
        id: (item.id as string | number | undefined) ?? index,
        symbol: String(item.symbol || ''),
        type,
        strength: Number(item.strength || 0),
        result,
        timestamp: String(item.timestamp || ''),
        holdingPeriod:
          typeof item.holdingPeriod === 'number'
            ? item.holdingPeriod
            : item.holdingPeriod
              ? Number(item.holdingPeriod)
              : undefined
      }
    })
  })

  const getBuySignalsCount = (): string => tradingSignals.value.filter(signal => signal.type === 'buy').length.toString()

  const getSellSignalsCount = (): string => tradingSignals.value.filter(signal => signal.type === 'sell').length.toString()

  const getSuccessRate = (): string => {
    const history = signalHistory.value
    if (history.length === 0) return 'N/A'

    const successful = history.filter((item) => item.result === 'profit').length
    const total = history.filter((item) => item.result !== 'pending').length

    if (total === 0) return 'N/A'
    return `${((successful / total) * 100).toFixed(1)}%`
  }

  const getAvgHoldingPeriod = (): string => {
    const completedTrades = signalHistory.value.filter((item) => item.result !== 'pending' && item.holdingPeriod)
    if (completedTrades.length === 0) return 'N/A'

    const totalPeriod = completedTrades.reduce((sum, trade) => sum + (trade.holdingPeriod || 0), 0)
    const avgPeriod = totalPeriod / completedTrades.length

    if (avgPeriod < 60) return `${avgPeriod.toFixed(0)}分钟`
    if (avgPeriod < 1440) return `${(avgPeriod / 60).toFixed(1)}小时`
    return `${(avgPeriod / 1440).toFixed(1)}天`
  }

  const getSignalClass = (signal: TradingSignal): string =>
    `${signal.type} strength-${signal.strength >= 80 ? 'high' : signal.strength >= 60 ? 'medium' : 'low'}`

  const getSignalTypeText = (type: SignalType): string => (type === 'buy' ? '买入' : '卖出')

  const getStrengthClass = (strength: number): string => {
    if (strength >= 80) return 'high'
    if (strength >= 60) return 'medium'
    return 'low'
  }

  const getResultClass = (result: SignalResult): string => {
    if (result === 'profit') return 'profit'
    if (result === 'loss') return 'loss'
    return 'pending'
  }

  const getResultText = (result: SignalResult): string => {
    if (result === 'profit') return '盈利'
    if (result === 'loss') return '亏损'
    return '待定'
  }

  const formatTime = (timestamp: string): string =>
    new Date(timestamp).toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })

  const handleSignalAction = (_signal: TradingSignal, _action: string): void => {}

  let refreshTimer: ReturnType<typeof globalThis.setInterval> | null = null

  const startAutoRefresh = () => {
    if (autoRefresh.value && !refreshTimer) {
      refreshTimer = globalThis.setInterval(() => undefined, 5000)
    }
  }

  const stopAutoRefresh = () => {
    if (refreshTimer) {
      globalThis.clearInterval(refreshTimer)
      refreshTimer = null
    }
  }

  onMounted(() => {
    startAutoRefresh()
  })

  onUnmounted(() => {
    stopAutoRefresh()
  })

  watch(autoRefresh, (enabled) => {
    if (enabled) {
      startAutoRefresh()
      return
    }

    stopAutoRefresh()
  })

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
    signalFilterOptions: SIGNAL_FILTER_OPTIONS,
    historyPeriodOptions: HISTORY_PERIOD_OPTIONS,
    confirmationPeriodOptions: CONFIRMATION_PERIOD_OPTIONS,
    availableSignalTypes: AVAILABLE_SIGNAL_TYPES,
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
    handleSignalAction
  }
}
