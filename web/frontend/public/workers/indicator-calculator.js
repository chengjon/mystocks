/**
 * Technical Indicators Calculation Worker
 * GPU-accelerated technical analysis for MyStocks frontend
 *
 * Implements 8 core technical indicators:
 * - MACD (Moving Average Convergence Divergence)
 * - RSI (Relative Strength Index)
 * - Bollinger Bands (布林带)
 * - Stochastic Oscillator (随机指标)
 * - Williams %R (威廉指标)
 * - ATR (Average True Range)
 * - SMA (Simple Moving Average)
 * - EMA (Exponential Moving Average)
 */

// Import the communication protocol
importScripts('./protocol.js');

class TechnicalIndicatorsCalculator {
  constructor() {
    this.indicators = new Map();
    this.registerIndicators();
  }

  /**
   * Register all available technical indicators
   */
  registerIndicators() {
    this.indicators.set('MACD', this.calculateMACD.bind(this));
    this.indicators.set('RSI', this.calculateRSI.bind(this));
    this.indicators.set('BBANDS', this.calculateBollingerBands.bind(this));
    this.indicators.set('STOCH', this.calculateStochastic.bind(this));
    this.indicators.set('WILLIAMS_R', this.calculateWilliamsR.bind(this));
    this.indicators.set('ATR', this.calculateATR.bind(this));
    this.indicators.set('SMA', this.calculateSMA.bind(this));
    this.indicators.set('EMA', this.calculateEMA.bind(this));
  }

  /**
   * Main calculation entry point
   */
  async calculate(indicatorName, data, params = {}) {
    const calculator = this.indicators.get(indicatorName.toUpperCase());
    if (!calculator) {
      throw new Error(`Unknown indicator: ${indicatorName}`);
    }

    try {
      return await calculator(data, params);
    } catch (error) {
      throw new Error(`Failed to calculate ${indicatorName}: ${error.message}`);
    }
  }

  /**
   * MACD (Moving Average Convergence Divergence)
   * Formula: MACD = EMA(close, 12) - EMA(close, 26)
   * Signal = EMA(MACD, 9)
   * Histogram = MACD - Signal
   */
  calculateMACD(data, params = {}) {
    const fastPeriod = params.fastPeriod || 12;
    const slowPeriod = params.slowPeriod || 26;
    const signalPeriod = params.signalPeriod || 9;

    if (data.length < slowPeriod) {
      throw new Error('Insufficient data for MACD calculation');
    }

    const closes = data.map(d => d.close);
    const fastEMA = this.calculateEMAArray(closes, fastPeriod);
    const slowEMA = this.calculateEMAArray(closes, slowPeriod);

    // Calculate MACD line
    const macdLine = [];
    for (let i = slowPeriod - 1; i < closes.length; i++) {
      macdLine.push(fastEMA[i - (slowPeriod - fastPeriod)] - slowEMA[i - (slowPeriod - slowPeriod)]);
    }

    // Calculate Signal line (EMA of MACD)
    const signalLine = this.calculateEMAArray(macdLine, signalPeriod);

    // Calculate Histogram
    const histogram = [];
    const startIndex = macdLine.length - signalLine.length;
    for (let i = 0; i < signalLine.length; i++) {
      histogram.push(macdLine[i + startIndex] - signalLine[i]);
    }

    return {
      macd: macdLine,
      signal: signalLine,
      histogram: histogram,
      metadata: {
        fastPeriod,
        slowPeriod,
        signalPeriod,
        periods: macdLine.length
      }
    };
  }

  /**
   * RSI (Relative Strength Index)
   * Formula: RSI = 100 - (100 / (1 + RS))
   * RS = Average Gain / Average Loss (over period)
   */
  calculateRSI(data, params = {}) {
    const period = params.period || 14;

    if (data.length < period + 1) {
      throw new Error('Insufficient data for RSI calculation');
    }

    const gains = [];
    const losses = [];

    // Calculate price changes
    for (let i = 1; i < data.length; i++) {
      const change = data[i].close - data[i - 1].close;
      gains.push(Math.max(change, 0));
      losses.push(Math.max(-change, 0));
    }

    const rsi = [];
    let avgGain = gains.slice(0, period).reduce((sum, g) => sum + g, 0) / period;
    let avgLoss = losses.slice(0, period).reduce((sum, l) => sum + l, 0) / period;

    // First RSI value
    if (avgLoss === 0) {
      rsi.push(100);
    } else {
      const rs = avgGain / avgLoss;
      rsi.push(100 - (100 / (1 + rs)));
    }

    // Subsequent RSI values using Wilder's smoothing
    for (let i = period; i < gains.length; i++) {
      avgGain = ((avgGain * (period - 1)) + gains[i]) / period;
      avgLoss = ((avgLoss * (period - 1)) + losses[i]) / period;

      if (avgLoss === 0) {
        rsi.push(100);
      } else {
        const rs = avgGain / avgLoss;
        rsi.push(100 - (100 / (1 + rs)));
      }
    }

    return {
      rsi: rsi,
      metadata: {
        period,
        periods: rsi.length
      }
    };
  }

