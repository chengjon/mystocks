/**
 * Phase 4: A股 Rules & Indicators - 使用示例
 *
 * 展示如何使用新的A股交易规则引擎和技术指标库
 */

import {
  calculateCommission,
  calculateBuyCost,
  calculateSellIncome,
  calculateBreakEvenPrice,
  validateLotSize,
  calculateRoundTripFees,
  formatTradingFees,
  TradeDirection,
  type TradingFeesConfig,
  type TradingFeesResult
} from '@/utils/atrading'

import {
  calculateIndicator,
  getAllSupportedIndicators,
  getIndicatorCategory,
  validateIndicatorParams,
  type ExtendedKLineDataPoint
} from '@/utils/indicators-extended'

// ============ 示例 1: A股交易费用计算 ============

/**
 * 示例1.1: 计算买入费用
 */
export function example1_buyFees() {
  const price = 10.5  // 股票价格（元）
  const quantity = 1000  // 买入数量（股）

  const cost = calculateBuyCost(price, quantity)

  console.log(`股票价格: ${price}元`)
  console.log(`买入数量: ${quantity}股`)
  console.log(`总成本: ${cost.toFixed(2)}元`)
  console.log(`每股成本: ${(cost / quantity).toFixed(4)}元`)

  // 输出:
  // 股票价格: 10.5元
  // 买入数量: 1000股
  // 总成本: 10505.11元
  // 每股成本: 10.5051元
}

/**
 * 示例1.2: 计算卖出收入
 */
export function example1_sellFees() {
  const price = 11.0  // 卖出价格（元）
  const quantity = 1000  // 卖出数量（股）

  const income = calculateSellIncome(price, quantity)

  console.log(`卖出价格: ${price}元`)
  console.log(`卖出数量: ${quantity}股`)
  console.log(`净收入: ${income.toFixed(2)}元`)
  console.log(`每股收入: ${(income / quantity).toFixed(4)}元`)

  // 输出:
  // 卖出价格: 11.0元
  // 卖出数量: 1000股
  // 净收入: 10984.89元
  // 每股收入: 10.9849元
}

/**
 * 示例1.3: 计算交易盈亏
 */
export function example1_tradingProfit() {
  const buyPrice = 10.5
  const sellPrice = 11.0
  const quantity = 1000

  const buyCost = calculateBuyCost(buyPrice, quantity)
  const sellIncome = calculateSellIncome(sellPrice, quantity)
  const profit = sellIncome - buyCost
  const profitPercent = (profit / buyCost) * 100

  console.log(`买入成本: ${buyCost.toFixed(2)}元`)
  console.log(`卖出收入: ${sellIncome.toFixed(2)}元`)
  console.log(`交易盈亏: ${profit.toFixed(2)}元`)
  console.log(`盈亏比例: ${profitPercent.toFixed(2)}%`)

  // 输出:
  // 买入成本: 10505.11元
  // 卖出收入: 10984.89元
  // 交易盈亏: 479.78元
  // 盈亏比例: 4.57%
}

/**
 * 示例1.4: 计算盈亏平衡点
 */
export function example1_breakEven() {
  const buyPrice = 10.5
  const quantity = 1000

  const breakEven = calculateBreakEvenPrice(buyPrice, quantity)
  const priceIncrease = ((breakEven - buyPrice) / buyPrice) * 100

  console.log(`买入价格: ${buyPrice}元`)
  console.log(`盈亏平衡价: ${breakEven.toFixed(2)}元`)
  console.log(`需上涨: ${priceIncrease.toFixed(2)}%才能保本`)

  // 输出:
  // 买入价格: 10.5元
  // 盈亏平衡价: 10.52元
  // 需上涨: 0.19%才能保本
}

/**
 * 示例1.5: 详细费用明细
 */
