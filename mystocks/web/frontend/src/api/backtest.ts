/**
 * 回测 API
 *
 * 与后端 strategy_api.py 回测接口对接
 */

import request from '@/utils/request'

export interface BacktestConfig {
  name: string
  strategy_id: number
  start_date: string
  end_date: string
  initial_cash: number
  commission_rate: number
  stamp_tax_rate: number
  slippage_rate: number
}

export const backtestApi = {
  // 执行回测
  runBacktest(data: BacktestConfig) {
    return request.post('/api/v1/strategy/backtest/run', data)
  },

  // 获取回测结果列表
  listBacktestResults(params?: { strategy_id?: number; page?: number; page_size?: number }) {
    return request.get('/api/v1/strategy/backtest/results', { params })
  },

  // 获取回测详情
  getBacktestResult(id: number) {
    return request.get(`/api/v1/strategy/backtest/results/${id}`)
  },

  // 获取回测图表数据
  getBacktestChartData(id: number) {
    return request.get(`/api/v1/strategy/backtest/results/${id}/chart-data`)
  }
}
