/**
 * Data Downsampling Utility
 *
 * 优化大量K线数据的显示性能
 * Implement data downsampling for large datasets (>10,000 points)
 */

import type { KLineDataPoint } from './indicators'

/**
 * 降采样方法枚举
 */
export enum DownsamplingMethod {
  /** 不降采样，返回原始数据 */
  NONE = 'none',
  /** 简单采样：每N个点取一个 */
  SIMPLE = 'simple',
  /** 保留极值点：高点和低点 */
  EXTREME = 'extreme',
  /** 保留关键点：开盘、最高、最低、收盘 */
  OHLC = 'ohlc',
  /** LTTB算法：Largest-Triangle-Three-Buckets (适合可视化) */
  LTTB = 'lttb'
}

/**
 * 降采样配置
 */
export interface DownsamplingConfig {
  /** 最大数据点数 */
  maxPoints: number
  /** 降采样方法 */
  method: DownsamplingMethod
  /** 是否保留最后一个数据点（用于显示最新数据） */
  keepLast: boolean
}

/**
 * 默认配置
 */
const DEFAULT_CONFIG: DownsamplingConfig = {
  maxPoints: 1000,
  method: DownsamplingMethod.EXTREME,
  keepLast: true
}

/**
 * 简单降采样
 * 每N个点取一个
 */
function simpleDownsample(
  data: KLineDataPoint[],
  targetLength: number,
  keepLast: boolean
): KLineDataPoint[] {
  if (data.length <= targetLength) {
    return data
  }

  const step = Math.floor(data.length / targetLength)
  const result: KLineDataPoint[] = []

  for (let i = 0; i < data.length; i += step) {
    if (result.length < targetLength || (keepLast && i === data.length - 1)) {
      result.push(data[i])
    }
  }

  // 确保包含最后一个点
  if (keepLast && result[result.length - 1] !== data[data.length - 1]) {
    result.push(data[data.length - 1])
  }

  return result
}

/**
 * 极值降采样
 * 保留高点和低点
 */
function extremeDownsample(
  data: KLineDataPoint[],
  targetLength: number,
  keepLast: boolean
): KLineDataPoint[] {
  if (data.length <= targetLength) {
    return data
  }

  const bucketSize = Math.floor(data.length / targetLength)
  const result: KLineDataPoint[] = []

  for (let i = 0; i < data.length; i += bucketSize) {
    const bucket = data.slice(i, i + bucketSize)

    if (bucket.length === 0) break

    // 找到bucket中的最高点和最低点
    let highPoint = bucket[0]
    let lowPoint = bucket[0]

    bucket.forEach(point => {
      if (point.high > highPoint.high) {
        highPoint = point
      }
      if (point.low < lowPoint.low) {
        lowPoint = point
      }
    })

    // 添加高点和低点（如果是不同点）
    result.push(highPoint)
    if (highPoint.timestamp !== lowPoint.timestamp) {
      result.push(lowPoint)
    }

    if (result.length >= targetLength) break
  }

  // 确保包含最后一个点
  if (keepLast) {
    const lastPoint = data[data.length - 1]
    if (result[result.length - 1].timestamp !== lastPoint.timestamp) {
      result.push(lastPoint)
    }
  }

  return result
}

/**
 * OHLC降采样
 * 保留开盘、最高、最低、收盘等关键点
 */
function ohlcDownsample(
  data: KLineDataPoint[],
  targetLength: number,
  keepLast: boolean
): KLineDataPoint[] {
  if (data.length <= targetLength) {
    return data
  }

  const bucketSize = Math.floor(data.length / targetLength)
  const result: KLineDataPoint[] = []

  for (let i = 0; i < data.length; i += bucketSize) {
    const bucket = data.slice(i, i + bucketSize)

    if (bucket.length === 0) break

    // 聚合bucket数据
    const open = bucket[0].open
    let high = bucket[0].high
    let low = bucket[0].low
    const close = bucket[bucket.length - 1].close
    let volume = 0

    bucket.forEach(point => {
      if (point.high > high) high = point.high
      if (point.low < low) low = point.low
      volume += point.volume
    })

    const aggregatedPoint: KLineDataPoint = {
      timestamp: bucket[0].timestamp,
      open,
      high,
      low,
      close,
      volume
    }

    result.push(aggregatedPoint)

    if (result.length >= targetLength) break
  }

  // 确保包含最后一个点
  if (keepLast) {
    const lastPoint = data[data.length - 1]
    if (result[result.length - 1].timestamp !== lastPoint.timestamp) {
      result.push(lastPoint)
    }
  }

  return result
}

/**
 * LTTB降采样算法
 * Largest-Triangle-Three-Buckets
 * 适合可视化，保留数据的整体趋势
 */
