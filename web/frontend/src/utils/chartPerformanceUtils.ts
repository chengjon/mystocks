/**
 * Chart Performance Optimization Utilities
 *
 * Provides performance optimization strategies for large datasets and complex charts
 * including data sampling, lazy loading, caching, and rendering optimizations.
 */

import type { EChartsOption } from 'echarts'

// ================ 数据采样策略 ================

export interface SamplingConfig {
    maxPoints: number
    strategy: 'lttb' | 'minmax' | 'average' | 'random'
    preserveExtremes: boolean
}

export class DataSampler {
    /**
     * 最大的三角形三桶化算法 (Largest Triangle Three Bucket)
     * 用于时间序列数据降采样，保持趋势特征
     */
    static lttbSampling(data: Array<{ x: number; y: number }>, threshold: number): Array<{ x: number; y: number }> {
        if (data.length <= threshold) return data

        const sampled: Array<{ x: number; y: number }> = []
        const bucketSize = (data.length - 2) / (threshold - 2)

        // 始终保留第一个和最后一个点
        sampled.push(data[0])

        for (let i = 1; i < threshold - 1; i++) {
            const bucketStart = Math.floor((i - 1) * bucketSize) + 1
            const bucketEnd = Math.floor(i * bucketSize) + 1
            const bucket = data.slice(bucketStart, bucketEnd)

            if (bucket.length > 0) {
                let maxArea = -1
                let maxAreaPoint = bucket[0]

                // 在当前桶中找到形成最大三角形的点
                for (const point of bucket) {
                    const area = this.triangleArea(data[bucketStart - 1], data[bucketEnd], point)
                    if (area > maxArea) {
                        maxArea = area
                        maxAreaPoint = point
                    }
                }

                sampled.push(maxAreaPoint)
            }
        }

        sampled.push(data[data.length - 1])
        return sampled
    }

    /**
     * 计算三角形面积
     */
    private static triangleArea(
        a: { x: number; y: number },
        b: { x: number; y: number },
        c: { x: number; y: number }
    ): number {
        return Math.abs((a.x * (b.y - c.y) + b.x * (c.y - a.y) + c.x * (a.y - b.y)) / 2)
    }

    /**
     * 最大最小值采样
     */
    static minmaxSampling(data: Array<{ x: number; y: number }>, threshold: number): Array<{ x: number; y: number }> {
        if (data.length <= threshold) return data

        const sampled: Array<{ x: number; y: number }> = []
        const bucketSize = Math.floor(data.length / threshold)

        sampled.push(data[0]) // 保留第一个点

        for (let i = 1; i < threshold - 1; i++) {
            const start = i * bucketSize
            const end = Math.min((i + 1) * bucketSize, data.length)
            const bucket = data.slice(start, end)

            if (bucket.length > 0) {
                const minPoint = bucket.reduce((min, p) => (p.y < min.y ? p : min))
                const maxPoint = bucket.reduce((max, p) => (p.y > max.y ? p : max))

                // 保留极值点
                if (minPoint.x < maxPoint.x) {
                    sampled.push(minPoint, maxPoint)
                } else {
                    sampled.push(maxPoint, minPoint)
                }
            }
        }

        sampled.push(data[data.length - 1]) // 保留最后一个点
        return sampled
    }

    /**
     * 平均值采样
     */
    static averageSampling(data: Array<{ x: number; y: number }>, threshold: number): Array<{ x: number; y: number }> {
        if (data.length <= threshold) return data

        const sampled: Array<{ x: number; y: number }> = []
        const bucketSize = Math.floor(data.length / threshold)

        for (let i = 0; i < threshold; i++) {
            const start = i * bucketSize
            const end = Math.min((i + 1) * bucketSize, data.length)
            const bucket = data.slice(start, end)

            if (bucket.length > 0) {
                const avgX = bucket.reduce((sum, p) => sum + p.x, 0) / bucket.length
                const avgY = bucket.reduce((sum, p) => sum + p.y, 0) / bucket.length
                sampled.push({ x: avgX, y: avgY })
            }
        }

        return sampled
    }

