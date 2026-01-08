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

// 注意：不要使用 export * from 'echarts/core'，这会导致全量导入
// 组件中应该使用：import * as echarts from 'echarts'（自动使用按需引入的版本）
