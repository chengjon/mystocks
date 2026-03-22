export interface ETFItem {
  code: string
  name: string
  type: string
  price: number
  nav: number
  change: number
  changePercent: number
  volume: number
  amount: number
  premium: number
  status: 'trading' | 'suspended'
}

export interface EtfCategory {
  key: string
  name: string
  description: string
  count: number
  avgVolume: number
}

export interface EtfMarketOverview {
  totalAssets: number
  totalProducts: number
  dailyVolume: number
  avgChange: number
}

function createEtfItem(partial: Partial<ETFItem> & Pick<ETFItem, 'code' | 'name'>): ETFItem {
  return {
    code: partial.code,
    name: partial.name,
    type: partial.type ?? '宽基',
    price: partial.price ?? 1,
    nav: partial.nav ?? partial.price ?? 1,
    change: partial.change ?? 0,
    changePercent: partial.changePercent ?? 0,
    volume: partial.volume ?? 0,
    amount: partial.amount ?? 0,
    premium: partial.premium ?? 0,
    status: partial.status ?? 'trading'
  }
}

export function createEtfMarketOverview(): EtfMarketOverview {
  return {
    totalAssets: 2_450_000_000_000,
    totalProducts: 1260,
    dailyVolume: 185_000_000_000,
    avgChange: 0.86
  }
}

export function createEtfCategories(): EtfCategory[] {
  return [
    { key: 'broad-market', name: '宽基ETF', description: '覆盖主要指数与核心市场敞口', count: 3, avgVolume: 82_000_000 },
    { key: 'sector', name: '行业ETF', description: '聚焦高景气行业轮动机会', count: 3, avgVolume: 56_000_000 },
    { key: 'cross-border', name: '跨境ETF', description: '跟踪海外市场和跨境主题', count: 2, avgVolume: 41_000_000 }
  ]
}

export function createEtfDataByCategory(): Record<string, ETFItem[]> {
  return {
    'broad-market': [
      createEtfItem({ code: '510300', name: '沪深300ETF', type: '宽基', price: 3.812, nav: 3.801, change: 0.032, changePercent: 0.85, volume: 92_500_000, amount: 352_000_000, premium: 0.29 }),
      createEtfItem({ code: '510500', name: '中证500ETF', type: '宽基', price: 5.216, nav: 5.198, change: 0.054, changePercent: 1.05, volume: 88_000_000, amount: 459_000_000, premium: 0.35 }),
      createEtfItem({ code: '159915', name: '创业板ETF', type: '成长', price: 2.447, nav: 2.438, change: -0.012, changePercent: -0.49, volume: 65_400_000, amount: 160_000_000, premium: 0.37 })
    ],
    sector: [
      createEtfItem({ code: '512480', name: '半导体ETF', type: '行业', price: 1.925, nav: 1.910, change: 0.044, changePercent: 2.34, volume: 71_200_000, amount: 138_000_000, premium: 0.79 }),
      createEtfItem({ code: '515790', name: '光伏ETF', type: '行业', price: 0.882, nav: 0.876, change: 0.018, changePercent: 2.08, volume: 48_600_000, amount: 42_000_000, premium: 0.68 }),
      createEtfItem({ code: '516160', name: '新能源车ETF', type: '行业', price: 1.134, nav: 1.129, change: 0.015, changePercent: 1.34, volume: 49_000_000, amount: 56_000_000, premium: 0.44 })
    ],
    'cross-border': [
      createEtfItem({ code: '513100', name: '纳指ETF', type: '跨境', price: 1.866, nav: 1.852, change: 0.026, changePercent: 1.41, volume: 35_100_000, amount: 65_000_000, premium: 0.76 }),
      createEtfItem({ code: '513500', name: '标普500ETF', type: '跨境', price: 1.642, nav: 1.636, change: 0.017, changePercent: 1.05, volume: 28_400_000, amount: 47_000_000, premium: 0.37 })
    ]
  }
}

export function createTopGainers(): ETFItem[] {
  return [
    createEtfItem({ code: '512480', name: '半导体ETF', changePercent: 2.34, volume: 71_200_000 }),
    createEtfItem({ code: '515790', name: '光伏ETF', changePercent: 2.08, volume: 48_600_000 }),
    createEtfItem({ code: '513100', name: '纳指ETF', changePercent: 1.41, volume: 35_100_000 })
  ]
}

export function createTopVolume(): ETFItem[] {
  return [
    createEtfItem({ code: '510300', name: '沪深300ETF', volume: 92_500_000 }),
    createEtfItem({ code: '510500', name: '中证500ETF', volume: 88_000_000 }),
    createEtfItem({ code: '512480', name: '半导体ETF', volume: 71_200_000 })
  ]
}
