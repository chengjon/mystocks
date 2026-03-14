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
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: () => import('@/layouts/ArtDecoLayoutEnhanced.vue'),
    redirect: HOME_ROUTE_PATH,
    children: [
      // 0. Dealing Room (The Soul of the System)
      {
        path: 'dashboard',
        name: HOME_ROUTE_NAME,
        component: () => import('@/views/artdeco-pages/ArtDecoDashboard.vue'),
        meta: { title: '交易室', requiresAuth: true, api: '/api/v1/market/overview' }
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
            component: () => import('@/views/artdeco-pages/market-tabs/MarketRealtimeTab.vue'),
            meta: { title: '实时行情', requiresAuth: true, api: '/api/v1/market/quotes' }
          },
          {
            path: 'technical',
            name: 'market-technical',
            component: () => import('@/views/artdeco-pages/market-tabs/MarketKLineTab.vue'),
            meta: { title: 'K线分析', requiresAuth: true, api: '/api/v1/market/kline' }
          },
          {
            path: 'lhb',
            name: 'market-lhb',
            component: () => import('@/views/artdeco-pages/market-data-tabs/DragonTigerAnalysis.vue'),
            meta: { title: '龙虎榜', requiresAuth: true, api: '/api/data/lhb' }
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
            component: () => import('@/views/artdeco-pages/market-data-tabs/ArtDecoIndustryAnalysis.vue'),
            meta: { title: '板块动向', requiresAuth: true, api: '/api/akshare_market/boards' }
          },
          {
            path: 'concept',
            name: 'data-concept',
            component: () => import('@/views/artdeco-pages/market-tabs/MarketConceptTab.vue'),
            meta: { title: '概念动向', requiresAuth: true, api: '/api/akshare_market/boards' }
          },
          {
            path: 'fund-flow',
            name: 'data-fund-flow',
            component: () => import('@/views/artdeco-pages/market-data-tabs/FundFlowAnalysis.vue'),
            meta: { title: '资金流向', requiresAuth: true, api: '/api/akshare_market/fund_flow' }
          },
          {
            path: 'indicator',
            name: 'data-indicator',
            component: () => import('@/views/artdeco-pages/ArtDecoDataAnalysis.vue'),
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
            component: () => import('@/views/artdeco-pages/stock-management-tabs/WatchlistManager.vue'),
            meta: { title: '组合管理', requiresAuth: true, api: '/api/watchlist' }
          },
          {
            path: 'signals',
            name: 'watchlist-signals',
            component: () => import('@/views/artdeco-pages/strategy-tabs/StrategySignalsTab.vue'),
            meta: { title: '信号雷达', requiresAuth: true, api: '/api/v1/trade/signals' }
          },
          {
            path: 'screener',
            name: 'watchlist-screener',
            component: () => import('@/views/stocks/Screener.vue'),
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
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyManagement.vue'),
            meta: { title: '策略仓库', requiresAuth: true, api: '/api/v1/strategy/list' }
          },
          {
            path: 'parameters',
            name: 'strategy-parameters',
            component: () => import('@/views/artdeco-pages/strategy-tabs/StrategyParametersTab.vue'),
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
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoBacktestAnalysis.vue'),
            meta: { title: '回测引擎', requiresAuth: true, api: '/api/v1/strategy/backtest' }
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
            component: () => import('@/views/artdeco-pages/strategy-tabs/ArtDecoStrategyOptimization.vue'),
            meta: { title: '参数优化', requiresAuth: true }
          },
          {
            path: 'pos',
            name: 'strategy-pos',
            component: () => import('@/views/artdeco-pages/stock-management-tabs/PortfolioMonitor.vue'),
            meta: { title: '仓位管理', requiresAuth: true }
          }
        ]
      },

      // 5. Trade (交易管理)
      {
        path: 'trade',
        redirect: '/trade/terminal',
        meta: { title: '交易管理', group: 'trade' },
        children: [
          {
            path: 'positions',
            name: 'trade-positions',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingPositions.vue'),
            meta: { title: '头寸管理', requiresAuth: true }
          },
          {
            path: 'terminal',
            name: 'trade-terminal',
            component: () => import('@/views/TradingDashboard.vue'),
            meta: { title: '交易操作', requiresAuth: true }
          },
          {
            path: 'signals',
            name: 'trade-signals',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoSignalsView.vue'),
            meta: { title: '信号监控', requiresAuth: true }
          },
          {
            path: 'portfolio',
            name: 'trade-portfolio',
            component: () => import('@/views/artdeco-pages/portfolio-tabs/PortfolioOverviewTab.vue'),
            meta: { title: '持仓透视', requiresAuth: true }
          },
          {
            path: 'history',
            name: 'trade-history',
            component: () => import('@/views/artdeco-pages/trading-tabs/ArtDecoTradingHistory.vue'),
            meta: { title: '历史对账', requiresAuth: true }
          }
        ]
      },

      // 6. Risk (风险管理)
      {
        path: 'risk',
        redirect: '/risk/overview',
        meta: { title: '风险管理', group: 'risk' },
        children: [
          {
            path: 'management',
            alias: ['/risk-management'],
            name: 'risk-management',
            component: () => import('@/views/artdeco-pages/ArtDecoRiskManagement.vue'),
            meta: { title: '风险管理中心', requiresAuth: true }
          },
          {
            path: 'overview',
            name: 'risk-overview',
            component: () => import('@/views/artdeco-pages/risk-tabs/RiskOverviewTab.vue'),
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
            component: () => import('@/views/artdeco-pages/risk-tabs/StopLossMonitorTab.vue'),
            meta: { title: '止损雷达', requiresAuth: true }
          },
          {
            path: 'alerts',
            name: 'risk-alerts',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoRiskAlerts.vue'),
            meta: { title: '告警中心', requiresAuth: true }
          },
          {
            path: 'news',
            name: 'risk-news',
            component: () => import('@/views/artdeco-pages/risk-tabs/ArtDecoAnnouncementMonitor.vue'),
            meta: { title: '舆情预警', requiresAuth: true }
          }
        ]
      },

      // 7. System (系统设置)
      {
        path: 'system',
        redirect: '/system/config',
        meta: { title: '系统设置', group: 'system' },
        children: [
          {
            path: 'config',
            name: 'system-config',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoSystemSettings.vue'),
            meta: { title: '系统配置', requiresAuth: true }
          },
          {
            path: 'health',
            name: 'system-health',
            component: () => import('@/views/artdeco-pages/system-tabs/SystemHealthTab.vue'),
            meta: { title: '健康矩阵', requiresAuth: true }
          },
          {
            path: 'api',
            name: 'system-api',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoMonitoringDashboard.vue'),
            meta: { title: 'API 终端', requiresAuth: true }
          },
          {
            path: 'data',
            name: 'system-data',
            component: () => import('@/views/artdeco-pages/system-tabs/ArtDecoDataManagement.vue'),
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
    component: () => import('@/layouts/QuantMatrixLayout.vue'),
    redirect: '/qm/dealing-room',
    children: [
      {
        path: 'dealing-room',
        name: 'qm-dealing-room',
        component: () => import('@/views/quant-matrix/QuantMatrixDealingRoom.vue'),
        meta: { title: '交易室', requiresAuth: true }
      },
      {
        path: 'market/realtime',
        name: 'qm-market-realtime',
        component: () => import('@/views/quant-matrix/market/QuantMatrixMarketRealtime.vue'),
        meta: { title: '实时行情流', requiresAuth: true }
      },
      {
        path: 'strategy/repo',
        name: 'qm-strategy-repo',
        component: () => import('@/views/quant-matrix/strategy/QuantMatrixStrategyRepo.vue'),
        meta: { title: '策略仓库', requiresAuth: true }
      },
      {
        path: 'market/technical',
        name: 'qm-market-technical',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: 'K线分析', description: '构建多周期K线、成交量与策略信号叠加分析能力。' },
        meta: { title: 'K线分析', requiresAuth: true }
      },
      {
        path: 'market/lhb',
        name: 'qm-market-lhb',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '龙虎榜分析', description: '聚焦席位异动、资金结构与次日延续性分析。' },
        meta: { title: '龙虎榜分析', requiresAuth: true }
      },
      {
        path: 'data/industry',
        name: 'qm-data-industry',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '板块动向', description: '跟踪行业轮动、热度迁移与龙头联动关系。' },
        meta: { title: '板块动向', requiresAuth: true }
      },
      {
        path: 'data/indicator',
        name: 'qm-data-indicator',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '指标分析', description: '提供技术指标组合、阈值告警与多市场对比。' },
        meta: { title: '指标分析', requiresAuth: true }
      },
      {
        path: 'data/concept',
        name: 'qm-data-concept',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '概念动向', description: '跟踪概念板块热度、成分股强弱和资金偏好。' },
        meta: { title: '概念动向', requiresAuth: true }
      },
      {
        path: 'data/fund-flow',
        name: 'qm-data-fund-flow',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '资金流向', description: '展示主力、北向和两融资金的结构性变化。' },
        meta: { title: '资金流向', requiresAuth: true }
      },
      {
        path: 'watchlist/manage',
        name: 'qm-watchlist-manage',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '组合管理', description: '管理策略观察池、分组标签与风险阈值。' },
        meta: { title: '组合管理', requiresAuth: true }
      },
      {
        path: 'watchlist/signals',
        name: 'qm-watchlist-signals',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '信号雷达', description: '汇总监控标的触发信号并支持优先级排序。' },
        meta: { title: '信号雷达', requiresAuth: true }
      },
      {
        path: 'watchlist/screener',
        name: 'qm-watchlist-screener',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '策略选股', description: '提供多因子筛选、回看与导出能力。' },
        meta: { title: '策略选股', requiresAuth: true }
      },
      {
        path: 'strategy/parameters',
        name: 'qm-strategy-parameters',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '参数设置', description: '管理策略参数模板、版本与灰度发布。' },
        meta: { title: '参数设置', requiresAuth: true }
      },
      {
        path: 'strategy/signals',
        name: 'qm-strategy-signals',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '策略信号', description: '统一展示策略触发信号与执行状态。' },
        meta: { title: '策略信号', requiresAuth: true }
      },
      {
        path: 'strategy/backtest',
        name: 'qm-strategy-backtest',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '回测引擎', description: '提供历史回测任务、结果快照和对比分析。' },
        meta: { title: '回测引擎', requiresAuth: true }
      },
      {
        path: 'strategy/gpu',
        name: 'qm-strategy-gpu',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '加速监控', description: '监控GPU队列、利用率与任务延迟表现。' },
        meta: { title: '加速监控', requiresAuth: true }
      },
      {
        path: 'strategy/opt',
        name: 'qm-strategy-opt',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '参数优化', description: '集中管理调参实验和收益风险平衡结果。' },
        meta: { title: '参数优化', requiresAuth: true }
      },
      {
        path: 'strategy/pos',
        name: 'qm-strategy-pos',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '仓位管理', description: '按策略与账户维度追踪仓位暴露和约束。' },
        meta: { title: '仓位管理', requiresAuth: true }
      },
      {
        path: 'trade/positions',
        name: 'qm-trade-positions',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '头寸管理', description: '展示实时头寸分布与风险敞口汇总。' },
        meta: { title: '头寸管理', requiresAuth: true }
      },
      {
        path: 'trade/terminal',
        name: 'qm-trade-terminal',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '交易操作', description: '承载交易下单、撤单和成交确认流程。' },
        meta: { title: '交易操作', requiresAuth: true }
      },
      {
        path: 'trade/signals',
        name: 'qm-trade-signals',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '信号监控', description: '按优先级和执行状态监控交易信号。' },
        meta: { title: '信号监控', requiresAuth: true }
      },
      {
        path: 'trade/portfolio',
        name: 'qm-trade-portfolio',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '持仓透视', description: '透视账户持仓结构、集中度与相关性。' },
        meta: { title: '持仓透视', requiresAuth: true }
      },
      {
        path: 'trade/history',
        name: 'qm-trade-history',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '历史对账', description: '用于成交明细回溯、损益归因与对账审计。' },
        meta: { title: '历史对账', requiresAuth: true }
      },
      {
        path: 'risk/management',
        name: 'qm-risk-management',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '风险管理中心', description: '集中呈现风险规则、限额与执行策略。' },
        meta: { title: '风险管理中心', requiresAuth: true }
      },
      {
        path: 'risk/overview',
        name: 'qm-risk-overview',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '风险概览', description: '汇总组合风险指标与异常事件追踪。' },
        meta: { title: '风险概览', requiresAuth: true }
      },
      {
        path: 'risk/pnl',
        name: 'qm-risk-pnl',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '组合盈亏', description: '按策略、行业和账户拆解盈亏贡献。' },
        meta: { title: '组合盈亏', requiresAuth: true }
      },
      {
        path: 'risk/stop-loss',
        name: 'qm-risk-stop-loss',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '止损雷达', description: '识别触发止损条件的标的并提示处置优先级。' },
        meta: { title: '止损雷达', requiresAuth: true }
      },
      {
        path: 'risk/alerts',
        name: 'qm-risk-alerts',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '告警中心', description: '统一查看风险告警、确认状态与处理流程。' },
        meta: { title: '告警中心', requiresAuth: true }
      },
      {
        path: 'risk/news',
        name: 'qm-risk-news',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '舆情预警', description: '跟踪舆情事件与持仓相关性的风险暴露。' },
        meta: { title: '舆情预警', requiresAuth: true }
      },
      {
        path: 'system/config',
        name: 'qm-system-config',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '系统配置', description: '维护交易参数、数据源与运行时配置。' },
        meta: { title: '系统配置', requiresAuth: true }
      },
      {
        path: 'system/health',
        name: 'qm-system-health',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '健康矩阵', description: '展示服务状态、可用性和故障诊断信息。' },
        meta: { title: '健康矩阵', requiresAuth: true }
      },
      {
        path: 'system/api',
        name: 'qm-system-api',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: 'API 终端', description: '观察API调用链路、延迟分位与错误分布。' },
        meta: { title: 'API 终端', requiresAuth: true }
      },
      {
        path: 'system/data',
        name: 'qm-system-data',
        component: () => import('@/views/quant-matrix/common/QuantMatrixScaffoldPage.vue'),
        props: { title: '数据源管理', description: '管理行情、交易和基础数据源接入状态。' },
        meta: { title: '数据源管理', requiresAuth: true }
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
