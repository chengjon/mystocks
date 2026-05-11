import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import { authGuard } from './guards'
import { HOME_ROUTE_NAME, HOME_ROUTE_PATH, LEGACY_HOME_ROUTE_PATH } from './homeRoute'

/**
 * MyStocks Frontend Router - V3.2 Elite
 * Architecture Aligned Navigation & Deep Linking
 */

declare module 'vue-router' {
  interface RouteMeta {
    title: string
    requiresAuth?: boolean
    icon?: string
    api?: string
    layout?: 'ArtDeco' | 'Blank'
    isDetail?: boolean
    group?: string
    permission?: string
    permissions?: string[]
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
    redirect: HOME_ROUTE_PATH,
    children: [
      // 0. Dashboard / Trading Room (The Soul of the System)
      {
        path: 'dashboard',
        name: HOME_ROUTE_NAME,
        component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
        meta: { title: '交易室', requiresAuth: true, api: '/api/v1/market/quotes' }
      },

      // 1. Market Domain (市场行情)
      {
        path: 'market',
        redirect: '/market/realtime',
        meta: { title: '市场行情', group: 'market' },
        children: [
          {
            path: 'realtime',
            name: 'market-realtime',
            component: () => import('@/views/market/Realtime.vue'),
            meta: { title: '实时行情', requiresAuth: true, api: '/api/v1/market/quotes' }
          },
          {
            path: 'technical',
            name: 'market-technical',
            component: () => import('@/views/market/Technical.vue'),
            meta: { title: 'K线分析', requiresAuth: true, api: '/api/v1/market/kline' }
          },
          {
            path: 'lhb',
            name: 'market-lhb',
            component: () => import('@/views/market/LHB.vue'),
            meta: { title: '龙虎榜', requiresAuth: true, api: '/api/v2/market/lhb' }
          }
        ]
      },

      // 2. Data Analysis (数据分析)
      {
        path: 'data',
        redirect: '/data/industry',
        meta: { title: '数据分析', group: 'data' },
        children: [
          {
            path: 'industry',
            name: 'data-industry',
            component: () => import('@/views/data/Industry.vue'),
            meta: { title: '板块动向', requiresAuth: true, api: '/api/v2/market/sector/fund-flow?sector_type=行业' }
          },
          {
            path: 'concept',
            name: 'data-concept',
            component: () => import('@/views/data/Concepts.vue'),
            meta: { title: '概念动向', requiresAuth: true, api: '/api/v2/market/sector/fund-flow?sector_type=概念' }
          },
          {
            path: 'fund-flow',
            name: 'data-fund-flow',
            component: () => import('@/views/data/FundFlow.vue'),
            meta: { title: '资金流向', requiresAuth: true, api: '/api/akshare/market/fund-flow/hsgt-summary' }
          },
          {
            path: 'indicator',
            name: 'data-indicator',
            component: () => import('@/views/data/Advanced.vue'),
            meta: { title: '指标分析', requiresAuth: true, api: '/api/v1/indicators/registry' }
          }
        ]
      },

      // 3. Watchlist (自选管理)
      {
        path: 'watchlist',
        redirect: '/watchlist/manage',
        meta: { title: '自选管理', group: 'watchlist' },
        children: [
          {
            path: 'manage',
            name: 'watchlist-manage',
            component: () => import('@/views/watchlist/Manage.vue'),
            meta: { title: '组合管理', requiresAuth: true, api: '/api/v1/monitoring/watchlists' }
          },
          {
            path: 'signals',
            name: 'watchlist-signals',
            component: () => import('@/views/watchlist/Signals.vue'),
            meta: { title: '信号雷达', requiresAuth: true, api: '/api/v1/trade/signals' }
          },
          {
            path: 'screener',
            name: 'watchlist-screener',
            component: () => import('@/views/watchlist/Screener.vue'),
            meta: { title: '策略选股', requiresAuth: true, api: '/api/v1/data/stocks/basic' }
          }
        ]
      },

      // 4. Strategy (策略管理)
      {
        path: 'strategy',
        redirect: '/strategy/repo',
        meta: { title: '策略管理', group: 'strategy' },
        children: [
          {
            path: 'repo',
            name: 'strategy-repo',
            component: () => import('@/views/strategy/List.vue'),
            meta: { title: '策略仓库', requiresAuth: true, api: '/api/v1/strategy/strategies' }
          },
          {
            path: 'parameters',
            name: 'strategy-parameters',
            component: () => import('@/views/strategy/Parameters.vue'),
            meta: { title: '策略参数', requiresAuth: true, api: '/api/v1/strategy/strategies' }
          },
          {
            path: 'signals',
            name: 'strategy-signals',
            component: () => import('@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue'),
            meta: { title: '策略信号', requiresAuth: true, api: '/api/v1/trade/signals' }
          },
          {
            path: 'backtest',
            name: 'strategy-backtest',
            component: () => import('@/views/strategy/Backtest.vue'),
            meta: { title: '回测引擎', requiresAuth: true, api: '/api/v1/strategy/strategies' }
          },
          {
            path: 'gpu',
            name: 'strategy-gpu',
            component: () => import('@/views/strategy/BacktestGPU.vue'),
            meta: { title: '加速监控', requiresAuth: true }
          },
          {
            path: 'opt',
            name: 'strategy-opt',
            component: () => import('@/views/strategy/Optimization.vue'),
            meta: { title: '参数优化', requiresAuth: true }
          },
          {
            path: 'pos',
            name: 'strategy-pos',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'),
            meta: { title: '仓位管理', requiresAuth: true, api: '/api/v1/trade/positions' }
          }
        ]
      },

      // 5. AI (高级分析与AI)
      {
        path: 'ai',
        redirect: '/ai/sentiment',
        meta: { title: 'AI 分析', group: 'ai' },
        children: [
          {
            path: 'sentiment',
            name: 'ai-sentiment',
            component: () => import('@/views/ai/Sentiment.vue'),
            meta: { title: '情感分析', requiresAuth: true, api: '/api/v1/sentiment/market' }
          },
          {
            path: 'ml',
            name: 'ai-ml',
            component: () => import('@/views/ai/MlWorkbench.vue'),
            meta: { title: '模型训练 / 预测', requiresAuth: true, api: '/api/v1/strategies/ml/runtime-status' }
          },
          {
            path: 'batch',
            name: 'ai-batch',
            component: () => import('@/views/ai/BatchAnalysis.vue'),
            meta: { title: '批量分析', requiresAuth: true, api: '/api/v1/strategies/batch-analysis/runtime-status' }
          }
        ]
      },

      // 6. Trade (交易管理)
      {
        path: 'trade',
        redirect: '/trade/terminal',
        meta: { title: '交易管理', group: 'trade' },
        children: [
          {
            path: 'positions',
            name: 'trade-positions',
            component: () => import('@/views/trade/Center.vue'),
            meta: { title: '头寸管理', requiresAuth: true }
          },
          {
            path: 'terminal',
            name: 'trade-terminal',
            component: () => import('@/views/TradingDashboard.vue'),
            meta: { title: '交易操作', requiresAuth: true }
          },
          {
            path: 'execution',
            name: 'trade-execution',
            component: () => import('@/views/trade/Execution.vue'),
            meta: { title: '执行跟踪', requiresAuth: true, api: '/api/v1/trade/execution-tracking' }
          },
          {
            path: 'signals',
            name: 'trade-signals',
            component: () => import('@/views/trade/Signals.vue'),
            meta: { title: '信号监控', requiresAuth: true }
          },
          {
            path: 'portfolio',
            name: 'trade-portfolio',
            component: () => import('@/views/trade/Portfolio.vue'),
            meta: { title: '持仓透视', requiresAuth: true }
          },
          {
            path: 'history',
            name: 'trade-history',
            component: () => import('@/views/trade/History.vue'),
            meta: { title: '交易历史', requiresAuth: true }
          },
          {
            path: 'reconciliation',
            name: 'trade-reconciliation',
            component: () => import('@/views/trade/Reconciliation.vue'),
            meta: { title: '对账单', requiresAuth: true, api: '/api/v1/trade/reconciliation/accounts' }
          }
        ]
      },

      // 7. Risk (风险管理)
      {
        path: 'risk',
        redirect: '/risk/overview',
        meta: { title: '风险管理', group: 'risk' },
        children: [
          {
            path: 'management',
            alias: ['/risk-management'],
            name: 'risk-management',
            component: () => import('@/views/risk/Center.vue'),
            meta: { title: '风险管理中心', requiresAuth: true }
          },
          {
            path: 'overview',
            name: 'risk-overview',
            component: () => import('@/views/risk/Overview.vue'),
            meta: { title: '风险概览', requiresAuth: true }
          },
          {
            path: 'pnl',
            name: 'risk-pnl',
            component: () => import('@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue'),
            meta: { title: '组合盈亏', requiresAuth: true }
          },
          {
            path: 'stop-loss',
            name: 'risk-stop-loss',
            component: () => import('@/views/risk/StopLoss.vue'),
            meta: { title: '止损雷达', requiresAuth: true }
          },
          {
            path: 'alerts',
            name: 'risk-alerts',
            component: () => import('@/views/risk/Alerts.vue'),
            meta: { title: '告警中心', requiresAuth: true }
          },
          {
            path: 'news',
            name: 'risk-news',
            component: () => import('@/views/risk/News.vue'),
            meta: { title: '舆情预警', requiresAuth: true }
          }
        ]
      },

      // 8. System (系统设置)
      {
        path: 'system',
        redirect: '/system/config',
        meta: { title: '系统设置', group: 'system' },
        children: [
          {
            path: 'config',
            name: 'system-config',
            component: () => import('@/views/system/Settings.vue'),
            meta: { title: '系统配置', requiresAuth: true }
          },
          {
            path: 'health',
            name: 'system-health',
            component: () => import('@/views/system/Health.vue'),
            meta: { title: '健康矩阵', requiresAuth: true }
          },
          {
            path: 'api',
            name: 'system-api',
            component: () => import('@/views/system/API.vue'),
            meta: { title: 'API 终端', requiresAuth: true, api: '/api/health' }
          },
          {
            path: 'resources',
            name: 'system-resources',
            component: () => import('@/views/system/Resources.vue'),
            meta: { title: '资源使用', requiresAuth: true, api: '/api/v1/system/resources' }
          },
          {
            path: 'data',
            name: 'system-data',
            component: () => import('@/views/system/DataSource.vue'),
            meta: { title: '数据源管理', requiresAuth: true }
          }
        ]
      },

      // Detail Pages (Details Groups - 同标准、同规则)
      {
        path: 'detail',
        meta: { title: '详情页', isDetail: true },
        children: [
          {
            path: 'graphics/:symbol',
            name: 'stock-graphics',
            component: () => import('@/views/artdeco-pages/analysis-tabs/KLineAnalysis.vue'),
            meta: { title: '股票图形', requiresAuth: true }
          },
          {
            path: 'news/:symbol',
            name: 'stock-news',
            component: () => import('@/views/announcement/AnnouncementMonitor.vue'),
            meta: { title: '相关新闻', requiresAuth: true }
          }
        ]
      }
    ]
  },
  {
    path: LEGACY_HOME_ROUTE_PATH,
    redirect: HOME_ROUTE_PATH
  },
  {
    path: '/qm',
    redirect: HOME_ROUTE_PATH
  },
  {
    path: '/qm/:pathMatch(.*)*',
    redirect: (to) => {
      const pathMatch = to.params.pathMatch
      const normalized = Array.isArray(pathMatch) ? pathMatch.join('/') : pathMatch
      return {
        path: normalized ? `/${normalized}` : '/',
        query: to.query,
        hash: to.hash
      }
    }
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
  scrollBehavior(_to, _from, savedPosition) {
    return savedPosition || { top: 0 }
  }
})

router.beforeEach((to, _from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - MyStocks` : 'MyStocks Platform'
  const authResult = authGuard(to)
  if (authResult !== true) {
    next(authResult)
    return
  }
  next()
})

export default router
