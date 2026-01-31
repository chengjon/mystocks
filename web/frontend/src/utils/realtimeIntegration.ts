import { marketDataWebSocket, tradingWebSocket, riskWebSocket } from '@/utils/webSocketManager'
import { useTradingSignalsStore, useRiskAlertsStore } from '@/stores/apiStores'

// Initialize WebSocket connections for real-time data
export const initializeWebSocketConnections = () => {
  // Connect market data WebSocket
  marketDataWebSocket.connect().catch(error => {
    console.warn('Market data WebSocket connection failed:', error)
  })

  // Connect trading WebSocket
  tradingWebSocket.connect().catch(error => {
    console.warn('Trading WebSocket connection failed:', error)
  })

  // Connect risk WebSocket
  riskWebSocket.connect().catch(error => {
    console.warn('Risk WebSocket connection failed:', error)
  })
}

// Handle real-time data integration with stores
export const setupRealtimeDataIntegration = () => {
  const tradingSignalsStore = useTradingSignalsStore()
  const riskAlertsStore = useRiskAlertsStore()

  // Connect real-time stores to WebSocket
  tradingSignalsStore.connectWebSocket()
  riskAlertsStore.connectWebSocket()

  // Set up automatic reconnection on page visibility change
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState === 'visible') {
      // Reconnect WebSockets when page becomes visible
      initializeWebSocketConnections()
    }
  })
}

// Utility functions for WebSocket connection status
export const getWebSocketStatus = () => ({
  marketData: marketDataWebSocket.getState(),
  trading: tradingWebSocket.getState(),
  risk: riskWebSocket.getState()
})

export const isAnyWebSocketConnected = () =>
  marketDataWebSocket.isConnected() ||
  tradingWebSocket.isConnected() ||
  riskWebSocket.isConnected()

// Export WebSocket managers for direct access if needed
export {
  marketDataWebSocket,
  tradingWebSocket,
  riskWebSocket
}