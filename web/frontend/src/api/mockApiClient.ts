// web/frontend/src/api/mockApiClient.ts

import type { UnifiedResponse } from './types/common.ts';
import mockDashboard from '../mock/mockDashboard.js';
import { loadMockKlineData } from './mockKlineData.ts';
import type { IntervalType } from '../types/kline.ts';

type RequestParams = Record<string, unknown>;

interface MockRequestConfig {
  params?: RequestParams;
}

function getRequestParams(config?: MockRequestConfig): RequestParams {
  return config?.params ?? {};
}

function isIntervalType(value: unknown): value is IntervalType {
  return value === '1m' || value === '5m' || value === '15m' || value === '1h' || value === '1d' || value === '1w' || value === '1M';
}

// A simple delay function to simulate network latency
const simulateNetworkDelay = (min = 100, max = 500) =>
  new Promise((resolve) => setTimeout(resolve, Math.random() * (max - min) + min));

// Generic mock data wrapper
const createMockResponse = <T>(data: T): UnifiedResponse<T> => ({
  success: true,
  code: 200,
  message: 'Mock data fetched successfully',
  data,
  timestamp: new Date().toISOString(),
  request_id: `mock-req-${Math.floor(Math.random() * 10000)}`,
  errors: null,
});

const toMockResult = <T>(value: unknown): T => value as T;

const normalizeMockPath = (url = '') => url.replace(/^\/api(?=\/)/, '');

const matchesMockRoute = (url: string, route: string): boolean => {
  const normalizedUrl = normalizeMockPath(url);
  const normalizedRoute = normalizeMockPath(route);

  if (normalizedRoute.endsWith('/')) {
    return normalizedUrl.startsWith(normalizedRoute);
  }

  return normalizedUrl === normalizedRoute;
};

