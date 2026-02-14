import { createRouter, createWebHistory, createWebHashHistory, type RouteRecordRaw } from 'vue-router'
import { authGuard } from './guards'

/**
 * MyStocks Frontend Router Configuration (Refactored 2026-02-14)
 * Based on 'Core 48' Route List - Vertical Slicing Strategy
 * 
 * Features:
 * - Dynamic Lazy Loading (Code Splitting)
 * - ArtDeco Layout Integration
 * - API Contract Alignment
 * - Unified Error Handling
 */

// Extend RouteMeta for TypeScript
declare module 'vue-router' {
  interface RouteMeta {
    title: string
    requiresAuth?: boolean
    icon?: string
    api?: string // Associated Backend API Endpoint
    layout?: 'ArtDeco' | 'Blank' // Layout Strategy
  }
}

const routes: RouteRecordRaw[] = [
  // =================================================================
  // 1. Core Layout Container (ArtDeco)
  // =================================================================
  {
    path: '/',
    component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
    redirect: '/dashboard',
    children: [
      // 1.1 Dashboard (1)
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
        meta: { 
          title: '指挥中心', 
          requiresAuth: true,
          api: '/api/v1/market/overview'
        }
      },

      // 1.2 Market Domain (13)
      {
        path: 'market',
        redirect: '/market/realtime',
        children: [
          {
            path: 'realtime',
            name: 'market-realtime',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'),
            meta: { title: '实时行情', requiresAuth: true, api: '/api/v1/market/quotes' }
          },
          {
            path: 'overview',
            name: 'market-overview',
            component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue'),
            meta: { title: '市场概览', requiresAuth: true, api: '/api/v1/market/overview' }
          },
          {
            path: 'analysis',
            name: 'market-analysis',
            component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue'),
            meta: { title: '市场分析', requiresAuth: true, api: '/api/v1/market/analysis' }
          },
          {
            path: 'industry',
            name: 'market-industry',
            component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue'),
            meta: { title: '行业分析', requiresAuth: true, api: '/api/v1/market/industry' }
          },
          {
            path: 'technical',
            name: 'market-technical',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'), // Reuse for technical view
            meta: { title: '技术指标', requiresAuth: true, api: '/api/v1/market/technical' }
          },
          {
            path: 'fund-flow',
            name: 'market-fund-flow',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '资金流向', requiresAuth: true, api: '/api/v1/market/fund-flow' }
          },
          {
            path: 'etf',
            name: 'market-etf',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: 'ETF行情', requiresAuth: true, api: '/api/v1/market/etf' }
          },
          {
            path: 'concept',
            name: 'market-concept',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '概念板块', requiresAuth: true, api: '/api/v1/market/concept' }
          },
          {
            path: 'auction',
            name: 'market-auction',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '竞价抢筹', requiresAuth: true, api: '/api/v1/market/auction' }
          },
          {
            path: 'longhubang',
            name: 'market-longhubang',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '龙虎榜', requiresAuth: true, api: '/api/v1/market/dragon-tiger' }
          },
          {
            path: 'institution',
            name: 'market-institution',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '机构调研', requiresAuth: true, api: '/api/v1/market/institution' }
          },
          {
            path: 'wencai',
            name: 'market-wencai',
            component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
            meta: { title: '问财选股', requiresAuth: true, api: '/api/v1/market/wencai' }
          },
          {
            path: 'screener',
            name: 'market-screener',
            component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
            meta: { title: '股票筛选', requiresAuth: true, api: '/api/v1/market/screener' }
          }
        ]
      },

      // 1.3 Stocks Domain (2)
      {
        path: 'stocks',
        redirect: '/stocks/management',
        children: [
          {
            path: 'management',
            name: 'stock-management',
            component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
            meta: { title: '股票管理', requiresAuth: true, api: '/api/v1/stock/list' }
          },
          {
            path: 'portfolio',
            name: 'stock-portfolio',
            component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
            meta: { title: '我的持仓', requiresAuth: true, api: '/api/v1/trade/positions' }
          }
        ]
      },

      // 1.4 Trading Domain (5)
      {
        path: 'trading',
        redirect: '/trading/signals',
        children: [
          {
            path: 'signals',
            name: 'trading-signals',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue'),
            meta: { title: '交易信号', requiresAuth: true, api: '/api/v1/trade/signals' }
          },
          {
            path: 'history',
            name: 'trading-history',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue'),
            meta: { title: '历史订单', requiresAuth: true, api: '/api/v1/trade/orders' }
          },
          {
            path: 'positions',
            name: 'trading-positions',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'),
            meta: { title: '持仓监控', requiresAuth: true, api: '/api/v1/trade/positions' }
          },
          {
            path: 'performance',
            name: 'trading-performance',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue'),
            meta: { title: '绩效分析', requiresAuth: true, api: '/api/v1/trade/performance' }
          },
          {
            path: 'attribution',
            name: 'trading-attribution',
            component: () => import('@/views/artdeco-pages/components/ArtDecoAttributionAnalysis.vue'),
            meta: { title: '绩效归因', requiresAuth: true, api: '/api/v1/trade/attribution' }
          }
        ]
      },

      // 1.5 Strategy Domain (5)
      {
        path: 'strategy',
        redirect: '/strategy/management',
        children: [
          {
            path: 'design',
            name: 'strategy-design',
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue'),
            meta: { title: '策略设计', requiresAuth: true, api: '/api/v1/strategy/design' }
          },
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
            meta: { title: '策略回测', requiresAuth: true, api: '/api/v1/strategy/backtest' }
          },
          {
            path: 'gpu-backtest',
            name: 'strategy-gpu-backtest',
            // 优化：指向高级批量分析视图，而非简单的回测页
            component: () => import('@/views/advanced-analysis/BatchAnalysisView.vue'),
            meta: { title: 'GPU加速回测', requiresAuth: true, api: '/api/v1/strategy/gpu-backtest' }
          },
          {
            path: 'optimization',
            name: 'strategy-optimization',
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue'),
            meta: { title: '参数优化', requiresAuth: true, api: '/api/v1/strategy/optimization' }
          }
        ]
      },

      // 1.6 Risk Domain (5) - 修复：替换占位符为真实组件
      {
        path: 'risk',
        redirect: '/risk/overview',
        children: [
          {
            path: 'overview',
            name: 'risk-overview',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoRiskMonitor.vue'),
            meta: { title: '风险概览', requiresAuth: true, api: '/api/v1/risk/overview' }
          },
          {
            path: 'alerts',
            name: 'risk-alerts',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue'),
            meta: { title: '告警中心', requiresAuth: true, api: '/api/v1/risk/alerts' }
          },
          {
            path: 'indicators',
            name: 'risk-indicators',
            // 优化：复用高级分析组件
            component: () => import('@/views/artdeco-pages/components/AnalysisIndicators.vue'),
            meta: { title: '风险指标', requiresAuth: true, api: '/api/v1/risk/indicators' }
          },
          {
            path: 'sentiment',
            name: 'risk-sentiment',
            // 优化：激活高级舆情分析视图
            component: () => import('@/views/advanced-analysis/SentimentAnalysisView.vue'),
            meta: { title: '舆情监控', requiresAuth: true, api: '/api/v1/risk/sentiment' }
          },
          {
            path: 'announcement',
            name: 'risk-announcement',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue'),
            meta: { title: '公告监控', requiresAuth: true, api: '/api/v1/risk/announcement' }
          }
        ]
      },

      // 1.7 Analysis Domain (New) - 激活高级分析视图
      {
        path: 'analysis',
        redirect: '/analysis/fundamental',
        children: [
          {
            path: 'fundamental',
            name: 'analysis-fundamental',
            component: () => import('@/views/advanced-analysis/FundamentalAnalysisView.vue'),
            meta: { title: '基本面分析', requiresAuth: true, api: '/api/v1/analysis/fundamental' }
          },
          {
            path: 'technical',
            name: 'analysis-technical',
            component: () => import('@/views/advanced-analysis/TechnicalAnalysisView.vue'),
            meta: { title: '高级技术分析', requiresAuth: true, api: '/api/v1/analysis/technical' }
          },
          {
            path: 'chip',
            name: 'analysis-chip',
            component: () => import('@/views/advanced-analysis/ChipDistributionView.vue'),
            meta: { title: '筹码分布', requiresAuth: true, api: '/api/v1/analysis/chip' }
          },
          {
            path: 'valuation',
            name: 'analysis-valuation',
            component: () => import('@/views/advanced-analysis/FinancialValuationView.vue'),
            meta: { title: '财务估值', requiresAuth: true, api: '/api/v1/analysis/valuation' }
          }
        ]
      },

      // 1.8 System Domain (5)
      {
        path: 'system',
        redirect: '/system/monitoring',
        children: [
          {
            path: 'monitoring',
            name: 'system-monitoring',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'),
            meta: { title: '运维监控', requiresAuth: true, api: '/api/v1/system/monitor' }
          },
          {
            path: 'settings',
            name: 'system-settings',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue'),
            meta: { title: '系统设置', requiresAuth: true, api: '/api/v1/system/settings' }
          },
          {
            path: 'data-update',
            name: 'system-data-update',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'),
            meta: { title: '数据更新', requiresAuth: true, api: '/api/v1/system/data-update' }
          },
          {
            path: 'data-quality',
            name: 'system-data-quality',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'),
            meta: { title: '数据质量', requiresAuth: true, api: '/api/v1/system/data-quality' }
          },
          {
            path: 'api-health',
            name: 'system-api-health',
            // 优化：复用监控面板
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'),
            meta: { title: 'API 健康', requiresAuth: true, api: '/api/v1/system/api-health' }
          }
        ]
      }
    ]
  },

  // =================================================================
  // 2. Authentication & Public
  // =================================================================
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: 'Login', requiresAuth: false, layout: 'Blank' }
  },

  // =================================================================
  // 3. Testing & Development
  // =================================================================
  {
    path: '/test',
    name: 'test',
    component: () => import('@/views/Test.vue'),
    meta: { title: 'Test Page', requiresAuth: true }
  },
  {
    path: '/artdeco/test',
    name: 'artdeco-test',
    component: () => import('@/views/ArtDecoTest.vue'),
    meta: { title: 'ArtDeco Test', requiresAuth: true }
  },
  {
    path: '/artdeco/skeleton-demo',
    name: 'artdeco-skeleton-demo',
    component: () => import('@/views/SkeletonUsage.vue'),
    meta: { title: 'Skeleton Demo', requiresAuth: true }
  },

  // =================================================================
  // 4. Fallback (404)
  // =================================================================
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Page Not Found', requiresAuth: false, layout: 'Blank' }
  }
]

// HTML5 History API Support Check
const supportsHistory = 'pushState' in window.history && 'replaceState' in window.history

const router = createRouter({
  history: supportsHistory 
    ? createWebHistory(import.meta.env.BASE_URL) 
    : createWebHashHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

// Global Navigation Guard
router.beforeEach(async (to, from, next) => {
  // Update Document Title
  const title = to.meta.title ? `${to.meta.title} - MyStocks` : 'MyStocks Platform'
  document.title = title

  // Auth Guard
  const authResult = await authGuard(to)
  if (authResult !== true) {
    next(authResult)
    return
  }
  next()
})

export default router
