/**
 * 实时行情 API 服务
 * Real-time Market API Service
 *
 * 提供 WebSocket 连接和 REST API 调用功能
 *
 * Author: Claude Code
 * Date: 2026-01-09
 */

import { ref, computed } from 'vue'

const API_BASE = '/api'

interface Quote {
  symbol: string
  name: string
  price: number
  open: number
  high: number
  low: number
  close: number
  pre_close: number
  volume: number
  amount: number
  change: number
  change_percent: number
  bid_price?: number[]
  ask_price?: number[]
  bid_volume?: number[]
  ask_volume?: number[]
  timestamp: string
  source: string
}

interface PositionSnapshot {
  position_id: string
  symbol: string
  quantity: number
  avg_price: number
  market_price: number
  market_value: number
  unrealized_profit: number
  profit_ratio: number
  total_profit: number
  last_update: string
  price_change?: number
  price_change_percent?: number
  name?: string
}

interface PortfolioSnapshot {
  portfolio_id: string
  total_market_value: number
  total_cost: number
  total_unrealized_profit: number
  total_realized_profit: number
  total_profit: number
  profit_ratio: number
  cash_balance: number
  available_cash: number
  position_count: number
  last_update: string
  positions: Record<string, PositionSnapshot>
}

class RealtimeMarketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 3000
  private listeners: Map<string, Set<(data: any) => void>> = new Map()

  connectionStatus = ref<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
  lastPrice = ref<Record<string, number>>({})

  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  async getQuote(symbol: string): Promise<Quote | null> {
    try {
      const response = await fetch(`${API_BASE}/realtime/quote/${symbol}`)
      const data = await response.json()
      if (data.success && data.data) {
        return data.data
      }
      return null
    } catch (error) {
      console.error('Failed to get quote:', error)
      return null
    }
  }

  async getQuotes(symbols: string[]): Promise<Record<string, Quote>> {
    try {
      const response = await fetch(`${API_BASE}/realtime/quotes?symbols=${symbols.join(',')}`)
      const data = await response.json()
      if (data.success && data.data) {
        return data.data
      }
      return {}
    } catch (error) {
      console.error('Failed to get quotes:', error)
      return {}
    }
  }

  async getPortfolioMTM(portfolioId: string): Promise<PortfolioSnapshot | null> {
    try {
      const response = await fetch(`${API_BASE}/mtm/portfolio/${portfolioId}`)
      const data = await response.json()
      if (data.success && data.data) {
        return data.data
      }
      return null
    } catch (error) {
      console.error('Failed to get portfolio MTM:', error)
      return null
    }
  }

  async getPositionMTM(positionId: string): Promise<PositionSnapshot | null> {
    try {
      const response = await fetch(`${API_BASE}/mtm/position/${positionId}`)
      const data = await response.json()
      if (data.success && data.data) {
        return data.data
      }
      return null
    } catch (error) {
      console.error('Failed to get position MTM:', error)
      return null
    }
  }

  async getMTMStats(): Promise<any> {
    try {
      const response = await fetch(`${API_BASE}/mtm/stats`)
      return await response.json()
    } catch (error) {
      console.error('Failed to get MTM stats:', error)
      return null
    }
  }

  connectWebSocket(portfolioId: string = 'default'): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return
    }

    this.connectionStatus.value = 'connecting'

    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws://'}${window.location.host}${API_BASE}/ws/portfolio?portfolio_id=${portfolioId}`

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        this.connectionStatus.value = 'connected'
        this.reconnectAttempts = 0
        this.emit('connected', { status: 'connected' })
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e)
        }
      }

      this.ws.onclose = () => {
        this.connectionStatus.value = 'disconnected'
        this.emit('disconnected', { status: 'disconnected' })
        this.attemptReconnect(portfolioId)
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.connectionStatus.value = 'error'
      }
    } catch (error) {
      console.error('Failed to connect WebSocket:', error)
      this.connectionStatus.value = 'error'
    }
  }

  private attemptReconnect(portfolioId: string): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      setTimeout(() => {
        this.connectWebSocket(portfolioId)
      }, this.reconnectDelay)
    }
  }

  private handleMessage(data: any): void {
    switch (data.action) {
      case 'connected':
        this.emit('connected', data)
        break
      case 'portfolio_update':
        this.emit('portfolio_update', data)
        break
      case 'snapshot':
        this.emit('snapshot', data)
        break
      case 'position_registered':
        this.emit('position_registered', data)
        break
      case 'pong':
        this.emit('pong', data)
        break
      default:
        this.emit('message', data)
    }

    if (data.snapshot?.positions) {
      for (const [symbol, position] of Object.entries(data.snapshot.positions) as [string, PositionSnapshot][]) {
        if (position.market_price) {
          this.lastPrice.value[symbol] = position.market_price
        }
      }
    }
  }

  subscribe(symbol: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'subscribe',
        symbol
      }))
    }
  }

  unsubscribe(symbol: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'unsubscribe',
        symbol
      }))
    }
  }

  registerPosition(
    positionId: string,
    symbol: string,
    quantity: number,
    avgPrice: number
  ): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'register_position',
        position_id: positionId,
        symbol,
        quantity,
        avg_price: avgPrice
      }))
    }
  }

  updatePrice(symbol: string, price: number): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'update_price',
        symbol,
        price
      }))
    }
  }

  requestSnapshot(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'get_snapshot'
      }))
    }
  }

  ping(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        action: 'ping'
      }))
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
    this.connectionStatus.value = 'disconnected'
  }

  on(event: string, callback: (data: any) => void): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set())
    }
    this.listeners.get(event)!.add(callback)
  }

  off(event: string, callback: (data: any) => void): void {
    this.listeners.get(event)?.delete(callback)
  }

  private emit(event: string, data: any): void {
    this.listeners.get(event)?.forEach(callback => callback(data))
    this.listeners.get('*')?.forEach(callback => callback({ event, ...data }))
  }

  getLastPrice(symbol: string): number | undefined {
    return this.lastPrice.value[symbol]
  }

  getPriceChange(symbol: string): { change: number; percent: number } | undefined {
    const snapshot = this.lastSnapshot.value
    if (snapshot?.positions?.[symbol]) {
      const position = snapshot.positions[symbol]
      return {
        change: position.price_change || 0,
        percent: position.price_change_percent || 0
      }
    }
    return undefined
  }

  lastSnapshot = ref<PortfolioSnapshot | null>(null)

  setSnapshot(snapshot: PortfolioSnapshot): void {
    this.lastSnapshot.value = snapshot
  }
}

