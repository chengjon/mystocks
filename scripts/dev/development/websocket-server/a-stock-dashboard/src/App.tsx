import { useState, useEffect, useRef, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'
import { TrendingUp, TrendingDown, Activity, DollarSign, BarChart3, AlertTriangle, Eye, RefreshCw, Sparkles, Wifi, WifiOff, LineChart } from 'lucide-react'
import { calculateEMA, calculateRSI, calculateMACD, calculateBollingerBands } from './utils/technicalIndicators'

// 数字滚动动画Hook
function useNumberAnimation(endValue: number, duration: number = 1000) {
  const [currentValue, setCurrentValue] = useState(0)
  const [isAnimating, setIsAnimating] = useState(false)

  useEffect(() => {
    setIsAnimating(true)
    const startTime = Date.now()
    const startValue = currentValue

    const animate = () => {
      const now = Date.now()
      const progress = Math.min((now - startTime) / duration, 1)
      const easeProgress = 1 - Math.pow(1 - progress, 3) // easeOutCubic
      setCurrentValue(startValue + (endValue - startValue) * easeProgress)

      if (progress < 1) {
        requestAnimationFrame(animate)
      } else {
        setIsAnimating(false)
      }
    }

    requestAnimationFrame(animate)
  }, [endValue, duration])

  return { value: currentValue, isAnimating }
}

// WebSocket客户端Hook
function useWebSocketClient(url: string) {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected'>('disconnected')
  const [marketData, setMarketData] = useState<any>(null)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<NodeJS.Timeout | null>(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return
    }

    setConnectionStatus('connecting')
    const ws = new WebSocket(url)

    ws.onopen = () => {
      console.log('✅ WebSocket连接成功')
      setConnectionStatus('connected')
      ws.send(JSON.stringify({ action: 'start' }))
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data)

        if (message.type === 'init') {
          console.log('📦 收到初始快照:', message.data)
          setMarketData(message.data)
        } else if (message.type === 'incremental') {
          setMarketData((prev: any) => {
            if (!prev) return message.data

            const updated = { ...prev }

            message.updates.forEach((update: any) => {
              if (update.type === 'index') {
                updated.indices = prev.indices.map((idx: any) =>
                  idx.code === update.data.code ? { ...idx, ...update.data } : idx
                )
              } else if (update.type === 'stock') {
                updated.stocks = prev.stocks.map((stock: any) =>
                  stock.code === update.data.code ? { ...stock, ...update.data } : stock
                )
              }
            })

            return updated
          })
        } else if (message.type === 'info') {
          console.log('ℹ️', message.message)
        }
      } catch (error) {
        console.error('解析消息失败:', error)
      }
    }

    ws.onerror = (error) => {
      console.error('❌ WebSocket错误:', error)
      setConnectionStatus('disconnected')
    }

    ws.onclose = () => {
      console.log('🔌 WebSocket连接关闭')
      setConnectionStatus('disconnected')

      // 自动重连
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current)
      }
      reconnectTimerRef.current = setTimeout(() => {
        console.log('🔄 尝试重新连接...')
        connect()
      }, 3000)
    }

    wsRef.current = ws
  }, [url])

  const disconnect = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current)
      reconnectTimerRef.current = null
    }
    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
    }
    setConnectionStatus('disconnected')
  }, [])

  useEffect(() => {
    connect()
    return () => disconnect()
  }, [connect, disconnect])

  return { connectionStatus, marketData, disconnect }
}

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

