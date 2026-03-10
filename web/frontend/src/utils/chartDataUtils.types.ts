export interface ChartDataPoint {
  name: string
  value: number
  [key: string]: unknown
}

export interface TimeSeriesDataPoint {
  timestamp: number | string | Date
  value: number
  [key: string]: unknown
}

export interface SankeyNode {
  name: string
  [key: string]: unknown
}

export interface SankeyLink {
  source: string
  target: string
  value: number
  [key: string]: unknown
}

export interface TreeNode {
  name: string
  value?: number
  children?: TreeNode[]
  [key: string]: unknown
}

export interface HeatmapDataPoint {
  x: number | string
  y: number | string
  value: number
  [key: string]: unknown
}