export const realtimeMarketService = new RealtimeMarketService()

export function useRealtimeMarket() {
  const service = realtimeMarketService

  return {
    service,
    connectionStatus: service.connectionStatus,
    lastSnapshot: service.lastSnapshot,
    lastPrice: service.lastPrice,
    isConnected: computed(() => service.isConnected),

    getQuote: (symbol: string) => service.getQuote(symbol),
    getQuotes: (symbols: string[]) => service.getQuotes(symbols),
    getPortfolioMTM: (portfolioId: string) => service.getPortfolioMTM(portfolioId),
    getPositionMTM: (positionId: string) => service.getPositionMTM(positionId),
    getMTMStats: () => service.getMTMStats(),

    connectWebSocket: (portfolioId?: string) => service.connectWebSocket(portfolioId),
    disconnect: () => service.disconnect(),

    subscribe: (symbol: string) => service.subscribe(symbol),
    unsubscribe: (symbol: string) => service.unsubscribe(symbol),
    registerPosition: (positionId: string, symbol: string, quantity: number, avgPrice: number) =>
      service.registerPosition(positionId, symbol, quantity, avgPrice),
    updatePrice: (symbol: string, price: number) => service.updatePrice(symbol, price),
    requestSnapshot: () => service.requestSnapshot(),
    ping: () => service.ping(),

    on: (event: string, callback: (data: any) => void) => service.on(event, callback),
    off: (event: string, callback: (data: any) => void) => service.off(event, callback),

    getLastPrice: (symbol: string) => service.getLastPrice(symbol),
    getPriceChange: (symbol: string) => service.getPriceChange(symbol)
  }
}

export type { Quote, PositionSnapshot, PortfolioSnapshot }
