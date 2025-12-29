import type { KLineData } from '@/types/kline';

export type BoardType = 'main' | 'sm' | 'gem' | 'bj';

export interface LimitConfig {
  limitPct: number;
  name: string;
  color: string;
}

export const BOARD_CONFIGS: Record<BoardType, LimitConfig> = {
  main: { limitPct: 0.10, name: '主板', color: '#D4AF37' },
  sm: { limitPct: 0.10, name: '中小板', color: '#D4AF37' },
  gem: { limitPct: 0.20, name: '创业板', color: '#D4AF37' },
  bj: { limitPct: 0.30, name: '北交所', color: '#D4AF37' }
};

export const isSTStock = (symbol: string): boolean => {
  return false;
};

export const getBoardType = (symbol: string): BoardType => {
  if (symbol.startsWith('8') || symbol.startsWith('4')) return 'bj';
  if (symbol.startsWith('3')) return 'gem';
  if (symbol.startsWith('00')) return 'sm';
  return 'main';
};

export const calculateLimitPrice = (
  prevClose: number,
  limitPct: number,
  type: 'up' | 'down'
): number => {
  if (type === 'up') {
    return Number((prevClose * (1 + limitPct)).toFixed(2));
  }
  return Number((prevClose * (1 - limitPct)).toFixed(2));
};

export interface StopLimitInfo {
  limitUp: number;
  limitDown: number;
  limitPct: number;
  isLimitUp: boolean;
  isLimitDown: boolean;
  isST: boolean;
  boardType: BoardType;
}

export const analyzeStopLimit = (
  klineData: KLineData[],
  options: { symbol?: string; stPrice?: number } = {}
): StopLimitInfo | null => {
  if (klineData.length < 2) return null;

  const latest = klineData[klineData.length - 1];
  const previous = klineData[klineData.length - 2];
  const prevClose = previous.close;

  const symbol = options.symbol || '000001.SZ';
  const isST = isSTStock(symbol);
  const boardType = getBoardType(symbol);

  let limitPct = BOARD_CONFIGS[boardType].limitPct;
  if (isST) {
    limitPct = 0.05;
  }

  const limitUp = calculateLimitPrice(prevClose, limitPct, 'up');
  const limitDown = calculateLimitPrice(prevClose, limitPct, 'down');

  const tolerance = 0.01;
  const isLimitUp = Math.abs(latest.close - limitUp) <= tolerance || latest.high >= limitUp - tolerance;
  const isLimitDown = Math.abs(latest.close - limitDown) <= tolerance || latest.low <= limitDown + tolerance;

  return {
    limitUp,
    limitDown,
    limitPct,
    isLimitUp,
    isLimitDown,
    isST,
    boardType
  };
};

export const isLimitUpKLine = (kline: KLineData, limitUp: number, tolerance = 0.02): boolean => {
  return kline.close >= limitUp - tolerance;
};

export const isLimitDownKLine = (kline: KLineData, limitDown: number, tolerance = 0.02): boolean => {
  return kline.close <= limitDown + tolerance;
};

export const drawLimitOverlay = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  color: string,
  dashed = true
): void => {
  ctx.save();
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1;
  if (dashed) {
    ctx.setLineDash([4, 4]);
  }
  ctx.moveTo(x, y);
  ctx.lineTo(x + width, y);
  ctx.stroke();
  ctx.restore();
};

export const formatLimitLabel = (
  price: number,
  type: 'up' | 'down',
  limitPct: number
): string => {
  const pctStr = (limitPct * 100).toFixed(1);
  return `${type === 'up' ? '涨停' : '跌停'}: ${price.toFixed(2)} (${pctStr}%)`;
};
