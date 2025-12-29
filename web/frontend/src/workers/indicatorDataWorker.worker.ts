import type { KLineData, IndicatorResult } from '@/types/kline';
import type { IndicatorParams } from '@/types/indicator';

interface WorkerMessage {
  type: 'CALCULATE_INDICATOR';
  payload: {
    data: KLineData[];
    indicatorType: string;
    params?: IndicatorParams;
  };
}

interface WorkerResponse {
  type: 'INDICATOR_RESULT';
  payload: {
    indicatorType: string;
    result: IndicatorResult;
  };
}

function calculateSMA(data: number[], period: number): number[] {
  const result: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(NaN);
    } else {
      let sum = 0;
      for (let j = 0; j < period; j++) {
        sum += data[i - j];
      }
      result.push(sum / period);
    }
  }
  return result;
}

function calculateEMA(data: number[], period: number): number[] {
  const result: number[] = [];
  const multiplier = 2 / (period + 1);

  let sum = 0;
  for (let i = 0; i < period && i < data.length; i++) {
    sum += data[i];
  }
  let initialSMA = sum / period;

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      result.push(NaN);
    } else if (i === period - 1) {
      result.push(initialSMA);
    } else {
      const ema = (data[i] - result[i - 1]) * multiplier + result[i - 1];
      result.push(ema);
    }
  }
  return result;
}

function calculateBOLL(data: number[], period: number = 20, std: number = 2): { upper: number[]; middle: number[]; lower: number[] } {
  const middle = calculateSMA(data, period);
  const upper: number[] = [];
  const lower: number[] = [];

  for (let i = 0; i < data.length; i++) {
    if (i < period - 1) {
      upper.push(NaN);
      lower.push(NaN);
    } else {
      let sumSquares = 0;
      for (let j = 0; j < period; j++) {
        const diff = data[i - j] - middle[i];
        sumSquares += diff * diff;
      }
      const stdDev = Math.sqrt(sumSquares / period);
      upper.push(middle[i] + stdDev * std);
      lower.push(middle[i] - stdDev * std);
    }
  }
  return { upper, middle, lower };
}

function calculateMACD(
  data: number[],
  fastPeriod: number = 12,
  slowPeriod: number = 26,
  signalPeriod: number = 9
): { dif: number[]; dea: number[]; macd: number[] } {
  const fastEMA = calculateEMA(data, fastPeriod);
  const slowEMA = calculateEMA(data, slowPeriod);

  const dif: number[] = [];
  for (let i = 0; i < data.length; i++) {
    if (i < slowPeriod - 1) {
      dif.push(NaN);
    } else {
      dif.push(fastEMA[i] - slowEMA[i]);
    }
  }

  const difValid = dif.filter(v => !isNaN(v));
  const deaValid = calculateEMA(difValid, signalPeriod);

  const dea: number[] = [];
  const macd: number[] = [];
  let deaIndex = 0;

  for (let i = 0; i < dif.length; i++) {
    if (isNaN(dif[i])) {
      dea.push(NaN);
      macd.push(NaN);
    } else {
      if (deaIndex < deaValid.length) {
        dea.push(deaValid[deaIndex]);
        macd.push((dif[i] - deaValid[deaIndex]) * 2);
        deaIndex++;
      } else {
        dea.push(NaN);
        macd.push(NaN);
      }
    }
  }
  return { dif, dea, macd };
}

function calculateRSI(data: number[], period: number = 14): number[] {
  const result: number[] = [];
  const gains: number[] = [];
  const losses: number[] = [];

  for (let i = 1; i < data.length; i++) {
    const change = data[i] - data[i - 1];
    gains.push(change > 0 ? change : 0);
    losses.push(change < 0 ? -change : 0);
  }

  for (let i = 0; i < data.length; i++) {
    if (i === 0) {
      result.push(NaN);
    } else if (i < period) {
      result.push(NaN);
    } else {
      let avgGain = 0;
      let avgLoss = 0;

      for (let j = 0; j < period; j++) {
        avgGain += gains[i - 1 - j];
        avgLoss += losses[i - 1 - j];
      }
      avgGain /= period;
      avgLoss /= period;

      if (avgLoss === 0) {
        result.push(100);
      } else {
        const rs = avgGain / avgLoss;
        result.push(100 - 100 / (1 + rs));
      }
    }
  }
  return result;
}

