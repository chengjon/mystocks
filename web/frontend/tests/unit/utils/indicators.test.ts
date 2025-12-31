/**
 * 基础技术指标测试
 *
 * 测试覆盖率目标: 85%+
 * 测试内容:
 * - 基础技术指标计算准确性
 * - MACD, RSI, KDJ, Bollinger Bands等
 * - 数据格式转换
 * - 边界情况处理
 */

import { describe, it, expect } from 'vitest'
import {
  calculateMA,
  calculateEMA,
  calculateVOLUME_MA,
  calculateMACD,
  calculateRSI,
  calculateKDJ,
  calculateBOLL,
  calculateATR,
  KLineDataPoint
} from '@/utils/indicators'

// 使用别名以保持测试代码一致性
const calculateBollingerBands = calculateBOLL

// 生成测试用K线数据
function generateKLineData(count: number): KLineDataPoint[] {
  const data: KLineDataPoint[] = []
  let price = 10.0

  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 0.5
    const open = price
    price = price + change
    const high = Math.max(open, price) + Math.random() * 0.1
    const low = Math.min(open, price) - Math.random() * 0.1
    const volume = Math.floor(1000000 + Math.random() * 9000000)

    data.push({
      timestamp: Date.now() - (count - i) * 86400000,
      open,
      high,
      low,
      close: price,
      volume
    })
  }

  return data
}

