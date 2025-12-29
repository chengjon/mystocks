/**
 * Services统一导出
 * 提供所有API服务的统一访问接口
 */

// 导出API客户端
export {
  apiClient,
  APIClient,
  setAuthToken,
  getAuthToken,
  clearAuthToken,
  initAuthToken,
  type APIResponse,
  type APIErrorResponse,
  type RequestConfig,
} from './api-client';

// 导出Market Service
export {
  marketService,
  MarketService,
  type StockSymbol,
  type StockQuote,
  type KlineData,
  type WatchlistItem,
} from './market.service';

// 导出Technical Service
export {
  technicalService,
  TechnicalService,
  type IndicatorData,
  type MAData,
  type MACDData,
  type KDJData,
  type BOLLData,
} from './technical.service';

// 导出Trade Service
export {
  tradeService,
  TradeService,
  OrderType,
  OrderDirection,
  OrderStatus,
  type Order,
  type Position,
  type AccountBalance,
  type TradeRecord,
} from './trade.service';

/**
 * 使用示例:
 *
 * import { marketService, technicalService, tradeService } from '@/services';
 *
 * // 获取股票列表
 * const stocks = await marketService.getStockList({ market: 'SZ' });
 *
 * // 获取MA指标
 * const maData = await technicalService.getMA({ symbol: '000001.SZ', periods: [5, 10, 20] });
 *
 * // 创建订单
 * const order = await tradeService.createOrder({
 *   symbol: '000001.SZ',
 *   type: OrderType.LIMIT,
 *   direction: OrderDirection.BUY,
 *   price: 10.50,
 *   quantity: 100,
 * });
 */