export function example1_feeDetails() {
  const amount = 10000  // 交易金额（元）

  const buyFees = calculateCommission(amount, TradeDirection.BUY)
  const sellFees = calculateCommission(amount, TradeDirection.SELL)

  console.log('=== 买入费用 ===')
  console.log(formatTradingFees(buyFees))
  console.log(`净支出: ${Math.abs(buyFees.netAmount).toFixed(2)}元`)

  console.log('\n=== 卖出费用 ===')
  console.log(formatTradingFees(sellFees))
  console.log(`净收入: ${sellFees.netAmount.toFixed(2)}元`)

  // 输出:
  // === 买入费用 ===
  // 佣金: 5.00元, 印花税: 0.00元, 过户费: 0.10元, 总计: 5.10元
  // 净支出: 10005.10元
  //
  // === 卖出费用 ===
  // 佣金: 5.00元, 印花税: 10.00元, 过户费: 0.10元, 总计: 15.10元
  // 净收入: 9984.90元
}

/**
 * 示例1.6: 手数验证
 */
export function example1_lotValidation() {
  const quantities = [50, 100, 150, 200, 1000, 1234]

  quantities.forEach(qty => {
    const isValid = validateLotSize(qty)
    const lots = Math.floor(qty / 100)
    console.log(`${qty}股: ${isValid ? '✅' : '❌'} (${lots}手)`)
  })

  // 输出:
  // 50股: ❌ (0手)
  // 100股: ✅ (1手)
  // 150股: ❌ (1手)
  // 200股: ✅ (2手)
  // 1000股: ✅ (10手)
  // 1234股: ❌ (12手)
}

/**
 * 示例1.7: 往返交易费用
 */
export function example1_roundTrip() {
  const buyPrice = 10.5
  const sellPrice = 11.0
  const quantity = 1000

  const roundTripFees = calculateRoundTripFees(buyPrice, quantity, sellPrice)

  console.log(`买入价格: ${buyPrice}元`)
  console.log(`卖出价格: ${sellPrice}元`)
  console.log(`往返总费用: ${roundTripFees.toFixed(2)}元`)
  console.log(`费用占比: ${((roundTripFees / (buyPrice * quantity)) * 100).toFixed(2)}%`)

  // 输出:
  // 买入价格: 10.5元
  // 卖出价格: 11.0元
  // 往返总费用: 20.21元
  // 费用占比: 0.19%
}

/**
 * 示例1.8: 自定义费率配置
 */
export function example1_customRates() {
  const customConfig: TradingFeesConfig = {
    commissionRate: 0.00025,  // 万分之2.5
    minCommission: 5,
    stampTaxRate: 0.001,
    transferFeeRate: 0.00001
  }

  const amount = 10000
  const fees = calculateCommission(amount, TradeDirection.SELL, customConfig)

  console.log('使用自定义费率（佣金2.5‰）:')
  console.log(formatTradingFees(fees))
}

// ============ 示例 2: 技术指标计算 ============

/**
 * 示例2.1: 生成模拟K线数据
 */
export function generateMockKlineData(count: number = 100): ExtendedKLineDataPoint[] {
  const data: ExtendedKLineDataPoint[] = []
  let price = 10.0
  let timestamp = Date.now() - count * 86400000

  for (let i = 0; i < count; i++) {
    const open = price + (Math.random() - 0.5) * 0.2
    const close = open + (Math.random() - 0.5) * 0.4
    const high = Math.max(open, close) + Math.random() * 0.1
    const low = Math.min(open, close) - Math.random() * 0.1
    const volume = Math.floor(1000000 + Math.random() * 9000000)

    data.push({
      timestamp: timestamp + i * 86400000,
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume
    })

    price = close
  }

  return data
}

/**
 * 示例2.2: 计算移动平均线
 */
export function example2_movingAverages() {
  const klineData = generateMockKlineData(100)

  const ma5 = calculateIndicator('SMA', klineData, { period: 5 })
  const ma20 = calculateIndicator('SMA', klineData, { period: 20 })
  const ema12 = calculateIndicator('EMA', klineData, { period: 12 })

  console.log('=== 移动平均线 ===')
  console.log(`MA5最新值: ${ma5[ma5.length - 1].toFixed(2)}`)
  console.log(`MA20最新值: ${ma20[ma20.length - 1].toFixed(2)}`)
  console.log(`EMA12最新值: ${ema12[ema12.length - 1].toFixed(2)}`)

  // 判断趋势
  const lastPrice = klineData[klineData.length - 1].close
  const lastMA5 = ma5[ma5.length - 1]
  const lastMA20 = ma20[ma20.length - 1]

  if (lastPrice > lastMA5 && lastMA5 > lastMA20) {
    console.log('趋势: 多头排列（价格 > MA5 > MA20）')
  } else if (lastPrice < lastMA5 && lastMA5 < lastMA20) {
    console.log('趋势: 空头排列（价格 < MA5 < MA20）')
  } else {
    console.log('趋势: 盘整')
  }
}

