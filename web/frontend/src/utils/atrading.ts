/**
 * A股市场特性工具
 *
 * 提供A股特有的交易规则和市场特性支持
 */

/**
 * 涨跌停状态枚举
 */
export enum PriceLimitStatus {
  NONE = 'none',
  LIMIT_UP = 'limit_up',      // 涨停
  LIMIT_DOWN = 'limit_down'   // 跌停
}

/**
 * 交易方向枚举
 */
export enum TradeDirection {
  BUY = 'buy',
  SELL = 'sell'
}

/**
 * A股交易费率配置接口
 */
export interface TradingFeesConfig {
  /** 佣金费率（默认 0.03%） */
  commissionRate?: number
  /** 佣金最低收费（默认 5元） */
  minCommission?: number
  /** 印花税率（默认 0.1%，仅卖出） */
  stampTaxRate?: number
  /** 过户费率（默认 0.001%，双向） */
  transferFeeRate?: number
}

/**
 * 交易费用计算结果接口
 */
export interface TradingFeesResult {
  /** 佣金 */
  commission: number
  /** 印花税 */
  stampTax: number
  /** 过户费 */
  transferFee: number
  /** 总费用 */
  total: number
  /** 净额（买入为负，卖出为正） */
  netAmount: number
}

/**
 * 检测涨跌停
 * 主板：10%涨跌停
 * 科创板/创业板：20%涨跌停
 * 北交所：30%涨跌停
 */
export function detectPriceLimit(
  current: number,
  prevClose: number,
  boardType: 'main' | 'chiNext' | 'star' | 'bje' = 'main'
): PriceLimitStatus {
  if (!prevClose || prevClose === 0) {
    return PriceLimitStatus.NONE
  }

  const changePercent = ((current - prevClose) / prevClose) * 100

  let limitPercent: number
  switch (boardType) {
    case 'main':
      limitPercent = 10
      break
    case 'chiNext':
    case 'star':
      limitPercent = 20
      break
    case 'bje':
      limitPercent = 30
      break
    default:
      limitPercent = 10
  }

  // 考虑小数点误差（±0.01%）
  if (changePercent >= limitPercent - 0.01) {
    return PriceLimitStatus.LIMIT_UP
  } else if (changePercent <= -limitPercent + 0.01) {
    return PriceLimitStatus.LIMIT_DOWN
  }

  return PriceLimitStatus.NONE
}

/**
 * 获取涨跌停颜色
 * A股：红涨绿跌
 */
export function getPriceLimitColor(status: PriceLimitStatus): string {
  switch (status) {
    case PriceLimitStatus.LIMIT_UP:
      return '#EF5350' // 红色 (涨停)
    case PriceLimitStatus.LIMIT_DOWN:
      return '#26A69A' // 绿色 (跌停)
    default:
      return ''
  }
}

/**
 * 检测是否需要复权
 * 根据时间间隔判断是否需要复权
 */
export function needsAdjustment(period: string): boolean {
  // 日线、周线、月线需要复权
  // 分时、分钟线不需要复权
  const needsAdjPeriods = ['1d', '1w', '1M']
  return needsAdjPeriods.includes(period)
}

/**
 * 计算复权因子
 * 简化版本：实际应该从API获取
 */
export function calculateAdjustmentFactor(
  originalPrice: number,
  adjustedPrice: number
): number {
  if (originalPrice === 0) {
    return 1
  }
  return adjustedPrice / originalPrice
}

/**
 * 获取手数
 * A股：100股为1手
 */
export function getLotShares(quantity: number): number {
  return Math.floor(quantity / 100)
}

/**
 * 格式化手数显示
 */
export function formatLotShares(quantity: number): string {
  const lots = getLotShares(quantity)
  if (lots === 0) {
    return '< 1手'
  }
  return `${lots}手`
}

/**
 * 判断是否为交易日
 * 简化版本：实际应该调用API
 */
export function isTradingDay(date: Date): boolean {
  const day = date.getDay()
  // 周末不是交易日
  if (day === 0 || day === 6) {
    return false
  }
  // TODO: 检查节假日
  return true
}

