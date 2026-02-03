import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Separator } from '@/components/ui/separator'
import { Progress } from '@/components/ui/progress'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  TrendingUp, TrendingDown, AlertTriangle, Shield,
  Activity, PieChart, BarChart3, Eye, DollarSign,
  Target, Zap, HeartPulse, Info, Plus, Trash2, Save,
  Edit2, GripVertical, X, Check, Sparkles
} from 'lucide-react'

// 数字滚动动画Hook
function useNumberAnimation(endValue: number, duration: number = 1000) {
  const [currentValue, setCurrentValue] = useState(0)

  useEffect(() => {
    const startTime = Date.now()
    const startValue = currentValue

    const animate = () => {
      const now = Date.now()
      const progress = Math.min((now - startTime) / duration, 1)
      const easeProgress = 1 - Math.pow(1 - progress, 3)
      setCurrentValue(startValue + (endValue - startValue) * easeProgress)

      if (progress < 1) {
        requestAnimationFrame(animate)
      }
    }

    requestAnimationFrame(animate)
  }, [endValue, duration])

  return currentValue
}

// A股风险管理配色
const colors = {
  bgPrimary: '#0B0F19',
  riskHigh: '#FF5252',    // 高风险 - 红色
  riskMedium: '#FFA726',  // 中风险 - 橙色
  riskLow: '#66BB6A',     // 低风险 - 绿色
  bgCard: '#232936',
  primary: '#2979FF'
}

// 风险条件类型
type RiskCondition = {
  id: number
  name: string
  type: 'technical' | 'price' | 'volume' | 'custom'
  description: string
  enabled: boolean
  createdAt: string
}

