/**
 * ArtDeco 菜单配置 - 增强版
 *
 * 特性：
 * - 6个主菜单，40个子菜单
 * - SVG图标系统（使用ArtDecoIcon组件）
 * - 完整的API端点映射（基于571个实际API）
 * - WebSocket实时数据支持
 * - ArtDeco设计令牌集成
 *
 * @version 2.0
 * @updated 2026-01-20
 */

import { ARTDECO_MENU_ITEMS } from './MenuConfig'

// ========== 图标常量 ==========
// 对应 ArtDecoIcon.vue 中的 50+ 个专业图标
export const ARTDECO_ICONS = {
  // 市场相关图标
  CHART: 'Chart',
  REALTIME: 'Bolt',
  TECHNICAL: 'Chart',
  FUND_FLOW: 'TrendingUp',
  ETF: 'Collection',
  CONCEPT: 'LightBulb',
  AUCTION: 'Gavel',
  LONGHU: 'Trophy',
  INSTITUTION: 'Building',
  WENCAI: 'Search',
  SCREENER: 'Filter',

  // 股票管理图标
  PORTFOLIO: 'PieChart',
  WATCHLIST: 'Star',
  ACTIVITY: 'Clock',
  STRATEGY_SELECTION: 'Sparkles',
  INDUSTRY_SELECTION: 'BuildingOffice',
  CONCEPT_SELECTION: 'LightBulb',

  // 分析图标
  ANALYSIS: 'MagnifyingGlass',
  TECHNICAL_ANALYSIS: 'Chart',
  FUNDAMENTAL: 'DocumentText',
  INDICATOR: 'Gauge',
  CUSTOM_INDICATOR: 'Adjustments',
  STOCK_ANALYSIS: 'ChartBar',
  LIST_ANALYSIS: 'TableCells',

  // 风险管理图标
  RISK: 'Shield',
  ALERT: 'Bell',
  RISK_INDICATORS: 'Gauge',
  SENTIMENT: 'Newspaper',
  POSITION_RISK: 'ExclamationTriangle',
  FACTOR_ANALYSIS: 'Beaker',

  // 策略交易图标
  STRATEGY: 'Target',
  STRATEGY_DESIGN: 'Pencil',
  STRATEGY_MANAGEMENT: 'FolderOpen',
  BACKTEST: 'Flask',
  GPU_BACKTEST: 'Chip',
  SIGNALS: 'Signal',
  TRADE_HISTORY: 'ArchiveBox',
  POSITIONS: 'Briefcase',
  ATTRIBUTION: 'ChartPie',

  // 系统图标
  MONITORING: 'DesktopComputer',
  SETTINGS: 'Cog',
  DATA_UPDATE: 'ArrowPath',
  DATA_QUALITY: 'CheckCircle',
  API_HEALTH: 'Server',
} as const

// ========== 菜单接口定义 ==========
export interface MenuItem {
  // 必填字段
  path: string
  label: string
  icon: string // SVG图标名称

  // 可选字段
  description?: string
  badge?: string | number
  children?: MenuItem[]
  disabled?: boolean
  divider?: boolean

  // API集成
  apiEndpoint?: string
  apiMethod?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  liveUpdate?: boolean
  wsChannel?: string
  apiParams?: Record<string, any>

  // 视觉配置
  iconColor?: string
  activeIconColor?: string
  priority?: 'primary' | 'secondary' | 'tertiary'
  featured?: boolean

  // 状态
  lastUpdate?: number
  count?: number

  // 运行时状态（动态添加）
  error?: string | null
  status?: 'idle' | 'loading' | 'success' | 'error'
}

// ========== 增强版菜单配置 ==========

/**
 * 1. 市场观察（10个子菜单）
 * 对应API: market.py, market_v2.py, realtime_market.py (120+ endpoints)
 */
