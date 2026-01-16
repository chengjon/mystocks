import { ref } from 'vue'

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
    type: string
    typeText: string
    symbol: string
    strength: number
    outcome: string
    outcomeText: string
    pnl?: number
}

export function useSignalMonitoring() {
    const signalMetrics = ref<SignalMetrics>({
        accuracy: 72.5,
        responseTime: 45,
        coverage: 89.3,
        qualityScore: 8.2
    })

    const signalQuality = ref<SignalQuality>({
        wins: 145,
        losses: 55,
        avgProfit: 2850,
        avgLoss: 1650,
        profitLossRatio: '1.73',
        maxWinStreak: 12,
        maxLossStreak: 4
    })

    const signalTypes = ref<SignalType[]>([
        { name: '买入信号', description: '技术指标金叉', count: 89, accuracy: 74.2 },
        { name: '卖出信号', description: '技术指标死叉', count: 67, accuracy: 68.9 },
        { name: '强势信号', description: '多重指标共振', count: 34, accuracy: 82.1 },
        { name: '转折信号', description: '形态识别突破', count: 23, accuracy: 76.5 }
    ])

    const signalHistory = ref<SignalHistoryItem[]>([
        {
            id: 1,
            time: '2024-01-15 09:45:30',
            type: 'buy',
            typeText: '买入',
            symbol: '600519',
            strength: 5,
            outcome: 'win',
            outcomeText: '盈利',
            pnl: 2850
        },
        {
            id: 2,
            time: '2024-01-15 10:15:22',
            type: 'sell',
            typeText: '卖出',
            symbol: '300750',
            strength: 4,
            outcome: 'win',
            outcomeText: '盈利',
            pnl: 1650
        },
        {
            id: 3,
            time: '2024-01-15 14:25:30',
            type: 'buy',
            typeText: '买入',
            symbol: '000001',
            strength: 3,
            outcome: 'loss',
            outcomeText: '亏损',
            pnl: -1250
        }
    ])

    return {
        signalMetrics,
        signalQuality,
        signalTypes,
        signalHistory
    }
}
