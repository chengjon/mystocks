/**
 * KLineChart v9 TypeScript Type Declaration
 *
 * Based on /opt/mydoc/mymd/KLINECHART_API.md
 * Extends the klinecharts npm package with complete type definitions
 *
 * @version 9.8.12
 * @see https://klinecharts.com/
 */

declare module 'klinecharts' {
  /**
   * 格式化器
   */
  interface Formatter {
    date?: (timestamp: number, format: string) => string
    dateTime?: (timestamp: number, format: string) => string
    price?: (value: number, precision: number) => string
    volume?: (value: number, precision: number) => string
  }

  /**
   * 技术指标
   */
  interface Indicator {
    name?: string
    shortName?: string
    calcParams?: (number | string)[]
    figures?: IndicatorFigure[]
    calc?: any  // 放宽类型限制，支持各种形式的计算函数
    createTooltipDataSource?: any
    styles?: any
  }

  /**
   * 技术指标图形
   */
  interface IndicatorFigure {
    key: string
    title?: string
    type: 'line' | 'circle' | 'rect' | 'text' | 'bar'
    styles?: any  // 放宽类型限制，支持数组、回调或任何形式
    baseFigure?: any
  }

  /**
   * 指标计算回调
   */
  type IndicatorCalcCallback<T = any> = (
    kLineDataList: KLineData[],
    options?: { calcParams?: (number | string)[]; figures?: IndicatorFigure[] }
  ) => T | any

  /**
   * 指标图形样式回调
   */
  type IndicatorFigureStylesCallback<T = any> = (
    data: any,
    indicator: Indicator
  ) => T

  /**
   * 覆盖物
   */
  interface Overlay {
    name: string
    totalStep?: number
    points?: OverlayPoint[]
    extendData?: any
    createPointFigures?: (options: any) => any
    performEventPressedMove?: (options: any) => boolean
    performEventMove?: (options: any) => boolean
  }

  /**
   * 覆盖物点
   */
  interface OverlayPoint {
    timestamp: number
    value: number
    [key: string]: any
  }

  /**
   * 窗格选项
   */
  interface PaneOptions {
    id?: string
    height?: number
    minHeight?: number
    axisOptions?: {
      name?: string
    }
    calcParams?: any | (number | string)[]
  }

  /**
   * 坐标
   */
  interface Coordinate {
    x: number
    y: number
  }

  /**
   * 点
   */
  interface Point {
    timestamp?: number
    value?: number
    dataIndex?: number
    [key: string]: any
  }

  /**
   * 类型定义
   */
  type CandleType =
    | 'candle_solid'
    | 'candle_stroke'
    | 'candle_up_stroke'
    | 'ohlc'
    | 'area'
    | 'candle'
    | 'candle_t'

  type TooltipShowRule = 'always' | 'follow_cross' | 'none' | 'always_cross'

  type TooltipShowType = 'standard' | 'rect' | 'rect_cross'

  type LineType = 'solid' | 'dashed' | 'dotted'

  type YAxisPosition = 'left' | 'right' | 'none'

  type LayoutChildType =
    | 'candle'
    | 'volume'
    | 'indicator'
    | 'yAxis'
    | 'candle_pane'
    | 'xAxis'
    | 'XAxis'

  type ActionType =
    | 'onZoom'
    | 'onScroll'
    | 'onCrosshairChange'
    | 'onVisibleRangeChange'
    | 'onPaneDrag'

  /**
   * K线数据
   */
  interface KLineData {
    timestamp: number
    open: number
    high: number
    low: number
    close: number
    volume: number
    amount?: number
    [key: string]: any
  }

  /**
   * 图表数据接口
   */
  interface KLineChartData {
    dataList?: KLineData[]
    data?: KLineData[]
    loadData?(data: KLineData[]): void
    getData?(): KLineData[]
  }

  /**
   * 图表实例接口
   * 扩展自原始 Chart 接口，补充项目中使用的方法
   */
  interface Chart {
    /**
     * 基础配置方法
     */
    setStyles(styles: Styles | string): void
    getStyles(): Styles

    /**
     * 语言设置
     */
    setLocale(locale: string): void

    /**
     * 数据操作
     */
    applyNewData(dataList: KLineData[], callback?: () => void): void
    applyMoreData(dataList: KLineData[], more: boolean, callback?: () => void): void
    updateData(data: KLineData, callback?: () => void): void

    /**
     * 技术指标操作
     */
    createIndicator(
      value: string | Indicator,
      isStack?: boolean,
      paneOptions?: PaneOptions,
      callback?: () => void
    ): Pane | null
    createIndicator(
      value: string | Indicator,
      isStack?: boolean,
      callback?: () => void
    ): Pane | null
    createIndicator(
      value: string | Indicator,
      callback?: () => void
    ): Pane | null
    getIndicators(filter?: any): Indicator[]
    overrideIndicator(override: any, paneId?: string): void
    removeIndicator(paneId: string, name?: string): void
    removeIndicator(name: string): void