export const MARKET_OBSERVATION_MENU_ENHANCED: MenuItem = {
  path: '/market',
  label: '市场观察',
  icon: ARTDECO_ICONS.CHART,
  description: '实时行情、技术指标、资金流向、ETF、概念、龙虎榜',
  apiEndpoint: '/api/v1/data/market/summary',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'market:summary',
  priority: 'primary',
  featured: true,
  children: [
    {
      path: '/market/realtime',
      label: '实时行情',
      icon: ARTDECO_ICONS.REALTIME,
      description: '实时市场数据监控',
      apiEndpoint: '/api/v1/data/market/realtime',
      apiMethod: 'GET',
      liveUpdate: true,
      wsChannel: 'market:realtime',
      badge: 'LIVE',
    },
    {
      path: '/market/technical',
      label: '技术指标',
      icon: ARTDECO_ICONS.TECHNICAL,
      description: 'K线、技术分析',
      apiEndpoint: '/api/indicators/technical',
      apiMethod: 'GET',
      apiParams: { indicator: 'MACD,RSI,KDJ' },
    },
    {
      path: '/market/fund-flow',
      label: '资金流向',
      icon: ARTDECO_ICONS.FUND_FLOW,
      description: '资金流向分析',
      apiEndpoint: '/api/v1/data/market/fund-flow',
      apiMethod: 'GET',
    },
    {
      path: '/market/etf',
      label: 'ETF行情',
      icon: ARTDECO_ICONS.ETF,
      description: 'ETF市场数据',
      apiEndpoint: '/api/v1/data/market/etf',
      apiMethod: 'GET',
    },
    {
      path: '/market/concept',
      label: '概念行情',
      icon: ARTDECO_ICONS.CONCEPT,
      description: '概念板块分析',
      apiEndpoint: '/api/v1/data/market/concept',
      apiMethod: 'GET',
    },
    {
      path: '/market/auction',
      label: '竞价抢筹',
      icon: ARTDECO_ICONS.AUCTION,
      description: '集合竞价分析',
      apiEndpoint: '/api/v1/data/market/auction',
      apiMethod: 'GET',
    },
    {
      path: '/market/longhubang',
      label: '龙虎榜',
      icon: ARTDECO_ICONS.LONGHU,
      description: '龙虎榜数据',
      apiEndpoint: '/api/v1/data/market/longhubang',
      apiMethod: 'GET',
    },
    {
      path: '/market/institution',
      label: '机构荐股',
      icon: ARTDECO_ICONS.INSTITUTION,
      description: '机构推荐股票',
      apiEndpoint: '/api/v1/data/market/institution',
      apiMethod: 'GET',
    },
    {
      path: '/market/wencai',
      label: '问财选股',
      icon: ARTDECO_ICONS.WENCAI,
      description: '问财选股工具',
      apiEndpoint: '/api/v1/market/wencai',
      apiMethod: 'POST',
    },
    {
      path: '/market/screener',
      label: '股票筛选',
      icon: ARTDECO_ICONS.SCREENER,
      description: '多维股票筛选',
      apiEndpoint: '/api/v1/data/market/screener',
      apiMethod: 'GET',
    },
  ],
}

/**
 * 2. 选股分析（6个子菜单）
 * 对应API: portfolio.py, watchlist.py, selection.py (50+ endpoints)
 */
export const STOCK_SELECTION_MENU_ENHANCED: MenuItem = {
  path: '/stocks',
  label: '选股分析',
  icon: ARTDECO_ICONS.WATCHLIST,
  description: 'Portfolio + Watchlist + Activity',
  apiEndpoint: '/api/user/stock-management-summary',
  apiMethod: 'GET',
  priority: 'primary',
  children: [
    {
      path: '/stocks/portfolio',
      label: '投资组合',
      icon: ARTDECO_ICONS.PORTFOLIO,
      description: '投资组合管理',
      apiEndpoint: '/api/portfolio/overview',
      apiMethod: 'GET',
    },
    {
      path: '/stocks/watchlist',
      label: '关注列表',
      icon: ARTDECO_ICONS.WATCHLIST,
      description: '自选股/关注列表',
      apiEndpoint: '/api/watchlist',
      apiMethod: 'GET',
      liveUpdate: true,
      wsChannel: 'watchlist:update',
    },
    {
      path: '/stocks/activity',
      label: '交易活动',
      icon: ARTDECO_ICONS.ACTIVITY,
      description: '交易历史记录',
      apiEndpoint: '/api/trading/activity',
      apiMethod: 'GET',
    },
    {
      path: '/stocks/strategy-selection',
      label: '策略选股',
      icon: ARTDECO_ICONS.STRATEGY_SELECTION,
      description: '策略选股结果',
      apiEndpoint: '/api/selection/strategy',
      apiMethod: 'GET',
    },
    {
      path: '/stocks/industry-selection',
      label: '行业选股',
      icon: ARTDECO_ICONS.INDUSTRY_SELECTION,
      description: '行业股票筛选',
      apiEndpoint: '/api/selection/industry',
      apiMethod: 'GET',
    },
    {
      path: '/stocks/concept-selection',
      label: '概念选股',
      icon: ARTDECO_ICONS.CONCEPT_SELECTION,
      description: '概念股票筛选',
      apiEndpoint: '/api/selection/concept',
      apiMethod: 'GET',
    },
  ],
}