// 模拟A股风险数据
const riskData = {
  // 风险条件列表
  riskConditions: [
    { id: 1, name: '日KDJ死叉', type: 'technical', description: '日K线KDJ指标出现死叉信号', enabled: true, createdAt: '2025-12-20' },
    { id: 2, name: '月KDJ死叉', type: 'technical', description: '月K线KDJ指标出现死叉信号', enabled: true, createdAt: '2025-12-20' },
    { id: 3, name: '股价创新低', type: 'price', description: '股价创60日新低', enabled: false, createdAt: '2025-12-21' },
    { id: 4, name: '成交量异常萎缩', type: 'volume', description: '成交量低于5日均量的50%', enabled: true, createdAt: '2025-12-22' },
    { id: 5, name: 'MACD顶背离', type: 'technical', description: '股价创新高但MACD未创新高', enabled: false, createdAt: '2025-12-23' },
    { id: 6, name: '跌破重要均线', type: 'price', description: '股价跌破60日均线', enabled: true, createdAt: '2025-12-23' },
  ],

  // 1. 持仓风险
  positionRisk: {
    totalValue: 1258000,      // 总市值（元）
    totalCost: 1180000,       // 总成本（元）
    profit: 78000,            // 浮动盈亏
    profitRate: 6.61,         // 盈亏比例
    positions: [
      { code: '600519', name: '贵州茅台', value: 285600, cost: 268000, weight: 22.7, risk: 'high' },
      { code: '300750', name: '宁德时代', value: 198500, cost: 215000, weight: 15.8, risk: 'high' },
      { code: '601318', name: '中国平安', value: 156800, cost: 145000, weight: 12.5, risk: 'medium' },
      { code: '000858', name: '五粮液', value: 134200, cost: 138000, weight: 10.7, risk: 'medium' },
      { code: '002594', name: '比亚迪', value: 267900, cost: 245000, weight: 21.3, risk: 'high' },
      { code: '600036', name: '招商银行', value: 89500, cost: 92000, weight: 7.1, risk: 'low' },
      { code: '601012', name: '隆基绿能', value: 125500, cost: 78000, weight: 9.9, risk: 'high' },
    ]
  },

  // 2. 组合风险
  portfolioRisk: {
    volatility: 18.5,          // 波动率
    maxDrawdown: -12.3,        // 最大回撤
    sharpe: 1.85,               // 夏普比率
    beta: 1.12,                // Beta系数
    var: -85000,               // VaR（风险价值）
    concentration: 45.2        // 集中度（%）
  },

  // 3. 市场情绪
  sentiment: {
    index: 65,                 // 情绪指数（0-100）
    fearGreed: 'greed',        // 恐惧贪婪指数
    putCallRatio: 0.68,        // 认沽认购比
      margin: 15230,           // 融资余额（亿）
      shortBalance: 89.5       // 融券余额（亿）
  },

  // 4. 风险告警
  alerts: [
    { level: 'critical', type: '集中度过高', message: '贵州茅台持仓占比22.7%，超过20%风控线', time: '10:23:45' },
    { level: 'warning', type: '波动率异常', message: '宁德时代近5日波动率达35%，注意风险', time: '09:45:12' },
    { level: 'info', type: '涨停风险', message: '比亚迪涨停，考虑止盈', time: '10:15:33' },
    { level: 'warning', type: '流动性风险', message: '隆基绿能成交量不足，流动性下降', time: '13:23:11' },
    { level: 'critical', type: 'ST风险', message: '持仓中有ST股票，需特别关注', time: '14:12:00' }
  ],

  // 5. 回撤分析
  drawdown: {
    current: -3.2,            // 当前回撤
    max: -15.8,               // 历史最大回撤
    avg: -8.5,                // 平均回撤
    recoveryDays: 23,         // 恢复天数
    history: [
      { date: '2025-12-01', value: 0, nav: 1000000 },
      { date: '2025-12-05', value: -5.2, nav: 948000 },
      { date: '2025-12-10', value: -12.8, nav: 872000 },
      { date: '2025-12-15', value: -15.8, nav: 842000 },
      { date: '2025-12-20', value: -8.5, nav: 915000 },
      { date: '2025-12-25', value: -3.2, nav: 968000 }
    ]
  },

  // 6. 相关性矩阵
  correlation: [
    { stock1: '贵州茅台', stock2: '五粮液', value: 0.85 },
    { stock1: '宁德时代', stock2: '比亚迪', value: 0.72 },
    { stock1: '中国平安', stock2: '招商银行', value: 0.68 },
    { stock1: '隆基绿能', stock2: '宁德时代', value: 0.81 },
    { stock1: '比亚迪', stock2: '宁德时代', value: 0.72 },
    { stock1: '贵州茅台', stock2: '中国平安', value: 0.12 }
  ],

  // 7. 风险归因
  attribution: {
    market: 5.2,              // 市场风险
    sector: 2.8,               // 行业风险
    style: 1.5,                // 风格风险
    specific: -2.9             // 特质风险
  },

  // 8. 压力测试
  stressTest: {
    crash2008: -28.5,         // 2008暴跌情景
    crash2015: -22.3,         // 2015股灾情景
    crash2020: -18.7,         // 2020疫情情景
    tradeWar: -15.2           // 贸易摩擦情景
  }
}

function RiskGauge({ value, label, size = 'default' }: { value: number, label: string, size?: 'small' | 'default' }) {
  const getRiskLevel = (val: number) => {
    if (val >= 70) return { color: 'text-red-500', bg: 'bg-red-500/20', label: '高风险' }
    if (val >= 40) return { color: 'text-orange-500', bg: 'bg-orange-500/20', label: '中风险' }
    return { color: 'text-green-500', bg: 'bg-green-500/20', label: '低风险' }
  }

  const risk = getRiskLevel(value)
  const sizeClass = size === 'small' ? 'w-16 h-16' : 'w-24 h-24'

  return (
    <div className="flex flex-col items-center gap-2">
      <div className={`${sizeClass} rounded-full border-4 ${risk.bg} ${risk.color} flex items-center justify-center`}>
        <span className={`font-bold ${size === 'small' ? 'text-lg' : 'text-2xl'}`}>{value}</span>
      </div>
      <div className="text-center">
        <p className="text-xs text-gray-400">{label}</p>
        <Badge className={`${risk.bg} ${risk.color} border-0 mt-1`}>{risk.label}</Badge>
      </div>
    </div>
  )
}