/**
 * 计算T+1结算日期
 * A股：T+1结算（当天买入，下一个交易日卖出）
 */
export function calculateTPlus1SettlementDate(tradeDate: Date): Date {
  const settlementDate = new Date(tradeDate)
  let daysToAdd = 1

  // 向后查找交易日
  while (daysToAdd > 0) {
    settlementDate.setDate(settlementDate.getDate() + 1)
    if (isTradingDay(settlementDate)) {
      daysToAdd--
    }
  }

  return settlementDate
}

/**
 * 格式化T+1结算日期显示
 */
export function formatSettlementDate(date: Date): string {
  const t1Date = calculateTPlus1SettlementDate(date)
  const month = String(t1Date.getMonth() + 1).padStart(2, '0')
  const day = String(t1Date.getDate()).padStart(2, '0')
  return `${t1Date.getFullYear()}-${month}-${day}`
}

/**
 * 判断K线是否为涨跌停
 * 用于在图表上标记
 */
export function isPriceLimitBar(
  open: number,
  high: number,
  low: number,
  close: number,
  prevClose: number,
  boardType: 'main' | 'chiNext' | 'star' | 'bje' = 'main'
): boolean {
  const limitStatus = detectPriceLimit(close, prevClose, boardType)
  return limitStatus !== PriceLimitStatus.NONE
}

/**
 * 计算A股交易费用
 *
 * @param amount 交易金额（元）
 * @param direction 交易方向（买入/卖出）
 * @param config 费率配置（可选）
 * @returns 交易费用明细
 *
 * @example
 * ```typescript
 * // 买入10000元的股票
 * const buyFees = calculateCommission(10000, TradeDirection.BUY)
 * // {
 * //   commission: 5,      // 佣金（最低5元）
 * //   stampTax: 0,        // 印花税（买入免征）
 * //   transferFee: 0.1,   // 过户费
 * //   total: 5.1,
 * //   netAmount: -10005.1
 * // }
 *
 * // 卖出10000元的股票
 * const sellFees = calculateCommission(10000, TradeDirection.SELL)
 * // {
 * //   commission: 5,       // 佣金（最低5元）
 * //   stampTax: 10,        // 印花税（0.1%）
 * //   transferFee: 0.1,    // 过户费
 * //   total: 15.1,
 * //   netAmount: 9984.9
 * // }
 * ```
 */
export function calculateCommission(
  amount: number,
  direction: TradeDirection,
  config: TradingFeesConfig = {}
): TradingFeesResult {
  // 默认费率配置
  const {
    commissionRate = 0.0003,    // 0.03% 佣金
    minCommission = 5,          // 最低5元
    stampTaxRate = 0.001,       // 0.1% 印花税
    transferFeeRate = 0.00001   // 0.001% 过户费
  } = config

  // 1. 计算佣金（双向收取，最低5元）
  const commissionAmount = amount * commissionRate
  const commission = Math.max(commissionAmount, minCommission)

  // 2. 计算印花税（仅卖出收取）
  const stampTax = direction === TradeDirection.SELL ? amount * stampTaxRate : 0

  // 3. 计算过户费（双向收取）
  const transferFee = amount * transferFeeRate

  // 4. 计算总费用
  const total = commission + stampTax + transferFee

  // 5. 计算净额
  const netAmount = direction === TradeDirection.BUY
    ? -(amount + total)  // 买入：金额 + 费用（支出）
    : (amount - total)   // 卖出：金额 - 费用（收入）

  return {
    commission: Number(commission.toFixed(2)),
    stampTax: Number(stampTax.toFixed(2)),
    transferFee: Number(transferFee.toFixed(2)),
    total: Number(total.toFixed(2)),
    netAmount: Number(netAmount.toFixed(2))
  }
}

/**
 * 格式化交易费用显示
 *
 * @param fees 交易费用结果
 * @returns 格式化后的费用字符串
 *
 * @example
 * ```typescript
 * const fees = calculateCommission(10000, TradeDirection.SELL)
 * const formatted = formatTradingFees(fees)
 * // "佣金: 5.00元, 印花税: 10.00元, 过户费: 0.10元, 总计: 15.10元"
 * ```
 */
