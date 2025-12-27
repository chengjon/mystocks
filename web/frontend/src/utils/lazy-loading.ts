/**
 * K线数据懒加载工具
 *
 * Implement lazy loading for historical data
 * Load initial 1000 points, then load more on scroll/zoom
 */

import type { KLineDataPoint } from './indicators'
import { downsampleData, DownsamplingMethod } from './data-sampling'

/**
 * 数据加载状态
 */
export enum LoadingStatus {
  /** 空闲 */
  IDLE = 'idle',
  /** 加载中 */
  LOADING = 'loading',
  /** 已完成 */
  COMPLETED = 'completed',
  /** 出错 */
  ERROR = 'error'
}

/**
 * 数据块
 */
export interface DataChunk {
  /** 数据点 */
  data: KLineDataPoint[]
  /** 起始索引 */
  startIndex: number
  /** 结束索引 */
  endIndex: number
  /** 是否为第一块 */
  isFirst: boolean
  /** 是否为最后一块 */
  isLast: boolean
}

/**
 * 加载请求配置
 */
export interface LoadRequestConfig {
  /** 数据符号 */
  symbol: string
  /** 时间周期 */
  period: string
  /** 起始时间戳 */
  fromTimestamp?: number
  /** 结束时间戳 */
  toTimestamp?: number
  /** 数据点数量 */
  limit?: number
  /** 是否使用复权 */
  adjust?: 'forward' | 'backward' | 'none'
}

/**
 * 懒加载管理器配置
 */
export interface LazyLoaderConfig {
  /** 初始加载数量 */
  initialLoadSize: number
  /** 每次加载数量 */
  chunkSize: number
  /** 最大缓存数据量 */
  maxCacheSize: number
  /** 是否启用降采样 */
  enableDownsampling: boolean
  /** 预加载数据块数量 */
  preloadChunks: number
  /** 数据加载函数 */
  dataLoader: (config: LoadRequestConfig) => Promise<KLineDataPoint[]>
}

/**
 * 默认配置
 */
const DEFAULT_CONFIG: LazyLoaderConfig = {
  initialLoadSize: 1000,
  chunkSize: 500,
  maxCacheSize: 10000,
  enableDownsampling: true,
  preloadChunks: 2,
  dataLoader: async () => []
}

/**
 * K线数据懒加载管理器
 */
export class KLineDataLazyLoader {
  private config: LazyLoaderConfig
  private status: LoadingStatus = LoadingStatus.IDLE
  private cachedData: KLineDataPoint[] = []
  private loadedChunks: DataChunk[] = []
  private currentSymbol: string = ''
  private currentPeriod: string = ''
  private totalDataCount: number = 0
  private error: Error | null = null

  constructor(config: Partial<LazyLoaderConfig> = {}) {
    this.config = { ...DEFAULT_CONFIG, ...config }
  }

  /**
   * 初始化加载器
   */
  async initialize(
    symbol: string,
    period: string,
    adjust: 'forward' | 'backward' | 'none' = 'none'
  ): Promise<KLineDataPoint[]> {
    this.currentSymbol = symbol
    this.currentPeriod = period
    this.status = LoadingStatus.LOADING
    this.error = null
    this.cachedData = []
    this.loadedChunks = []

    try {
      // 加载初始数据
      const initialData = await this.loadDataChunk({
        symbol,
        period,
        limit: this.config.initialLoadSize,
        adjust
      })

      this.cachedData = initialData
      this.totalDataCount = initialData.length

      // 记录第一个数据块
      this.loadedChunks.push({
        data: initialData,
        startIndex: 0,
        endIndex: initialData.length - 1,
        isFirst: true,
        isLast: initialData.length < this.config.initialLoadSize
      })

      // 预加载后续数据块
      if (this.config.preloadChunks > 0 && !this.loadedChunks[0].isLast) {
        this.preloadNextChunks(adjust)
      }

      this.status = LoadingStatus.COMPLETED

      return initialData
    } catch (err) {
      this.error = err as Error
      this.status = LoadingStatus.ERROR
      throw err
    }
  }

  /**
   * 加载更多历史数据（向左）
   */
  async loadMore(
    adjust: 'forward' | 'backward' | 'none' = 'none'
  ): Promise<KLineDataPoint[]> {
    if (this.status === LoadingStatus.LOADING) {
      return []
    }

    const lastChunk = this.loadedChunks[this.loadedChunks.length - 1]
    if (lastChunk && lastChunk.isLast) {
      // 已经加载到最后
      return []
    }

    this.status = LoadingStatus.LOADING

    try {
      const fromTimestamp = lastChunk
        ? lastChunk.data[lastChunk.data.length - 1].timestamp - 1
        : Date.now()

      const newData = await this.loadDataChunk({
        symbol: this.currentSymbol,
        period: this.currentPeriod,
        fromTimestamp,
        limit: this.config.chunkSize,
        adjust
      })

      if (newData.length === 0) {
        // 标记最后一个数据块为已加载完成
        if (lastChunk) {
          lastChunk.isLast = true
        }
        this.status = LoadingStatus.COMPLETED
        return []
      }

      // 添加到缓存
      const startIndex = this.cachedData.length
      this.cachedData = [...this.cachedData, ...newData]
      this.totalDataCount = this.cachedData.length

      // 记录数据块
      const newChunk: DataChunk = {
        data: newData,
        startIndex,
        endIndex: startIndex + newData.length - 1,
        isFirst: false,
        isLast: newData.length < this.config.chunkSize
      }

      this.loadedChunks.push(newChunk)

      // 检查缓存大小，超出则清理旧数据
      this.checkCacheSize()

      this.status = LoadingStatus.COMPLETED

      return newData
    } catch (err) {
      this.error = err as Error
      this.status = LoadingStatus.ERROR
      throw err
    }
  }

