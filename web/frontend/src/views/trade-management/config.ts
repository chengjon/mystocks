/**
 * Trade Management 配置文件
 */

export interface TabItem {
  label: string
  name: string
}

/**
 * 标签页配置
 */
export const TABS: TabItem[] = [
  { label: 'POSITIONS', name: 'positions' },
  { label: 'TRADE HISTORY', name: 'trades' },
  { label: 'STATISTICS', name: 'statistics' }
]

/**
 * 交易类型
 */
export const TRADE_TYPES = [
  { label: 'BUY', value: 'buy' },
  { label: 'SELL', value: 'sell' }
]

/**
 * 交易状态
 */
export const TRADE_STATUS = {
  pending: 'PENDING',
  completed: 'COMPLETED',
  cancelled: 'CANCELLED',
  failed: 'FAILED'
}

/**
 * 状态标签样式映射
 */
export const STATUS_BADGE_CLASS: Record<string, string> = {
  pending: 'artdeco-badge-warning',
  completed: 'artdeco-badge-success',
  cancelled: 'artdeco-badge-fall',
  failed: 'artdeco-badge-danger'
}
