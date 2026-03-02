/**
 * MyStocks ArtDeco v3.2 Elite - 核心菜单配置
 * 整合 7 大核心业务领域，作为系统导航的单一真实源 (SSOT)
 */

// ========== 业务域图标常量 ==========
export const ARTDECO_ICONS = {
  MARKET: 'Market',
  DATA: 'FundFlow',
  WATCHLIST: 'Bookmark',
  STRATEGY: 'StrategySelection',
  TRADE: 'StrategyTrading',
  RISK: 'RiskManagement',
  SYSTEM: 'Settings',
  // 功能图标
  REALTIME: 'Realtime',
  TECHNICAL: 'Technical',
  LHB: 'LongHuBang',
  CONCEPT: 'Concept',
  FLOW: 'FundFlow',
  SIGNALS: 'Signals',
  BACKTEST: 'Backtest',
  GPU: 'GPUBacktest',
  PORTFOLIO: 'Positions',
  ALERT: 'Alert',
  NEWS: 'Fundamental',
  HEALTH: 'APIHealth'
} as const

export interface MenuItem {
  path: string
  label: string
  icon: string
  businessKey: string
  children?: MenuItem[]
  badge?: string | number
  featured?: boolean
  // API 配置（可选）
  apiEndpoint?: string
  apiMethod?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  apiParams?: Record<string, unknown>
  // WebSocket 配置（可选）
  wsChannel?: string
  liveUpdate?: boolean
}

// ========== 业务域定义 (7 Domains) ==========

// 1. 市场行情 (Market)
const MARKET_DOMAIN: MenuItem = {
  path: '/market',
  label: '市场行情',
  icon: ARTDECO_ICONS.MARKET,
  businessKey: 'domain.market',
  featured: true,
  children: [
    { path: '/market/realtime', label: '实时行情流', icon: ARTDECO_ICONS.REALTIME, businessKey: 'market.realtime', badge: 'LIVE' },
    { path: '/market/technical', label: 'K线分析', icon: ARTDECO_ICONS.TECHNICAL, businessKey: 'market.technical' },
    { path: '/market/lhb', label: '龙虎榜分析', icon: ARTDECO_ICONS.LHB, businessKey: 'market.lhb' }
  ]
}

// 2. 数据分析 (Data Analysis)
const DATA_DOMAIN: MenuItem = {
  path: '/data',
  label: '数据分析',
  icon: ARTDECO_ICONS.DATA,
  businessKey: 'domain.data',
  children: [
    { path: '/data/industry', label: '板块动向', icon: ARTDECO_ICONS.CONCEPT, businessKey: 'data.industry' },
    { path: '/data/indicator', label: '指标分析', icon: 'Indicator', businessKey: 'data.indicator' },
    { path: '/data/concept', label: '概念动向', icon: ARTDECO_ICONS.CONCEPT, businessKey: 'data.concept' },
    { path: '/data/fund-flow', label: '资金流向', icon: ARTDECO_ICONS.FLOW, businessKey: 'data.fundflow' }
  ]
}

// 3. 自选股管理 (Watchlist)
const WATCHLIST_DOMAIN: MenuItem = {
  path: '/watchlist',
  label: '自选管理',
  icon: ARTDECO_ICONS.WATCHLIST,
  businessKey: 'domain.watchlist',
  children: [
    { path: '/watchlist/manage', label: '组合管理', icon: ARTDECO_ICONS.WATCHLIST, businessKey: 'watchlist.manage' },
    { path: '/watchlist/signals', label: '信号雷达', icon: ARTDECO_ICONS.SIGNALS, businessKey: 'watchlist.signals' },
    { path: '/watchlist/screener', label: '策略选股', icon: 'Screener', businessKey: 'watchlist.screener' }
  ]
}

// 4. 策略管理 (Strategy)
const STRATEGY_DOMAIN: MenuItem = {
  path: '/strategy',
  label: '策略管理',
  icon: ARTDECO_ICONS.STRATEGY,
  businessKey: 'domain.strategy',
  children: [
    { path: '/strategy/repo', label: '策略仓库', icon: ARTDECO_ICONS.STRATEGY, businessKey: 'strategy.repo' },
    { path: '/strategy/backtest', label: '回测引擎', icon: ARTDECO_ICONS.BACKTEST, businessKey: 'strategy.backtest' },
    { path: '/strategy/gpu', label: '加速监控', icon: ARTDECO_ICONS.GPU, businessKey: 'strategy.gpu', badge: 'PRO' },
    { path: '/strategy/opt', label: '参数优化', icon: 'Indicator', businessKey: 'strategy.opt' },
    { path: '/strategy/pos', label: '仓位管理', icon: ARTDECO_ICONS.PORTFOLIO, businessKey: 'strategy.pos' }
  ]
}