    /**
     * 覆盖物操作
     */
    createOverlay(value: string | Overlay, paneId?: string): string | null
    getOverlays(filter?: any): Overlay[]
    overrideOverlay(override: any): void
    removeOverlay(id: string): void

    /**
     * 窗格操作
     */
    setPaneOptions(options: any): void
    getPaneOptions(id?: string): PaneOptions

    /**
     * 滚动操作
     */
    scrollByDistance(distance: number, animationDuration?: number): void
    scrollToRealTime(animationDuration?: number): void
    scrollToDataIndex(dataIndex: number, animationDuration?: number): void
    scrollToTimestamp(timestamp: number, animationDuration?: number): void

    /**
     * 缩放操作
     */
    zoomAtCoordinate(scale: number, coordinate: Coordinate, animationDuration?: number): void
    zoomAtDataIndex(scale: number, dataIndex: number, animationDuration?: number): void
    zoomAtTimestamp(scale: number, timestamp: number, animationDuration?: number): void

    /**
     * 坐标转换
     */
    convertToPixel(points: Point[], filter?: any): Coordinate[] | null
    convertFromPixel(coordinates: Coordinate[], filter?: any): Point[] | null

    /**
     * 事件订阅
     */
    executeAction(type: ActionType, data?: any): void
    subscribeAction(type: ActionType, callback: (data?: any) => void): void
    unsubscribeAction(type: ActionType, callback: (data?: any) => void): void

    /**
     * DOM和尺寸
     */
    getDom(paneId?: string, position?: string): HTMLElement
    getSize(paneId?: string, position?: string): { width: number; height: number }

    /**
     * 其他操作
     */
    getConvertPictureUrl(includeOverlay?: boolean, type?: string, backgroundColor?: string): string
    resize(): void

    /**
     * 数据加载方法
     */
    loadData(data: KLineData[]): void
    getData(): KLineData[]
    getVisibleRange?(): VisibleRange

    /**
     * 时间范围操作
     */
    getTimeScaleVisibleRange(): TimeScaleRange | null
    zoomToTimeScaleVisibleRange(from: number, to: number): void
    setVisibleRange(from: number, to: number): void
  }

  /**
   * 窗格
   */
  interface Pane {
    id: string
    options: PaneOptions
  }

  /**
   * 全局静态方法
   */
  function init(
    ds: string | HTMLElement,
    options?: ChartOptions
  ): Chart

  function dispose(dcs: string | HTMLElement | Chart): void

  function registerStyles(name: string, styles: Styles): void

  function registerLocale(locale: string, locales: any): void

  function getSupportedLocales(): string[]

  function registerIndicator(indicator: any): void  // 放宽类型限制

  function getSupportedIndicators(): string[]

  function registerOverlay(overlay: Overlay): void

  function getSupportedOverlays(): string[]

  function registerFigure(figure: any): void

  function getSupportedFigures(): string[]

  function getFigureClass(name: string): any

  function registerXAxis(axis: any): void

  function registerYAxis(axis: any): void

  /**
   * 工具方法
   */
  namespace utils {
    function clone<T>(obj: T): T
    function merge<T>(target: any, source: T): T
    function isString(value: any): value is string
    function isNumber(value: any): value is number
    function isValid(value: any): boolean
    function isObject(value: any): value is object
    function isArray(value: any): value is any[]
    function isFunction(value: any): value is Function
    function isBoolean(value: any): value is boolean

    function formatValue(value: number, precision?: number): string
    function formatPrecision(value: number, precision?: number): string
    function formatBigNumber(value: number): string
    function formatDate(timestamp: number, format: string): string
    function formatThousands(value: number): string
    function formatFoldDecimal(value: number, foldDecimals: number): string

    function calcTextWidth(text: string, fontSize: number, fontFamily: string): number

    function checkCoordinateOnArc(coordinate: Coordinate, attrs: any): boolean
    function checkCoordinateOnCircle(coordinate: Coordinate, attrs: any): boolean
    function checkCoordinateOnLine(coordinate: Coordinate, attrs: any): boolean
    function checkCoordinateOnPolygon(coordinate: Coordinate, attrs: any): boolean
    function checkCoordinateOnRect(coordinate: Coordinate, attrs: any): boolean
    function checkCoordinateOnText(coordinate: Coordinate, attrs: any): boolean
  }

  export = klinecharts
}

/**
 * 全局类型导出
 */
export type {
  Chart,
  ChartOptions,
  Styles,
  KLineData,
  KLineChartData,
  Indicator,
  Overlay,
  CandleType,
  TooltipShowRule,
  TooltipShowType,
  LineType,
  YAxisPosition,
  LayoutChildType,
  LayoutOptions,
  ActionType,
  PaneOptions,
  Coordinate,
  Point,
  IndicatorCalcCallback,
  IndicatorFigureStylesCallback,
  TimeScaleRange,
  VisibleRange
}
