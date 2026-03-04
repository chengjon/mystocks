import { beforeEach, describe, expect, it, vi } from 'vitest'

const {
  axiosGetMock,
  axiosPostMock,
  axiosDeleteMock,
  messageWarningMock
} = vi.hoisted(() => ({
  axiosGetMock: vi.fn(),
  axiosPostMock: vi.fn(),
  axiosDeleteMock: vi.fn(),
  messageWarningMock: vi.fn()
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
    success: vi.fn(),
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
})
