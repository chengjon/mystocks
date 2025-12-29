/**
 * Trade API Service
 * 封装所有交易相关的API调用
 */

import { apiClient, APIResponse } from './api-client';

/**
 * 订单类型
 */
export enum OrderType {
  MARKET = 'market', // 市价单
  LIMIT = 'limit',   // 限价单
  STOP = 'stop',     // 止损单
}

/**
 * 订单方向
 */
export enum OrderDirection {
  BUY = 'buy',   // 买入
  SELL = 'sell', // 卖出
}

/**
 * 订单状态
 */
export enum OrderStatus {
  PENDING = 'pending',     // 待成交
  PARTIAL = 'partial',     // 部分成交
  FILLED = 'filled',       // 完全成交
  CANCELLED = 'cancelled', // 已取消
  REJECTED = 'rejected',   // 已拒绝
}

/**
 * 订单信息
 */
export interface Order {
  id: number;
  symbol: string;
  type: OrderType;
  direction: OrderDirection;
  price?: number;
  quantity: number;
  filled_quantity: number;
  status: OrderStatus;
  created_at: string;
  updated_at: string;
  notes?: string;
}

/**
 * 持仓信息
 */
export interface Position {
  id: number;
  symbol: string;
  name: string;
  quantity: number;
  available_quantity: number;
  cost_price: number;
  current_price: number;
  market_value: number;
  profit_loss: number;
  profit_loss_percent: number;
}

/**
 * 账户余额
 */
export interface AccountBalance {
  total_balance: number;
  available_balance: number;
  frozen_balance: number;
  market_value: number;
  profit_loss: number;
  profit_loss_percent: number;
}

/**
 * 交易记录
 */
export interface TradeRecord {
  id: number;
  order_id: number;
  symbol: string;
  direction: OrderDirection;
  price: number;
  quantity: number;
  amount: number;
  created_at: string;
}

/**
 * Trade API Service
 */
export class TradeService {
  private readonly basePath = '/trade';

  /**
   * 创建订单
   */
  async createOrder(params: {
    symbol: string;
    type: OrderType;
    direction: OrderDirection;
    price?: number;
    quantity: number;
    notes?: string;
  }): Promise<APIResponse<Order>> {
    return apiClient.post(`${this.basePath}/orders`, params);
  }

  /**
   * 获取订单列表
   */
  async getOrders(params?: {
    symbol?: string;
    status?: OrderStatus;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<{ orders: Order[]; total: number }>> {
    return apiClient.get(`${this.basePath}/orders`, params);
  }

  /**
   * 获取订单详情
   */
  async getOrder(orderId: number): Promise<APIResponse<Order>> {
    return apiClient.get(`${this.basePath}/orders/${orderId}`);
  }

  /**
   * 取消订单
   */
  async cancelOrder(orderId: number): Promise<APIResponse<Order>> {
    return apiClient.post(`${this.basePath}/orders/${orderId}/cancel`);
  }

  /**
   * 批量取消订单
   */
  async cancelOrders(orderIds: number[]): Promise<APIResponse<{ cancelled: number; failed: number }>> {
    return apiClient.post(`${this.basePath}/orders/cancel-batch`, { order_ids: orderIds });
  }

  /**
   * 获取持仓列表
   */
  async getPositions(): Promise<APIResponse<Position[]>> {
    return apiClient.get(`${this.basePath}/positions`);
  }

  /**
   * 获取持仓详情
   */
  async getPosition(positionId: number): Promise<APIResponse<Position>> {
    return apiClient.get(`${this.basePath}/positions/${positionId}`);
  }

  /**
   * 平仓
   */
  async closePosition(params: {
    position_id: number;
    quantity: number;
    price?: number;
  }): Promise<APIResponse<Order>> {
    return apiClient.post(`${this.basePath}/positions/close`, params);
  }

  /**
   * 获取账户余额
   */
  async getAccountBalance(): Promise<APIResponse<AccountBalance>> {
    return apiClient.get(`${this.basePath}/account/balance`);
  }

  /**
   * 获取交易记录
   */
  async getTradeRecords(params?: {
    symbol?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<{ trades: TradeRecord[]; total: number }>> {
    return apiClient.get(`${this.basePath}/trades`, params);
  }

  /**
   * 获取交易统计
   */
  async getTradeStats(params?: {
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<{
    total_trades: number;
    total_amount: number;
    profit_loss: number;
    profit_loss_percent: number;
    win_rate: number;
  }>> {
    return apiClient.get(`${this.basePath}/stats`, params);
  }

  /**
   * 获取订单历史
   */
  async getOrderHistory(params?: {
    symbol?: string;
    start_date?: string;
    end_date?: string;
    limit?: number;
    offset?: number;
  }): Promise<APIResponse<{ orders: Order[]; total: number }>> {
    return apiClient.get(`${this.basePath}/orders/history`, params);
  }

  /**
   * 验证订单
   */
  async validateOrder(params: {
    symbol: string;
    type: OrderType;
    direction: OrderDirection;
    price?: number;
    quantity: number;
  }): Promise<APIResponse<{
    valid: boolean;
    estimated_amount: number;
    commission: number;
    available_balance: number;
    errors?: string[];
  }>> {
    return apiClient.post(`${this.basePath}/orders/validate`, params);
  }

  /**
   * 获取交易费用
   */
  async getCommission(symbol: string, amount: number): Promise<APIResponse<{
    commission: number;
    commission_rate: number;
    min_commission: number;
  }>> {
    return apiClient.get(`${this.basePath}/commission`, { symbol, amount });
  }
}

// 导出Service实例
export const tradeService = new TradeService();
