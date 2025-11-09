byapi是biyingapi.com提供的一个公开的数据接口，它的API文档请参考下面的三个链接
https://biyingapi.com/doc_hs
https://biyingapi.com/doc_zs
https://biyingapi.com/doc_jj

由于byapi是以网页和JSON数据的形式提取，所以我只能对它进行整理。
我整理的它的api_mapping如下：

        api_mapping = {
            # 股票列表
            "股票列表": "stock_list",
            "新股日历": "new_stock_calendar",
            
            # 指数行业概念
            "指数、行业、概念树": "index_industry_concept_tree",
            "根据指数、行业、概念找相关股票": "stocks_by_index_industry_concept",
            "根据股票找相关指数、行业、概念": "index_industry_concept_by_stock",
            
            # 涨跌股池
            "涨停股池": "limit_up_stocks",
            "跌停股池": "limit_down_stocks",
            "强势股池": "strong_stocks",
            "次新股池": "new_stocks",
            "炸板股池": "broken_limit_stocks",
            
            # 上市公司详情
            "公司简介": "company_profile",
            "所属指数": "index_membership",
            "历届高管成员": "executive_history",
            "历届董事会成员": "board_history",
            "历届监事会成员": "supervisory_history",
            "近年分红": "recent_dividends",
            "近年增发": "recent_seo",
            "解禁限售": "lifted_shares",
            "近一年各季度利润": "quarterly_profits",
            "近一年各季度现金流": "quarterly_cashflow",
            "近年业绩预告": "earnings_forecast",
            
            # 财务指标
            "财务指标": "financial_indicators",
            
            # 股东信息
            "十大股东": "top_shareholders",
            "十大流通股东": "top_float_shareholders",
            "股东变化趋势": "shareholder_trend",
            "基金持股": "fund_ownership",
            
            # 实时交易
            "实时交易(公开数据)": "realtime_quotes_public",
            "当天逐笔交易": "intraday_transactions",
            "实时交易数据": "realtime_quotes",
            "买卖五档盘口": "five_level_quotes",
            "实时交易数据（多股）": "multi_stock_realtime",
            "资金流向数据": "fund_flow_data",
            
            # 行情数据
            "最新分时交易": "latest_minute_quotes",
            "历史分时交易": "history_minute_quotes",
            "历史涨跌停价格": "history_limit_prices",
            "行情指标": "market_indicators",
            
            # 基础信息
            "股票基础信息": "stock_basic_info",
            
            # 公司财务
            "资产负债表": "balance_sheet",
            "利润表": "income_statement",
            "现金流量表": "cash_flow_statement",
            "财务主要指标": "financial_ratios",
            "公司股本表": "capital_structure",
            "公司十大股东": "company_top_shareholders",
            "公司十大流通股东": "company_top_float_holders",
            "公司股东数": "shareholder_count",
            
            # 技术指标
            "历史分时MACD": "history_macd",
            "历史分时MA": "history_ma",
            "历史分时BOLL": "history_boll",
            "历史分时KDJ": "history_kdj"
        }


另外，本目录下有几个文件：
byapi_info_all.md
load_json_1by1.py
optimized_api_data_v2.json
byapi_mapping_optimized.py
byapi_mapping_updated.py
可供参考。

根据以上信息，我编写了byapi_new_updated.py文件作为主程序来调用byapi提供的数据