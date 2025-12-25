/**
 * Mock Market Overview Data
 *
 * Used for fallback when API fails
 */

export default {
  success: true,
  code: 200,
  message: 'Mock data',
  data: {
    marketStats: {
      totalStocks: 10,
      risingStocks: 10,
      fallingStocks: 0,
      avgChangePercent: 2.36,
    },
    topEtfs: [
      {
        symbol: '159583',
        name: '通信设备ETF',
        latestPrice: 2.076,
        changePercent: 3.39,
        volume: 594905,
      },
      {
        symbol: '159502',
        name: '标普生物科技ETF',
        latestPrice: 1.146,
        changePercent: 2.96,
        volume: 1130878,
      },
      {
        symbol: '159316',
        name: '恒生创新药ETF',
        latestPrice: 1.494,
        changePercent: 2.47,
        volume: 4197592,
      },
    ],
    chipRaces: [
      {
        symbol: '000555',
        name: '神州信息',
        raceAmount: 432653536.0,
        changePercent: 4.0,
      },
      {
        symbol: '688183',
        name: '生益电子',
        raceAmount: 306806979.3,
        changePercent: 19.99,
      },
      {
        symbol: '300476',
        name: '胜宏科技',
        raceAmount: 291165000.0,
        changePercent: 7.95,
      },
    ],
    longHuBang: [
      {
        symbol: '000063',
        name: '中兴通讯',
        netAmount: -420002995.03,
        reason: '2家机构卖出，成功率26.14%',
      },
      {
        symbol: '000572',
        name: '海马汽车',
        netAmount: -24678989.4,
        reason: '主力做T，成功率40.81%',
      },
      {
        symbol: '000592',
        name: '平潭发展',
        netAmount: 155910954.74,
        reason: '主力做T，成功率49.17%',
      },
    ],
    timestamp: '2025-12-25T13:47:41.694443',
  },
  timestamp: new Date().toISOString(),
  request_id: 'mock',
  errors: null,
};