// 模拟A股实时数据
const marketData = {
  indices: [
    { name: '上证指数', code: '000001', value: 3245.67, change: 1.23, changeAmount: 39.56, volume: '2856亿' },
    { name: '深证成指', code: '399001', value: 10234.89, change: 0.87, changeAmount: 88.45, volume: '3624亿' },
    { name: '创业板指', code: '399006', value: 2145.32, change: -0.34, changeAmount: -7.31, volume: '1658亿' },
    { name: '科创50', code: '000688', value: 987.45, change: 1.56, changeAmount: 15.18, volume: '425亿' },
  ],
  marketStats: {
    limitUp: 45,        // 涨停数
    limitDown: 12,      // 跌停数
    northBound: 52.3,   // 北向资金（亿）
    totalVolume: 8563,  // 总成交额（亿）
    riseCount: 2845,    // 上涨家数
    fallCount: 1892     // 下跌家数
  },
  watchlist: [
    { code: '600519', name: '贵州茅台', price: 1856.00, change: 2.35, volume: '2.3万手' },
    { code: '300750', name: '宁德时代', price: 245.67, change: -1.23, volume: '8.5万手' },
    { code: '601318', name: '中国平安', price: 52.34, change: 0.89, volume: '15.2万手' },
    { code: '000858', name: '五粮液', price: 178.45, change: 1.56, volume: '5.8万手' },
    { code: '002594', name: '比亚迪', price: 267.89, change: 3.12, volume: '12.1万手' },
  ],
  hotSectors: [
    { name: '新能源汽车', change: 3.45, leader: '比亚迪', leaders: 3 },
    { name: '半导体', change: 2.87, leader: '中芯国际', leaders: 5 },
    { name: '人工智能', change: 2.34, leader: '科大讯飞', leaders: 4 },
    { name: '国防军工', change: -0.89, leader: '中航沈飞', leaders: 2 },
  ],
  alerts: [
    { type: '涨停', code: '600123', name: '兰花科创', time: '09:32:15' },
    { type: '异动', code: '300059', name: '东方财富', time: '09:45:23', detail: '大单流入' },
    { type: '公告', code: '601398', name: '工商银行', time: '10:15:00', detail: '分红派息' },
    { type: '跌停', code: '002456', name: '欧菲光', time: '10:23:45' },
  ]
}

function IndexCard({ index, style }: { index: typeof marketData.indices[0], style?: React.CSSProperties }) {
  const isUp = index.change >= 0
  const animatedValue = useNumberAnimation(index.value, 800)
  const [isHovered, setIsHovered] = useState(false)

  return (
    <Card
      className="border-2 hover:border-blue-500/50 transition-all duration-300 cursor-pointer relative overflow-hidden group"
      style={style}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 悬停发光效果 */}
      <div
        className={`absolute inset-0 bg-gradient-to-br from-blue-500/10 to-purple-500/10 transition-opacity duration-300 ${
          isHovered ? 'opacity-100' : 'opacity-0'
        }`}
      />

      <CardContent className="pt-6 relative z-10">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-400">{index.name}</p>
            <p className="text-xs text-gray-500 mt-1">{index.code}</p>
          </div>
          <div className={`transition-transform duration-300 ${isHovered ? 'scale-110' : 'scale-100'}`}>
            {isUp ? (
              <TrendingUp className="h-5 w-5 text-green-400" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-400" />
            )}
          </div>
        </div>
        <div className="mt-4">
          <h3 className="text-2xl font-bold text-white">
            {animatedValue.value.toFixed(2)}
          </h3>
          <div className="flex items-center gap-2 mt-2">
            <Badge
              variant="outline"
              className={`${
                isUp
                  ? 'border-green-500 text-green-400 bg-green-500/10'
                  : 'border-red-500 text-red-400 bg-red-500/10'
              } transition-all duration-300`}
            >
              {isUp ? '+' : ''}{index.change.toFixed(2)}%
            </Badge>
            <span className={`text-sm ${isUp ? 'text-green-400' : 'text-red-400'}`}>
              {isUp ? '+' : ''}{index.changeAmount.toFixed(2)}
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-2">成交量: {index.volume}</p>
        </div>

        {/* 价格变化指示器 */}
        <div className={`absolute top-2 right-2 h-2 w-2 rounded-full ${isUp ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
      </CardContent>
    </Card>
  )
}

function StatCard({ title, value, change, icon: Icon, prefix = '' }: {
  title: string
  value: string | number
  change?: number
  icon: any
  prefix?: string
}) {
  const numericValue = typeof value === 'number' ? value : parseFloat(value.toString())
  const animatedValue = useNumberAnimation(numericValue, 1000)
  const [isHovered, setIsHovered] = useState(false)

  return (
    <Card
      className="border-2 hover:border-blue-500/50 transition-all duration-300 cursor-pointer relative overflow-hidden"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* 背景渐变效果 */}
      <div
        className={`absolute inset-0 bg-gradient-to-br from-blue-500/5 to-cyan-500/5 transition-opacity duration-300 ${
          isHovered ? 'opacity-100' : 'opacity-0'
        }`}
      />

      <CardContent className="pt-6 relative z-10">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-400">{title}</p>
            <h3 className="text-2xl font-bold text-white mt-2 tabular-nums">
              {prefix}{animatedValue.value.toLocaleString('zh-CN', { maximumFractionDigits: 2 })}
            </h3>
            {change !== undefined && (
              <p className={`text-sm mt-2 ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                {change >= 0 ? '+' : ''}{change}%
              </p>
            )}
          </div>
          <Icon
            className={`h-8 w-8 text-blue-400 transition-transform duration-300 ${
              isHovered ? 'scale-110 rotate-3' : 'scale-100 rotate-0'
            }`}
          />
        </div>
      </CardContent>
    </Card>
  )
}

