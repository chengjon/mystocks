/**
 * Mock数据文件: Dashboard
 * JavaScript版本 - 为Vue组件提供Mock数据
 *
 * 提供接口:
 * 1. getDashboardStats() -> Array - 获取Dashboard统计数据数组格式
 * 2. getMarketHeatData() -> Array - 获取市场热度数据（图表）
 * 3. getLeadingSectors() -> Array - 获取领涨板块数据（图表）
 * 4. getPriceDistribution() -> Array - 获取涨跌分布数据（图表）
 * 5. getCapitalFlowData() -> Array - 获取资金流向数据（图表）
 * 6. getDashboardIndustryData() -> Object - 获取行业资金流向数据
 * 7. getFavoriteStocks() -> Array - 获取自选股板块表现数据
 * 8. getStrategyStocks() -> Array - 获取策略选股板块表现数据
 * 9. getIndustryStocks() -> Array - 获取行业选股板块表现数据
 * 10. getConceptStocks() -> Array - 获取概念选股板块表现数据
 */

// 工具函数：生成随机数
const randomInt = (min, max) => Math.floor(Math.random() * (max - min + 1)) + min
const randomFloat = (min, max, decimals = 2) => parseFloat((Math.random() * (max - min) + min).toFixed(decimals))

// 工具函数：格式化价格
const formatPrice = () => randomFloat(10, 2000, 2)

// 工具函数：格式化百分比
const formatPercent = () => randomFloat(-5, 8, 2)

/**
 * 获取Dashboard专用的统计数据数组格式
 * 对应Dashboard.vue中期望的stats数组格式
 */
export function getDashboardStats() {
  const currentTime = new Date().toLocaleString('zh-CN')

  return [
    {
      title: "总股票数",
      value: "4,526",
      trend: "较昨日 +12",
      trendClass: "up",
      icon: "TrendCharts",
      color: "#409eff"
    },
    {
      title: "活跃股票",
      value: "3,891",
      trend: "较昨日 +8",
      trendClass: "up",
      icon: "DataLine",
      color: "#67c23a"
    },
    {
      title: "数据更新",
      value: "刚刚",
      trend: "今日更新",
      trendClass: "neutral",
      icon: "Refresh",
      color: "#e6a23c"
    },
    {
      title: "系统状态",
      value: "正常",
      trend: "所有服务运行中",
      trendClass: "up",
      icon: "CircleCheck",
      color: "#67c23a"
    }
  ]
}

/**
 * 获取市场热度数据（图表数据）
 */
export function getMarketHeatData() {
  const sectors = ["人工智能", "新能源车", "芯片半导体", "医药生物", "5G通信", "军工", "白酒", "光伏"]

  return sectors.map(sector => ({
    name: sector,
    value: randomInt(60, 95)
  }))
}

/**
 * 获取领涨板块数据（图表数据）
 */
export function getLeadingSectors() {
  const sectors = ["人工智能", "芯片", "新能源", "医疗", "5G", "军工", "消费", "金融"]

  return sectors.map(sector => ({
    name: sector,
    change: randomFloat(2.0, 8.5)
  }))
}

/**
 * 获取涨跌分布数据（图表数据）
 */
export function getPriceDistribution() {
  return [
    { name: "涨停", value: randomInt(400, 500), itemStyle: { color: "#f56c6c" } },
    { name: "上涨", value: randomInt(1200, 1300), itemStyle: { color: "#fca5a5" } },
    { name: "平盘", value: randomInt(750, 850), itemStyle: { color: "#909399" } },
    { name: "下跌", value: randomInt(1100, 1200), itemStyle: { color: "#86efac" } },
    { name: "跌停", value: randomInt(300, 400), itemStyle: { color: "#67c23a" } }
  ]
}

/**
 * 获取资金流向数据（图表数据）
 */
export function getCapitalFlowData() {
  return [
    { name: "超大单", value: randomFloat(100, 150, 1) },
    { name: "大单", value: randomFloat(80, 90, 1) },
    { name: "中单", value: randomFloat(-50, -40, 1) },
    { name: "小单", value: randomFloat(-170, -160, 1) }
  ]
}

/**
 * 获取Dashboard专用的行业数据
 * 对应Dashboard.vue中期望的industryData格式
 */
