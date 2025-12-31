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
        tradeDate: '2025-12-20',
        mainNetInflow: 200000000,
        mainNetInflowRate: 0.5,
        superLargeNetInflow: 100000000,
        largeNetInflow: 80000000,
        mediumNetInflow: 50000000,
        smallNetInflow: 30000000,
      },
      {
        tradeDate: '2025-12-21',
        mainNetInflow: 200000000,
        mainNetInflowRate: 0.45,
        superLargeNetInflow: 120000000,
        largeNetInflow: 90000000,
        mediumNetInflow: 60000000,
        smallNetInflow: 40000000,
      },
      {
        tradeDate: '2025-12-22',
        mainNetInflow: 200000000,
        mainNetInflowRate: 0.55,
        superLargeNetInflow: 110000000,
        largeNetInflow: 85000000,
        mediumNetInflow: 55000000,
        smallNetInflow: 35000000,
      },
      {
        tradeDate: '2025-12-23',
        mainNetInflow: 200000000,
        mainNetInflowRate: 0.48,
        superLargeNetInflow: 95000000,
        largeNetInflow: 75000000,
        mediumNetInflow: 50000000,
        smallNetInflow: 25000000,
      },
      {
        tradeDate: '2025-12-24',
        mainNetInflow: 200000000,
        mainNetInflowRate: 0.52,
        superLargeNetInflow: 105000000,
        largeNetInflow: 80000000,
        mediumNetInflow: 52000000,
        smallNetInflow: 28000000,
      },
      {
        tradeDate: '2025-12-25',
        mainNetInflow: 250000000,
        mainNetInflowRate: 0.6,
        superLargeNetInflow: 130000000,
        largeNetInflow: 100000000,
        mediumNetInflow: 60000000,
        smallNetInflow: 40000000,
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