function WatchlistTable({
  watchlist,
  onStockClick,
  selectedStock
}: {
  watchlist: any[]
  onStockClick?: (stock: any) => void
  selectedStock?: any
}) {
  const displayList = watchlist || marketData.watchlist

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Eye className="h-5 w-5" />
          自选股列表
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">代码</TableHead>
              <TableHead className="text-gray-400">名称</TableHead>
              <TableHead className="text-gray-400">最新价</TableHead>
              <TableHead className="text-gray-400">涨跌幅</TableHead>
              <TableHead className="text-gray-400">成交量</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {displayList.map((stock, index: number) => (
              <TableRow
                key={stock.code}
                onClick={() => onStockClick?.(stock)}
                className={`border-gray-700 hover:bg-blue-500/10 transition-all duration-300 cursor-pointer ${
                  selectedStock?.code === stock.code ? 'bg-blue-500/20' : ''
                }`}
                style={{
                  animation: `slideIn 0.3s ease-out ${index * 0.1}s both`
                }}
              >
                <TableCell className="text-gray-300">{stock.code}</TableCell>
                <TableCell className="text-white font-medium">{stock.name}</TableCell>
                <TableCell className="text-white tabular-nums">{stock.price.toFixed(2)}</TableCell>
                <TableCell>
                  <Badge
                    className={
                      stock.change >= 0
                        ? 'border-green-500 text-green-400 bg-green-500/10'
                        : 'border-red-500 text-red-400 bg-red-500/10'
                    }
                  >
                    {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}%
                  </Badge>
                </TableCell>
                <TableCell className="text-gray-400">{stock.volume}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  )
}

function HotSectors({ sectors }: { sectors: any[] }) {
  const displaySectors = sectors || marketData.hotSectors

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Activity className="h-5 w-5" />
          热门板块
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {displaySectors.map((sector, idx) => (
            <div
              key={idx}
              className="flex items-center justify-between p-3 rounded-lg bg-gray-800/50 hover:bg-gray-800 transition-all duration-300 cursor-pointer group"
              style={{
                animation: `fadeIn 0.4s ease-out ${idx * 0.1}s both`
              }}
            >
              <div className="flex-1">
                <p className="text-white font-medium group-hover:text-blue-300 transition-colors">
                  {sector.name}
                </p>
                <p className="text-xs text-gray-400 mt-1">龙头: {sector.leader}</p>
              </div>
              <div className="text-right">
                <Badge
                  className={
                    sector.change >= 0
                      ? 'border-green-500 text-green-400 bg-green-500/10'
                      : 'border-red-500 text-red-400 bg-red-500/10'
                  }
                >
                  {sector.change >= 0 ? '+' : ''}{sector.change.toFixed(2)}%
                </Badge>
                <p className="text-xs text-gray-500 mt-1">{sector.leaders}只涨停</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function AlertsPanel({ alerts }: { alerts: any[] }) {
  const displayAlerts = alerts || marketData.alerts

  const getAlertColor = (type: string) => {
    switch (type) {
      case '涨停':
        return 'border-green-500 bg-green-500/10'
      case '跌停':
        return 'border-red-500 bg-red-500/10'
      case '异动':
        return 'border-yellow-500 bg-yellow-500/10'
      case '公告':
        return 'border-blue-500 bg-blue-500/10'
      default:
        return 'border-blue-500 bg-blue-500/10'
    }
  }

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 animate-pulse" />
          实时告警
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          {displayAlerts.map((alert, idx) => (
            <div
              key={idx}
              className={`flex items-center justify-between p-3 rounded-lg bg-gray-800/50 border-l-4 ${getAlertColor(
                alert.type
              )} hover:bg-gray-800 transition-all duration-300 cursor-pointer`}
              style={{
                animation: `slideIn 0.3s ease-out ${idx * 0.15}s both`
              }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={`${
                      alert.type === '涨停'
                        ? 'border-green-500 text-green-400 bg-green-500/10'
                        : alert.type === '跌停'
                        ? 'border-red-500 text-red-400 bg-red-500/10'
                        : alert.type === '异动'
                        ? 'border-yellow-500 text-yellow-400 bg-yellow-500/10'
                        : 'border-blue-500 text-blue-400 bg-blue-500/10'
                    }`}
                  >
                    {alert.type}
                  </Badge>
                  <span className="text-white">{alert.name}</span>
                  <span className="text-gray-500">({alert.code})</span>
                </div>
                {alert.detail && (
                  <p className="text-xs text-gray-400 mt-1">{alert.detail}</p>
                )}
              </div>
              <span className="text-xs text-gray-500">{alert.time}</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

// 技术指标展示面板
function TechnicalIndicatorsPanel({ selectedStock }: { selectedStock: any }) {
  const [indicatorType, setIndicatorType] = useState<'MACD' | 'RSI' | 'BOLL' | 'EMA'>('MACD')
  const [indicators, setIndicators] = useState<any>(null)

  useEffect(() => {
    if (!selectedStock) return

    // 模拟历史价格数据（实际应用中应该从API获取）
    const mockPrices = generateMockPrices(selectedStock.price, 100)

    // 根据选择的指标类型计算指标
    let result = null
    switch (indicatorType) {
      case 'MACD':
        result = calculateMACD(mockPrices, 12, 26, 9)
        break
      case 'RSI':
        const rsiValues = calculateRSI(mockPrices, 14)
        result = { rsi: rsiValues }
        break
      case 'BOLL':
        result = calculateBollingerBands(mockPrices, 20, 2)
        break
      case 'EMA':
        const ema20 = calculateEMA(mockPrices, 20)
        const ema50 = calculateEMA(mockPrices, 50)
        result = { ema20, ema50 }
        break
    }
    setIndicators(result)
  }, [selectedStock, indicatorType])

  // 生成模拟价格数据
  function generateMockPrices(basePrice: number, count: number): number[] {
    const prices: number[] = []
    let price = basePrice
    for (let i = 0; i < count; i++) {
      price = price + (Math.random() - 0.5) * (basePrice * 0.02)
      prices.push(price)
    }
    return prices
  }

  // 获取数组最后一个有效值
  const getCurrentValue = (arr: (number | null)[]) => {
    const validValues = arr.filter(v => v !== null)
    return validValues.length > 0 ? validValues[validValues.length - 1]?.toFixed(2) : '--'
  }

  if (!selectedStock) {
    return (
      <Card className="border-2">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <LineChart className="h-5 w-5 text-blue-400" />
            技术指标
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-gray-400 text-sm">请从自选股列表中选择一只股票查看技术指标</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <LineChart className="h-5 w-5 text-blue-400" />
          技术指标 - {selectedStock.name}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* 指标选择器 */}
        <div className="flex gap-2 mb-4">
          {(['MACD', 'RSI', 'BOLL', 'EMA'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setIndicatorType(type)}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                indicatorType === type
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        {/* 指标数值展示 */}
        {indicators && (
          <div className="space-y-3">
            {indicatorType === 'MACD' && (
              <>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">MACD</span>
                  <span className="text-white font-medium">{getCurrentValue(indicators.macd)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">Signal</span>
                  <span className="text-white font-medium">{getCurrentValue(indicators.signal)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">Histogram</span>
                  <span className="text-white font-medium">{getCurrentValue(indicators.histogram)}</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  💡 MACD &gt; Signal: 买入信号 | MACD &lt; Signal: 卖出信号
                </p>
              </>
            )}

            {indicatorType === 'RSI' && (
              <>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">RSI (14)</span>
                  <span className={`font-medium ${
                    Number(getCurrentValue(indicators.rsi)) > 70 ? 'text-red-400' :
                    Number(getCurrentValue(indicators.rsi)) < 30 ? 'text-green-400' :
                    'text-white'
                  }`}>
                    {getCurrentValue(indicators.rsi)}
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-3">
                  <div
                    className="h-2 rounded-full transition-all"
                    style={{
                      width: `${getCurrentValue(indicators.rsi)}%`,
                      backgroundColor: Number(getCurrentValue(indicators.rsi)) > 70 ? '#ef4444' :
                                   Number(getCurrentValue(indicators.rsi)) < 30 ? '#22c55e' : '#3b82f6'
                    }}
                  />
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  💡 RSI &gt; 70: 超买 | RSI &lt; 30: 超卖
                </p>
              </>
            )}

            {indicatorType === 'BOLL' && (
              <>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">上轨</span>
                  <span className="text-red-400 font-medium">{getCurrentValue(indicators.upper)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">中轨</span>
                  <span className="text-white font-medium">{getCurrentValue(indicators.middle)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">下轨</span>
                  <span className="text-green-400 font-medium">{getCurrentValue(indicators.lower)}</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  💡 价格突破上轨: 强势 | 价格跌破下轨: 弱势
                </p>
              </>
            )}

            {indicatorType === 'EMA' && (
              <>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">EMA 20</span>
                  <span className="text-blue-400 font-medium">{getCurrentValue(indicators.ema20)}</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-gray-800/50 rounded-lg">
                  <span className="text-gray-400 text-sm">EMA 50</span>
                  <span className="text-purple-400 font-medium">{getCurrentValue(indicators.ema50)}</span>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  💡 EMA 20 &gt; EMA 50: 上升趋势 | EMA 20 &lt; EMA 50: 下降趋势
                </p>
              </>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function App() {
  const [currentTime, setCurrentTime] = useState(new Date())
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [selectedStock, setSelectedStock] = useState<any>(null)

  // WebSocket连接到实时数据
  const { connectionStatus, marketData: wsMarketData } = useWebSocketClient('ws://localhost:8001/ws/market')

  // 使用WebSocket数据或fallback到模拟数据
  const marketDataState = wsMarketData || marketData

  // 实时时间更新
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date())
    }, 1000)
    return () => clearInterval(timer)
  }, [])

  // 手动刷新功能（重新连接WebSocket）
  const handleRefresh = () => {
    setIsRefreshing(true)
    // WebSocket会自动重连，这里只是UI反馈
    setTimeout(() => {
      setIsRefreshing(false)
    }, 1000)
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.bgPrimary }}>
      {/* Header */}
      <header className="border-b-2 border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white flex items-center gap-2">
              <Sparkles className="h-6 w-6 text-blue-400" />
              MyStocks A股交易终端
            </h1>
            <p className="text-sm text-gray-500 mt-1">专业级量化交易平台 v2.1</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-green-500 text-green-400 animate-pulse">
              ● 市场交易中
            </Badge>
            <Badge
              variant="outline"
              className={
                connectionStatus === 'connected'
                  ? 'border-green-500 text-green-400'
                  : connectionStatus === 'connecting'
                  ? 'border-yellow-500 text-yellow-400'
                  : 'border-red-500 text-red-400'
              }
            >
              {connectionStatus === 'connected' ? (
                <>
                  <Wifi className="h-3 w-3 mr-1" />
                  实时数据已连接
                </>
              ) : connectionStatus === 'connecting' ? (
                <>
                  <WifiOff className="h-3 w-3 mr-1 animate-pulse" />
                  连接中...
                </>
              ) : (
                <>
                  <WifiOff className="h-3 w-3 mr-1" />
                  实时数据未连接
                </>
              )}
            </Badge>
            <button
              onClick={handleRefresh}
              disabled={isRefreshing}
              className="p-2 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
              title="刷新数据"
            >
              <RefreshCw className={`h-5 w-5 text-blue-400 ${isRefreshing ? 'animate-spin' : ''}`} />
            </button>
            <span className="text-sm text-gray-400">
              {currentTime.toLocaleString('zh-CN', {
                hour12: false,
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
              })}
            </span>
          </div>
        </div>
      </header>

      <main className="p-6 space-y-6">
        {/* A股主要指数 + 市场统计（合并一行） */}
        <section>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* 左侧：A股主要指数（缩窄） */}
            <div>
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-blue-400" />
                A股主要指数
              </h2>
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                {marketDataState.indices.map((idx: any) => (
                  <IndexCard key={idx.code} index={idx} />
                ))}
              </div>
            </div>

            {/* 右侧：市场统计 */}
            <div>
              <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Activity className="h-5 w-5 text-blue-400" />
                市场统计
              </h2>
              <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                <StatCard
                  title="涨停"
                  value={marketDataState.marketStats?.limitUp || marketData.marketStats.limitUp}
                  icon={TrendingUp}
                />
                <StatCard
                  title="跌停"
                  value={marketDataState.marketStats?.limitDown || marketData.marketStats.limitDown}
                  icon={TrendingDown}
                />
                <StatCard
                  title="北向资金"
                  value={marketDataState.marketStats?.northBound || marketData.marketStats.northBound}
                  change={2.34}
                  icon={DollarSign}
                  prefix="¥"
                />
                <StatCard
                  title="总成交额"
                  value={marketDataState.marketStats?.totalVolume || marketData.marketStats.totalVolume}
                  icon={BarChart3}
                  prefix="¥"
                />
                <StatCard
                  title="上涨家数"
                  value={marketDataState.marketStats?.riseCount || marketData.marketStats.riseCount}
                  icon={TrendingUp}
                />
                <StatCard
                  title="下跌家数"
                  value={marketDataState.marketStats?.fallCount || marketData.marketStats.fallCount}
                  icon={TrendingDown}
                />
              </div>
            </div>
          </div>
        </section>

        <Separator className="bg-gray-800" />

        {/* 详细信息面板 */}
        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <WatchlistTable
              watchlist={marketDataState.stocks || marketData.watchlist}
              onStockClick={setSelectedStock}
              selectedStock={selectedStock}
            />
          </div>
          <div className="lg:col-span-1">
            <HotSectors sectors={marketDataState.hotSectors || marketData.hotSectors} />
          </div>
          <div className="lg:col-span-1">
            <AlertsPanel alerts={marketDataState.alerts || marketData.alerts} />
          </div>
        </section>

        {/* 技术指标面板 */}
        {selectedStock && (
          <section className="mt-6">
            <TechnicalIndicatorsPanel selectedStock={selectedStock} />
          </section>
        )}

        {/* 底部信息 */}
        <footer className="mt-8 pt-6 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              <p>数据来源: 通达信TDX | 问财 | 东方财富</p>
              <p className="mt-1">更新频率: 实时推送 | 延迟: &lt;100ms</p>
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
