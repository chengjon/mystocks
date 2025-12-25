/**
 * Mock Fund Flow Data
 *
 * Used for fallback when API fails
 */

export default {
  success: true,
  code: 200,
  message: 'Mock data',
  data: {
    fundFlow: [
      {
        date: '2025-12-20',
        mainInflow: 500000000,
        mainOutflow: 300000000,
        netInflow: 200000000,
      },
      {
        date: '2025-12-21',
        mainInflow: 600000000,
        mainOutflow: 400000000,
        netInflow: 200000000,
      },
      {
        date: '2025-12-22',
        mainInflow: 700000000,
        mainOutflow: 500000000,
        netInflow: 200000000,
      },
      {
        date: '2025-12-23',
        mainInflow: 550000000,
        mainOutflow: 350000000,
        netInflow: 200000000,
      },
      {
        date: '2025-12-24',
        mainInflow: 650000000,
        mainOutflow: 450000000,
        netInflow: 200000000,
      },
      {
        date: '2025-12-25',
        mainInflow: 750000000,
        mainOutflow: 500000000,
        netInflow: 250000000,
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
