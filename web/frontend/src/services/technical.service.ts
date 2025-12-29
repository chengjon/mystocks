/**
 * Technical Analysis API Service
 * 封装所有技术分析相关的API调用
 */

import { apiClient, APIResponse } from './api-client';

/**
 * 技术指标数据
 */
export interface IndicatorData {
  symbol: string;
  indicator: string;
  values: {
    timestamp: string;
    value: number;
  }[];
}

/**
 * MA指标数据
 */
export interface MAData {
  symbol: string;
  ma5?: number;
  ma10?: number;
  ma20?: number;
  ma30?: number;
  ma60?: number;
  timestamp: string;
}

/**
 * MACD指标数据
 */
export interface MACDData {
  symbol: string;
  dif: number;
  dea: number;
  macd: number;
  timestamp: string;
}

/**
 * KDJ指标数据
 */
export interface KDJData {
  symbol: string;
  k: number;
  d: number;
  j: number;
  timestamp: string;
}

/**
 * BOLL指标数据
 */
export interface BOLLData {
  symbol: string;
  upper: number;
  middle: number;
  lower: number;
  timestamp: string;
}

/**
 * Technical Analysis API Service
 */
export class TechnicalService {
  private readonly basePath = '/technical';

  /**
   * 获取MA均线数据
   */
  async getMA(params: {
    symbol: string;
    periods: number[];
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<MAData[]>> {
    return apiClient.get(`${this.basePath}/indicators/ma`, params);
  }

  /**
   * 获取MACD数据
   */
  async getMACD(params: {
    symbol: string;
    fast_period?: number;
    slow_period?: number;
    signal_period?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<MACDData[]>> {
    return apiClient.get(`${this.basePath}/indicators/macd`, params);
  }

  /**
   * 获取KDJ数据
   */
  async getKDJ(params: {
    symbol: string;
    k_period?: number;
    d_period?: number;
    j_period?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<KDJData[]>> {
    return apiClient.get(`${this.basePath}/indicators/kdj`, params);
  }

  /**
   * 获取BOLL布林带数据
   */
  async getBOLL(params: {
    symbol: string;
    period?: number;
    std_dev?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<BOLLData[]>> {
    return apiClient.get(`${this.basePath}/indicators/boll`, params);
  }

  /**
   * 获取RSI数据
   */
  async getRSI(params: {
    symbol: string;
    period?: number;
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<{
    timestamp: string;
    rsi: number;
  }[]>> {
    return apiClient.get(`${this.basePath}/indicators/rsi`, params);
  }

  /**
   * 批量获取技术指标
   */
  async getBatchIndicators(params: {
    symbol: string;
    indicators: string[];
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<{
    symbol: string;
    data: Record<string, any[]>;
  }>> {
    return apiClient.post(`${this.basePath}/indicators/batch`, params);
  }

  /**
   * 获取所有支持的指标列表
   */
  async getSupportedIndicators(): Promise<APIResponse<{
    name: string;
    display_name: string;
    description: string;
    parameters: {
      name: string;
      default: number;
      min?: number;
      max?: number;
    }[];
  }[]>> {
    return apiClient.get(`${this.basePath}/indicators`);
  }

  /**
   * 计算自定义指标
   */
  async calculateCustomIndicator(params: {
    symbol: string;
    formula: string;
    parameters: Record<string, number>;
    start_date?: string;
    end_date?: string;
  }): Promise<APIResponse<{
    timestamp: string;
    value: number;
  }[]>> {
    return apiClient.post(`${this.basePath}/indicators/custom`, params);
  }
}

// 导出Service实例
export const technicalService = new TechnicalService();
