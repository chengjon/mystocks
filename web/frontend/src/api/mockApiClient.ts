// web/frontend/src/api/mockApiClient.ts

import { UnifiedResponse } from './apiClient';
import mockDashboard from '../mock/mockDashboard';
import { loadMockKlineData, loadMockIndicators } from './mockKlineData';

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

export const mockApiClient = {
  async get<T = UnifiedResponse>(url: string, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.log(`[Mock API] GET ${url}`, config);

    const params = config?.params || {};

    // --- Dashboard & Market Routes ---

    // 1. Market Overview (ETF List / Indices)
    if (url.includes('/api/market/v2/etf/list')) {
      // Mocking indices based on limit or sort
      const indices = [
        { symbol: '000001.SH', name: '上证指数', latest_price: 3128.45, change_percent: 0.85, volume: 1000000 },
        { symbol: '399001.SZ', name: '深证成指', latest_price: 10245.67, change_percent: 1.23, volume: 2000000 },
        { symbol: '399006.SZ', name: '创业板指', latest_price: 2156.89, change_percent: -0.45, volume: 500000 },
        { symbol: '510300.SH', name: '沪深300', latest_price: 3800.00, change_percent: 0.50, volume: 800000 },
      ];
      return createMockResponse(indices) as any;
    }

    // 2. Fund Flow
    if (url.includes('/api/market/fund-flow')) {
      // Use mockDashboard data or generate consistent structure
      const flowData = {
        hgt: { amount: 28.6, change: 5.2 },
        sgt: { amount: 30.2, change: 8.9 },
        northTotal: { amount: 58.8, monthly: 1256 },
        mainForce: { amount: 126.5, percentage: 68 }
      };
      return createMockResponse(flowData) as any;
    }

    // 3. Industry Flow
    if (url.includes('/api/market/industry/flow')) {
      // Use mockDashboard logic
      const sectors = mockDashboard.getLeadingSectors();
      return createMockResponse(sectors) as any;
    }

    // 4. Stock Flow Ranking
    if (url.includes('/api/monitoring/stock/flow/ranking')) {
      const stocks = [
        { code: '600519', name: '贵州茅台', amount: 12.5, change: 2.1 },
        { code: '300750', name: '宁德时代', amount: 8.9, change: 3.5 },
        { code: '600028', name: '中国石化', amount: -5.2, change: -1.8 },
        { code: '600036', name: '招商银行', amount: 6.7, change: 1.2 },
        { code: '000002', name: '万科A', amount: -3.1, change: -0.9 }
      ];
      return createMockResponse(stocks) as any;
    }

    // 5. Long Hu Bang (Dragon Tiger List)
    if (url.includes('/api/market/long-hu-bang')) {
      const lhb = [
        { code: '000001', name: '平安银行', reason: '日涨幅偏离值达7%', amount: 12000, change_percent: 10.01 },
        { code: '600000', name: '浦发银行', reason: '连续三个交易日内，涨幅偏离值累计达20%', amount: 8500, change_percent: 9.98 }
      ];
      return createMockResponse(lhb) as any;
    }

    // 6. Block Trading
    if (url.includes('/api/market/v2/block-trading')) {
      const block = [
        { code: '600519', name: '贵州茅台', price: 1800.00, amount: 5000, buyer: '机构专用', seller: '中信证券北京总部' },
        { code: '300750', name: '宁德时代', price: 240.00, amount: 3000, buyer: '深股通专用', seller: '机构专用' }
      ];
      return createMockResponse(block) as any;
    }

    // 7. K-Line Data
    if (url.includes('/api/market/kline')) {
        const symbol = params.symbol || '000001.SH';
        const period = params.period || '1d';
        const kline = await loadMockKlineData(symbol, period);
        return createMockResponse(kline.candles) as any;
    }

    // 8. Real-time Quote
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
        return createMockResponse(quote) as any;
    }

    // 9. Intraday Trend
    if (url.includes('/api/market/trend/')) {
        const symbol = url.split('/').pop() || '000001.SH';
        // Use 1m kline as trend data source
        const kline = await loadMockKlineData(symbol, '1m');
        // Simplify for trend: just timestamp and close price
        const trendData = kline.candles.slice(0, 240).map(c => ({
            timestamp: c.timestamp,
            price: c.close
        })).reverse(); // Mock data generation is reverse time usually? check generateMockCandles implementation. 
        // generateMockCandles pushes from count-1 to 0 (past to present). So it's chronological.
        // Wait, generateMockCandles loop: for (let i = count - 1; i >= 0; i--) { timestamp = now - i * interval }
        // So i=count-1 is oldest. i=0 is now.
        // push order: oldest first. So it is chronological. 
        // However, let's just return what generateMockCandles returns.
        
        return createMockResponse({
            symbol,
            lastClose: kline.candles[0].open * 0.98, // approximate
            data: kline.candles.map(c => c.close) // Simpler trend array
        }) as any;
    }

    // 10. Technical Indicators
    if (url.includes('/api/strategy/v2/indicators')) {
      return createMockResponse([
        { name: 'RSI', value: '65.2', signal: '超买', signalType: 'fall' },
        { name: 'MACD', value: '+0.45', signal: '金叉', signalType: 'rise' },
        { name: 'KDJ', value: '78.5', signal: '中性', signalType: 'neutral' },
        { name: 'BOLL', value: '上轨', signal: '强势', signalType: 'rise' }
      ]) as any;
    }

    // 11. Portfolio Summary & Positions
    if (url.includes('/api/portfolio/v2/summary')) {
      return createMockResponse({
        total_assets: 1256789,
        daily_pnl: 8450,
        daily_pnl_percent: 0.68,
        position_ratio: 65,
        available_cash: 439339,
        positions: [
          { symbol: '600519', name: '贵州茅台', quantity: 100, cost: 1800, price: 1850, pnl: 5000, pnl_percent: 2.78 },
          { symbol: '300750', name: '宁德时代', quantity: 200, cost: 230, price: 245, pnl: 3000, pnl_percent: 6.52 }
        ]
      }) as any;
    }

    // 12. Watchlist Data
    if (url.includes('/api/portfolio/v2/watchlist')) {
      return createMockResponse([
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
      ]) as any;
    }

    // 13. Data Quality Monitoring
    if (url.includes('/api/monitoring/v2/data-quality')) {
      return createMockResponse({
        metrics: { integrity: 99.8, accuracy: 99.5, timeliness: 98.2, consistency: 99.1 },
        sources: [
          { name: '交易所实时行情', type: '实时', status: 'healthy', statusText: '正常', quality: 100 },
          { name: '财务报表数据库', type: '离线', status: 'healthy', statusText: '正常', quality: 99.5 },
          { name: '问财三方数据', type: 'API', status: 'warning', statusText: '稍慢', quality: 85.2 }
        ]
      }) as any;
    }

    // Default fallback
    console.warn(`[Mock API] No handler for GET ${url}, returning generic mock.`);
    return { ...createMockResponse({}), data: { url, method: 'GET', ...config?.params } } as T;
  },

  async post<T = UnifiedResponse>(url: string, data?: any, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] POST request to ${url} with data:`, data, 'and config:', config);
    return { ...createMockResponse({}), data: { url, method: 'POST', requestData: data, ...config?.params } } as T;
  },

  async put<T = UnifiedResponse>(url: string, data?: any, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] PUT request to ${url} with data:`, data, 'and config:', config);
    return { ...createMockResponse({}), data: { url, method: 'PUT', requestData: data, ...config?.params } } as T;
  },

  async patch<T = UnifiedResponse>(url: string, data?: any, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] PATCH request to ${url} with data:`, data, 'and config:', config);
    return { ...createMockResponse({}), data: { url, method: 'PATCH', requestData: data, ...config?.params } } as T;
  },

  async delete<T = UnifiedResponse>(url: string, config?: any): Promise<T> {
    await simulateNetworkDelay();
    console.warn(`[Mock API] DELETE request to ${url} with config:`, config);
    return { ...createMockResponse({}), data: { url, method: 'DELETE', ...config?.params } } as T;
  },
};
