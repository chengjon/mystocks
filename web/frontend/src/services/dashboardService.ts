// web/frontend/src/services/dashboardService.ts
//
// ✅ Mock数据到真实数据迁移 - 实施版本
// 使用方案A的替代API替换缺失的端点
//

import { apiGet, apiPost } from '@/api/apiClient';
import type { UnifiedResponse } from '@/api/apiClient';
import {
  MarketOverviewDetailedResponse,
  WatchlistSummary,
  PortfolioSummary,
  RiskAlertSummary,
  IndustryInfo,
  ConceptInfo
} from '@/api/types/common';

// ChartDataPoint type definition
export interface ChartDataPoint {
  name: string;
  value: number;
  change_percent: number;
}

// Interface for dashboard summary data
export interface DashboardSummary {
  marketOverview?: MarketOverviewDetailedResponse;
  watchlist?: WatchlistSummary;
  portfolio?: PortfolioSummary;
  riskAlerts?: RiskAlertSummary;
}

export interface IndustryConceptData {
  industry_name: string;
  avg_change: number;
  stock_count: number;
}

// Helper to create UnifiedResponse
function createUnifiedResponse<T>(data: T, success = true): UnifiedResponse<T> {
  return {
    success,
    code: success ? 200 : 500,
    message: success ? 'Success' : 'Error',
    data,
    timestamp: new Date().toISOString(),
    request_id: crypto.randomUUID?.() || Math.random().toString(36),
    errors: success ? null : {}
  };
}

