import type { KLineData } from '@/types/kline';

export type IndicatorType = 'MA' | 'EMA' | 'BOLL' | 'SAR' | 'KAMA' | 'WMA' | 'DEMA' | 'TEMA';

export interface IndicatorConfig {
  name: string;
  shortName: string;
  type: IndicatorType;
  params: number[];
  colors: string[];
  visible: boolean;
}

export interface IndicatorResult {
  [key: string]: number[];
}

export const DEFAULT_INDICATORS: IndicatorConfig[] = [
  { name: '移动平均线', shortName: 'MA', type: 'MA', params: [5, 10, 20, 60], colors: ['#2DC08E', '#D4AF37', '#F92855', '#1E3D59'], visible: true },
  { name: '指数移动平均', shortName: 'EMA', type: 'EMA', params: [12, 26], colors: ['#D4AF37', '#2DC08E'], visible: false },
  { name: '布林带', shortName: 'BOLL', type: 'BOLL', params: [20, 2], colors: ['#D4AF37', '#D4AF37', '#D4AF37'], visible: false },
  { name: '抛物线指标', shortName: 'SAR', type: 'SAR', params: [0.02, 0.2], colors: ['#D4AF37'], visible: false },
  { name: '考夫曼自适应', shortName: 'KAMA', type: 'KAMA', params: [10, 2, 30], colors: ['#2DC08E'], visible: false }
];

const calculateSMA = (data: number[], period: number): number[] => {
  const result: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(NaN);
    } else {
      const slice = data.slice(i - period + 1, i + 1);
      const sum = slice.reduce((a, b) => a + b, 0);
      result.push(Number((sum / period).toFixed(2)));
    }
  }
  return result;
};

const calculateEMA = (data: number[], period: number): number[] => {
  const result: number[] = [];
  const k = 2 / (period + 1);

  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      result.push(data[i]);
    } else {
      result.push(Number((data[i] * k + result[i - 1] * (1 - k)).toFixed(2)));
    }
  }
  return result;
};

const calculateBOLL = (data: number[], period: number, stdDev: number): { upper: number[]; middle: number[]; lower: number[] } => {
  const upper: number[] = [];
  const middle: number[] = [];
  const lower: number[] = [];

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      upper.push(NaN);
      middle.push(NaN);
      lower.push(NaN);
    } else {
      const slice = data.slice(i - period + 1, i + 1);
      const sma = slice.reduce((a, b) => a + b, 0) / period;
      const variance = slice.reduce((a, b) => a + Math.pow(b - sma, 2), 0) / period;
      const std = Math.sqrt(variance);

      middle.push(Number(sma.toFixed(2)));
      upper.push(Number((sma + stdDev * std).toFixed(2)));
      lower.push(Number((sma - stdDev * std).toFixed(2)));
    }
  }
  return { upper, middle, lower };
};

const calculateSAR = (high: number[], low: number[], af: number = 0.02, maxAf: number = 0.2): number[] => {
  const result: number[] = [];
  const n = high.length;

  if (n < 2) {
    return new Array(n).fill(NaN);
  }

  let isUptrend = high[1] > high[0];
  let sar = isUptrend ? low[0] : high[0];
  let ep = isUptrend ? high[0] : low[0];
  let afVal = af;

  for (let i = 0; i < n; i++) {
    if (i === 0) {
      result.push(sar);
      continue;
    }

    const prevSar = sar;
    const newSar = prevSar + afVal * (ep - prevSar);
    const prevHigh = high[i - 1];
    const prevLow = low[i - 1];
    const currHigh = high[i];
    const currLow = low[i];

    if (isUptrend) {
      if (currHigh > ep) {
        ep = currHigh;
        afVal = Math.min(afVal + af, maxAf);
      }
      if (currLow < newSar) {
        isUptrend = false;
        sar = ep;
        ep = currLow;
        afVal = af;
      }
    } else {
      if (currLow < ep) {
        ep = currLow;
        afVal = Math.min(afVal + af, maxAf);
      }
      if (currHigh > newSar) {
        isUptrend = true;
        sar = ep;
        ep = currHigh;
        afVal = af;
      }
    }

    sar = newSar;
    result.push(Number(sar.toFixed(2)));
  }

  return result;
};

export const calculateKAMA = (data: number[], fastPeriod: number = 10, slowPeriod: number = 2, maxPeriod: number = 30): number[] => {
  const result: number[] = [];
  const n = data.length;

  if (n < maxPeriod) {
    return new Array(n).fill(NaN);
  }

  const smooth = 2 / (fastPeriod + 1);
  const fast = 2 / (fastPeriod + 1);
  const slow = 2 / (slowPeriod + 1);
  const diff = Math.abs(data[0] - data[0]);

  for (let i = 0; i < n; i++) {
    if (i < maxPeriod) {
      result.push(NaN);
      continue;
    }

    const periodData = data.slice(i - maxPeriod + 1, i + 1);
    const change = Math.abs(data[i] - data[i - maxPeriod]);
    const volatility = periodData.reduce((sum, val, idx) => {
      if (idx === 0) return sum;
      return sum + Math.abs(val - periodData[idx - 1]);
    }, 0);

    const er = volatility === 0 ? 0 : change / volatility;
    const sc = Math.pow(er * (fast - slow) + slow, 2);

    if (i === maxPeriod) {
      result.push(data[i]);
    } else {
      const prevKama = result[i - 1];
      const newKama = prevKama + sc * (data[i] - prevKama);
      result.push(Number(newKama.toFixed(2)));
    }
  }

  return result;
};

export const calculateIndicator = (
  klineData: KLineData[],
  type: IndicatorType,
  params: number[]
): IndicatorResult => {
  const closes = klineData.map(d => d.close);
  const highs = klineData.map(d => d.high);
  const lows = klineData.map(d => d.low);

  switch (type) {
    case 'MA': {
      const result: IndicatorResult = {};
      params.forEach((p, idx) => {
        result[`MA${p}`] = calculateSMA(closes, p);
      });
      return result;
    }
    case 'EMA': {
      const result: IndicatorResult = {};
      params.forEach((p, idx) => {
        result[`EMA${p}`] = calculateEMA(closes, p);
      });
      return result;
    }
    case 'BOLL': {
      const boll = calculateBOLL(closes, params[0], params[1] || 2);
      return {
        [`BOLL_UPPER`]: boll.upper,
        [`BOLL_MIDDLE`]: boll.middle,
        [`BOLL_LOWER`]: boll.lower
      };
    }
    case 'SAR': {
      const sar = calculateSAR(highs, lows, params[0], params[1]);
      return { SAR: sar };
    }
    case 'KAMA': {
      const kama = calculateKAMA(closes, params[0], params[1], params[2]);
      return { KAMA: kama };
    }
    default:
      return {};
  }
};

export const formatIndicatorValue = (value: number): string => {
  if (isNaN(value) || !isFinite(value)) return '--';
  if (Math.abs(value) >= 10000) {
    return value.toFixed(0);
  }
  if (Math.abs(value) >= 100) {
    return value.toFixed(2);
  }
  return value.toFixed(3);
};
