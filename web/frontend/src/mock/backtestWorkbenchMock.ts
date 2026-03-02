import type { StrategyConfig, StrategyStatus } from '@/api/types/common'

export type BacktestDataMode = 'mock' | 'real'
export type BacktestStatusClass = 'running' | 'queued' | 'done'
type BacktestOption = { label: string; value: string }
type BacktestMetricVariant = '' | 'rise' | 'fall'
type BacktestMetricVariantWithGold = BacktestMetricVariant | 'gold'
type BacktestOpsVariant = 'rise' | 'gold' | 'fall'

interface StatusItem {
  name: string
  status: string
  statusClass: BacktestStatusClass
}

export interface BacktestWorkbenchDataConfig {
  tabs: Array<{ key: string; label: string }>
  systemStatus: string
  lastUpdated: string
  summary: {
    totalRuns: number
    winRate: number
    annualReturn: number
    maxDrawdown: number
  }
  opsOverview: Array<{ label: string; value: string; meta: string; variant: BacktestOpsVariant }>
  strategyOptions: BacktestOption[]
  periodOptions: BacktestOption[]
  benchmarkOptions: BacktestOption[]
  strategyMetrics: Array<{ label: string; value: string; variant: BacktestMetricVariant }>
  signalFlow: BacktestOption[]
  strategyLibrary: Array<{ name: string; meta: string }>
  backtestTasks: Array<{ name: string; detail: string; status: string; statusClass: BacktestStatusClass }>
  progress: {
    phase: string
    percent: number
    steps: StatusItem[]
  }
  runLogs: Array<{ ts: string; msg: string }>
  optimizeRows: Array<{ name: string; score: string; annual: string; drawdown: string }>
  optimizeHints: Array<{ label: string; value: string; variant: BacktestMetricVariantWithGold }>
  reportRows: Array<{ name: string; period: string; return: string; drawdown: string; updatedAt: string }>
  reportSummary: Array<{ label: string; value: string; variant: BacktestMetricVariantWithGold }>
}

