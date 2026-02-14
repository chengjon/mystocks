
/**
 * 回测摘要
 */
export interface BacktestSummary {
  /** 策略名称 */
  strategyName: string;

  /** 回测时间范围 */
  timeRange: BacktestTimeRange;

  /** 初始资金（元） */
  initialCapital: number;

  /** 最终资金（元） */
  finalCapital: number;

  /** 总收益（元） */
  totalProfit: number;

  /** 总收益率（%） */
  totalReturn: number;

  /** 年化收益率（%） */
  annualizedReturn: number;

  /** 最大回撤（%） */
  maxDrawdown: number;

  /** 夏普比率 */
  sharpeRatio: number;

  /** 胜率（%） */
  winRate: number;

  /** 总交易次数 */
  totalTrades: number;
}

/**
 * 策略评估结果
 */
export interface StrategyEvaluation {
  /** 评估ID */
  id: string;

  /** 策略ID */
  strategyId: string;

  /** 评估时间范围 */
  timeRange: BacktestTimeRange;

  /** 评估指标 */
  metrics: PerformanceMetrics;

  /** 评分（0-100） */
  score: number;

  /** 评级 */
  rating: 'A+' | 'A' | 'B' | 'C' | 'D' | 'E';

  /** 评估建议 */
  recommendations: string[];

  /** 评估时间 */
  evaluatedAt: string;
}

/**
 * 策略对比结果
 */
export interface StrategyComparison {
  /** 对比ID */
  id: string;

  /** 对比的策略ID列表 */
  strategyIds: string[];

  /** 对比指标 */
  metrics: PerformanceMetrics[];

  /** 排名 */
  ranking: {
    strategyId: string;
    rank: number;
    score: number;
  }[];

  /** 对比时间 */
  comparedAt: string;
}

/**
 * 策略优化参数
 */
export interface StrategyOptimization {
  /** 优化目标 */
  objective: 'sharpe_ratio' | 'total_return' | 'max_drawdown' | 'custom';

  /** 优化算法 */
  algorithm: 'grid_search' | 'random_search' | 'genetic' | 'bayesian';

  /** 参数空间 */
  paramSpace: Record<string, StrategyParamValue[]>;

  /** 迭代次数 */
  maxIterations: number;

  /** 并行数 */
  parallelJobs: number;
}

/**
 * 策略实时监控数据
 */
export interface StrategyMonitoring {
  /** 策略ID */
  strategyId: string;

  /** 当前持仓 */
  currentPositions: PositionRecord[];

  /** 今日盈亏（元） */
  todayProfitLoss: number;

  /** 今日收益率（%） */
  todayReturn: number;

  /** 当前状态 */
  status: StrategyStatus;

  /** 最后更新时间 */
  lastUpdate: string;

  /** 告警信息 */
  alerts: StrategyAlert[];
}

/**
 * 策略告警
 */
export interface StrategyAlert {
  /** 告警ID */
  id: string;

  /** 告警级别 */
  level: 'info' | 'warning' | 'error' | 'critical';

  /** 告警消息 */
  message: string;

  /** 告警时间 */
  timestamp: string;

  /** 是否已读 */
  read: boolean;
}

