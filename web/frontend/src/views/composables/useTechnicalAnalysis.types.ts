export interface IndicatorParameters {
  [key: string]: number | string | boolean | undefined
  timeperiod?: number
}

export interface SelectedIndicator {
  abbreviation: string
  parameters: IndicatorParameters
}

export interface OHLCVData {
  dates: string[]
  open: number[]
  high: number[]
  low: number[]
  close: number[]
  volume: number[]
}

export interface IndicatorOutput {
  output_name: string
  values: (number | null)[]
  displayName: string
}

export interface ChartIndicator {
  abbreviation: string
  parameters: IndicatorParameters
  outputs: IndicatorOutput[]
  panelType: 'overlay' | 'separate'
}

export interface ChartData {
  symbol: string
  symbolName: string
  ohlcv: OHLCVData | null
  indicators: ChartIndicator[]
  calculationTime: number
}

export interface DateRangeShortcut {
  text: string
  value: () => Date[]
}

export interface KlineDataItem {
  date: string
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface KlineApiResponse {
  success: boolean
  data: KlineDataItem[]
  stock_code?: string
  stock_name?: string
  total?: number
}

export interface IndicatorConfig {
  id: number
  name: string
  indicators: SelectedIndicator[]
}

export interface ConfigListResponse {
  total_count: number
  configs: IndicatorConfig[]
}

export interface ConfigOption {
  label: string
  value: number
}

declare global {
  interface Window {
    deleteConfig: (configId: number) => Promise<void>
  }
}
