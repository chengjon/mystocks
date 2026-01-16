import type {
    TradingStats,
    TradingSignal,
    TradeHistory,
    Position,
    SignalMetrics,
    SignalQuality,
    SignalType
} from './types'

const API_BASE = '/api/v1'

export async function fetchTradingStats(): Promise<TradingStats> {
    const response = await fetch(`${API_BASE}/trading/stats`)
    if (!response.ok) {
        throw new Error('Failed to fetch trading stats')
    }
    return response.json()
}

export async function fetchTradingSignals(filters?: Record<string, string>): Promise<TradingSignal[]> {
    const params = new URLSearchParams(filters)
    const response = await fetch(`${API_BASE}/trading/signals?${params}`)
    if (!response.ok) {
        throw new Error('Failed to fetch trading signals')
    }
    return response.json()
}

export async function executeSignal(signalId: number, action: 'buy' | 'sell'): Promise<void> {
    const response = await fetch(`${API_BASE}/trading/signals/${signalId}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
    })
    if (!response.ok) {
        throw new Error('Failed to execute signal')
    }
}

export async function batchExecuteSignals(signalIds: number[]): Promise<void> {
    const response = await fetch(`${API_BASE}/trading/signals/batch-execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ signalIds })
    })
    if (!response.ok) {
        throw new Error('Failed to batch execute signals')
    }
}

export async function fetchTradeHistory(params: {
    startDate?: string
    endDate?: string
    symbol?: string
    type?: string
}): Promise<TradeHistory[]> {
    const searchParams = new URLSearchParams()
    if (params.startDate) searchParams.append('start_date', params.startDate)
    if (params.endDate) searchParams.append('end_date', params.endDate)
    if (params.symbol) searchParams.append('symbol', params.symbol)
    if (params.type) searchParams.append('type', params.type)

    const response = await fetch(`${API_BASE}/trading/history?${searchParams}`)
    if (!response.ok) {
        throw new Error('Failed to fetch trade history')
    }
    return response.json()
}

export async function fetchPositions(): Promise<Position[]> {
    const response = await fetch(`${API_BASE}/trading/positions`)
    if (!response.ok) {
        throw new Error('Failed to fetch positions')
    }
    return response.json()
}

export async function exportTradeHistory(format: 'csv' | 'excel' = 'csv'): Promise<Blob> {
    const response = await fetch(`${API_BASE}/trading/history/export?format=${format}`)
    if (!response.ok) {
        throw new Error('Failed to export trade history')
    }
    return response.blob()
}

export async function fetchSignalMetrics(): Promise<SignalMetrics> {
    const response = await fetch(`${API_BASE}/trading/signals/metrics`)
    if (!response.ok) {
        throw new Error('Failed to fetch signal metrics')
    }
    return response.json()
}

export async function fetchSignalQuality(): Promise<SignalQuality> {
    const response = await fetch(`${API_BASE}/trading/signals/quality`)
    if (!response.ok) {
        throw new Error('Failed to fetch signal quality')
    }
    return response.json()
}

export async function fetchSignalTypes(): Promise<SignalType[]> {
    const response = await fetch(`${API_BASE}/trading/signals/types`)
    if (!response.ok) {
        throw new Error('Failed to fetch signal types')
    }
    return response.json()
}

export async function fetchSignalHistory(limit?: number): Promise<unknown[]> {
    const params = limit ? `?limit=${limit}` : ''
    const response = await fetch(`${API_BASE}/trading/signals/history${params}`)
    if (!response.ok) {
        throw new Error('Failed to fetch signal history')
    }
    return response.json()
}
