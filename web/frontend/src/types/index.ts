/**
 * @fileoverview 统一的类型定义桶文件
 * @description 集中导出所有业务模块的TypeScript类型定义，提供类型导入的单一入口点
 * @module types
 */

// ============================================
// 通用类型定义
// ============================================

export * from './common/pagination'
export * from './common/response'
export * from './common/helpers'

// ============================================
// 用户模块类型
// ============================================

export * from './user/index'

// ============================================
// 认证模块类型
// ============================================

export * from './auth/index'

// ============================================
// 市场数据模块类型
// ============================================

export * from './market/stock'
export * from './market/quote'
export * from './market/candle'
export * from './market/moneyflow'

// ============================================
// 测试模块类型
// ============================================

export * from './test/index'

// ============================================
// 技术分析模块类型
// ============================================

export * from './technical/indicator'
export * from './technical/signal'

// ============================================
// 仪表板模块类型
// ============================================

export * from './dashboard/dashboard'
export * from './dashboard/widget'

// ============================================
// 设置模块类型
// ============================================

export * from './settings/account'
export * from './settings/notification'
export * from './settings/theme'
export * from './settings/security'
export * from './settings/advanced'

// ============================================
// 新闻模块类型
// ============================================

export * from './news/news'
export * from './news/filter'

// ============================================
// 投资组合模块类型
// ============================================

export * from './portfolio/portfolio'
export * from './portfolio/allocation'
export * from './portfolio/performance'
export * from './portfolio/risk'
export * from './portfolio/rebalancing'