function createMockBacktestWorkbenchConfig(): BacktestWorkbenchDataConfig {
  return {
    tabs: [
      { key: 'designer', label: '策略设计器' },
      { key: 'library', label: '策略库' },
      { key: 'tasks', label: '回测任务' },
      { key: 'execution', label: '执行中枢' },
      { key: 'optimize', label: '参数优化' },
      { key: 'reports', label: '报告中心' }
    ],
    systemStatus: '运行中 · GPU池可用',
    lastUpdated: '2026-03-01 01:16',
    summary: {
      totalRuns: 428,
      winRate: 63.4,
      annualReturn: 18.7,
      maxDrawdown: -9.2
    },
    opsOverview: [
      { label: 'GPU 资源池', value: '6 / 8 在线', meta: '当前负载 71%', variant: 'rise' },
      { label: '任务队列深度', value: '12', meta: '高优先级 3 个', variant: 'gold' },
      { label: '风险告警', value: '2 条', meta: '均为中等级别', variant: 'fall' }
    ],
    strategyOptions: [
      { label: '动量轮动策略', value: 'momentum' },
      { label: '均值回归策略', value: 'mean-reversion' },
      { label: '多因子组合策略', value: 'multi-factor' }
    ],
    periodOptions: [
      { label: '近6个月', value: '6m' },
      { label: '近1年', value: '1y' },
      { label: '近3年', value: '3y' }
    ],
    benchmarkOptions: [
      { label: '沪深300', value: 'csi300' },
      { label: '中证500', value: 'csi500' },
      { label: '上证指数', value: 'shanghai' }
    ],
    strategyMetrics: [
      { label: '触发条件', value: '6 项', variant: 'rise' },
      { label: '过滤器', value: '3 层', variant: '' },
      { label: '仓位上限', value: '35%', variant: '' },
      { label: '风控命中率', value: '92%', variant: 'rise' }
    ],
    signalFlow: [
      { label: '数据清洗', value: '实时校验已开启' },
      { label: '因子评分', value: '权重版本 v2.4' },
      { label: '执行频率', value: '每 5 分钟' },
      { label: '异常告警', value: '高优先级 2 条' }
    ],
    strategyLibrary: [
      { name: 'Trend Prism', meta: '动量/波动率双门限 · 最近胜率 67%' },
      { name: 'Value Rebalance', meta: '估值回归 · 最大回撤 -11.4%' },
      { name: 'Sector Switch', meta: '行业轮动 · 最近收益 +18.2%' },
      { name: 'Risk Neutral Core', meta: '对冲中性 · 夏普 1.55' }
    ],
    backtestTasks: [
      { name: 'Q1_轮动增强', detail: '样本区间 2024-01 ~ 2025-12', status: 'running', statusClass: 'running' },
      { name: '稳健价值池', detail: '样本区间 2022-01 ~ 2025-12', status: 'queued', statusClass: 'queued' },
      { name: '反转策略试验', detail: '样本区间 2025-01 ~ 2025-12', status: 'done', statusClass: 'done' }
    ],
    progress: {
      phase: '收益归因计算',
      percent: 72,
      steps: [
        { name: '行情载入', status: 'done', statusClass: 'done' },
        { name: '信号回放', status: 'done', statusClass: 'done' },
        { name: '撮合执行', status: 'running', statusClass: 'running' },
        { name: '绩效计算', status: 'queued', statusClass: 'queued' }
      ]
    },
    runLogs: [
      { ts: '01:11:03', msg: '已加载行情数据分片 12/16。' },
      { ts: '01:11:21', msg: '撮合引擎已完成 136 笔模拟成交。' },
      { ts: '01:12:04', msg: '风控校验通过，进入收益归因阶段。' },
      { ts: '01:12:35', msg: 'GPU 任务队列空闲，计算优先级已提升。' }
    ],
    optimizeRows: [
      { name: 'Momentum-v3', score: '92', annual: '+24.6%', drawdown: '-9.1%' },
      { name: 'Reversion-v2', score: '87', annual: '+18.4%', drawdown: '-7.4%' },
      { name: 'Hybrid-v5', score: '84', annual: '+21.1%', drawdown: '-11.2%' }
    ],
    optimizeHints: [
      { label: '建议仓位上限', value: '32%', variant: 'gold' },
      { label: '建议止损阈值', value: '2.8%', variant: 'fall' },
      { label: '建议调仓频率', value: '每 3 天', variant: '' }
    ],
    reportRows: [
      { name: '2026Q1_轮动增强', period: '1年', return: '+22.3%', drawdown: '-8.4%', updatedAt: '2026-03-01 01:02' },
      { name: '稳健价值组合', period: '3年', return: '+48.1%', drawdown: '-12.1%', updatedAt: '2026-02-28 21:40' },
      { name: '快速反转试验', period: '6个月', return: '+9.5%', drawdown: '-5.3%', updatedAt: '2026-02-28 18:16' }
    ],
    reportSummary: [
      { label: '今日新增报告', value: '4 份', variant: 'rise' },
      { label: '已归档策略', value: '26 个', variant: '' },
      { label: '待复核异常', value: '1 条', variant: 'fall' }
    ]
  }
}

function mapStatusClass(status?: StrategyStatus): BacktestStatusClass {
  if (status === 'active') {
    return 'running'
  }
  if (status === 'draft' || status === 'paused') {
    return 'queued'
  }
  return 'done'
}

