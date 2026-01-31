/**
 * 侧边栏菜单配置
 * 
 * 为6个功能域提供统一的菜单配置
 * 每个菜单项包含：路径、标签、图标、徽章（可选）
 */

export interface MenuItem {
  path: string
  label: string
  icon: string
  badge?: string | number
  description?: string
  children?: MenuItem[]
  disabled?: boolean
  divider?: boolean
  apiEndpoint?: string
  apiMethod?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  liveUpdate?: boolean
  wsChannel?: string
  priority?: 'primary' | 'secondary' | 'tertiary'
  featured?: boolean
  lastUpdate?: number // Timestamp
  count?: number

  // Runtime status (dynamic)
  error?: string | null
  status?: 'idle' | 'loading' | 'success' | 'error'
}

// ========== Dashboard域菜单 ==========
export const DASHBOARD_MENU_ITEMS: MenuItem[] = [
  { 
    path: '/dashboard', 
    label: 'Overview', 
    icon: '📊',
    description: 'Dashboard overview and key metrics'
  },
  { 
    path: '/dashboard/watchlist', 
    label: 'Watchlist', 
    icon: '⭐',
    description: 'Your watched stocks'
  },
  { 
    path: '/dashboard/portfolio', 
    label: 'Portfolio', 
    icon: '💼',
    description: 'Portfolio overview and performance'
  },
  { 
    path: '/dashboard/activity', 
    label: 'Activity', 
    icon: '📈',
    description: 'Recent trading activity'
  }
]

// ========== Market Data域菜单 ==========
export const MARKET_MENU_ITEMS: MenuItem[] = [
  { 
    path: '/market/list', 
    label: 'Stock List', 
    icon: '📋',
    description: 'Browse all stocks'
  },
  { 
    path: '/market/realtime', 
    label: 'Realtime', 
    icon: '⚡',
    description: 'Real-time market monitoring',
    badge: 'LIVE'
  },
  { 
    path: '/market/kline', 
    label: 'K-Line', 
    icon: '📊',
    description: 'K-line chart analysis'
  },
  { 
    path: '/market/depth', 
    label: 'Depth', 
    icon: '📉',
    description: 'Order depth and flow'
  },
  { 
    path: '/market/sector', 
    label: 'Sector', 
    icon: '🏢',
    description: 'Sector performance analysis'
  }
]

// ========== Stock Analysis域菜单 ==========
export const ANALYSIS_MENU_ITEMS: MenuItem[] = [
  { 
    path: '/analysis/screener', 
    label: 'Stock Screener', 
    icon: '🔍',
    description: 'Screen stocks by criteria'
  },
  { 
    path: '/analysis/industry', 
    label: 'Industry', 
    icon: '🏢',
    description: 'Industry analysis'
  },
  { 
    path: '/analysis/concept', 
    label: 'Concept', 
    icon: '💡',
    description: 'Concept stock analysis'
  },
  { 
    path: '/analysis/fundamental', 
    label: 'Fundamental', 
    icon: '📑',
    description: 'Fundamental analysis'
  },
  { 
    path: '/analysis/technical', 
    label: 'Technical', 
    icon: '📊',
    description: 'Technical indicators'
  }
]

// ========== Risk Monitor域菜单 ==========
export const RISK_MENU_ITEMS: MenuItem[] = [
  { 
    path: '/risk/overview', 
    label: 'Overview', 
    icon: '📊',
    description: 'Risk dashboard'
  },
  { 
    path: '/risk/position', 
    label: 'Position Risk', 
    icon: '📉',
    description: 'Position-level risk analysis'
  },
  { 
    path: '/risk/portfolio', 
    label: 'Portfolio Risk', 
    icon: '💼',
    description: 'Portfolio risk metrics'
  },
  { 
    path: '/risk/alerts', 
    label: 'Alerts', 
    icon: '🔔',
    description: 'Risk alerts',
    badge: 3 // 示例徽章
  },
  { 
    path: '/risk/stress', 
    label: 'Stress Test', 
    icon: '🧪',
    description: 'Stress testing scenarios'
  }
]

// ========== Strategy Management域菜单 ==========
export const STRATEGY_MENU_ITEMS: MenuItem[] = [
  { 
    path: '/strategy/list', 
    label: 'My Strategies', 
    icon: '📚',
    description: 'Manage your trading strategies'
  },
  { 
    path: '/strategy/market', 
    label: 'Market', 
    icon: '📈',
    description: 'Market conditions'
  },
  { 
    path: '/strategy/backtest', 
    label: 'Backtest', 
    icon: '🔬',
    description: 'Backtest your strategies'
  },
  { 
    path: '/strategy/signals', 
    label: 'Signals', 
    icon: '📡',
    description: 'Trading signals',
    badge: 'NEW'
  },
  { 
    path: '/strategy/performance', 
    label: 'Performance', 
    icon: '📊',
    description: 'Strategy performance metrics'
  }
]