/**
 * 3. 策略中心（6个子菜单）
 * 对应API: technical_analysis.py, indicators.py, strategy_design.py (45+ endpoints)
 */
export const STRATEGY_CENTER_MENU_ENHANCED: MenuItem = {
  path: '/strategy',
  label: '策略中心',
  icon: ARTDECO_ICONS.STRATEGY,
  description: '技术分析、基本面分析、指标分析',
  apiEndpoint: '/api/analysis/summary',
  apiMethod: 'GET',
  priority: 'secondary',
  children: [
    {
      path: '/analysis/technical',
      label: '技术分析',
      icon: ARTDECO_ICONS.TECHNICAL_ANALYSIS,
      description: '技术指标分析',
      apiEndpoint: '/api/technical/analyze',
      apiMethod: 'POST',
    },
    {
      path: '/analysis/fundamental',
      label: '基本面分析',
      icon: ARTDECO_ICONS.FUNDAMENTAL,
      description: '基本面数据分析',
      apiEndpoint: '/api/fundamental/analyze',
      apiMethod: 'GET',
    },
    {
      path: '/analysis/indicator',
      label: '指标分析',
      icon: ARTDECO_ICONS.INDICATOR,
      description: '自定义指标分析',
      apiEndpoint: '/api/indicators/calculate',
      apiMethod: 'POST',
    },
    {
      path: '/analysis/custom-indicator',
      label: '自定义指标',
      icon: ARTDECO_ICONS.CUSTOM_INDICATOR,
      description: '自定义技术指标',
      apiEndpoint: '/api/indicators/custom',
      apiMethod: 'POST',
    },
    {
      path: '/analysis/stock-analysis',
      label: '股票分析',
      icon: ARTDECO_ICONS.STOCK_ANALYSIS,
      description: '基于个股的分析',
      apiEndpoint: '/api/analysis/stock',
      apiMethod: 'GET',
    },
    {
      path: '/analysis/list-analysis',
      label: '列表分析',
      icon: ARTDECO_ICONS.LIST_ANALYSIS,
      description: '基于关注列表/选股的分析',
      apiEndpoint: '/api/analysis/list',
      apiMethod: 'POST',
    },
  ],
}

/**
 * 4. 交易管理（5个子菜单）
 * 对应API: risk_management.py, trading.py (37+ endpoints)
 */
export const TRADING_MANAGEMENT_MENU_ENHANCED: MenuItem = {
  path: '/trading',
  label: '交易管理',
  icon: ARTDECO_ICONS.TRADING,
  description: '个股预警、风险指标、舆情管理',
  apiEndpoint: '/api/risk/overview',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'risk:overview',
  priority: 'secondary',
  children: [
    {
      path: '/risk/alerts',
      label: '个股预警',
      icon: ARTDECO_ICONS.ALERT,
      description: '个股预警设置',
      apiEndpoint: '/api/risk/alerts',
      apiMethod: 'GET',
      badge: 3,
    },
    {
      path: '/risk/indicators',
      label: '风险指标',
      icon: ARTDECO_ICONS.RISK_INDICATORS,
      description: '风险指标管理',
      apiEndpoint: '/api/risk/indicators',
      apiMethod: 'GET',
    },
    {
      path: '/risk/sentiment',
      label: '舆情管理',
      icon: ARTDECO_ICONS.SENTIMENT,
      description: '舆情监控管理',
      apiEndpoint: '/api/risk/sentiment',
      apiMethod: 'GET',
    },
    {
      path: '/risk/position-risk',
      label: '持仓风险',
      icon: ARTDECO_ICONS.POSITION_RISK,
      description: '个股/持仓风险表现',
      apiEndpoint: '/api/risk/position',
      apiMethod: 'GET',
    },
    {
      path: '/risk/factor-analysis',
      label: '因子分析',
      icon: ARTDECO_ICONS.FACTOR_ANALYSIS,
      description: '风险因子分析',
      apiEndpoint: '/api/risk/factors',
      apiMethod: 'POST',
    },
  ],
}

