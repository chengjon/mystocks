/**
 * Market API Service
 *
 * 基于API契约管理平台生成的TypeScript类型定义
 * Contract: market-data v1.0.0
 *
 * 提供市场数据相关的API调用服务，包括：
 * - 市场概览 (Market Overview)
 * - 资金流向 (Fund Flow)
 * - K线数据 (Kline Data)
 * - ETF列表 (ETF List)
 * - 龙虎榜 (Longhubang)
 * - 竞价抢筹 (Chip Race)
 */

import axios from 'axios';
import type { components } from '@/types/market-data-api';

// Extract type aliases for convenience
type UnifiedResponse<T> = components['schemas']['UnifiedResponse'];
type MarketOverviewData = components['schemas']['MarketOverviewData'];
type FundFlowData = components['schemas']['FundFlowData'];
type KlineData = components['schemas']['KlineData'];
type ETFData = components['schemas']['ETFData'];
type LonghubangData = components['schemas']['LongHuBangData'];
type ChipRaceData = components['schemas']['ChipRaceData'];

/**
 * API响应类型包装
 */
type APIResponse<T> = UnifiedResponse<T>;

/**
 * 配置
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = 10000; // 10 seconds
const API_PREFIX = '/api/market';

/**
 * MarketApiService类
 *
 * 使用Axios提供类型安全的API调用
 * 包含请求/响应拦截器用于日志和错误处理
 */
