import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: () => import('@/layout/index.vue'),
      redirect: '/dashboard',
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: () => import('@/views/Dashboard.vue'),
          meta: { title: '仪表盘', icon: 'Odometer' }
        },
        {
          path: 'market',
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
          path: 'market-data',
          name: 'market-data',
          redirect: '/market-data/fund-flow',
          meta: { title: '市场数据', icon: 'DataLine' }
        },
        {
          path: 'market-data/fund-flow',
          name: 'market-data-fund-flow',
          component: () => import('@/components/market/FundFlowPanel.vue'),
          meta: { title: '资金流向', icon: 'Money' }
        },
        {
          path: 'market-data/etf',
          name: 'market-data-etf',
          component: () => import('@/components/market/ETFDataTable.vue'),
          meta: { title: 'ETF行情', icon: 'TrendCharts' }
        },
        {
          path: 'market-data/chip-race',
          name: 'market-data-chip-race',
          component: () => import('@/components/market/ChipRaceTable.vue'),
          meta: { title: '竞价抢筹', icon: 'ShoppingCart' }
        },
        {
          path: 'market-data/lhb',
          name: 'market-data-lhb',
          component: () => import('@/components/market/LongHuBangTable.vue'),
          meta: { title: '龙虎榜', icon: 'Flag' }
        },
        {
          path: 'market-data/wencai',
          name: 'market-data-wencai',
          component: () => import('@/components/market/WencaiPanelV2.vue'),
          meta: { title: '问财筛选', icon: 'Search' }
        },
        {
          path: 'watchlist',
          name: 'watchlist',
          component: () => import('@/views/Watchlist.vue'),
          meta: { title: '自选股', icon: 'Grid' }
        },
        {
          path: 'analysis',
          name: 'analysis',
          component: () => import('@/views/Analysis.vue'),
          meta: { title: '数据分析', icon: 'DataAnalysis' }
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
          path: 'risk',
          name: 'risk',
          component: () => import('@/views/RiskMonitor.vue'),
          meta: { title: '风险监控', icon: 'Warning' }
        },
        {
          path: 'realtime',
          name: 'realtime',
          component: () => import('@/views/RealTimeMonitor.vue'),
          meta: { title: '实时监控', icon: 'Monitor' }
        },
        {
          path: 'trade',
          name: 'trade',
          component: () => import('@/views/TradeManagement.vue'),
          meta: { title: '交易管理', icon: 'Tickets' }
        },
        {
          path: 'strategy',
          name: 'strategy',
          component: () => import('@/views/StrategyManagement.vue'),
          meta: { title: '策略管理', icon: 'Management' }
        },
        {
          path: 'backtest',
          name: 'backtest',
          component: () => import('@/views/BacktestAnalysis.vue'),
          meta: { title: '回测分析', icon: 'Histogram' }
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
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'notFound',
      component: () => import('@/views/NotFound.vue')
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth !== false && !authStore.isAuthenticated) {
    // 需要登录但未登录,重定向到登录页
    next({ name: 'login', query: { redirect: to.fullPath } })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    // 已登录,访问登录页,重定向到首页
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
