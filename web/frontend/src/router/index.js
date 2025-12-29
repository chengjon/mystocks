import { createRouter, createWebHistory } from 'vue-router'
// import { useAuthStore } from '@/stores/auth'  // 已移除认证依赖

/**
 * MyStocks Frontend Router Configuration
 *
 * Layout Mapping:
 * - MainLayout: Dashboard, Analysis, Settings, and general pages
 * - MarketLayout: Market data pages (market, tdx-market, realtime)
 * - DataLayout: Market data analysis pages (fund-flow, etf, chip-race, longhubang, wencai)
 * - RiskLayout: Risk monitoring pages (risk, announcement)
 * - StrategyLayout: Strategy and backtesting pages (strategy, backtest, signals)
 *
 * Architecture: Nested routes with layout components as parents
 * Reference: openspec/changes/frontend-optimization-six-phase/design.md
 */

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },

    // ========== MainLayout Routes (仪表盘/分析/设置/通用页面) ==========
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
          meta: { title: '仪表盘', icon: 'Odometer' }
        },
        {
          path: 'analysis',
          name: 'analysis',
          component: () => import('@/views/Analysis.vue'),
          meta: { title: '数据分析', icon: 'DataAnalysis' }
        },
        {
          path: 'analysis/industry-concept',
          name: 'industry-concept-analysis',
          component: () => import('@/views/IndustryConceptAnalysis.vue'),
          meta: { title: '行业概念分析', icon: 'Box' }
        },
        {
          path: 'stocks',
          name: 'stocks',
          component: () => import('@/views/Stocks.vue'),
          meta: { title: '股票管理', icon: 'Grid' }
        },
        {
          path: 'stock-detail/:symbol',
          name: 'stock-detail',
          component: () => import('@/views/StockDetail.vue'),
          props: true,
          meta: { title: '股票详情', icon: 'Document' }
        },
        {
          path: 'technical',
          name: 'technical',
          component: () => import('@/views/TechnicalAnalysis.vue'),
          meta: { title: '技术分析', icon: 'DataLine' }
        },
        {
          path: 'indicators',
          name: 'indicators',
          component: () => import('@/views/IndicatorLibrary.vue'),
          meta: { title: '指标库', icon: 'Grid' }
        },
        {
          path: 'trade',
          name: 'trade',
          component: () => import('@/views/TradeManagement.vue'),
          meta: { title: '交易管理', icon: 'Tickets' }
        },
        {
          path: 'tasks',
          name: 'tasks',
          component: () => import('@/views/TaskManagement.vue'),
          meta: { title: '任务管理', icon: 'List' }
        },
        {
          path: 'settings',
          name: 'settings',
          component: () => import('@/views/Settings.vue'),
          meta: { title: '系统设置', icon: 'Setting' }
        },
        {
          path: 'system/architecture',
          name: 'system-architecture',
          component: () => import('@/views/system/Architecture.vue'),
          meta: { title: '系统架构', icon: 'Grid' }
        },
        {
          path: 'system/database-monitor',
          name: 'system-database-monitor',
          component: () => import('@/views/system/DatabaseMonitor.vue'),
          meta: { title: '数据库监控', icon: 'Database' }
        },
        {
          path: 'gpu-monitoring',
          name: 'gpu-monitoring',
          component: () => import('@/views/GPUMonitoring.vue'),
          meta: { title: 'GPU监控', icon: 'Monitor' }
        },
        // Demo pages
        {
          path: 'openstock-demo',
          name: 'openstock-demo',
          component: () => import('@/views/OpenStockDemo.vue'),
          meta: { title: 'OpenStock 功能演示', icon: 'Operation' }
        },
        {
          path: 'pyprofiling-demo',
          name: 'pyprofiling-demo',
          component: () => import('@/views/PyprofilingDemo.vue'),
          meta: { title: 'PyProfiling 功能演示', icon: 'DataAnalysis' }
        },
        {
          path: 'freqtrade-demo',
          name: 'freqtrade-demo',
          component: () => import('@/views/FreqtradeDemo.vue'),
          meta: { title: 'Freqtrade 功能演示', icon: 'TrendCharts' }
        },
        {
          path: 'stock-analysis-demo',
          name: 'stock-analysis-demo',
          component: () => import('@/views/StockAnalysisDemo.vue'),
          meta: { title: 'Stock-Analysis 功能演示', icon: 'DataAnalysis' }
        },
        {
          path: 'tdxpy-demo',
          name: 'tdxpy-demo',
          component: () => import('@/views/TdxpyDemo.vue'),
          meta: { title: 'pytdx 功能演示', icon: 'Connection' }
        },
        {
          path: 'smart-data-test',
          name: 'smart-data-test',
          component: () => import('@/views/SmartDataSourceTest.vue'),
          meta: { title: '智能数据源测试', icon: 'Monitor' }
        }
      ]
    },

    // ========== MarketLayout Routes (市场行情/TDX行情/实时监控) ==========
    {
      path: '/market',
      component: () => import('@/layouts/MarketLayout.vue'),
      redirect: '/market/list',
      meta: { requiresAuth: false },
      children: [
        {
          path: 'list',
          name: 'market',
          component: () => import('@/views/Market.vue'),
          meta: { title: '市场行情', icon: 'TrendCharts' }
        },
        {
          path: 'tdx-market',
          name: 'tdx-market',
          component: () => import('@/views/TdxMarket.vue'),
          meta: { title: 'TDX行情', icon: 'TrendCharts' }
        },
        {
          path: 'realtime',
          name: 'realtime',
          component: () => import('@/views/RealTimeMonitor.vue'),
          meta: { title: '实时监控', icon: 'Monitor' }
        }
      ]
    },

    // ========== DataLayout Routes (市场数据分析/资金流向/ETF/龙虎榜等) ==========
    {
      path: '/market-data',
      component: () => import('@/layouts/DataLayout.vue'),
      redirect: '/market-data/fund-flow',
      meta: { requiresAuth: false, title: '市场数据', icon: 'DataLine' },
      children: [
        {
          path: 'fund-flow',
          name: 'market-data-fund-flow',
          component: () => import('@/components/market/FundFlowPanel.vue'),
          meta: { title: '资金流向', icon: 'Money' }
        },
        {
          path: 'etf',
          name: 'market-data-etf',
          component: () => import('@/components/market/ETFDataTable.vue'),
          meta: { title: 'ETF行情', icon: 'TrendCharts' }
        },
        {
          path: 'chip-race',
          name: 'market-data-chip-race',
          component: () => import('@/components/market/ChipRaceTable.vue'),
          meta: { title: '竞价抢筹', icon: 'ShoppingCart' }
        },
        {
          path: 'lhb',
          name: 'market-data-lhb',
          component: () => import('@/components/market/LongHuBangTable.vue'),
          meta: { title: '龙虎榜', icon: 'Flag' }
        },
        {
          path: 'wencai',
          name: 'market-data-wencai',
          component: () => import('@/components/market/WencaiPanelV2.vue'),
          meta: { title: '问财筛选', icon: 'Search' }
        }
      ]
    },

    // ========== RiskLayout Routes (风险监控/公告监控) ==========
    {
      path: '/risk-monitor',
      component: () => import('@/layouts/RiskLayout.vue'),
      redirect: '/risk-monitor/overview',
      meta: { requiresAuth: false, title: '风险监控', icon: 'Warning' },
      children: [
        {
          path: 'overview',
          name: 'risk',
          component: () => import('@/views/RiskMonitor.vue'),
          meta: { title: '风险监控', icon: 'Warning' }
        },
        {
          path: 'announcement',
          name: 'announcement',
          component: () => import('@/views/announcement/AnnouncementMonitor.vue'),
          meta: { title: '公告监控', icon: 'Document' }
        }
      ]
    },

    // ========== StrategyLayout Routes (策略管理/回测分析/交易信号) ==========
    {
      path: '/strategy-hub',
      component: () => import('@/layouts/StrategyLayout.vue'),
      redirect: '/strategy-hub/management',
      meta: { requiresAuth: false, title: '策略中心', icon: 'Management' },
      children: [
        {
          path: 'management',
          name: 'strategy',
          component: () => import('@/views/StrategyManagement.vue'),
          meta: { title: '策略管理', icon: 'Management' }
        },
        {
          path: 'backtest',
          name: 'backtest',
          component: () => import('@/views/BacktestAnalysis.vue'),
          meta: { title: '回测分析', icon: 'Histogram' }
        }
      ]
    },

    // 404 Not Found
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// 路由守卫 - 已禁用认证检查
// router.beforeEach(async (to, from, next) => {
//   const authStore = useAuthStore()

//   if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
//     // 需要登录但未登录,重定向到登录页
//     next({ name: 'login', query: { redirect: to.fullPath } })
//   } else if (to.name === 'login' && authStore.isAuthenticated) {
//     // 已登录,访问登录页,重定向到首页
//     next({ name: 'dashboard' })
//   } else {
//     next()
//   }
// })

export default router