  /**
   * Bollinger Bands (布林带)
   * Formula:
   * Middle = SMA(close, period)
   * Upper = Middle + (StdDev * multiplier)
   * Lower = Middle - (StdDev * multiplier)
   */
  calculateBollingerBands(data, params = {}) {
    const period = params.period || 20;
    const multiplier = params.multiplier || 2;

    if (data.length < period) {
      throw new Error('Insufficient data for Bollinger Bands calculation');
    }

    const closes = data.map(d => d.close);
    const sma = this.calculateSMAArray(closes, period);

    const upper = [];
    const lower = [];

    for (let i = period - 1; i < closes.length; i++) {
      const slice = closes.slice(i - period + 1, i + 1);
      const stdDev = this.calculateStandardDeviation(slice);
      const middle = sma[i - (period - 1)];

      upper.push(middle + (stdDev * multiplier));
      lower.push(middle - (stdDev * multiplier));
    }

    return {
      upper: upper,
      middle: sma,
      lower: lower,
      metadata: {
        period,
        multiplier,
        periods: upper.length
      }
    };
  }

  /**
   * Stochastic Oscillator (随机指标)
   * Formula:
   * %K = (Current Close - Lowest Low) / (Highest High - Lowest Low) * 100
   * %D = SMA(%K, 3)
   */
  calculateStochastic(data, params = {}) {
    const kPeriod = params.kPeriod || 14;
    const dPeriod = params.dPeriod || 3;

    if (data.length < kPeriod) {
      throw new Error('Insufficient data for Stochastic calculation');
    }

    const kValues = [];

    for (let i = kPeriod - 1; i < data.length; i++) {
      const slice = data.slice(i - kPeriod + 1, i + 1);
      const highest = Math.max(...slice.map(d => d.high));
      const lowest = Math.min(...slice.map(d => d.low));
      const currentClose = data[i].close;

      if (highest === lowest) {
        kValues.push(50); // Neutral when no range
      } else {
        const k = ((currentClose - lowest) / (highest - lowest)) * 100;
        kValues.push(k);
      }
    }

    const dValues = this.calculateSMAArray(kValues, dPeriod);

    return {
      k: kValues,
      d: dValues,
      metadata: {
        kPeriod,
        dPeriod,
        periods: kValues.length
      }
    };
  }

  /**
   * Williams %R (威廉指标)
   * Formula: %R = (Highest High - Current Close) / (Highest High - Lowest Low) * -100
   */
  calculateWilliamsR(data, params = {}) {
    const period = params.period || 14;

    if (data.length < period) {
      throw new Error('Insufficient data for Williams %R calculation');
    }

    const williamsR = [];

    for (let i = period - 1; i < data.length; i++) {
      const slice = data.slice(i - period + 1, i + 1);
      const highest = Math.max(...slice.map(d => d.high));
      const lowest = Math.min(...slice.map(d => d.low));
      const currentClose = data[i].close;

      if (highest === lowest) {
        williamsR.push(-50); // Neutral when no range
      } else {
        const r = ((highest - currentClose) / (highest - lowest)) * -100;
        williamsR.push(r);
      }
    }

    return {
      williamsR: williamsR,
      metadata: {
        period,
        periods: williamsR.length
      }
    };
  }

