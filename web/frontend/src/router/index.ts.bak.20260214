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
    activeTab?: string // 新增：用于 monolithic 组件内部 Tab 切换
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
      requiresAuth: true
    }
  },

  // ArtDeco 组件测试页面
  {
    path: '/artdeco/test',
    name: 'artdeco-test',
    component: () => import('@/views/ArtDecoTest.vue'),
    meta: {
      title: 'ArtDeco Component Test',
             requiresAuth: true
    }
  },
  {
    path: '/artdeco/skeleton-demo',
    name: 'artdeco-skeleton-demo',
    component: () => import('@/views/SkeletonUsage.vue'),
    meta: {
      title: 'Skeleton Demo',
      requiresAuth: true
    }
  },

  // ========== 公开路由 ==========
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: 'Login',
      requiresAuth: false  // 🔒 安全关键：公开页面不能要求认证，否则死循环
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
           path: 'dashboard',
           name: 'dashboard',
           component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
           meta: {
             title: '仪表盘',
             requiresAuth: true
           }
         }
      ]
    },

    // ArtDeco Market域 - 市场行情 (核心 8 页面)
    {
      path: '/market',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/market/realtime',
      children: [
       {
         path: 'realtime',
         name: 'market-realtime',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'),
          meta: {
            title: '实时行情',
            breadcrumb: 'Market > Realtime',
            requiresAuth: true,
            activeTab: 'realtime'
          }
       },
       {
         path: 'overview',
         name: 'market-overview',
         component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoMarketOverview.vue'),
         meta: {
           title: '市场概览',
           breadcrumb: 'Market > Overview',
           requiresAuth: true
         }
       },
       {
         path: 'analysis',
         name: 'market-analysis',
         component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoMarketAnalysis.vue'),
         meta: {
           title: '市场分析',
           breadcrumb: 'Market > Analysis',
           requiresAuth: true
         }
       },
       {
         path: 'industry',
         name: 'market-industry',
         component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue'),
         meta: {
           title: '行业分析',
           breadcrumb: 'Market > Industry',
           requiresAuth: true
         }
       },
       {
         path: 'technical',
         name: 'market-technical',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'),
         meta: {
           title: '技术指标',
           breadcrumb: 'Market > Technical',
           requiresAuth: true,
           activeTab: 'technical'
         }
       },
       {
         path: 'fund-flow',
         name: 'market-fund-flow',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: '资金流向',
           breadcrumb: 'Market > Fund Flow',
           requiresAuth: true,
           activeTab: 'fund-flow'
         }
       },
       {
         path: 'etf',
         name: 'market-etf',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: 'ETF行情',
           breadcrumb: 'Market > ETF',
           requiresAuth: true,
           activeTab: 'etf'
         }
       },
       {
         path: 'concept',
         name: 'market-concept',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: '概念板块',
           breadcrumb: 'Market > Concept',
           requiresAuth: true,
           activeTab: 'concepts'
         }
       },
       {
         path: 'auction',
         name: 'market-auction',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: '竞价抢筹',
           breadcrumb: 'Market > Auction',
           requiresAuth: true,
           activeTab: 'auction'
         }
       },
       {
         path: 'longhubang',
         name: 'market-longhubang',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: '龙虎榜',
           breadcrumb: 'Market > LHB',
           requiresAuth: true,
           activeTab: 'lhb'
         }
       },
       {
         path: 'institution',
         name: 'market-institution',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: '机构荐股',
           breadcrumb: 'Market > Institution',
           requiresAuth: true,
           activeTab: 'institution'
         }
       },
       {
         path: 'wencai',
         name: 'market-wencai',
         component: () => import('@/views/artdeco-pages/ArtDecoMarketData.vue'),
         meta: {
           title: '问财选股',
           breadcrumb: 'Market > Wencai',
           requiresAuth: true,
           activeTab: 'wencai'
         }
       },
       {
         path: 'screener',
         name: 'market-screener',
         component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
         meta: {
           title: '股票筛选',
           breadcrumb: 'Market > Screener',
           requiresAuth: true,
           activeTab: 'strategy'
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
           requiresAuth: true,
           activeTab: 'watchlist'
         }
       },
       {
         path: 'portfolio',
         name: 'stock-portfolio',
         component: () => import('@/views/artdeco-pages/ArtDecoStockManagement.vue'),
         meta: {
           title: '我的持仓',
           requiresAuth: true,
           activeTab: 'watchlist'
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
         component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingSignals.vue'),
         meta: {
           title: '交易信号',
           requiresAuth: true,
           activeTab: 'signals'
         }
       },
       {
         path: 'history',
         name: 'trading-history',
         component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue'),
         meta: {
           title: '历史订单',
           requiresAuth: true,
           activeTab: 'history'
         }
       },
       {
         path: 'positions',
         name: 'trading-positions',
         component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'),
         meta: {
           title: '持仓监控',
           requiresAuth: true,
           activeTab: 'positions'
         }
       },
       {
         path: 'performance',
         name: 'trading-performance',
         component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoPerformanceAnalysis.vue'),
         meta: {
           title: '绩效分析',
           requiresAuth: true,
           activeTab: 'performance'
         }
       },
       {
         path: 'attribution',
         name: 'trading-attribution',
         component: () => import('@/views/artdeco-pages/components/ArtDecoAttributionAnalysis.vue'),
         meta: {
           title: '绩效归因',
           requiresAuth: true,
           activeTab: 'attribution'
         }
       }
     ]
   },

    // ArtDeco Strategy域 - 策略中心
    {
      path: '/strategy',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/strategy/management',
     children: [
       {
         path: 'design',
         name: 'strategy-design',
         component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue'), // Placeholder
         meta: {
           title: '策略设计',
           requiresAuth: true,
         }
       },
       {
         path: 'management',
         name: 'strategy-management',
         component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue'),
         meta: {
           title: '策略管理',
           requiresAuth: true,
         }
       },
       {
         path: 'backtest',
         name: 'strategy-backtest',
         component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue'),
         meta: {
           title: '策略回测',
           requiresAuth: true,
         }
       },
       {
         path: 'gpu-backtest',
         name: 'strategy-gpu-backtest',
         component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue'), // Placeholder
         meta: {
           title: 'GPU加速回测',
           requiresAuth: true,
         }
       },
       {
         path: 'optimization',
         name: 'strategy-optimization',
         component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue'),
         meta: {
           title: '参数优化',
           requiresAuth: true,
         }
       },
       // Legacy strategy routes now redirected to trading domain
       {
         path: 'strategy-mgmt',
         redirect: '/strategy/management'
       },
       {
         path: 'signals',
         redirect: '/trading/signals'
       },
       {
         path: 'history',
         redirect: '/trading/history'
       },
       {
         path: 'position',
         redirect: '/trading/positions'
       },
       {
         path: 'positions',
         redirect: '/trading/positions'
       },
       {
         path: 'performance',
         redirect: '/trading/performance'
       },
       {
         path: 'attribution',
         redirect: '/trading/attribution'
       }
     ]
   },

    // ArtDeco Risk域 - 风险控制
    {
      path: '/risk',
      component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
      redirect: '/risk/overview',
      children: [
        {
          path: 'overview',
          name: 'risk-overview',
          component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'), // Placeholder
          meta: {
            title: '风险概览',
            requiresAuth: true,
          }
        },
        {
          path: 'alerts',
          name: 'risk-alerts',
          component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'), // Placeholder
          meta: {
            title: '告警中心',
            requiresAuth: true,
          }
        },
        {
          path: 'indicators',
          name: 'risk-indicators',
          component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'), // Placeholder
          meta: {
            title: '风险指标',
            requiresAuth: true,
          }
        },
        {
          path: 'sentiment',
          name: 'risk-sentiment',
          component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'), // Placeholder
          meta: {
            title: '舆情监控',
            requiresAuth: true,
          }
        },
        {
          path: 'announcement',
          name: 'risk-announcement',
          component: () => import('@/views/artdeco-pages/ArtDecoMarketQuotes.vue'), // Placeholder
          meta: {
            title: '公告监控',
            requiresAuth: true,
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
         component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'),
         meta: {
           title: '运维监控',
           requiresAuth: true,
         }
       },
       {
         path: 'settings',
         name: 'system-settings',
         component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue'),
         meta: {
           title: '系统设置',
           requiresAuth: true,
         }
       },
       {
         path: 'data-update',
         name: 'system-data-update',
         component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'),
         meta: {
           title: '数据更新',
           requiresAuth: true,
         }
       },
       {
         path: 'data-quality',
         name: 'system-data-quality',
         component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'),
         meta: {
           title: '数据质量',
           requiresAuth: true,
         }
       },
       {
         path: 'api-health',
         name: 'system-api-health',
         component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'), // Placeholder
         meta: {
           title: 'API 健康',
           requiresAuth: true,
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



  // ========== 404 Not Found ==========
  {
    path: '/:pathMatch(.*)*',
    name: 'notFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { title: 'Not Found' }
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

// 导航守卫 - 认证检查和页面标题更新
import { authGuard } from './guards'

router.beforeEach(async (to, from, next) => {
  // 先执行认证检查
  const authResult = await authGuard(to)
  if (authResult !== true) {
    next(authResult)
    return
  }

  // 更新页面标题
  const title = to.meta.title || 'MyStocks'
  document.title = `${title} - MyStocks Platform`
  next()
})

export default router
