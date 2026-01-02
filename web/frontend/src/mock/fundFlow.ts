/**
 * Mock Fund Flow Data
 *
 * Used for fallback when API fails
 */

// The API returns: { success, code, message, data: { fundFlow: [...] }, timestamp, request_id, errors }
// data.fundFlow contains FundFlowItem[]
export default {
  success: true,
  code: 200,
  message: 'Mock data',
  data: {
    fundFlow: [
      {
        trade_date: '2025-12-20',
        main_net_inflow: 200000000,
        main_net_inflow_rate: 0.5,
        super_large_net_inflow: 100000000,
        large_net_inflow: 80000000,
        medium_net_inflow: 50000000,
        small_net_inflow: 30000000,
      },
      {
        trade_date: '2025-12-21',
        main_net_inflow: 200000000,
        main_net_inflow_rate: 0.45,
        super_large_net_inflow: 120000000,
        large_net_inflow: 90000000,
        medium_net_inflow: 60000000,
        small_net_inflow: 40000000,
      },
      {
        trade_date: '2025-12-22',
        main_net_inflow: 200000000,
        main_net_inflow_rate: 0.55,
        super_large_net_inflow: 110000000,
        large_net_inflow: 85000000,
        medium_net_inflow: 55000000,
        small_net_inflow: 35000000,
      },
      {
        trade_date: '2025-12-23',
        main_net_inflow: 200000000,
        main_net_inflow_rate: 0.48,
        super_large_net_inflow: 95000000,
        large_net_inflow: 75000000,
        medium_net_inflow: 50000000,
        small_net_inflow: 25000000,
      },
      {
        trade_date: '2025-12-24',
        main_net_inflow: 200000000,
        main_net_inflow_rate: 0.52,
        super_large_net_inflow: 105000000,
        large_net_inflow: 80000000,
        medium_net_inflow: 52000000,
        small_net_inflow: 28000000,
      },
      {
        trade_date: '2025-12-25',
        main_net_inflow: 250000000,
        main_net_inflow_rate: 0.6,
        super_large_net_inflow: 130000000,
        large_net_inflow: 100000000,
        medium_net_inflow: 60000000,
        small_net_inflow: 40000000,
      },
    ],
    total: 6,
    symbol: null,
    timeframe: null,
  },
  timestamp: new Date().toISOString(),
  request_id: 'mock',
  errors: null,
};
