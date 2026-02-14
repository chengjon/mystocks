import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Slider } from '@/components/ui/slider'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, Settings, Play, Download, Calendar, Target, AlertCircle, LineChart, PieChart } from 'lucide-react'

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

// 自选股列表类型
type StockList = {
  id: string
  name: string
  stockCount: number
  description: string
  createdAt: string
}

// 模拟策略回测数据
const backtestData = {
  // 自选股列表
  stockLists: [
    { id: 'list-1', name: '我的核心股池', stockCount: 15, description: '精选优质蓝筹股', createdAt: '2025-12-01' },
    { id: 'list-2', name: '新能源板块', stockCount: 8, description: '新能源汽车产业链', createdAt: '2025-12-05' },
    { id: 'list-3', name: '科技龙头', stockCount: 12, description: '科技创新企业', createdAt: '2025-12-10' },
    { id: 'list-4', name: '消费白马', stockCount: 10, description: '大消费板块', createdAt: '2025-12-15' },
    { id: 'list-5', name: '金融权重', stockCount: 6, description: '银行保险券商', createdAt: '2025-12-20' },
  ],

  // 策略配置
  config: {
    name: '双均线策略',
    type: '趋势跟踪',
    symbol: '000001', // 上证指数
    shortPeriod: 5,
    longPeriod: 20,
    startDate: '2020-01-01',
    endDate: '2025-12-25',
    initialCapital: 1000000
  },

  // 回测结果概览
  summary: {
    totalReturn: 157.32,      // 总收益率 (%)
    annualReturn: 23.45,      // 年化收益率 (%)
    sharpeRatio: 1.85,        // 夏普比率
    maxDrawdown: -18.56,      // 最大回撤 (%)
    winRate: 62.5,            // 胜率 (%)
    profitLossRatio: 2.3,     // 盈亏比
    totalTrades: 48,          // 总交易次数
    profitTrades: 30,         // 盈利次数
    lossTrades: 18            // 亏损次数
  },

  // 净值曲线数据点
  equityCurve: [
    { date: '2020-01-01', value: 1000000, benchmark: 1000000 },
    { date: '2020-06-30', value: 1156000, benchmark: 1034000 },
    { date: '2020-12-31', value: 1298000, benchmark: 1089000 },
    { date: '2021-06-30', value: 1456000, benchmark: 1156000 },
    { date: '2021-12-31', value: 1689000, benchmark: 1223000 },
    { date: '2022-06-30', value: 1534000, benchmark: 1178000 },
    { date: '2022-12-31', value: 1412000, benchmark: 1123000 },
    { date: '2023-06-30', value: 1657000, benchmark: 1245000 },
    { date: '2023-12-31', value: 1894000, benchmark: 1312000 },
    { date: '2024-06-30', value: 2145000, benchmark: 1398000 },
    { date: '2024-12-31', value: 2567300, benchmark: 1489000 },
    { date: '2025-12-25', value: 2573200, benchmark: 1492000 }
  ],

  // 持仓分析
  positions: [
    { date: '2020-02-15', symbol: '000001', name: '上证指数', type: 'long', price: 2987.56, quantity: 100, value: 298756, profit: 58234, profitPercent: 24.23 },
    { date: '2020-05-20', symbol: '600519', name: '贵州茅台', type: 'long', price: 1356.00, quantity: 200, value: 271200, profit: 124500, profitPercent: 84.56 },
    { date: '2021-03-10', symbol: '300750', name: '宁德时代', type: 'long', price: 285.60, quantity: 500, value: 142800, profit: 89600, profitPercent: 62.78 },
    { date: '2022-08-15', symbol: '000858', name: '五粮液', type: 'long', price: 168.45, quantity: 600, value: 101070, profit: -12450, profitPercent: -10.96 },
    { date: '2023-01-20', symbol: '601318', name: '中国平安', type: 'long', price: 48.32, quantity: 2000, value: 96640, profit: 23400, profitPercent: 32.04 },
    { date: '2024-05-10', symbol: '002594', name: '比亚迪', type: 'long', price: 245.80, quantity: 400, value: 98320, profit: 78500, profitPercent: 79.85 }
  ],

  // 交易记录
  trades: [
    { date: '2020-02-15', symbol: '000001', name: '上证指数', type: 'buy', price: 2987.56, quantity: 100, amount: 298756, fee: 896 },
    { date: '2020-05-08', symbol: '000001', name: '上证指数', type: 'sell', price: 3156.32, quantity: 100, amount: 315632, fee: 947, profit: 16876 },
    { date: '2020-05-20', symbol: '600519', name: '贵州茅台', type: 'buy', price: 1356.00, quantity: 200, amount: 271200, fee: 814 },
    { date: '2021-03-10', symbol: '300750', name: '宁德时代', type: 'buy', price: 285.60, quantity: 500, amount: 142800, fee: 428 },
    { date: '2021-08-25', symbol: '600519', name: '贵州茅台', type: 'sell', price: 1685.00, quantity: 200, amount: 337000, fee: 1011, profit: 64786 },
    { date: '2022-08-15', symbol: '000858', name: '五粮液', type: 'buy', price: 168.45, quantity: 600, amount: 101070, fee: 303 },
    { date: '2022-10-18', symbol: '300750', name: '宁德时代', type: 'sell', price: 412.30, quantity: 500, amount: 206150, fee: 618, profit: 62322 },
    { date: '2023-01-20', symbol: '601318', name: '中国平安', type: 'buy', price: 48.32, quantity: 2000, amount: 96640, fee: 290 },
    { date: '2023-06-15', symbol: '000858', name: '五粮液', type: 'sell', price: 152.30, quantity: 600, amount: 91380, fee: 274, profit: -12450 },
    { date: '2024-05-10', symbol: '002594', name: '比亚迪', type: 'buy', price: 245.80, quantity: 400, amount: 98320, fee: 295 }
  ],

  // 月度收益
  monthlyReturns: [
    { month: '2020-01', return: 2.35, benchmark: 0.85 },
    { month: '2020-02', return: 5.67, benchmark: 3.12 },
    { month: '2020-03', return: -3.24, benchmark: -5.67 },
    { month: '2020-04', return: 4.56, benchmark: 2.34 },
    { month: '2020-05', return: 3.78, benchmark: 1.23 },
    { month: '2020-06', return: 6.45, benchmark: 4.56 },
    { month: '2020-07', return: 8.92, benchmark: 6.78 },
    { month: '2020-08', return: -2.34, benchmark: -1.23 },
    { month: '2020-09', return: 1.56, benchmark: 0.89 },
    { month: '2020-10', return: 4.23, benchmark: 2.45 },
    { month: '2020-11', return: 7.89, benchmark: 5.67 },
    { month: '2020-12', return: 5.34, benchmark: 3.45 }
  ],

  // 风险指标
  riskMetrics: {
    volatility: 18.56,        // 波动率 (%)
    downsideDeviation: 12.34, // 下行偏差 (%)
    var95: -85000,            // VaR 95% (元)
    cvar95: -125000,          // CVaR 95% (元)
    beta: 1.15,               // Beta系数
    alpha: 8.45,              // Alpha (%)
    informationRatio: 1.23,   // 信息比率
    trackingError: 6.78       // 跟踪误差 (%)
  }
}

