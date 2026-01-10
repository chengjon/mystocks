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

// ========== 菜单映射表 ==========
export const MENU_CONFIG_MAP = {
  MainLayout: DASHBOARD_MENU_ITEMS,
  MarketLayout: MARKET_MENU_ITEMS,
  DataLayout: ANALYSIS_MENU_ITEMS,
  RiskLayout: RISK_MENU_ITEMS,
  StrategyLayout: STRATEGY_MENU_ITEMS,
  MonitoringLayout: MONITORING_MENU_ITEMS
} as const

// ========== 类型导出 ==========
export type LayoutName = keyof typeof MENU_CONFIG_MAP
export type MenuConfigMap = typeof MENU_CONFIG_MAP
