export interface MarketHeatItem {
  name: string
  change: number
  amount?: number
}

export interface FundFlowItem {
  amount: number
  change?: number
  monthly?: number
  percentage?: number
}

export interface MarketData {
  shanghai: { index: string; change: string }
  shenzhen: { index: string; change: string }
  chuangye: { index: string; change: string }
  fundFlow: {
    hgt: FundFlowItem
    sgt: FundFlowItem
    northTotal: FundFlowItem
    mainForce: FundFlowItem
  }
  northFund: { amount: string; change: number }
  stocks: { up: number; down: number }
  volume: { amount: string }
}

export interface TopStock {
  code: string
  name: string
  price: string
  change: number
}

export interface IndicatorItem {
  name: string
  value: string
  trend: string
  signal: string
}

export interface SystemHealthItem {
  name: string
  status: string
  value: string
}

export interface StressTestResult {
  drawdown: number
  var95: number
  concentrationRisk: number
  timestamp: string
}
