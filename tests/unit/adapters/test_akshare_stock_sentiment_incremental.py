from unittest.mock import patch

import pandas as pd
import pytest

from src.adapters.akshare.market_adapter import AkshareMarketDataAdapter


@pytest.mark.asyncio
async def test_get_stock_hot_follow_xq_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_hot_follow_xq", create=True) as mock_hot_follow:
        mock_hot_follow.return_value = pd.DataFrame(
            {
                "股票代码": ["600519", "000858"],
                "股票简称": ["贵州茅台", "五粮液"],
                "关注": [128450, 86520],
                "最新价": [1688.88, 132.55],
            }
        )

        result = await adapter.get_stock_hot_follow_xq("最热门")

    assert len(result) == 2
    assert {"symbol", "stock_name", "follow_count", "latest_price", "query_scope", "query_timestamp"} <= set(result.columns)
    assert result["query_scope"].tolist() == ["最热门", "最热门"]


@pytest.mark.asyncio
async def test_get_stock_board_change_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_board_change_em", create=True) as mock_board_change:
        mock_board_change.return_value = pd.DataFrame(
            {
                "板块名称": ["证券"],
                "涨跌幅": [3.25],
                "主力净流入": [1860000000.0],
                "板块异动总次数": [12],
                "板块异动最频繁个股及所属类型-股票代码": ["600030"],
                "板块异动最频繁个股及所属类型-股票名称": ["中信证券"],
                "板块异动最频繁个股及所属类型-买卖方向": ["买入"],
                "板块具体异动类型列表及出现次数": ["大笔买入(8), 火箭发射(4)"],
            }
        )

        result = await adapter.get_stock_board_change_em()

    assert len(result) == 1
    assert {
        "board_name",
        "change_percent",
        "main_net_inflow",
        "change_event_count",
        "frequent_stock_symbol",
        "frequent_stock_name",
        "frequent_stock_direction",
        "change_type_summary",
        "query_timestamp",
    } <= set(result.columns)


@pytest.mark.asyncio
async def test_get_stock_changes_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_changes_em", create=True) as mock_changes:
        mock_changes.return_value = pd.DataFrame(
            {
                "时间": ["09:35:21"],
                "代码": ["600519"],
                "名称": ["贵州茅台"],
                "板块": ["大笔买入"],
                "相关信息": ["成交 1200 手"],
            }
        )

        result = await adapter.get_stock_changes_em("大笔买入")

    assert len(result) == 1
    assert {"change_time", "symbol", "stock_name", "change_type", "related_info", "query_type", "query_timestamp"} <= set(
        result.columns
    )
    assert result["query_type"].tolist() == ["大笔买入"]


@pytest.mark.asyncio
async def test_get_stock_zt_pool_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_zt_pool_em", create=True) as mock_zt_pool:
        mock_zt_pool.return_value = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["603777"],
                "名称": ["来伊份"],
                "涨跌幅": [10.02],
                "最新价": [24.55],
                "成交额": [580000000.0],
                "流通市值": [8400000000.0],
                "总市值": [12300000000.0],
                "换手率": [16.8],
                "封板资金": [186000000.0],
                "首次封板时间": ["093015"],
                "最后封板时间": ["145700"],
                "炸板次数": [2],
                "涨停统计": ["3/5"],
                "连板数": [2],
                "所属行业": ["食品饮料"],
            }
        )

        result = await adapter.get_stock_zt_pool_em("20241008")

    assert len(result) == 1
    assert {
        "sequence_no",
        "symbol",
        "stock_name",
        "change_percent",
        "latest_price",
        "turnover_amount",
        "circulating_market_cap",
        "total_market_cap",
        "turnover_rate",
        "limit_up_fund",
        "first_limit_up_time",
        "last_limit_up_time",
        "reopen_count",
        "limit_up_stats",
        "consecutive_limit_up_count",
        "industry",
        "query_date",
        "query_timestamp",
    } <= set(result.columns)
    assert result["query_date"].tolist() == ["20241008"]


@pytest.mark.asyncio
async def test_get_stock_dt_pool_em_normalizes_columns():
    adapter = AkshareMarketDataAdapter()

    with patch("src.adapters.akshare.market_adapter.stock_sentiment.ak.stock_zt_pool_dtgc_em", create=True) as mock_dt_pool:
        mock_dt_pool.return_value = pd.DataFrame(
            {
                "序号": [1],
                "代码": ["000001"],
                "名称": ["平安银行"],
                "涨跌幅": [-9.98],
                "最新价": [8.21],
                "成交额": [560000000.0],
                "流通市值": [145000000000.0],
                "总市值": [182000000000.0],
                "动态市盈率": [5.8],
                "换手率": [3.2],
                "封单资金": [68000000.0],
                "最后封板时间": ["145501"],
                "板上成交额": [120000000.0],
                "连续跌停": [2],
                "开板次数": [1],
                "所属行业": ["银行"],
            }
        )

        result = await adapter.get_stock_dt_pool_em("20241011")

    assert len(result) == 1
    assert {
        "sequence_no",
        "symbol",
        "stock_name",
        "change_percent",
        "latest_price",
        "turnover_amount",
        "circulating_market_cap",
        "total_market_cap",
        "dynamic_pe_ratio",
        "turnover_rate",
        "limit_down_fund",
        "last_limit_down_time",
        "board_turnover_amount",
        "consecutive_limit_down_count",
        "reopen_count",
        "industry",
        "query_date",
        "query_timestamp",
    } <= set(result.columns)
    assert result["query_date"].tolist() == ["20241011"]
