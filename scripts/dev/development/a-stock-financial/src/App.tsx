import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, FileText, PieChart, LineChart, Calculator, Target, Award, AlertCircle, Search, List } from 'lucide-react'

// A股配色方案：Bloomberg/Wind风格
const colors = {
  bgPrimary: '#0B0F19',
  bgSecondary: '#1A1F2E',
  bgCard: '#232936',
  up: '#00E676',      // A股涨（绿色）
  down: '#FF5252',    // A股跌（红色）
  primary: '#2979FF',  // 主题蓝
  textPrimary: '#E0E6ED',
  textSecondary: '#94A3B8',
  border: '#2D3748'
}

// 股票列表类型
type StockList = {
  id: string
  name: string
  description: string
  stocks: Array<{ code: string; name: string; price: number }>
}

// 股票列表数据
const stockLists: StockList[] = [
  {
    id: 'watchlist-1',
    name: '我的自选股',
    description: '个人关注的股票',
    stocks: [
      { code: '600519', name: '贵州茅台', price: 1856.00 },
      { code: '300750', name: '宁德时代', price: 245.67 },
      { code: '601318', name: '中国平安', price: 52.34 },
      { code: '000858', name: '五粮液', price: 178.45 },
      { code: '002594', name: '比亚迪', price: 267.89 },
    ]
  },
  {
    id: 'list-baijiu',
    name: '白酒板块',
    description: '白酒行业龙头股',
    stocks: [
      { code: '600519', name: '贵州茅台', price: 1856.00 },
      { code: '000858', name: '五粮液', price: 178.45 },
      { code: '000568', name: '泸州老窖', price: 198.32 },
      { code: '600809', name: '山西汾酒', price: 245.67 },
    ]
  },
  {
    id: 'list-tech',
    name: '科技龙头',
    description: '科技创新领军企业',
    stocks: [
      { code: '300750', name: '宁德时代', price: 245.67 },
      { code: '002415', name: '海康威视', price: 32.45 },
      { code: '688981', name: '中芯国际', price: 52.18 },
      { code: '300059', name: '东方财富', price: 18.92 },
    ]
  }
]