export function formatTradingFees(fees: TradingFeesResult): string {
  return `佣金: ${fees.commission.toFixed(2)}元, ` +
         `印花税: ${fees.stampTax.toFixed(2)}元, ` +
         `过户费: ${fees.transferFee.toFixed(2)}元, ` +
         `总计: ${fees.total.toFixed(2)}元`
}

/**
 * 计算买入成本
 *
 * @param price 买入价格（元）
 * @param quantity 买入数量（股）
 * @param config 费率配置（可选）
 * @returns 总成本（含费用）
 *
 * @example
 * ```typescript
 * const cost = calculateBuyCost(10.5, 1000)
 * // 10500 + 5 + 0 + 0.105 = 10505.105
 * ```
 */
export function calculateBuyCost(
  price: number,
  quantity: number,
  config?: TradingFeesConfig
): number {
  const amount = price * quantity
  const fees = calculateCommission(amount, TradeDirection.BUY, config)
  return Math.abs(fees.netAmount)
}

/**
 * 计算卖出收入
 *
 * @param price 卖出价格（元）
 * @param quantity 卖出数量（股）
 * @param config 费率配置（可选）
 * @returns 净收入（扣除费用后）
 *
 * @example
 * ```typescript
 * const income = calculateSellIncome(11.0, 1000)
 * // 11000 - 5 - 11 - 0.11 = 10983.89
 * ```
 */
export function calculateSellIncome(
  price: number,
  quantity: number,
  config?: TradingFeesConfig
): number {
  const amount = price * quantity
  const fees = calculateCommission(amount, TradeDirection.SELL, config)
  return fees.netAmount
}

/**
 * 计算盈亏平衡点
 *
 * @param buyPrice 买入价格
 * @param buyQuantity 买入数量
 * @param config 费率配置（可选）
 * @returns 盈亏平衡价格（需要卖出的最低价格）
 *
 * @example
 * ```typescript
 * const breakEven = calculateBreakEvenPrice(10.5, 1000)
 * // 约 10.52（需要上涨0.19%才能保本）
 * ```
 */
export function calculateBreakEvenPrice(
  buyPrice: number,
  buyQuantity: number,
  config?: TradingFeesConfig
): number {
  const buyCost = calculateBuyCost(buyPrice, buyQuantity, config)

  // 二分查找盈亏平衡价格
  let low = buyPrice
  let high = buyPrice * 1.5  // 假设最多上涨50%
  let breakEvenPrice = buyPrice

  for (let i = 0; i < 50; i++) {  // 50次迭代足够精确
    const mid = (low + high) / 2
    const sellIncome = calculateSellIncome(mid, buyQuantity, config)

    if (Math.abs(sellIncome - buyCost) < 0.01) {
      breakEvenPrice = mid
      break
    }

    if (sellIncome > buyCost) {
      high = mid
    } else {
      low = mid
    }
    breakEvenPrice = mid
  }

  return breakEvenPrice
}

/**
 * 验证手数是否合法
 *
 * @param quantity 股数
 * @returns 是否为100的整数倍
 */
export function validateLotSize(quantity: number): boolean {
  return quantity > 0 && quantity % 100 === 0
}

/**
 * 计算交易回合费用（买入+卖出）
 *
 * @param price 买入价格
 * @param quantity 数量
 * @param sellPrice 卖出价格（可选，默认同买入价格）
 * @param config 费率配置（可选）
 * @returns 往返总费用
 */
export function calculateRoundTripFees(
  price: number,
  quantity: number,
  sellPrice?: number,
  config?: TradingFeesConfig
): number {
  const buyAmount = price * quantity
  const sellAmount = (sellPrice || price) * quantity

  const buyFees = calculateCommission(buyAmount, TradeDirection.BUY, config)
  const sellFees = calculateCommission(sellAmount, TradeDirection.SELL, config)

  return buyFees.total + sellFees.total
}
