/**
 * ECharts 按需引入配置
 * 优化目标：体积从 3MB 降到 600KB (↓80%)
 */
import { use } from 'echarts/core'

// 按需引入图表类型
import {
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  CandlestickChart,
  EffectScatterChart,
  LinesChart,
  HeatmapChart,
  GraphChart,
  TreemapChart,
  GaugeChart
} from 'echarts/charts'

// 按需引入组件
import {
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  ToolboxComponent,
  VisualMapComponent,
  TimelineComponent,
  CalendarComponent,
  GraphicComponent
} from 'echarts/components'

// 按需引入渲染器
import {
  CanvasRenderer
  // SVGRenderer  // 需要时启用
} from 'echarts/renderers'

// 注册必需的组件
use([
  // 图表类型
  BarChart,
  LineChart,
  PieChart,
  ScatterChart,
  CandlestickChart,
  EffectScatterChart,
  LinesChart,
  HeatmapChart,
  GraphChart,
  TreemapChart,
  GaugeChart,

  // 组件
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  DataZoomComponent,
  MarkLineComponent,
  MarkPointComponent,
  ToolboxComponent,
  VisualMapComponent,
  TimelineComponent,
  CalendarComponent,
  GraphicComponent,

  // 渲染器
  CanvasRenderer
])

// 注意：组件中应该使用 import * as echarts from 'echarts'
// Vite 会自动使用我们已注册的按需引入版本

// ============================================
//   ARTDECO V3.0 THEME - ECharts主题配置
//   ⭐ 专家评估版：A股颜色规范 + 完整字体系统
// ============================================

import type { EChartsOption } from 'echarts'

/**
 * ArtDeco V3.0 主题 - 专为MyStocks金融仪表盘设计
 *
 * 核心特性：
 * - A股颜色约定：红涨绿跌（与西方市场相反）
 * - 大胆的金色品牌元素
 * - 完整的字体系统：Cinzel + Barlow + JetBrains Mono
 * - 深色背景优化长时间盯盘
 */
export const artDecoTheme: EChartsOption = {
  // ============================================
  //   COLOR PALETTE - A股颜色规范
  //   ⚠️ 红色=上涨，绿色=下跌（A股市场约定）
  // ============================================
  color: [
    '#D4AF37',  // 古典金 - 主品牌色
    '#4A90E2',  // 装饰蓝
    '#E94B3C',  // 装饰红
    '#FF5252',  // 鲜红 - 上涨 (A股约定) ✅
    '#CD7F32',  // 青铜
    '#00E676'   // 鲜绿 - 下跌 (A股约定) ✅
  ],

  backgroundColor: '#1A1A1D',  // 深炭灰 - 主背景

  // ============================================
  //   TYPOGRAPHY - 字体系统
  // ============================================
  textStyle: {
    fontFamily: "'Barlow', 'Inter', sans-serif",  // 正文字体
    color: '#FFFFFF',
    fontSize: 14
  },

  // ============================================
  //   TITLE - 标题样式
  // ============================================
  title: {
    textStyle: {
      color: '#D4AF37',  // 金色标题
      fontWeight: 'bold',
      fontSize: 20,
      fontFamily: "'Cinzel', serif"  // ArtDeco标题字体
    },
    subtextStyle: {
      color: '#B8B8B8',
      fontSize: 14,
      fontFamily: "'Barlow', sans-serif"
    }
  },

  // ============================================
  //   AXIS - 坐标轴样式
  // ============================================
  axisLine: {
    lineStyle: {
      color: '#D4AF37',  // 金色轴线
      width: 2
    }
  },

  axisLabel: {
    color: '#FFFFFF',
    fontFamily: "'JetBrains Mono', monospace"  // 等宽字体用于数字
  },

  splitLine: {
    lineStyle: {
      color: ['#2A2A2E'],
      type: 'dashed'
    }
  },

  // ============================================
  //   LEGEND - 图例样式
  // ============================================
  legend: {
    textStyle: {
      color: '#FFFFFF',
      fontFamily: "'Barlow', sans-serif"
    },
    itemStyle: {
      borderColor: '#D4AF37',
      borderWidth: 2
    }
  },

  // ============================================
  //   TOOLTIP - 提示框样式
  // ============================================
  tooltip: {
    backgroundColor: 'rgba(26, 26, 29, 0.95)',
    borderColor: '#D4AF37',
    borderWidth: 2,
    textStyle: {
      fontFamily: "'Barlow', sans-serif",
      color: '#FFFFFF'
    },
    extraCssText: 'box-shadow: 0 0 20px rgba(212, 175, 55, 0.3);'
  },

  // ============================================
  //   CANDLESTICK - K线图样式 (A股颜色)
  // ============================================
  candlestick: {
    itemStyle: {
      color: '#FF5252',        // 涨 - 红色 (A股约定) ✅
      color0: '#00E676',       // 跌 - 绿色 (A股约定) ✅
      borderColor: '#FF5252',
      borderColor0: '#00E676',
      borderWidth: 2
    },
    emphasis: {
      itemStyle: {
        borderColor: '#D4AF37',  // Hover时金色边框
        borderWidth: 3
      }
    }
  },

  // ============================================
  //   LINE CHART - 折线图样式
  // ============================================
  line: {
    itemStyle: {
      borderWidth: 2
    },
    lineStyle: {
      width: 3
    },
    symbolSize: 8,
    symbol: 'circle',
    smooth: true
  },

  // ============================================
  //   BAR CHART - 柱状图样式
  // ============================================
  bar: {
    itemStyle: {
      borderRadius: [4, 4, 0, 0],
      borderColor: '#D4AF37',
      borderWidth: 1
    }
  }
}

/**
 * 获取涨跌颜色（A股约定）
 * @param value - 数值（正数=涨，负数=跌）
 * @returns 颜色值
 */
export function getStockColor(value: number): string {
  if (value > 0) return '#FF5252'  // 红色 - 上涨
  if (value < 0) return '#00E676'  // 绿色 - 下跌
  return '#B0B3B8'                 // 灰色 - 平盘
}

/**
 * 获取涨跌图标
 * @param value - 数值
 * @returns 图标字符
 */
export function getStockIcon(value: number): string {
  if (value > 0) return '▲'  // 上涨
  if (value < 0) return '▼'  // 下跌
  return '━'                 // 平盘
}
