/**
 * Dashboard相关API接口
 */

import request from './index.js'

export default {
  /**
   * 获取全市场涨跌分布统计
   */
  getPriceDistribution() {
    return request({
      url: '/api/data/markets/price-distribution',
      method: 'get'
    })
  },

  /**
   * 获取热门行业TOP5表现数据
   */
  getHotIndustries(limit = 5) {
    return request({
      url: '/api/data/markets/hot-industries',
      method: 'get',
      params: { limit }
    })
  },

  /**
   * 获取热门概念TOP5表现数据
   */
  getHotConcepts(limit = 5) {
    return request({
      url: '/api/data/markets/hot-concepts',
      method: 'get',
      params: { limit }
    })
  },

  /**
   * 获取市场概览数据
   */
  getMarketOverview() {
    return request({
      url: '/api/data/markets/overview',
      method: 'get'
    })
  },

  /**
   * 获取自选股列表
   */
  getWatchlist() {
    return request({
      url: '/api/watchlist/',
      method: 'get'
    })
  },

  /**
   * 添加股票到自选股
   */
  addToWatchlist(data) {
    return request({
      url: '/api/watchlist/add',
      method: 'post',
      data
    })
  },

  /**
   * 从自选股中移除股票
   */
  removeFromWatchlist(symbol) {
    return request({
      url: `/api/watchlist/remove/${symbol}`,
      method: 'delete'
    })
  },

  /**
   * 检查股票是否在自选股中
   */
  checkInWatchlist(symbol) {
    return request({
      url: `/api/watchlist/check/${symbol}`,
      method: 'get'
    })
  },

  /**
   * 获取股票基本信息
   */
  getStocksBasic(params = {}) {
    return request({
      url: '/api/data/stocks/basic',
      method: 'get',
      params
    })
  }
}
