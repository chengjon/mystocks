/**
 * 技术指标计算工具
 * 实现基础技术指标计算功能
 */

/**
 * 计算简单移动平均线 (SMA)
 * @param {number[]} data - 数据数组
 * @param {number} period - 周期
 * @returns {number[]} - SMA数组
 */
export function calculateSMA(data, period) {
  if (!data || data.length < period) {
    return Array(data?.length || 0).fill(null);
  }

  const result = Array(data.length).fill(null);

  for (let i = period - 1; i < data.length; i++) {
    let sum = 0;
    for (let j = 0; j < period; j++) {
      sum += data[i - j];
    }
    result[i] = sum / period;
  }

  return result;
}

/**
 * 计算指数移动平均线 (EMA)
 * @param {number[]} data - 数据数组
 * @param {number} period - 周期
 * @returns {number[]} - EMA数组
 */
export function calculateEMA(data, period) {
  if (!data || data.length === 0) {
    return Array(data?.length || 0).fill(null);
  }

  const result = Array(data.length).fill(null);
  const multiplier = 2 / (period + 1);

  // 第一个EMA值为第一个数据点
  result[0] = data[0];

  for (let i = 1; i < data.length; i++) {
    if (result[i - 1] !== null && data[i] !== null) {
      result[i] = (data[i] - result[i - 1]) * multiplier + result[i - 1];
    } else if (data[i] !== null) {
      result[i] = data[i];
    }
  }

  // 填充前period-1个值为null，因为需要足够的数据点来计算准确的EMA
  for (let i = 1; i < period && i < data.length; i++) {
    result[i] = null;
  }

  return result;
}

/**
 * 计算RSI (相对强弱指数)
 * @param {number[]} closePrices - 收盘价数组
 * @param {number} period - 周期
 * @returns {number[]} - RSI数组
 */
export function calculateRSI(closePrices, period) {
  if (!closePrices || closePrices.length < 2) {
    return Array(closePrices?.length || 0).fill(null);
  }

  const gains = new Array(closePrices.length).fill(0);
  const losses = new Array(closePrices.length).fill(0);
  const rsi = new Array(closePrices.length).fill(null);

  // 计算每日涨跌值
  for (let i = 1; i < closePrices.length; i++) {
    const change = closePrices[i] - closePrices[i - 1];
    gains[i] = change > 0 ? change : 0;
    losses[i] = change < 0 ? Math.abs(change) : 0;
  }

  // 计算RSI
  for (let i = period; i < closePrices.length; i++) {
    let avgGain = 0;
    let avgLoss = 0;

    // 计算前period期的平均涨跌幅
    if (i === period) {
      // 第一个period期使用简单平均
      for (let j = 1; j <= period; j++) {
        avgGain += gains[i - period + j];
        avgLoss += losses[i - period + j];
      }
      avgGain /= period;
      avgLoss /= period;
    } else {
      // 后续期使用平滑移动平均
      avgGain = ((gains[i - 1] + (period - 1) * rsi[i - 1] * avgLoss / (100 - rsi[i - 1])) / period);
      avgLoss = ((losses[i - 1] + (period - 1) * (100 - rsi[i - 1] * avgLoss / (100 - rsi[i - 1])) / period));
    }

    if (avgLoss === 0) {
      rsi[i] = 100;
    } else {
      const rs = avgGain / avgLoss;
      rsi[i] = 100 - (100 / (1 + rs));
    }
  }

  return rsi;
}

/**
 * 计算MACD指标
 * @param {number[]} closePrices - 收盘价数组
 * @param {number} fastPeriod - 快速移动平均周期 (默认12)
 * @param {number} slowPeriod - 慢速移动平均周期 (默认26)
 * @param {number} signalPeriod - 信号线周期 (默认9)
 * @returns {Object} - MACD, signal, histogram数组
 */
export function calculateMACD(closePrices, fastPeriod = 12, slowPeriod = 26, signalPeriod = 9) {
  if (!closePrices || closePrices.length < slowPeriod) {
    const length = closePrices?.length || 0;
    return {
      macd: Array(length).fill(null),
      signal: Array(length).fill(null),
      histogram: Array(length).fill(null)
    };
  }

  const fastEMA = calculateEMA(closePrices, fastPeriod);
  const slowEMA = calculateEMA(closePrices, slowPeriod);

  const macdLine = fastEMA.map((fast, i) => {
    if (fast !== null && slowEMA[i] !== null) {
      return fast - slowEMA[i];
    }
    return null;
  });

  const signalLine = calculateEMA(macdLine, signalPeriod);
  const histogram = macdLine.map((macd, i) => {
    if (macd !== null && signalLine[i] !== null) {
      return macd - signalLine[i];
    }
    return null;
  });

  return {
    macd: macdLine,
    signal: signalLine,
    histogram
  };
}

/**
 * 计算布林带
 * @param {number[]} closePrices - 收盘价数组
 * @param {number} period - 周期
 * @param {number} stdDev - 标准差倍数
 * @returns {Object} - upper, middle, lower带
 */
export function calculateBollingerBands(closePrices, period = 20, stdDev = 2) {
  if (!closePrices || closePrices.length < period) {
    const length = closePrices?.length || 0;
    return {
      upper: Array(length).fill(null),
      middle: Array(length).fill(null),
      lower: Array(length).fill(null)
    };
  }

  const middle = calculateSMA(closePrices, period);
  const upper = Array(closePrices.length).fill(null);
  const lower = Array(closePrices.length).fill(null);

  for (let i = period - 1; i < closePrices.length; i++) {
    if (middle[i] !== null) {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        const deviation = closePrices[i - j] - middle[i];
        sum += deviation * deviation;
      }
      const std = Math.sqrt(sum / period);
      upper[i] = middle[i] + std * stdDev;
      lower[i] = middle[i] - std * stdDev;
    }
  }

  return {
    upper,
    middle,
    lower
  };
}

/**
 * 根据收盘价计算多个技术指标
 * @param {Object} ohlcvData - OHLCV数据对象
 * @param {Array} indicators - 需要计算的指标数组
 * @returns {Object} - 计算结果
 */
export function calculateTechnicalIndicators(ohlcvData, indicators) {
  const result = {};
  const closePrices = ohlcvData.close;
  const length = closePrices.length;

  indicators.forEach(indicator => {
    const { abbreviation, parameters } = indicator;
    const period = parameters?.timeperiod || 14; // 默认周期

    switch (abbreviation.toUpperCase()) {
      case 'SMA':
      case 'MA':
        result[`${abbreviation}_${period}`] = calculateSMA(closePrices, period);
        break;
      case 'EMA':
        result[`${abbreviation}_${period}`] = calculateEMA(closePrices, period);
        break;
      case 'RSI':
        result[`${abbreviation}_${period}`] = calculateRSI(closePrices, period);
        break;
      case 'MACD':
        const macdParams = parameters || {};
        const macdResult = calculateMACD(
          closePrices,
          macdParams.fastperiod || 12,
          macdParams.slowperiod || 26,
          macdParams.signalperiod || 9
        );
        Object.assign(result, {
          'macd': macdResult.macd,
          'macd_signal': macdResult.signal,
          'macd_histogram': macdResult.histogram
        });
        break;
      case 'BBANDS':
        const bbResult = calculateBollingerBands(closePrices, period);
        Object.assign(result, {
          'bb_upper': bbResult.upper,
          'bb_middle': bbResult.middle,
          'bb_lower': bbResult.lower
        });
        break;
      default:
        // 其他不支持的指标，返回空数组
        result[abbreviation] = Array(length).fill(null);
        break;
    }
  });

  return result;
}