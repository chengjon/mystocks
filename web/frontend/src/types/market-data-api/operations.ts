
export interface operations {
    getMarketOverview: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description 成功响应 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UnifiedResponse"] & {
                        data?: components["schemas"]["MarketOverviewData"];
                    };
                };
            };
            /** @description 请求参数错误 */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
            /** @description 服务器内部错误 */
            500: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    getFundFlow: {
        parameters: {
            query: {
                /**
                 * @description 股票代码
                 * @example 600519
                 */
                symbol: string;
                /** @description 时间维度（1/3/5/10天） */
                timeframe?: "1" | "3" | "5" | "10";
                /** @description 开始日期（YYYY-MM-DD） */
                start_date?: string;
                /** @description 结束日期（YYYY-MM-DD） */
                end_date?: string;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description 成功响应 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UnifiedResponse"] & {
                        data?: components["schemas"]["FundFlowData"];
                    };
                };
            };
            /** @description 请求参数错误 */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
            /** @description 股票代码不存在 */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    getKlineData: {
        parameters: {
            query: {
                /**
                 * @description 股票代码
                 * @example 600519
                 */
                symbol: string;
                /** @description K线周期 */
                interval?: "1m" | "5m" | "15m" | "30m" | "1h" | "1d";
                /** @description 开始日期（YYYY-MM-DD） */
                start_date?: string;
                /** @description 结束日期（YYYY-MM-DD） */
                end_date?: string;
                /** @description 返回数据点数量限制 */
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description 成功响应 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UnifiedResponse"] & {
                        data?: components["schemas"]["KlineData"];
                    };
                };
            };
            /** @description 请求参数错误 */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
            /** @description 股票代码不存在或无数据 */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    getETFList: {
        parameters: {
            query?: {
                /** @description ETF代码（精确查询） */
                symbol?: string;
                /** @description 关键词搜索（代码或名称模糊匹配） */
                keyword?: string;
                /** @description 市场类型 */
                market?: "SH" | "SZ";
                /** @description ETF类型 */
                category?: "股票" | "债券" | "商品" | "货币" | "QDII";
                /** @description 返回数量限制 */
                limit?: number;
                /** @description 偏移量（用于分页） */
                offset?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description 成功响应 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UnifiedResponse"] & {
                        data?: {
                            etfs?: components["schemas"]["ETFData"][];
                            /** @description 总数量 */
                            total?: number;
                            /** @description 当前页码 */
                            page?: number;
                            /** @description 每页大小 */
                            page_size?: number;
                        };
                    };
                };
            };
            /** @description 请求参数错误 */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    getLongHuBang: {
        parameters: {
            query?: {
                /** @description 日期（YYYY-MM-DD），默认为最新交易日 */
                date?: string;
                /** @description 龙虎榜类型（涨幅榜/跌幅榜/全部） */
                type?: "rise" | "fall" | "all";
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description 成功响应 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UnifiedResponse"] & {
                        data?: components["schemas"]["LongHuBangData"];
                    };
                };
            };
            /** @description 请求参数错误 */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
            /** @description 指定日期无数据 */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
    getChipRace: {
        parameters: {
            query?: {
                /** @description 日期（YYYY-MM-DD），默认为最新交易日 */
                date?: string;
                /** @description 返回股票数量限制 */
                limit?: number;
            };
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description 成功响应 */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["UnifiedResponse"] & {
                        data?: components["schemas"]["ChipRaceData"];
                    };
                };
            };
            /** @description 请求参数错误 */
            400: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
            /** @description 指定日期无数据 */
            404: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ErrorResponse"];
                };
            };
        };
    };
}

