export interface QuantMatrixMenuItem {
  path: string
  label: string
  businessKey: string
  children?: QuantMatrixMenuItem[]
  badge?: string | number
}

const MARKET_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/market',
  label: '市场行情',
  businessKey: 'qm.domain.market',
  children: [
    { path: '/qm/market/realtime', label: '实时行情流', businessKey: 'qm.market.realtime', badge: 'LIVE' },
    { path: '/qm/market/technical', label: 'K线分析', businessKey: 'qm.market.technical' },
    { path: '/qm/market/lhb', label: '龙虎榜分析', businessKey: 'qm.market.lhb' }
  ]
}

const DATA_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/data',
  label: '数据分析',
  businessKey: 'qm.domain.data',
  children: [
    { path: '/qm/data/industry', label: '板块动向', businessKey: 'qm.data.industry' },
    { path: '/qm/data/indicator', label: '指标分析', businessKey: 'qm.data.indicator' },
    { path: '/qm/data/concept', label: '概念动向', businessKey: 'qm.data.concept' },
    { path: '/qm/data/fund-flow', label: '资金流向', businessKey: 'qm.data.fundflow' }
  ]
}

const WATCHLIST_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/watchlist',
  label: '自选管理',
  businessKey: 'qm.domain.watchlist',
  children: [
    { path: '/qm/watchlist/manage', label: '组合管理', businessKey: 'qm.watchlist.manage' },
    { path: '/qm/watchlist/signals', label: '信号雷达', businessKey: 'qm.watchlist.signals' },
    { path: '/qm/watchlist/screener', label: '策略选股', businessKey: 'qm.watchlist.screener' }
  ]
}

const STRATEGY_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/strategy',
  label: '策略管理',
  businessKey: 'qm.domain.strategy',
  children: [
    { path: '/qm/strategy/repo', label: '策略仓库', businessKey: 'qm.strategy.repo' },
    { path: '/qm/strategy/parameters', label: '参数设置', businessKey: 'qm.strategy.parameters' },
    { path: '/qm/strategy/signals', label: '策略信号', businessKey: 'qm.strategy.signals' },
    { path: '/qm/strategy/backtest', label: '回测引擎', businessKey: 'qm.strategy.backtest' },
    { path: '/qm/strategy/gpu', label: '加速监控', businessKey: 'qm.strategy.gpu', badge: 'PRO' },
    { path: '/qm/strategy/opt', label: '参数优化', businessKey: 'qm.strategy.opt' },
    { path: '/qm/strategy/pos', label: '仓位管理', businessKey: 'qm.strategy.pos' }
  ]
}

const TRADE_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/trade',
  label: '交易管理',
  businessKey: 'qm.domain.trade',
  children: [
    { path: '/qm/trade/positions', label: '头寸管理', businessKey: 'qm.trade.positions' },
    { path: '/qm/trade/terminal', label: '交易操作', businessKey: 'qm.trade.terminal' },
    { path: '/qm/trade/signals', label: '信号监控', businessKey: 'qm.trade.signals' },
    { path: '/qm/trade/portfolio', label: '持仓透视', businessKey: 'qm.trade.portfolio' },
    { path: '/qm/trade/history', label: '历史对账', businessKey: 'qm.trade.history' }
  ]
}

const RISK_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/risk',
  label: '风险管理',
  businessKey: 'qm.domain.risk',
  children: [
    { path: '/qm/risk/management', label: '风险管理中心', businessKey: 'qm.risk.management' },
    { path: '/qm/risk/overview', label: '风险概览', businessKey: 'qm.risk.overview' },
    { path: '/qm/risk/pnl', label: '组合盈亏', businessKey: 'qm.risk.pnl' },
    { path: '/qm/risk/stop-loss', label: '止损雷达', businessKey: 'qm.risk.stoploss' },
    { path: '/qm/risk/alerts', label: '告警中心', businessKey: 'qm.risk.alerts', badge: 3 },
    { path: '/qm/risk/news', label: '舆情预警', businessKey: 'qm.risk.news' }
  ]
}

const SYSTEM_DOMAIN: QuantMatrixMenuItem = {
  path: '/qm/system',
  label: '系统设置',
  businessKey: 'qm.domain.system',
  children: [
    { path: '/qm/system/config', label: '系统配置', businessKey: 'qm.system.config' },
    { path: '/qm/system/health', label: '健康矩阵', businessKey: 'qm.system.health' },
    { path: '/qm/system/api', label: 'API 终端', businessKey: 'qm.system.api' },
    { path: '/qm/system/data', label: '数据源管理', businessKey: 'qm.system.datasource' }
  ]
}

export const QUANT_MATRIX_MENU_ITEMS: QuantMatrixMenuItem[] = [
  MARKET_DOMAIN,
  DATA_DOMAIN,
  WATCHLIST_DOMAIN,
  STRATEGY_DOMAIN,
  TRADE_DOMAIN,
  RISK_DOMAIN,
  SYSTEM_DOMAIN
]

export const QUANT_MATRIX_DEALING_ROOM: QuantMatrixMenuItem = {
  path: '/qm/dealing-room',
  label: '交易室',
  businessKey: 'qm.core.dealing_room'
}