  /**
   * 加载指定时间范围的数据
   */
  async loadRange(
    fromTimestamp: number,
    toTimestamp: number,
    adjust: 'forward' | 'backward' | 'none' = 'none'
  ): Promise<KLineDataPoint[]> {
    this.status = LoadingStatus.LOADING

    try {
      const data = await this.loadDataChunk({
        symbol: this.currentSymbol,
        period: this.currentPeriod,
        fromTimestamp,
        toTimestamp,
        limit: this.config.chunkSize,
        adjust
      })

      this.status = LoadingStatus.COMPLETED

      return data
    } catch (err) {
      this.error = err as Error
      this.status = LoadingStatus.ERROR
      throw err
    }
  }

  /**
   * 获取当前已加载的所有数据
   */
  getAllData(): KLineDataPoint[] {
    return this.cachedData
  }

  /**
   * 获取降采样后的数据（用于渲染）
   */
  getDisplayData(maxPoints: number = 1000): KLineDataPoint[] {
    if (!this.config.enableDownsampling) {
      return this.cachedData
    }

    return downsampleData(this.cachedData, {
      maxPoints,
      method: DownsamplingMethod.LTTB,
      keepLast: true
    })
  }

  /**
   * 获取加载状态
   */
  getStatus(): LoadingStatus {
    return this.status
  }

  /**
   * 获取错误信息
   */
  getError(): Error | null {
    return this.error
  }

  /**
   * 重置加载器
   */
  reset(): void {
    this.cachedData = []
    this.loadedChunks = []
    this.status = LoadingStatus.IDLE
    this.error = null
    this.totalDataCount = 0
  }

  /**
   * 加载数据块
   */
  private async loadDataChunk(
    config: LoadRequestConfig
  ): Promise<KLineDataPoint[]> {
    return await this.config.dataLoader(config)
  }

  /**
   * 预加载后续数据块
   */
  private async preloadNextChunks(
    adjust: 'forward' | 'backward' | 'none'
  ): Promise<void> {
    for (let i = 0; i < this.config.preloadChunks; i++) {
      const lastChunk = this.loadedChunks[this.loadedChunks.length - 1]
      if (lastChunk && lastChunk.isLast) {
        break
      }

      try {
        await this.loadMore(adjust)
      } catch (err) {
        console.warn('Preload failed:', err)
        break
      }
    }
  }

  /**
   * 检查缓存大小，超出则清理旧数据
   */
  private checkCacheSize(): void {
    if (this.cachedData.length > this.config.maxCacheSize) {
      // 保留最新的数据
      const excess = this.cachedData.length - this.config.maxCacheSize
      this.cachedData = this.cachedData.slice(excess)

      // 更新数据块的起始索引
      this.loadedChunks.forEach(chunk => {
        chunk.startIndex -= excess
      })

      // 移除完全超出缓存的数据块
      this.loadedChunks = this.loadedChunks.filter(
        chunk => chunk.endIndex >= 0
      )
    }
  }

  /**
   * 查找指定时间戳最近的数据点
   */
  findNearestDataPoint(timestamp: number): KLineDataPoint | null {
    if (this.cachedData.length === 0) {
      return null
    }

    // 二分查找
    let left = 0
    let right = this.cachedData.length - 1

    while (left < right) {
      const mid = Math.floor((left + right) / 2)
      if (this.cachedData[mid].timestamp < timestamp) {
        left = mid + 1
      } else {
        right = mid
      }
    }

    // 返回最近的数据点
    if (left === 0) {
      return this.cachedData[0]
    }

    const prevPoint = this.cachedData[left - 1]
    const currPoint = this.cachedData[left]

    if (
      Math.abs(prevPoint.timestamp - timestamp) <
      Math.abs(currPoint.timestamp - timestamp)
    ) {
      return prevPoint
    } else {
      return currPoint
    }
  }

  /**
   * 获取数据加载进度
   */
  getLoadProgress(): {
    loaded: number
    total: number
    percentage: number
  } {
    const lastChunk = this.loadedChunks[this.loadedChunks.length - 1]
    const isComplete = lastChunk?.isLast || false

    return {
      loaded: this.cachedData.length,
      total: isComplete ? this.cachedData.length : this.cachedData.length + this.config.chunkSize,
      percentage: isComplete ? 100 : Math.min(99, (this.cachedData.length / (this.cachedData.length + this.config.chunkSize)) * 100)
    }
  }
}

/**
 * 创建懒加载管理器实例
 */
export function createLazyLoader(
  dataLoader: (config: LoadRequestConfig) => Promise<KLineDataPoint[]>,
  config?: Partial<LazyLoaderConfig>
): KLineDataLazyLoader {
  return new KLineDataLazyLoader({
    ...config,
    dataLoader
  })
}
