import { describe, expect, it } from 'vitest'
import {
  OPTIMIZATION_WRITEBACK_POINTS,
  createOptimizationWritebackPayload
} from '@/views/artdeco-pages/strategy-tabs/strategyOptimizationWriteback'

describe('strategyOptimizationWriteback', () => {
  it('exposes stable write-back points to management/parameters/backtest', () => {
    expect(OPTIMIZATION_WRITEBACK_POINTS).toEqual([
      {
        target: 'management',
        label: '策略管理回写',
        description: '回写优化评分与最近优化时间'
      },
      {
        target: 'parameters',
        label: '参数页回写',
        description: '回写推荐参数并作为默认配置'
      },
      {
        target: 'backtest',
        label: '回测页回写',
        description: '带优化上下文进入回测执行'
      }
    ])
  })

  it('creates write-back payload from optimization candidate row', () => {
    const payload = createOptimizationWritebackPayload({
      strategyId: 's9',
      score: 88,
      recommendedParameters: {
        threshold: 1.8,
        hold_days: 5
      }
    })

    expect(payload).toMatchObject({
      strategyId: 's9',
      score: 88,
      recommendedParameters: {
        threshold: 1.8,
        hold_days: 5
      },
      writebackTargets: ['management', 'parameters', 'backtest']
    })
    expect(payload.updatedAt).toMatch(/T/)
  })
})