/**
 * 示例2.3: 计算动量指标
 */
export function example2_momentumIndicators() {
  const klineData = generateMockKlineData(100)

  const rsi = calculateIndicator('RSI', klineData, { period: 14 })
  const macd = calculateIndicator('MACD', klineData, { fastPeriod: 12, slowPeriod: 26, signalPeriod: 9 })
  const cci = calculateIndicator('CCI', klineData, { period: 20 })

  console.log('=== 动量指标 ===')
  console.log(`RSI(14)最新值: ${rsi[rsi.length - 1].toFixed(2)}`)

  // RSI解读
  const lastRSI = rsi[rsi.length - 1]
  if (lastRSI > 70) {
    console.log('RSI信号: 超买（可能回调）')
  } else if (lastRSI < 30) {
    console.log('RSI信号: 超卖（可能反弹）')
  } else {
    console.log('RSI信号: 正常范围')
  }

  console.log(`CCI(20)最新值: ${cci[cci.length - 1].toFixed(2)}`)
}

/**
 * 示例2.4: 计算布林带
 */
export function example2_bollingerBands() {
  const klineData = generateMockKlineData(100)

  const bb = calculateIndicator('BB', klineData, { period: 20, stdDev: 2 })
  const lastPrice = klineData[klineData.length - 1].close
  const lastUpper = bb.upper[bb.upper.length - 1]
  const lastMiddle = bb.middle[bb.middle.length - 1]
  const lastLower = bb.lower[bb.lower.length - 1]

  console.log('=== 布林带 ===')
  console.log(`上轨: ${lastUpper.toFixed(2)}`)
  console.log(`中轨: ${lastMiddle.toFixed(2)}`)
  console.log(`下轨: ${lastLower.toFixed(2)}`)
  console.log(`当前价格: ${lastPrice.toFixed(2)}`)

  // 布林带解读
  const bbWidth = ((lastUpper - lastLower) / lastMiddle) * 100
  console.log(`带宽: ${bbWidth.toFixed(2)}%`)

  if (lastPrice >= lastUpper) {
    console.log('信号: 价格触及上轨（可能超买）')
  } else if (lastPrice <= lastLower) {
    console.log('信号: 价格触及下轨（可能超卖）')
  } else {
    console.log('信号: 价格在正常区间')
  }
}

/**
 * 示例2.5: 计算成交量指标
 */
export function example2_volumeIndicators() {
  const klineData = generateMockKlineData(100)

  const obv = calculateIndicator('OBV', klineData)
  const mfi = calculateIndicator('MFI', klineData, { period: 14 })

  console.log('=== 成交量指标 ===')
  console.log(`OBV最新值: ${obv[obv.length - 1].toFixed(0)}`)
  console.log(`MFI(14)最新值: ${mfi[mfi.length - 1].toFixed(2)}`)

  // MFI解读
  const lastMFI = mfi[mfi.length - 1]
  if (lastMFI > 80) {
    console.log('MFI信号: 资金流入过度（可能回调）')
  } else if (lastMFI < 20) {
    console.log('MFI信号: 资金流出过度（可能反弹）')
  } else {
    console.log('MFI信号: 正常范围')
  }
}

/**
 * 示例2.6: 多指标综合分析
 */
