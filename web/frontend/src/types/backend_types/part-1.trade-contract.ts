import type { TradeDirection, TradeStatus, TradeType } from './part-1'

export interface TradeContract {
  id: string;
  symbol: string;
  type: TradeType;
  status: TradeStatus;
  direction: TradeDirection;
  entryPrice: number;
  exitPrice: number;
  entryTime: string;
  exitTime: string;
  entryQuantity: number;
  exitQuantity: number;
  entryAmount: number;
  exitAmount: number;
  commission: number;
  slippage: number;
  pnl: number;
  pnlPercent: number;
}
