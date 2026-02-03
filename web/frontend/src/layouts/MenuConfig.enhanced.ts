/**
 * ArtDeco 菜单配置 - 增强版 (ArtDeco 2.0)
 * 
 * 特性：
 * - 5个主功能域 (Domains)，严格遵守 3 层嵌套深度
 * - SVG图标系统（使用ArtDecoIcon组件）
 * - 业务键 (Business Key) 映射机制，实现 UI 与 API 解耦
 * - 完整的 40+ 子菜单支持
 * 
 * @version 2.1
 * @updated 2026-01-24
 */

import { ARTDECO_MENU_ITEMS } from './archive/MenuConfig'

// ========== 图标常量 ==========
// 对应 ArtDecoIcon.vue 中的 50+ 个专业图标
export const ARTDECO_ICONS = {
  // 市场相关图标
  CHART: 'Market',
  REALTIME: 'Realtime',
  TECHNICAL: 'Technical',
  FUND_FLOW: 'FundFlow',
  ETF: 'ETF',
  CONCEPT: 'Concept',
  AUCTION: 'Auction',
  LONGHU: 'LongHuBang',
  INSTITUTION: 'Institution',
  WENCAI: 'Wencai',

  // 自选股相关图标
  BOOKMARK: 'Bookmark',
  INDUSTRY: 'Industry',
  SCREENER: 'Screener',

  // 交易管理图标
  TRADING: 'StrategyTrading',
  SIGNALS: 'Signals',
  TRADE_HISTORY: 'TradeHistory',
  POSITIONS: 'Positions',
  ATTRIBUTION: 'Attribution',

  // 策略中心图标
  STRATEGY: 'StrategySelection',
  STRATEGY_DESIGN: 'StrategyDesign',
  STRATEGY_MANAGEMENT: 'StrategyManagement',
  BACKTEST: 'Backtest',
  GPU_BACKTEST: 'GPUBacktest',
  INDICATOR: 'Indicator',

  // 风险管理图标
  RISK: 'RiskManagement',
  ALERT: 'Alert',
  RISK_INDICATORS: 'RiskIndicators',
  SENTIMENT: 'Sentiment',
  POSITION_RISK: 'PositionRisk',
  FACTOR_ANALYSIS: 'FactorAnalysis',
  FUNDAMENTAL: 'Fundamental',

  // 系统管理图标
  SETTINGS: 'Settings',
  MONITORING: 'Monitoring',
  DATA_UPDATE: 'DataUpdate',
  DATA_QUALITY: 'DataQuality',
  API_HEALTH: 'APIHealth',
  HOME: 'Home',
} as const

// ========== 菜单接口定义 ==========
export interface MenuItem {
  // 必填字段
  path: string
  label: string
  icon: string // SVG图标名称

  // 业务解耦字段
  businessKey?: string // 用于映射 API 和 WebSocket
  apiEndpoint?: string // 后端 API 端点
  apiMethod?: 'GET' | 'POST' | 'PUT' | 'DELETE' // API 请求方法
  apiParams?: Record<string, any> // API 请求参数
  wsChannel?: string // WebSocket 频道名称
  liveUpdate?: boolean // 是否开启实时更新

  // 可选字段
  description?: string
  badge?: string | number
  key?: string | number  // 用于Vue循环的唯一标识
  children?: MenuItem[]
  disabled?: boolean
  divider?: boolean

  // 视觉配置
  iconColor?: string
  activeIconColor?: string
  priority?: 'primary' | 'secondary' | 'tertiary'
  featured?: boolean

  // 运行时状态
  status?: 'idle' | 'loading' | 'success' | 'error'
}

// ========== 增强版菜单配置 (Functional Tree) ==========

/**
 * 0. 指挥中心 (Dashboard)
 * 职责：系统概览、核心指标、快速入口
 */
export const DASHBOARD_DOMAIN_MENU: MenuItem = {
  path: '/dashboard',
  label: '指挥中心',
  icon: ARTDECO_ICONS.HOME,
  businessKey: 'dashboard.root',
  priority: 'primary',
}

/**
 * 1. 市场总览 (Market)
 * 职责：实时行情、指数、排行、行业概念分析、龙虎榜
 */
