import axios from 'axios'

import { createCSRFTokenResolver } from '../../api/csrfTokenResolver.ts'

type HeaderConfig = {
  headers?: Record<string, string>
}

type TradingDashboardTransport = {
  getCsrfToken: () => Promise<string>
  post: (url: string, data?: unknown, config?: HeaderConfig) => Promise<unknown>
  delete: (url: string, config?: HeaderConfig) => Promise<unknown>
}

const getCsrfToken = createCSRFTokenResolver(async () => {
  const response = await axios.get('/api/csrf-token', {
    withCredentials: true,
  })

  if (response.data?.data?.csrf_token) {
    return response.data.data.csrf_token as string
  }

  return ''
})

function buildHeaders(token: string): HeaderConfig {
  return token ? { headers: { 'X-CSRF-Token': token } } : {}
}

export function createTradingDashboardActions(transport: TradingDashboardTransport) {
  return {
    async startTradingSession() {
      const token = await transport.getCsrfToken()
      return transport.post('/api/trading/start', undefined, buildHeaders(token))
    },
    async stopTradingSession() {
      const token = await transport.getCsrfToken()
      return transport.post('/api/trading/stop', undefined, buildHeaders(token))
    },
    async addStrategy(strategyName: string) {
      const token = await transport.getCsrfToken()
      return transport.post('/api/trading/strategies/add', { strategy_name: strategyName }, buildHeaders(token))
    },
    async removeStrategy(strategyName: string) {
      const token = await transport.getCsrfToken()
      return transport.delete(`/api/trading/strategies/${strategyName}`, buildHeaders(token))
    },
  }
}

export const tradingDashboardActions = createTradingDashboardActions({
  getCsrfToken,
  post: (url, data, config) => axios.post(url, data, config),
  delete: (url, config) => axios.delete(url, config),
})
