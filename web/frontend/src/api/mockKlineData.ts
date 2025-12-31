import type { KLineData, IntervalType, AdjustType } from '../types/kline';

const generateMockCandles = (
  basePrice: number,
  count: number,
  interval: IntervalType
): KLineData[] => {
  const candles: KLineData[] = [];
  let currentPrice = basePrice;
  const now = Date.now();

  const intervalMs: Record<IntervalType, number> = {
    '1m': 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
    '1w': 7 * 24 * 60 * 60 * 1000,
    '1M': 30 * 24 * 60 * 60 * 1000
  };

  for (let i = count - 1; i >= 0; i--) {
    const volatility = 0.02;
    const change = (Math.random() - 0.5) * 2 * volatility * currentPrice;
    const open = currentPrice;
    const close = currentPrice + change;
    const high = Math.max(open, close) + Math.random() * volatility * currentPrice;
    const low = Math.min(open, close) - Math.random() * volatility * currentPrice;
    const volume = Math.floor(Math.random() * 10000000) + 1000000;

    candles.push({
      timestamp: now - i * intervalMs[interval],
      open: Number(open.toFixed(2)),
      high: Number(high.toFixed(2)),
      low: Number(low.toFixed(2)),
      close: Number(close.toFixed(2)),
      volume,
      amount: Number((volume * (open + close) / 2).toFixed(2))
    });

    currentPrice = close;
  }

  return candles;
};

export const mockKlineData: Record<string, KLineData[]> = {
  '000001.SZ': generateMockCandles(10.5, 500, '1d'),
  '600519.SH': generateMockCandles(1800, 500, '1d'),
  '000001.SH': generateMockCandles(3200, 500, '1d'),
  '300750.SZ': generateMockCandles(240, 500, '1d')
};

export const loadMockKlineData = async (
  symbol: string,
  interval: IntervalType = '1d',
  _adjust: AdjustType = 'qfq',
  startDate?: string,
  endDate?: string
): Promise<{ candles: KLineData[] }> => {
  await new Promise(resolve => setTimeout(resolve, 300));

  let candles = mockKlineData[symbol] || generateMockCandles(10.5, 500, interval);

  if (startDate || endDate) {
    const start = startDate ? new Date(startDate).getTime() : 0;
    const end = endDate ? new Date(endDate).getTime() : Date.now();
    candles = candles.filter(c => c.timestamp >= start && c.timestamp <= end);
  }

  return { candles };
};

export const mockIndicators = {
  MA: (candles: KLineData[], periods: number[] = [5, 10, 20]) => {
    const result: Record<string, number[]> = {};
    periods.forEach(p => {
      result[`MA${p}`] = [];
      for (let i = 0; i < candles.length; i++) {
        if (i < p - 1) {
          result[`MA${p}`].push(NaN);
        } else {
          const sum = candles.slice(i - p + 1, i + 1).reduce((s, c) => s + c.close, 0);
          result[`MA${p}`].push(Number((sum / p).toFixed(2)));
        }
      }
    });
    return result;
  },
  BOLL: (candles: KLineData[], period: number = 20, stdDev: number = 2) => {
    const upper: number[] = [];
    const middle: number[] = [];
    const lower: number[] = [];

    for (let i = 0; i < candles.length; i++) {
      if (i < period - 1) {
        upper.push(NaN);
        middle.push(NaN);
        lower.push(NaN);
      } else {
        const slice = candles.slice(i - period + 1, i + 1);
        const closes = slice.map(c => c.close);
        const sma = closes.reduce((s, c) => s + c, 0) / period;
        const variance = closes.reduce((s, c) => s + Math.pow(c - sma, 2), 0) / period;
        const std = Math.sqrt(variance);

        middle.push(Number(sma.toFixed(2)));
        upper.push(Number((sma + stdDev * std).toFixed(2)));
        lower.push(Number((sma - stdDev * std).toFixed(2)));
      }
    }
    return { upper, middle, lower };
  },
  RSI: (candles: KLineData[], period: number = 14) => {
    const values: number[] = [];
    let gains = 0;
    let losses = 0;

    for (let i = 1; i < candles.length; i++) {
      const change = candles[i].close - candles[i - 1].close;
      if (i <= period) {
        if (change > 0) gains += change;
        else losses -= change;
        if (i === period) {
          const rs = gains / losses;
          values.push(Number((100 - 100 / (1 + rs)).toFixed(2)));
        } else {
          values.push(NaN);
        }
      } else {
        const avgGain = gains / period;
        const avgLoss = losses / period;
        const currentGain = change > 0 ? change : 0;
        const currentLoss = change > 0 ? 0 : -change;
        const newAvgGain = (avgGain * (period - 1) + currentGain) / period;
        const newAvgLoss = (avgLoss * (period - 1) + currentLoss) / period;
        gains = newAvgGain * period;
        losses = newAvgLoss * period;
        const rs = newAvgLoss === 0 ? 100 : newAvgGain / newAvgLoss;
        values.push(Number((100 - 100 / (1 + rs)).toFixed(2)));
      }
    }
    values.unshift(NaN);
    return values;
  },
  MACD: (candles: KLineData[], fast: number = 12, slow: number = 26, signal: number = 9) => {
    const ema = (data: number[], period: number): number[] => {
      const result: number[] = [];
      const k = 2 / (period + 1);
      for (let i = 0; i < data.length; i++) {
        if (i === 0) {
          result.push(data[i]);
        } else {
          result.push(data[i] * k + result[i - 1] * (1 - k));
        }
      }
      return result;
    };

    const closes = candles.map(c => c.close);
    const fastEma = ema(closes, fast);
    const slowEma = ema(closes, slow);
    const dif = fastEma.map((f, i) => Number((f - slowEma[i]).toFixed(4)));
    const dea = ema(dif, signal);
    const macd = dif.map((d, i) => Number((d - dea[i]) * 2).toFixed(4));

    return { dif, dea, macd };
  }
};

export const loadMockIndicators = async (
  symbol: string,
  interval: IntervalType,
  type: 'overlay' | 'oscillator',
  indicatorNames: string[]
) => {
  await new Promise(resolve => setTimeout(resolve, 200));

  const candles = mockKlineData[symbol] || generateMockCandles(10.5, 500, interval);
  const result: Record<string, unknown> = {};

  if (type === 'overlay') {
    if (indicatorNames.includes('MA')) {
      result['MA'] = mockIndicators.MA(candles);
    }
    if (indicatorNames.includes('BOLL')) {
      result['BOLL'] = mockIndicators.BOLL(candles);
    }
  } else {
    if (indicatorNames.includes('RSI')) {
      result['RSI'] = mockIndicators.RSI(candles);
    }
    if (indicatorNames.includes('MACD')) {
      result['MACD'] = mockIndicators.MACD(candles);
    }
  }

  return result;
};

export const mockStopLimit = {
  '000001.SZ': { limit_up: 11.55, limit_down: 9.45, limit_pct: 0.10 },
  '600519.SH': { limit_up: 1980.00, limit_down: 1620.00, limit_pct: 0.10 },
  'default': { limit_up: 0, limit_down: 0, limit_pct: 0.10 }
};

export const loadMockStopLimit = async (symbol: string, prevClose: number) => {
  await new Promise(resolve => setTimeout(resolve, 100));
  const limit = mockStopLimit[symbol] || mockStopLimit['default'];
  if (limit.limit_up === 0) {
    return {
      limit_up: Number((prevClose * 1.10).toFixed(2)),
      limit_down: Number((prevClose * 0.90).toFixed(2)),
      limit_pct: 0.10
    };
  }
  return limit;
};