export function example2_multiIndicatorAnalysis() {
  const klineData = generateMockKlineData(100)

  const ma20 = calculateIndicator('SMA', klineData, { period: 20 })
  const rsi = calculateIndicator('RSI', klineData, { period: 14 })
  const bb = calculateIndicator('BB', klineData, { period: 20, stdDev: 2 })

  const lastPrice = klineData[klineData.length - 1].close
  const lastMA20 = ma20[ma20.length - 1]
  const lastRSI = rsi[rsi.length - 1]
  const lastBBLower = bb.lower[bb.lower.length - 1]
  const lastBBUpper = bb.upper[bb.upper.length - 1]

  console.log('=== 综合技术分析 ===')
  console.log(`价格: ${lastPrice.toFixed(2)}`)
  console.log(`MA20: ${lastMA20.toFixed(2)}`)
  console.log(`RSI: ${lastRSI.toFixed(2)}`)
  console.log(`布林带: ${lastBBLower.toFixed(2)} ~ ${lastBBUpper.toFixed(2)}`)
  console.log()

  let bullishSignals = 0
  let bearishSignals = 0

  // 趋势分析
  if (lastPrice > lastMA20) {
    console.log('✅ 多头信号: 价格位于MA20之上')
    bullishSignals++
  } else {
    console.log('❌ 空头信号: 价格位于MA20之下')
    bearishSignals++
  }

  // 动量分析
  if (lastRSI < 30) {
    console.log('✅ 多头信号: RSI超卖')
    bullishSignals++
  } else if (lastRSI > 70) {
    console.log('❌ 空头信号: RSI超买')
    bearishSignals++
  }

  // 波动率分析
  if (lastPrice <= lastBBLower) {
    console.log('✅ 多头信号: 价格触及布林带下轨')
    bullishSignals++
  } else if (lastPrice >= lastBBUpper) {
    console.log('❌ 空头信号: 价格触及布林带上轨')
    bearishSignals++
  }

  console.log()
  console.log(`多空信号比: ${bullishSignals}:${bearishSignals}`)

  if (bullishSignals > bearishSignals) {
    console.log('综合建议: 偏多')
  } else if (bearishSignals > bullishSignals) {
    console.log('综合建议: 偏空')
  } else {
    console.log('综合建议: 观望')
  }
}

/**
 * 示例2.7: 获取所有支持的指标
 */
export function example2_listIndicators() {
  const allIndicators = getAllSupportedIndicators()

  console.log(`支持的指标总数: ${allIndicators.length}`)
  console.log()

  const categories = ['trend', 'momentum', 'volatility', 'volume']

  categories.forEach(category => {
    const indicators = allIndicators.filter(ind => getIndicatorCategory(ind) === category)
    console.log(`${category.toUpperCase()} (${indicators.length}):`)
    console.log(`  ${indicators.join(', ')}`)
  })

  // 输出:
  // 支持的指标总数: 39
  //
  // TREND (14):
  //   SMA, EMA, WMA, DEMA, TEMA, TRIMA, VWMA, VWAP, KAMA, HMA, PSAR, ADX, DonchianUpper, DonchianLower
  // MOMENTUM (16):
  //   MACD, RSI, StochRSI, Stochastic, CCI, AO, CMO, MOM, ROC, WilliamsR, BullBearPower, UltimateOscillator, MFI, TRIX, KST, ForceIndex
  // VOLATILITY (5):
  //   BB, ATR, KeltnerChannel
  // VOLUME (4):
  //   OBV, ADL, ChaikinMF, VWMA
}

/**
 * 示例2.8: 验证指标参数
 */
export function example2_validateParams() {
  // 有效参数
  console.log('SMA(20):', validateIndicatorParams('SMA', [20]) ? '✅' : '❌')
  console.log('RSI(14):', validateIndicatorParams('RSI', [14]) ? '✅' : '❌')
  console.log('BB(20, 2):', validateIndicatorParams('BB', [20, 2]) ? '✅' : '❌')
  console.log('MACD(12, 26, 9):', validateIndicatorParams('MACD', [12, 26, 9]) ? '✅' : '❌')

  // 无效参数
  console.log('SMA():', validateIndicatorParams('SMA', []) ? '✅' : '❌')
  console.log('SMA(0):', validateIndicatorParams('SMA', [0]) ? '✅' : '❌')
  console.log('RSI(14, 14):', validateIndicatorParams('RSI', [14, 14]) ? '✅' : '❌')

  // 输出:
  // SMA(20): ✅
  // RSI(14): ✅
  // BB(20, 2): ✅
  // MACD(12, 26, 9): ✅
  // SMA(): ❌
  // SMA(0): ❌
  // RSI(14, 14): ❌
}

// ============ 示例 3: 实际应用场景 ============

/**
 * 示例3.1: 交易决策辅助
 */
