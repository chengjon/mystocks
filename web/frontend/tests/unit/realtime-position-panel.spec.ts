import { beforeEach, describe, expect, it, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick, ref } from 'vue'
import RealtimePositionPanel from '@/components/realtime/RealtimePositionPanel.vue'

type PositionSnapshot = {
  position_id: string
  symbol: string
  quantity: number
  avg_price: number
  market_price: number
  market_value: number
  unrealized_profit: number
  profit_ratio: number
  price_change_percent: number
  name?: string
}

type PortfolioSnapshot = {
  portfolio_id: string
  total_market_value: number
  total_profit: number
  profit_ratio: number
  position_count: number
  last_update: string
  positions: Record<string, PositionSnapshot>
}

const connectionStatus = ref<'disconnected' | 'connecting' | 'connected' | 'error'>('disconnected')
const eventHandlers = new Map<string, Set<(payload: unknown) => void>>()
const connectWebSocket = vi.fn()
const disconnect = vi.fn()
const getPortfolioMTM = vi.fn<() => Promise<PortfolioSnapshot | null>>()
const on = vi.fn((event: string, handler: (payload: unknown) => void) => {
  if (!eventHandlers.has(event)) {
    eventHandlers.set(event, new Set())
  }
  eventHandlers.get(event)?.add(handler)
})
const off = vi.fn((event: string, handler: (payload: unknown) => void) => {
  eventHandlers.get(event)?.delete(handler)
})
const requestSnapshot = vi.fn()
const subscribe = vi.fn()
const unsubscribe = vi.fn()

vi.mock('@/services/realtimeMarket', () => ({
  useRealtimeMarket: () => ({
    connectionStatus,
    connectWebSocket,
    disconnect,
    getPortfolioMTM,
    on,
    off,
    requestSnapshot,
    subscribe,
    unsubscribe
  })
}))

const mountPanel = (props: Record<string, unknown> = {}) =>
  mount(RealtimePositionPanel, {
    props,
    global: {
      directives: {
        loading: () => {}
      },
      stubs: {
        'el-icon': true,
        'el-tag': true,
        'el-button': true,
        'el-table': true,
        'el-table-column': true
      }
    }
  })

const flushTasks = async () => {
  await Promise.resolve()
  await Promise.resolve()
  await nextTick()
}

const emitRealtimeEvent = async (event: string, payload: unknown = {}) => {
  eventHandlers.get(event)?.forEach((handler) => handler(payload))
  await flushTasks()
}

const createSnapshot = (positions: PositionSnapshot[]): PortfolioSnapshot => ({
  portfolio_id: 'default',
  total_market_value: 100000,
  total_profit: 1200,
  profit_ratio: 1.2,
  position_count: positions.length,
  last_update: '2026-03-15T09:30:00Z',
  positions: Object.fromEntries(positions.map((position) => [position.symbol, position]))
})

describe('RealtimePositionPanel', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    connectionStatus.value = 'disconnected'
    eventHandlers.clear()
  })

  it('subscribes current symbols when the websocket connects after an initial snapshot load', async () => {
    getPortfolioMTM.mockResolvedValue(
      createSnapshot([
        {
          position_id: 'p-1',
          symbol: '600519',
          quantity: 100,
          avg_price: 1800,
          market_price: 1850,
          market_value: 185000,
          unrealized_profit: 5000,
          profit_ratio: 2.7,
          price_change_percent: 1.1
        },
        {
          position_id: 'p-2',
          symbol: '000001',
          quantity: 200,
          avg_price: 12,
          market_price: 12.5,
          market_value: 2500,
          unrealized_profit: 100,
          profit_ratio: 4.2,
          price_change_percent: 0.8
        }
      ])
    )

    mountPanel({ autoConnect: false })
    await flushTasks()

    expect(subscribe).not.toHaveBeenCalled()

    connectionStatus.value = 'connected'
    await emitRealtimeEvent('connected')

    expect(requestSnapshot).toHaveBeenCalledTimes(1)
    expect(subscribe).toHaveBeenNthCalledWith(1, '600519')
    expect(subscribe).toHaveBeenNthCalledWith(2, '000001')
  })

  it('handles the backend connected snapshot without repeating handshake actions', async () => {
    getPortfolioMTM.mockResolvedValue(null)

    mountPanel({ autoConnect: false })
    await flushTasks()

    connectionStatus.value = 'connected'
    await emitRealtimeEvent('connected')

    expect(requestSnapshot).toHaveBeenCalledTimes(1)
    expect(subscribe).not.toHaveBeenCalled()

    await emitRealtimeEvent('connected', {
      action: 'connected',
      snapshot: createSnapshot([
        {
          position_id: 'p-9',
          symbol: '600519',
          quantity: 100,
          avg_price: 1800,
          market_price: 1850,
          market_value: 185000,
          unrealized_profit: 5000,
          profit_ratio: 2.7,
          price_change_percent: 1.1
        }
      ])
    })

    expect(requestSnapshot).toHaveBeenCalledTimes(1)
    expect(subscribe).toHaveBeenCalledTimes(1)
    expect(subscribe).toHaveBeenCalledWith('600519')
  })

  it('deduplicates subscriptions and unsubscribes removed symbols when the snapshot changes', async () => {
    getPortfolioMTM
      .mockResolvedValueOnce(
        createSnapshot([
          {
            position_id: 'p-1',
            symbol: '600519',
            quantity: 100,
            avg_price: 1800,
            market_price: 1850,
            market_value: 185000,
            unrealized_profit: 5000,
            profit_ratio: 2.7,
            price_change_percent: 1.1
          },
          {
            position_id: 'p-2',
            symbol: '000001',
            quantity: 200,
            avg_price: 12,
            market_price: 12.5,
            market_value: 2500,
            unrealized_profit: 100,
            profit_ratio: 4.2,
            price_change_percent: 0.8
          }
        ])
      )
      .mockResolvedValueOnce(
        createSnapshot([
          {
            position_id: 'p-1',
            symbol: '600519',
            quantity: 100,
            avg_price: 1800,
            market_price: 1860,
            market_value: 186000,
            unrealized_profit: 6000,
            profit_ratio: 3.1,
            price_change_percent: 1.4
          },
          {
            position_id: 'p-3',
            symbol: '600036',
            quantity: 150,
            avg_price: 38,
            market_price: 39,
            market_value: 5850,
            unrealized_profit: 150,
            profit_ratio: 2.5,
            price_change_percent: 0.9
          }
        ])
      )

    connectionStatus.value = 'connected'
    const wrapper = mountPanel({ autoConnect: false })
    await flushTasks()

    expect(subscribe).toHaveBeenNthCalledWith(1, '600519')
    expect(subscribe).toHaveBeenNthCalledWith(2, '000001')

    await (wrapper.vm as { refreshData: () => Promise<void> }).refreshData()
    await flushTasks()

    expect(unsubscribe).toHaveBeenCalledWith('000001')
    expect(subscribe).toHaveBeenNthCalledWith(3, '600036')
    expect(subscribe).toHaveBeenCalledTimes(3)
  })
})