// 模拟贵州茅台财务数据
const financialData = {
  stock: {
    code: '600519',
    name: '贵州茅台',
    price: 1856.00,
    marketCap: 2345000000000, // 2.345万亿
    pe: 35.6,
    pb: 12.8,
    dividend: 25.91,
    dividendYield: 1.4
  },

  // 主要财务指标
  keyMetrics: {
    totalRevenue: 137400000000,      // 营业总收入 1374亿
    revenueGrowth: 18.2,              // 营收增长率 18.2%
    netProfit: 74730000000,          // 净利润 747.3亿
    netProfitGrowth: 15.8,           // 净利润增长率 15.8%
    grossMargin: 91.2,                // 毛利率 91.2%
    netMargin: 54.4,                  // 净利率 54.4%
    roe: 25.6,                        // ROE 25.6%
    roa: 22.3,                        // ROA 22.3%
    debtRatio: 18.5,                  // 资产负债率 18.5%
    currentRatio: 8.5,                // 流动比率 8.5
    quickRatio: 7.2                   // 速动比率 7.2
  },

  // 资产负债表摘要
  balanceSheet: [
    { item: '货币资金', value: 695700000000, change: 12.5 },
    { item: '应收账款', value: 245000000, change: -8.3 },
    { item: '存货', value: 38950000000, change: 15.6 },
    { item: '固定资产', value: 18520000000, change: 8.9 },
    { item: '总资产', value: 2345000000000, change: 14.2 },
    { item: '总负债', value: 433800000000, change: 16.8 },
    { item: '股东权益', value: 1911200000000, change: 13.7 }
  ],

  // 利润表摘要
  incomeStatement: [
    { item: '营业收入', value: 137400000000, change: 18.2 },
    { item: '营业成本', value: 12150000000, change: 22.5 },
    { item: '毛利润', value: 125250000000, change: 17.8 },
    { item: '销售费用', value: 4560000000, change: 12.3 },
    { item: '管理费用', value: 9870000000, change: 8.7 },
    { item: '财务费用', value: -185000000, change: -45.2 },
    { item: '净利润', value: 74730000000, change: 15.8 }
  ],

  // 现金流量表摘要
  cashFlow: [
    { item: '经营活动现金流', value: 89250000000, change: 22.3 },
    { item: '投资活动现金流', value: -15620000000, change: -35.6 },
    { item: '筹资活动现金流', value: -32150000000, change: 28.5 },
    { item: '现金净增加额', value: 41480000000, change: 15.7 }
  ],

  // 财务比率
  ratios: {
    profitability: [
      { name: '销售毛利率', value: 91.2, change: 0.5, rating: 'excellent' },
      { name: '销售净利率', value: 54.4, change: -0.3, rating: 'excellent' },
      { name: 'ROE', value: 25.6, change: 1.2, rating: 'excellent' },
      { name: 'ROA', value: 22.3, change: 0.8, rating: 'excellent' }
    ],
    liquidity: [
      { name: '流动比率', value: 8.5, change: -0.2, rating: 'excellent' },
      { name: '速动比率', value: 7.2, change: -0.1, rating: 'excellent' },
      { name: '现金比率', value: 6.8, change: 0.3, rating: 'excellent' }
    ],
    leverage: [
      { name: '资产负债率', value: 18.5, change: 1.2, rating: 'good' },
      { name: '权益乘数', value: 1.23, change: 0.05, rating: 'good' },
      { name: '利息保障倍数', value: 125.6, change: 8.5, rating: 'excellent' }
    ],
    efficiency: [
      { name: '存货周转率', value: 0.68, change: 0.05, rating: 'normal' },
      { name: '应收账款周转率', value: 185.6, change: 12.3, rating: 'excellent' },
      { name: '总资产周转率', value: 0.62, change: 0.02, rating: 'normal' }
    ]
  },

  // 营收趋势（最近8个季度）
  revenueTrend: [
    { period: '2023-Q4', revenue: 35250000000, profit: 19230000000 },
    { period: '2024-Q1', revenue: 31850000000, profit: 16870000000 },
    { period: '2024-Q2', revenue: 34560000000, profit: 18240000000 },
    { period: '2024-Q3', revenue: 36230000000, profit: 19560000000 },
    { period: '2024-Q4', revenue: 38750000000, profit: 21450000000 },
    { period: '2025-Q1', revenue: 35120000000, profit: 18760000000 },
    { period: '2025-Q2', revenue: 37890000000, profit: 20340000000 },
    { period: '2025-Q3', revenue: 39560000000, profit: 21230000000 }
  ],

  // 同行业对比
  industryComparison: [
    { name: '贵州茅台', pe: 35.6, pb: 12.8, roe: 25.6, margin: 54.4 },
    { name: '五粮液', pe: 28.5, pb: 9.2, roe: 22.3, margin: 42.8 },
    { name: '泸州老窖', pe: 32.1, pb: 8.9, roe: 20.5, margin: 38.6 },
    { name: '剑南春', pe: 30.8, pb: 7.5, roe: 18.9, margin: 35.2 },
    { name: '行业平均', pe: 31.75, pb: 9.6, roe: 21.8, margin: 42.75 }
  ]
}

// 财务指标卡片
function MetricCard({ label, value, unit = '', change, icon: Icon, reverse = false }: {
  label: string
  value: number
  unit?: string
  change?: number
  icon?: any
  reverse?: boolean
}) {
  const isPositive = change !== undefined ? (reverse ? change < 0 : change > 0) : value > 0

  return (
    <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-700 hover:border-blue-500/50 transition-all">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        {Icon && <Icon className={`h-4 w-4 ${isPositive ? 'text-green-400' : 'text-red-400'}`} />}
      </div>
      <p className="text-2xl font-bold text-white mb-1">
        {value.toLocaleString()}{unit}
      </p>
      {change !== undefined && (
        <p className={`text-sm ${isPositive ? 'text-green-400' : 'text-red-400'}`}>
          {isPositive ? '+' : ''}{change.toFixed(2)}%
        </p>
      )}
    </div>
  )
}