    /**
     * 智能采样策略
     */
    static smartSampling(
        data: Array<{ x: number; y: number }>,
        config: SamplingConfig
    ): Array<{ x: number; y: number }> {
        if (data.length <= config.maxPoints) return data

        switch (config.strategy) {
            case 'lttb':
                return this.lttbSampling(data, config.maxPoints)
            case 'minmax':
                return this.minmaxSampling(data, config.maxPoints)
            case 'average':
                return this.averageSampling(data, config.maxPoints)
            case 'random':
                return this.randomSampling(data, config.maxPoints)
            default:
                return this.lttbSampling(data, config.maxPoints)
        }
    }

    /**
     * 随机采样
     */
    static randomSampling(data: Array<{ x: number; y: number }>, threshold: number): Array<{ x: number; y: number }> {
        if (data.length <= threshold) return data

        const sampled: Array<{ x: number; y: number }> = []
        const step = Math.floor(data.length / threshold)

        for (let i = 0; i < threshold; i++) {
            const index = Math.min(i * step + Math.floor(Math.random() * step), data.length - 1)
            sampled.push(data[index])
        }

        return sampled
    }
}

// ================ 懒加载和虚拟化 ================

export interface VirtualScrollConfig {
    itemHeight: number
    containerHeight: number
    bufferSize: number
}

export class VirtualScroller {
    private visibleRange: { start: number; end: number } = { start: 0, end: 0 }

    /**
     * 计算可见范围
     */
    calculateVisibleRange(scrollTop: number, config: VirtualScrollConfig): { start: number; end: number } {
        const start = Math.floor(scrollTop / config.itemHeight)
        const visibleCount = Math.ceil(config.containerHeight / config.itemHeight)
        const end = start + visibleCount + config.bufferSize * 2

        this.visibleRange = {
            start: Math.max(0, start - config.bufferSize),
            end: Math.min(end, Math.ceil(scrollTop / config.itemHeight) + visibleCount + config.bufferSize)
        }

        return this.visibleRange
    }

    /**
     * 获取可见数据
     */
    getVisibleData<T>(data: T[], range: { start: number; end: number }): T[] {
        return data.slice(range.start, range.end)
    }

    /**
     * 计算总高度
     */
    getTotalHeight(dataLength: number, itemHeight: number): number {
        return dataLength * itemHeight
    }
}

// ================ 缓存管理 ================

export interface CacheConfig {
    maxSize: number
    ttl: number // Time to live in milliseconds
    strategy: 'lru' | 'lfu' | 'fifo'
}

export class ChartDataCache {
    private cache = new Map<string, { data: any; timestamp: number; accessCount: number }>()
    private maxSize: number
    private ttl: number
    private strategy: 'lru' | 'lfu' | 'fifo'

    constructor(config: CacheConfig) {
        this.maxSize = config.maxSize
        this.ttl = config.ttl
        this.strategy = config.strategy
    }

    /**
     * 获取缓存数据
     */
    get(key: string): any | null {
        const item = this.cache.get(key)

        if (!item) return null

        // 检查是否过期
        if (Date.now() - item.timestamp > this.ttl) {
            this.cache.delete(key)
            return null
        }

        // 更新访问信息
        item.accessCount++
        item.timestamp = Date.now() // 更新最后访问时间

        return item.data
    }

    /**
     * 设置缓存数据
     */
    set(key: string, data: any): void {
        // 如果缓存已满，根据策略移除项目
        if (this.cache.size >= this.maxSize) {
            this.evict()
        }

        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            accessCount: 1
        })
    }

    /**
     * 根据策略移除缓存项
     */
    private evict(): void {
        if (this.cache.size === 0) return

        let keyToRemove: string | null = null

        switch (this.strategy) {
            case 'lru': // Least Recently Used
                let oldestTime = Date.now()
                for (const [key, item] of this.cache) {
                    if (item.timestamp < oldestTime) {
                        oldestTime = item.timestamp
                        keyToRemove = key
                    }
                }
                break

            case 'lfu': // Least Frequently Used
                let minAccess = Infinity
                for (const [key, item] of this.cache) {
                    if (item.accessCount < minAccess) {
                        minAccess = item.accessCount
                        keyToRemove = key
                    }
                }
                break

            case 'fifo': // First In First Out
                keyToRemove = this.cache.keys().next().value
                break
        }

        if (keyToRemove) {
            this.cache.delete(keyToRemove)
        }
    }

    /**
     * 清空缓存
     */
    clear(): void {
        this.cache.clear()
    }

    /**
     * 获取缓存统计信息
     */
    getStats(): { size: number; hitRate: number; totalAccess: number } {
        const totalAccess = Array.from(this.cache.values()).reduce((sum, item) => sum + item.accessCount, 0)
        return {
            size: this.cache.size,
            hitRate: 0, // 需要外部跟踪命中率
            totalAccess
        }
    }
}

