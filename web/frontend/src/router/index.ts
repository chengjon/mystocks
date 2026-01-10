import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

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

  // ========== Dashboard域 (MainLayout) ==========
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: false },
    children: [
      {
        path: 'dashboard',
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
      {
        path: 'overview',
        name: 'risk-overview',
        component: () => import('@/views/RiskMonitor.vue'),
        meta: { title: 'Overview', icon: '📊', breadcrumb: 'Overview' }
      },
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

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
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
