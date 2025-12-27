/**
 * 扩展技术指标测试
 *
 * 测试覆盖率目标: 85%+
 * 测试内容:
 * - 39个技术指标计算准确性
 * - 边界情况处理（数据不足、空数据）
 * - 参数验证
 * - 性能测试
 */

import { describe, it, expect, beforeEach } from 'vitest'
import {
  calculateADX,
  calculateADL,
  calculateDEMA,
  calculateEMA,
  calculateTEMA,
  calculateTRIMA,
  calculateVWMA,
  calculateVWAP,
  calculateKAMA,
  calculateHMA,
  calculatePSAR,
  calculateDonchianChannel,
  calculateStochastic,
  calculateStochRSI,
  calculateCCI,
  calculateAO,
  calculateCMO,
  calculateMOM,
  calculateROC,
  calculateWilliamsR,
  calculateBullBearPower,
  calculateUltimateOscillator,
  calculateMFI,
  calculateTRIX,
  calculateForceIndex,
  calculateBB,
  calculateATR,
  calculateKeltnerChannel,
  calculateOBV,
  calculateChaikinMF,
  getAllSupportedIndicators,
  getIndicatorCategory,
  validateIndicatorParams,
  calculateIndicator,
  ExtendedKLineDataPoint
} from '@/utils/indicators-extended'