  /**
   * ATR (Average True Range)
   * Formula: TR = Max(High - Low, |High - PrevClose|, |Low - PrevClose|)
   * ATR = EMA(TR, period)
   */
  calculateATR(data, params = {}) {
    const period = params.period || 14;

    if (data.length < period + 1) {
      throw new Error('Insufficient data for ATR calculation');
    }

    const trueRanges = [];

    for (let i = 1; i < data.length; i++) {
      const high = data[i].high;
      const low = data[i].low;
      const prevClose = data[i - 1].close;

      const tr1 = high - low;
      const tr2 = Math.abs(high - prevClose);
      const tr3 = Math.abs(low - prevClose);

      trueRanges.push(Math.max(tr1, tr2, tr3));
    }

    const atr = this.calculateEMAArray(trueRanges, period);

    return {
      atr: atr,
      trueRanges: trueRanges,
      metadata: {
        period,
        periods: atr.length
      }
    };
  }

  /**
   * SMA (Simple Moving Average)
   * Formula: SMA = (Sum of closes over period) / period
   */
  calculateSMA(data, params = {}) {
    const period = params.period || 20;

    if (data.length < period) {
      throw new Error('Insufficient data for SMA calculation');
    }

    const closes = data.map(d => d.close);
    const sma = this.calculateSMAArray(closes, period);

    return {
      sma: sma,
      metadata: {
        period,
        periods: sma.length
      }
    };
  }

  /**
   * EMA (Exponential Moving Average)
   * Formula: EMA(today) = (Close(today) * multiplier) + (EMA(yesterday) * (1 - multiplier))
   * multiplier = 2 / (period + 1)
   */
  calculateEMA(data, params = {}) {
    const period = params.period || 20;

    if (data.length < period) {
      throw new Error('Insufficient data for EMA calculation');
    }

    const closes = data.map(d => d.close);
    const ema = this.calculateEMAArray(closes, period);

    return {
      ema: ema,
      metadata: {
        period,
        periods: ema.length
      }
    };
  }

  // Utility functions for array calculations

  calculateSMAArray(data, period) {
    const sma = [];
    for (let i = period - 1; i < data.length; i++) {
      const sum = data.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      sma.push(sum / period);
    }
    return sma;
  }

  calculateEMAArray(data, period) {
    const multiplier = 2 / (period + 1);
    const ema = [];

    // First EMA is SMA
    let sum = 0;
    for (let i = 0; i < period; i++) {
      sum += data[i];
    }
    ema.push(sum / period);

    // Calculate subsequent EMAs
    for (let i = period; i < data.length; i++) {
      const currentEMA = (data[i] * multiplier) + (ema[ema.length - 1] * (1 - multiplier));
      ema.push(currentEMA);
    }

    return ema;
  }

  calculateStandardDeviation(data) {
    const mean = data.reduce((sum, value) => sum + value, 0) / data.length;
    const squaredDiffs = data.map(value => Math.pow(value - mean, 2));
    const variance = squaredDiffs.reduce((sum, value) => sum + value, 0) / data.length;
    return Math.sqrt(variance);
  }
}

// Worker instance
const calculator = new TechnicalIndicatorsCalculator();

// Message handler
self.onmessage = async function(e) {
  const message = e.data;

  try {
    // Validate message
    if (!WorkerMessageUtils.validateMessage(message)) {
      throw new Error('Invalid message format');
    }

    // Process calculation request
    if (message.type === WorkerMessageType.CALCULATE_INDICATOR) {
      const { indicatorName, data, params } = message.payload;

      // Send progress update
      self.postMessage(WorkerMessageUtils.createProgress(message.id, 50, 'Calculating indicator'));

      // Perform calculation
      const result = await calculator.calculate(indicatorName, data, params);

      // Send success response
      const response = WorkerMessageUtils.createResponse(message, true, result);
      response.duration = Date.now() - message.timestamp;

      self.postMessage(response);
    } else {
      throw new Error(`Unsupported message type: ${message.type}`);
    }

  } catch (error) {
    // Send error response
    const errorResponse = WorkerMessageUtils.createError(message, error.message);
    self.postMessage(errorResponse);
  }
};

// Send ready signal
self.postMessage(WorkerMessageUtils.createMessage(WorkerMessageType.READY, {
  supportedIndicators: Array.from(calculator.indicators.keys()),
  version: '1.0.0'
}));

// Periodic heartbeat
setInterval(() => {
  self.postMessage(WorkerMessageUtils.createMessage(WorkerMessageType.HEARTBEAT, {
    timestamp: Date.now(),
    memoryUsage: performance.memory ? {
      used: performance.memory.usedJSHeapSize,
      total: performance.memory.totalJSHeapSize,
      limit: performance.memory.jsHeapSizeLimit
    } : null
  }));
}, 30000); // 30 seconds