// 5. 交易管理 (Trade)
const TRADE_DOMAIN: MenuItem = {
  path: '/trade',
  label: '交易管理',
  icon: ARTDECO_ICONS.TRADE,
  businessKey: 'domain.trade',
  children: [
    { path: '/trade/positions', label: '头寸管理', icon: ARTDECO_ICONS.PORTFOLIO, businessKey: 'trade.pos' },
    { path: '/trade/terminal', label: '交易操作', icon: 'StrategyTrading', businessKey: 'trade.terminal' },
    { path: '/trade/signals', label: '信号监控', icon: ARTDECO_ICONS.SIGNALS, businessKey: 'trade.signals' },
    { path: '/trade/portfolio', label: '持仓透视', icon: ARTDECO_ICONS.PORTFOLIO, businessKey: 'trade.portfolio' },
    { path: '/trade/history', label: '历史对账', icon: 'TradeHistory', businessKey: 'trade.history' }
  ]
}

// 6. 风险管理 (Risk)
const RISK_DOMAIN: MenuItem = {
  path: '/risk',
  label: '风险管理',
  icon: ARTDECO_ICONS.RISK,
  businessKey: 'domain.risk',
  children: [
    { path: '/risk/management', label: '风险管理中心', icon: ARTDECO_ICONS.RISK, businessKey: 'risk.management' },
    { path: '/risk/overview', label: '风险概览', icon: ARTDECO_ICONS.RISK, businessKey: 'risk.overview' },
    { path: '/risk/pnl', label: '组合盈亏', icon: 'Indicator', businessKey: 'risk.pnl' },
    { path: '/risk/stop-loss', label: '止损雷达', icon: 'PositionRisk', businessKey: 'risk.stoploss' },
    { path: '/risk/alerts', label: '告警中心', icon: ARTDECO_ICONS.ALERT, businessKey: 'risk.alerts', badge: 3 },
    { path: '/risk/news', label: '舆情预警', icon: ARTDECO_ICONS.NEWS, businessKey: 'risk.news' }
  ]
}

// 7. 系统设置 (System)
const SYSTEM_DOMAIN: MenuItem = {
  path: '/system',
  label: '系统设置',
  icon: ARTDECO_ICONS.SYSTEM,
  businessKey: 'domain.system',
  children: [
    { path: '/system/config', label: '系统配置', icon: ARTDECO_ICONS.SYSTEM, businessKey: 'system.config' },
    { path: '/system/health', label: '健康矩阵', icon: ARTDECO_ICONS.HEALTH, businessKey: 'system.health' },
    { path: '/system/api', label: 'API 终端', icon: 'APIHealth', businessKey: 'system.api' },
    { path: '/system/data', label: '数据源管理', icon: 'DataUpdate', businessKey: 'system.datasource' }
  ]
}

// ========== 导出主菜单配置 ==========
// 注意：DEALING_ROOM 不在这里列出，因为它不在侧边栏显示
export const ARTDECO_MENU_ITEMS: MenuItem[] = [
  MARKET_DOMAIN,
  DATA_DOMAIN,
  WATCHLIST_DOMAIN,
  STRATEGY_DOMAIN,
  TRADE_DOMAIN,
  RISK_DOMAIN,
  SYSTEM_DOMAIN
]

// 兼容导出
export const ARTDECO_MENU_ENHANCED = ARTDECO_MENU_ITEMS

// 特殊路由定义 (非菜单项)
export const DEALING_ROOM_CONFIG: MenuItem = {
  path: '/dealing-room',
  label: '交易室',
  icon: 'Home',
  businessKey: 'core.dealing_room'
}

export const MENU_CONFIG_MAP = {
  ArtDecoDashboard: ARTDECO_MENU_ITEMS,
  ArtDecoEnhanced: ARTDECO_MENU_ITEMS
} as const