/**
 * 5. 风险监控（8个子菜单）
 * 对应API: risk_management.py, alerts.py (50+ endpoints)
 */
export const RISK_MONITORING_MENU_ENHANCED: MenuItem = {
  path: '/risk',
  label: '风险监控',
  icon: ARTDECO_ICONS.RISK,
  description: '策略设计、GPU回测、交易信号',
  apiEndpoint: '/api/strategy/overview',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'strategy:overview',
  priority: 'secondary',
  children: [
    {
      path: '/strategy/design',
      label: '策略设计',
      icon: ARTDECO_ICONS.STRATEGY_DESIGN,
      description: '交易策略设计',
      apiEndpoint: '/api/strategy/design',
      apiMethod: 'POST',
    },
    {
      path: '/strategy/management',
      label: '策略管理',
      icon: ARTDECO_ICONS.STRATEGY_MANAGEMENT,
      description: '策略管理',
      apiEndpoint: '/api/strategy/list',
      apiMethod: 'GET',
    },
    {
      path: '/strategy/backtest',
      label: '策略回测',
      icon: ARTDECO_ICONS.BACKTEST,
      description: 'GPU加速回测',
      apiEndpoint: '/api/backtest/run',
      apiMethod: 'POST',
    },
    {
      path: '/strategy/gpu-backtest',
      label: 'GPU回测',
      icon: ARTDECO_ICONS.GPU_BACKTEST,
      description: 'GPU加速回测引擎',
      apiEndpoint: '/api/gpu/backtest',
      apiMethod: 'POST',
      badge: 'NEW',
    },
    {
      path: '/strategy/signals',
      label: '交易信号',
      icon: ARTDECO_ICONS.SIGNALS,
      description: '交易信号管理',
      apiEndpoint: '/api/signals',
      apiMethod: 'GET',
      liveUpdate: true,
      wsChannel: 'signals:update',
    },
    {
      path: '/strategy/trade-history',
      label: '交易历史',
      icon: ARTDECO_ICONS.TRADE_HISTORY,
      description: '交易历史记录',
      apiEndpoint: '/api/trading/history',
      apiMethod: 'GET',
    },
    {
      path: '/strategy/positions',
      label: '持仓分析',
      icon: ARTDECO_ICONS.POSITIONS,
      description: '持仓分析',
      apiEndpoint: '/api/positions',
      apiMethod: 'GET',
    },
    {
      path: '/strategy/attribution',
      label: '事后归因',
      icon: ARTDECO_ICONS.ATTRIBUTION,
      description: '交易归因分析',
      apiEndpoint: '/api/attribution',
      apiMethod: 'POST',
    },
  ],
}

/**
 * 6. 系统设置（5个子菜单）
 * 对应API: monitoring.py, system.py, settings.py (35+ endpoints)
 */
