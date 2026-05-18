"""Auto-extracted response constants."""

from typing import Any

def _success_response_spec(description: str, example: object) -> dict[int, dict]:
    return {
        200: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


def _error_response_spec(status_code: int, description: str, example: dict) -> dict[int, dict]:
    return {
        status_code: {
            "description": description,
            "content": {
                "application/json": {
                    "example": example,
                }
            },
        }
    }


ETF_REFRESH_RESPONSES = {
    **_error_response_spec(
        400,
        "ETF 数据刷新失败",
        {"detail": "ETF数据源不可用", "error_code": "MARKET_OPERATION_FAILED"},
    ),
    **_error_response_spec(
        500,
        "ETF 数据刷新过程中发生内部错误",
        {"detail": "刷新ETF数据时发生错误", "error_code": "INTERNAL_SERVER_ERROR"},
    ),
    **_success_response_spec(
        "ETF 数据刷新成功",
        {"success": True, "message": "ETF实时数据刷新成功", "data": {"source": "akshare", "refreshed": True}},
    ),
}

CHIP_RACE_RESPONSES = {
    **_error_response_spec(
        500,
        "竞价抢筹查询失败",
        {"detail": "竞价抢筹服务不可用", "error_code": "MARKET_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "竞价抢筹数据列表",
        [
            {
                "id": 1,
                "symbol": "600519",
                "name": "贵州茅台",
                "trade_date": "2026-04-03",
                "race_type": "open",
                "latest_price": 1688.0,
                "change_percent": 1.86,
                "prev_close": 1657.2,
                "open_price": 1668.0,
                "race_amount": 58000000.0,
                "race_amplitude": 3.2,
                "race_commission": 72000000.0,
                "race_transaction": 58000000.0,
                "race_ratio": 12.4,
                "created_at": "2026-04-03T09:30:00",
            }
        ],
    ),
}

LHB_RESPONSES = {
    **_error_response_spec(
        500,
        "龙虎榜查询失败",
        {"detail": "龙虎榜服务不可用", "error_code": "MARKET_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "龙虎榜数据列表",
        [
            {
                "id": 1,
                "symbol": "002594",
                "name": "比亚迪",
                "trade_date": "2026-04-03",
                "reason": "日涨幅偏离值达7%",
                "buy_amount": 325000000.0,
                "sell_amount": 186000000.0,
                "net_amount": 139000000.0,
                "turnover_rate": 8.6,
                "institution_buy": 98000000.0,
                "institution_sell": 42000000.0,
                "created_at": "2026-04-03T16:05:00",
            }
        ],
    ),
}

FUND_FLOW_RESPONSES = {
    **_error_response_spec(
        500,
        "资金流向查询失败",
        {"detail": "获取资金流向数据失败: upstream unavailable", "error_code": "EXTERNAL_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "个股资金流向查询结果",
        {
            "success": True,
            "data": {
                "fund_flow": [
                    {
                        "trade_date": "2026-04-03",
                        "main_net_inflow": 128000000.0,
                        "super_large_net_inflow": 51200000.0,
                        "large_net_inflow": 76800000.0,
                        "medium_net_inflow": -8600000.0,
                        "small_net_inflow": -20100000.0,
                    }
                ],
                "total": 1,
            },
            "message": "获取600519.SH资金流向数据成功",
            "timestamp": "2026-04-07T09:30:00Z",
            "request_id": "req-market-fund-flow-001",
        },
    ),
}

FUND_FLOW_REFRESH_RESPONSES = {
    **_error_response_spec(
        400,
        "资金流向刷新失败",
        {"detail": "刷新资金流向数据失败", "error_code": "OPERATION_FAILED"},
    ),
    **_error_response_spec(
        500,
        "资金流向刷新过程中发生内部错误",
        {"detail": "刷新资金流向数据时发生错误", "error_code": "INTERNAL_SERVER_ERROR"},
    ),
    **_success_response_spec(
        "资金流向刷新结果",
        {
            "success": True,
            "data": {"symbol": "600519.SH", "timeframe": "1", "refreshed": True},
            "message": "600519.SH资金流向数据刷新成功",
            "timestamp": "2026-04-07T09:30:00Z",
            "request_id": "req-market-fund-flow-refresh-001",
        },
    ),
}

ETF_LIST_RESPONSES = {
    **_error_response_spec(
        500,
        "ETF 列表查询失败",
        {"detail": "获取ETF列表失败: upstream unavailable", "error_code": "EXTERNAL_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "ETF 实时行情列表",
        {
            "success": True,
            "data": {
                "etf_list": [
                    {
                        "id": 1,
                        "symbol": "510300",
                        "name": "沪深300ETF",
                        "trade_date": "2026-04-03",
                        "latest_price": 3.986,
                        "change_percent": 0.72,
                        "change_amount": 0.03,
                        "volume": 85234123,
                        "amount": 338000000.0,
                        "open_price": 3.95,
                        "high_price": 4.01,
                        "low_price": 3.94,
                        "prev_close": 3.956,
                        "turnover_rate": 1.86,
                        "total_market_cap": 12450000000.0,
                        "circulating_market_cap": 12450000000.0,
                        "created_at": "2026-04-03T15:00:00",
                    }
                ],
                "total": 1,
                "symbol": None,
                "keyword": "300",
            },
            "message": "获取ETF列表成功，共1条记录",
            "timestamp": "2026-04-07T09:30:00Z",
            "request_id": "req-market-etf-list-001",
        },
    ),
}

CHIP_RACE_REFRESH_RESPONSES = {
    **_error_response_spec(
        400,
        "竞价抢筹刷新失败",
        {"detail": "刷新抢筹数据失败", "error_code": "MARKET_OPERATION_FAILED"},
    ),
    **_error_response_spec(
        500,
        "竞价抢筹刷新过程中发生内部错误",
        {"detail": "刷新抢筹数据时发生错误", "error_code": "MARKET_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        "竞价抢筹刷新结果",
        {
            "success": True,
            "message": "竞价抢筹数据刷新成功",
            "data": {"race_type": "open", "trade_date": "2026-04-03", "refreshed": True},
        },
    ),
}

LHB_REFRESH_RESPONSES = {
    **_error_response_spec(
        400,
        "龙虎榜刷新失败",
        {"detail": "刷新龙虎榜数据失败", "error_code": "MARKET_OPERATION_FAILED"},
    ),
    **_error_response_spec(
        500,
        "龙虎榜刷新过程中发生内部错误",
        {"detail": "刷新龙虎榜数据时发生错误", "error_code": "MARKET_OPERATION_FAILED"},
    ),
    **_success_response_spec(
        "龙虎榜刷新结果",
        {
            "success": True,
            "message": "龙虎榜数据刷新成功",
            "data": {"trade_date": "2026-04-03", "refreshed": True},
        },
    ),
}

MARKET_QUOTES_RESPONSES = {
    **_error_response_spec(
        500,
        "实时行情查询失败",
        {"detail": "获取实时行情失败: upstream unavailable", "error_code": "EXTERNAL_SERVICE_ERROR"},
    ),
    **_success_response_spec(
        "实时行情列表",
        {
            "success": True,
            "data": {
                "quotes": [
                    {
                        "symbol": "000001",
                        "name": "平安银行",
                        "price": 12.35,
                        "change": 0.11,
                        "change_percent": 0.9,
                        "volume": 1250000,
                        "amount": 155000000.0,
                    }
                ],
                "total": 1,
                "symbols": ["000001"],
                "source": "market",
                "endpoint": "quotes",
            },
            "message": "获取1只股票实时行情成功",
            "timestamp": "2026-04-07T09:30:00Z",
            "request_id": "req-market-quotes-001",
        },
    ),
}

STOCK_LIST_RESPONSES = {
    **_error_response_spec(
        500,
        "股票列表查询失败",
        {"detail": "查询股票列表失败: database unavailable", "error_code": "DATABASE_ERROR"},
    ),
    **_success_response_spec(
        "股票基础信息列表",
        {
            "success": True,
            "data": {
                "stocks": [
                    {
                        "symbol": "600519",
                        "name": "贵州茅台",
                        "exchange": "SSE",
                        "security_type": "stock",
                        "list_date": "2001-08-27",
                        "status": "active",
                        "listing_board": "主板",
                        "market_cap": 2120000000000.0,
                        "circulating_market_cap": 2120000000000.0,
                    }
                ],
                "total": 1,
                "source": "real",
                "search": "茅台",
                "exchange": "SSE",
                "security_type": "stock",
            },
            "message": "获取股票列表成功，共1条记录",
            "timestamp": "2026-04-07T09:30:00Z",
            "request_id": "req-market-stocks-001",
        },
    ),
}

KLINE_DATA_RESPONSES = {
    **_error_response_spec(
        400,
        "K 线参数错误",
        {"detail": "开始日期格式错误: 2026/04/03，应为 YYYY-MM-DD", "error_code": "VALIDATION_ERROR"},
    ),
    **_error_response_spec(
        404,
        "未找到股票 K 线数据",
        {"detail": "股票K线数据不存在: 600519.SH", "error_code": "RESOURCE_NOT_FOUND"},
    ),
    **_error_response_spec(
        500,
        "K 线查询失败",
        {"detail": "数据源暂时不可用，请稍后重试: upstream unavailable", "error_code": "DATA_SOURCE_UNAVAILABLE"},
    ),
    **_success_response_spec(
        "股票 K 线历史数据",
        {
            "success": True,
            "stock_code": "600519.SH",
            "stock_name": "贵州茅台",
            "period": "daily",
            "adjust": "qfq",
            "data": [
                {
                    "date": "2026-04-03",
                    "timestamp": 1775174400,
                    "open": 1680.0,
                    "high": 1698.0,
                    "low": 1672.0,
                    "close": 1688.0,
                    "volume": 4589123,
                    "amount": 7742000000.0,
                    "amplitude": 1.55,
                    "change_percent": 0.86,
                }
            ],
            "count": 60,
            "source": "fallback",
            "timestamp": "2026-04-07T09:30:00",
        },
    ),
}