// 风险条件列表组件（增强版）
function RiskConditionsList() {
  const [conditions, setConditions] = useState<RiskCondition[]>(riskData.riskConditions)
  const [newConditionName, setNewConditionName] = useState('')
  const [newConditionDesc, setNewConditionDesc] = useState('')
  const [newConditionType, setNewConditionType] = useState<'technical' | 'price' | 'volume' | 'custom'>('technical')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [editName, setEditName] = useState('')
  const [editDesc, setEditDesc] = useState('')
  const [editType, setEditType] = useState<'technical' | 'price' | 'volume' | 'custom'>('technical')

  const toggleCondition = (id: number) => {
    setConditions(conditions.map(cond =>
      cond.id === id ? { ...cond, enabled: !cond.enabled } : cond
    ))
  }

  const deleteCondition = (id: number) => {
    setConditions(conditions.filter(cond => cond.id !== id))
  }

  const startEdit = (cond: RiskCondition) => {
    setEditingId(cond.id)
    setEditName(cond.name)
    setEditDesc(cond.description)
    setEditType(cond.type)
  }

  const saveEdit = (id: number) => {
    setConditions(conditions.map(cond =>
      cond.id === id
        ? { ...cond, name: editName, description: editDesc, type: editType }
        : cond
    ))
    setEditingId(null)
  }

  const cancelEdit = () => {
    setEditingId(null)
    setEditName('')
    setEditDesc('')
  }

  const addCondition = () => {
    if (!newConditionName.trim()) return

    const newCondition: RiskCondition = {
      id: Math.max(...conditions.map(c => c.id)) + 1,
      name: newConditionName,
      type: newConditionType,
      description: newConditionDesc || '自定义风险条件',
      enabled: true,
      createdAt: new Date().toISOString().split('T')[0]
    }

    setConditions([...conditions, newCondition])
    setNewConditionName('')
    setNewConditionDesc('')
  }

  const getTypeLabel = (type: string) => {
    const labels = {
      technical: '技术指标',
      price: '价格',
      volume: '成交量',
      custom: '自定义'
    }
    return labels[type as keyof typeof labels] || type
  }

  const getTypeColor = (type: string) => {
    const colors = {
      technical: 'border-blue-500 text-blue-400 bg-blue-500/10',
      price: 'border-purple-500 text-purple-400 bg-purple-500/10',
      volume: 'border-orange-500 text-orange-400 bg-orange-500/10',
      custom: 'border-green-500 text-green-400 bg-green-500/10'
    }
    return colors[type as keyof typeof colors] || colors.custom
  }

  return (
    <Card className="border-2">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2">
            <Shield className="h-5 w-5" />
            风险条件列表
          </CardTitle>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
            <Save className="h-4 w-4 mr-1" />
            保存配置
          </Button>
        </div>
        <p className="text-sm text-gray-400 mt-2">
          管理自定义风险条件，可应用于自选股列表或单个股票进行风险监控。支持拖拽排序和实时编辑。
        </p>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* 添加新条件 */}
        <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
          <h3 className="text-white font-medium mb-4 flex items-center gap-2">
            <Plus className="h-4 w-4" />
            添加风险条件
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm text-gray-400 mb-2 block">条件名称</label>
              <Input
                placeholder="如: 日KDJ死叉"
                value={newConditionName}
                onChange={(e) => setNewConditionName(e.target.value)}
                className="bg-gray-900 border-gray-700 text-white"
              />
            </div>
            <div>
              <label className="text-sm text-gray-400 mb-2 block">条件类型</label>
              <select
                value={newConditionType}
                onChange={(e) => setNewConditionType(e.target.value as any)}
                className="w-full h-10 px-3 rounded-md bg-gray-900 border border-gray-700 text-white text-sm"
              >
                <option value="technical">技术指标</option>
                <option value="price">价格</option>
                <option value="volume">成交量</option>
                <option value="custom">自定义</option>
              </select>
            </div>
            <div>
              <label className="text-sm text-gray-400 mb-2 block">条件描述</label>
              <Input
                placeholder="条件描述"
                value={newConditionDesc}
                onChange={(e) => setNewConditionDesc(e.target.value)}
                className="bg-gray-900 border-gray-700 text-white"
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={addCondition}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                <Plus className="h-4 w-4 mr-1" />
                添加条件
              </Button>
            </div>
          </div>
        </div>

        {/* 条件列表 */}
        <div className="space-y-2">
          <h3 className="text-white font-medium mb-3">已保存的条件 ({conditions.length})</h3>
          {conditions.map((cond, index) => (
            <div
              key={cond.id}
              className={`flex items-center justify-between p-4 rounded-lg transition-all duration-300 ${
                cond.enabled
                  ? 'bg-gray-800/50 border-l-4 border-blue-500 hover:bg-gray-800'
                  : 'bg-gray-900/30 border-l-4 border-gray-600 hover:bg-gray-800/30 opacity-60'
              }`}
              style={{
                animation: `fadeIn 0.3s ease-out ${index * 0.05}s both`
              }}
            >
              <div className="flex items-center gap-3 flex-1">
                {/* 拖拽手柄 */}
                <div className="cursor-grab active:cursor-grabbing text-gray-500 hover:text-gray-300">
                  <GripVertical className="h-5 w-5" />
                </div>

                {/* 条件信息 */}
                <div className="flex-1">
                  {editingId === cond.id ? (
                    <div className="grid grid-cols-3 gap-2">
                      <Input
                        value={editName}
                        onChange={(e) => setEditName(e.target.value)}
                        className="bg-gray-900 border-gray-700 text-white h-8"
                      />
                      <select
                        value={editType}
                        onChange={(e) => setEditType(e.target.value as any)}
                        className="h-8 px-2 rounded bg-gray-900 border border-gray-700 text-white text-xs"
                      >
                        <option value="technical">技术指标</option>
                        <option value="price">价格</option>
                        <option value="volume">成交量</option>
                        <option value="custom">自定义</option>
                      </select>
                      <Input
                        value={editDesc}
                        onChange={(e) => setEditDesc(e.target.value)}
                        className="bg-gray-900 border-gray-700 text-white h-8"
                      />
                    </div>
                  ) : (
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-white font-medium">{cond.name}</span>
                        <Badge className={getTypeColor(cond.type)}>
                          {getTypeLabel(cond.type)}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-400">{cond.description}</p>
                    </div>
                  )}
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex items-center gap-2">
                {editingId === cond.id ? (
                  <>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => saveEdit(cond.id)}
                      className="text-green-400 hover:text-green-300 hover:bg-green-500/10 h-8 w-8 p-0"
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={cancelEdit}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10 h-8 w-8 p-0"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </>
                ) : (
                  <>
                    <button
                      onClick={() => toggleCondition(cond.id)}
                      className={`px-3 py-1 rounded text-xs font-medium transition-all ${
                        cond.enabled
                          ? 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'
                          : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                      }`}
                    >
                      {cond.enabled ? '已启用' : '已禁用'}
                    </button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => startEdit(cond)}
                      className="text-blue-400 hover:text-blue-300 hover:bg-blue-500/10 h-8 w-8 p-0"
                    >
                      <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => deleteCondition(cond.id)}
                      className="text-red-400 hover:text-red-300 hover:bg-red-500/10 h-8 w-8 p-0"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* 提示信息 */}
        {conditions.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Shield className="h-12 w-12 mx-auto mb-3 opacity-50" />
            <p>暂无风险条件，请添加您的第一个条件</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

function PositionRiskCard() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <PieChart className="h-5 w-5" />
          持仓风险分析
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="text-center">
            <p className="text-sm text-gray-400">总市值</p>
            <p className="text-xl font-bold text-white mt-1">¥{riskData.positionRisk.totalValue.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400">总成本</p>
            <p className="text-xl font-bold text-white mt-1">¥{riskData.positionRisk.totalCost.toLocaleString()}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400">浮动盈亏</p>
            <p className={`text-xl font-bold mt-1 ${riskData.positionRisk.profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              ¥{riskData.positionRisk.profit.toLocaleString()}
            </p>
          </div>
          <div className="text-center">
            <p className="text-sm text-gray-400">盈亏比例</p>
            <p className={`text-xl font-bold mt-1 ${riskData.positionRisk.profitRate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {riskData.positionRisk.profitRate >= 0 ? '+' : ''}{riskData.positionRisk.profitRate}%
            </p>
          </div>
        </div>

        <Table>
          <TableHeader>
            <TableRow className="border-gray-700">
              <TableHead className="text-gray-400">代码</TableHead>
              <TableHead className="text-gray-400">名称</TableHead>
              <TableHead className="text-gray-400">市值</TableHead>
              <TableHead className="text-gray-400">成本</TableHead>
              <TableHead className="text-gray-400">占比</TableHead>
              <TableHead className="text-gray-400">风险</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {riskData.positionRisk.positions.map((pos, idx) => (
              <TableRow key={idx} className="border-gray-700">
                <TableCell className="text-gray-300">{pos.code}</TableCell>
                <TableCell className="text-white">{pos.name}</TableCell>
                <TableCell className="text-white">¥{pos.value.toLocaleString()}</TableCell>
                <TableCell className="text-white">¥{pos.cost.toLocaleString()}</TableCell>
                <TableCell>
                  <Badge className={pos.weight > 20 ? 'border-red-500 text-red-400' : 'border-green-500 text-green-400'}>
                    {pos.weight}%
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge className={
                    pos.risk === 'high' ? 'border-red-500 text-red-400' :
                    pos.risk === 'medium' ? 'border-orange-500 text-orange-400' :
                    'border-green-500 text-green-400'
                  }>
                    {pos.risk === 'high' ? '高' : pos.risk === 'medium' ? '中' : '低'}
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

function PortfolioRiskCard() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          组合风险指标
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-3 gap-6">
          <RiskGauge value={Math.abs(riskData.portfolioRisk.maxDrawdown)} label="最大回撤 (%)" />
          <RiskGauge value={riskData.portfolioRisk.volatility} label="波动率 (%)" />
          <RiskGauge value={riskData.portfolioRisk.concentration} label="集中度 (%)" />
        </div>

        <Separator className="bg-gray-700 my-6" />

        <div className="grid grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-gray-400">夏普比率</p>
            <p className="text-xl font-bold text-white mt-1">{riskData.portfolioRisk.sharpe}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">Beta系数</p>
            <p className="text-xl font-bold text-white mt-1">{riskData.portfolioRisk.beta}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">VaR（95%）</p>
            <p className="text-xl font-bold text-red-400 mt-1">¥{Math.abs(riskData.portfolioRisk.var).toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">当前回撤</p>
            <p className="text-xl font-bold text-orange-400 mt-1">{riskData.portfolioRisk.maxDrawdown}%</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function SentimentCard() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <HeartPulse className="h-5 w-5" />
          市场情绪分析
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-400">市场情绪指数</span>
              <Badge className="bg-green-500/20 text-green-400 border-0">{riskData.sentiment.fearGreed === 'greed' ? '贪婪' : '恐惧'}</Badge>
            </div>
            <Progress value={riskData.sentiment.index} className="h-3" />
            <p className="text-xs text-gray-500 mt-1">0（极度恐慌）→ 100（极度贪婪）</p>
          </div>

          <Separator className="bg-gray-700" />

          <div className="grid grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-gray-400">认沽认购比</p>
              <p className="text-lg font-bold text-white mt-1">{riskData.sentiment.putCallRatio}</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">融资余额</p>
              <p className="text-lg font-bold text-blue-400 mt-1">¥{riskData.sentiment.margin.toLocaleString()}亿</p>
            </div>
            <div>
              <p className="text-sm text-gray-400">融券余额</p>
              <p className="text-lg font-bold text-orange-400 mt-1">{riskData.sentiment.shortBalance}亿</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

function AlertsCard() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          风险告警
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {riskData.alerts.map((alert, idx) => (
            <Alert key={idx} className={
              alert.level === 'critical' ? 'border-red-500 bg-red-500/10' :
              alert.level === 'warning' ? 'border-orange-500 bg-orange-500/10' :
              'border-blue-500 bg-blue-500/10'
            }>
              <AlertTriangle className={`h-4 w-4 ${
                alert.level === 'critical' ? 'text-red-400' :
                alert.level === 'warning' ? 'text-orange-400' :
                'text-blue-400'
              }`} />
              <AlertDescription>
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <p className="text-white font-medium">{alert.type}</p>
                    <p className="text-sm text-gray-300 mt-1">{alert.message}</p>
                  </div>
                  <span className="text-xs text-gray-500">{alert.time}</span>
                </div>
              </AlertDescription>
            </Alert>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function DrawdownChart() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Activity className="h-5 w-5" />
          回撤分析
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div>
            <p className="text-sm text-gray-400">当前回撤</p>
            <p className="text-xl font-bold text-orange-400">{riskData.drawdown.current}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">历史最大</p>
            <p className="text-xl font-bold text-red-400">{riskData.drawdown.max}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">平均回撤</p>
            <p className="text-xl font-bold text-white">{riskData.drawdown.avg}%</p>
          </div>
          <div>
            <p className="text-sm text-gray-400">恢复天数</p>
            <p className="text-xl font-bold text-blue-400">{riskData.drawdown.recoveryDays}天</p>
          </div>
        </div>

        <div className="space-y-2">
          <p className="text-sm text-gray-400 mb-3">回撤历史</p>
          {riskData.drawdown.history.map((item, idx) => (
            <div key={idx} className="flex items-center gap-4">
              <span className="text-xs text-gray-500 w-24">{item.date}</span>
              <div className="flex-1 h-6 bg-gray-800 rounded overflow-hidden">
                <div
                  className={`h-full ${item.value <= -10 ? 'bg-red-500' : item.value <= -5 ? 'bg-orange-500' : 'bg-yellow-500'}`}
                  style={{ width: `${Math.abs(item.value)}%` }}
                />
              </div>
              <span className={`text-xs font-bold ${item.value <= -10 ? 'text-red-400' : item.value <= -5 ? 'text-orange-400' : 'text-yellow-400'} w-16 text-right`}>
                {item.value}%
              </span>
              <span className="text-xs text-gray-500 w-24 text-right">¥{(item.nav / 10000).toFixed(1)}万</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function AttributionCard() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Target className="h-5 w-5" />
          风险归因
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {[
            { label: '市场风险', value: riskData.attribution.market, color: 'bg-blue-500' },
            { label: '行业风险', value: riskData.attribution.sector, color: 'bg-purple-500' },
            { label: '风格风险', value: riskData.attribution.style, color: 'bg-orange-500' },
            { label: '特质风险', value: riskData.attribution.specific, color: 'bg-pink-500' }
          ].map((item, idx) => (
            <div key={idx}>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">{item.label}</span>
                <span className={`text-sm font-bold ${item.value >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {item.value >= 0 ? '+' : ''}{item.value}%
                </span>
              </div>
              <Progress value={Math.abs(item.value)} className="h-2">
                <div className={item.color} />
              </Progress>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function StressTestCard() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Zap className="h-5 w-5" />
          压力测试
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {Object.entries(riskData.stressTest).map(([scenario, loss], idx) => (
            <div key={idx} className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">
                    {scenario === 'crash2008' ? '2008年暴跌' :
                     scenario === 'crash2015' ? '2015年股灾' :
                     scenario === 'crash2020' ? '2020年疫情' :
                     '贸易摩擦情景'}
                  </p>
                  <p className="text-xs text-gray-500 mt-1">
                    {scenario === 'crash2008' ? '上证指数下跌72%' :
                     scenario === 'crash2015' ? '千股跌停，流动性危机' :
                     scenario === 'crash2020' ? '疫情冲击，全球暴跌' :
                     '中美贸易摩擦升级'}
                  </p>
                </div>
                <div className="text-right">
                  <p className={`text-2xl font-bold text-red-400`}>
                    {loss >= 0 ? '' : ''}{loss}%
                  </p>
                  <p className="text-xs text-gray-500">预估损失</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function CorrelationMatrix() {
  return (
    <Card className="border-2">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Eye className="h-5 w-5" />
          相关性矩阵
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow className="border-gray-700">
                <TableHead className="text-gray-400">股票</TableHead>
                <TableHead className="text-gray-400">贵州茅台</TableHead>
                <TableHead className="text-gray-400">五粮液</TableHead>
                <TableHead className="text-gray-400">宁德时代</TableHead>
                <TableHead className="text-gray-400">比亚迪</TableHead>
                <TableHead className="text-gray-400">中国平安</TableHead>
                <TableHead className="text-gray-400">招商银行</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {riskData.positionRisk.positions.slice(0, 6).map((stock, rowIdx) => (
                <TableRow key={rowIdx} className="border-gray-700">
                  <TableCell className="text-gray-300">{stock.name}</TableCell>
                  {riskData.positionRisk.positions.slice(0, 6).map((_, colIdx) => {
                    const correlation = riskData.correlation.find(
                      c => c.stock1 === stock.name && c.stock2 === riskData.positionRisk.positions[colIdx].name
                    )
                    const value = correlation?.value || 0
                    return (
                      <TableCell key={colIdx}>
                        <div className="flex items-center gap-2">
                          <Progress
                            value={Math.abs(value) * 100}
                            className={`h-2 ${value > 0 ? 'bg-green-500' : 'bg-blue-500'}`}
                          />
                          <span className={`text-xs font-bold ${Math.abs(value) > 0.7 ? 'text-white' : 'text-gray-500'}`}>
                            {value.toFixed(2)}
                          </span>
                        </div>
                      </TableCell>
                    )
                  })}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  )
}

function App() {
  return (
    <div className="min-h-screen" style={{ backgroundColor: colors.bgPrimary }}>
      {/* Header */}
      <header className="border-b-2 border-gray-800 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-white">MyStocks A股风险管理</h1>
            <p className="text-sm text-gray-500 mt-1">专业级量化风险控制平台</p>
          </div>
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="border-blue-500 text-blue-400">
              <Shield className="h-3 w-3 inline mr-1" />
              实时监控中
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
        {/* 风险条件列表 */}
        <RiskConditionsList />

        <Separator className="bg-gray-800" />

        {/* 风险管理标签页 */}
        <Tabs defaultValue="position" className="space-y-6">
          <TabsList className="bg-gray-900 border border-gray-700">
            <TabsTrigger value="position" className="data-[state=active]:bg-blue-600">
              持仓风险
            </TabsTrigger>
            <TabsTrigger value="portfolio" className="data-[state=active]:bg-blue-600">
              组合风险
            </TabsTrigger>
            <TabsTrigger value="sentiment" className="data-[state=active]:bg-blue-600">
              市场情绪
            </TabsTrigger>
            <TabsTrigger value="alerts" className="data-[state=active]:bg-blue-600">
              风险告警
            </TabsTrigger>
            <TabsTrigger value="drawdown" className="data-[state=active]:bg-blue-600">
              回撤分析
            </TabsTrigger>
            <TabsTrigger value="attribution" className="data-[state=active]:bg-blue-600">
              风险归因
            </TabsTrigger>
            <TabsTrigger value="correlation" className="data-[state=active]:bg-blue-600">
              相关性
            </TabsTrigger>
            <TabsTrigger value="stresstest" className="data-[state=active]:bg-blue-600">
              压力测试
            </TabsTrigger>
          </TabsList>

          <TabsContent value="position" className="space-y-6">
            <PositionRiskCard />
          </TabsContent>

          <TabsContent value="portfolio" className="space-y-6">
            <PortfolioRiskCard />
          </TabsContent>

          <TabsContent value="sentiment" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <SentimentCard />
              <DrawdownChart />
            </div>
          </TabsContent>

          <TabsContent value="alerts" className="space-y-6">
            <AlertsCard />
          </TabsContent>

          <TabsContent value="drawdown" className="space-y-6">
            <DrawdownChart />
          </TabsContent>

          <TabsContent value="attribution" className="space-y-6">
            <AttributionCard />
          </TabsContent>

          <TabsContent value="correlation" className="space-y-6">
            <CorrelationMatrix />
          </TabsContent>

          <TabsContent value="stresstest" className="space-y-6">
            <StressTestCard />
          </TabsContent>
        </Tabs>

        {/* 底部信息 */}
        <footer className="mt-8 pt-6 border-t border-gray-800">
          <div className="flex items-center justify-between text-sm text-gray-500">
            <div>
              <p>数据来源: A股实时持仓 | 市场情绪数据 | 历史回测数据</p>
              <p className="mt-1">更新频率: 实时计算 | 风险模型: VaR | 夏普比率</p>
            </div>
            <div className="text-right">
              <p>© 2025 MyStocks Risk Management</p>
              <p className="mt-1">专业A股风险控制平台</p>
            </div>
          </div>
        </footer>
      </main>
    </div>
  )
}

export default App
