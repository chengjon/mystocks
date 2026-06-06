import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  axiosGetMock,
  axiosPostMock,
  axiosDeleteMock,
  messageWarningMock,
  messageSuccessMock,
} = vi.hoisted(() => ({
  axiosGetMock: vi.fn(),
  axiosPostMock: vi.fn(),
  axiosDeleteMock: vi.fn(),
  messageWarningMock: vi.fn(),
  messageSuccessMock: vi.fn(),
}))

vi.mock('axios', () => ({
  default: {
    get: axiosGetMock,
    post: axiosPostMock,
    delete: axiosDeleteMock
  }
}))

vi.mock('element-plus', () => ({
  ElMessage: {
    success: messageSuccessMock,
    error: vi.fn(),
    warning: messageWarningMock,
    info: vi.fn()
  },
  ElMessageBox: {
    confirm: vi.fn()
  }
}))

vi.mock('vue', async () => {
  const actual = await vi.importActual<typeof import('vue')>('vue')
  return {
    ...actual,
    onMounted: vi.fn(),
    onUnmounted: vi.fn()
  }
})

import { useTradingDashboard } from '../useTradingDashboard'

describe('useTradingDashboard', () => {
  beforeEach(() => {
    axiosGetMock.mockReset()
    axiosPostMock.mockReset()
    axiosDeleteMock.mockReset()
    messageWarningMock.mockReset()
    messageSuccessMock.mockReset()
    vi.restoreAllMocks()
  })

  it('falls back to placeholder trading data and warns only once when endpoint is unavailable', async () => {
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {})

    axiosGetMock.mockRejectedValue({
      response: { status: 404 },
      message: 'Not Found'
    })

    const dashboard = useTradingDashboard()

    await dashboard.loadTradingData()

    expect(dashboard.tradingData.value).toMatchObject({
      session_id: 'fallback-offline',
      active_positions: 0,
      total_pnl: 0,
      daily_pnl: 0,
      current_drawdown: 0
    })
    expect(dashboard.statusMetrics.value[0].value).toBe('¥0.00')
    expect(messageWarningMock).toHaveBeenCalledTimes(1)
    expect(consoleErrorSpy).not.toHaveBeenCalled()

    await dashboard.loadTradingData()
    expect(messageWarningMock).toHaveBeenCalledTimes(1)
    expect(axiosGetMock).toHaveBeenCalledTimes(1)
  })

  it('degrades lightweight runtime demo payloads instead of presenting them as live trading truth', async () => {
    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/status') {
        return {
          data: {
            data: {
              session_id: null,
              is_running: false,
              current_drawdown: 0,
              daily_pnl: 0,
              total_pnl: 0,
              active_positions: 0,
              win_rate: 0,
            },
          },
        }
      }

      if (url === '/api/trading/strategies/performance') {
        return {
          data: {
            data: [
              {
                id: 'demo-momentum',
                name: 'Demo Momentum',
                pnl: 0,
                win_rate: 0,
              },
            ],
          },
        }
      }

      if (url === '/api/trading/market/snapshot') {
        return {
          data: {
            data: {
              timestamp: '2026-04-28T09:30:00Z',
              market_status: 'open',
              data: {
                '000001.SH': {
                  price: 12.5,
                  change: 0.08,
                  change_percent: 0.64,
                },
              },
            },
          },
        }
      }

      if (url === '/api/trading/risk/metrics') {
        return {
          data: {
            data: {
              risk_status: 'normal',
              current_drawdown: 0,
              daily_pnl: 0,
              active_positions: 0,
              last_updated: '2026-04-28T09:30:00Z',
            },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(dashboard.tradingStatus.value.text).toBe('待接入')
    expect(dashboard.runtimeStatus.value).toContain('轻量运行时占位数据')
    expect(dashboard.statusMetrics.value.map((metric) => metric.value)).toEqual([
      '待接入',
      '待接入',
      '待接入',
      '待接入',
    ])
    expect(dashboard.riskRecommendations.value).toEqual([
      '当前仅展示轻量运行时占位数据，实盘风控建议待接入。',
    ])
    expect(dashboard.loadIssues.value).toEqual([])
  })

  it('retains the last verified risk snapshot when a later risk refresh fails', async () => {
    let riskRequestCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/status') {
        return {
          data: {
            data: {
              session_id: 'mock-session-running',
              is_running: true,
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              total_pnl: 12890.4,
              active_positions: 2,
              win_rate: 0.67,
            },
          },
        }
      }

      if (url === '/api/trading/strategies/performance') {
        return {
          data: {
            data: [
              {
                id: 'strategy-1',
                strategy_name: 'Momentum Alpha',
                status: 'active',
                performance_metrics: {
                  expected_return: 0.12,
                  sharpe_ratio: 1.48,
                  win_rate: 0.67,
                },
              },
            ],
          },
        }
      }

      if (url === '/api/trading/market/snapshot') {
        return {
          data: {
            data: {
              timestamp: '2026-05-04T09:30:00Z',
              data: {
                SH000001: {
                  price: 3321.08,
                  change: 21.16,
                  change_percent: 0.64,
                },
              },
            },
          },
        }
      }

      if (url === '/api/trading/risk/metrics') {
        riskRequestCount += 1

        if (riskRequestCount === 1) {
          return {
            data: {
              data: {
                risk_status: 'warning',
                current_drawdown: 0.018,
                daily_pnl: 3450.5,
                active_positions: 2,
                last_updated: '2026-05-04T09:30:00Z',
              },
            },
          }
        }

        throw new Error('risk metrics unavailable')
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(dashboard.riskData.value).toMatchObject({
      risk_status: 'warning',
      current_drawdown: 0.018,
      daily_pnl: 3450.5,
      active_positions: 2,
      last_updated: '2026-05-04T09:30:00Z',
    })
    expect(dashboard.loadIssues.value).toEqual([])

    await dashboard.refreshData()

    expect(dashboard.riskData.value).toMatchObject({
      risk_status: 'warning',
      current_drawdown: 0.018,
      daily_pnl: 3450.5,
      active_positions: 2,
      last_updated: '2026-05-04T09:30:00Z',
    })
    expect(dashboard.loadIssues.value).toContain('风险指标')
    expect(dashboard.runtimeStatus.value).toContain('部分数据降级')
    expect(dashboard.displayRiskStatus.value.text).toBe('警告')
  })

  it('retains the last verified trading snapshot when a later status refresh fails', async () => {
    let tradingStatusRequestCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/status') {
        tradingStatusRequestCount += 1

        if (tradingStatusRequestCount === 1) {
          return {
            data: {
              data: {
                session_id: 'mock-session-running',
                is_running: true,
                current_drawdown: 0.018,
                daily_pnl: 3450.5,
                total_pnl: 12890.4,
                active_positions: 2,
                win_rate: 0.67,
              },
            },
          }
        }

        throw new Error('trading status unavailable')
      }

      if (url === '/api/trading/strategies/performance') {
        return {
          data: {
            data: [
              {
                id: 'strategy-1',
                strategy_name: 'Momentum Alpha',
                status: 'active',
                performance_metrics: {
                  expected_return: 0.12,
                  sharpe_ratio: 1.48,
                  win_rate: 0.67,
                },
              },
            ],
          },
        }
      }

      if (url === '/api/trading/market/snapshot') {
        return {
          data: {
            data: {
              timestamp: '2026-05-04T09:30:00Z',
              data: {
                SH000001: {
                  price: 3321.08,
                  change: 21.16,
                  change_percent: 0.64,
                },
              },
            },
          },
        }
      }

      if (url === '/api/trading/risk/metrics') {
        return {
          data: {
            data: {
              risk_status: 'warning',
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              active_positions: 2,
              last_updated: '2026-05-04T09:30:00Z',
            },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(dashboard.tradingData.value).toMatchObject({
      session_id: 'mock-session-running',
      is_running: true,
      current_drawdown: 0.018,
      daily_pnl: 3450.5,
      total_pnl: 12890.4,
      active_positions: 2,
      win_rate: 0.67,
    })
    expect(dashboard.statusMetrics.value.map((metric) => metric.value)).toEqual([
      '¥12,890.40',
      '2',
      '67.00%',
      '1.80%',
    ])

    await dashboard.refreshData()

    expect(dashboard.tradingData.value).toMatchObject({
      session_id: 'mock-session-running',
      is_running: true,
      current_drawdown: 0.018,
      daily_pnl: 3450.5,
      total_pnl: 12890.4,
      active_positions: 2,
      win_rate: 0.67,
    })
    expect(dashboard.statusMetrics.value.map((metric) => metric.value)).toEqual([
      '¥12,890.40',
      '2',
      '67.00%',
      '1.80%',
    ])
    expect(dashboard.loadIssues.value).toContain('交易状态')
    expect(dashboard.runtimeStatus.value).toContain('部分数据降级')
    expect(dashboard.tradingStatus.value.text).toBe('运行中')
  })

  it('retains the last verified market snapshot when a later market refresh fails', async () => {
    let marketRequestCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/status') {
        return {
          data: {
            data: {
              session_id: 'mock-session-running',
              is_running: true,
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              total_pnl: 12890.4,
              active_positions: 2,
              win_rate: 0.67,
            },
          },
        }
      }

      if (url === '/api/trading/strategies/performance') {
        return {
          data: {
            data: [
              {
                id: 'strategy-1',
                strategy_name: 'Momentum Alpha',
                status: 'active',
                performance_metrics: {
                  expected_return: 0.12,
                  sharpe_ratio: 1.48,
                  win_rate: 0.67,
                },
              },
            ],
          },
        }
      }

      if (url === '/api/trading/market/snapshot') {
        marketRequestCount += 1

        if (marketRequestCount === 1) {
          return {
            data: {
              data: {
                timestamp: '2026-05-04T09:30:00Z',
                data: {
                  SH000001: {
                    price: 3321.08,
                    change: 21.16,
                    change_percent: 0.64,
                  },
                  SZ399001: {
                    price: 10214.2,
                    change: 72.44,
                    change_percent: 0.71,
                  },
                },
              },
            },
          }
        }

        throw new Error('market snapshot unavailable')
      }

      if (url === '/api/trading/risk/metrics') {
        return {
          data: {
            data: {
              risk_status: 'warning',
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              active_positions: 2,
              last_updated: '2026-05-04T09:30:00Z',
            },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(dashboard.marketData.value).toMatchObject({
      timestamp: '2026-05-04T09:30:00Z',
      data: {
        SH000001: {
          price: 3321.08,
          change: 21.16,
          change_percent: 0.64,
        },
        SZ399001: {
          price: 10214.2,
          change: 72.44,
          change_percent: 0.71,
        },
      },
    })
    expect(dashboard.marketStatusLabel.value).toContain('2026')
    expect(dashboard.loadIssues.value).toEqual([])

    await dashboard.refreshData()

    expect(dashboard.marketData.value).toMatchObject({
      timestamp: '2026-05-04T09:30:00Z',
      data: {
        SH000001: {
          price: 3321.08,
          change: 21.16,
          change_percent: 0.64,
        },
        SZ399001: {
          price: 10214.2,
          change: 72.44,
          change_percent: 0.71,
        },
      },
    })
    expect(dashboard.marketStatusLabel.value).toContain('2026')
    expect(dashboard.loadIssues.value).toContain('市场快照')
    expect(dashboard.runtimeStatus.value).toContain('部分数据降级')
    expect(dashboard.marketNotice.value).toBe('')
  })

  it('retains the last verified strategy performance rows when a later strategy refresh fails', async () => {
    let strategyRequestCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/status') {
        return {
          data: {
            data: {
              session_id: 'mock-session-running',
              is_running: true,
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              total_pnl: 12890.4,
              active_positions: 2,
              win_rate: 0.67,
            },
          },
        }
      }

      if (url === '/api/trading/strategies/performance') {
        strategyRequestCount += 1

        if (strategyRequestCount === 1) {
          return {
            data: {
              data: [
                {
                  id: 'strategy-1',
                  strategy_name: 'Momentum Alpha',
                  status: 'active',
                  performance_metrics: {
                    expected_return: 0.12,
                    sharpe_ratio: 1.48,
                    win_rate: 0.67,
                  },
                },
                {
                  id: 'strategy-2',
                  strategy_name: 'Mean Reversion',
                  status: 'idle',
                  performance_metrics: {
                    expected_return: 0.04,
                    sharpe_ratio: 0.82,
                    win_rate: 0.51,
                  },
                },
              ],
            },
          }
        }

        throw new Error('strategy performance unavailable')
      }

      if (url === '/api/trading/market/snapshot') {
        return {
          data: {
            data: {
              timestamp: '2026-05-04T09:30:00Z',
              data: {
                SH000001: {
                  price: 3321.08,
                  change: 21.16,
                  change_percent: 0.64,
                },
              },
            },
          },
        }
      }

      if (url === '/api/trading/risk/metrics') {
        return {
          data: {
            data: {
              risk_status: 'warning',
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              active_positions: 2,
              last_updated: '2026-05-04T09:30:00Z',
            },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(dashboard.strategyPerformance.value).toHaveLength(2)
    expect(dashboard.strategyPerformance.value.map((strategy) => strategy.strategy_name)).toEqual([
      'Momentum Alpha',
      'Mean Reversion',
    ])
    expect(dashboard.loadIssues.value).toEqual([])

    await dashboard.refreshData()

    expect(dashboard.strategyPerformance.value).toHaveLength(2)
    expect(dashboard.strategyPerformance.value.map((strategy) => strategy.strategy_name)).toEqual([
      'Momentum Alpha',
      'Mean Reversion',
    ])
    expect(dashboard.loadIssues.value).toContain('策略绩效')
    expect(dashboard.runtimeStatus.value).toContain('部分数据降级')
  })

  it('does not announce a full refresh success toast when a later slice refresh degraded the route shell', async () => {
    let riskRequestCount = 0

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/status') {
        return {
          data: {
            data: {
              session_id: 'mock-session-running',
              is_running: true,
              current_drawdown: 0.018,
              daily_pnl: 3450.5,
              total_pnl: 12890.4,
              active_positions: 2,
              win_rate: 0.67,
            },
          },
        }
      }

      if (url === '/api/trading/strategies/performance') {
        return {
          data: {
            data: [
              {
                id: 'strategy-1',
                strategy_name: 'Momentum Alpha',
                status: 'active',
                performance_metrics: {
                  expected_return: 0.12,
                  sharpe_ratio: 1.48,
                  win_rate: 0.67,
                },
              },
            ],
          },
        }
      }

      if (url === '/api/trading/market/snapshot') {
        return {
          data: {
            data: {
              timestamp: '2026-05-04T09:30:00Z',
              data: {
                SH000001: {
                  price: 3321.08,
                  change: 21.16,
                  change_percent: 0.64,
                },
              },
            },
          },
        }
      }

      if (url === '/api/trading/risk/metrics') {
        riskRequestCount += 1

        if (riskRequestCount === 1) {
          return {
            data: {
              data: {
                risk_status: 'warning',
                current_drawdown: 0.018,
                daily_pnl: 3450.5,
                active_positions: 2,
                last_updated: '2026-05-04T09:30:00Z',
              },
            },
          }
        }

        throw new Error('risk metrics unavailable')
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(messageSuccessMock).toHaveBeenCalledWith('数据已刷新')
    messageSuccessMock.mockClear()
    messageWarningMock.mockClear()

    await dashboard.refreshData()

    expect(dashboard.loadIssues.value).toContain('风险指标')
    expect(dashboard.runtimeStatus.value).toContain('部分数据降级')
    expect(messageSuccessMock).not.toHaveBeenCalled()
    expect(messageWarningMock).toHaveBeenCalledWith('数据刷新完成，但部分模块降级：风险指标')
  })

  it('refreshes sibling runtime slices after starting the trading session', async () => {
    let tradingRunning = false

    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/csrf-token') {
        return {
          data: {
            data: {
              csrf_token: 'mock-csrf-token',
            },
          },
        }
      }

      if (url === '/api/trading/status') {
        return {
          data: {
            data: tradingRunning
              ? {
                  session_id: 'mock-session-running',
                  is_running: true,
                  current_drawdown: 0.018,
                  daily_pnl: 3450.5,
                  total_pnl: 12890.4,
                  active_positions: 2,
                  win_rate: 0.67,
                }
              : {
                  session_id: 'mock-session-idle',
                  is_running: false,
                  current_drawdown: 0,
                  daily_pnl: 0,
                  total_pnl: 0,
                  active_positions: 0,
                  win_rate: 0,
                },
          },
        }
      }

      if (url === '/api/trading/strategies/performance') {
        return {
          data: {
            data: [
              {
                id: 'strategy-1',
                strategy_name: 'Momentum Alpha',
                status: tradingRunning ? 'active' : 'idle',
                performance_metrics: {
                  expected_return: tradingRunning ? 0.12 : 0,
                  sharpe_ratio: tradingRunning ? 1.48 : 0,
                  win_rate: tradingRunning ? 0.67 : 0,
                },
              },
            ],
          },
        }
      }

      if (url === '/api/trading/market/snapshot') {
        return {
          data: {
            data: tradingRunning
              ? {
                  timestamp: '2026-05-04T09:30:00Z',
                  data: {
                    SH000001: {
                      price: 3321.08,
                      change: 21.16,
                      change_percent: 0.64,
                    },
                  },
                }
              : {
                  timestamp: '2026-05-04T09:00:00Z',
                  data: {},
                },
          },
        }
      }

      if (url === '/api/trading/risk/metrics') {
        return {
          data: {
            data: tradingRunning
              ? {
                  risk_status: 'warning',
                  current_drawdown: 0.018,
                  daily_pnl: 3450.5,
                  active_positions: 2,
                  last_updated: '2026-05-04T09:30:00Z',
                }
              : {
                  risk_status: 'normal',
                  current_drawdown: 0,
                  daily_pnl: 0,
                  active_positions: 0,
                  last_updated: '2026-05-04T09:00:00Z',
                },
          },
        }
      }

      throw new Error(`Unexpected url: ${url}`)
    })

    axiosPostMock.mockImplementation(async (url: string) => {
      if (url === '/api/trading/start') {
        tradingRunning = true
        return {
          data: {
            success: true,
          },
        }
      }

      throw new Error(`Unexpected POST ${url}`)
    })

    const dashboard = useTradingDashboard()

    await dashboard.refreshData()

    expect(dashboard.isRunning.value).toBe(false)
    expect(dashboard.riskData.value).toMatchObject({
      daily_pnl: 0,
      active_positions: 0,
    })
    expect(dashboard.strategyPerformance.value[0]?.status).toBe('idle')

    await dashboard.toggleTradingSession()

    expect(dashboard.isRunning.value).toBe(true)
    expect(dashboard.riskData.value).toMatchObject({
      daily_pnl: 3450.5,
      active_positions: 2,
      current_drawdown: 0.018,
    })
    expect(dashboard.strategyPerformance.value[0]?.status).toBe('active')
    expect(dashboard.marketData.value.timestamp).toBe('2026-05-04T09:30:00Z')
  })
})