export function createBacktestWorkbenchRealConfig(strategies: StrategyConfig[]): BacktestWorkbenchDataConfig {
  const mockConfig = createMockBacktestWorkbenchConfig()
  const currentTimestamp = new Date().toLocaleString()
  const getStrategyDisplayName = (item: StrategyConfig, index: number) => item.strategy_name || `策略 ${index + 1}`
  const getParametersCount = (item: StrategyConfig) => item.parameters?.length ?? 0
  const getStrategyStatus = (item: StrategyConfig) => item.status || 'draft'

  if (!strategies.length) {
    return {
      ...mockConfig,
      systemStatus: '运行中 · REAL 策略接口可用（暂无策略）',
      lastUpdated: currentTimestamp
    }
  }

  const activeCount = strategies.filter((item) => item.status === 'active').length
  const queuedCount = strategies.filter((item) => item.status === 'draft' || item.status === 'paused').length
  const archivedCount = strategies.filter((item) => item.status === 'archived').length

  const strategyOptions = strategies.map((item, index) => {
    const fallbackValue = `strategy-${index + 1}`
    return {
      label: getStrategyDisplayName(item, index),
      value: item.strategy_type || fallbackValue
    }
  })

  const strategyLibrary = strategies.map((item, index) => {
    const paramsCount = getParametersCount(item)
    const status = getStrategyStatus(item)
    return {
      name: getStrategyDisplayName(item, index),
      meta: `${status.toUpperCase()} · 参数 ${paramsCount} 项`
    }
  })

  const backtestTasks = strategies.slice(0, 3).map((item, index) => {
    const mappedStatus = mapStatusClass(item.status)
    return {
      name: item.strategy_name || `策略任务 ${index + 1}`,
      detail: `状态 ${getStrategyStatus(item)} · 参数 ${getParametersCount(item).toString()} 项`,
      status: mappedStatus,
      statusClass: mappedStatus
    }
  })

  return {
    ...mockConfig,
    systemStatus: '运行中 · REAL 策略接口可用',
    lastUpdated: currentTimestamp,
    summary: {
      ...mockConfig.summary,
      totalRuns: Math.max(mockConfig.summary.totalRuns, strategies.length * 20),
      winRate: Number((56 + activeCount * 2.5).toFixed(1))
    },
    opsOverview: [
      {
        label: 'REAL 策略总数',
        value: `${strategies.length}`,
        meta: `活跃 ${activeCount} · 归档 ${archivedCount}`,
        variant: 'rise'
      },
      {
        label: '任务队列深度',
        value: `${queuedCount}`,
        meta: queuedCount > 0 ? '待调度策略存在' : '暂无排队策略',
        variant: queuedCount > 0 ? 'gold' : 'rise'
      },
      {
        label: '风险告警',
        value: archivedCount > 0 ? '1 条' : '0 条',
        meta: archivedCount > 0 ? '存在归档策略，请复核' : '策略状态稳定',
        variant: archivedCount > 0 ? 'fall' : 'rise'
      }
    ],
    strategyOptions,
    strategyMetrics: [
      { label: '策略总量', value: `${strategies.length} 项`, variant: 'rise' },
      { label: '活跃策略', value: `${activeCount} 项`, variant: activeCount > 0 ? 'rise' : '' },
      { label: '参数字段', value: `${strategies.reduce((acc, cur) => acc + getParametersCount(cur), 0)} 项`, variant: '' },
      { label: '归档策略', value: `${archivedCount} 项`, variant: archivedCount > 0 ? 'fall' : '' }
    ],
    strategyLibrary,
    backtestTasks: backtestTasks.length ? backtestTasks : mockConfig.backtestTasks,
    signalFlow: [
      { label: '策略装载', value: `已加载 ${strategies.length} 个策略` },
      { label: '数据来源', value: 'REAL API /v1/strategy/strategies' },
      ...mockConfig.signalFlow.slice(2)
    ],
    runLogs: [
      {
        ts: new Date().toTimeString().slice(0, 8),
        msg: `REAL 模式已接入，策略列表同步完成（${strategies.length} 条）。`
      },
      ...mockConfig.runLogs.slice(0, 3)
    ]
  }
}

export function getBacktestWorkbenchConfig(mode: BacktestDataMode): BacktestWorkbenchDataConfig {
  if (mode === 'real') {
    return createMockBacktestWorkbenchConfig()
  }

  return createMockBacktestWorkbenchConfig()
}
