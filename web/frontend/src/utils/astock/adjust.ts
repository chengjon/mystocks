import type { KLineData } from '@/types/kline';

export interface AdjustInfo {
  type: 'qfq' | 'hfq' | 'none';
  label: string;
  description: string;
}

export const ADJUST_CONFIGS: Record<string, AdjustInfo> = {
  qfq: {
    type: 'qfq',
    label: '前复权',
    description: '复权后价格 = 复权前价格 × 复权因子'
  },
  hfq: {
    type: 'hfq',
    label: '后复权',
    description: '复权前价格 = 复权后价格 ÷ 复权因子'
  },
  none: {
    type: 'none',
    label: '不复权',
    description: '使用原始交易价格'
  }
};

export const getAdjustConfig = (adjust: string): AdjustInfo => {
  return ADJUST_CONFIGS[adjust] || ADJUST_CONFIGS.none;
};

export interface AdjustData {
  factor: number;
  baseDate: string;
  adjustedPrices: KLineData[];
}

export const calculateAdjustFactor = (
  klineData: KLineData[],
  targetDate: Date,
  type: 'qfq' | 'hfq'
): { factor: number; basePrice: number } | null => {
  if (klineData.length === 0) return null;

  let baseKline: KLineData | null = null;
  for (let i = klineData.length - 1; i >= 0; i--) {
    if (new Date(klineData[i].timestamp) <= targetDate) {
      baseKline = klineData[i];
      break;
    }
  }

  if (!baseKline) return null;

  const basePrice = baseKline.close;
  const currentPrice = klineData[klineData.length - 1].close;

  if (type === 'qfq') {
    return { factor: currentPrice / basePrice, basePrice };
  } else {
    return { factor: basePrice / currentPrice, basePrice };
  }
};

export const applyAdjustFactor = (
  klineData: KLineData[],
  factor: number
): KLineData[] => {
  return klineData.map(kline => ({
    ...kline,
    open: Number((kline.open * factor).toFixed(2)),
    high: Number((kline.high * factor).toFixed(2)),
    low: Number((kline.low * factor).toFixed(2)),
    close: Number((kline.close * factor).toFixed(2)),
    amount: kline.amount ? Number((kline.amount * factor).toFixed(2)) : undefined
  }));
};

export const generateAdjustLabel = (
  adjust: 'qfq' | 'hfq' | 'none',
  factor?: number
): string => {
  const config = ADJUST_CONFIGS[adjust];
  if (!factor || adjust === 'none') {
    return config.label;
  }

  const factorDisplay = factor >= 1 ? factor.toFixed(2) : factor.toFixed(4);
  return `${config.label} (${factorDisplay})`;
};

export const validateAdjustData = (
  klineData: KLineData[],
  adjust: string
): { valid: boolean; error?: string } => {
  if (klineData.length === 0) {
    return { valid: false, error: '无数据' };
  }

  if (adjust === 'none') {
    return { valid: true };
  }

  const hasInvalidPrices = klineData.some(
    kline => kline.open <= 0 || kline.high <= 0 || kline.low <= 0 || kline.close <= 0
  );

  if (hasInvalidPrices) {
    return { valid: false, error: '价格数据无效' };
  }

  return { valid: true };
};