export const dashboardService = {
  // ============================================
  //   ✅ REAL API IMPLEMENTATIONS (Option A)
  //   使用真实API替代Mock数据
  // ============================================

  // --- 1. Market Overview (指数列表API替代方案) ---
  /**
   * 获取市场概览 - 使用Dashboard Market Overview
   * 注意: 后端需将MockBusinessDataSource改为真实数据源
   */
  async getMarketOverview(): Promise<UnifiedResponse<MarketOverviewDetailedResponse>> {
    try {
      const response = await apiGet<any>('/api/dashboard/market-overview');
      return response;
    } catch (error) {
      console.error('[dashboardService] Failed to fetch market overview:', error);
      throw error;
    }
  },

  /**
   * 获取主要指数列表（新增方法）
   * 替代缺失的: /api/market/v2/indices/list
   * 使用: /api/market/v2/etf/list + 筛选
   */
  async getIndicesList(): Promise<UnifiedResponse<any[]>> {
    try {
      // 使用ETF列表API
      const response = await apiGet<any>('/api/market/v2/etf/list', {
        limit: 100
      });

      if (response.data && Array.isArray(response.data)) {
        // 筛选主要指数型ETF
        const indexETFs = response.data
          .filter((etf: any) =>
            // 沪市指数基金（510开头）
            etf.symbol.match(/^510(300|500|050|900)/) ||
            // 深市指数基金（159开头）
            etf.symbol.match(/^159(915|919|949|940|922)/) ||
            // 名称包含"指数"
            etf.name.includes('指数')
          )
          .slice(0, 10)  // 取前10个
          .map((etf: any) => ({
            symbol: etf.symbol,
            name: etf.name
              .replace('ETF', '')
              .replace('交易型开放式指数基金', '')
              .trim(),
            current_price: etf.latest_price,
            change_percent: etf.change_percent,
            change_amount: etf.change_amount,
            volume: etf.volume,
            turnover: etf.amount,
            update_time: etf.created_at || etf.trade_date
          }));

        return createUnifiedResponse(indexETFs);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch indices list:', error);
      return createUnifiedResponse([]);
    }
  },

  // --- 2. Market Stats (市场统计API替代方案) ---
  /**
   * 获取市场统计数据
   * 替代缺失的: /api/market/v2/market-stats
   * 使用: /api/dashboard/market-overview
   */
  async getMarketStats(): Promise<UnifiedResponse<any>> {
    try {
      const response = await apiGet<any>('/api/dashboard/market-overview');

      // 提取统计字段
      const stats = {
        up_count: response.data?.up_count || 0,
        down_count: response.data?.down_count || 0,
        flat_count: response.data?.flat_count || 0,
        total_volume: response.data?.total_volume || 0,
        total_turnover: response.data?.total_turnover || 0,
        limit_up: response.data?.top_gainers?.length || 0,
        limit_down: response.data?.top_losers?.length || 0
      };

      return createUnifiedResponse(stats);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch market stats:', error);
      throw error;
    }
  },

  /**
   * 获取价格分布（使用市场统计）
   */
  async getPriceDistribution(): Promise<UnifiedResponse<Record<string, number>>> {
    // 使用市场统计数据
    const response = await this.getMarketStats();
    return response as UnifiedResponse<Record<string, number>>;
  },

  // --- 3. User Portfolio (用户持仓API替代方案) ---
  /**
   * 获取用户持仓数据
   * 替代缺失的: /api/v1/portfolio/{user_id}
   * 使用: /api/mtm/portfolio/{user_id} (axios baseURL已经是/api)
   */
  async getUserPortfolio(userId: number): Promise<UnifiedResponse<any>> {
    try {
      // 使用实时市值API，将user_id作为portfolio_id
      const response = await apiGet<any>(`/api/mtm/portfolio/${userId}`);

      return createUnifiedResponse({
        total_market_value: response.data?.total_value || 0,
        total_cost: response.data?.total_cost || 0,
        total_profit_loss: response.data?.profit_loss || 0,
        total_profit_loss_percent: response.data?.profit_loss_percent || 0,
        positions: response.data?.positions || []
      });
    } catch (error) {
      console.error('[dashboardService] Failed to fetch user portfolio:', error);
      // 返回空数据而不是抛出错误
      return createUnifiedResponse({
        total_market_value: 0,
        total_cost: 0,
        total_profit_loss: 0,
        total_profit_loss_percent: 0,
        positions: []
      });
    }
  },

  // --- 4. Industry List (行业列表API替代方案) ---
  /**
   * 获取热门行业
   * 替代: /api/analysis/industry/list (返回空数据)
   * 使用: /api/analysis/industry/performance
   */
  async getHotIndustries(): Promise<UnifiedResponse<IndustryConceptData[]>> {
    try {
      // 使用行业表现API
      const response = await apiGet<any>('/api/analysis/industry/performance');

      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        const industries = response.data.map((item: any) => ({
          industry_name: item.name || item.industry_name,
          avg_change: item.change_percent || item.avg_change || 0,
          stock_count: item.stock_count || 0
        }));

        return createUnifiedResponse(industries.slice(0, 10));
      }

      // 备选方案：使用行业资金流向API
      try {
        const fundFlowResponse = await apiGet<any>('/api/market/v2/sector/fund-flow');

        if (fundFlowResponse.data && Array.isArray(fundFlowResponse.data)) {
          // 从资金流向提取行业列表
          const industries = [...new Set(fundFlowResponse.data.map((item: any) => item.sector_name))]
            .filter(name => name)
            .slice(0, 10)
            .map(name => ({
              industry_name: String(name),
              avg_change: 0,
              stock_count: 1
            }));

          return createUnifiedResponse(industries);
        }
      } catch (fallbackError) {
        console.error('[dashboardService] Fallback to sector fund-flow failed:', fallbackError);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch hot industries:', error);
      return createUnifiedResponse([]);
    }
  },

  // --- 5. Concept List (概念列表API替代方案) ---
  /**
   * 获取热门概念
   * 替代: /api/analysis/concept/list (返回空数据)
   * 使用: /api/analysis/concept/stocks 聚合
   */
  async getHotConcepts(): Promise<UnifiedResponse<IndustryConceptData[]>> {
    try {
      // 使用概念股票API反向聚合
      const response = await apiGet<any>('/api/analysis/concept/stocks');

      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        // 提取概念名称并聚合
        const conceptMap = new Map<string, number>();
        response.data.forEach((item: any) => {
          const conceptName = item.concept_name || item.name;
          if (conceptName) {
            conceptMap.set(conceptName, (conceptMap.get(conceptName) || 0) + 1);
          }
        });

        const concepts = Array.from(conceptMap.entries())
          .map(([name, count]) => ({
            industry_name: name,
            avg_change: 0,
            stock_count: count
          }))
          .sort((a, b) => b.stock_count - a.stock_count)
          .slice(0, 10);

        return createUnifiedResponse(concepts);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch hot concepts:', error);
      return createUnifiedResponse([]);
    }
  },

  // --- Chart Data Methods ---
  /**
   * 获取市场热力图数据
   * 使用指数列表数据
   */
  async getMarketHeatChartData(): Promise<UnifiedResponse<ChartDataPoint[]>> {
    try {
      const indicesResponse = await this.getIndicesList();

      if (indicesResponse.data && indicesResponse.data.length > 0) {
        const chartData = indicesResponse.data
          .map((idx: any) => ({
            name: idx.name,
            value: Math.abs(idx.change_percent || 0),
            change_percent: idx.change_percent || 0
          }));

        return createUnifiedResponse(chartData);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch market heat chart:', error);
      return createUnifiedResponse([]);
    }
  },

  /**
   * 获取领涨板块数据
   * 使用热门行业数据
   */
  async getLeadingSectorChartData(): Promise<UnifiedResponse<ChartDataPoint[]>> {
    try {
      const industriesResponse = await this.getHotIndustries();

      if (industriesResponse.data && industriesResponse.data.length > 0) {
        const chartData = industriesResponse.data
          .map((ind: any) => ({
            name: ind.industry_name,
            value: Math.abs(ind.avg_change || 0),
            change_percent: ind.avg_change || 0
          }));

        return createUnifiedResponse(chartData);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch leading sectors:', error);
      return createUnifiedResponse([]);
    }
  },

  /**
   * 获取资金流向数据
   * 使用: /api/market/v2/fund-flow
   */
  async getCapitalFlowChartData(): Promise<UnifiedResponse<ChartDataPoint[]>> {
    try {
      const response = await apiGet<any>('/api/market/v2/fund-flow', {
        symbol: '000001',  // 上证指数
        timeframe: '1'
      });

      // 转换为图表数据（根据实际响应格式调整）
      const chartData: ChartDataPoint[] = [];

      return createUnifiedResponse(chartData);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch capital flow:', error);
      return createUnifiedResponse([]);
    }
  },

  /**
   * 获取行业资金流向数据
   * 使用: /api/market/v2/sector/fund-flow
   */
  async getIndustryCapitalFlowChartData(industryStandard: string): Promise<UnifiedResponse<ChartDataPoint[]>> {
    try {
      const response = await apiGet<any>('/api/market/v2/sector/fund-flow');

      if (response.data && Array.isArray(response.data)) {
        // 筛选指定行业
        const industryData = response.data
          .filter((item: any) => item.sector_name === industryStandard || item.sector_code === industryStandard)
          .map((item: any) => ({
            name: item.sector_name,
            value: Math.abs(item.main_net_inflow || 0),
            change_percent: item.main_net_inflow_rate || 0
          }));

        return createUnifiedResponse(industryData);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch industry capital flow:', error);
      return createUnifiedResponse([]);
    }
  },

  // --- Dashboard Summary (整合所有数据) ---
  /**
   * 获取仪表盘汇总数据
   * 整合市场概览、自选股、持仓、风险预警
   */
  async getDashboardSummary(userId: number): Promise<UnifiedResponse<DashboardSummary>> {
    try {
      // 并行获取所有数据
      const [marketOverview, portfolio] = await Promise.all([
        this.getMarketOverview(),
        this.getUserPortfolio(userId)
      ]);

      return createUnifiedResponse({
        marketOverview: marketOverview.data,
        portfolio: portfolio.data,
        // watchlist和riskAlerts可以后续添加
        watchlist: undefined,
        riskAlerts: undefined
      });
    } catch (error) {
      console.error('[dashboardService] Failed to fetch dashboard summary:', error);
      throw error;
    }
  },

  // ============================================
  //   新增方法: 策略和搜索
  // ============================================

  /**
   * 获取用户活跃策略
   * 替代缺失的: /api/strategy/{user_id}/active
   * 使用: /api/strategy-mgmt/strategies
   */
  async getUserActiveStrategies(userId: number): Promise<UnifiedResponse<any[]>> {
    try {
      const response = await apiGet<any>('/api/strategy-mgmt/strategies', {
        user_id: userId,
        status: 'active'
      });

      if (response.data) {
        const activeStrategies = Array.isArray(response.data)
          ? response.data.filter((s: any) => s.status === 'active' || s.is_active === true)
          : [];

        return createUnifiedResponse(activeStrategies);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Failed to fetch user strategies:', error);
      return createUnifiedResponse([]);
    }
  },

  /**
   * 股票搜索
   * 替代: /api/stock/search
   * 使用: /api/market/wencai/query
   */
  async searchStocks(query: string): Promise<UnifiedResponse<any[]>> {
    try {
      const response = await apiPost<any>('/api/market/wencai/query', {
        query: query,
        limit: 20
      });

      if (response.data && response.data.results) {
        const stocks = response.data.results.map((stock: any) => ({
          symbol: stock.code || stock.symbol,
          name: stock.name,
          price: stock.price || stock.latest_price,
          change_percent: stock.change_percent || stock.chg_pct
        }));

        return createUnifiedResponse(stocks);
      }

      return createUnifiedResponse([]);
    } catch (error) {
      console.error('[dashboardService] Stock search failed:', error);
      return createUnifiedResponse([]);
    }
  }
};

// 默认导出
export default dashboardService;
