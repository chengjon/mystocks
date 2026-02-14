export interface CancelOrderRequest {
  order_id?: string;
}

export interface CancelOrderResponse {
  order_id?: string;
  success?: boolean;
  message?: string;
  cancelled_quantity?: number;
  remaining_quantity?: number;
  cancelled_at?: string;
}

export interface OrderRequest {
  symbol?: string;
  direction?: string;
  order_type?: string;
  price?: number | null;
  quantity?: number;
}

export interface OrderResponse {
  order_id?: string;
  symbol?: string;
  direction?: string;
  order_type?: string;
  price?: number | null;
  quantity?: number;
  filled_quantity?: number;
  average_price?: number | null;
  status?: string;
  commission?: number | null;
  created_at?: string;
  updated_at?: string | null;
}

export interface PortfolioSummary {
  total_market_value?: number;
  total_cost?: number;
  total_profit_loss?: number;
  total_profit_loss_percent?: number;
  position_count?: number;
  positions?: PositionItem[];
}

export interface TradeHistoryItem {
  trade_id?: string;
  order_id?: string;
  symbol?: string;
  direction?: string;
  price?: number;
  quantity?: number;
  amount?: number;
  commission?: number;
  trade_time?: string;
  trade_type?: string;
}

export interface TradeHistoryRequest {
  start_date?: string | null;
  end_date?: string | null;
  symbol?: string | null;
  page?: number;
  page_size?: number;
}

export interface TradeHistoryResponse {
  trades?: TradeHistoryItem[];
  total_count?: number;
  total_amount?: number;
  total_commission?: number;
  page?: number;
  page_size?: number;
}

export interface TradeOrderModel {
  symbol?: string;
  order_type?: string;
  price?: number;
  quantity?: number;
  order_validity?: string | null;
}

export interface TradeRecord {
  trade_id?: number;
  symbol?: string;
  trade_date?: string;
  action?: string;
  price?: number;
  quantity?: number;
  amount?: number;
  commission?: number;
  profit_loss?: number | null;
}