export const MARKET_DOMAIN_MENU: MenuItem = {
  path: '/market',
  label: '市场总览',
  icon: ARTDECO_ICONS.CHART,
  businessKey: 'market.root',
  priority: 'primary',
  featured: true,
  children: [
    {
      path: '/market/realtime',
      label: '实时行情',
      icon: ARTDECO_ICONS.REALTIME,
      businessKey: 'market.realtime',
      badge: 'LIVE',
    },
    {
      path: '/market/overview',
      label: '市场概览',
      icon: ARTDECO_ICONS.CHART,
      businessKey: 'market.overview',
    },
    {
      path: '/market/analysis',
      label: '市场分析',
      icon: ARTDECO_ICONS.TECHNICAL,
      businessKey: 'market.analysis',
    },
    {
      path: '/market/industry',
      label: '行业分析',
      icon: ARTDECO_ICONS.INDUSTRY,
      businessKey: 'market.industry',
    },
    {
      path: '/market/technical',
      label: '技术指标',
      icon: ARTDECO_ICONS.TECHNICAL,
      businessKey: 'market.technical',
    },
    {
      path: '/market/fund-flow',
      label: '资金流向',
      icon: ARTDECO_ICONS.FUND_FLOW,
      businessKey: 'market.fund_flow',
    },
    {
      path: '/market/etf',
      label: 'ETF行情',
      icon: ARTDECO_ICONS.ETF,
      businessKey: 'market.etf',
    },
    {
      path: '/market/concept',
      label: '概念板块',
      icon: ARTDECO_ICONS.CONCEPT,
      businessKey: 'market.concept',
    },
    {
      path: '/market/auction',
      label: '竞价抢筹',
      icon: ARTDECO_ICONS.AUCTION,
      businessKey: 'market.auction',
    },
    {
      path: '/market/longhubang',
      label: '龙虎榜',
      icon: ARTDECO_ICONS.LONGHU,
      businessKey: 'market.longhubang',
    },
    {
      path: '/market/institution',
      label: '机构荐股',
      icon: ARTDECO_ICONS.INSTITUTION,
      businessKey: 'market.institution',
    },
    {
      path: '/market/wencai',
      label: '问财选股',
      icon: ARTDECO_ICONS.WENCAI,
      businessKey: 'market.wencai',
    },
  ],
}

/**
 * 2. 自选股 (Watchlist)
 * 职责：自选股管理、行业股票池、股票筛选器
 */
export const WATCHLIST_DOMAIN_MENU: MenuItem = {
  path: '/watchlist',
  label: '自选股',
  icon: ARTDECO_ICONS.BOOKMARK,
  businessKey: 'watchlist.root',
  priority: 'primary',
  children: [
    {
      path: '/watchlist/manage',
      label: '自选股管理',
      icon: ARTDECO_ICONS.BOOKMARK,
      businessKey: 'watchlist.manage',
      badge: 'FAV',
    },
    {
      path: '/watchlist/sector-pools',
      label: '行业股票池',
      icon: ARTDECO_ICONS.INDUSTRY,
      businessKey: 'watchlist.sector_pools',
    },
    {
      path: '/watchlist/screener',
      label: '股票筛选器',
      icon: ARTDECO_ICONS.SCREENER,
      businessKey: 'watchlist.screener',
    },
  ],
}

/**
 * 3. 交易管理 (Trading)
 * 职责：交易信号、历史订单、持仓监控、绩效归因
 */
export const TRADING_DOMAIN_MENU: MenuItem = {
  path: '/trading',
  label: '交易管理',
  icon: ARTDECO_ICONS.TRADING,
  businessKey: 'trading.root',
  priority: 'primary',
  children: [
    {
      path: '/trading/signals',
      label: '交易信号',
      icon: ARTDECO_ICONS.SIGNALS,
      businessKey: 'trading.signals',
    },
    {
      path: '/trading/history',
      label: '历史订单',
      icon: ARTDECO_ICONS.TRADE_HISTORY,
      businessKey: 'trading.history',
    },
    {
      path: '/trading/positions',
      label: '持仓监控',
      icon: ARTDECO_ICONS.POSITIONS,
      businessKey: 'trading.positions',
    },
    {
      path: '/trading/performance',
      label: '绩效分析',
      icon: ARTDECO_ICONS.INDICATOR,
      businessKey: 'trading.performance',
    },
    {
      path: '/trading/attribution',
      label: '绩效归因',
      icon: ARTDECO_ICONS.ATTRIBUTION,
      businessKey: 'trading.attribution',
    },
  ],
}

/**
 * 3. 策略中心 (Strategy)
 * 职责：策略创建/配置、回测分析 (GPU加速)、参数优化
 */
