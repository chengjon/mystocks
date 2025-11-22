/**
 * Phase 4 路由配置
 *
 * 包含仪表盘和策略管理的路由定义
 */

const phase4Routes = [
  {
    path: '/phase4-dashboard',
    name: 'Phase4Dashboard',
    component: () => import('@/views/Phase4Dashboard.vue'),
    meta: {
      title: 'Phase 4 仪表盘',
      requiresAuth: true,
      icon: 'TrendCharts'
    }
  },
  {
    path: '/strategy-mgmt-phase4',
    name: 'StrategyMgmtPhase4',
    component: () => import('@/views/StrategyMgmtPhase4.vue'),
    meta: {
      title: 'Phase 4 策略管理',
      requiresAuth: true,
      icon: 'DataAnalysis'
    }
  }
]

export default phase4Routes
