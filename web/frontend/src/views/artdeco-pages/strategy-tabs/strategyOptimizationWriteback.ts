import type { StrategyOptimizationWritebackTarget } from '@/composables/strategy/useStrategyCrossTabContext'

export interface OptimizationWritebackPoint {
  target: StrategyOptimizationWritebackTarget
  label: string
  description: string
}

export interface OptimizationWritebackInput {
  strategyId: string
  score: number
  recommendedParameters: Record<string, unknown>
}

export interface OptimizationWritebackPayload extends OptimizationWritebackInput {
  writebackTargets: StrategyOptimizationWritebackTarget[]
  updatedAt: string
}

export const OPTIMIZATION_WRITEBACK_POINTS: OptimizationWritebackPoint[] = [
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
]

export function createOptimizationWritebackPayload(
  input: OptimizationWritebackInput
): OptimizationWritebackPayload {
  return {
    strategyId: input.strategyId,
    score: input.score,
    recommendedParameters: { ...input.recommendedParameters },
    writebackTargets: OPTIMIZATION_WRITEBACK_POINTS.map((item) => item.target),
    updatedAt: new Date().toISOString()
  }
}
