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
    description: '汇总信息、市场热度、资金流向、股票池表现',
    apiEndpoint: '/api/dashboard/overview',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'primary',
    featured: true
  },
  { 
    path: '/market/data', 
    label: '市场行情', 
    icon: '📊', 
    description: '实时行情、TDX接口、资金流向、ETF、概念、龙虎榜',
    apiEndpoint: '/api/market/realtime-summary',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'market:summary',
    priority: 'primary',
    featured: true
  },
  { 
    path: '/stocks/management', 
    label: '股票管理', 
    icon: '📋', 
    description: '自选股、关注列表、策略选股、行业选股',
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
    description: '技术分析、基本面分析、指标分析、筛选',
    apiEndpoint: '/api/analysis/summary',
    apiMethod: 'GET',
    liveUpdate: false,
    wsChannel: undefined,
    priority: 'secondary'
  },
  { 
    path: '/risk/management', 
    label: '风险管理', 
    icon: '⚠️', 
    description: '个股预警设置、风险指标管理、舆情管理、个股/监控列表的风险表现，因子分析等',
    apiEndpoint: '/api/risk/overview',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'risk:overview',
    priority: 'secondary'
  },
  { 
    path: '/strategy/trading', 
    label: '策略和交易管理', 
    icon: '💰', 
    description: '策略的设计、管理、测试，GPU加速回测，交易信号，交易历史记录，持仓分析，事后归因等',
    apiEndpoint: '/api/strategy/overview',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'strategy:overview',
    priority: 'secondary'
  },
  { 
    path: '/system/monitoring', 
    label: '系统监控', 
    icon: '⚙️', 
    description: '平台监控、系统设置、数据更新、数据质量监控',
    apiEndpoint: '/api/monitoring/platform-status',
    apiMethod: 'GET',
    liveUpdate: true,
    wsChannel: 'system:status',
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
