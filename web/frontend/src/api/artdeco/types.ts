export interface TradingStats {
    todaySignals: number
    executedSignals: number
    pendingSignals: number
    accuracy: number
    todayTrades: number
    totalReturn: number
}

export interface TradingSignal {
    id: number
    selected?: boolean
    time: string
    symbol: string
    symbolName: string
    type: 'buy' | 'sell'
    typeText: string
    strength: number
    price: number
    reason: string
    confidence: number
}

export interface TradeHistory {
    id: number
    time: string
    symbol: string
    symbolName: string
    type: 'buy' | 'sell'
    typeText: string
    price: number
    quantity: number
    amount: number
    fee: number
    status: 'completed' | 'pending' | 'cancelled'
    statusText: string
}

export interface Position {
    symbol: string
    name: string
    shares: number
    avgCost: number
    currentPrice: number
    marketValue: number
    pnl: number
    pnlPercent: number
    positionPercent: number
}

export interface PositionsData {
    totalStocks: number
    totalValue: number
    totalPnL: number
    winRate: number
    positions: Position[]
}

export interface SignalMetrics {
    accuracy: number
    responseTime: number
    coverage: number
    qualityScore: number
}

export interface SignalQuality {
    wins: number
    losses: number
    avgProfit: number
    avgLoss: number
    profitLossRatio: string
    maxWinStreak: number
    maxLossStreak: number
}

export interface SignalType {
    name: string
    description: string
    count: number
    accuracy: number
}

export interface SignalHistoryItem {
    id: number
    time: string
    type: 'buy' | 'sell'
    typeText: string
    symbol: string
    strength: number
    outcome: 'win' | 'loss'
    outcomeText: string
    pnl?: number
}

export interface SignalFilter {
    key: string
    label: string
}

export interface SelectOption {
    label: string
    value: string
}