export function getDashboardIndustryData() {
  return {
    csrc: {
      categories: ["金融业", "房地产业", "制造业", "信息技术", "批发零售", "建筑业", "采矿业", "交通运输"],
      values: [185.5, 125.3, 98.7, 85.2, 52.8, 45.6, -38.5, -65.2]
    },
    sw_l1: {
      categories: ["计算机", "电子", "医药生物", "电力设备", "汽车", "食品饮料", "银行", "非银金融"],
      values: [165.8, 142.5, 118.9, 95.3, 78.6, 65.4, -45.8, -88.9]
    },
    sw_l2: {
      categories: ["半导体", "光学光电子", "计算机设备", "通信设备", "医疗器械", "化学制药", "白酒", "保险"],
      values: [195.2, 158.7, 125.6, 98.5, 85.3, 72.1, -52.3, -95.6]
    }
  }
}

/**
 * 获取自选股板块表现数据（表格数据）
 */
export function getFavoriteStocks() {
  const stocks = [
    { symbol: "600519", name: "贵州茅台", industry: "白酒" },
    { symbol: "000858", name: "五粮液", industry: "白酒" },
    { symbol: "300750", name: "宁德时代", industry: "电池" },
    { symbol: "601012", name: "隆基绿能", industry: "光伏" },
    { symbol: "002594", name: "比亚迪", industry: "新能源车" }
  ]

  return stocks.map(stock => ({
    symbol: stock.symbol,
    name: stock.name,
    price: formatPrice(),
    change: formatPercent(),
    volume: `${randomInt(10, 50)}万手`,
    turnover: randomFloat(0.5, 5.0, 2),
    industry: stock.industry
  }))
}

/**
 * 获取策略选股板块表现数据（表格数据）
 */
export function getStrategyStocks() {
  const strategies = [
    { symbol: "688981", name: "中芯国际", strategy: "突破策略", score: 88 },
    { symbol: "002475", name: "立讯精密", strategy: "趋势跟踪", score: 85 },
    { symbol: "300059", name: "东方财富", strategy: "均线策略", score: 82 },
    { symbol: "600036", name: "招商银行", strategy: "价值投资", score: 78 },
    { symbol: "000001", name: "平安银行", strategy: "价值投资", score: 65 }
  ]

  return strategies.map(stock => ({
    symbol: stock.symbol,
    name: stock.name,
    price: formatPrice(),
    change: formatPercent(),
    strategy: stock.strategy,
    score: stock.score,
    signal: stock.score > 80 ? "买入" : (stock.score < 70 ? "卖出" : "持有")
  }))
}

/**
 * 获取行业选股板块表现数据（表格数据）
 */
export function getIndustryStocks() {
  const industries = [
    { symbol: "600519", name: "贵州茅台", industry: "白酒", rank: 1, marketCap: 21056 },
    { symbol: "000858", name: "五粮液", industry: "白酒", rank: 2, marketCap: 6125 },
    { symbol: "000568", name: "泸州老窖", industry: "白酒", rank: 3, marketCap: 2089 },
    { symbol: "002304", name: "洋河股份", industry: "白酒", rank: 4, marketCap: 1516 },
    { symbol: "600809", name: "山西汾酒", industry: "白酒", rank: 5, marketCap: 2268 }
  ]

  return industries.map(stock => ({
    symbol: stock.symbol,
    name: stock.name,
    price: formatPrice(),
    change: formatPercent(),
    industry: stock.industry,
    industryRank: stock.rank,
    marketCap: stock.marketCap
  }))
}

/**
 * 获取概念选股板块表现数据（表格数据）
 */
export function getConceptStocks() {
  const concepts = [
    { symbol: "300750", name: "宁德时代", concepts: ["新能源", "电池", "MSCI"], heat: 98 },
    { symbol: "688981", name: "中芯国际", concepts: ["芯片", "半导体", "华为概念"], heat: 95 },
    { symbol: "600276", name: "恒瑞医药", concepts: ["医药", "创新药", "抗癌"], heat: 88 },
    { symbol: "300122", name: "智飞生物", concepts: ["疫苗", "医药", "生物制品"], heat: 92 },
    { symbol: "002230", name: "科大讯飞", concepts: ["AI", "人工智能", "语音识别"], heat: 96 }
  ]

  return concepts.map(stock => ({
    symbol: stock.symbol,
    name: stock.name,
    price: formatPrice(),
    change: formatPercent(),
    concepts: stock.concepts,
    conceptHeat: stock.heat
  }))
}

// 默认导出所有函数
export default {
  getDashboardStats,
  getMarketHeatData,
  getLeadingSectors,
  getPriceDistribution,
  getCapitalFlowData,
  getDashboardIndustryData,
  getFavoriteStocks,
  getStrategyStocks,
  getIndustryStocks,
  getConceptStocks
}
