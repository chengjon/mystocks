import { createRouter, createWebHistory, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { authGuard } from './guards'

/**
 * MyStocks Frontend Router Configuration (ArtDeco v3.1 Baseline)
 * Synchronized with menu.config.js - 2026-02-15
 */

declare module 'vue-router' {
  interface RouteMeta {
    title: string
    requiresAuth?: boolean
    icon?: string
    api?: string
    layout?: 'ArtDeco' | 'Blank'
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
    redirect: '/dashboard',
    children: [
      // 1. Dashboard
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
        meta: { title: '指挥中心', requiresAuth: true, api: '/api/v1/market/overview' }
      },

      // 2. Market Domain
      {
        path: 'market',
        redirect: '/market/realtime',
        children: [
          {
            path: 'realtime',
            name: 'market-realtime',
            component: () => import('@/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue'),
            meta: { title: '实时行情', requiresAuth: true, api: '/api/v1/market/quotes' }
          },
          {
            path: 'overview',
            name: 'market-overview',
            component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue'),
            meta: { title: '市场概览', requiresAuth: true, api: '/api/v1/market/overview' }
          },
          {
            path: 'technical',
            name: 'market-kline',
            component: () => import('@/views/artdeco-pages/market-tabs/MarketKLineTab.vue'),
            meta: { title: 'K线图', requiresAuth: true, api: '/api/v1/market/kline' }
          },
          {
            path: 'wencai',
            name: 'market-wencai',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '问财选股', requiresAuth: true, api: '/api/v1/market/wencai' }
          },
          {
            path: 'etf',
            name: 'market-etf',
            component: () => import('@/views/artdeco-pages/market-tabs/MarketETFTab.vue'),
            meta: { title: 'ETF行情', requiresAuth: true, api: '/api/v1/market/etf' }
          },
          {
            path: 'concept',
            name: 'market-concept',
            component: () => import('@/views/artdeco-pages/market-tabs/MarketConceptTab.vue'),
            meta: { title: '概念板块', requiresAuth: true, api: '/api/v1/market/concept' }
          }
        ]
      },

      // 3. Technical Analysis
      {
        path: 'technical',
        redirect: '/technical/indicators',
        children: [
          {
            path: 'indicators',
            name: 'technical-indicators',
            component: () => import('@/views/artdeco-pages/technical-tabs/TechnicalScannerTab.vue'),
            meta: { title: '技术指标', requiresAuth: true, api: '/api/v1/data/stocks' }
          },
          {
            path: 'analysis',
            name: 'technical-analysis',
            component: () => import('@/views/artdeco-pages/ArtDecoTechnicalAnalysis.vue'),
            meta: { title: '综合分析', requiresAuth: true, api: '/api/v1/market/analysis' }
          }
        ]
      },

      // 4. Strategy Domain
      {
        path: 'strategy',
        redirect: '/strategy/management',
        children: [
          {
            path: 'management',
            name: 'strategy-management',
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue'),
            meta: { title: '策略管理', requiresAuth: true, api: '/api/v1/strategy/list' }
          },
          {
            path: 'backtest',
            name: 'strategy-backtest',
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue'),
            meta: { title: '回测分析', requiresAuth: true, api: '/api/v1/strategy/backtest' }
          },
          {
            path: 'risk',
            name: 'strategy-risk',
            component: () => import('@/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue'),
            meta: { title: '策略参数', requiresAuth: true, api: '/api/v1/strategy/risk' }
          },
          {
            path: 'signals',
            name: 'strategy-signals',
            component: () => import('@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue'),
            alias: '/trading/signals', // 对齐菜单配置
            meta: { title: '信号监控', requiresAuth: true, api: '/api/v1/trade/signals' }
          }
        ]
      },

      // 5. Risk Management
      {
        path: 'risk',
        redirect: '/risk/overview',
        children: [
          {
            path: 'overview',
            name: 'risk-overview',
            component: () => import('@/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue'),
            meta: { title: '风险概览', requiresAuth: true, api: '/api/v1/risk/overview' }
          },
          {
            path: 'alerts',
            name: 'risk-alerts',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue'),
            meta: { title: '告警中心', requiresAuth: true, api: '/api/v1/risk/alerts' }
          },
          {
            path: 'announcement',
            name: 'risk-announcement',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue'),
            meta: { title: '公告监控', requiresAuth: true, api: '/api/v1/risk/announcement' }
          }
        ]
      },

      // 6. Monitoring (Stop-Loss)
      {
        path: 'monitoring',
        redirect: '/monitoring/watchlists',
        children: [
          {
            path: 'watchlists',
            name: 'risk-stop-loss',
            component: () => import('@/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue'),
            meta: { title: '止损监控', requiresAuth: true, api: '/api/v1/monitoring/watchlists' }
          }
        ]
      },

      // 7. Watchlist & Portfolio
      {
        path: 'stocks',
        redirect: '/stocks/management',
        children: [
          {
            path: 'management',
            name: 'watchlist-manage',
            component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
            alias: '/watchlist/manage', // 对齐菜单配置
            meta: { title: '自选管理', requiresAuth: true, api: '/api/v1/stock/list' }
          },
          {
            path: 'portfolio',
            name: 'watchlist-portfolio',
            component: () => import('@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue'),
            alias: ['/stocks/portfolio', '/trading/positions'], // 核心校准：支持两个路径
            meta: { title: '持仓透视', requiresAuth: true, api: '/api/v1/trade/positions' }
          }
        ]
      },

      // 8. System Management
      {
        path: 'system',
        redirect: '/system/monitoring',
        children: [
          {
            path: 'architecture',
            name: 'system-architecture',
            component: () => import('@/views/system/Architecture.vue'),
            meta: { title: '系统架构', requiresAuth: true }
          },
          {
            path: 'database-monitor',
            name: 'system-database-monitor',
            component: () => import('@/views/system/DatabaseMonitor.vue'),
            meta: { title: '数据库监控', requiresAuth: true }
          },
          {
            path: 'monitoring',
            name: 'system-monitoring',
            component: () => import('@/views/artdeco-pages/system-tabs/SystemHealthTab.vue'),
            meta: { title: '运维监控', requiresAuth: true, api: '/health' }
          },
          {
            path: 'settings',
            name: 'system-config',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue'),
            meta: { title: '系统配置', requiresAuth: true }
          }
        ]
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Login', requiresAuth: false, layout: 'Blank' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Page Not Found', requiresAuth: false, layout: 'Blank' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - MyStocks` : 'MyStocks Platform'
  const authResult = await authGuard(to)
  if (authResult !== true) {
    next(authResult)
    return
  }
  next()
})

export default router
