import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { UnifiedResponse } from '@/api/types/common'
import { useStrategy } from '@/composables/useStrategy'
import type { StrategyConfig } from '@/api/types/common'

const strategyServiceMock = {
  getDataSource: vi.fn(() => 'real'),
  getStrategyList: vi.fn(),
  getStrategy: vi.fn(),
  createStrategy: vi.fn(),
  updateStrategy: vi.fn(),
  deleteStrategy: vi.fn(),
  startStrategy: vi.fn(),
  stopStrategy: vi.fn(),
  pauseStrategy: vi.fn(),
  resumeStrategy: vi.fn(),
  startBacktest: vi.fn(),
  getBacktestStatus: vi.fn()
}

vi.mock('@/api/services/strategyService', () => ({
  StrategyApiService: class StrategyApiServiceMock {
    getDataSource = strategyServiceMock.getDataSource
    getStrategyList = strategyServiceMock.getStrategyList
    getStrategy = strategyServiceMock.getStrategy
    createStrategy = strategyServiceMock.createStrategy
    updateStrategy = strategyServiceMock.updateStrategy
    deleteStrategy = strategyServiceMock.deleteStrategy
    startStrategy = strategyServiceMock.startStrategy
    stopStrategy = strategyServiceMock.stopStrategy
    pauseStrategy = strategyServiceMock.pauseStrategy
    resumeStrategy = strategyServiceMock.resumeStrategy
    startBacktest = strategyServiceMock.startBacktest
    getBacktestStatus = strategyServiceMock.getBacktestStatus
  }
}))

function createListResponse(data: unknown, success = true): UnifiedResponse<unknown> {
  return {
    success,
    code: success ? 200 : 500,
    message: success ? 'ok' : 'failed',
    data,
    request_id: 'req-123',
    process_time: '0.25s',
    timestamp: '2026-03-01T00:00:00Z'
  }
}

describe('useStrategy', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('keeps REAL source for successful empty strategy list', async () => {
    strategyServiceMock.getStrategyList.mockResolvedValue(createListResponse([]))

    const { fetchStrategies, strategies, dataSource, error, lastRequestId, lastProcessTimeMs } = useStrategy(false)
    await fetchStrategies()

    expect(strategies.value).toEqual([])
    expect(dataSource.value).toBe('real')
    expect(error.value).toBeNull()
    expect(lastRequestId.value).toBe('req-123')
    expect(lastProcessTimeMs.value).toBe('250.00')
  })

  it('keeps REAL source and surfaces error when API returns non-success response', async () => {
    strategyServiceMock.getStrategyList.mockResolvedValue(createListResponse(null, false))

    const { fetchStrategies, strategies, dataSource, error } = useStrategy(false)
    await fetchStrategies()

    expect(dataSource.value).toBe('real')
    expect(strategies.value).toEqual([])
    expect(error.value).toBe('failed')
  })

  it('maps REAL strategy payload into StrategyListItemVM rows', async () => {
    const realPayload: StrategyConfig[] = [
      {
        strategy_id: 9,
        strategy_name: 'Momentum 9',
        strategy_type: 'momentum',
        status: 'active',
        description: 'demo strategy',
        updated_at: '2026-03-01T10:00:00Z'
      }
    ]
    strategyServiceMock.getStrategyList.mockResolvedValue(createListResponse(realPayload))

    const { fetchStrategies, strategies, dataSource } = useStrategy(false)
    await fetchStrategies()

    expect(dataSource.value).toBe('real')
    expect(strategies.value).toHaveLength(1)
    expect(strategies.value[0]).toMatchObject({
      id: '9',
      name: 'Momentum 9',
      type: 'momentum',
      status: 'running'
    })
  })
})
