import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useStrategy } from '../useStrategy'

const getStrategyListMock = vi.fn()
const getDataSourceMock = vi.fn(() => 'real')

vi.mock('@/api/services/strategyService', () => {
  class StrategyApiService {
    getDataSource = getDataSourceMock
    getStrategyList = getStrategyListMock
    getStrategy = vi.fn()
    createStrategy = vi.fn()
    updateStrategy = vi.fn()
    deleteStrategy = vi.fn()
    startStrategy = vi.fn()
    stopStrategy = vi.fn()
    pauseStrategy = vi.fn()
    resumeStrategy = vi.fn()
    startBacktest = vi.fn()
    getBacktestStatus = vi.fn()
  }

  return { StrategyApiService }
})

describe('useStrategy', () => {
  beforeEach(() => {
    getDataSourceMock.mockReturnValue('real')
    getStrategyListMock.mockReset()
  })

  it('keeps REAL source and surfaces error when API returns unsuccessful response', async () => {
    getStrategyListMock.mockResolvedValue({
      success: false,
      message: 'upstream unavailable',
      data: null,
      request_id: 'req-1',
      process_time: '20ms'
    })

    const strategy = useStrategy(false)
    await strategy.fetchStrategies()

    expect(strategy.dataSource.value).toBe('real')
    expect(strategy.strategies.value).toEqual([])
    expect(strategy.error.value).toContain('upstream unavailable')
  })

  it('keeps REAL source and surfaces error when API request throws', async () => {
    getStrategyListMock.mockRejectedValue(new Error('network down'))

    const strategy = useStrategy(false)
    await strategy.fetchStrategies()

    expect(strategy.dataSource.value).toBe('real')
    expect(strategy.strategies.value).toEqual([])
    expect(strategy.error.value).toContain('network down')
  })
})