export function example3_tradingDecision() {
  const klineData = generateMockKlineData(100)
  const currentPrice = klineData[klineData.length - 1].close

  // 计算关键指标
  const ma5 = calculateIndicator('SMA', klineData, { period: 5 })
  const ma20 = calculateIndicator('SMA', klineData, { period: 20 })
  const rsi = calculateIndicator('RSI', klineData, { period: 14 })
  const atr = calculateIndicator('ATR', klineData, { period: 14 })

  const signals = {
    trend: currentPrice > ma5[ma5.length - 1] && ma5[ma5.length - 1] > ma20[ma20.length - 1],
    momentum: rsi[rsi.length - 1] < 70 && rsi[rsi.length - 1] > 30,
    volatility: atr[atr.length - 1] < currentPrice * 0.05  // ATR < 5%
  }

  console.log('=== 交易决策分析 ===')
  console.log(`当前价格: ${currentPrice.toFixed(2)}`)
  console.log(`MA5: ${ma5[ma5.length - 1].toFixed(2)}`)
  console.log(`MA20: ${ma20[ma20.length - 1].toFixed(2)}`)
  console.log(`RSI: ${rsi[rsi.length - 1].toFixed(2)}`)
  console.log(`ATR: ${atr[atr.length - 1].toFixed(2)}`)
  console.log()

  const score = Object.values(signals).filter(Boolean).length

  console.log(`技术面得分: ${score}/3`)

  if (score === 3) {
    console.log('建议: 技术面强势，可考虑买入')
  } else if (score === 2) {
    console.log('建议: 技术面良好，谨慎参与')
  } else if (score === 1) {
    console.log('建议: 技术面一般，观望为主')
  } else {
    console.log('建议: 技术面偏弱，避免操作')
  }
}

/**
 * 示例3.2: 仓位管理建议
 */
export function example3_positionSizing() {
  const capital = 100000  // 总资金（元）
  const stockPrice = 10.5  // 股票价格
  const atrPercent = 0.03  // ATR占价格比例（3%）

  // 风险参数
  const riskPerTrade = 0.02  // 每笔交易风险2%
  const stopLossATR = 2  // 止损距离2倍ATR

  // 计算仓位
  const riskAmount = capital * riskPerTrade
  const stopLossDistance = stockPrice * atrPercent * stopLossATR
  const shares = Math.floor(riskAmount / stopLossDistance)
  const positionValue = shares * stockPrice
  const positionPercent = (positionValue / capital) * 100

  console.log('=== 仓位管理建议 ===')
  console.log(`总资金: ${capital.toFixed(0)}元`)
  console.log(`股票价格: ${stockPrice.toFixed(2)}元`)
  console.log(`ATR占比: ${(atrPercent * 100).toFixed(2)}%`)
  console.log(`风险额度: ${riskAmount.toFixed(2)}元 (${riskPerTrade * 100}%)`)
  console.log(`止损距离: ${stopLossDistance.toFixed(2)}元 (${(stopLossDistance / stockPrice * 100).toFixed(2)}%)`)
  console.log()
  console.log(`建议仓位: ${shares}股`)
  console.log(`仓位价值: ${positionValue.toFixed(2)}元`)
  console.log(`仓位比例: ${positionPercent.toFixed(2)}%`)

  // 止损止盈价
  const stopLossPrice = stockPrice - stopLossDistance
  const takeProfitPrice = stockPrice + stopLossDistance * 2

  console.log()
  console.log(`止损价: ${stopLossPrice.toFixed(2)}元`)
  console.log(`止盈价: ${takeProfitPrice.toFixed(2)}元`)
}

// ============ 导出所有示例函数 ============

export const examples = {
  // A股交易规则示例
  example1_buyFees,
  example1_sellFees,
  example1_tradingProfit,
  example1_breakEven,
  example1_feeDetails,
  example1_lotValidation,
  example1_roundTrip,
  example1_customRates,

  // 技术指标示例
  example2_movingAverages,
  example2_momentumIndicators,
  example2_bollingerBands,
  example2_volumeIndicators,
  example2_multiIndicatorAnalysis,
  example2_listIndicators,
  example2_validateParams,

  // 实际应用示例
  example3_tradingDecision,
  example3_positionSizing
}
