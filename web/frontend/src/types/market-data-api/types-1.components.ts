export interface components {
    schemas: {
        UnifiedResponse: {
            /**
             * @description 操作是否成功
             * @example true
             */
            success?: boolean;
            /**
             * @description HTTP状态码
             * @example 200
             */
            code?: number;
            /**
             * @description 用户友好消息
             * @example 操作成功
             */
            message?: string;
            /** @description 响应数据 */
            data?: Record<string, never>;
            /**
             * Format: date-time
             * @description ISO 8601时间戳
             * @example 2025-12-29T23:53:41Z
             */
            timestamp?: string;
            /**
             * @description 请求追踪ID
             * @example req_20251229235341
             */
            request_id?: string;
            /** @description 错误详情列表 */
            errors?: components["schemas"]["ErrorDetail"][];
        };
        ErrorDetail: {
            /**
             * @description 错误码
             * @example VALIDATION_ERROR
             */
            code?: string;
            /**
             * @description 错误消息
             * @example 参数验证失败
             */
            message?: string;
            /** @description 详细错误信息 */
            details?: Record<string, never>;
        };
        MarketOverviewData: {
            /**
             * @description 主要市场指数
             * @example {
             *       "sh000001": 3200.5,
             *       "sz399001": 10500.2
             *     }
             */
            market_index?: {
                [key: string]: number;
            };
            /**
             * @description 换手率
             * @example 0.025
             */
            turnover_rate?: number;
            rise_fall_count?: {
                /**
                 * @description 上涨股票数
                 * @example 2500
                 */
                rise?: number;
                /**
                 * @description 下跌股票数
                 * @example 1800
                 */
                fall?: number;
                /**
                 * @description 平盘股票数
                 * @example 300
                 */
                flat?: number;
            };
            /** @description 涨幅榜前N名ETF */
            top_etfs?: components["schemas"]["TopETF"][];
            /**
             * Format: date-time
             * @description 数据时间戳
             */
            timestamp?: string;
        };
        TopETF: {
            /**
             * @description ETF代码
             * @example 510300
             */
            symbol?: string;
            /**
             * @description ETF名称
             * @example 沪深300ETF
             */
            name?: string;
            /**
             * @description 涨跌幅（%）
             * @example 2.5
             */
            change_percent?: number;
        };
        FundFlowData: {
            /**
             * @description 股票代码
             * @example 600519
             */
            symbol?: string;
            /**
             * @description 主力净流入（万元）
             * @example 12500.5
             */
            main_net_inflow?: number;
            /**
             * @description 散户净流入（万元）
             * @example -3200.8
             */
            retail_net_inflow?: number;
            /**
             * @description 大单净流入（万元）
             * @example 8900.3
             */
            big_order_net_inflow?: number;
            /**
             * @description 时间维度（1/3/5/10天）
             * @example 1
             */
            timeframe?: string;
            /**
             * Format: date-time
             * @description 数据时间戳
             */
            timestamp?: string;
        };
        KlineData: {
            /**
             * @description 股票代码
             * @example 600519
             */
            symbol?: string;
            /**
             * @description K线周期
             * @example 1d
             * @enum {string}
             */
            interval?: "1m" | "5m" | "15m" | "30m" | "1h" | "1d";
            /** @description K线数据点 */
            data?: components["schemas"]["KlinePoint"][];
            /**
             * Format: date-time
             * @description 数据时间戳
             */
            timestamp?: string;
        };
        KlinePoint: {
            /**
             * Format: date-time
             * @description 时间戳
             * @example 2025-12-29T00:00:00Z
             */
            timestamp?: string;
            /**
             * @description 开盘价
             * @example 100.5
             */
            open?: number;
            /**
             * @description 最高价
             * @example 102.3
             */
            high?: number;
            /**
             * @description 最低价
             * @example 99.8
             */
            low?: number;
            /**
             * @description 收盘价
             * @example 101.2
             */
            close?: number;
            /**
             * @description 成交量
             * @example 12345678
             */
            volume?: number;
            /**
             * @description 成交额
             * @example 1234567890.12
             */
            amount?: number;
        };
        ETFData: {
            /**
             * @description ETF代码
             * @example 510300
             */
            symbol?: string;
            /**
             * @description ETF名称
             * @example 沪深300ETF
             */
            name?: string;
            /**
             * @description 当前价格
             * @example 4.523
             */
            price?: number;
            /**
             * @description 涨跌幅（%）
             * @example 1.25
             */
            change_percent?: number;
            /**
             * @description 成交量
             * @example 12345678
             */
            volume?: number;
            /**
             * @description 成交额
             * @example 123456789.01
             */
            amount?: number;
            /**
             * @description 市场（SH/SZ）
             * @example SH
             */
            market?: string;
        };
        LongHuBangData: {
            /**
             * Format: date
             * @description 日期
             * @example 2025-12-29
             */
            date?: string;
            /** @description 龙虎榜股票列表 */
            stocks?: components["schemas"]["LongHuBangStock"][];
        };
        LongHuBangStock: {
            /**
             * @description 股票代码
             * @example 600519
             */
            symbol?: string;
            /**
             * @description 股票名称
             * @example 贵州茅台
             */
            name?: string;
            /**
             * @description 上榜原因
             * @example 日涨幅偏离值达7%
             */
            reason?: string;
            /**
             * @description 买入金额（万元）
             * @example 12345.67
             */
            buy_amount?: number;
            /**
             * @description 卖出金额（万元）
             * @example 9876.54
             */
            sell_amount?: number;
        };
        ChipRaceData: {
            /**
             * Format: date
             * @description 日期
             * @example 2025-12-29
             */
            date?: string;
            /** @description 抢筹股票列表 */
            stocks?: components["schemas"]["ChipRaceStock"][];
        };
        ChipRaceStock: {
            /**
             * @description 股票代码
             * @example 600519
             */
            symbol?: string;
            /**
             * @description 股票名称
             * @example 贵州茅台
             */
            name?: string;
            /**
             * @description 抢筹比例（%）
             * @example 85.5
             */
            race_ratio?: number;
            /**
             * @description 主力买入金额（万元）
             * @example 25000.8
             */
            main_buy_amount?: number;
            /**
             * @description 散户买入金额（万元）
             * @example 12500.4
             */
            retail_buy_amount?: number;
        };
        ErrorResponse: components["schemas"]["UnifiedResponse"] & {
            /** @example false */
            success?: unknown;
            /** @example 400 */
            code?: unknown;
            /** @example null */
            data?: unknown;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}

export type $defs = Record<string, never>;
