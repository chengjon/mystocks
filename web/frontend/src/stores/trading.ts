import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface TradeOrder {
  id: string
  symbol: string
  type: 'buy' | 'sell'
  quantity: number
  price: number
  status: 'pending' | 'filled' | 'cancelled'
  timestamp: Date
}

export const useTradingStore = defineStore('trading', () => {
  // State
  const orders = ref<TradeOrder[]>([])
  const currentSymbol = ref<string>('')
  const isTradingEnabled = ref(true)

  // Actions
  const addOrder = (order: Omit<TradeOrder, 'id' | 'timestamp'>) => {
    const newOrder: TradeOrder = {
      ...order,
      id: Date.now().toString(),
      timestamp: new Date()
    }
    orders.value.push(newOrder)
  }

  const cancelOrder = (orderId: string) => {
    const order = orders.value.find(o => o.id === orderId)
    if (order) {
      order.status = 'cancelled'
    }
  }

  const setCurrentSymbol = (symbol: string) => {
    currentSymbol.value = symbol
  }

  const clearOrders = () => {
    orders.value = []
  }

  // Added to satisfy ArtDecoTradingCenter usage
  const systemConfig = ref({
    refreshRate: 5000,
    notifications: true
  })

  const switchActiveFunction = (funcName: string) => {
    console.log('Switching to function:', funcName)
  }

  const refreshAllData = async () => {
    console.log('Refreshing all trading data...')
    return Promise.resolve()
  }

  return {
    // State
    orders,
    currentSymbol,
    isTradingEnabled,
    systemConfig,

    // Actions
    addOrder,
    cancelOrder,
    setCurrentSymbol,
    clearOrders,
    switchActiveFunction,
    refreshAllData
  }
})