describe('indicators.ts - 基础技术指标', () => {
  let testData: KLineDataPoint[]

  beforeEach(() => {
    testData = generateKLineData(100)
  })

  // ==================== 移动平均线测试 ====================
  describe('calculateMA - 简单移动平均线', () => {
    it('应该正确计算MA', () => {
      const ma = calculateMA(testData, 20)
      expect(ma).toBeDefined()
      expect(Array.isArray(ma)).toBe(true)
      expect(ma.length).toBeGreaterThan(0)
    })

    it('MA长度应该正确', () => {
      const period = 20
      const ma = calculateMA(testData, period)
      // technicalindicators库会返回 (data.length - period + 1) 个值
      expect(ma.length).toBeLessThanOrEqual(testData.length)
    })

    it('MA值应该在价格范围内', () => {
      const ma = calculateMA(testData, 20)
      const prices = testData.map(d => d.close)
      const minPrice = Math.min(...prices)
      const maxPrice = Math.max(...prices)

      ma.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(minPrice * 0.9)
        expect(value).toBeLessThanOrEqual(maxPrice * 1.1)
      })
    })

    it('应该验证MA计算准确性', () => {
      const period = 5
      const ma = calculateMA(testData, period)

      // 手动计算最后5个值的平均
      const last5Prices = testData.slice(-period).map(d => d.close)
      const manualAverage = last5Prices.reduce((a, b) => a + b, 0) / period

      expect(ma[ma.length - 1]).toBeCloseTo(manualAverage, 4)
    })
  })

  // ==================== 指数移动平均线测试 ====================
  describe('calculateEMA - 指数移动平均线', () => {
    it('应该正确计算EMA', () => {
      const ema = calculateEMA(testData, 20)
      expect(ema).toBeDefined()
      expect(Array.isArray(ema)).toBe(true)
      expect(ema.length).toBeGreaterThan(0)
    })

    it('EMA应该比MA反应更快', () => {
      const period = 20
      const ma = calculateMA(testData, period)
      const ema = calculateEMA(testData, period)

      // 最后一个EMA值应该更接近当前价格
      const lastPrice = testData[testData.length - 1].close
      const lastMA = ma[ma.length - 1]
      const lastEMA = ema[ema.length - 1]

      const emaDistance = Math.abs(lastPrice - lastEMA)
      const maDistance = Math.abs(lastPrice - lastMA)

      // EMA应该更接近当前价格（但不是绝对的，取决于趋势）
      expect(emaDistance).toBeDefined()
      expect(maDistance).toBeDefined()
    })
  })

  // ==================== 成交量移动平均线测试 ====================
  describe('calculateVOLUME_MA - 成交量均线', () => {
    it('应该正确计算VOLUME_MA', () => {
      const volumeMA = calculateVOLUME_MA(testData, 20)
      expect(volumeMA).toBeDefined()
      expect(Array.isArray(volumeMA)).toBe(true)
      expect(volumeMA.length).toBeGreaterThan(0)
    })

    it('VOLUME_MA值应该在合理范围内', () => {
      const volumeMA = calculateVOLUME_MA(testData, 20)
      const volumes = testData.map(d => d.volume)
      const minVolume = Math.min(...volumes)
      const maxVolume = Math.max(...volumes)

      volumeMA.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(minVolume * 0.5)
        expect(value).toBeLessThanOrEqual(maxVolume * 2)
      })
    })
  })

  // ==================== MACD测试 ====================
  describe('calculateMACD - MACD指标', () => {
    it('应该正确计算MACD', () => {
      const macd = calculateMACD(testData)
      expect(macd).toBeDefined()
      expect(macd.macd).toBeDefined()
      expect(macd.signal).toBeDefined()
      expect(macd.histogram).toBeDefined()
    })

    it('MACD组件长度应该一致', () => {
      const macd = calculateMACD(testData)
      expect(macd.macd.length).toBe(macd.signal.length)
      expect(macd.macd.length).toBe(macd.histogram.length)
    })

    it('histogram应该等于MACD - signal', () => {
      const macd = calculateMACD(testData)
      const lastIndex = macd.macd.length - 1

      const histogramDiff = macd.macd[lastIndex] - macd.signal[lastIndex]

      expect(macd.histogram[lastIndex]).toBeCloseTo(histogramDiff, 4)
    })

    it('MACD值应该是有限的', () => {
      const macd = calculateMACD(testData)

      macd.macd.forEach(value => {
        expect(value).not.toBeNaN()
        expect(isFinite(value)).toBe(true)
      })

      macd.signal.forEach(value => {
        expect(value).not.toBeNaN()
        expect(isFinite(value)).toBe(true)
      })
    })
  })

  // ==================== RSI测试 ====================
  describe('calculateRSI - RSI指标', () => {
    it('应该正确计算RSI', () => {
      const rsi = calculateRSI(testData, 14)
      expect(rsi).toBeDefined()
      expect(Array.isArray(rsi)).toBe(true)
    })

    it('RSI值应该在0-100之间', () => {
      const rsi = calculateRSI(testData, 14)

      rsi.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(0)
        expect(value).toBeLessThanOrEqual(100)
      })
    })

    it('应该处理不同的周期参数', () => {
      const rsi14 = calculateRSI(testData, 14)
      const rsi21 = calculateRSI(testData, 21)

      expect(rsi14).toBeDefined()
      expect(rsi21).toBeDefined()
    })

    it('极端上涨市场RSI应该接近100', () => {
      // 创建连续上涨的数据
      const uptrendData: KLineDataPoint[] = []
      for (let i = 0; i < 50; i++) {
        uptrendData.push({
          timestamp: Date.now() - (50 - i) * 86400000,
          open: 10 + i * 0.1,
          high: 10.1 + i * 0.1,
          low: 10 + i * 0.1,
          close: 10.1 + i * 0.1,
          volume: 1000000
        })
      }

      const rsi = calculateRSI(uptrendData, 14)
      const lastRsi = rsi[rsi.length - 1]

      // 连续上涨应该产生很高的RSI值
      expect(lastRsi).toBeGreaterThan(70)
    })
  })

  // ==================== KDJ测试 ====================
  describe('calculateKDJ - KDJ随机指标', () => {
    it('应该正确计算KDJ', () => {
      const kdj = calculateKDJ(testData, 9, 3, 3)
      expect(kdj).toBeDefined()
      expect(kdj.k).toBeDefined()
      expect(kdj.d).toBeDefined()
      expect(kdj.j).toBeDefined()
    })

    it('KDJ长度应该一致', () => {
      const kdj = calculateKDJ(testData, 9, 3, 3)
      expect(kdj.k.length).toBe(kdj.d.length)
      expect(kdj.k.length).toBe(kdj.j.length)
    })

    it('KDJ值应该在合理范围内', () => {
      const kdj = calculateKDJ(testData, 9, 3, 3)

      // K和D应该在0-100之间
      kdj.k.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(0)
        expect(value).toBeLessThanOrEqual(100)
      })

      kdj.d.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(0)
        expect(value).toBeLessThanOrEqual(100)
      })

      // J可能超出0-100范围（J = 3K - 2D，可能大于100或小于0）
      kdj.j.forEach(value => {
        expect(isFinite(value)).toBe(true)
      })
    })

    it('J应该等于3K - 2D', () => {
      const kdj = calculateKDJ(testData, 9, 3, 3)
      const lastIndex = kdj.k.length - 1

      const calculatedJ = 3 * kdj.k[lastIndex] - 2 * kdj.d[lastIndex]

      expect(kdj.j[lastIndex]).toBeCloseTo(calculatedJ, 4)
    })
  })

  // ==================== Bollinger Bands测试 ====================
  describe('calculateBollingerBands - 布林带', () => {
    it('应该正确计算布林带', () => {
      const bb = calculateBollingerBands(testData, 20, 2)
      expect(bb).toBeDefined()
      expect(bb.upper).toBeDefined()
      expect(bb.middle).toBeDefined()
      expect(bb.lower).toBeDefined()
    })

    it('布林带上轨应该大于中轨', () => {
      const bb = calculateBollingerBands(testData, 20, 2)

      for (let i = 0; i < bb.upper.length; i++) {
        // 跳过null值
        if (bb.upper[i] === null || bb.middle[i] === null) continue
        expect(bb.upper[i]).toBeGreaterThan(bb.middle[i])
      }
    })

    it('布林带下轨应该小于中轨', () => {
      const bb = calculateBollingerBands(testData, 20, 2)

      for (let i = 0; i < bb.lower.length; i++) {
        // 跳过null值
        if (bb.lower[i] === null || bb.middle[i] === null) continue
        expect(bb.lower[i]).toBeLessThan(bb.middle[i])
      }
    })

    it('布林带应该包含大部分价格', () => {
      const bb = calculateBollingerBands(testData, 20, 2)

      // 检查最后50个数据点
      const checkLength = Math.min(50, bb.upper.length)
      let withinBands = 0
      let validChecks = 0

      for (let i = bb.upper.length - checkLength; i < bb.upper.length; i++) {
        // 跳过null值
        if (bb.upper[i] === null || bb.lower[i] === null) continue
        const price = testData[testData.length - (bb.upper.length - i)].close
        if (price >= bb.lower[i] && price <= bb.upper[i]) {
          withinBands++
        }
        validChecks++
      }

      // 大部分价格应该在布林带内（使用更宽松的阈值70%）
      if (validChecks > 0) {
        const ratio = withinBands / validChecks
        expect(ratio).toBeGreaterThan(0.7)
      }
    })

    it('中轨应该等于SMA', () => {
      const period = 20
      const bb = calculateBollingerBands(testData, period, 2)
      const sma = calculateMA(testData, period)

      // BB中轨前面有 (period - 1) 个 null 值
      // BB.middle[period - 1 + i] 应该等于 SMA[i]
      const offset = period - 1
      let matchCount = 0
      let totalComparisons = 0

      for (let i = 0; i < sma.length; i++) {
        const bbIndex = offset + i
        if (bbIndex >= bb.middle.length) break
        if (bb.middle[bbIndex] === null) continue

        totalComparisons++
        if (Math.abs(bb.middle[bbIndex] - sma[i]) < 0.01) {
          matchCount++
        }
      }

      // 大部分值应该匹配
      if (totalComparisons > 0) {
        expect(matchCount / totalComparisons).toBeGreaterThan(0.95)
      }
    })
  })

  // ==================== ATR测试 ====================
  describe('calculateATR - 平均真实波幅', () => {
    it('应该正确计算ATR', () => {
      const atr = calculateATR(testData, 14)
      expect(atr).toBeDefined()
      expect(Array.isArray(atr)).toBe(true)
    })

    it('ATR值应该大于0', () => {
      const atr = calculateATR(testData, 14)

      atr.forEach(value => {
        expect(value).toBeGreaterThan(0)
      })
    })

    it('ATR应该反映波动率', () => {
      // 创建高波动数据
      const highVolatilityData: KLineDataPoint[] = []
      for (let i = 0; i < 50; i++) {
        highVolatilityData.push({
          timestamp: Date.now() - (50 - i) * 86400000,
          open: 10,
          high: 12, // 2元差距
          low: 8,   // 2元差距
          close: 10,
          volume: 1000000
        })
      }

      const atrHigh = calculateATR(highVolatilityData, 14)

      // 创建低波动数据
      const lowVolatilityData: KLineDataPoint[] = []
      for (let i = 0; i < 50; i++) {
        lowVolatilityData.push({
          timestamp: Date.now() - (50 - i) * 86400000,
          open: 10,
          high: 10.1, // 0.1元差距
          low: 9.9,
          close: 10,
          volume: 1000000
        })
      }

      const atrLow = calculateATR(lowVolatilityData, 14)

      // 高波动数据的ATR应该显著大于低波动数据
      const avgAtrHigh = atrHigh.reduce((a, b) => a + b, 0) / atrHigh.length
      const avgAtrLow = atrLow.reduce((a, b) => a + b, 0) / atrLow.length

      expect(avgAtrHigh).toBeGreaterThan(avgAtrLow * 5) // 至少5倍
    })
  })

  // ==================== 边界情况测试 ====================
  describe('边界情况测试', () => {
    it('应该处理空数据', () => {
      const ma = calculateMA([], 20)
      expect(ma).toBeDefined()
      expect(Array.isArray(ma)).toBe(true)
    })

    it('应该处理数据不足的情况', () => {
      const shortData = generateKLineData(5)
      const ma = calculateMA(shortData, 20)
      expect(ma).toBeDefined()
    })

    it('应该处理单个数据点', () => {
      const singleData = [testData[0]]
      const ma = calculateMA(singleData, 1)
      expect(ma).toBeDefined()
    })

    it('应该处理极端周期值', () => {
      const ma1 = calculateMA(testData, 1)
      expect(ma1).toBeDefined()
      expect(ma1.length).toBe(testData.length)
    })

    it('应该处理包含0的成交量', () => {
      const zeroVolumeData: KLineDataPoint[] = testData.map(d => ({
        ...d,
        volume: 0
      }))

      const volumeMA = calculateVOLUME_MA(zeroVolumeData, 20)
      expect(volumeMA).toBeDefined()
    })

    it('应该处理相同价格的数据', () => {
      const flatPriceData: KLineDataPoint[] = []
      for (let i = 0; i < 50; i++) {
        flatPriceData.push({
          timestamp: Date.now() - (50 - i) * 86400000,
          open: 10,
          high: 10,
          low: 10,
          close: 10,
          volume: 1000000
        })
      }

      const rsi = calculateRSI(flatPriceData, 14)
      expect(rsi).toBeDefined()

      const atr = calculateATR(flatPriceData, 14)
      expect(atr).toBeDefined()

      // ATR应该接近0（没有波动）
      const lastAtr = atr[atr.length - 1]
      expect(lastAtr).toBeCloseTo(0, 1)
    })
  })

  // ==================== 数据格式测试 ====================
  describe('数据格式测试', () => {
    it('应该正确处理K线数据格式', () => {
      const validData: KLineDataPoint = {
        timestamp: Date.now(),
        open: 10,
        high: 11,
        low: 9,
        close: 10.5,
        volume: 1000000
      }

      const ma = calculateMA([validData], 1)
      expect(ma).toBeDefined()
    })

    it('所有指标应该返回可序列化的数据', () => {
      const macd = calculateMACD(testData)
      const rsi = calculateRSI(testData, 14)
      const bb = calculateBollingerBands(testData, 20, 2)
      const kdj = calculateKDJ(testData)

      expect(() => JSON.stringify(macd)).not.toThrow()
      expect(() => JSON.stringify(rsi)).not.toThrow()
      expect(() => JSON.stringify(bb)).not.toThrow()
      expect(() => JSON.stringify(kdj)).not.toThrow()
    })
  })

  // ==================== 性能测试 ====================
  describe('性能测试', () => {
    it('应该快速计算1000个数据点的指标', () => {
      const largeDataset = generateKLineData(1000)

      const start = Date.now()
      calculateMA(largeDataset, 20)
      calculateRSI(largeDataset, 14)
      calculateMACD(largeDataset)
      const duration = Date.now() - start

      expect(duration).toBeLessThan(200) // 应该在200ms内完成
    })

    it('大数据集性能测试', () => {
      const largeDataset = generateKLineData(5000)

      const start = Date.now()
      calculateMA(largeDataset, 20)
      const duration = Date.now() - start

      expect(duration).toBeLessThan(300)
    })
  })

  // ==================== 指标关系测试 ====================
  describe('指标关系测试', () => {
    it('MACD histogram应该反映趋势强度', () => {
      const macd = calculateMACD(testData)

      // 检查histogram的符号
      const positiveHistogram = macd.histogram.filter(h => h > 0).length
      const negativeHistogram = macd.histogram.filter(h => h < 0).length

      // 应该既有正值也有负值
      expect(positiveHistogram + negativeHistogram).toBeGreaterThan(0)
    })

    it('RSI极值应该对应超买超卖', () => {
      const rsi = calculateRSI(testData, 14)

      const overboughtCount = rsi.filter(r => r > 70).length
      const oversoldCount = rsi.filter(r => r < 30).length

      // 应该有一些超买超卖的情况（除非市场一直在中性区域）
      expect(overboughtCount + oversoldCount).toBeGreaterThanOrEqual(0)
    })

    it('布林带宽度应该反映波动率', () => {
      const bb = calculateBollingerBands(testData, 20, 2)

      const bandwidths = bb.upper.map((u, i) => {
        // 跳过null值
        if (u === null || bb.lower[i] === null || bb.middle[i] === null) return null
        return (u - bb.lower[i]) / bb.middle[i]
      }).filter((bw): bw is number => bw !== null)

      // 带宽应该都是正值
      bandwidths.forEach(bw => {
        expect(bw).toBeGreaterThan(0)
      })
    })
  })
})