export const mockApiClient = {
  async get<T = UnifiedResponse<unknown>>(url: string, config?: MockRequestConfig): Promise<T> {
    await simulateNetworkDelay();

    const params = getRequestParams(config);

    // --- Dashboard & Market Routes ---

    // 1. Dashboard Root Object
    if (matchesMockRoute(url, '/dashboard/market-overview')) {
      const requestedLimit = Number(params.limit || 10);
      const safeLimit = Number.isFinite(requestedLimit) && requestedLimit > 0 ? requestedLimit : 10;

      const indices = [
        { symbol: '000001.SH', name: '上证指数', current_price: 3128.45, change_percent: 0.85, volume: 1000000 },
        { symbol: '399001.SZ', name: '深证成指', current_price: 10245.67, change_percent: 1.23, volume: 2000000 },
        { symbol: '399006.SZ', name: '创业板指', current_price: 2156.89, change_percent: -0.45, volume: 500000 },
        { symbol: '899050.BJ', name: '北证50', current_price: 980.15, change_percent: 0.38, volume: 180000 }
      ].slice(0, safeLimit);

      const response = createMockResponse({
        indices,
        up_count: 3120,
        down_count: 1456,
        flat_count: 210,
        total_volume: 1280000000,
        total_turnover: 128960000000,
        top_gainers: [],
        top_losers: [],
        most_active: []
      });

      return {
        ...response,
        process_time: '0.00'
      } as T;
    }

    // 2. Market Overview (ETF List / Indices)
    if (url.includes('/api/market/v2/etf/list')) {
      // Mocking indices based on limit or sort
      const indices = [
        { symbol: '000001.SH', name: '上证指数', latest_price: 3128.45, change_percent: 0.85, volume: 1000000 },
        { symbol: '399001.SZ', name: '深证成指', latest_price: 10245.67, change_percent: 1.23, volume: 2000000 },
        { symbol: '399006.SZ', name: '创业板指', latest_price: 2156.89, change_percent: -0.45, volume: 500000 },
        { symbol: '510300.SH', name: '沪深300', latest_price: 3800.00, change_percent: 0.50, volume: 800000 },
      ];
      return toMockResult<T>(createMockResponse(indices));
    }

    // 3. Fund Flow
    if (matchesMockRoute(url, '/akshare/market/fund-flow/hsgt-summary')) {
      // P0 fix (B4.014, 2026-06-29): mock 契约对齐前端 fundFlowPageData.ts 真相源
      // (板块/资金方向/成交净买额/指数涨跌幅/交易日 中文宽表).
      // 真实后端经 src/adapters/akshare/market_adapter/fund_flow.py 透传 akshare
      // stock_hsgt_fund_flow_summary_em 原始 13 列, 字段名与此处一致.
      const today = new Date().toISOString().slice(0, 10)
      const flowRows = [
        { 交易日: today, 类型: '沪港通', 板块: '沪股通', 资金方向: '北向', 交易状态: '3', 成交净买额: 28.6, 资金净流入: 28.6, 当日资金余额: 525, 上涨数: 930, 持平数: 38, 下跌数: 668, 相关指数: '上证指数', 指数涨跌幅: 0.85 },
        { 交易日: today, 类型: '沪港通', 板块: '港股通(沪)', 资金方向: '南向', 交易状态: '3', 成交净买额: 18.2, 资金净流入: 18.2, 当日资金余额: 425, 上涨数: 436, 持平数: 30, 下跌数: 146, 相关指数: '恒生指数', 指数涨跌幅: 0.64 },
        { 交易日: today, 类型: '深港通', 板块: '深股通', 资金方向: '北向', 交易状态: '3', 成交净买额: 30.2, 资金净流入: 30.2, 当日资金余额: 510, 上涨数: 817, 持平数: 35, 下跌数: 1017, 相关指数: '深证成指', 指数涨跌幅: 0.19 },
        { 交易日: today, 类型: '深港通', 板块: '港股通(深)', 资金方向: '南向', 交易状态: '3', 成交净买额: 12.4, 资金净流入: 12.4, 当日资金余额: 480, 上涨数: 280, 持平数: 22, 下跌数: 110, 相关指数: '恒生指数', 指数涨跌幅: 0.57 },
      ]
      return toMockResult<T>(createMockResponse(flowRows))
    }

    if (url.includes('/api/market/fund-flow')) {
      // Use mockDashboard data or generate consistent structure
      const flowData = {
        hgt: { amount: 28.6, change: 5.2 },
        sgt: { amount: 30.2, change: 8.9 },
        northTotal: { amount: 58.8, monthly: 1256 },
        mainForce: { amount: 126.5, percentage: 68 }
      };
      return toMockResult<T>(createMockResponse(flowData));
    }

    // 4. Industry Flow
    if (matchesMockRoute(url, '/v2/market/sector/fund-flow')) {
      const sectors = mockDashboard.getLeadingSectors().map((sector, index) => ({
        ...sector,
        amount: Number((150 - index * 12.5).toFixed(1))
      }));
      return toMockResult<T>(createMockResponse(sectors));
    }

    if (url.includes('/api/market/industry/flow')) {
      // Use mockDashboard logic
      const sectors = mockDashboard.getLeadingSectors();
      return toMockResult<T>(createMockResponse(sectors));
    }

    // 5. Stock Flow Ranking
    if (matchesMockRoute(url, '/akshare/market/fund-flow/big-deal')) {
      // P0 fix (B4.014, 2026-06-29): mock 契约对齐前端 buildStockRanking 真相源
      // (symbol/股票简称/成交价格/成交额/大单性质/涨跌幅 中文宽表).
      // 真实后端经 src/adapters/akshare/market_adapter/fund_flow.py 透传 akshare
      // stock_fund_flow_big_deal 原始字段 + 股票代码→symbol 重命名.
      const now = new Date().toISOString().replace('T', ' ').slice(0, 19)
      const stocks = [
        { 成交时间: now, symbol: '600519', 股票简称: '贵州茅台', 成交价格: 1850.0, 成交量: 70000, 成交额: 12.5, 大单性质: '买盘', 涨跌幅: '2.10%', 涨跌额: 38.2 },
        { 成交时间: now, symbol: '300750', 股票简称: '宁德时代', 成交价格: 245.0, 成交量: 40000, 成交额: 8.9, 大单性质: '买盘', 涨跌幅: '3.50%', 涨跌额: 8.3 },
        { 成交时间: now, symbol: '600028', 股票简称: '中国石化', 成交价格: 6.2, 成交量: 950000, 成交额: 5.2, 大单性质: '卖盘', 涨跌幅: '-1.80%', 涨跌额: -0.11 },
        { 成交时间: now, symbol: '600036', 股票简称: '招商银行', 成交价格: 35.8, 成交量: 200000, 成交额: 6.7, 大单性质: '买盘', 涨跌幅: '1.20%', 涨跌额: 0.42 },
        { 成交时间: now, symbol: '000002', 股票简称: '万科A', 成交价格: 9.1, 成交量: 380000, 成交额: 3.1, 大单性质: '卖盘', 涨跌幅: '-0.90%', 涨跌额: -0.08 }
      ]
      return toMockResult<T>(createMockResponse(stocks))
    }

    if (url.includes('/api/monitoring/stock/flow/ranking')) {
      const stocks = [
        { code: '600519', name: '贵州茅台', amount: 12.5, change: 2.1 },
        { code: '300750', name: '宁德时代', amount: 8.9, change: 3.5 },
        { code: '600028', name: '中国石化', amount: -5.2, change: -1.8 },
        { code: '600036', name: '招商银行', amount: 6.7, change: 1.2 },
        { code: '000002', name: '万科A', amount: -3.1, change: -0.9 }
      ];
      return toMockResult<T>(createMockResponse(stocks));
    }

    // 6. Long Hu Bang (Dragon Tiger List)
    if (url.includes('/api/market/long-hu-bang')) {
      const lhb = [
        { code: '000001', name: '平安银行', reason: '日涨幅偏离值达7%', amount: 12000, change_percent: 10.01 },
        { code: '600000', name: '浦发银行', reason: '连续三个交易日内，涨幅偏离值累计达20%', amount: 8500, change_percent: 9.98 }
      ];
      return toMockResult<T>(createMockResponse(lhb));
    }

    // 7. Block Trading
    if (url.includes('/api/market/v2/block-trading')) {
      const block = [
        { code: '600519', name: '贵州茅台', price: 1800.00, amount: 5000, buyer: '机构专用', seller: '中信证券北京总部' },
        { code: '300750', name: '宁德时代', price: 240.00, amount: 3000, buyer: '深股通专用', seller: '机构专用' }
      ];
      return toMockResult<T>(createMockResponse(block));
    }

    // 8. K-Line Data
    if (url.includes('/api/market/kline')) {
        const symbol = typeof params.symbol === 'string' ? params.symbol : '000001.SH';
        const period = isIntervalType(params.period) ? params.period : '1d';
        const kline = await loadMockKlineData(symbol, period);
        return toMockResult<T>(createMockResponse(kline.candles));
    }

    // 9. Real-time Quote
    if (url.includes('/api/market/quote/')) {
        const symbol = url.split('/').pop() || '000001.SH';
        const quote = {
            symbol,
            price: (Math.random() * 100 + 50).toFixed(2),
            change: (Math.random() * 4 - 2).toFixed(2),
            changePercent: (Math.random() * 4 - 2).toFixed(2),
            volume: Math.floor(Math.random() * 1000000),
            turnover: Math.floor(Math.random() * 100000000)
        };
        return toMockResult<T>(createMockResponse(quote));
    }

    // 10. Intraday Trend
    if (url.includes('/api/market/trend/')) {
        const symbol = url.split('/').pop() || '000001.SH';
        // Use 1m kline as trend data source
        const kline = await loadMockKlineData(symbol, '1m');
        // Simplify for trend: just timestamp and close price
        const _trendData = kline.candles.slice(0, 240).map(c => ({
            timestamp: c.timestamp,
            price: c.close
        })).reverse(); // Mock data generation is reverse time usually? check generateMockCandles implementation. 
        // generateMockCandles pushes from count-1 to 0 (past to present). So it's chronological.
        // Wait, generateMockCandles loop: for (let i = count - 1; i >= 0; i--) { timestamp = now - i * interval }
        // So i=count-1 is oldest. i=0 is now.
        // push order: oldest first. So it is chronological. 
        // However, let's just return what generateMockCandles returns.
        
        return toMockResult<T>(createMockResponse({
            symbol,
            lastClose: kline.candles[0].open * 0.98, // approximate
            data: kline.candles.map(c => c.close) // Simpler trend array
        }));
    }

    // 11. Technical Indicators
    if (url.includes('/api/strategy/v2/indicators')) {
      return toMockResult<T>(createMockResponse([
        { name: 'RSI', value: '65.2', signal: '超买', signalType: 'fall' },
        { name: 'MACD', value: '+0.45', signal: '金叉', signalType: 'rise' },
        { name: 'KDJ', value: '78.5', signal: '中性', signalType: 'neutral' },
        { name: 'BOLL', value: '上轨', signal: '强势', signalType: 'rise' }
      ]));
    }

    // 12. Portfolio Summary & Positions
    if (url.includes('/api/portfolio/v2/summary')) {
      return toMockResult<T>(createMockResponse({
        total_assets: 1256789,
        daily_pnl: 8450,
        daily_pnl_percent: 0.68,
        position_ratio: 65,
        available_cash: 439339,
        positions: [
          { symbol: '600519', name: '贵州茅台', quantity: 100, cost: 1800, price: 1850, pnl: 5000, pnl_percent: 2.78 },
          { symbol: '300750', name: '宁德时代', quantity: 200, cost: 230, price: 245, pnl: 3000, pnl_percent: 6.52 }
        ]
      }));
    }

    // 13. Watchlist Data
    if (url.includes('/api/portfolio/v2/watchlist')) {
      return toMockResult<T>(createMockResponse([
        { 
          id: 'default', 
          name: '默认自选', 
          stocks: [
            { symbol: '600519', name: '贵州茅台', price: '1850', change: 2.1 },
            { symbol: '000001', name: '平安银行', price: '12.45', change: 1.2 }
          ] 
        },
        { 
          id: 'tech', 
          name: '科技核心', 
          stocks: [
            { symbol: '300750', name: '宁德时代', price: '245', change: 3.5 },
            { symbol: '002230', name: '科大讯飞', price: '45.6', change: -1.2 }
          ] 
        }
      ]));
    }

    // 14. Data Quality Monitoring
    if (url.includes('/api/monitoring/v2/data-quality')) {
      return toMockResult<T>(createMockResponse({
        metrics: { integrity: 99.8, accuracy: 99.5, timeliness: 98.2, consistency: 99.1 },
        sources: [
          { name: '交易所实时行情', type: '实时', status: 'healthy', statusText: '正常', quality: 100 },
          { name: '财务报表数据库', type: '离线', status: 'healthy', statusText: '正常', quality: 99.5 },
          { name: '问财三方数据', type: 'API', status: 'warning', statusText: '稍慢', quality: 85.2 }
        ]
      }));
    }

    // Default fallback
    console.warn(`[Mock API] No handler for GET ${url}, returning generic mock.`);
      return { ...createMockResponse({}), data: { url, method: 'GET', ...params } } as T;
  },

  async post<T = UnifiedResponse<unknown>>(url: string, data?: unknown, config?: MockRequestConfig): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] POST request to ${url} with data:`, data, 'and config:', config);
    return { ...createMockResponse({}), data: { url, method: 'POST', requestData: data, ...getRequestParams(config) } } as T;
  },

  async put<T = UnifiedResponse<unknown>>(url: string, data?: unknown, config?: MockRequestConfig): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] PUT request to ${url} with data:`, data, 'and config:', config);
    return { ...createMockResponse({}), data: { url, method: 'PUT', requestData: data, ...getRequestParams(config) } } as T;
  },

  async patch<T = UnifiedResponse<unknown>>(url: string, data?: unknown, config?: MockRequestConfig): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] PATCH request to ${url} with data:`, data, 'and config:', config);
    return { ...createMockResponse({}), data: { url, method: 'PATCH', requestData: data, ...getRequestParams(config) } } as T;
  },

  async delete<T = UnifiedResponse<unknown>>(url: string, config?: MockRequestConfig): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] DELETE request to ${url} with config:`, config);
    return { ...createMockResponse({}), data: { url, method: 'DELETE', ...getRequestParams(config) } } as T;
  },
};
