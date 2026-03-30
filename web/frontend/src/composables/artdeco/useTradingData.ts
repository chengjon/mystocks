import { ref } from 'vue'

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
    type: string
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
    type: string
    typeText: string
    price: number
    quantity: number
    amount: number
    fee: number
    status: string
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

export interface SignalFilter {
    key: string
    label: string
}

export interface PositionsData {
    totalStocks: number
    totalValue: number
    totalPnL: number
    winRate: number
    positions: Position[]
}

export function useTradingData() {
    const stats = ref<TradingStats>({
        todaySignals: 23,
        executedSignals: 15,
        pendingSignals: 8,
        accuracy: 72.5,
        todayTrades: 12,
        totalReturn: 15.8
    })

    const signalFilters: SignalFilter[] = [
        { key: 'all', label: '全部' },
        { key: 'buy', label: '买入' },
        { key: 'sell', label: '卖出' },
        { key: 'strong', label: '强势' },
        { key: 'reversal', label: '转折' }
    ]

    const activeSignalFilter = ref('all')

    const tradingSignals = ref<TradingSignal[]>([
        {
            id: 1,
            selected: false,
            time: '2024-01-15 09:45:30',
            symbol: '600519',
            symbolName: '贵州茅台',
            type: 'buy',
            typeText: '买入',
            strength: 5,
            price: 1850.0,
            reason: 'MA金叉+放量突破',
            confidence: 85
        },
        {
            id: 2,
            selected: false,
            time: '2024-01-15 10:15:22',
            symbol: '300750',
            symbolName: '宁德时代',
            type: 'buy',
            typeText: '买入',
            strength: 4,
            price: 245.5,
            reason: 'RSI超买+资金流入',
            confidence: 72
        },
        {
            id: 3,
            selected: false,
            time: '2024-01-15 11:30:15',
            symbol: '000001',
            symbolName: '平安银行',
            type: 'sell',
            typeText: '卖出',
            strength: 3,
            price: 12.35,
            reason: 'MACD死叉+压力位',
            confidence: 65
        }
    ])

    const historyStartDate = ref('')
    const historyEndDate = ref('')
    const historySymbol = ref('')
    const historyType = ref('')

    const symbolOptions = [
        { label: '贵州茅台 (600519)', value: '600519' },
        { label: '宁德时代 (300750)', value: '300750' },
        { label: '平安银行 (000001)', value: '000001' }
    ]

    const tradeTypeOptions = [
        { label: '全部', value: 'all' },
        { label: '买入', value: 'buy' },
        { label: '卖出', value: 'sell' }
    ]

    const tradeHistory = ref<TradeHistory[]>([
        {
            id: 1,
            time: '2024-01-15 09:45:30',
            symbol: '600519',
            symbolName: '贵州茅台',
            type: 'buy',
            typeText: '买入',
            price: 1850.0,
            quantity: 100,
            amount: 185000,
            fee: 27.75,
            status: 'completed',
            statusText: '已完成'
        },
        {
            id: 2,
            time: '2024-01-15 10:15:22',
            symbol: '300750',
            symbolName: '宁德时代',
            type: 'buy',
            typeText: '买入',
            price: 245.5,
            quantity: 500,
            amount: 122750,
            fee: 18.41,
            status: 'completed',
            statusText: '已完成'
        },
        {
            id: 3,
            time: '2024-01-15 14:30:45',
            symbol: '000001',
            symbolName: '平安银行',
            type: 'sell',
            typeText: '卖出',
            price: 12.35,
            quantity: 1000,
            amount: 12350,
            fee: 1.85,
            status: 'completed',
            statusText: '已完成'
        }
    ])

    const positionsData = ref<PositionsData>({
        totalStocks: 8,
        totalValue: 458000,
        totalPnL: 28500,
        winRate: 72.5,
        positions: [
            {
                symbol: '600519',
                name: '贵州茅台',
                shares: 200,
                avgCost: 1680.0,
                currentPrice: 1850.0,
                marketValue: 370000,
                pnl: 34000,
                pnlPercent: 10.1,
                positionPercent: 80
            },
            {
                symbol: '300750',
                name: '宁德时代',
                shares: 500,
                avgCost: 220.0,
                currentPrice: 245.5,
                marketValue: 122750,
                pnl: 12750,
                pnlPercent: 11.6,
                positionPercent: 20
            }
        ]
    })

    const activeTab = ref('signals')

    const mainTabs = [
        { key: 'signals', label: '交易信号', icon: '📊' },
        { key: 'history', label: '交易历史', icon: '📋' },
        { key: 'positions', label: '持仓分析', icon: '💼' },
        { key: 'attribution', label: '事后归因', icon: '🔍' },
        { key: 'signal-monitoring', label: '信号监控', icon: '📈' },
        { key: 'performance', label: '绩效评估', icon: '🎯' }
    ]

    const refreshData = () => {
    }

    const switchTab = (tabKey: string) => {
        activeTab.value = tabKey
    }

    const searchHistory = () => {
    }

    return {
        stats,
        signalFilters,
        activeSignalFilter,
        tradingSignals,
        historyStartDate,
        historyEndDate,
        historySymbol,
        historyType,
        symbolOptions,
        tradeTypeOptions,
        tradeHistory,
        positionsData,
        activeTab,
        mainTabs,
        refreshData,
        switchTab,
        searchHistory
    }
}
