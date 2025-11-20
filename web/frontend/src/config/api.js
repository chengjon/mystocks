/**
 * API 配置
 *
 * 根据环境变量动态配置 API 基础 URL
 */

// 从环境变量读取 API 基础 URL，如果未设置则使用默认值
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''

// API endpoints
export const API_ENDPOINTS = {
  // 问财筛选相关
  wencai: {
    queries: `${API_BASE_URL}/api/market/wencai/queries`,
    query: `${API_BASE_URL}/api/market/wencai/query`,
    customQuery: `${API_BASE_URL}/api/market/wencai/custom-query`,
    results: (queryName) => `${API_BASE_URL}/api/market/wencai/results/${queryName}`,
    refresh: (queryName) => `${API_BASE_URL}/api/market/wencai/refresh/${queryName}`,
    history: (queryName) => `${API_BASE_URL}/api/market/wencai/history/${queryName}`,
    health: `${API_BASE_URL}/api/market/wencai/health`
  },

  // 其他 API endpoints 可以在这里添加
  market: {
    fundFlow: `${API_BASE_URL}/api/market/fund-flow`,
    etf: `${API_BASE_URL}/api/market/etf`,
    // ...
  },

  // 策略管理相关
  strategy: {
    definitions: `${API_BASE_URL}/api/strategy/definitions`,
    runSingle: `${API_BASE_URL}/api/strategy/run/single`,
    runBatch: `${API_BASE_URL}/api/strategy/run/batch`,
    results: `${API_BASE_URL}/api/strategy/results`,
    matchedStocks: `${API_BASE_URL}/api/strategy/matched-stocks`,
    stats: `${API_BASE_URL}/api/strategy/stats/summary`
  },

  // 实时监控和告警系统
  monitoring: {
    // 告警规则管理
    alertRules: `${API_BASE_URL}/api/monitoring/alert-rules`,
    alertRule: (id) => `${API_BASE_URL}/api/monitoring/alert-rules/${id}`,

    // 告警记录
    alerts: `${API_BASE_URL}/api/monitoring/alerts`,
    markAlertRead: (id) => `${API_BASE_URL}/api/monitoring/alerts/${id}/mark-read`,
    markAllRead: `${API_BASE_URL}/api/monitoring/alerts/mark-all-read`,

    // 实时数据
    realtime: `${API_BASE_URL}/api/monitoring/realtime`,
    realtimeSymbol: (symbol) => `${API_BASE_URL}/api/monitoring/realtime/${symbol}`,
    fetchRealtime: `${API_BASE_URL}/api/monitoring/realtime/fetch`,

    // 龙虎榜
    dragonTiger: `${API_BASE_URL}/api/monitoring/dragon-tiger`,
    fetchDragonTiger: `${API_BASE_URL}/api/monitoring/dragon-tiger/fetch`,

    // 统计和摘要
    summary: `${API_BASE_URL}/api/monitoring/summary`,
    statsToday: `${API_BASE_URL}/api/monitoring/stats/today`,

    // 监控控制
    controlStart: `${API_BASE_URL}/api/monitoring/control/start`,
    controlStop: `${API_BASE_URL}/api/monitoring/control/stop`,
    controlStatus: `${API_BASE_URL}/api/monitoring/control/status`
  },

  // 技术分析系统
  technical: {
    // 综合指标
    allIndicators: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/indicators`,

    // 分类指标
    trend: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/trend`,
    momentum: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/momentum`,
    volatility: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/volatility`,
    volume: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/volume`,

    // 交易信号
    signals: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/signals`,

    // 历史数据
    history: (symbol) => `${API_BASE_URL}/api/technical/${symbol}/history`,

    // 批量查询
    batchIndicators: `${API_BASE_URL}/api/technical/batch/indicators`,

    // 形态识别
    patterns: (symbol) => `${API_BASE_URL}/api/technical/patterns/${symbol}`
  },

  // 多数据源管理系统
  multiSource: {
    // 健康状态
    health: `${API_BASE_URL}/api/multi-source/health`,
    healthBySource: (sourceType) => `${API_BASE_URL}/api/multi-source/health/${sourceType}`,

    // 数据获取
    realtimeQuote: `${API_BASE_URL}/api/multi-source/realtime-quote`,
    fundFlow: `${API_BASE_URL}/api/multi-source/fund-flow`,
    dragonTiger: `${API_BASE_URL}/api/multi-source/dragon-tiger`,

    // 系统管理
    supportedCategories: `${API_BASE_URL}/api/multi-source/supported-categories`,
    refreshHealth: `${API_BASE_URL}/api/multi-source/refresh-health`,
    clearCache: `${API_BASE_URL}/api/multi-source/clear-cache`
  },

  // 公告监控系统
  announcement: {
    // 公告获取
    fetch: `${API_BASE_URL}/api/announcement/fetch`,
    list: `${API_BASE_URL}/api/announcement/list`,
    today: `${API_BASE_URL}/api/announcement/today`,
    important: `${API_BASE_URL}/api/announcement/important`,
    byStock: (stockCode) => `${API_BASE_URL}/api/announcement/stock/${stockCode}`,

    // 公告类型和统计
    types: `${API_BASE_URL}/api/announcement/types`,
    stats: `${API_BASE_URL}/api/announcement/stats`,

    // 监控管理
    evaluateRules: `${API_BASE_URL}/api/announcement/monitor/evaluate`
  }
}

export default {
  API_BASE_URL,
  API_ENDPOINTS
}