export const STRATEGY_DOMAIN_MENU: MenuItem = {
  path: '/strategy',
  label: '策略中心',
  icon: ARTDECO_ICONS.STRATEGY,
  businessKey: 'strategy.root',
  priority: 'secondary',
  children: [
    {
      path: '/strategy/design',
      label: '策略设计',
      icon: ARTDECO_ICONS.STRATEGY_DESIGN,
      businessKey: 'strategy.design',
    },
    {
      path: '/strategy/management',
      label: '策略管理',
      icon: ARTDECO_ICONS.STRATEGY_MANAGEMENT,
      businessKey: 'strategy.management',
    },
    {
      path: '/strategy/backtest',
      label: '策略回测',
      icon: ARTDECO_ICONS.BACKTEST,
      businessKey: 'strategy.backtest',
    },
    {
      path: '/strategy/gpu-backtest',
      label: 'GPU加速回测',
      icon: ARTDECO_ICONS.GPU_BACKTEST,
      businessKey: 'strategy.gpu_backtest',
      badge: 'PRO',
    },
    {
      path: '/strategy/optimization',
      label: '参数优化',
      icon: ARTDECO_ICONS.INDICATOR,
      businessKey: 'strategy.optimization',
    },
  ],
}

/**
 * 4. 风险控制 (Risk)
 * 职责：风险概览、趋势分析、公告监控、告警中心
 */
export const RISK_DOMAIN_MENU: MenuItem = {
  path: '/risk',
  label: '风险控制',
  icon: ARTDECO_ICONS.RISK,
  businessKey: 'risk.root',
  priority: 'secondary',
  children: [
    {
      path: '/risk/overview',
      label: '风险概览',
      icon: ARTDECO_ICONS.RISK,
      businessKey: 'risk.overview',
    },
    {
      path: '/risk/alerts',
      label: '告警中心',
      icon: ARTDECO_ICONS.ALERT,
      businessKey: 'risk.alerts',
      badge: 3,
    },
    {
      path: '/risk/indicators',
      label: '风险指标',
      icon: ARTDECO_ICONS.RISK_INDICATORS,
      businessKey: 'risk.indicators',
    },
    {
      path: '/risk/sentiment',
      label: '舆情监控',
      icon: ARTDECO_ICONS.SENTIMENT,
      businessKey: 'risk.sentiment',
    },
    {
      path: '/risk/announcement',
      label: '公告监控',
      icon: ARTDECO_ICONS.FUNDAMENTAL,
      businessKey: 'risk.announcement',
    },
  ],
}

/**
 * 5. 系统管理 (System)
 * 职责：运维监控、数据导入导出、系统安全性设置
 */
export const SYSTEM_DOMAIN_MENU: MenuItem = {
  path: '/system',
  label: '系统管理',
  icon: ARTDECO_ICONS.SETTINGS,
  businessKey: 'system.root',
  priority: 'tertiary',
  children: [
    {
      path: '/system/monitoring',
      label: '运维监控',
      icon: ARTDECO_ICONS.MONITORING,
      businessKey: 'system.monitoring',
    },
    {
      path: '/system/settings',
      label: '系统设置',
      icon: ARTDECO_ICONS.SETTINGS,
      businessKey: 'system.settings',
    },
    {
      path: '/system/data-update',
      label: '数据更新',
      icon: ARTDECO_ICONS.DATA_UPDATE,
      businessKey: 'system.data_update',
    },
    {
      path: '/system/data-quality',
      label: '数据质量',
      icon: ARTDECO_ICONS.DATA_QUALITY,
      businessKey: 'system.data_quality',
    },
    {
      path: '/system/api-health',
      label: 'API 健康',
      icon: ARTDECO_ICONS.API_HEALTH,
      businessKey: 'system.api_health',
    },
  ],
}

// ========== 导出增强版菜单配置 ==========
export const ARTDECO_MENU_ENHANCED: MenuItem[] = [
  DASHBOARD_DOMAIN_MENU,
  MARKET_DOMAIN_MENU,
  WATCHLIST_DOMAIN_MENU,
  TRADING_DOMAIN_MENU,
  STRATEGY_DOMAIN_MENU,
  RISK_DOMAIN_MENU,
  SYSTEM_DOMAIN_MENU,
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
 * 获取所有菜单项的 API 端点映射
 */
export function getMenuApiEndpoints(menus: MenuItem[]): Record<string, string> {
  const endpoints: Record<string, string> = {}

  const traverse = (items: MenuItem[]) => {
    items.forEach(item => {
      if (item.apiEndpoint) {
        endpoints[item.path] = item.apiEndpoint
      }
      if (item.children) {
        traverse(item.children)
      }
    })
  }

  traverse(menus)
  return endpoints
}

/**
 * 获取所有菜单项的 WebSocket 频道列表
 */
export function getAllWebSocketChannels(menus: MenuItem[]): string[] {
  const channels = new Set<string>()

  const traverse = (items: MenuItem[]) => {
    items.forEach(item => {
      if (item.wsChannel) {
        channels.add(item.wsChannel)
      }
      if (item.children) {
        traverse(item.children)
      }
    })
  }

  traverse(menus)
  return Array.from(channels)
}