// 自选股列表选择器组件
function StockListSelector() {
  const [selectedList, setSelectedList] = useState('list-1')
  const lists = backtestData.stockLists

  return (
    <Card className="border-2">
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <label className="text-sm text-gray-400 mb-2 block">选择自选股列表</label>
            <Select value={selectedList} onValueChange={setSelectedList}>
              <SelectTrigger className="w-full">
                <SelectValue placeholder="选择自选股列表" />
              </SelectTrigger>
              <SelectContent>
                {lists.map((list) => (
                  <SelectItem key={list.id} value={list.id}>
                    <div className="flex items-center justify-between w-full pr-4">
                      <span className="font-medium">{list.name}</span>
                      <span className="text-xs text-gray-500 ml-2">{list.stockCount}只股票</span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="ml-6 text-right">
            <p className="text-sm text-gray-400">当前列表</p>
            <p className="text-lg font-bold text-white mt-1">
              {lists.find(l => l.id === selectedList)?.name}
            </p>
            <p className="text-xs text-gray-500 mt-1">
              {lists.find(l => l.id === selectedList)?.description}
            </p>
          </div>
        </div>
        <div className="mt-4 p-3 rounded-lg bg-blue-500/10 border border-blue-500/30">
          <p className="text-sm text-blue-300">
            ✓ 所有策略配置将应用于选定的自选股列表中的 {lists.find(l => l.id === selectedList)?.stockCount} 只股票
          </p>
        </div>
      </CardContent>
    </Card>
  )
}

// 配置面板组件
function ConfigPanel() {
  const [strategyType, setStrategyType] = useState('trend')
  const [shortPeriod, setShortPeriod] = useState([5])
  const [longPeriod, setLongPeriod] = useState([20])
  const [initialCapital, setInitialCapital] = useState(1000000)

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Settings className="h-5 w-5" />
          策略配置
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="strategy-type" className="text-gray-300">策略类型</Label>
            <Select value={strategyType} onValueChange={setStrategyType}>
              <SelectTrigger className="mt-2">
                <SelectValue placeholder="选择策略类型" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="trend">趋势跟踪</SelectItem>
                <SelectItem value="mean-reversion">均值回归</SelectItem>
                <SelectItem value="momentum">动量策略</SelectItem>
                <SelectItem value="arbitrage">套利策略</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <Label htmlFor="symbol" className="text-gray-300">标的代码</Label>
            <Input id="symbol" placeholder="000001" className="mt-2" defaultValue="000001" />
          </div>
        </div>

        <div>
          <Label className="text-gray-300">短期周期: {shortPeriod[0]}天</Label>
          <Slider
            value={shortPeriod}
            onValueChange={setShortPeriod}
            max={30}
            min={3}
            step={1}
            className="mt-2"
          />
        </div>

        <div>
          <Label className="text-gray-300">长期周期: {longPeriod[0]}天</Label>
          <Slider
            value={longPeriod}
            onValueChange={setLongPeriod}
            max={120}
            min={20}
            step={5}
            className="mt-2"
          />
        </div>

        <div>
          <Label htmlFor="capital" className="text-gray-300">初始资金 (元)</Label>
          <Input
            id="capital"
            type="number"
            value={initialCapital}
            onChange={(e) => setInitialCapital(Number(e.target.value))}
            className="mt-2"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="start-date" className="text-gray-300">开始日期</Label>
            <Input id="start-date" type="date" defaultValue="2020-01-01" className="mt-2" />
          </div>
          <div>
            <Label htmlFor="end-date" className="text-gray-300">结束日期</Label>
            <Input id="end-date" type="date" defaultValue="2025-12-25" className="mt-2" />
          </div>
        </div>

        <div className="flex gap-3">
          <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
            <Play className="h-4 w-4 mr-2" />
            运行回测
          </Button>
          <Button variant="outline" className="flex-1">
            <Download className="h-4 w-4 mr-2" />
            导出结果
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

// 回测结果概览
function SummaryCard() {
  const summary = backtestData.summary

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          回测结果概览
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <SummaryItem
            label="总收益率"
            value={`${summary.totalReturn > 0 ? '+' : ''}${summary.totalReturn.toFixed(2)}%`}
            positive={summary.totalReturn > 0}
            icon={TrendingUp}
          />
          <SummaryItem
            label="年化收益率"
            value={`${summary.annualReturn > 0 ? '+' : ''}${summary.annualReturn.toFixed(2)}%`}
            positive={summary.annualReturn > 0}
            icon={Activity}
          />
          <SummaryItem
            label="夏普比率"
            value={summary.sharpeRatio.toFixed(2)}
            positive={summary.sharpeRatio > 1}
            icon={Target}
          />
          <SummaryItem
            label="最大回撤"
            value={`${summary.maxDrawdown.toFixed(2)}%`}
            positive={false}
            icon={AlertCircle}
          />
          <SummaryItem
            label="胜率"
            value={`${summary.winRate.toFixed(1)}%`}
            positive={summary.winRate > 50}
            icon={DollarSign}
          />
          <SummaryItem
            label="盈亏比"
            value={summary.profitLossRatio.toFixed(2)}
            positive={summary.profitLossRatio > 1}
            icon={TrendingUp}
          />
          <SummaryItem
            label="总交易"
            value={`${summary.totalTrades}次`}
            positive={true}
            icon={Activity}
          />
          <SummaryItem
            label="盈利/亏损"
            value={`${summary.profitTrades}/${summary.lossTrades}`}
            positive={summary.profitTrades > summary.lossTrades}
            icon={Target}
          />
        </div>
      </CardContent>
    </Card>
  )
}

function SummaryItem({ label, value, positive, icon: Icon }: {
  label: string
  value: string
  positive: boolean
  icon: any
}) {
  return (
    <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-gray-400">{label}</span>
        <Icon className={`h-4 w-4 ${positive ? 'text-green-400' : 'text-red-400'}`} />
      </div>
      <p className={`text-xl font-bold ${positive ? 'text-green-400' : 'text-red-400'}`}>
        {value}
      </p>
    </div>
  )
}

// 净值曲线
function EquityCurve() {
  const curve = backtestData.equityCurve

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <LineChart className="h-5 w-5" />
          净值曲线
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="h-64 flex items-end justify-between gap-1">
            {curve.map((point, idx) => {
              const maxValue = Math.max(...curve.map(p => p.value))
              const height = (point.value / maxValue) * 100

              return (
                <div key={idx} className="flex-1 flex flex-col items-center gap-1">
                  <div
                    className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t hover:from-blue-500 hover:to-blue-300 transition-all cursor-pointer"
                    style={{ height: `${height}%` }}
                    title={`${point.date}: ¥${point.value.toLocaleString()}`}
                  />
                  {idx % 2 === 0 && (
                    <span className="text-xs text-gray-500 transform -rotate-45 origin-left">
                      {point.date.substring(0, 4)}
                    </span>
                  )}
                </div>
              )
            })}
          </div>

          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-blue-500 rounded"></div>
                <span className="text-gray-400">策略净值</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-gray-500 rounded"></div>
                <span className="text-gray-400">基准</span>
              </div>
            </div>
            <div className="text-gray-400">
              起始: ¥1,000,000 → 最新: ¥{curve[curve.length - 1].value.toLocaleString()}
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// 持仓分析
function PositionAnalysis() {
  const positions = backtestData.positions

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <PieChart className="h-5 w-5" />
          持仓分析
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">日期</TableHead>
              <TableHead className="text-gray-400">代码</TableHead>
              <TableHead className="text-gray-400">名称</TableHead>
              <TableHead className="text-gray-400">类型</TableHead>
              <TableHead className="text-gray-400">成本价</TableHead>
              <TableHead className="text-gray-400">市值</TableHead>
              <TableHead className="text-gray-400">盈亏</TableHead>
              <TableHead className="text-gray-400">收益率</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {positions.map((position, idx) => (
              <TableRow key={idx} className="border-gray-700 hover:bg-blue-500/10">
                <TableCell className="text-gray-300">{position.date}</TableCell>
                <TableCell className="text-white font-medium">{position.symbol}</TableCell>
                <TableCell className="text-gray-300">{position.name}</TableCell>
                <TableCell>
                  <Badge className="border-blue-500 text-blue-400">
                    {position.type === 'long' ? '做多' : '做空'}
                  </Badge>
                </TableCell>
                <TableCell className="text-white">¥{position.price.toFixed(2)}</TableCell>
                <TableCell className="text-white">¥{position.value.toLocaleString()}</TableCell>
                <TableCell className={position.profit >= 0 ? 'text-green-400' : 'text-red-400'}>
                  {position.profit >= 0 ? '+' : ''}¥{position.profit.toLocaleString()}
                </TableCell>
                <TableCell>
                  <Badge className={position.profitPercent >= 0
                    ? 'border-green-500 text-green-400'
                    : 'border-red-500 text-red-400'}>
                    {position.profitPercent >= 0 ? '+' : ''}{position.profitPercent.toFixed(2)}%
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

// 交易记录
function TradeHistory() {
  const trades = backtestData.trades

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Calendar className="h-5 w-5" />
          交易记录
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">日期</TableHead>
              <TableHead className="text-gray-400">代码</TableHead>
              <TableHead className="text-gray-400">名称</TableHead>
              <TableHead className="text-gray-400">方向</TableHead>
              <TableHead className="text-gray-400">价格</TableHead>
              <TableHead className="text-gray-400">数量</TableHead>
              <TableHead className="text-gray-400">金额</TableHead>
              <TableHead className="text-gray-400">手续费</TableHead>
              <TableHead className="text-gray-400">盈亏</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {trades.map((trade, idx) => (
              <TableRow key={idx} className="border-gray-700 hover:bg-blue-500/10">
                <TableCell className="text-gray-300">{trade.date}</TableCell>
                <TableCell className="text-white font-medium">{trade.symbol}</TableCell>
                <TableCell className="text-gray-300">{trade.name}</TableCell>
                <TableCell>
                  <Badge className={trade.type === 'buy'
                    ? 'border-blue-500 text-blue-400'
                    : 'border-orange-500 text-orange-400'}>
                    {trade.type === 'buy' ? '买入' : '卖出'}
                  </Badge>
                </TableCell>
                <TableCell className="text-white">¥{trade.price.toFixed(2)}</TableCell>
                <TableCell className="text-white">{trade.quantity}</TableCell>
                <TableCell className="text-white">¥{trade.amount.toLocaleString()}</TableCell>
                <TableCell className="text-gray-400">¥{trade.fee}</TableCell>
                <TableCell className={trade.profit !== undefined
                  ? (trade.profit >= 0 ? 'text-green-400' : 'text-red-400')
                  : 'text-gray-500'}>
                  {trade.profit !== undefined ? (
                    `${trade.profit >= 0 ? '+' : ''}¥${trade.profit.toLocaleString()}`
                  ) : (
                    '-'
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

// 月度收益
function MonthlyReturns() {
  const returns = backtestData.monthlyReturns

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Activity className="h-5 w-5" />
          月度收益
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {returns.map((item, idx) => {
            const maxReturn = Math.max(...returns.map(r => Math.abs(r.return)))
            const barWidth = (Math.abs(item.return) / maxReturn) * 100

            return (
              <div key={idx} className="flex items-center gap-3">
                <div className="w-20 text-sm text-gray-400">
                  {item.month.substring(5)}
                </div>
                <div className="flex-1">
                  <div className="relative h-6 bg-gray-800 rounded">
                    <div
                      className={`absolute top-0 h-full rounded ${item.return >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                      style={{ width: `${barWidth}%`, left: item.return >= 0 ? '50%' : `${50 - barWidth}%` }}
                    />
                  </div>
                </div>
                <div className="w-24 text-right">
                  <span className={`text-sm font-medium ${item.return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {item.return >= 0 ? '+' : ''}{item.return.toFixed(2)}%
                  </span>
                  <div className="text-xs text-gray-500">
                    基准: {item.benchmark >= 0 ? '+' : ''}{item.benchmark.toFixed(2)}%
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

// 风险指标
function RiskMetrics() {
  const metrics = backtestData.riskMetrics

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <AlertCircle className="h-5 w-5" />
          风险指标
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <RiskItem label="波动率" value={`${metrics.volatility.toFixed(2)}%`} />
          <RiskItem label="下行偏差" value={`${metrics.downsideDeviation.toFixed(2)}%`} />
          <RiskItem label="VaR 95%" value={`¥${metrics.var95.toLocaleString()}`} />
          <RiskItem label="CVaR 95%" value={`¥${metrics.cvar95.toLocaleString()}`} />
          <RiskItem label="Beta系数" value={metrics.beta.toFixed(2)} />
          <RiskItem label="Alpha" value={`${metrics.alpha.toFixed(2)}%`} />
          <RiskItem label="信息比率" value={metrics.informationRatio.toFixed(2)} />
          <RiskItem label="跟踪误差" value={`${metrics.trackingError.toFixed(2)}%`} />
        </div>
      </CardContent>
    </Card>
  )
}

function RiskItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 border border-gray-700">
      <span className="text-sm text-gray-400">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  )
}

// 策略配置与回测结果（合并）
function StrategyConfigAndResults() {
  const [activeTab, setActiveTab] = useState('config')

  return (
    <Card className="border-2">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <CardHeader className="pb-3">
          <TabsList className="bg-gray-900 border border-gray-700 w-full justify-start">
            <TabsTrigger value="config" className="data-[state=active]:bg-blue-600">
              策略配置
            </TabsTrigger>
            <TabsTrigger value="results" className="data-[state=active]:bg-blue-600">
              回测结果
            </TabsTrigger>
          </TabsList>
        </CardHeader>

        <CardContent>
          <TabsContent value="config" className="mt-0">
            <ConfigPanelContent />
          </TabsContent>
          <TabsContent value="results" className="mt-0">
            <SummaryCardContent />
          </TabsContent>
        </CardContent>
      </Tabs>
    </Card>
  )
}

// 配置面板内容（提取为独立组件以便复用）
function ConfigPanelContent() {
  const [strategyType, setStrategyType] = useState('trend')
  const [shortPeriod, setShortPeriod] = useState([5])
  const [longPeriod, setLongPeriod] = useState([20])
  const [initialCapital, setInitialCapital] = useState(1000000)

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="strategy-type" className="text-gray-300">策略类型</Label>
          <Select value={strategyType} onValueChange={setStrategyType}>
            <SelectTrigger className="mt-2">
              <SelectValue placeholder="选择策略类型" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="trend">趋势跟踪</SelectItem>
              <SelectItem value="mean-reversion">均值回归</SelectItem>
              <SelectItem value="momentum">动量策略</SelectItem>
              <SelectItem value="arbitrage">套利策略</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div>
          <Label htmlFor="symbol" className="text-gray-300">标的代码</Label>
          <Input id="symbol" placeholder="000001" className="mt-2" defaultValue="000001" />
        </div>
      </div>

      <div>
        <Label className="text-gray-300">短期周期: {shortPeriod[0]}天</Label>
        <Slider
          value={shortPeriod}
          onValueChange={setShortPeriod}
          max={30}
          min={3}
          step={1}
          className="mt-2"
        />
      </div>

      <div>
        <Label className="text-gray-300">长期周期: {longPeriod[0]}天</Label>
        <Slider
          value={longPeriod}
          onValueChange={setLongPeriod}
          max={120}
          min={20}
          step={5}
          className="mt-2"
        />
      </div>

      <div>
        <Label htmlFor="capital" className="text-gray-300">初始资金 (元)</Label>
        <Input
          id="capital"
          type="number"
          value={initialCapital}
          onChange={(e) => setInitialCapital(Number(e.target.value))}
          className="mt-2"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label htmlFor="start-date" className="text-gray-300">开始日期</Label>
          <Input id="start-date" type="date" defaultValue="2020-01-01" className="mt-2" />
        </div>
        <div>
          <Label htmlFor="end-date" className="text-gray-300">结束日期</Label>
          <Input id="end-date" type="date" defaultValue="2025-12-25" className="mt-2" />
        </div>
      </div>

      <div className="flex gap-3">
        <Button className="flex-1 bg-blue-600 hover:bg-blue-700">
          <Play className="h-4 w-4 mr-2" />
          运行回测
        </Button>
        <Button variant="outline" className="flex-1">
          <Download className="h-4 w-4 mr-2" />
          导出结果
        </Button>
      </div>
    </div>
  )
}

// 回测结果概览内容（提取为独立组件以便复用）
function SummaryCardContent() {
  const summary = backtestData.summary

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
      <SummaryItem
        label="总收益率"
        value={`${summary.totalReturn > 0 ? '+' : ''}${summary.totalReturn.toFixed(2)}%`}
        positive={summary.totalReturn > 0}
        icon={TrendingUp}
      />
      <SummaryItem
        label="年化收益率"
        value={`${summary.annualReturn > 0 ? '+' : ''}${summary.annualReturn.toFixed(2)}%`}
        positive={summary.annualReturn > 0}
        icon={Activity}
      />
      <SummaryItem
        label="夏普比率"
        value={summary.sharpeRatio.toFixed(2)}
        positive={summary.sharpeRatio > 1}
        icon={Target}
      />
      <SummaryItem
        label="最大回撤"
        value={`${summary.maxDrawdown.toFixed(2)}%`}
        positive={false}
        icon={AlertCircle}
      />
      <SummaryItem
        label="胜率"
        value={`${summary.winRate.toFixed(1)}%`}
        positive={summary.winRate > 50}
        icon={DollarSign}
      />
      <SummaryItem
        label="盈亏比"
        value={summary.profitLossRatio.toFixed(2)}
        positive={summary.profitLossRatio > 1}
        icon={TrendingUp}
      />
      <SummaryItem
        label="总交易"
        value={`${summary.totalTrades}次`}
        positive={true}
        icon={Activity}
      />
      <SummaryItem
        label="盈利/亏损"
        value={`${summary.profitTrades}/${summary.lossTrades}`}
        positive={summary.profitTrades > summary.lossTrades}
        icon={Target}
      />
    </div>
  )
}

// 净值曲线与月度收益（合并）
function EquityAndMonthlyReturns() {
  const [activeTab, setActiveTab] = useState('equity')

  return (
    <Card className="border-2">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <CardHeader className="pb-3">
          <TabsList className="bg-gray-900 border border-gray-700 w-full justify-start">
            <TabsTrigger value="equity" className="data-[state=active]:bg-blue-600">
              净值曲线
            </TabsTrigger>
            <TabsTrigger value="monthly" className="data-[state=active]:bg-blue-600">
              月度收益
            </TabsTrigger>
          </TabsList>
        </CardHeader>

        <CardContent>
          <TabsContent value="equity" className="mt-0">
            <EquityCurveContent />
          </TabsContent>
          <TabsContent value="monthly" className="mt-0">
            <MonthlyReturnsContent />
          </TabsContent>
        </CardContent>
      </Tabs>
    </Card>
  )
}

// 净值曲线内容（提取为独立组件以便复用）
function EquityCurveContent() {
  const curve = backtestData.equityCurve

  return (
    <div className="space-y-4">
      <div className="h-64 flex items-end justify-between gap-1">
        {curve.map((point, idx) => {
          const maxValue = Math.max(...curve.map(p => p.value))
          const height = (point.value / maxValue) * 100

          return (
            <div key={idx} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-gradient-to-t from-blue-600 to-blue-400 rounded-t hover:from-blue-500 hover:to-blue-300 transition-all cursor-pointer"
                style={{ height: `${height}%` }}
                title={`${point.date}: ¥${point.value.toLocaleString()}`}
              />
              {idx % 2 === 0 && (
                <span className="text-xs text-gray-500 transform -rotate-45 origin-left">
                  {point.date.substring(0, 4)}
                </span>
              )}
            </div>
          )
        })}
      </div>

      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-blue-500 rounded"></div>
            <span className="text-gray-400">策略净值</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 bg-gray-500 rounded"></div>
            <span className="text-gray-400">基准</span>
          </div>
        </div>
        <div className="text-gray-400">
          起始: ¥1,000,000 → 最新: ¥{curve[curve.length - 1].value.toLocaleString()}
        </div>
      </div>
    </div>
  )
}

// 月度收益内容（提取为独立组件以便复用）
function MonthlyReturnsContent() {
  const returns = backtestData.monthlyReturns

  return (
    <div className="space-y-3">
      {returns.map((item, idx) => {
        const maxReturn = Math.max(...returns.map(r => Math.abs(r.return)))
        const barWidth = (Math.abs(item.return) / maxReturn) * 100

        return (
          <div key={idx} className="flex items-center gap-3">
            <div className="w-20 text-sm text-gray-400">
              {item.month.substring(5)}
            </div>
            <div className="flex-1">
              <div className="relative h-6 bg-gray-800 rounded">
                <div
                  className={`absolute top-0 h-full rounded ${item.return >= 0 ? 'bg-green-500' : 'bg-red-500'}`}
                  style={{ width: `${barWidth}%`, left: item.return >= 0 ? '50%' : `${50 - barWidth}%` }}
                />
              </div>
            </div>
            <div className="w-24 text-right">
              <span className={`text-sm font-medium ${item.return >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {item.return >= 0 ? '+' : ''}{item.return.toFixed(2)}%
              </span>
              <div className="text-xs text-gray-500">
                基准: {item.benchmark >= 0 ? '+' : ''}{item.benchmark.toFixed(2)}%
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

function App() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.bgPrimary }}>
      {/* Header */}
      <header className="border-b-2 border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">MyStocks A股策略回测系统</h1>
            <p className="text-sm text-gray-500 mt-1">专业级量化策略回测与优化平台 v2.1</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-blue-500 text-blue-400">
              <Activity className="h-3 w-3 mr-1" />
              回测就绪
            </Badge>
            <span className="text-sm text-gray-400">
              {new Date().toLocaleString('zh-CN', {
                hour12: false,
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </span>
          </div>
        </div>
      </header>

      <main className="p-6 space-y-6">
        {/* 自选股列表选择器 */}
        <section>
          <StockListSelector />
        </section>

        <Separator className="bg-gray-800" />

        {/* 策略配置与回测结果（合并） */}
        <section>
          <StrategyConfigAndResults />
        </section>

        <Separator className="bg-gray-800" />

        {/* 净值曲线与月度收益（合并） */}
        <section>
          <EquityAndMonthlyReturns />
        </section>

        {/* 交易分析 */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div>
            <PositionAnalysis />
          </div>
          <div>
            <TradeHistory />
          </div>
        </section>

        {/* 风险指标 */}
        <section>
          <RiskMetrics />
        </section>

        {/* 底部信息 */}
        <footer className="mt-8 pt-6 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              <p>回测引擎: MyStocks Quantitative Engine</p>
              <p className="mt-1">数据来源: 通达信TDX | 问财 | 东方财富</p>
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