// ================ 渲染优化 ================

export class RenderOptimizer {
    /**
     * 增量更新配置
     */
    static createIncrementalUpdate(baseOption: EChartsOption, newData: any, dataPath: string[]): EChartsOption {
        const updateOption: EChartsOption = { ...baseOption }

        // 使用ECharts的增量更新特性
        let current = updateOption
        for (let i = 0; i < dataPath.length - 1; i++) {
            const key = dataPath[i]
            if (!current[key]) current[key] = {}
            current = current[key] as any
        }

        const lastKey = dataPath[dataPath.length - 1]
        current[lastKey] = newData

        return updateOption
    }

    /**
     * 分批渲染大数据
     */
    static createProgressiveRender(
        data: any[],
        batchSize: number = 1000,
        delay: number = 16 // ~60fps
    ): Promise<any[]> {
        return new Promise(resolve => {
            const result: any[] = []
            let index = 0

            const processBatch = () => {
                const endIndex = Math.min(index + batchSize, data.length)
                const batch = data.slice(index, endIndex)
                result.push(...batch)
                index = endIndex

                if (index < data.length) {
                    setTimeout(processBatch, delay)
                } else {
                    resolve(result)
                }
            }

            processBatch()
        })
    }

    /**
     * Web Workers 数据处理
     */
    static async processInWorker(data: any[], processor: (data: any[]) => any, workerPath?: string): Promise<any> {
        // 检查是否支持Web Workers
        if (typeof Worker === 'undefined') {
            return processor(data)
        }

        return new Promise((resolve, reject) => {
            try {
                const worker = new Worker(workerPath || '/chart-worker.js')

                worker.postMessage({
                    type: 'process',
                    data,
                    processor: processor.toString()
                })

                worker.onmessage = e => {
                    if (e.data.type === 'result') {
                        resolve(e.data.result)
                    } else if (e.data.type === 'error') {
                        reject(new Error(e.data.error))
                    }
                    worker.terminate()
                }

                worker.onerror = error => {
                    reject(error)
                    worker.terminate()
                }
            } catch (error) {
                // 如果Web Workers失败，回退到主线程处理
                resolve(processor(data))
            }
        })
    }

    /**
     * 内存优化配置
     */
    static createMemoryOptimizedConfig(baseOption: EChartsOption): EChartsOption {
        return {
            ...baseOption,
            // 禁用不必要的动画
            animation: false,
            // 减少渐变和阴影
            series: baseOption.series?.map((series: any) => ({
                ...series,
                // 简化样式
                itemStyle: {
                    ...series.itemStyle,
                    shadowBlur: 0,
                    shadowColor: 'transparent'
                }
            })),
            // 优化工具提示
            tooltip: {
                ...baseOption.tooltip,
                confine: true,
                enterable: false
            }
        }
    }

    /**
     * 检测设备性能
     */
    static detectDeviceCapability(): {
        isLowEnd: boolean
        recommendedBatchSize: number
        enableProgressive: boolean
    } {
        // 检测内存
        const memory = (navigator as any).deviceMemory || 4
        // 检测CPU核心数
        const cores = navigator.hardwareConcurrency || 2
        // 检测是否为移动设备
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)

        const isLowEnd = memory < 4 || cores < 2 || isMobile

        return {
            isLowEnd,
            recommendedBatchSize: isLowEnd ? 500 : 2000,
            enableProgressive: isLowEnd || memory < 8
        }
    }
}
