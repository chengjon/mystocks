import apiClient from './apiClient';

export interface StopLimitResponse {
  limit_up: number;
  limit_down: number;
  limit_pct: number;
  is_limit_up: boolean;
  is_limit_down: boolean;
}

export interface T1SellableResponse {
  buy_date: string;
  sellable_date: string;
  t_status: 'T+0' | 'T+1';
  days_remaining: number;
}

export interface AdjustmentResponse {
  symbol: string;
  forward_adjustment_factor: number;
  backward_adjustment_factor: number;
  adjustment_type: 'qfq' | 'hfq' | 'none';
}

export interface AStockInfoResponse {
  symbol: string;
  name: string;
  market: '主板' | '中小板' | '创业板' | '科创板' | '北交所';
  is_st: boolean;
  is_new: boolean;
  price_limit_pct: number;
  trading_mode: 'T+0' | 'T+1';
}

export const astockApi = {
  async getStopLimit(
    symbol: string,
    date: string,
    prev_close: number
  ): Promise<StopLimitResponse> {
    const response = await apiClient.get('/api/astock/stop-limit', {
      params: { symbol, date, prev_close }
    });
    return response.data;
  },

  async checkT1Sellable(buy_date: string, symbol?: string): Promise<T1SellableResponse> {
    const response = await apiClient.get('/api/astock/t1-sellable', {
      params: { buy_date, symbol }
    });
    return response.data;
  },

  async getAdjustmentFactors(symbol: string): Promise<AdjustmentResponse> {
    const response = await apiClient.get('/api/astock/adjustment', {
      params: { symbol }
    });
    return response.data;
  },

  async getAStockInfo(symbol: string): Promise<AStockInfoResponse> {
    const response = await apiClient.get('/api/astock/info', {
      params: { symbol }
    });
    return response.data;
  },

  async validateTradingRules(
    symbol: string,
    buy_date: string,
    buy_price: number,
    buy_volume: number
  ): Promise<{
    can_sell: boolean;
    sellable_date: string;
    limit_up_price: number;
    limit_down_price: number;
    messages: string[];
  }> {
    const response = await apiClient.post('/api/astock/validate', {
      symbol,
      buy_date,
      buy_price,
      buy_volume
    });
    return response.data;
  }
};

export default astockApi;
