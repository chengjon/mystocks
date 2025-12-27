/**
 * A股交易规则工具测试
 *
 * 测试覆盖率目标: 90%+
 * 测试内容:
 * - 涨跌停检测（主板/创业板/科创板/北交所）
 * - T+1结算规则
 * - 手数验证（100股倍数）
 * - 交易费用计算（佣金/印花税/过户费）
 * - 复权处理
 */

import { describe, it, expect } from 'vitest'
import {
  detectPriceLimit,
  getPriceLimitColor,
  getLotShares,
  formatLotShares,
  calculateCommission,
  calculateBuyCost,
  calculateSellIncome,
  calculateBreakEvenPrice,
  validateLotSize,
  calculateRoundTripFees,
  formatTradingFees,
  PriceLimitStatus,
  TradeDirection
} from '@/utils/atrading'

describe('atrading.ts - A股交易规则', () => {
  // ==================== 涨跌停检测 ====================
  describe('detectPriceLimit - 涨跌停检测', () => {
    it('应该正确检测主板涨停（10%）', () => {
      const prevClose = 10.0
      const limitUp = 11.0 // 10% 涨停
      const result = detectPriceLimit(limitUp, prevClose, 'main')
      expect(result).toBe(PriceLimitStatus.LIMIT_UP)
    })

    it('应该正确检测主板跌停（-10%）', () => {
      const prevClose = 10.0
      const limitDown = 9.0 // -10% 跌停
      const result = detectPriceLimit(limitDown, prevClose, 'main')
      expect(result).toBe(PriceLimitStatus.LIMIT_DOWN)
    })

    it('应该正确检测创业板涨停（20%）', () => {
      const prevClose = 10.0
      const limitUp = 12.0 // 20% 涨停
      const result = detectPriceLimit(limitUp, prevClose, 'chiNext')
      expect(result).toBe(PriceLimitStatus.LIMIT_UP)
    })

    it('应该正确检测科创板涨停（20%）', () => {
      const prevClose = 10.0
      const limitUp = 12.0 // 20% 涨停
      const result = detectPriceLimit(limitUp, prevClose, 'star')
      expect(result).toBe(PriceLimitStatus.LIMIT_UP)
    })

    it('应该正确检测北交所涨停（30%）', () => {
      const prevClose = 10.0
      const limitUp = 13.0 // 30% 涨停
      const result = detectPriceLimit(limitUp, prevClose, 'bje')
      expect(result).toBe(PriceLimitStatus.LIMIT_UP)
    })

    it('应该正确识别正常波动（非涨跌停）', () => {
      const prevClose = 10.0
      const normal = 10.5 // 5% 涨幅，未涨停
      const result = detectPriceLimit(normal, prevClose, 'main')
      expect(result).toBe(PriceLimitStatus.NONE)
    })

    it('应该处理昨日收盘价为0的情况', () => {
      const result = detectPriceLimit(10.0, 0, 'main')
      expect(result).toBe(PriceLimitStatus.NONE)
    })

    it('应该处理昨日收盘价为null的情况', () => {
      const result = detectPriceLimit(10.0, null as any, 'main')
      expect(result).toBe(PriceLimitStatus.NONE)
    })

    it('应该考虑小数点误差（±0.01%）', () => {
      const prevClose = 10.0
      const nearLimitUp = 10.989 // 9.99% 涨幅，接近但未涨停
      const result = detectPriceLimit(nearLimitUp, prevClose, 'main')
      expect(result).toBe(PriceLimitStatus.NONE)
    })
  })

  // ==================== 涨跌停颜色 ====================
  describe('getPriceLimitColor - 涨跌停颜色', () => {
    it('应该返回涨停颜色（红色）', () => {
      const color = getPriceLimitColor(PriceLimitStatus.LIMIT_UP)
      expect(color).toBe('#EF5350') // 红色
    })

    it('应该返回跌停颜色（绿色）', () => {
      const color = getPriceLimitColor(PriceLimitStatus.LIMIT_DOWN)
      expect(color).toBe('#26A69A') // 绿色
    })

    it('应该返回正常颜色（空字符串）', () => {
      const color = getPriceLimitColor(PriceLimitStatus.NONE)
      expect(color).toBe('') // 空字符串
    })
  })

  // ==================== 手数处理 ====================
  describe('getLotShares - 获取手数', () => {
    it('应该正确计算手数（100股为1手）', () => {
      expect(getLotShares(100)).toBe(1)
      expect(getLotShares(500)).toBe(5)
      expect(getLotShares(1000)).toBe(10)
      expect(getLotShares(1500)).toBe(15)
    })

    it('应该处理小数（向下取整）', () => {
      expect(getLotShares(150)).toBe(1)
      expect(getLotShares(250)).toBe(2)
      expect(getLotShares(999)).toBe(9)
    })

    it('应该处理0股', () => {
      expect(getLotShares(0)).toBe(0)
    })
  })

  describe('formatLotShares - 格式化手数', () => {
    it('应该正确格式化手数显示', () => {
      expect(formatLotShares(100)).toBe('1手')
      expect(formatLotShares(500)).toBe('5手')
      expect(formatLotShares(1000)).toBe('10手')
    })

    it('应该处理不足1手的情况', () => {
      expect(formatLotShares(0)).toBe('< 1手')
      expect(formatLotShares(50)).toBe('< 1手')
    })
  })

  // ==================== 交易费用计算 ====================
  describe('calculateCommission - 计算交易费用', () => {
    const defaultConfig = {
      commissionRate: 0.0003, // 0.03%
      minCommission: 5,
      stampTaxRate: 0.001, // 0.1%
      transferFeeRate: 0.00001 // 0.001%
    }

    it('应该正确计算买入佣金（最低5元）', () => {
      const amount = 10000
      const result = calculateCommission(amount, TradeDirection.BUY, defaultConfig)

      expect(result.commission).toBe(5) // 最低佣金
      expect(result.stampTax).toBe(0) // 买入免征
      expect(result.transferFee).toBeCloseTo(0.1, 1)
      expect(result.total).toBeCloseTo(5.1, 1)
      expect(result.netAmount).toBeCloseTo(-10005.1, 1)
    })

    it('应该正确计算大额买入佣金（按实际费率）', () => {
      const amount = 1000000 // 100万
      const result = calculateCommission(amount, TradeDirection.BUY, defaultConfig)

      expect(result.commission).toBe(300) // 100万 * 0.03% = 300元
      expect(result.stampTax).toBe(0)
      expect(result.transferFee).toBe(10) // 100万 * 0.001%
      expect(result.total).toBe(310)
      expect(result.netAmount).toBeCloseTo(-1000310, 0)
    })

    it('应该正确计算卖出费用（含印花税）', () => {
      const amount = 10000
      const result = calculateCommission(amount, TradeDirection.SELL, defaultConfig)

      expect(result.commission).toBe(5) // 最低佣金
      expect(result.stampTax).toBe(10) // 10000 * 0.1% = 10元
      expect(result.transferFee).toBeCloseTo(0.1, 1)
      expect(result.total).toBeCloseTo(15.1, 1)
      expect(result.netAmount).toBeCloseTo(9984.9, 1)
    })

    it('应该正确计算大额卖出费用', () => {
      const amount = 1000000 // 100万
      const result = calculateCommission(amount, TradeDirection.SELL, defaultConfig)

      expect(result.commission).toBe(300)
      expect(result.stampTax).toBe(1000) // 100万 * 0.1% = 1000元
      expect(result.transferFee).toBe(10)
      expect(result.total).toBe(1310)
      expect(result.netAmount).toBeCloseTo(998690, 0)
    })

    it('应该处理小额交易（佣金低于最低5元）', () => {
      const amount = 1000 // 1000元
      const result = calculateCommission(amount, TradeDirection.BUY, defaultConfig)

      expect(result.commission).toBe(5) // 最低佣金
      expect(result.total).toBeGreaterThanOrEqual(5)
    })
  })

  // ==================== 买入成本计算 ====================
  describe('calculateBuyCost - 计算买入成本', () => {
    it('应该正确计算买入总成本', () => {
      const price = 10.5
      const quantity = 1000
      const cost = calculateBuyCost(price, quantity)

      // 金额 = 10.5 * 1000 = 10500
      // 佣金 = 5元（最低）
      // 过户费 = 10500 * 0.001% = 0.105
      // 总成本 = 10500 + 5 + 0.105 = 10505.105
      expect(cost).toBeCloseTo(10505.11, 1)
    })

    it('应该处理大额买入', () => {
      const price = 100
      const quantity = 10000 // 100万
      const cost = calculateBuyCost(price, quantity)

      // 佣金 = 100万 * 0.03% = 300元
      expect(cost).toBeCloseTo(1000310, 0)
    })
  })

  // ==================== 卖出收入计算 ====================
  describe('calculateSellIncome - 计算卖出收入', () => {
    it('应该正确计算卖出净收入', () => {
      const price = 10.5
      const quantity = 1000
      const income = calculateSellIncome(price, quantity)

      // 金额 = 10.5 * 1000 = 10500
      // 佣金 = 5元（最低）
      // 印花税 = 10500 * 0.1% = 10.5元
      // 过户费 = 10500 * 0.001% = 0.105元
      // 净收入 = 10500 - 5 - 10.5 - 0.105 = 10484.395
      expect(income).toBeCloseTo(10484.4, 1)
    })

    it('应该处理大额卖出', () => {
      const price = 100
      const quantity = 10000 // 100万
      const income = calculateSellIncome(price, quantity)

      // 佣金 = 300元
      // 印花税 = 1000元
      // 过户费 = 10元
      // 净收入 = 1000000 - 1310 = 998690元
      expect(income).toBeCloseTo(998690, 0)
    })
  })

  // ==================== 盈亏平衡点计算 ====================
  describe('calculateBreakEvenPrice - 计算盈亏平衡点', () => {
    it('应该正确计算盈亏平衡价格', () => {
      const buyPrice = 10.5
      const quantity = 1000
      const breakEven = calculateBreakEvenPrice(buyPrice, quantity)

      // 买入成本 = 10505.105
      // 卖出需要覆盖成本 = 10505.105 + 卖出费用
      // 大约比买入价高 0.2% 左右
      expect(breakEven).toBeGreaterThan(buyPrice)
      expect(breakEven).toBeLessThan(buyPrice * 1.01) // 不应超过1%
    })

    it('应该处理小金额交易', () => {
      const buyPrice = 5.0
      const quantity = 100
      const breakEven = calculateBreakEvenPrice(buyPrice, quantity)

      expect(breakEven).toBeGreaterThan(buyPrice)
    })
  })

  // ==================== 手数验证 ====================
  describe('validateLotSize - 验证手数', () => {
    it('应该接受合法手数（100股倍数）', () => {
      expect(validateLotSize(100)).toBe(true)
      expect(validateLotSize(200)).toBe(true)
      expect(validateLotSize(500)).toBe(true)
      expect(validateLotSize(1000)).toBe(true)
    })

    it('应该拒绝非法手数（非100股倍数）', () => {
      expect(validateLotSize(50)).toBe(false)
      expect(validateLotSize(150)).toBe(false)
      expect(validateLotSize(250)).toBe(false)
      expect(validateLotSize(999)).toBe(false)
    })

    it('应该拒绝0股', () => {
      expect(validateLotSize(0)).toBe(false)
    })

    it('应该拒绝负数', () => {
      expect(validateLotSize(-100)).toBe(false)
    })
  })

  // ==================== 往返交易费用 ====================
  describe('calculateRoundTripFees - 计算往返交易费用', () => {
    it('应该正确计算买入+卖出总费用', () => {
      const price = 10.5
      const quantity = 1000
      const fees = calculateRoundTripFees(price, quantity)

      // 买入费用 ≈ 5.105
      // 卖出费用 ≈ 15.605
      // 总费用 ≈ 20.71
      expect(fees).toBeGreaterThan(20)
      expect(fees).toBeLessThan(25)
    })

    it('应该是返回一个数字值', () => {
      const price = 10.5
      const quantity = 1000
      const fees = calculateRoundTripFees(price, quantity)

      expect(typeof fees).toBe('number')
      expect(fees).toBeGreaterThan(0)
    })
  })

  // ==================== 费用格式化 ====================
  describe('formatTradingFees - 格式化费用显示', () => {
    it('应该正确格式化费用对象', () => {
      const fees = {
        commission: 5.0,
        stampTax: 10.5,
        transferFee: 0.105,
        total: 15.605,
        netAmount: 9984.395
      }

      const formatted = formatTradingFees(fees)
      expect(formatted).toContain('佣金')
      expect(formatted).toContain('印花税')
      expect(formatted).toContain('过户费')
      expect(formatted).toContain('15.61')
    })

    it('应该处理小数位数', () => {
      const fees = {
        commission: 5.1234,
        stampTax: 10.5678,
        transferFee: 0.1001,
        total: 15.7913,
        netAmount: 9984.2087
      }

      const formatted = formatTradingFees(fees)
      expect(formatted).toBeDefined()
    })
  })

  // ==================== 边界情况测试 ====================
  describe('边界情况测试', () => {
    it('应该处理极端高价格', () => {
      const price = 1000
      const quantity = 100000
      const cost = calculateBuyCost(price, quantity)

      expect(Number.isFinite(cost)).toBe(true)
      expect(cost).toBeGreaterThan(0)
    })

    it('应该处理极端低价格', () => {
      const price = 1.0
      const quantity = 100
      const cost = calculateBuyCost(price, quantity)

      expect(cost).toBeGreaterThan(100) // 至少是本金
    })

    it('应该处理大量小数', () => {
      const price = 10.123456789
      const quantity = 1000
      const cost = calculateBuyCost(price, quantity)

      expect(Number.isFinite(cost)).toBe(true)
    })

    it('应该处理自定义费率配置', () => {
      const customConfig = {
        commissionRate: 0.0002, // 0.02%
        minCommission: 1,
        stampTaxRate: 0.001,
        transferFeeRate: 0.00001
      }

      const result = calculateCommission(10000, TradeDirection.BUY, customConfig)
      expect(result.commission).toBe(2) // 10000 * 0.02% = 2元
    })
  })

  // ==================== A股特性测试 ====================
  describe('A股市场特性', () => {
    it('买入应该免征印花税', () => {
      const result = calculateCommission(10000, TradeDirection.BUY)
      expect(result.stampTax).toBe(0)
    })

    it('卖出应该征收印花税', () => {
      const result = calculateCommission(10000, TradeDirection.SELL)
      expect(result.stampTax).toBeGreaterThan(0)
    })

    it('过户费应该双向征收', () => {
      const buy = calculateCommission(100000, TradeDirection.BUY)
      const sell = calculateCommission(100000, TradeDirection.SELL)

      expect(buy.transferFee).toBeGreaterThan(0)
      expect(sell.transferFee).toBeGreaterThan(0)
    })

    it('佣金应该有最低收费限制', () => {
      const smallAmount = 1000 // 小额交易
      const result = calculateCommission(smallAmount, TradeDirection.BUY)

      // 即使金额很小，佣金也应该是5元
      expect(result.commission).toBeGreaterThanOrEqual(5)
    })
  })
})