// 股票信息头部
function StockHeader() {
  const stock = financialData.stock

  return (
    <Card className="border-2">
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold text-white">{stock.name}</h1>
              <Badge variant="outline" className="border-blue-500 text-blue-400">
                {stock.code}
              </Badge>
            </div>
            <p className="text-sm text-gray-400">白酒行业龙头 | 沪深300成分股</p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-white">¥{stock.price.toFixed(2)}</p>
            <div className="flex items-center gap-2 mt-1">
              <Badge className="border-green-500 text-green-400">+2.35%</Badge>
              <span className="text-sm text-gray-400">今日</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-5 gap-4 mt-6">
          <div className="text-center">
            <p className="text-xs text-gray-400">总市值</p>
            <p className="text-lg font-semibold text-white">¥{(stock.marketCap / 100000000).toFixed(0)}万亿</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-400">PE(TTM)</p>
            <p className="text-lg font-semibold text-white">{stock.pe.toFixed(1)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-400">PB</p>
            <p className="text-lg font-semibold text-white">{stock.pb.toFixed(1)}</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-400">股息率</p>
            <p className="text-lg font-semibold text-green-400">{stock.dividendYield.toFixed(1)}%</p>
          </div>
          <div className="text-center">
            <p className="text-xs text-gray-400">每股派息</p>
            <p className="text-lg font-semibold text-white">¥{stock.dividend.toFixed(2)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 主要财务指标
function KeyMetrics() {
  const metrics = financialData.keyMetrics

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          主要财务指标
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <MetricCard
            label="营业总收入"
            value={metrics.totalRevenue / 100000000}
            unit="亿"
            change={metrics.revenueGrowth}
            icon={Activity}
          />
          <MetricCard
            label="净利润"
            value={metrics.netProfit / 100000000}
            unit="亿"
            change={metrics.netProfitGrowth}
            icon={DollarSign}
          />
          <MetricCard
            label="毛利率"
            value={metrics.grossMargin}
            unit="%"
            change={0.5}
            icon={Target}
          />
          <MetricCard
            label="净利率"
            value={metrics.netMargin}
            unit="%"
            change={-0.3}
            icon={Award}
          />
          <MetricCard
            label="ROE"
            value={metrics.roe}
            unit="%"
            change={1.2}
            icon={TrendingUp}
          />
          <MetricCard
            label="ROA"
            value={metrics.roa}
            unit="%"
            change={0.8}
            icon={PieChart}
          />
          <MetricCard
            label="资产负债率"
            value={metrics.debtRatio}
            unit="%"
            change={1.2}
            reverse={true}
            icon={AlertCircle}
          />
          <MetricCard
            label="流动比率"
            value={metrics.currentRatio}
            change={-0.2}
            icon={LineChart}
          />
        </div>
      </CardContent>
    </Card>
  )
}

// 财务报表表格
function FinancialTable({ title, icon: Icon, data }: {
  title: string
  icon: any
  data: Array<{ item: string; value: number; change: number }>
}) {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Icon className="h-5 w-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">项目</TableHead>
              <TableHead className="text-gray-400 text-right">金额（亿元）</TableHead>
              <TableHead className="text-gray-400 text-right">同比变化</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((row, idx) => (
              <TableRow key={idx} className="border-gray-700 hover:bg-blue-500/10">
                <TableCell className="text-white font-medium">{row.item}</TableCell>
                <TableCell className="text-white text-right">
                  {(row.value / 100000000).toFixed(2)}
                </TableCell>
                <TableCell className="text-right">
                  <Badge className={row.change >= 0
                    ? 'border-green-500 text-green-400'
                    : 'border-red-500 text-red-400'}>
                    {row.change >= 0 ? '+' : ''}{row.change.toFixed(1)}%
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

// 财务比率分析
function RatioAnalysis() {
  const ratios = financialData.ratios

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case 'excellent': return 'text-green-400'
      case 'good': return 'text-blue-400'
      case 'normal': return 'text-yellow-400'
      case 'poor': return 'text-red-400'
      default: return 'text-gray-400'
    }
  }

  const RatioSection = ({ title, items }: { title: string; items: Array<{ name: string; value: number; change: number; rating: string }> }) => (
    <div className="space-y-3">
      <h4 className="text-white font-semibold mb-3">{title}</h4>
      {items.map((item, idx) => (
        <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 border border-gray-700">
          <div className="flex-1">
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-300">{item.name}</span>
              <span className={`text-lg font-bold ${getRatingColor(item.rating)}`}>
                {item.value.toFixed(2)}{item.value < 10 && item.value > 0 ? '%' : ''}
              </span>
            </div>
            <div className="flex items-center gap-2">
              <Progress value={item.value > 100 ? 100 : item.value * (item.value < 10 ? 10 : 1)} className="flex-1 h-2" />
              <span className={`text-xs ${item.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {item.change >= 0 ? '+' : ''}{item.change.toFixed(1)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Calculator className="h-5 w-5" />
          财务比率分析
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <RatioSection title="盈利能力" items={ratios.profitability} />
          <RatioSection title="偿债能力" items={ratios.liquidity} />
          <RatioSection title="杠杆能力" items={ratios.leverage} />
          <RatioSection title="运营效率" items={ratios.efficiency} />
        </div>
      </CardContent>
    </Card>
  )
}

// 营收趋势
function RevenueTrend() {
  const trend = financialData.revenueTrend

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <LineChart className="h-5 w-5" />
          营收与利润趋势
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded"></div>
                  <span className="text-sm text-gray-400">营业收入</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded"></div>
                  <span className="text-sm text-gray-400">净利润</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              {trend.map((item, idx) => {
                const maxRevenue = Math.max(...trend.map(t => t.revenue))
                const revenueHeight = (item.revenue / maxRevenue) * 100
                const profitHeight = (item.profit / item.revenue) * 100

                return (
                  <div key={idx} className="space-y-2">
                    <div className="flex items-center gap-3">
                      <div className="w-24 text-xs text-gray-500">{item.period}</div>
                      <div className="flex-1">
                        <div className="relative h-6 bg-gray-800 rounded">
                          <div
                            className="absolute top-0 h-full bg-blue-500 rounded"
                            style={{ width: `${revenueHeight}%` }}
                          />
                          <div
                            className="absolute top-0 h-full bg-green-500/80 rounded"
                            style={{ width: `${revenueHeight * (item.profit / item.revenue)}%` }}
                          />
                        </div>
                      </div>
                      <div className="w-40 text-right text-sm">
                        <div className="text-white">¥{(item.revenue / 100000000).toFixed(1)}亿</div>
                        <div className="text-green-400 text-xs">净利润 ¥{(item.profit / 100000000).toFixed(1)}亿</div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 同行业对比
function IndustryComparison() {
  const comparison = financialData.industryComparison

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Activity className="h-5 w-5" />
          同行业对比
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">公司</TableHead>
              <TableHead className="text-gray-400 text-right">PE</TableHead>
              <TableHead className="text-gray-400 text-right">PB</TableHead>
              <TableHead className="text-gray-400 text-right">ROE</TableHead>
              <TableHead className="text-gray-400 text-right">净利率</TableHead>
              <TableHead className="text-gray-400 text-center">综合评级</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {comparison.map((company, idx) => {
              const isTarget = company.name === '贵州茅台'
              const score = ((40 - company.pe) / 40 * 0.3 +
                           (20 / company.pb) / 20 * 0.2 +
                           (company.roe / 30) * 0.3 +
                           (company.margin / 60) * 0.2) * 100

              return (
                <TableRow
                  key={idx}
                  className={`border-gray-700 ${isTarget ? 'bg-blue-500/10' : 'hover:bg-blue-500/10'}`}
                >
                  <TableCell className={`font-medium ${isTarget ? 'text-blue-400' : 'text-white'}`}>
                    {company.name}
                    {isTarget && <Badge className="ml-2 bg-blue-600">目标</Badge>}
                  </TableCell>
                  <TableCell className="text-white text-right">{company.pe.toFixed(1)}</TableCell>
                  <TableCell className="text-white text-right">{company.pb.toFixed(1)}</TableCell>
                  <TableCell className="text-white text-right">{company.roe.toFixed(1)}%</TableCell>
                  <TableCell className="text-white text-right">{company.margin.toFixed(1)}%</TableCell>
                  <TableCell className="text-center">
                    <div className="flex items-center justify-center gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <span
                          key={star}
                          className={star <= Math.floor(score / 20) ? 'text-yellow-400' : 'text-gray-600'}
                        >
                          ★
                        </span>
                      ))}
                      <span className="ml-2 text-xs text-gray-400">{score.toFixed(0)}</span>
                    </div>
                  </TableCell>
                </TableRow>
              )
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

// 股票列表财务数据表格
function StockListFinancialTable({ stocks }: { stocks: Array<{ code: string; name: string; price: number }> }) {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <FileText className="h-5 w-5" />
          财务数据概览
        </CardTitle>
        <p className="text-sm text-gray-400 mt-2">
          显示 {stocks.length} 只股票的主要财务指标
        </p>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">代码</TableHead>
              <TableHead className="text-gray-400">名称</TableHead>
              <TableHead className="text-gray-400 text-right">最新价</TableHead>
              <TableHead className="text-gray-400 text-right">总市值</TableHead>
              <TableHead className="text-gray-400 text-right">PE(TTM)</TableHead>
              <TableHead className="text-gray-400 text-right">ROE</TableHead>
              <TableHead className="text-gray-400 text-right">毛利率</TableHead>
              <TableHead className="text-gray-400 text-right">净利率</TableHead>
              <TableHead className="text-gray-400 text-center">评级</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {stocks.map((stock) => (
              <TableRow key={stock.code} className="border-gray-700 hover:bg-blue-500/10">
                <TableCell className="text-white font-medium">{stock.code}</TableCell>
                <TableCell className="text-white">{stock.name}</TableCell>
                <TableCell className="text-white text-right">¥{stock.price.toFixed(2)}</TableCell>
                <TableCell className="text-white text-right">
                  {(Math.random() * 5 + 0.5).toFixed(2)}万亿
                </TableCell>
                <TableCell className="text-white text-right">
                  {(Math.random() * 30 + 20).toFixed(1)}
                </TableCell>
                <TableCell className="text-white text-right">
                  <span className={(Math.random() * 30 > 15) ? 'text-green-400' : 'text-red-400'}>
                    {(Math.random() * 30).toFixed(1)}%
                  </span>
                </TableCell>
                <TableCell className="text-white text-right">
                  {(Math.random() * 40 + 50).toFixed(1)}%
                </TableCell>
                <TableCell className="text-white text-right">
                  {(Math.random() * 30 + 30).toFixed(1)}%
                </TableCell>
                <TableCell className="text-center">
                  <Badge className={
                    Math.random() > 0.5 ? 'border-green-500 text-green-400' :
                    Math.random() > 0.25 ? 'border-yellow-500 text-yellow-400' :
                    'border-red-500 text-red-400'
                  }>
                    {Math.random() > 0.5 ? '优秀' : Math.random() > 0.25 ? '良好' : '一般'}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

// 查询模式选择器包装组件（用于协调状态）
function QueryModeSelectorWrapper({
  queryMode,
  setQueryMode,
  selectedList,
  setSelectedList
}: {
  queryMode: 'single' | 'list'
  setQueryMode: (mode: 'single' | 'list') => void
  selectedList: string
  setSelectedList: (list: string) => void
}) {
  const [stockCode, setStockCode] = useState('600519')

  return (
    <Card className="border-2">
      <CardContent className="pt-6">
        <Tabs value={queryMode} onValueChange={(v) => setQueryMode(v as 'single' | 'list')} className="w-full">
          <TabsList className="bg-gray-900 border border-gray-700 w-full justify-start">
            <TabsTrigger value="single" className="data-[state=active]:bg-blue-600">
              <Search className="h-4 w-4 mr-2" />
              单股查询
            </TabsTrigger>
            <TabsTrigger value="list" className="data-[state=active]:bg-blue-600">
              <List className="h-4 w-4 mr-2" />
              列表查询
            </TabsTrigger>
          </TabsList>

          <div className="mt-4">
            <TabsContent value="single" className="mt-0">
              <div className="flex gap-3">
                <div className="flex-1">
                  <Input
                    placeholder="请输入股票代码（如：600519）"
                    value={stockCode}
                    onChange={(e) => setStockCode(e.target.value)}
                    className="bg-gray-900 border-gray-700 text-white"
                  />
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Search className="h-4 w-4 mr-2" />
                  查询
                </Button>
              </div>
            </TabsContent>

            <TabsContent value="list" className="mt-0">
              <div className="flex gap-3">
                <div className="flex-1">
                  <Select value={selectedList} onValueChange={setSelectedList}>
                    <SelectTrigger className="bg-gray-900 border-gray-700 text-white">
                      <SelectValue placeholder="选择股票列表" />
                    </SelectTrigger>
                    <SelectContent>
                      {stockLists.map((list) => (
                        <SelectItem key={list.id} value={list.id}>
                          <div>
                            <div className="font-medium">{list.name}</div>
                            <div className="text-xs text-gray-500">{list.description} ({list.stocks.length}只股票)</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button className="bg-blue-600 hover:bg-blue-700">
                  <Search className="h-4 w-4 mr-2" />
                  查询列表
                </Button>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </CardContent>
    </Card>
  )
}

function App() {
  const [queryMode, setQueryMode] = useState<'single' | 'list'>('single')
  const [selectedList, setSelectedList] = useState('watchlist-1')

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.bgPrimary }}>
      {/* Header */}
      <header className="border-b-2 border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">MyStocks A股财务数据分析</h1>
            <p className="text-sm text-gray-500 mt-1">专业级财务报表与分析平台 v2.1</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-green-500 text-green-400">
              <FileText className="h-3 w-3 mr-1" />
              2025年三季报
            </Badge>
            <span className="text-sm text-gray-400">
              {new Date().toLocaleString('zh-CN', {
                hour12: false,
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
              })}
            </span>
          </div>
        </div>
      </header>

      <main className="p-6 space-y-6">
        {/* 查询模式选择器 */}
        <QueryModeSelectorWrapper
          queryMode={queryMode}
          setQueryMode={setQueryMode}
          selectedList={selectedList}
          setSelectedList={setSelectedList}
        />

        <Separator className="bg-gray-800" />

        {/* 根据查询模式显示不同内容 */}
        {queryMode === 'single' ? (
          <>
            {/* 单股查询模式：显示详细卡片 */}
            <section>
              <StockHeader />
            </section>

            <section>
              <KeyMetrics />
            </section>

            <Separator className="bg-gray-800" />

            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <FinancialTable title="资产负债表" icon={PieChart} data={financialData.balanceSheet} />
              <FinancialTable title="利润表" icon={BarChart3} data={financialData.incomeStatement} />
              <FinancialTable title="现金流量表" icon={LineChart} data={financialData.cashFlow} />
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <RatioAnalysis />
              <RevenueTrend />
            </section>

            <section>
              <IndustryComparison />
            </section>
          </>
        ) : (
          <>
            {/* 列表查询模式：显示股票列表财务数据表格 */}
            <section>
              <StockListFinancialTable
                stocks={stockLists.find(l => l.id === selectedList)?.stocks || stockLists[0].stocks}
              />
            </section>
          </>
        )}

        {/* 底部信息 */}
        <footer className="mt-8 pt-6 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              <p>数据来源: 东方财富 | 同花顺 | 巨潮资讯</p>
              <p className="mt-1">更新频率: 季度更新 | 延迟: 1个交易日</p>
            </div>
            <div className="text-right">
              <p>© 2025 MyStocks Quantitative Trading</p>
              <p className="mt-1">专业A股量化交易平台</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}

export default App