class MarketApiService {
  private client = axios.create({
    baseURL: `${API_BASE}${API_PREFIX}`,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  constructor() {
    this.setupInterceptors();
  }

  /**
   * 设置拦截器
   *
   * 请求拦截器: 添加日志和请求ID
   * 响应拦截器: 处理错误和日志
   */
  private setupInterceptors(): void {
    // 请求拦截器
    this.client.interceptors.request.use(
      (config) => {
        const requestId = this.generateRequestId();
        config.headers['X-Request-ID'] = requestId;

        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          params: config.params,
          requestId,
        });

        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    // 响应拦截器
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
          status: response.status,
          requestId: response.config.headers['X-Request-ID'],
        });
        return response;
      },
      (error) => {
        if (error.response) {
          console.error('[API Error]', {
            status: error.response.status,
            data: error.response.data,
            url: error.config?.url,
          });
        } else if (error.request) {
          console.error('[API Network Error]', {
            message: error.message,
            url: error.config?.url,
          });
        } else {
          console.error('[API Config Error]', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  /**
   * 生成请求ID
   */
  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  }

  /**
   * 获取市场概览数据
   *
   * GET /api/market/overview
   *
   * 返回数据包括:
   * - 主要市场指数（上证指数、深证成指等）
   * - 市场涨跌统计
   * - 换手率
   * - 涨幅榜前N名ETF
   *
   * @returns Promise<MarketOverviewData>
   */
  async getMarketOverview(): Promise<MarketOverviewData> {
    const response = await this.client.get<APIResponse<MarketOverviewData>>('/overview');
    return response.data.data!;
  }

  /**
   * 查询资金流向数据
   *
   * GET /api/market/fund-flow
   *
   * 返回数据包括:
   * - 主力资金流向
   * - 散户资金流向
   * - 大单资金流向
   *
   * @param params 查询参数
   * @param params.symbol 股票代码 (必填)
   * @param params.timeframe 时间维度：1/3/5/10天 (可选，默认"1")
   * @param params.start_date 开始日期 YYYY-MM-DD (可选)
   * @param params.end_date 结束日期 YYYY-MM-DD (可选)
   * @returns Promise<FundFlowData>
   */
  async getFundFlow(params: {
    symbol: string;
    timeframe?: '1' | '3' | '5' | '10';
    start_date?: string;
    end_date?: string;
  }): Promise<FundFlowData> {
    const response = await this.client.get<APIResponse<FundFlowData>>('/fund-flow', {
      params: {
        symbol: params.symbol,
        timeframe: params.timeframe || '1',
        start_date: params.start_date,
        end_date: params.end_date,
      },
    });
    return response.data.data!;
  }

  /**
   * 获取K线数据
   *
   * GET /api/market/kline
   *
   * 支持的周期:
   * - 分钟K: 1m, 5m, 15m, 30m
   * - 小时K: 1h
   * - 日K: 1d
   *
   * @param params 查询参数
   * @param params.symbol 股票代码 (必填)
   * @param params.period K线周期 (必填)
   * @param params.start_date 开始日期 YYYY-MM-DD (可选)
   * @param params.end_date 结束日期 YYYY-MM-DD (可选)
   * @param params.limit 返回数据条数 (可选)
   * @returns Promise<KlineData>
   */
  async getKlineData(params: {
    symbol: string;
    period: '1m' | '5m' | '15m' | '30m' | '1h' | '1d';
    start_date?: string;
    end_date?: string;
    limit?: number;
  }): Promise<KlineData> {
    const response = await this.client.get<APIResponse<KlineData>>('/kline', {
      params: {
        symbol: params.symbol,
        period: params.period,
        start_date: params.start_date,
        end_date: params.end_date,
        limit: params.limit,
      },
    });
    return response.data.data!;
  }

  /**
   * 查询ETF列表
   *
   * GET /api/market/etf/list
   *
   * 支持筛选条件:
   * - 按代码或名称搜索
   * - 按市场筛选（上海/深圳）
   * - 按类型筛选（股票/债券/商品/货币/QDII）
   *
   * @param params 查询参数 (所有参数可选)
   * @param params.search 搜索关键词（代码或名称）
   * @param params.market 市场（上海/深圳）
   * @param params.type 类型（股票/债券/商品/货币/QDII）
   * @param params.limit 返回数据条数 (可选)
   * @param params.offset 偏移量 (可选)
   * @returns Promise<ETFData>
   */
  async getETFList(params?: {
    search?: string;
    market?: 'SH' | 'SZ';
    type?: 'stock' | 'bond' | 'commodity' | 'currency' | 'qdii';
    limit?: number;
    offset?: number;
  }): Promise<ETFData> {
    const response = await this.client.get<APIResponse<ETFData>>('/etf/list', {
      params: {
        search: params?.search,
        market: params?.market,
        type: params?.type,
        limit: params?.limit,
        offset: params?.offset,
      },
    });
    return response.data.data!;
  }

  /**
   * 查询龙虎榜数据
   *
   * GET /api/market/lhb
   *
   * 返回指定日期的龙虎榜数据，包括:
   * - 涨幅榜上榜股票
   * - 跌幅榜上榜股票
   * - 异常波动股票
   *
   * @param params 查询参数
   * @param params.date 日期 YYYY-MM-DD (可选，默认当日)
   * @param params.market 市场（上海/深圳） (可选)
   * @returns Promise<LonghubangData>
   */
  async getLongHuBang(params?: {
    date?: string;
    market?: 'SH' | 'SZ';
  }): Promise<LonghubangData> {
    const response = await this.client.get<APIResponse<LonghubangData>>('/lhb', {
      params: {
        date: params?.date,
        market: params?.market,
      },
    });
    return response.data.data!;
  }

  /**
   * 查询竞价抢筹数据
   *
   * GET /api/market/chip-race
   *
   * 返回指定日期的竞价抢筹数据，包括:
   * - 开盘抢筹比例
   * - 主力vs散户买入对比
   * - 热门抢筹股票排行
   *
   * @param params 查询参数
   * @param params.date 日期 YYYY-MM-DD (可选，默认当日)
   * @returns Promise<ChipRaceData>
   */
  async getChipRace(params?: {
    date?: string;
  }): Promise<ChipRaceData> {
    const response = await this.client.get<APIResponse<ChipRaceData>>('/chip-race', {
      params: {
        date: params?.date,
      },
    });
    return response.data.data!;
  }
}

/**
 * 导出单例实例
 *
 * 使用示例:
 * ```typescript
 * import { marketService } from '@/services/api/marketService';
 *
 * // 获取市场概览
 * const overview = await marketService.getMarketOverview();
 * console.log(overview.market_index);
 *
 * // 获取资金流向
 * const fundFlow = await marketService.getFundFlow({
 *   symbol: '600519',
 *   timeframe: '5'
 * });
 * ```
 */
export const marketService = new MarketApiService();

/**
 * 导出类型
 */
export type {
  MarketOverviewData,
  FundFlowData,
  KlineData,
  ETFData,
  LonghubangData,
  ChipRaceData,
  APIResponse,
};