function lttbDownsample(
  data: KLineDataPoint[],
  targetLength: number,
  keepLast: boolean
): KLineDataPoint[] {
  if (data.length <= targetLength) {
    return data
  }

  // 实际目标长度（如果需要保留最后一个点）
  const actualTargetLength = keepLast ? targetLength - 1 : targetLength

  const sampled: KLineDataPoint[] = []
  const bucketSize = (data.length - 2) / (actualTargetLength - 2)

  // 始终保留第一个点
  sampled.push(data[0])

  let a = 0 // 上一个选中点的索引

  for (let i = 0; i < actualTargetLength - 2; i++) {
    // 计算当前bucket的范围
    const avgRangeStart = Math.floor((i + 1) * bucketSize) + 1
    const avgRangeEnd = Math.floor((i + 2) * bucketSize) + 1
    const avgRangeLength = avgRangeEnd - avgRangeStart

    // 计算下一个bucket的平均值
    let avgX = 0
    let avgY = 0

    for (let j = avgRangeStart; j < avgRangeEnd && j < data.length; j++) {
      avgX += j
      avgY += data[j].close
    }

    avgX /= avgRangeLength
    avgY /= avgRangeLength

    // 当前bucket的范围
    const rangeStart = Math.floor((i + 1) * bucketSize) + 1
    const rangeEnd = Math.floor((i + 2) * bucketSize) + 1

    // 在当前bucket中找到形成最大三角形的点
    let maxArea = -1
    let maxAreaPoint = data[Math.floor((rangeStart + rangeEnd) / 2)]

    const pointAX = a
    const pointAY = data[a].close

    for (let j = rangeStart; j < rangeEnd && j < data.length; j++) {
      const area = Math.abs(
        (pointAX - avgX) * (data[j].close - pointAY) -
        (pointAX - j) * (avgY - pointAY)
      ) * 0.5

      if (area > maxArea) {
        maxArea = area
        maxAreaPoint = data[j]
        a = j
      }
    }

    sampled.push(maxAreaPoint)
  }

  // 始终保留最后一个点
  if (keepLast) {
    sampled.push(data[data.length - 1])
  }

  return sampled
}

/**
 * 主降采样函数
 * 根据配置自动选择降采样方法
 */
export function downsampleData(
  data: KLineDataPoint[],
  config: Partial<DownsamplingConfig> = {}
): KLineDataPoint[] {
  const finalConfig = { ...DEFAULT_CONFIG, ...config }

  // 如果数据量小于阈值，不需要降采样
  if (data.length <= finalConfig.maxPoints) {
    return data
  }

  // 根据方法选择降采样算法
  switch (finalConfig.method) {
    case DownsamplingMethod.NONE:
      return data

    case DownsamplingMethod.SIMPLE:
      return simpleDownsample(data, finalConfig.maxPoints, finalConfig.keepLast)

    case DownsamplingMethod.EXTREME:
      return extremeDownsample(data, finalConfig.maxPoints, finalConfig.keepLast)

    case DownsamplingMethod.OHLC:
      return ohlcDownsample(data, finalConfig.maxPoints, finalConfig.keepLast)

    case DownsamplingMethod.LTTB:
      return lttbDownsample(data, finalConfig.maxPoints, finalConfig.keepLast)

    default:
      console.warn('Unknown downsampling method, using EXTREME')
      return extremeDownsample(data, finalConfig.maxPoints, finalConfig.keepLast)
  }
}

/**
 * 自动降采样
 * 根据数据量自动选择降采样参数
 */
export function autoDownsample(
  data: KLineDataPoint[],
  keepLast: boolean = true
): KLineDataPoint[] {
  const dataLength = data.length

  // 根据数据量选择降采样策略
  if (dataLength <= 1000) {
    // 不需要降采样
    return data
  } else if (dataLength <= 5000) {
    // 轻度降采样
    return downsampleData(data, {
      maxPoints: 2000,
      method: DownsamplingMethod.EXTREME,
      keepLast
    })
  } else if (dataLength <= 10000) {
    // 中度降采样
    return downsampleData(data, {
      maxPoints: 1500,
      method: DownsamplingMethod.EXTREME,
      keepLast
    })
  } else if (dataLength <= 50000) {
    // 重度降采样
    return downsampleData(data, {
      maxPoints: 1000,
      method: DownsamplingMethod.LTTB,
      keepLast
    })
  } else {
    // 极重度降采样
    return downsampleData(data, {
      maxPoints: 500,
      method: DownsamplingMethod.LTTB,
      keepLast
    })
  }
}

/**
 * 获取推荐的最大数据点数
 * 根据图表宽度和期望的像素密度
 */
export function getRecommendedMaxPoints(
  chartWidth: number,
  pointsPerPixel: number = 0.5
): number {
  return Math.floor(chartWidth * pointsPerPixel)
}

/**
 * 分块加载数据
 * 将大数据集分成多个小块，便于分批加载
 */
export function chunkData(
  data: KLineDataPoint[],
  chunkSize: number = 1000
): KLineDataPoint[][] {
  const chunks: KLineDataPoint[][] = []

  for (let i = 0; i < data.length; i += chunkSize) {
    chunks.push(data.slice(i, i + chunkSize))
  }

  return chunks
}