export const SYSTEM_SETTINGS_MENU_ENHANCED: MenuItem = {
  path: '/system',
  label: '系统设置',
  icon: ARTDECO_ICONS.SETTINGS,
  description: '平台监控、系统设置、数据更新',
  apiEndpoint: '/api/monitoring/platform-status',
  apiMethod: 'GET',
  liveUpdate: true,
  wsChannel: 'system:status',
  priority: 'tertiary',
  children: [
    {
      path: '/system/monitoring',
      label: '平台监控',
      icon: ARTDECO_ICONS.MONITORING,
      description: 'Grafana平台监控',
      apiEndpoint: '/api/monitoring/dashboard',
      apiMethod: 'GET',
    },
    {
      path: '/system/settings',
      label: '系统设置',
      icon: ARTDECO_ICONS.SETTINGS,
      description: '系统配置',
      apiEndpoint: '/api/system/settings',
      apiMethod: 'GET',
    },
    {
      path: '/system/data-update',
      label: '数据更新',
      icon: ARTDECO_ICONS.DATA_UPDATE,
      description: '数据更新状态',
      apiEndpoint: '/api/system/data-update',
      apiMethod: 'GET',
    },
    {
      path: '/system/data-quality',
      label: '数据质量',
      icon: ARTDECO_ICONS.DATA_QUALITY,
      description: '数据质量监控',
      apiEndpoint: '/api/monitoring/data-quality',
      apiMethod: 'GET',
    },
    {
      path: '/system/api-health',
      label: 'API健康',
      icon: ARTDECO_ICONS.API_HEALTH,
      description: 'API健康状态',
      apiEndpoint: '/api/monitoring/api-health',
      apiMethod: 'GET',
    },
  ],
}

// ========== 导出增强版菜单配置 ==========
export const ARTDECO_MENU_ENHANCED: MenuItem[] = [
  MARKET_OBSERVATION_MENU_ENHANCED,
  STOCK_SELECTION_MENU_ENHANCED,
  STRATEGY_CENTER_MENU_ENHANCED,
  TRADING_MANAGEMENT_MENU_ENHANCED,
  RISK_MONITORING_MENU_ENHANCED,
  SYSTEM_SETTINGS_MENU_ENHANCED,
]

// ========== 菜单配置映射表 ==========
export const MENU_CONFIG_ENHANCED_MAP = {
  ArtDecoEnhanced: ARTDECO_MENU_ENHANCED,
  // 保持向后兼容
  ArtDecoDashboard: ARTDECO_MENU_ITEMS,
} as const

// ========== 类型导出 ==========
export type LayoutNameEnhanced = keyof typeof MENU_CONFIG_ENHANCED_MAP
export type MenuConfigEnhancedMap = typeof MENU_CONFIG_ENHANCED_MAP

// ========== 工具函数 ==========

/**
 * 获取菜单项的所有API端点
 * @param menu 菜单配置
 * @returns API端点列表
 */
export function getMenuApiEndpoints(menu: MenuItem): string[] {
  const endpoints: string[] = []

  if (menu.apiEndpoint) {
    endpoints.push(menu.apiEndpoint)
  }

  if (menu.children) {
    menu.children.forEach(child => {
      if (child.apiEndpoint) {
        endpoints.push(child.apiEndpoint)
      }
    })
  }

  return endpoints
}

/**
 * 获取所有WebSocket频道
 * @param menus 菜单配置数组
 * @returns WebSocket频道列表
 */
export function getAllWebSocketChannels(menus: MenuItem[]): string[] {
  const channels: string[] = []

  menus.forEach(menu => {
    if (menu.wsChannel) {
      channels.push(menu.wsChannel)
    }

    if (menu.children) {
      menu.children.forEach(child => {
        if (child.wsChannel) {
          channels.push(child.wsChannel)
        }
      })
    }
  })

  return [...new Set(channels)] // 去重
}

/**
 * 查找菜单项
 * @param menus 菜单配置数组
 * @param path 路由路径
 * @returns 菜单项或undefined
 */
export function findMenuItem(menus: MenuItem[], path: string): MenuItem | undefined {
  for (const menu of menus) {
    if (menu.path === path) {
      return menu
    }

    if (menu.children) {
      const found = menu.children.find(child => child.path === path)
      if (found) {
        return found
      }
    }
  }

  return undefined
}

/**
 * 获取实时更新的菜单项
 * @param menus 菜单配置数组
 * @returns 实时更新菜单项列表
 */
export function getLiveUpdateMenus(menus: MenuItem[]): MenuItem[] {
  const liveItems: MenuItem[] = []

  menus.forEach(menu => {
    if (menu.liveUpdate) {
      liveItems.push(menu)
    }

    if (menu.children) {
      menu.children.forEach(child => {
        if (child.liveUpdate) {
          liveItems.push(child)
        }
      })
    }
  })

  return liveItems
}