function calculateKDJ(
  high: number[],
  low: number[],
  close: number[],
  period: number = 9,
  kPeriod: number = 3,
  dPeriod: number = 3
): { k: number[]; d: number[]; j: number[] } {
  const resultK: number[] = [];
  const resultD: number[] = [];
  const resultJ: number[] = [];

  for (let i = 0; i < close.length; i++) {
    if (i < period - 1) {
      resultK.push(NaN);
      resultD.push(NaN);
      resultJ.push(NaN);
    } else {
      let highest = -Infinity;
      let lowest = Infinity;

      for (let j = 0; j < period; j++) {
        if (high[i - j] > highest) highest = high[i - j];
        if (low[i - j] < lowest) lowest = low[i - j];
      }

      const rsv = highest === lowest ? 50 : (close[i] - lowest) / (highest - lowest) * 100;

      let k: number;
      let d: number;

      if (i === period - 1) {
        k = (2/3) * 50 + (1/3) * rsv;
        d = (2/3) * 50 + (1/3) * k;
      } else {
        k = (2/3) * resultK[i - 1] + (1/3) * rsv;
        d = (2/3) * resultD[i - 1] + (1/3) * k;
      }

      resultK.push(k);
      resultD.push(d);
      resultJ.push(3 * k - 2 * d);
    }
  }
  return { k: resultK, d: resultD, j: resultJ };
}

self.onmessage = (event: MessageEvent<WorkerMessage>) => {
  const { type, payload } = event.data;

  if (type !== 'CALCULATE_INDICATOR') {
    return;
  }

  const { data, indicatorType, params } = payload;

  if (!data || data.length === 0) {
    self.postMessage({
      type: 'INDICATOR_RESULT',
      payload: {
        indicatorType,
        result: { values: [], timestamps: [] }
      }
    } as WorkerResponse);
    return;
  }

  try {
    const closes = data.map(d => d.close);
    const opens = data.map(d => d.open);
    const highs = data.map(d => d.high);
    const lows = data.map(d => d.low);
    const timestamps = data.map(d => d.timestamp);

    let result: IndicatorResult;

    switch (indicatorType.toUpperCase()) {
      case 'MA': {
        const period = (params?.period as number) || 20;
        const values = calculateSMA(closes, period);
        result = { values, timestamps };
        break;
      }

      case 'EMA': {
        const period = (params?.period as number) || 12;
        const values = calculateEMA(closes, period);
        result = { values, timestamps };
        break;
      }

      case 'BOLL': {
        const period = (params?.period as number) || 20;
        const std = (params?.std as number) || 2;
        const boll = calculateBOLL(closes, period, std);
        result = { upper: boll.upper, middle: boll.middle, lower: boll.lower, timestamps };
        break;
      }

      case 'MACD': {
        const fast = (params?.fast as number) || 12;
        const slow = (params?.slow as number) || 26;
        const signal = (params?.signal as number) || 9;
        const macd = calculateMACD(closes, fast, slow, signal);
        result = { dif: macd.dif, dea: macd.dea, macd: macd.macd, timestamps };
        break;
      }

      case 'RSI': {
        const period = (params?.period as number) || 14;
        const values = calculateRSI(closes, period);
        result = { values, timestamps };
        break;
      }

      case 'KDJ': {
        const period = (params?.period as number) || 9;
        const kdj = calculateKDJ(highs, lows, closes, period);
        result = { k: kdj.k, d: kdj.d, j: kdj.j, timestamps };
        break;
      }

      default:
        result = { values: [], timestamps };
    }

    self.postMessage({
      type: 'INDICATOR_RESULT',
      payload: {
        indicatorType,
        result
      }
    } as WorkerResponse);

  } catch (error) {
    console.error(`Error calculating ${indicatorType}:`, error);

    self.postMessage({
      type: 'INDICATOR_RESULT',
      payload: {
        indicatorType,
        result: { values: [], timestamps: [], error: String(error) }
      }
    } as WorkerResponse);
  }
};

export {};
