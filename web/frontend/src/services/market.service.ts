/**
 * Market API Service
 * 封装所有市场数据相关的API调用
 */

import { apiClient, APIResponse } from './api-client';

/**
 * 股票基本信息
 */
export interface StockSymbol {
  symbol: string;
  name: string;
  industry?: string;
  sector?: string;
  market?: string;
  list_date?: string;
}

/**
 * 股票行情数据
 */
export interface StockQuote {
  symbol: string;
  name: string;
  current_price: number;
  open_price: number;
  high_price: number;
  low_price: number;
  prev_close: number;
  volume: number;
  turnover: number;
  change: number;
  change_percent: number;
  timestamp: string;
}

/**
 * K线数据点
 */
export interface KlineData {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  turnover: number;
}

/**
 * 自选股
 */
export interface WatchlistItem {
  id: number;
  symbol: string;
  name: string;
  added_at: string;
  notes?: string;
}

/**
 * Market API Service
 */
export class MarketService {
  private readonly basePath = '/market';

  /**
   * 获取股票列表
   */
  async getStockList(params?: {
    market?: string;
    sector?: string;
    industry?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<{ stocks: StockSymbol[]; total: number }>> {
    return apiClient.get(`${this.basePath}/symbols`, params);
  }

  /**
   * 搜索股票
   */
  async searchStocks(query: string): Promise<APIResponse<StockSymbol[]>> {
    return apiClient.get(`${this.basePath}/search`, { q: query });
  }

  /**
   * 获取股票行情
   */
  async getQuote(symbol: string): Promise<APIResponse<StockQuote>> {
    return apiClient.get(`${this.basePath}/quote`, { symbol });
  }

  /**
   * 批量获取股票行情
   */
  async getBatchQuotes(symbols: string[]): Promise<APIResponse<StockQuote[]>> {
    return apiClient.get(`${this.basePath}/quote/batch`, { symbols: symbols.join(',') });
  }

  /**
   * 获取实时行情列表
   */
  async getRealtimeQuotes(symbols: string[]): Promise<APIResponse<StockQuote[]>> {
    return apiClient.post(`${this.basePath}/realtime`, { symbols });
  }

  /**
   * 获取K线数据
   */
  async getKlineData(params: {
    symbol: string;
    period: '1min' | '5min' | '15min' | '30min' | '60min' | 'day' | 'week' | 'month';
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<APIResponse<KlineData[]>> {
    return apiClient.get(`${this.basePath}/kline`, params);
  }

  /**
   * 获取分时数据
   */
  async getTickData(symbol: string, date?: string): Promise<APIResponse<{
    timestamp: string;
    price: number;
    volume: number;
  }[]>> {
    return apiClient.get(`${this.basePath}/tick`, { symbol, date });
  }

  /**
   * 获取板块列表
   */
  async getSectors(): Promise<APIResponse<{
    name: string;
    count: number;
    change_percent: number;
  }[]>> {
    return apiClient.get(`${this.basePath}/sectors`);
  }

  /**
   * 获取行业列表
   */
  async getIndustries(): Promise<APIResponse<{
    name: string;
    sector: string;
    count: number;
  }[]>> {
    return apiClient.get(`${this.basePath}/industries`);
  }

  /**
   * 获取板块成分股
   */
  async getSectorStocks(sector: string): Promise<APIResponse<StockSymbol[]>> {
    return apiClient.get(`${this.basePath}/sectors/${sector}/stocks`);
  }

  /**
   * 获取行业成分股
   */
  async getIndustryStocks(industry: string): Promise<APIResponse<StockSymbol[]>> {
    return apiClient.get(`${this.basePath}/industries/${industry}/stocks`);
  }

  /**
   * 获取自选股列表
   */
  async getWatchlist(): Promise<APIResponse<WatchlistItem[]>> {
    return apiClient.get(`${this.basePath}/watchlist`);
  }

  /**
   * 添加自选股
   */
  async addToWatchlist(data: {
    symbol: string;
    notes?: string;
  }): Promise<APIResponse<WatchlistItem>> {
    return apiClient.post(`${this.basePath}/watchlist`, data);
  }

  /**
   * 删除自选股
   */
  async removeFromWatchlist(id: number): Promise<APIResponse<void>> {
    return apiClient.delete(`${this.basePath}/watchlist/${id}`);
  }

  /**
   * 更新自选股备注
   */
  async updateWatchlistItem(id: number, notes: string): Promise<APIResponse<WatchlistItem>> {
    return apiClient.put(`${this.basePath}/watchlist/${id}`, { notes });
  }

  /**
   * 获取市场概况
   */
  async getMarketOverview(): Promise<APIResponse<{
    market_status: string;
    total_market_cap: number;
    total_turnover: number;
    up_count: number;
    down_count: number;
    unchanged_count: number;
    limit_up_count: number;
    limit_down_count: number;
  }>> {
    return apiClient.get(`${this.basePath}/overview`);
  }

  /**
   * 获取涨跌榜
   */
  async getTopMovers(params: {
    type: 'up' | 'down';
    limit?: number;
  }): Promise<APIResponse<StockQuote[]>> {
    return apiClient.get(`${this.basePath}/top-movers`, params);
  }

  /**
   * 获取成交额榜
   */
  async getTopTurnovers(limit: number = 10): Promise<APIResponse<StockQuote[]>> {
    return apiClient.get(`${this.basePath}/top-turnovers`, { limit });
  }

  /**
   * 获取振幅榜
   */
  async getTopAmplitudes(limit: number = 10): Promise<APIResponse<StockQuote[]>> {
    return apiClient.get(`${this.basePath}/top-amplitudes`, { limit });
  }
}

// 导出Service实例
export const marketService = new MarketService();