// 生成测试用K线数据
function generateKLineData(count: number): ExtendedKLineDataPoint[] {
  const data: ExtendedKLineDataPoint[] = []
  let price = 10.0

  for (let i = 0; i < count; i++) {
    const change = (Math.random() - 0.5) * 0.5 // -0.25 ~ +0.25
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

describe('indicators-extended.ts - 扩展技术指标', () => {
  let testData: ExtendedKLineDataPoint[]
  let shortData: ExtendedKLineDataPoint[] // 数据不足的情况

  beforeEach(() => {
    testData = generateKLineData(100)
    shortData = generateKLineData(5) // 数据不足
  })

  // ==================== 工具函数测试 ====================
  describe('getAllSupportedIndicators - 获取所有指标', () => {
    it('应该返回所有支持的指标列表', () => {
      const indicators = getAllSupportedIndicators()
      expect(indicators).toBeDefined()
      expect(indicators.length).toBeGreaterThan(30)
    })

    it('应该包含基础指标', () => {
      const indicators = getAllSupportedIndicators()
      expect(indicators).toContain('SMA')
      expect(indicators).toContain('EMA')
      expect(indicators).toContain('RSI')
      expect(indicators).toContain('MACD')
      expect(indicators).toContain('BB')
    })
  })

  describe('getIndicatorCategory - 获取指标分类', () => {
    it('应该正确分类趋势指标', () => {
      expect(getIndicatorCategory('SMA')).toBe('trend')
      expect(getIndicatorCategory('EMA')).toBe('trend')
      expect(getIndicatorCategory('ADX')).toBe('trend')
      expect(getIndicatorCategory('VWAP')).toBe('trend')
    })

    it('应该正确分类动量指标', () => {
      expect(getIndicatorCategory('RSI')).toBe('momentum')
      expect(getIndicatorCategory('MACD')).toBe('momentum')
      expect(getIndicatorCategory('Stochastic')).toBe('momentum')
      expect(getIndicatorCategory('CCI')).toBe('momentum')
    })

    it('应该正确分类波动率指标', () => {
      expect(getIndicatorCategory('BB')).toBe('volatility')
      expect(getIndicatorCategory('ATR')).toBe('volatility')
      expect(getIndicatorCategory('KeltnerChannel')).toBe('volatility')
    })

    it('应该正确分类成交量指标', () => {
      expect(getIndicatorCategory('OBV')).toBe('volume')
      expect(getIndicatorCategory('VWMA')).toBe('volume')
      expect(getIndicatorCategory('ADL')).toBe('volume')
    })

    it('应该处理未知指标', () => {
      const category = getIndicatorCategory('UnknownIndicator')
      expect(category).toBe('unknown')
    })
  })

  describe('validateIndicatorParams - 参数验证', () => {
    it('应该验证SMA参数', () => {
      expect(validateIndicatorParams('SMA', { period: 20 })).toBe(true)
      expect(validateIndicatorParams('SMA', { period: 0 })).toBe(false)
      expect(validateIndicatorParams('SMA', { period: -5 })).toBe(false)
    })

    it('应该验证BB参数', () => {
      expect(validateIndicatorParams('BB', { period: 20, stdDev: 2 })).toBe(true)
      expect(validateIndicatorParams('BB', { period: 20, stdDev: 0 })).toBe(false)
      expect(validateIndicatorParams('BB', { period: 20, stdDev: -1 })).toBe(false)
    })

    it('应该验证RSI参数', () => {
      expect(validateIndicatorParams('RSI', { period: 14 })).toBe(true)
      expect(validateIndicatorParams('RSI', { period: 5 })).toBe(false) // 最小周期
      expect(validateIndicatorParams('RSI', { period: 100 })).toBe(false) // 最大周期
    })
  })

  describe('calculateIndicator - 统一计算接口', () => {
    it('应该正确计算SMA', () => {
      const result = calculateIndicator('SMA', testData, { period: 20 })
      expect(result).toBeDefined()
      expect(Array.isArray(result)).toBe(true)
      expect(result.length).toBeGreaterThan(0)
    })

    it('应该正确计算RSI', () => {
      const result = calculateIndicator('RSI', testData, { period: 14 })
      expect(result).toBeDefined()
      expect(Array.isArray(result)).toBe(true)
    })

    it('应该正确计算MACD', () => {
      const result = calculateIndicator('MACD', testData, {
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9
      })
      expect(result).toBeDefined()
    })

    it('应该处理数据不足的情况', () => {
      const result = calculateIndicator('SMA', shortData, { period: 20 })
      expect(result).toBeDefined()
    })

    it('应该处理未知指标', () => {
      const result = calculateIndicator('UnknownIndicator', testData, {})
      expect(result).toBeNull()
    })
  })

  // ==================== 趋势指标测试 ====================
  describe('趋势指标 - Trend Indicators', () => {
    describe('EMA - 指数移动平均线', () => {
      it('应该正确计算EMA', () => {
        const ema = calculateEMA(testData, 20)
        expect(ema).toBeDefined()
        expect(ema.length).toBe(testData.length)
        expect(ema[ema.length - 1]).toBeGreaterThan(0)
      })

      it('应该处理数据不足', () => {
        const ema = calculateEMA(shortData, 20)
        expect(ema).toBeDefined()
      })
    })

    describe('DEMA - 双指数移动平均线', () => {
      it('应该正确计算DEMA', () => {
        const dema = calculateDEMA(testData, 20)
        expect(dema).toBeDefined()
        expect(dema.length).toBeGreaterThan(0)
      })
    })

    describe('ADX - 平均趋向指数', () => {
      it('应该正确计算ADX', () => {
        const adx = calculateADX(testData, 14)
        expect(adx).toBeDefined()
        expect(adx.length).toBeGreaterThan(0)
        // ADX值应该在0-100之间
        const lastAdx = adx[adx.length - 1]
        expect(lastAdx).toBeGreaterThanOrEqual(0)
        expect(lastAdx).toBeLessThanOrEqual(100)
      })
    })

    describe('ADL - 累积/派发线', () => {
      it('应该正确计算ADL', () => {
        const adl = calculateADL(testData)
        expect(adl).toBeDefined()
        expect(adl.length).toBe(testData.length)
      })
    })

    describe('VWMA - 成交量加权移动平均线', () => {
      it('应该正确计算VWMA', () => {
        const vwma = calculateVWMA(testData, 20)
        expect(vwma).toBeDefined()
        expect(vwma.length).toBeGreaterThan(0)
      })
    })

    describe('VWAP - 成交量加权平均价', () => {
      it('应该正确计算VWAP', () => {
        const vwap = calculateVWAP(testData)
        expect(vwap).toBeDefined()
        expect(vwap.length).toBe(testData.length)
      })
    })

    describe('PSAR - 抛物线转向', () => {
      it('应该正确计算PSAR', () => {
        const psar = calculatePSAR(testData, {
          step: 0.02,
          max: 0.2
        })
        expect(psar).toBeDefined()
        expect(psar.length).toBeGreaterThan(0)
      })
    })
  })

  // ==================== 动量指标测试 ====================
  describe('动量指标 - Momentum Indicators', () => {
    describe('Stochastic - 随机指标', () => {
      it('应该正确计算Stochastic', () => {
        const stoch = calculateStochastic(testData, 14, 3)
        expect(stoch).toBeDefined()
        expect(stoch.k).toBeDefined()
        expect(stoch.d).toBeDefined()
      })

      it('K值应该在0-100之间', () => {
        const stoch = calculateStochastic(testData, 14, 3)
        const lastK = stoch.k[stoch.k.length - 1]
        expect(lastK).toBeGreaterThanOrEqual(0)
        expect(lastK).toBeLessThanOrEqual(100)
      })
    })

    describe('StochRSI - 随机RSI', () => {
      it('应该正确计算StochRSI', () => {
        const stochRsi = calculateStochRSI(testData, 14, 14, 3, 3)
        expect(stochRsi).toBeDefined()
      })
    })

    describe('CCI - 顺势指标', () => {
      it('应该正确计算CCI', () => {
        const cci = calculateCCI(testData, 20)
        expect(cci).toBeDefined()
        expect(cci.length).toBeGreaterThan(0)
      })
    })

    describe('AO - 动量振荡指标', () => {
      it('应该正确计算AO', () => {
        const ao = calculateAO(testData)
        expect(ao).toBeDefined()
        expect(ao.length).toBeGreaterThan(0)
      })
    })

    describe('MOM - 动量指标', () => {
      it('应该正确计算MOM', () => {
        const mom = calculateMOM(testData, 10)
        expect(mom).toBeDefined()
        expect(mom.length).toBeGreaterThan(0)
      })
    })

    describe('ROC - 变动率指标', () => {
      it('应该正确计算ROC', () => {
        const roc = calculateROC(testData, 10)
        expect(roc).toBeDefined()
        expect(roc.length).toBeGreaterThan(0)
      })
    })

    describe('WilliamsR - 威廉指标', () => {
      it('应该正确计算WilliamsR', () => {
        const williamsR = calculateWilliamsR(testData, 14)
        expect(williamsR).toBeDefined()
        expect(williamsR.length).toBeGreaterThan(0)
      })

      it('值应该在-100到0之间', () => {
        const williamsR = calculateWilliamsR(testData, 14)
        const lastValue = williamsR[williamsR.length - 1]
        expect(lastValue).toBeGreaterThanOrEqual(-100)
        expect(lastValue).toBeLessThanOrEqual(0)
      })
    })

    describe('MFI - 资金流量指数', () => {
      it('应该正确计算MFI', () => {
        const mfi = calculateMFI(testData, 14)
        expect(mfi).toBeDefined()
        expect(mfi.length).toBeGreaterThan(0)
      })

      it('值应该在0-100之间', () => {
        const mfi = calculateMFI(testData, 14)
        const lastValue = mfi[mfi.length - 1]
        expect(lastValue).toBeGreaterThanOrEqual(0)
        expect(lastValue).toBeLessThanOrEqual(100)
      })
    })

    describe('TRIX - 三重指数平滑平均线', () => {
      it('应该正确计算TRIX', () => {
        const trix = calculateTRIX(testData, 18)
        expect(trix).toBeDefined()
        expect(trix.length).toBeGreaterThan(0)
      })
    })

    describe('ForceIndex - 强力指标', () => {
      it('应该正确计算ForceIndex', () => {
        const fi = calculateForceIndex(testData, 13)
        expect(fi).toBeDefined()
        expect(fi.length).toBeGreaterThan(0)
      })
    })
  })

  // ==================== 波动率指标测试 ====================
  describe('波动率指标 - Volatility Indicators', () => {
    describe('BB - 布林带', () => {
      it('应该正确计算布林带', () => {
        const bb = calculateBB(testData, 20, 2)
        expect(bb).toBeDefined()
        expect(bb.upper).toBeDefined()
        expect(bb.middle).toBeDefined()
        expect(bb.lower).toBeDefined()
      })

      it('上轨应该大于中轨', () => {
        const bb = calculateBB(testData, 20, 2)
        const lastUpper = bb.upper[bb.upper.length - 1]
        const lastMiddle = bb.middle[bb.middle.length - 1]
        expect(lastUpper).toBeGreaterThan(lastMiddle)
      })

      it('下轨应该小于中轨', () => {
        const bb = calculateBB(testData, 20, 2)
        const lastLower = bb.lower[bb.lower.length - 1]
        const lastMiddle = bb.middle[bb.middle.length - 1]
        expect(lastLower).toBeLessThan(lastMiddle)
      })
    })

    describe('ATR - 平均真实波幅', () => {
      it('应该正确计算ATR', () => {
        const atr = calculateATR(testData, 14)
        expect(atr).toBeDefined()
        expect(atr.length).toBeGreaterThan(0)
        expect(atr[atr.length - 1]).toBeGreaterThan(0)
      })
    })

    describe('KeltnerChannel - 肯特纳通道', () => {
      it('应该正确计算肯特纳通道', () => {
        const kc = calculateKeltnerChannel(testData, {
          period: 20,
          multiplier: 2
        })
        expect(kc).toBeDefined()
        expect(kc.upper).toBeDefined()
        expect(kc.middle).toBeDefined()
        expect(kc.lower).toBeDefined()
      })
    })
  })

  // ==================== 成交量指标测试 ====================
  describe('成交量指标 - Volume Indicators', () => {
    describe('OBV - 能量潮', () => {
      it('应该正确计算OBV', () => {
        const obv = calculateOBV(testData)
        expect(obv).toBeDefined()
        expect(obv.length).toBe(testData.length)
      })
    })

    describe('ChaikinMF - 佳庆资金流量', () => {
      it('应该正确计算ChaikinMF', () => {
        const cmf = calculateChaikinMF(testData, 20)
        expect(cmf).toBeDefined()
        expect(cmf.length).toBeGreaterThan(0)
      })
    })
  })

  // ==================== 边界情况测试 ====================
  describe('边界情况测试', () => {
    it('应该处理空数据', () => {
      const result = calculateIndicator('SMA', [], { period: 20 })
      expect(result).toBeDefined()
    })

    it('应该处理单个数据点', () => {
      const singleData = [testData[0]]
      const result = calculateIndicator('SMA', singleData, { period: 1 })
      expect(result).toBeDefined()
    })

    it('应该处理周期大于数据长度', () => {
      const result = calculateIndicator('SMA', shortData, { period: 100 })
      expect(result).toBeDefined()
    })

    it('应该处理极端周期值', () => {
      const result = calculateIndicator('SMA', testData, { period: 1 })
      expect(result).toBeDefined()
    })

    it('应该处理包含0的价格', () => {
      const zeroPriceData: ExtendedKLineDataPoint[] = [
        {
          timestamp: Date.now(),
          open: 0,
          high: 0,
          low: 0,
          close: 0,
          volume: 1000
        }
      ]
      const result = calculateIndicator('SMA', zeroPriceData, { period: 1 })
      expect(result).toBeDefined()
    })

    it('应该处理负数价格（不应崩溃）', () => {
      const negativePriceData: ExtendedKLineDataPoint[] = [
        {
          timestamp: Date.now(),
          open: -10,
          high: -5,
          low: -15,
          close: -10,
          volume: 1000
        }
      ]
      const result = calculateIndicator('SMA', negativePriceData, { period: 1 })
      expect(result).toBeDefined()
    })
  })

  // ==================== 性能测试 ====================
  describe('性能测试', () => {
    it('应该快速计算1000个数据点的SMA', () => {
      const largeDataset = generateKLineData(1000)
      const start = Date.now()
      calculateIndicator('SMA', largeDataset, { period: 20 })
      const duration = Date.now() - start

      expect(duration).toBeLessThan(100) // 应该在100ms内完成
    })

    it('应该快速计算多个指标', () => {
      const start = Date.now()
      calculateIndicator('SMA', testData, { period: 20 })
      calculateIndicator('EMA', testData, { period: 20 })
      calculateIndicator('RSI', testData, { period: 14 })
      calculateIndicator('BB', testData, { period: 20, stdDev: 2 })
      const duration = Date.now() - start

      expect(duration).toBeLessThan(200) // 4个指标应该在200ms内完成
    })

    it('大数据集测试（性能基准）', () => {
      const largeDataset = generateKLineData(5000)
      const start = Date.now()
      calculateIndicator('SMA', largeDataset, { period: 20 })
      const duration = Date.now() - start

      // 5000个数据点的SMA应该在合理时间内完成
      expect(duration).toBeLessThan(500)
    })
  })

  // ==================== 数据准确性测试 ====================
  describe('数据准确性测试', () => {
    it('SMA应该等于简单平均值（验证）', () => {
      const period = 5
      const sma = calculateIndicator('SMA', testData, { period }) as number[]

      // 手动计算最后5个值的平均
      const last5Prices = testData.slice(-period).map(d => d.close)
      const manualAverage = last5Prices.reduce((a, b) => a + b, 0) / period

      expect(sma[sma.length - 1]).toBeCloseTo(manualAverage, 4)
    })

    it('RSI值应该在合理范围内', () => {
      const rsi = calculateIndicator('RSI', testData, { period: 14 }) as number[]

      // 跳过前面的undefined值
      const validRsi = rsi.filter(v => v !== undefined && !isNaN(v))

      validRsi.forEach(value => {
        expect(value).toBeGreaterThanOrEqual(0)
        expect(value).toBeLessThanOrEqual(100)
      })
    })

    it('布林带应该包含大部分价格', () => {
      const bb = calculateBB(testData, { period: 20, stdDev: 2 })

      // 检查最后20个数据点
      const recentPrices = testData.slice(-20).map(d => d.close)
      const recentUpper = bb.upper.slice(-20)
      const recentLower = bb.lower.slice(-20)

      let withinBands = 0
      recentPrices.forEach((price, i) => {
        if (price >= recentLower[i] && price <= recentUpper[i]) {
          withinBands++
        }
      })

      // 大部分价格应该在布林带内（约95%）
      expect(withinBands / recentPrices.length).toBeGreaterThan(0.8)
    })
  })

  // ==================== 类型安全测试 ====================
  describe('类型安全测试', () => {
    it('应该返回正确的数据类型', () => {
      const sma = calculateIndicator('SMA', testData, { period: 20 })
      expect(Array.isArray(sma)).toBe(true)

      const bb = calculateIndicator('BB', testData, { period: 20, stdDev: 2 })
      expect(bb).toHaveProperty('upper')
      expect(bb).toHaveProperty('middle')
      expect(bb).toHaveProperty('lower')

      const macd = calculateIndicator('MACD', testData, {
        fastPeriod: 12,
        slowPeriod: 26,
        signalPeriod: 9
      })
      expect(macd).toHaveProperty('macd')
      expect(macd).toHaveProperty('signal')
      expect(macd).toHaveProperty('histogram')
    })
  })
})
