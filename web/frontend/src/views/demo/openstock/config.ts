/**
 * OpenStock Demo 配置文件
 * 定义标签页和API状态管理
 */

export interface TabItem {
  key: string
  label: string
  icon: string
}

/**
 * 标签页配置
 */
export const TABS: TabItem[] = [
  { key: 'search', label: '股票搜索', icon: '🔍' },
  { key: 'quote', label: '实时行情', icon: '📈' },
  { key: 'news', label: '股票新闻', icon: '📰' },
  { key: 'watchlist', label: '自选股管理', icon: '⭐' },
  { key: 'klinechart', label: 'K线图表', icon: '📊' },
  { key: 'heatmap', label: '股票热力图', icon: '🔥' },
  { key: 'status', label: '测试状态', icon: '✅' }
]

/**
 * API状态接口
 */
export interface ApiStatus {
  search: boolean
  quote: boolean
  news: boolean
  watchlist: boolean
  klinechart: boolean
  heatmap: boolean
}

/**
 * 默认API状态
 */
export const DEFAULT_API_STATUS: ApiStatus = {
  search: false,
  quote: false,
  news: false,
  watchlist: false,
  klinechart: false,
  heatmap: false
}
