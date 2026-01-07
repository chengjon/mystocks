import type { KLineData } from '@/types/kline';

export interface T1Status {
  isT1: boolean;
  buyDate: Date;
  sellableDate: Date;
  status: 'T+0' | 'T+1' | 'T+2' | 'T+3';
}

export const TRADE_DAYS_CYCLE = 3;

export const isTradeDay = (date: Date): boolean => {
  const day = date.getDay();
  return day >= 1 && day <= 5;
};

export const addTradeDays = (startDate: Date, days: number): Date => {
  const current = new Date(startDate);
  let added = 0;

  while (added < days) {
    current.setDate(current.getDate() + 1);
    if (isTradeDay(current)) {
      added++;
    }
  }

  return current;
};

export const calculateT1Status = (buyDate: Date, symbol: string): T1Status => {
  const isNewStock = symbol.startsWith('0') && parseInt(symbol.substring(0, 6)) >= 202300000;

  const sellableDate = isNewStock
    ? addTradeDays(buyDate, TRADE_DAYS_CYCLE + 1)
    : addTradeDays(buyDate, TRADE_DAYS_CYCLE);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const buyOnlyDate = new Date(buyDate);
  buyOnlyDate.setHours(0, 0, 0, 0);

  if (today.getTime() === buyOnlyDate.getTime()) {
    return {
      isT1: false,
      buyDate: buyOnlyDate,
      sellableDate,
      status: 'T+0'
    };
  }

  const sellableOnlyDate = new Date(sellableDate);
  sellableOnlyDate.setHours(0, 0, 0, 0);

  if (today >= sellableOnlyDate) {
    return {
      isT1: false,
      buyDate: buyOnlyDate,
      sellableDate,
      status: 'T+0'
    };
  }

  const daysDiff = Math.ceil((sellableOnlyDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  const status = `T+${daysDiff}` as 'T+1' | 'T+2' | 'T+3';

  return {
    isT1: true,
    buyDate: buyOnlyDate,
    sellableDate,
    status
  };
};

export interface T1Mark {
  index: number;
  timestamp: number;
  type: 'T+0' | 'T+1';
  label: string;
}

export const findT1Marks = (klineData: KLineData[], symbol: string): T1Mark[] => {
  const marks: T1Mark[] = [];

  for (let i = 0; i < klineData.length; i++) {
    const kline = klineData[i];
    const buyDate = new Date(kline.timestamp);

    const t1Status = calculateT1Status(buyDate, symbol);

    if (t1Status.status === 'T+0') {
      marks.push({
        index: i,
        timestamp: kline.timestamp,
        type: 'T+0',
        label: 'T+0'
      });
    } else if (t1Status.status === 'T+1') {
      marks.push({
        index: i,
        timestamp: kline.timestamp,
        type: 'T+1',
        label: 'T+1'
      });
    }
  }

  return marks;
};

export const drawT1Marker = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  type: 'T+0' | 'T+1',
  width = 30,
  height = 18
): void => {
  const colors = {
    'T+0': { bg: 'rgba(45, 192, 142, 0.3)', border: '#2DC08E', text: '#2DC08E' },
    'T+1': { bg: 'rgba(249, 40, 85, 0.3)', border: '#F92855', text: '#F92855' }
  };

  const color = colors[type];

  ctx.save();

  ctx.fillStyle = color.bg;
  ctx.strokeStyle = color.border;
  ctx.lineWidth = 1;

  ctx.beginPath();
  ctx.roundRect(x - width / 2, y - height / 2, width, height, 2);
  ctx.fill();
  ctx.stroke();

  ctx.fillStyle = color.text;
  ctx.font = '10px "Josefin Sans", sans-serif';
  ctx.textAlign = 'center';
  ctx.textBaseline = 'middle';
  ctx.fillText(type, x, y);

  ctx.restore();
};

export const getT1StatusForDate = (date: Date, symbol: string): 'T+0' | 'T+1' | 'T+2' | 'T+3' | '可卖' => {
  const status = calculateT1Status(date, symbol);
  if (status.status === 'T+0') {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const sellableOnlyDate = new Date(status.sellableDate);
    sellableOnlyDate.setHours(0, 0, 0, 0);
    return today >= sellableOnlyDate ? '可卖' : status.status;
  }
  return status.status;
};
