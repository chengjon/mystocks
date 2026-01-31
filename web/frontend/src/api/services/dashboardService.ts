/**
 * Dashboard API Service
 * 仪表盘API服务
 *
 * 提供Dashboard页面所需的所有API端点调用
 * 按优先级分为：核心市场数据(P0)、专业交易数据(P1)、技术分析(P2)
 */

import apiClient from '../apiClient'

export interface MarketOverviewData {
  symbol: string
  name: string
  latest_price: number
  change_percent: number
  volume: number
}

export interface FundFlowData {
  hgt: {
    amount: number
    change: number
  }
  sgt: {
    amount: number
    change: number
  }
  northTotal: {
    amount: number
    monthly: number
  }
  mainForce: {
    amount: number
    percentage: number
  }
}

export interface IndustryFlowData {
  name: string
  change: number
  amount: number
}

export interface LongHuBangData {
  code: string
  name: string
  reason: string
  amount: number
  change_percent: number
}

export interface BlockTradingData {
  code: string
  name: string
  price: number
  amount: number
  buyer: string
  seller: string
}

export interface StockFlowRankingData {
  code: string
  name: string
  amount: number
  change: number
}

export interface TechnicalIndicatorData {
  name: string
  value: number | string
  trend: 'rise' | 'fall' | 'neutral'
  signal: string
}

export interface PositionRiskData {
  totalValue: number
  totalPnL: number
  pnlPercent: number
  maxDrawdown: number
  riskLevel: 'low' | 'medium' | 'high' | 'extreme'
  riskLevelText: string
}

export interface SystemHealthData {
  label: string
  value: string
  status: 'good' | 'warning' | 'error'
}

/**
 * Dashboard API服务
 */
export const dashboardService = {
  // ============================================
  // P0: 核心市场数据
  // ============================================

  /**
   * 获取市场概览数据（主要指数）
   * API: GET /api/market/v2/etf/list
   * 用途: 获取上证、深证、创业板等主要指数数据
   */
  async getMarketOverview(limit = 100): Promise<{ data: MarketOverviewData[] }> {
    const response = await apiClient.get('/api/market/v2/etf/list', {
      params: { limit }
    })
    return response.data
  },

  /**
   * 获取资金流向数据
   * API: GET /api/market/fund-flow
   * 用途: 获取沪股通、深股通、北向资金、主力净流入数据
   */
  async getFundFlow(date?: string): Promise<{ data: FundFlowData }> {
    const params = date ? { date } : {}
    const response = await apiClient.get('/api/market/fund-flow', { params })
    return response.data
  },

  /**
   * 获取行业板块资金流向
   * API: GET /api/market/industry/flow
   * 用途: 获取市场热度板块前10名
   */
  async getIndustryFlow(
    sort = 'change_percent',
    limit = 10
  ): Promise<{ data: IndustryFlowData[] }> {
    const response = await apiClient.get('/api/market/industry/flow', {
      params: { sort, limit }
    })
    return response.data
  },

  // ============================================
  // P1: 专业交易数据
  // ============================================

  /**
   * 获取龙虎榜数据
   * API: GET /api/market/long-hu-bang
   * 用途: 获取市场活跃股票榜单
   */
  async getLongHuBang(
    date?: string,
    limit = 10
  ): Promise<{ data: LongHuBangData[] }> {
    const params: Record<string, any> = { limit }
    if (date) params.date = date
    const response = await apiClient.get('/api/market/long-hu-bang', { params })
    return response.data
  },

  /**
   * 获取大宗交易数据
   * API: GET /api/market/v2/block-trading
   * 用途: 获取大宗交易成交数据
   */
  async getBlockTrading(
    date?: string,
    limit = 10
  ): Promise<{ data: BlockTradingData[] }> {
    const params: Record<string, any> = { limit }
    if (date) params.date = date
    const response = await apiClient.get('/api/market/v2/block-trading', { params })
    return response.data
  },

  /**
   * 获取个股资金流向排名
   * API: GET /api/monitoring/stock/flow/ranking
   * 用途: 获取个股净流入前10名
   */
  async getStockFlowRanking(
    period = '1day',
    limit = 10
  ): Promise<{ data: StockFlowRankingData[] }> {
    const response = await apiClient.get('/api/monitoring/stock/flow/ranking', {
      params: { period, limit }
    })
    return response.data
  },

  /**
   * 获取ETF表现数据
   * API: GET /api/market/v2/etf/list
   * 用途: 获取ETF涨跌幅排名
   */
  async getETFPerformance(
    sort = 'change_percent',
    limit = 20
  ): Promise<{ data: MarketOverviewData[] }> {
    const response = await apiClient.get('/api/market/v2/etf/list', {
      params: { sort, limit }
    })
    return response.data
  },

  // ============================================
  // P2: 技术分析与风险
  // ============================================

  /**
   * 获取技术指标计算
   * API: GET /api/indicators/calculate/batch
   * 用途: 批量计算RSI、MACD、KDJ等指标
   */
  async getTechnicalIndicators(
    symbols: string[],
    indicators: string[]
  ): Promise<{ data: Record<string, TechnicalIndicatorData[]> }> {
    const response = await apiClient.get('/api/indicators/calculate/batch', {
      params: {
        symbols: symbols.join(','),
        indicators: indicators.join(',')
      }
    })
    return response.data
  },

  /**
   * 获取持仓风险评估
   * API: GET /api/v1/risk/position/assessment
   * 用途: 获取用户持仓的风险指标
   */
  async getPositionRisk(userId: number): Promise<{ data: PositionRiskData }> {
    const response = await apiClient.get('/api/v1/risk/position/assessment', {
      params: { user_id: userId }
    })
    return response.data
  },

  /**
   * 获取活跃策略
   * API: GET /api/strategy-mgmt/strategies
   * 用途: 获取用户的活跃策略数量
   */
  async getActiveStrategies(userId: number): Promise<{ data: any[] }> {
    const response = await apiClient.get('/api/strategy-mgmt/strategies', {
      params: { user_id: userId, status: 'active' }
    })
    return response.data
  },

  /**
   * 获取系统健康状态
   * API: GET /api/system/health
   * 用途: 获取API响应时间、CPU、内存等系统指标
   */
  async getSystemHealth(): Promise<{ data: SystemHealthData[] }> {
    const response = await apiClient.get('/api/system/health')
    return response.data
  },

  // ============================================
  // 辅助方法
  // ============================================

  /**
   * 格式化日期为API所需格式 (YYYY-MM-DD)
   */
  formatDate(date: Date = new Date()): string {
    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    return `${year}-${month}-${day}`
  },

  /**
   * 获取今日日期字符串
   */
  getToday(): string {
    return this.formatDate(new Date())
  }
}

export default dashboardService