// ========== Monitoring Platform域菜单 ==========
export const MONITORING_MENU_ITEMS: MenuItem[] = [
  { 
    path: '/monitoring/dashboard', 
    label: 'Dashboard', 
    icon: '📊',
    description: 'Monitoring dashboard'
  },
  { 
    path: '/monitoring/data-quality', 
    label: 'Data Quality', 
    icon: '✅',
    description: 'Data quality metrics'
  },
  { 
    path: '/monitoring/performance', 
    label: 'Performance', 
    icon: '⚡',
    description: 'System performance'
  },
  { 
    path: '/monitoring/api', 
    label: 'API Health', 
    icon: '🔌',
    description: 'API endpoint status'
  },
  { 
    path: '/monitoring/logs', 
    label: 'Logs', 
    icon: '📝',
    description: 'System logs'
  }
]

// ========== ArtDeco 菜单配置 (新设计) ==========
export const ARTDECO_MENU_ITEMS: MenuItem[] = [
  {
    path: '/dashboard',
    label: '仪表盘',
    icon: '📊',
    description: '市场汇总信息',
    apiEndpoint: '/api/dashboard/overview',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'primary',
    featured: true
  },
  {
    path: '/trading/signals',
    label: '交易信号',
    icon: '📡',
    description: '实时交易信号监控',
    apiEndpoint: '/api/trading/signals',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'trading:signals',
    priority: 'primary',
    featured: true
  },
  {
    path: '/trading/history',
    label: '交易历史',
    icon: '📋',
    description: '历史交易记录',
    apiEndpoint: '/api/trading/history',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/trading/positions',
    label: '持仓监控',
    icon: '📊',
    description: '当前持仓统计',
    apiEndpoint: '/api/mtm/portfolio',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/trading/stats',
    label: '交易统计',
    icon: '📈',
    description: '交易数据分析',
    apiEndpoint: '/api/trading/statistics',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/strategy/management',
    label: '策略管理',
    icon: '⚙️',
    description: '策略配置、测试、管理',
    apiEndpoint: '/api/strategy-mgmt/strategies',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/strategy/optimization',
    label: '策略优化',
    icon: '🎯',
    description: '参数优化、性能评估',
    apiEndpoint: '/api/strategy/optimize',
    apiMethod: 'POST',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/strategy/backtest',
    label: '回测分析',
    icon: '🔬',
    description: '回测配置、结果分析',
    apiEndpoint: '/api/analysis/backtest',
    apiMethod: 'POST',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/market/realtime',
    label: '实时监控',
    icon: '⚡',
    description: '实时市场监控',
    apiEndpoint: '/api/market/v2/realtime-summary',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'market:realtime',
    priority: 'primary',
    featured: true
  },
  {
    path: '/market/analysis',
    label: '市场分析',
    icon: '📊',
    description: '市场数据分析',
    apiEndpoint: '/api/market/v2/analysis',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/market/overview',
    label: '市场概览',
    icon: '🌐',
    description: '市场总体概览',
    apiEndpoint: '/api/market/v2/overview',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/market/industry',
    label: '行业分析',
    icon: '🏢',
    description: '行业板块分析',
    apiEndpoint: '/api/market/sector',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/risk/alerts',
    label: '风险告警',
    icon: '🔔',
    description: '风险告警通知',
    apiEndpoint: '/api/v1/risk/alerts',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'risk:alerts',
    priority: 'secondary'
  },
  {
    path: '/risk/monitor',
    label: '风险监控',
    icon: '📊',
    description: '风险指标监控',
    apiEndpoint: '/api/monitoring/watchlists',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/risk/announcement',
    label: '公告监控',
    icon: '📰',
    description: '公司公告监控',
    apiEndpoint: '/api/announcements',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/stocks/management',
    label: '股票管理',
    icon: '📋',
    description: '自选股、关注列表、策略选股',
    apiEndpoint: '/api/user/stock-management-summary',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/analysis/data',
    label: '投资分析',
    icon: '🔍',
    description: '技术分析、基本面分析、指标分析',
    apiEndpoint: '/api/analysis/summary',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/system/monitoring',
    label: '监控面板',
    icon: '📊',
    description: '平台监控仪表板',
    apiEndpoint: '/api/monitoring/platform-status',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'system:status',
    priority: 'secondary'
  },
  {
    path: '/system/data',
    label: '数据管理',
    icon: '🗂️',
    description: '数据源配置和管理',
    apiEndpoint: '/api/data-sources/config',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  {
    path: '/system/settings',
    label: '系统设置',
    icon: '⚙️',
    description: '系统配置和设置',
    apiEndpoint: '/api/system/config',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  }
]

// ========== 菜单映射表 ==========
export const MENU_CONFIG_MAP = {
  MainLayout: DASHBOARD_MENU_ITEMS,
  MarketLayout: MARKET_MENU_ITEMS,
  DataLayout: ANALYSIS_MENU_ITEMS,
  RiskLayout: RISK_MENU_ITEMS,
  StrategyLayout: STRATEGY_MENU_ITEMS,
  MonitoringLayout: MONITORING_MENU_ITEMS,
  // 新增 ArtDeco 布局映射
  ArtDecoDashboard: ARTDECO_MENU_ITEMS
} as const

// ========== 类型导出 ==========
export type LayoutName = keyof typeof MENU_CONFIG_MAP
export type MenuConfigMap = typeof MENU_CONFIG_MAP
