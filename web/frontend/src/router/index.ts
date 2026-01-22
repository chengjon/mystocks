import { createRouter, createWebHistory, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

/**
 * MyStocks Frontend Router Configuration (Phase 2.3 - 优化版)
 *
 * 功能域Layout映射:
 * - MainLayout: Dashboard, Watchlist, Portfolio, Activity
 * - MarketLayout: Stock List, Realtime, K-Line, Depth, Sector
 * - DataLayout: Stock Analysis (Screener, Industry, Concept, Fundamental, Technical)
 * - RiskLayout: Risk Monitor (Overview, Position Risk, Portfolio Risk, Alerts, Stress Test)
 * - StrategyLayout: Strategy Management (My Strategies, Market, Backtest, Signals, Performance)
 * - MonitoringLayout: Monitoring Platform (Dashboard, Data Quality, Performance, API Health, Logs)
 *
 * URL设计原则:
 * 1. 语义化 - 使用RESTful风格的URL结构
 * 2. 层级清晰 - 体现功能域和子功能的关系
 * 3. 简洁易读 - 避免过深的嵌套和冗余路径
 * 4. 一致性 - 同类功能使用相似的URL模式
 *
 * 面包屑生成:
 * - 使用 meta.title 和 meta.breadcrumb 自动生成
 * - 支持自定义面包屑覆盖
 */

// 扩展RouteMeta类型
declare module 'vue-router' {
  interface RouteMeta {
    title?: string
    icon?: string
    breadcrumb?: string
    requiresAuth?: boolean
    description?: string
  }
}

const routes: RouteRecordRaw[] = [
  // ========== 测试路由 ==========
  {
    path: '/test',
    name: 'test',
    component: () => import('@/views/Test.vue'),
    meta: {
      title: 'Test Page',
      requiresAuth: false
    }
  },

  // ArtDeco 组件测试页面
  {
    path: '/artdeco/test',
    name: 'artdeco-test',
    component: () => import('@/views/ArtDecoTest.vue'),
    meta: {
      title: 'ArtDeco Component Test',
      requiresAuth: false
    }
  },

  // ========== 公开路由 ==========
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: 'Login',
      requiresAuth: false
    }
  },

   // ========== ArtDeco 主菜单系统 ==========
   // 使用统一的ArtDecoLayout提供菜单导航

    // ArtDeco 主页路由 - MyStocks 指挥中心 (仪表盘)
    {
      path: '/',
      name: 'home',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/dashboard',
      children: [
        {
          path: '/dashboard',
          name: 'dashboard',
          component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
          meta: {
            title: '仪表盘',
            icon: '🏛️',
            requiresAuth: false
          }
        }
      ]
    },

    // ArtDeco Market域 - 市场行情
    {
      path: '/market',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/market/realtime',
     children: [
       {
         path: 'realtime',
         name: 'market-realtime',
         component: () => import('@/views/artdeco-pages/components/market/ArtDecoRealtimeMonitor.vue'),
         meta: {
           title: '实时监控',
           icon: '⚡',
           breadcrumb: 'Market > Realtime Monitor',
           requiresAuth: false,
           description: '实时市场监控',
           apiEndpoint: '/api/market/v2/realtime-summary',
           liveUpdate: true,
           wsChannel: 'market:realtime'
         }
       },
       {
         path: 'analysis',
         name: 'market-analysis',
         component: () => import('@/views/artdeco-pages/components/market/ArtDecoMarketAnalysis.vue'),
         meta: {
           title: '市场分析',
           icon: '📊',
           breadcrumb: 'Market > Analysis',
           requiresAuth: false,
           description: '市场数据分析',
           apiEndpoint: '/api/market/v2/analysis',
           liveUpdate: false
         }
       },
       {
         path: 'overview',
         name: 'market-overview',
         component: () => import('@/views/artdeco-pages/components/market/ArtDecoMarketOverview.vue'),
         meta: {
           title: '市场概览',
           icon: '🌐',
           breadcrumb: 'Market > Overview',
           requiresAuth: false,
           description: '市场总体概览',
           apiEndpoint: '/api/market/v2/overview',
           liveUpdate: false
         }
       },
       {
         path: 'industry',
         name: 'market-industry',
         component: () => import('@/views/artdeco-pages/components/market/ArtDecoIndustryAnalysis.vue'),
         meta: {
           title: '行业分析',
           icon: '🏢',
           breadcrumb: 'Market > Industry Analysis',
           requiresAuth: false,
           description: '行业板块分析',
           apiEndpoint: '/api/market/sector',
           liveUpdate: false
         }
       }
     ]
   },

    // ArtDeco 股票管理
    {
      path: '/stocks',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/stocks/management',
     children: [
       {
         path: 'management',
         name: 'stock-management',
         component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
         meta: {
           title: '股票管理',
           icon: '📋',
           requiresAuth: false
         }
       }
     ]
   },

    // ArtDeco 投资分析
    {
      path: '/analysis',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/analysis/data',
     children: [
       {
         path: 'data',
         name: 'data-analysis',
         component: () => import('@/views/artdeco-pages/ArtDecoDataAnalysis.vue'),
         meta: {
           title: '投资分析',
           icon: '🔍',
           requiresAuth: false
         }
       }
     ]
   },

    // ArtDeco Risk域 - 风险管理
    {
      path: '/risk',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/risk/alerts',
     children: [
       {
         path: 'alerts',
         name: 'risk-alerts',
         component: () => import('@/views/artdeco-pages/components/risk/ArtDecoRiskAlerts.vue'),
         meta: {
           title: '风险告警',
           icon: '🔔',
           breadcrumb: 'Risk > Alerts',
           requiresAuth: false,
           description: '风险告警通知',
           apiEndpoint: '/api/v1/risk/alerts',
           liveUpdate: true,
           wsChannel: 'risk:alerts'
         }
       },
       {
         path: 'monitor',
         name: 'risk-monitor',
         component: () => import('@/views/artdeco-pages/components/risk/ArtDecoRiskMonitor.vue'),
         meta: {
           title: '风险监控',
           icon: '📊',
           breadcrumb: 'Risk > Monitor',
           requiresAuth: false,
           description: '风险指标监控',
           apiEndpoint: '/api/monitoring/watchlists',
           liveUpdate: true
         }
       },
       {
         path: 'announcement',
         name: 'risk-announcement',
         component: () => import('@/views/artdeco-pages/components/risk/ArtDecoAnnouncementMonitor.vue'),
         meta: {
           title: '公告监控',
           icon: '📰',
           breadcrumb: 'Risk > Announcement',
           requiresAuth: false,
           description: '公司公告监控',
           apiEndpoint: '/api/announcements',
           liveUpdate: false
         }
       }
     ]
   },

    // ArtDeco Trading域 - 交易管理
    {
      path: '/trading',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/trading/signals',
     children: [
       {
         path: 'signals',
         name: 'trading-signals',
         component: () => import('@/views/artdeco-pages/components/ArtDecoTradingSignals.vue'),
         meta: {
           title: '交易信号',
           icon: '📡',
           breadcrumb: 'Trading > Signals',
           requiresAuth: false,
           description: '实时交易信号监控',
           apiEndpoint: '/api/trading/signals',
           liveUpdate: true,
           wsChannel: 'trading:signals'
         }
       },
       {
         path: 'history',
         name: 'trading-history',
         component: () => import('@/views/artdeco-pages/components/ArtDecoTradingHistory.vue'),
         meta: {
           title: '交易历史',
           icon: '📋',
           breadcrumb: 'Trading > History',
           requiresAuth: false,
           description: '历史交易记录',
           apiEndpoint: '/api/trading/history',
           liveUpdate: false
         }
       },
       {
         path: 'positions',
         name: 'trading-positions',
         component: () => import('@/views/artdeco-pages/components/ArtDecoTradingPositions.vue'),
         meta: {
           title: '持仓监控',
           icon: '📊',
           breadcrumb: 'Trading > Positions',
           requiresAuth: false,
           description: '当前持仓统计',
           apiEndpoint: '/api/api/mtm/portfolio',
           liveUpdate: false
         }
       },
       {
         path: 'stats',
         name: 'trading-stats',
         component: () => import('@/views/artdeco-pages/components/ArtDecoTradingStats.vue'),
         meta: {
           title: '交易统计',
           icon: '📈',
           breadcrumb: 'Trading > Statistics',
           requiresAuth: false,
           description: '交易数据分析',
           apiEndpoint: '/api/trading/statistics',
           liveUpdate: false
         }
       }
     ]
   },

    // ArtDeco Strategy域 - 策略管理
    {
      path: '/strategy',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/strategy/management',
     children: [
       {
         path: 'management',
         name: 'strategy-management',
         component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyManagement.vue'),
         meta: {
           title: '策略管理',
           icon: '⚙️',
           breadcrumb: 'Strategy > Management',
           requiresAuth: false,
           description: '策略配置、测试、管理',
           apiEndpoint: '/api/strategy-mgmt/strategies',
           liveUpdate: false
         }
       },
       {
         path: 'optimization',
         name: 'strategy-optimization',
         component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoStrategyOptimization.vue'),
         meta: {
           title: '策略优化',
           icon: '🎯',
           breadcrumb: 'Strategy > Optimization',
           requiresAuth: false,
           description: '参数优化、性能评估',
           apiEndpoint: '/api/strategy/optimize',
           liveUpdate: false
         }
       },
       {
         path: 'backtest',
         name: 'strategy-backtest',
         component: () => import('@/views/artdeco-pages/components/strategy/ArtDecoBacktestAnalysis.vue'),
         meta: {
           title: '回测分析',
           icon: '🔬',
           breadcrumb: 'Strategy > Backtest',
           requiresAuth: false,
           description: '回测配置、结果分析',
           apiEndpoint: '/api/analysis/backtest',
           liveUpdate: false
         }
       }
     ]
   },

    // ArtDeco System域 - 系统管理
    {
      path: '/system',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/system/monitoring',
     children: [
       {
         path: 'monitoring',
         name: 'system-monitoring',
         component: () => import('@/views/artdeco-pages/components/system/ArtDecoMonitoringDashboard.vue'),
         meta: {
           title: '监控面板',
           icon: '📊',
           breadcrumb: 'System > Monitoring Dashboard',
           requiresAuth: false,
           description: '平台监控仪表板',
           apiEndpoint: '/api/monitoring/platform-status',
           liveUpdate: true,
           wsChannel: 'system:status'
         }
       },
       {
         path: 'data',
         name: 'system-data',
         component: () => import('@/views/artdeco-pages/components/system/ArtDecoDataManagement.vue'),
         meta: {
           title: '数据管理',
           icon: '🗂️',
           breadcrumb: 'System > Data Management',
           requiresAuth: false,
           description: '数据源配置和管理',
           apiEndpoint: '/api/data-sources/config',
           liveUpdate: false
         }
       },
       {
         path: 'settings',
         name: 'system-settings',
         component: () => import('@/views/artdeco-pages/components/system/ArtDecoSystemSettings.vue'),
         meta: {
           title: '系统设置',
           icon: '⚙️',
           breadcrumb: 'System > Settings',
           requiresAuth: false,
           description: '系统配置和设置',
           apiEndpoint: '/api/system/config',
           liveUpdate: false
         }
       }
     ]
   },

   // ========== 兼容旧的ArtDeco路由 (重定向到新结构) ==========
   {
     path: '/artdeco/market',
     redirect: '/market/data'
   },
   {
     path: '/artdeco/market-quotes',
     redirect: '/market/quotes'
   },
   {
     path: '/artdeco/stock-management',
     redirect: '/stocks/management'
   },
   {
     path: '/artdeco/analysis',
     redirect: '/analysis/data'
   },
   {
     path: '/artdeco/risk',
     redirect: '/risk/management'
   },
   {
     path: '/artdeco/trading',
     redirect: '/strategy/trading'
   },
   {
     path: '/artdeco/backtest',
     redirect: '/strategy/backtest'
   },
   {
     path: '/artdeco/settings',
     redirect: '/system/monitoring'
   },

  // ========== 保留原有路由结构 (已禁用，统一使用ArtDeco) ==========
  // ========== Dashboard域 (MainLayout) - DISABLED ==========
  // 注释原因: 统一使用ArtDecoLayout + ArtDecoDashboard
  // Date: 2026-01-19
  /*
  {
    path: '/dashboard',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard/overview',
    meta: { requiresAuth: false },
    children: [
      {
        path: 'overview',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Overview', icon: '📊', breadcrumb: 'Dashboard' }
      },
      {
        path: 'dashboard/watchlist',
        name: 'dashboard-watchlist',
        component: () => import('@/views/Stocks.vue'),
        meta: { title: 'Watchlist', icon: '⭐', breadcrumb: 'Watchlist' }
      },
      {
        path: 'dashboard/portfolio',
        name: 'dashboard-portfolio',
        component: () => import('@/views/PortfolioManagement.vue'),
        meta: { title: 'Portfolio', icon: '💼', breadcrumb: 'Portfolio' }
      },
      {
        path: 'dashboard/activity',
        name: 'dashboard-activity',
        component: () => import('@/views/TradeManagement.vue'),
        meta: { title: 'Activity', icon: '📈', breadcrumb: 'Activity' }
      },
      // 兼容旧路由
      {
        path: 'analysis',
        redirect: '/analysis/screener'
      },
      {
        path: 'stocks',
        redirect: '/dashboard/watchlist'
      },
      {
        path: 'trade',
        redirect: '/dashboard/activity'
      },
      {
        path: 'portfolio',
        redirect: '/dashboard/portfolio'
      }
    ]
  },
  */

  // ========== Market Data域 (MarketLayout) ==========
  {
    path: '/market',
    component: () => import('@/layouts/MarketLayout.vue'),
    redirect: '/market/list',
    meta: { requiresAuth: false, title: 'Market Data', icon: '📈' },
    children: [
      {
        path: 'list',
        name: 'market-list',
        component: () => import('@/views/Market.vue'),
        meta: { title: 'Stock List', icon: '📋', breadcrumb: 'Stock List' }
      },
      {
        path: 'realtime',
        name: 'market-realtime',
        component: () => import('@/views/RealTimeMonitor.vue'),
        meta: { title: 'Realtime', icon: '⚡', breadcrumb: 'Realtime' }
      },
      {
        path: 'kline/:symbol?',
        name: 'market-kline',
        component: () => import('@/views/StockDetail.vue'),
        meta: { title: 'K-Line', icon: '📊', breadcrumb: 'K-Line' }
      },
      {
        path: 'depth',
        name: 'market-depth',
        component: () => import('@/views/TdxMarket.vue'),
        meta: { title: 'Depth', icon: '📉', breadcrumb: 'Depth' }
      },
      {
        path: 'sector',
        name: 'market-sector',
        component: () => import('@/views/IndustryConceptAnalysis.vue'),
        meta: { title: 'Sector', icon: '🏢', breadcrumb: 'Sector' }
      },
      // 兼容旧路由
      {
        path: 'tdx-market',
        redirect: '/market/depth'
      }
    ]
  },

  // ========== Stock Analysis域 (DataLayout) ==========
  {
    path: '/analysis',
    component: () => import('@/layouts/DataLayout.vue'),
    redirect: '/analysis/screener',
    meta: { requiresAuth: false, title: 'Stock Analysis', icon: '🔍' },
    children: [
      {
        path: 'screener',
        name: 'analysis-screener',
        component: () => import('@/views/Analysis.vue'),
        meta: { title: 'Stock Screener', icon: '🔍', breadcrumb: 'Screener' }
      },
      {
        path: 'industry',
        name: 'analysis-industry',
        component: () => import('@/views/IndustryConceptAnalysis.vue'),
        meta: { title: 'Industry', icon: '🏢', breadcrumb: 'Industry' }
      },
      {
        path: 'concept',
        name: 'analysis-concept',
        component: () => import('@/components/market/WencaiPanelV2.vue'),
        meta: { title: 'Concept', icon: '💡', breadcrumb: 'Concept' }
      },
      {
        path: 'fundamental',
        name: 'analysis-fundamental',
        component: () => import('@/views/StockDetail.vue'),
        meta: { title: 'Fundamental', icon: '📑', breadcrumb: 'Fundamental' }
      },
      {
        path: 'technical',
        name: 'analysis-technical',
        component: () => import('@/views/TechnicalAnalysis.vue'),
        meta: { title: 'Technical', icon: '📊', breadcrumb: 'Technical' }
      },
      // 兼容旧路由
      {
        path: 'industry-concept',
        redirect: '/analysis/industry'
      }
    ]
  },

  // ========== Risk Monitor域 (RiskLayout) ==========
  {
    path: '/risk',
    component: () => import('@/layouts/RiskLayout.vue'),
    redirect: '/risk/overview',
    meta: { requiresAuth: false, title: 'Risk Monitor', icon: '⚠️' },
    children: [
      // Temporarily removed - RiskMonitor.vue needs to be recreated
      // {
      //   path: 'overview',
      //   name: 'risk-overview',
      //   component: () => import('@/views/RiskMonitor.vue'),
      //   meta: { title: 'Overview', icon: '📊', breadcrumb: 'Overview' }
      // },
      {
        path: 'position',
        name: 'risk-position',
        component: () => import('@/views/TradeManagement.vue'),
        meta: { title: 'Position Risk', icon: '📉', breadcrumb: 'Position' }
      },
      {
        path: 'portfolio',
        name: 'risk-portfolio',
        component: () => import('@/views/PortfolioManagement.vue'),
        meta: { title: 'Portfolio Risk', icon: '💼', breadcrumb: 'Portfolio' }
      },
      {
        path: 'alerts',
        name: 'risk-alerts',
        component: () => import('@/views/announcement/AnnouncementMonitor.vue'),
        meta: { title: 'Alerts', icon: '🔔', breadcrumb: 'Alerts' }
      },
      {
        path: 'stress',
        name: 'risk-stress',
        component: () => import('@/views/BacktestAnalysis.vue'),
        meta: { title: 'Stress Test', icon: '🧪', breadcrumb: 'Stress Test' }
      }
    ]
  },

  // ========== Strategy Management域 (StrategyLayout) ==========
  {
    path: '/strategy',
    component: () => import('@/layouts/StrategyLayout.vue'),
    redirect: '/strategy/list',
    meta: { requiresAuth: false, title: 'Strategy Management', icon: '📚' },
    children: [
      {
        path: 'list',
        name: 'strategy-list',
        component: () => import('@/views/StrategyManagement.vue'),
        meta: { title: 'My Strategies', icon: '📚', breadcrumb: 'My Strategies' }
      },
      {
        path: 'market',
        name: 'strategy-market',
        component: () => import('@/views/Market.vue'),
        meta: { title: 'Market', icon: '📈', breadcrumb: 'Market' }
      },
      {
        path: 'backtest',
        name: 'strategy-backtest',
        component: () => import('@/views/BacktestAnalysis.vue'),
        meta: { title: 'Backtest', icon: '🔬', breadcrumb: 'Backtest' }
      },
      {
        path: 'signals',
        name: 'strategy-signals',
        component: () => import('@/views/RealTimeMonitor.vue'),
        meta: { title: 'Signals', icon: '📡', breadcrumb: 'Signals' }
      },
      {
        path: 'performance',
        name: 'strategy-performance',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Performance', icon: '📊', breadcrumb: 'Performance' }
      }
    ]
  },

  // ========== Monitoring Platform域 (MonitoringLayout) ==========
  {
    path: '/monitoring',
    component: () => import('@/layouts/MonitoringLayout.vue'),
    redirect: '/monitoring/dashboard',
    meta: { requiresAuth: false, title: 'Monitoring Platform', icon: '🔍' },
    children: [
      {
        path: 'dashboard',
        name: 'monitoring-dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Dashboard', icon: '📊', breadcrumb: 'Dashboard' }
      },
      {
        path: 'data-quality',
        name: 'monitoring-data-quality',
        component: () => import('@/views/monitoring/WatchlistManagement.vue'),
        meta: { title: 'Data Quality', icon: '✅', breadcrumb: 'Data Quality' }
      },
      {
        path: 'performance',
        name: 'monitoring-performance',
        component: () => import('@/views/monitoring/RiskDashboard.vue'),
        meta: { title: 'Performance', icon: '⚡', breadcrumb: 'Performance' }
      },
      {
        path: 'api',
        name: 'monitoring-api',
        component: () => import('@/views/system/DatabaseMonitor.vue'),
        meta: { title: 'API Health', icon: '🔌', breadcrumb: 'API' }
      },
      {
        path: 'logs',
        name: 'monitoring-logs',
        component: () => import('@/views/system/Architecture.vue'),
        meta: { title: 'Logs', icon: '📝', breadcrumb: 'Logs' }
      }
    ]
  },

  // ========== 系统管理页 (MainLayout) ==========
  {
    path: '/settings',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/settings/general',
    meta: { requiresAuth: false, title: 'Settings', icon: '⚙️' },
    children: [
      {
        path: 'general',
        name: 'settings-general',
        component: () => import('@/views/Settings.vue'),
        meta: { title: 'General', icon: '⚙️', breadcrumb: 'General' }
      },
      {
        path: 'system',
        name: 'settings-system',
        component: () => import('@/views/system/Architecture.vue'),
        meta: { title: 'System', icon: '🖥️', breadcrumb: 'System' }
      },
      {
        path: 'database',
        name: 'settings-database',
        component: () => import('@/views/system/DatabaseMonitor.vue'),
        meta: { title: 'Database', icon: '💾', breadcrumb: 'Database' }
      }
    ]
  },

  // ========== 演示和测试页 ==========
  {
    path: '/demo',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/demo/openstock',
    meta: { requiresAuth: false, title: 'Demos', icon: '🎮' },
    children: [
      {
        path: 'openstock',
        name: 'demo-openstock',
        component: () => import('@/views/OpenStockDemo.vue'),
        meta: { title: 'OpenStock Demo', icon: '📊', breadcrumb: 'OpenStock' }
      },
      {
        path: 'freqtrade',
        name: 'demo-freqtrade',
        component: () => import('@/views/FreqtradeDemo.vue'),
        meta: { title: 'Freqtrade Demo', icon: '📈', breadcrumb: 'Freqtrade' }
      },
      {
        path: 'stock-analysis',
        name: 'demo-stock-analysis',
        component: () => import('@/views/StockAnalysisDemo.vue'),
        meta: { title: 'Stock Analysis Demo', icon: '📊', breadcrumb: 'Stock Analysis' }
      },
      {
        path: 'tdxpy',
        name: 'demo-tdxpy',
        component: () => import('@/views/TdxpyDemo.vue'),
        meta: { title: 'TDXPY Demo', icon: '🔗', breadcrumb: 'TDXPY' }
      },
      {
        path: 'smart-data',
        name: 'demo-smart-data',
        component: () => import('@/views/SmartDataSourceTest.vue'),
        meta: { title: 'Smart Data Test', icon: '🧪', breadcrumb: 'Smart Data' }
      }
    ]
  },

  // ========== 404 Not Found ==========
  {
    path: '/:pathMatch(.*)*',
    name: 'notFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Not Found', icon: '❌' }
  }
]

// ✅ HTML5 History API 支持检测（IE9优雅降级）
// 检测浏览器是否支持HTML5 History API（pushState、replaceState）
const supportsHistory = 'pushState' in window.history &&
                        'replaceState' in window.history &&
                        !!(window.navigator.userAgent.indexOf('MSIE') === -1 ||
                           window.navigator.userAgent.indexOf('Trident/') === -1)

// 开发环境日志：记录使用的路由模式
if (import.meta.env.DEV) {
  console.log(`🚀 Router mode: ${supportsHistory ? 'HTML5 History' : 'Hash (fallback for IE9)'}`)
}

const router = createRouter({
  // 使用条件判断：支持History API时使用HTML5模式，否则回退到Hash模式
  history: supportsHistory
    ? createWebHistory(import.meta.env.BASE_URL)
    : createWebHashHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 导航守卫 - 更新页面标题
router.beforeEach((to, from, next) => {
  const title = to.meta.title || 'MyStocks'
  document.title = `${title} - MyStocks Platform`
  next()
})

export default router
