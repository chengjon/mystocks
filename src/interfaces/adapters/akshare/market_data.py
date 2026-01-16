"""
AkShare Market Data Functions and Adapter

市场总貌数据获取功能模块，包含适配器类和独立函数
"""

import logging
from typing import Dict, Any
import pandas as pd
import akshare as ak

logger = logging.getLogger(__name__)


# ============================================================================
# Helper Functions
# ============================================================================


def _retry_api_call(max_retries=3, delay=1):
    """API调用重试装饰器"""
    import time
    import asyncio
    from functools import wraps


def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2**attempt))  # 指数退避
                        continue
            raise last_exception

        return wrapper

    return decorator


# ============================================================================
# Legacy Functions (兼容性保持)
# ============================================================================


def get_concept_classify() -> pd.DataFrame:
    """
    获取概念分类数据

    Returns:
        pd.DataFrame: 概念分类数据
            - index: 概念代码
            - name: 概念名称
            - stock_count: 成分股数量
            - up_count: 上涨股票数
            - down_count: 下跌股票数
            - leader_stock: 领涨股
    """
    try:
        logger.info(r"[Akshare] 开始获取概念分类数据...")

        # 直接调用akshare接口
        df = ak.stock_board_concept_name_em()

        if df is None or df.empty:
            logger.info(r"[Akshare] 未能获取到概念分类数据")
            return pd.DataFrame()

        logger.info("[Akshare] 成功获取概念分类数据，共 %s 条记录", len(df))

        # 标准化列名
        df = df.rename(
            columns={
                "板块代码": "index",
                "板块名称": "name",
                "最新价": "latest_price",
                "涨跌幅": "change_percent",
                "涨跌额": "change_amount",
                "成交量": "volume",
                "成交额": "amount",
                "总市值": "total_market_value",
                "换手率": "turnover_rate",
                "上涨家数": "up_count",
                "下跌家数": "down_count",
                "领涨股": "leader_stock",
            }
        )

        # 添加股票数量列（如果不存在）
        if "up_count" in df.columns and "down_count" in df.columns:
            df["stock_count"] = df["up_count"] + df["down_count"]

        return df

    except Exception as e:
        logger.error(f"[Akshare] 获取概念分类数据失败: {str(e)}", exc_info=True)
        return pd.DataFrame()


# ============================================================================
# AkShare Market Data Adapter Class
# ============================================================================


class AkshareMarketDataAdapter:
    """
    AkShare市场总貌数据适配器

    提供上海/深圳交易所的市场总貌数据，包括：
    - 上海证券交易所市场总貌
    - 深圳证券交易所市场总貌
    - 深圳地区交易排序数据
    - 深圳行业成交数据
    - 上海交易所每日概况
    """

def __init__(self):
        """初始化适配器"""
        self.logger = logging.getLogger(__name__)

    @staticmethod
def _retry_api_call(func, max_retries=3, delay=1):
        """API调用重试装饰器"""
        import time
        import asyncio
        from functools import wraps

        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        await asyncio.sleep(delay * (2**attempt))  # 指数退避
                        continue
            raise last_exception

        return wrapper

async def get_market_overview_sse(self) -> pd.DataFrame:
        """
        获取上海证券交易所市场总貌数据

        Returns:
            pd.DataFrame: 上海市场总貌数据
                - 指数代码: index_code
                - 指数名称: index_name
                - 昨收: yesterday_close
                - 今开: today_open
                - 最新价: latest_price
                - 涨跌幅: change_percent
                - 成交量: volume
                - 成交额: amount
        """
        try:
            self.logger.info("[Akshare] 开始获取上海证券交易所市场总貌数据...")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_sse_overview():
                return ak.stock_sse_summary()

            # 调用akshare接口获取SSE市场总貌数据
            df = await _get_sse_overview()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到上海证券交易所市场总貌数据")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取上海证券交易所市场总貌数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "指数代码": "index_code",
                    "指数名称": "index_name",
                    "昨收": "yesterday_close",
                    "今开": "today_open",
                    "最新价": "latest_price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                }
            )

            # 添加查询时间戳
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取上海证券交易所市场总貌数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_market_overview_szse(self, date: str) -> pd.DataFrame:
        """
        获取深圳证券交易所市场总貌数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 深圳市场总貌数据
                - 板块: sector
                - 涨跌幅: change_percent
                - 总市值: total_market_value
                - 平均市盈率: avg_pe_ratio
                - 换手率: turnover_rate
                - 上涨家数: up_count
                - 下跌家数: down_count
        """
        try:
            self.logger.info(f"[Akshare] 开始获取深圳证券交易所市场总貌数据，日期: {date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_szse_overview():
                return ak.stock_szse_summary(date=date)

            # 调用akshare接口获取SZSE市场总貌数据
            df = await _get_szse_overview()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到深圳证券交易所市场总貌数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳证券交易所市场总貌数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块": "sector",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "平均市盈率": "avg_pe_ratio",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            # 添加查询参数
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取深圳证券交易所市场总貌数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_szse_area_trading_summary(self, date: str) -> pd.DataFrame:
        """
        获取深圳地区交易排序数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 深圳地区交易排序数据
                - 地区: region
                - 总市值: total_market_value
                - 平均市盈率: avg_pe_ratio
                - 涨跌幅: change_percent
                - 换手率: turnover_rate
                - 上涨家数: up_count
                - 下跌家数: down_count
        """
        try:
            self.logger.info(f"[Akshare] 开始获取深圳地区交易排序数据，日期: {date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_szse_area_trading():
                return ak.stock_szse_area_summary(date=date)

            # 调用akshare接口获取SZSE地区交易数据
            df = await _get_szse_area_trading()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到深圳地区交易排序数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳地区交易排序数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "地区": "region",
                    "总市值": "total_market_value",
                    "平均市盈率": "avg_pe_ratio",
                    "涨跌幅": "change_percent",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            # 添加查询参数
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取深圳地区交易排序数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_szse_sector_trading_summary(self, symbol: str, date: str) -> pd.DataFrame:
        """
        获取深圳行业成交数据

        Args:
            symbol: 行业代码，如 "BK0477"
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 深圳行业成交数据
                - 行业代码: sector_code
                - 行业名称: sector_name
                - 涨跌幅: change_percent
                - 总市值: total_market_value
                - 换手率: turnover_rate
                - 上涨家数: up_count
                - 下跌家数: down_count
        """
        try:
            self.logger.info(f"[Akshare] 开始获取深圳行业成交数据，行业: {symbol}，日期: {date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_szse_sector_trading():
                return ak.stock_szse_sector_summary(symbol=symbol, date=date)

            # 调用akshare接口获取SZSE行业成交数据
            df = await _get_szse_sector_trading()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到深圳行业成交数据，行业: {symbol}，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取深圳行业成交数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "板块代码": "sector_code",
                    "板块名称": "sector_name",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "up_count",
                    "下跌家数": "down_count",
                }
            )

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取深圳行业成交数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_sse_daily_deal_summary(self, date: str) -> pd.DataFrame:
        """
        获取上海交易所每日概况数据

        Args:
            date: 查询日期，格式为YYYY-MM-DD

        Returns:
            pd.DataFrame: 上海交易所每日概况数据
                - 项目: item
                - 数量: count
                - 金额: amount
                - 占总计: percentage
        """
        try:
            self.logger.info(f"[Akshare] 开始获取上海交易所每日概况数据，日期: {date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_sse_daily_deal():
                return ak.stock_sse_deal_daily(date=date)

            # 调用akshare接口获取SSE每日概况数据
            df = await _get_sse_daily_deal()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到上海交易所每日概况数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info("[Akshare] 成功获取上海交易所每日概况数据，共 %s 条记录", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "项目": "item",
                    "数量": "count",
                    "金额": "amount",
                    "占总计": "percentage",
                }
            )

            # 添加查询参数
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取上海交易所每日概况数据失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

def get_stock_industry_concept(self, symbol: str) -> Dict:
        """
        获取个股的行业和概念分类信息

        Args:
            symbol: str - 股票代码

        Returns:
            Dict: 个股行业和概念信息
                - symbol: 股票代码
                - industries: 行业列表
                - concepts: 概念列表
        """
        try:
            logger.info("[Akshare] 开始获取个股 %s 的行业和概念信息...", symbol)

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_stock_industry():
                return ak.stock_individual_info_em(symbol=symbol)

            # 调用akshare接口获取个股信息
            df = _get_stock_industry()

            if df is None or df.empty:
                logger.info("[Akshare] 未能获取到个股 %s 的信息", symbol)
                return {"symbol": symbol, "industries": [], "concepts": []}

            logger.info("[Akshare] 成功获取个股 %s 的信息", symbol)

            # 提取行业和概念信息
            industries = []
            concepts = []

            # 查找行业和概念相关的行
            for _, row in df.iterrows():
                if "行业" in str(row.get("item", "")) or "所属行业" in str(row.get("item", "")):
                    industry = row.get("value", "")
                    if industry and industry != "--":
                        industries.append(industry)
                elif "概念" in str(row.get("item", "")):
                    concept = row.get("value", "")
                    if concept and concept != "--":
                        # 概念可能包含多个，用逗号分隔
                        concept_list = [c.strip() for c in str(concept).split(",") if c.strip()]
                        concepts.extend(concept_list)

            return {
                "symbol": symbol,
                "industries": industries,
                "concepts": list(set(concepts)),  # 去重
            }

        except Exception as e:
            logger.error("[Akshare] 获取个股 %s 的行业和概念信息失败: %s", symbol, e)
            import traceback

            traceback.print_exc()
            return {"symbol": symbol, "industries": [], "concepts": []}

def get_market_overview_sse(self) -> pd.DataFrame:
        """
        获取上海证券交易所市场总貌数据

        Returns:
            pd.DataFrame: 上海交易所市场总貌数据
                - project: 项目名称 (流通股本、总市值、平均市盈率等)
                - stock: 股票数据
                - kcb: 科创板数据
                - main_board: 主板数据
        """
        try:
            logger.info("[Akshare] 开始获取上海证券交易所市场总貌数据...")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_sse_summary():
                return ak.stock_sse_summary()

            # 调用akshare接口获取上海交易所市场总貌数据
            df = _get_sse_summary()

            if df is None or df.empty:
                logger.warning("[Akshare] 未获取到上海交易所市场总貌数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取上海交易所市场总貌数据，共 %s 行", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "项目": "project",
                    "股票": "stock",
                    "科创板": "kcb",
                    "主板": "main_board",
                    "报告时间": "report_date",
                }
            )

            # 添加数据获取时间戳
            df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error("[Akshare] 获取上海交易所市场总貌数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

def get_market_overview_szse(self, date: str = None) -> pd.DataFrame:
        """
        获取深圳证券交易所市场总貌数据

        Args:
            date: str - 查询日期，格式YYYYMMDD，默认当前交易日

        Returns:
            pd.DataFrame: 深圳交易所市场总貌数据
                - securities_category: 证券类别
                - count: 数量
                - trading_amount: 成交金额
                - total_market_value: 总市值
                - circulating_market_value: 流通市值
        """
        try:
            logger.info("[Akshare] 开始获取深圳证券交易所市场总貌数据，日期: %s", date or "最新")

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_szse_summary():
                return ak.stock_szse_summary(date=date)

            # 调用akshare接口获取深圳交易所市场总貌数据
            df = _get_szse_summary()

            if df is None or df.empty:
                logger.warning("[Akshare] 未获取到深圳交易所市场总貌数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取深圳交易所市场总貌数据，共 %s 行", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "证券类别": "securities_category",
                    "数量": "count",
                    "成交金额": "trading_amount",
                    "总市值": "total_market_value",
                    "流通市值": "circulating_market_value",
                }
            )

            # 添加数据获取时间戳和查询日期
            df["query_date"] = date
            df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error("[Akshare] 获取深圳交易所市场总貌数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

def get_szse_area_trading_summary(self, date: str) -> pd.DataFrame:
        """
        获取深圳证券交易所地区交易排序数据

        Args:
            date: str - 查询日期，格式YYYYMM (如202412)

        Returns:
            pd.DataFrame: 地区交易排序数据
                - rank: 排名序号
                - region: 地区名称
                - total_trading_amount: 总交易额
                - market_share: 市场占比
                - stock_trading_amount: 股票交易额
                - fund_trading_amount: 基金交易额
                - bond_trading_amount: 债券交易额
                - priority_stock_trading: 优先股交易额 (2025年后)
                - option_trading: 期权交易额 (2025年后)
        """
        try:
            logger.info("[Akshare] 开始获取深圳交易所地区交易排序数据，日期: %s", date)

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_area_summary():
                return ak.stock_szse_area_summary(date=date)

            # 调用akshare接口获取地区交易排序数据
            df = _get_area_summary()

            if df is None or df.empty:
                logger.warning("[Akshare] 未获取到深圳交易所地区交易排序数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取深圳交易所地区交易排序数据，共 %s 行", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "序号": "rank",
                    "地区": "region",
                    "总交易额": "total_trading_amount",
                    "占市场": "market_share",
                    "股票交易额": "stock_trading_amount",
                    "基金交易额": "fund_trading_amount",
                    "债券交易额": "bond_trading_amount",
                    "优先股交易额": "priority_stock_trading",
                    "期权交易额": "option_trading",
                }
            )

            # 添加数据获取时间戳和查询日期
            df["query_date"] = date
            df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error("[Akshare] 获取深圳交易所地区交易排序数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

def get_szse_sector_trading_summary(self, symbol: str, date: str) -> pd.DataFrame:
        """
        获取深圳证券交易所股票行业成交数据

        Args:
            symbol: str - 查询类型 ("当月" 或 "当年")
            date: str - 年月，格式YYYYMM

        Returns:
            pd.DataFrame: 股票行业成交数据
                - project_name: 项目名称
                - project_name_en: 项目名称英文
                - trading_days: 交易天数
                - trading_amount_rmb: 成交金额(人民币元)
                - amount_market_share: 成交金额占总计(%)
                - volume_shares: 成交股数(股数)
                - volume_market_share: 成交股数占总计(%)
                - orders_count: 成交笔数(笔)
                - orders_market_share: 成交笔数占总计(%)
        """
        try:
            logger.info("[Akshare] 开始获取深圳交易所股票行业成交数据，类型: %s，日期: %s", symbol, date)

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_sector_summary():
                return ak.stock_szse_sector_summary(symbol=symbol, date=date)

            # 调用akshare接口获取股票行业成交数据
            df = _get_sector_summary()

            if df is None or df.empty:
                logger.warning("[Akshare] 未获取到深圳交易所股票行业成交数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取深圳交易所股票行业成交数据，共 %s 行", len(df))

            # 标准化列名
            df = df.rename(
                columns={
                    "项目名称": "project_name",
                    "项目名称-英文": "project_name_en",
                    "交易天数": "trading_days",
                    "成交金额-人民币元": "trading_amount_rmb",
                    "成交金额-占总计": "amount_market_share",
                    "成交股数-股数": "volume_shares",
                    "成交股数-占总计": "volume_market_share",
                    "成交笔数-笔": "orders_count",
                    "成交笔数-占总计": "orders_market_share",
                }
            )

            # 添加数据获取时间戳和查询参数
            df["query_symbol"] = symbol
            df["query_date"] = date
            df["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df

        except Exception as e:
            logger.error("[Akshare] 获取深圳交易所股票行业成交数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

def get_sse_daily_deal_summary(self, date: str) -> pd.DataFrame:
        """
        获取上海证券交易所每日概况数据

        Args:
            date: str - 查询日期，格式YYYYMMDD

        Returns:
            pd.DataFrame: 上海交易所每日概况数据
                - metric: 指标名称
                - stock: 股票数据
                - main_board_a: 主板A股
                - main_board_b: 主板B股
                - kcb: 科创板
                - stock_repo: 股票回购
        """
        try:
            logger.info("[Akshare] 开始获取上海交易所每日概况数据，日期: %s", date)

            # 使用重试装饰器包装API调用
            @self._retry_api_call
            def _get_sse_daily():
                return ak.stock_sse_deal_daily(date=date)

            # 调用akshare接口获取每日概况数据
            df = _get_sse_daily()

            if df is None or df.empty:
                logger.warning("[Akshare] 未获取到上海交易所每日概况数据")
                return pd.DataFrame()

            logger.info("[Akshare] 成功获取上海交易所每日概况数据，共 %s 行", len(df))

            # 数据透视：将宽表转换为长表格式
            df_melted = df.melt(id_vars=["单日情况"], var_name="category", value_name="value")

            # 标准化列名
            df_melted = df_melted.rename(columns={"单日情况": "metric", "category": "category", "value": "value"})

            # 添加数据获取时间戳和查询日期
            df_melted["query_date"] = date
            df_melted["data_fetch_time"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")

            return df_melted

        except Exception as e:
            logger.error("[Akshare] 获取上海交易所每日概况数据失败: %s", e)
            import traceback

            traceback.print_exc()
            return pd.DataFrame()

    # ============================================================================
    # Phase 2: 个股信息数据扩充
    # ============================================================================

async def get_stock_individual_info_em(self, symbol: str) -> Dict[str, Any]:
        """
        获取个股信息查询-东财 (akshare.stock_individual_info_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            Dict: 个股基本信息字典
                - symbol: 股票代码
                - company_name: 公司名称
                - industry: 行业分类
                - concept: 概念板块
                - province: 省份
                - city: 城市
                - business_scope: 主营业务
                - employees: 员工人数
                - total_assets: 总资产
                - total_liabilities: 总负债
                - net_assets: 净资产
                - revenue: 营业收入
                - net_profit: 净利润
                - pe_ratio: 市盈率
                - pb_ratio: 市净率
                - roe: 净资产收益率
                - roa: 总资产报酬率
        """
        try:
            self.logger.info(f"[Akshare] 开始获取个股信息，东财数据源，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_stock_info():
                return ak.stock_individual_info_em(symbol=symbol)

            # 调用akshare接口获取个股信息
            df = await _get_stock_info()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的东财个股信息")
                return {"symbol": symbol, "error": "No data found"}

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的东财个股信息，共 {len(df)} 条记录")

            # 转换为字典格式
            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            # 添加查询时间戳
            info_dict["query_timestamp"] = pd.Timestamp.now().isoformat()

            return info_dict

        except Exception as e:
            self.logger.error(f"[Akshare] 获取个股信息失败，东财数据源，股票 {symbol}: {str(e)}", exc_info=True)
            return {"symbol": symbol, "error": str(e)}

async def get_stock_individual_basic_info_xq(self, symbol: str) -> Dict[str, Any]:
        """
        获取个股信息查询-雪球 (akshare.stock_individual_basic_info_xq)

        Args:
            symbol: 股票代码，如 "SZ000001" 或 "SH600000"

        Returns:
            Dict: 个股雪球基本信息字典
                - symbol: 股票代码
                - name: 股票名称
                - current_price: 当前价格
                - change_percent: 涨跌幅
                - volume: 成交量
                - market_cap: 市值
                - pe_ratio: 市盈率
                - pb_ratio: 市净率
                - dividend_yield: 股息率
                - high_52w: 52周最高
                - low_52w: 52周最低
        """
        try:
            self.logger.info(f"[Akshare] 开始获取个股基本信息，雪球数据源，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_stock_basic_xq():
                return ak.stock_individual_basic_info_xq(symbol=symbol)

            # 调用akshare接口获取雪球个股信息
            df = await _get_stock_basic_xq()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的雪球个股基本信息")
                return {"symbol": symbol, "error": "No data found"}

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的雪球个股基本信息，共 {len(df)} 条记录")

            # 转换为字典格式
            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            # 添加查询时间戳
            info_dict["query_timestamp"] = pd.Timestamp.now().isoformat()

            return info_dict

        except Exception as e:
            self.logger.error(f"[Akshare] 获取个股基本信息失败，雪球数据源，股票 {symbol}: {str(e)}", exc_info=True)
            return {"symbol": symbol, "error": str(e)}

async def get_stock_zyjs_ths(self, symbol: str) -> Dict[str, Any]:
        """
        获取主营介绍-同花顺 (akshare.stock_zyjs_ths)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            Dict: 主营介绍信息字典
                - symbol: 股票代码
                - company_profile: 公司简介
                - main_business: 主营业务
                - business_scope: 经营范围
                - competitive_advantage: 竞争优势
                - development_strategy: 发展战略
                - risk_factors: 风险因素
        """
        try:
            self.logger.info(f"[Akshare] 开始获取主营介绍，同花顺数据源，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_zyjs_ths():
                return ak.stock_zyjs_ths(symbol=symbol)

            # 调用akshare接口获取同花顺主营介绍
            df = await _get_zyjs_ths()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的同花顺主营介绍")
                return {"symbol": symbol, "error": "No data found"}

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的同花顺主营介绍，共 {len(df)} 条记录")

            # 转换为字典格式
            info_dict = {"symbol": symbol}
            for _, row in df.iterrows():
                key = row.get("item", "").strip()
                value = row.get("value", "")
                if key:
                    info_dict[key] = value

            # 添加查询时间戳
            info_dict["query_timestamp"] = pd.Timestamp.now().isoformat()

            return info_dict

        except Exception as e:
            self.logger.error(f"[Akshare] 获取主营介绍失败，同花顺数据源，股票 {symbol}: {str(e)}", exc_info=True)
            return {"symbol": symbol, "error": str(e)}

async def get_stock_zygc_em(self, symbol: str) -> pd.DataFrame:
        """
        获取主营构成-东财 (akshare.stock_zygc_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 主营构成数据
                - symbol: 股票代码
                - business_segment: 业务板块
                - revenue: 营业收入
                - revenue_ratio: 收入占比
                - profit: 利润
                - profit_ratio: 利润占比
                - report_date: 报告期
        """
        try:
            self.logger.info(f"[Akshare] 开始获取主营构成，东财数据源，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_zygc_em():
                return ak.stock_zygc_em(symbol=symbol)

            # 调用akshare接口获取东财主营构成
            df = await _get_zygc_em()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的东财主营构成")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的东财主营构成，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "业务板块": "business_segment",
                    "营业收入": "revenue",
                    "收入占比": "revenue_ratio",
                    "利润": "profit",
                    "利润占比": "profit_ratio",
                    "报告期": "report_date",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询时间戳
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取主营构成失败，东财数据源，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_comment_em(self, symbol: str) -> pd.DataFrame:
        """
        获取千股千评 (akshare.stock_comment_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 千股千评数据
                - symbol: 股票代码
                - analyst_count: 分析师数量
                - rating_average: 平均评级
                - rating_buy: 买入评级数量
                - rating_overweight: 增持评级数量
                - rating_hold: 中性评级数量
                - rating_underweight: 减持评级数量
                - rating_sell: 卖出评级数量
                - target_price_avg: 平均目标价
                - target_price_high: 最高目标价
                - target_price_low: 最低目标价
        """
        try:
            self.logger.info(f"[Akshare] 开始获取千股千评，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_comment_em():
                return ak.stock_comment_em(symbol=symbol)

            # 调用akshare接口获取千股千评
            df = await _get_comment_em()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的千股千评数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的千股千评数据，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "分析师数量": "analyst_count",
                    "平均评级": "rating_average",
                    "买入": "rating_buy",
                    "增持": "rating_overweight",
                    "中性": "rating_hold",
                    "减持": "rating_underweight",
                    "卖出": "rating_sell",
                    "平均目标价": "target_price_avg",
                    "最高目标价": "target_price_high",
                    "最低目标价": "target_price_low",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询时间戳
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取千股千评失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_comment_detail_zlkp_jgcyd_em(self, symbol: str) -> pd.DataFrame:
        """
        获取千股千评详情-机构评级 (akshare.stock_comment_detail_zlkp_jgcyd_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 千股千评详情数据
                - symbol: 股票代码
                - analyst_name: 分析师姓名
                - organization: 机构名称
                - rating: 评级
                - target_price: 目标价
                - report_date: 报告日期
                - report_title: 报告标题
        """
        try:
            self.logger.info(f"[Akshare] 开始获取千股千评详情-机构评级，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_comment_detail():
                return ak.stock_comment_detail_zlkp_jgcyd_em(symbol=symbol)

            # 调用akshare接口获取千股千评详情
            df = await _get_comment_detail()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的千股千评详情")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的千股千评详情，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "分析师": "analyst_name",
                    "机构": "organization",
                    "评级": "rating",
                    "目标价": "target_price",
                    "报告日期": "report_date",
                    "报告标题": "report_title",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询时间戳
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取千股千评详情失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_news_em(self, symbol: str) -> pd.DataFrame:
        """
        获取个股新闻 (akshare.stock_news_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 个股新闻数据
                - symbol: 股票代码
                - title: 新闻标题
                - content: 新闻内容
                - publish_time: 发布时间
                - source: 新闻来源
                - url: 新闻链接
        """
        try:
            self.logger.info(f"[Akshare] 开始获取个股新闻，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_stock_news():
                return ak.stock_news_em(symbol=symbol)

            # 调用akshare接口获取个股新闻
            df = await _get_stock_news()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的新闻数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的新闻数据，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "标题": "title",
                    "内容": "content",
                    "发布时间": "publish_time",
                    "来源": "source",
                    "链接": "url",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询时间戳
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取个股新闻失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_bid_ask_em(self, symbol: str) -> pd.DataFrame:
        """
        获取行情报价 (akshare.stock_bid_ask_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 行情报价数据 (五档报价)
                - symbol: 股票代码
                - bid_price_1: 买一价
                - bid_volume_1: 买一量
                - ask_price_1: 卖一价
                - ask_volume_1: 卖一量
                - bid_price_2: 买二价
                - bid_volume_2: 买二量
                - ask_price_2: 卖二价
                - ask_volume_2: 卖二量
                - ... (买五/卖五报价)
        """
        try:
            self.logger.info(f"[Akshare] 开始获取行情报价，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_bid_ask():
                return ak.stock_bid_ask_em(symbol=symbol)

            # 调用akshare接口获取行情报价
            df = await _get_bid_ask()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的行情报价")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的行情报价，共 {len(df)} 行")

            # 标准化列名 (五档报价)
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "买一价": "bid_price_1",
                    "买一量": "bid_volume_1",
                    "卖一价": "ask_price_1",
                    "卖一量": "ask_volume_1",
                    "买二价": "bid_price_2",
                    "买二量": "bid_volume_2",
                    "卖二价": "ask_price_2",
                    "卖二量": "ask_volume_2",
                    "买三价": "bid_price_3",
                    "买三量": "bid_volume_3",
                    "卖三价": "ask_price_3",
                    "卖三量": "ask_volume_3",
                    "买四价": "bid_price_4",
                    "买四量": "bid_volume_4",
                    "卖四价": "ask_price_4",
                    "卖四量": "ask_volume_4",
                    "买五价": "bid_price_5",
                    "买五量": "bid_volume_5",
                    "卖五价": "ask_price_5",
                    "卖五量": "ask_volume_5",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询时间戳
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取行情报价失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

    # ============================================================================
    # Phase 3: 资金流向数据扩充
    # ============================================================================

async def get_stock_hsgt_fund_flow_summary_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取沪深港通资金流向汇总 (akshare.stock_hsgt_fund_flow_summary_em)

        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            pd.DataFrame: 沪深港通资金流向汇总数据
                - date: 日期
                - north_money: 北向资金
                - south_money: 南向资金
                - daily_limit: 当日额度
                - daily_balance: 当日余额
                - daily_used: 当日使用额度
        """
        try:
            self.logger.info(f"[Akshare] 开始获取沪深港通资金流向汇总，日期范围: {start_date} 到 {end_date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_hsgt_summary():
                return ak.stock_hsgt_fund_flow_summary_em(start_date=start_date, end_date=end_date)

            # 调用akshare接口获取沪深港通资金流向汇总
            df = await _get_hsgt_summary()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到沪深港通资金流向汇总，日期范围: {start_date} 到 {end_date}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取沪深港通资金流向汇总，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "北向资金": "north_money",
                    "南向资金": "south_money",
                    "当日额度": "daily_limit",
                    "当日余额": "daily_balance",
                    "当日使用额度": "daily_used",
                }
            )

            # 添加查询参数
            df["query_start_date"] = start_date
            df["query_end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取沪深港通资金流向汇总失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_hsgt_fund_flow_detail_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取沪深港通资金流向明细 (akshare.stock_hsgt_fund_flow_detail_em)

        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            pd.DataFrame: 沪深港通资金流向明细数据
                - date: 日期
                - market: 市场类型
                - direction: 资金方向
                - amount: 资金金额
                - buy_amount: 买入金额
                - sell_amount: 卖出金额
                - net_amount: 净流入
        """
        try:
            self.logger.info(f"[Akshare] 开始获取沪深港通资金流向明细，日期范围: {start_date} 到 {end_date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_hsgt_detail():
                return ak.stock_hsgt_fund_flow_detail_em(start_date=start_date, end_date=end_date)

            # 调用akshare接口获取沪深港通资金流向明细
            df = await _get_hsgt_detail()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到沪深港通资金流向明细，日期范围: {start_date} 到 {end_date}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取沪深港通资金流向明细，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "市场": "market",
                    "资金方向": "direction",
                    "资金金额": "amount",
                    "买入金额": "buy_amount",
                    "卖出金额": "sell_amount",
                    "净流入": "net_amount",
                }
            )

            # 添加查询参数
            df["query_start_date"] = start_date
            df["query_end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取沪深港通资金流向明细失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_hsgt_north_net_flow_in_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取北向资金每日统计 (akshare.stock_hsgt_north_net_flow_in_em)

        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            pd.DataFrame: 北向资金每日统计数据
                - date: 日期
                - net_flow: 净流入
                - buy_amount: 买入金额
                - sell_amount: 卖出金额
                - cumulative_net_flow: 累计净流入
        """
        try:
            self.logger.info(f"[Akshare] 开始获取北向资金每日统计，日期范围: {start_date} 到 {end_date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_north_flow():
                return ak.stock_hsgt_north_net_flow_in_em(start_date=start_date, end_date=end_date)

            # 调用akshare接口获取北向资金每日统计
            df = await _get_north_flow()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到北向资金每日统计，日期范围: {start_date} 到 {end_date}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取北向资金每日统计，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "净流入": "net_flow",
                    "买入金额": "buy_amount",
                    "卖出金额": "sell_amount",
                    "累计净流入": "cumulative_net_flow",
                }
            )

            # 添加查询参数
            df["query_start_date"] = start_date
            df["query_end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()
            df["fund_direction"] = "north"  # 北向资金标识

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取北向资金每日统计失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_hsgt_south_net_flow_in_em(self, start_date: str, end_date: str) -> pd.DataFrame:
        """
        获取南向资金每日统计 (akshare.stock_hsgt_south_net_flow_in_em)

        Args:
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            pd.DataFrame: 南向资金每日统计数据
                - date: 日期
                - net_flow: 净流入
                - buy_amount: 买入金额
                - sell_amount: 卖出金额
                - cumulative_net_flow: 累计净流入
        """
        try:
            self.logger.info(f"[Akshare] 开始获取南向资金每日统计，日期范围: {start_date} 到 {end_date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_south_flow():
                return ak.stock_hsgt_south_net_flow_in_em(start_date=start_date, end_date=end_date)

            # 调用akshare接口获取南向资金每日统计
            df = await _get_south_flow()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到南向资金每日统计，日期范围: {start_date} 到 {end_date}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取南向资金每日统计，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "净流入": "net_flow",
                    "买入金额": "buy_amount",
                    "卖出金额": "sell_amount",
                    "累计净流入": "cumulative_net_flow",
                }
            )

            # 添加查询参数
            df["query_start_date"] = start_date
            df["query_end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()
            df["fund_direction"] = "south"  # 南向资金标识

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取南向资金每日统计失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_hsgt_north_acc_flow_in_em(self, symbol: str) -> pd.DataFrame:
        """
        获取北向资金个股统计 (akshare.stock_hsgt_north_acc_flow_in_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 北向资金个股统计数据
                - symbol: 股票代码
                - date: 日期
                - hold_amount: 持股数量
                - hold_value: 持股市值
                - change_amount: 持股变化数量
                - change_value: 持股变化市值
        """
        try:
            self.logger.info(f"[Akshare] 开始获取北向资金个股统计，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_north_stock():
                return ak.stock_hsgt_north_acc_flow_in_em(symbol=symbol)

            # 调用akshare接口获取北向资金个股统计
            df = await _get_north_stock()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到北向资金个股统计，股票: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取北向资金个股统计，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "持股数量": "hold_amount",
                    "持股市值": "hold_value",
                    "持股变化数量": "change_amount",
                    "持股变化市值": "change_value",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            df["fund_direction"] = "north"

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取北向资金个股统计失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_hsgt_south_acc_flow_in_em(self, symbol: str) -> pd.DataFrame:
        """
        获取南向资金个股统计 (akshare.stock_hsgt_south_acc_flow_in_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 南向资金个股统计数据
                - symbol: 股票代码
                - date: 日期
                - hold_amount: 持股数量
                - hold_value: 持股市值
                - change_amount: 持股变化数量
                - change_value: 持股变化市值
        """
        try:
            self.logger.info(f"[Akshare] 开始获取南向资金个股统计，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_south_stock():
                return ak.stock_hsgt_south_acc_flow_in_em(symbol=symbol)

            # 调用akshare接口获取南向资金个股统计
            df = await _get_south_stock()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到南向资金个股统计，股票: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取南向资金个股统计，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "持股数量": "hold_amount",
                    "持股市值": "hold_value",
                    "持股变化数量": "change_amount",
                    "持股变化市值": "change_value",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            df["fund_direction"] = "south"

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取南向资金个股统计失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_hsgt_hold_stock_em(self, symbol: str) -> pd.DataFrame:
        """
        获取沪深港通持股明细 (akshare.stock_hsgt_hold_stock_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 沪深港通持股明细数据
                - symbol: 股票代码
                - date: 日期
                - participant_name: 参与者名称
                - hold_amount: 持股数量
                - hold_ratio: 持股比例
                - market_type: 市场类型
        """
        try:
            self.logger.info(f"[Akshare] 开始获取沪深港通持股明细，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_hsgt_hold():
                return ak.stock_hsgt_hold_stock_em(symbol=symbol)

            # 调用akshare接口获取沪深港通持股明细
            df = await _get_hsgt_hold()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到沪深港通持股明细，股票: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取沪深港通持股明细，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "参与者名称": "participant_name",
                    "持股数量": "hold_amount",
                    "持股比例": "hold_ratio",
                    "市场类型": "market_type",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取沪深港通持股明细失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_fund_flow_big_deal(self) -> pd.DataFrame:
        """
        获取资金流向大单统计 (akshare.stock_fund_flow_big_deal)

        Returns:
            pd.DataFrame: 资金流向大单统计数据
                - symbol: 股票代码
                - name: 股票名称
                - big_deal_amount: 大单成交金额
                - big_buy_amount: 大单买入金额
                - big_sell_amount: 大单卖出金额
                - net_big_deal: 大单净流入
        """
        try:
            self.logger.info("[Akshare] 开始获取资金流向大单统计")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_big_deal():
                return ak.stock_fund_flow_big_deal()

            # 调用akshare接口获取资金流向大单统计
            df = await _get_big_deal()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到资金流向大单统计")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取资金流向大单统计，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "股票名称": "name",
                    "大单成交金额": "big_deal_amount",
                    "大单买入金额": "big_buy_amount",
                    "大单卖出金额": "big_sell_amount",
                    "大单净流入": "net_big_deal",
                }
            )

            # 添加查询参数
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取资金流向大单统计失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_cyq_em(self, symbol: str) -> pd.DataFrame:
        """
        获取筹码分布数据 (akshare.stock_cyq_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 筹码分布数据
                - symbol: 股票代码
                - price_range: 价格区间
                - chip_amount: 筹码数量
                - chip_ratio: 筹码占比
                - concentration_degree: 集中度
        """
        try:
            self.logger.info(f"[Akshare] 开始获取筹码分布数据，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_cyq():
                return ak.stock_cyq_em(symbol=symbol)

            # 调用akshare接口获取筹码分布数据
            df = await _get_cyq()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到筹码分布数据，股票: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取筹码分布数据，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "价格区间": "price_range",
                    "筹码数量": "chip_amount",
                    "筹码占比": "chip_ratio",
                    "集中度": "concentration_degree",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取筹码分布数据失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

    # ============================================================================
    # Phase 4: 预测和分析数据扩充
    # ============================================================================

async def get_stock_profit_forecast_em(self, symbol: str) -> pd.DataFrame:
        """
        获取盈利预测-东方财富 (akshare.stock_profit_forecast_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 盈利预测数据
                - symbol: 股票代码
                - year: 预测年份
                - quarter: 预测季度
                - eps_forecast: 每股收益预测
                - net_profit_forecast: 净利润预测
                - growth_rate: 增长率预测
                - analyst_count: 分析师数量
                - institution_name: 机构名称
        """
        try:
            self.logger.info(f"[Akshare] 开始获取盈利预测，东方财富数据源，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_profit_forecast_em():
                return ak.stock_profit_forecast_em(symbol=symbol)

            # 调用akshare接口获取盈利预测数据
            df = await _get_profit_forecast_em()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的东方财富盈利预测")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的东方财富盈利预测，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "年度": "year",
                    "季度": "quarter",
                    "预测每股收益": "eps_forecast",
                    "预测净利润": "net_profit_forecast",
                    "预测增长率": "growth_rate",
                    "分析师数量": "analyst_count",
                    "机构名称": "institution_name",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            df["forecast_source"] = "em"  # 东方财富

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取盈利预测失败，东方财富数据源，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_profit_forecast_ths(self, symbol: str) -> pd.DataFrame:
        """
        获取盈利预测-同花顺 (akshare.stock_profit_forecast_ths)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 同花顺盈利预测数据
                - symbol: 股票代码
                - report_date: 报告日期
                - forecast_type: 预测类型
                - eps_forecast: 每股收益预测
                - revenue_forecast: 营收预测
                - net_profit_forecast: 净利润预测
                - pe_forecast: 市盈率预测
                - analyst_rating: 分析师评级
        """
        try:
            self.logger.info(f"[Akshare] 开始获取盈利预测，同花顺数据源，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_profit_forecast_ths():
                return ak.stock_profit_forecast_ths(symbol=symbol)

            # 调用akshare接口获取同花顺盈利预测数据
            df = await _get_profit_forecast_ths()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的同花顺盈利预测")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的同花顺盈利预测，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "报告日期": "report_date",
                    "预测类型": "forecast_type",
                    "每股收益预测": "eps_forecast",
                    "营收预测": "revenue_forecast",
                    "净利润预测": "net_profit_forecast",
                    "市盈率预测": "pe_forecast",
                    "分析师评级": "analyst_rating",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()
            df["forecast_source"] = "ths"  # 同花顺

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取盈利预测失败，同花顺数据源，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_technical_indicator_em(self, symbol: str) -> pd.DataFrame:
        """
        获取技术指标数据 (akshare.stock_technical_indicator_em)

        Args:
            symbol: 股票代码，如 "000001" 或 "600000"

        Returns:
            pd.DataFrame: 技术指标数据
                - symbol: 股票代码
                - date: 日期
                - ma5: 5日均线
                - ma10: 10日均线
                - ma20: 20日均线
                - ma30: 30日均线
                - ma60: 60日均线
                - macd: MACD指标
                - macd_signal: MACD信号线
                - macd_hist: MACD柱状图
                - rsi: RSI指标
                - kdj_k: KDJ的K值
                - kdj_d: KDJ的D值
                - kdj_j: KDJ的J值
                - boll_upper: 布林线上轨
                - boll_middle: 布林线中轨
                - boll_lower: 布林线下轨
        """
        try:
            self.logger.info(f"[Akshare] 开始获取技术指标数据，股票: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_technical_indicator():
                return ak.stock_technical_indicator_em(symbol=symbol)

            # 调用akshare接口获取技术指标数据
            df = await _get_technical_indicator()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票 {symbol} 的技术指标数据")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票 {symbol} 的技术指标数据，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "股票代码": "symbol",
                    "日期": "date",
                    "MA5": "ma5",
                    "MA10": "ma10",
                    "MA20": "ma20",
                    "MA30": "ma30",
                    "MA60": "ma60",
                    "MACD": "macd",
                    "MACD信号": "macd_signal",
                    "MACD柱状图": "macd_hist",
                    "RSI": "rsi",
                    "KDJ_K": "kdj_k",
                    "KDJ_D": "kdj_d",
                    "KDJ_J": "kdj_j",
                    "布林线上轨": "boll_upper",
                    "布林线中轨": "boll_middle",
                    "布林线下轨": "boll_lower",
                }
            )

            # 确保symbol列存在
            if "symbol" not in df.columns:
                df["symbol"] = symbol

            # 添加查询参数
            df["query_symbol"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取技术指标数据失败，股票 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_account_statistics_em(self, date: str) -> pd.DataFrame:
        """
        获取股票账户统计月度 (akshare.stock_account_statistics_em)

        Args:
            date: 查询日期，格式YYYY-MM，如 "2024-01"

        Returns:
            pd.DataFrame: 股票账户统计数据
                - date: 统计日期
                - total_accounts: 总账户数
                - active_accounts: 活跃账户数
                - new_accounts: 新增账户数
                - dormant_accounts: 休眠账户数
                - trading_accounts: 交易账户数
                - stock_accounts: 股票账户数
                - fund_accounts: 基金账户数
                - bond_accounts: 债券账户数
        """
        try:
            self.logger.info(f"[Akshare] 开始获取股票账户统计月度，日期: {date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_account_statistics():
                return ak.stock_account_statistics_em(date=date)

            # 调用akshare接口获取股票账户统计数据
            df = await _get_account_statistics()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到股票账户统计月度数据，日期: {date}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取股票账户统计月度数据，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "期末总账户数": "total_accounts",
                    "期末活跃账户数": "active_accounts",
                    "新增账户数": "new_accounts",
                    "休眠账户数": "dormant_accounts",
                    "交易账户数": "trading_accounts",
                    "股票账户数": "stock_accounts",
                    "基金账户数": "fund_accounts",
                    "债券账户数": "bond_accounts",
                }
            )

            # 添加查询参数
            df["query_date"] = date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取股票账户统计月度失败，日期 {date}: {str(e)}", exc_info=True)
            return pd.DataFrame()

    # ============================================================================
    # Phase 5: 板块和行业数据扩充
    # ============================================================================

async def get_stock_board_concept_cons_em(self, symbol: str) -> pd.DataFrame:
        """
        获取概念板块成分股 (akshare.stock_board_concept_cons_em)

        Args:
            symbol: 概念板块代码，如 "BK0477"

        Returns:
            pd.DataFrame: 概念板块成分股数据
                - symbol: 股票代码
                - name: 股票名称
                - price: 最新价
                - change_percent: 涨跌幅
                - volume: 成交量
                - amount: 成交额
                - market_cap: 市值
                - pe_ratio: 市盈率
                - pb_ratio: 市净率
        """
        try:
            self.logger.info(f"[Akshare] 开始获取概念板块成分股，板块: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_concept_cons():
                return ak.stock_board_concept_cons_em(symbol=symbol)

            # 调用akshare接口获取概念板块成分股
            df = await _get_concept_cons()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到概念板块成分股，板块: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取概念板块成分股，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "市值": "market_cap",
                    "市盈率-动态": "pe_ratio",
                    "市净率": "pb_ratio",
                }
            )

            # 添加查询参数
            df["concept_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取概念板块成分股失败，板块 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_board_concept_hist_em(
        self, symbol: str, start_date: str = None, end_date: str = None
    ) -> pd.DataFrame:
        """
        获取概念板块行情 (akshare.stock_board_concept_hist_em)

        Args:
            symbol: 概念板块代码，如 "BK0477"
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            pd.DataFrame: 概念板块行情数据
                - date: 日期
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - close: 收盘价
                - volume: 成交量
                - amount: 成交额
                - change_percent: 涨跌幅
                - concept_code: 概念板块代码
        """
        try:
            self.logger.info(f"[Akshare] 开始获取概念板块行情，板块: {symbol}，日期范围: {start_date} 到 {end_date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_concept_hist():
                return ak.stock_board_concept_hist_em(symbol=symbol, start_date=start_date, end_date=end_date)

            # 调用akshare接口获取概念板块行情
            df = await _get_concept_hist()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到概念板块行情，板块: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取概念板块行情，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "amount",
                    "振幅": "amplitude",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "换手率": "turnover_rate",
                }
            )

            # 添加查询参数
            df["concept_code"] = symbol
            df["query_start_date"] = start_date
            df["query_end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取概念板块行情失败，板块 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_board_concept_hist_min_em(self, symbol: str) -> pd.DataFrame:
        """
        获取概念板块历史行情 (akshare.stock_board_concept_hist_min_em)

        Args:
            symbol: 概念板块代码，如 "BK0477"

        Returns:
            pd.DataFrame: 概念板块分钟行情数据
                - datetime: 时间
                - price: 价格
                - volume: 成交量
                - concept_code: 概念板块代码
        """
        try:
            self.logger.info(f"[Akshare] 开始获取概念板块历史行情，板块: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_concept_hist_min():
                return ak.stock_board_concept_hist_min_em(symbol=symbol)

            # 调用akshare接口获取概念板块分钟行情
            df = await _get_concept_hist_min()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到概念板块历史行情，板块: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取概念板块历史行情，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "时间": "datetime",
                    "价格": "price",
                    "成交量": "volume",
                }
            )

            # 添加查询参数
            df["concept_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取概念板块历史行情失败，板块 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_board_industry_cons_em(self, symbol: str) -> pd.DataFrame:
        """
        获取行业板块成分股 (akshare.stock_board_industry_cons_em)

        Args:
            symbol: 行业板块代码，如 "BK0477"

        Returns:
            pd.DataFrame: 行业板块成分股数据
                - symbol: 股票代码
                - name: 股票名称
                - price: 最新价
                - change_percent: 涨跌幅
                - volume: 成交量
                - amount: 成交额
                - market_cap: 市值
                - pe_ratio: 市盈率
                - pb_ratio: 市净率
        """
        try:
            self.logger.info(f"[Akshare] 开始获取行业板块成分股，板块: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_industry_cons():
                return ak.stock_board_industry_cons_em(symbol=symbol)

            # 调用akshare接口获取行业板块成分股
            df = await _get_industry_cons()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到行业板块成分股，板块: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取行业板块成分股，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "代码": "symbol",
                    "名称": "name",
                    "最新价": "price",
                    "涨跌幅": "change_percent",
                    "成交量": "volume",
                    "成交额": "amount",
                    "市值": "market_cap",
                    "市盈率-动态": "pe_ratio",
                    "市净率": "pb_ratio",
                }
            )

            # 添加查询参数
            df["industry_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取行业板块成分股失败，板块 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_board_industry_hist_em(
        self, symbol: str, start_date: str = None, end_date: str = None
    ) -> pd.DataFrame:
        """
        获取行业板块行情 (akshare.stock_board_industry_hist_em)

        Args:
            symbol: 行业板块代码，如 "BK0477"
            start_date: 开始日期，格式YYYY-MM-DD
            end_date: 结束日期，格式YYYY-MM-DD

        Returns:
            pd.DataFrame: 行业板块行情数据
                - date: 日期
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - close: 收盘价
                - volume: 成交量
                - amount: 成交额
                - change_percent: 涨跌幅
                - industry_code: 行业板块代码
        """
        try:
            self.logger.info(f"[Akshare] 开始获取行业板块行情，板块: {symbol}，日期范围: {start_date} 到 {end_date}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_industry_hist():
                return ak.stock_board_industry_hist_em(symbol=symbol, start_date=start_date, end_date=end_date)

            # 调用akshare接口获取行业板块行情
            df = await _get_industry_hist()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到行业板块行情，板块: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取行业板块行情，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "日期": "date",
                    "开盘": "open",
                    "收盘": "close",
                    "最高": "high",
                    "最低": "low",
                    "成交量": "volume",
                    "成交额": "amount",
                    "振幅": "amplitude",
                    "涨跌幅": "change_percent",
                    "涨跌额": "change_amount",
                    "换手率": "turnover_rate",
                }
            )

            # 添加查询参数
            df["industry_code"] = symbol
            df["query_start_date"] = start_date
            df["query_end_date"] = end_date
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取行业板块行情失败，板块 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_board_industry_hist_min_em(self, symbol: str) -> pd.DataFrame:
        """
        获取行业板块历史行情 (akshare.stock_board_industry_hist_min_em)

        Args:
            symbol: 行业板块代码，如 "BK0477"

        Returns:
            pd.DataFrame: 行业板块分钟行情数据
                - datetime: 时间
                - price: 价格
                - volume: 成交量
                - industry_code: 行业板块代码
        """
        try:
            self.logger.info(f"[Akshare] 开始获取行业板块历史行情，板块: {symbol}")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_industry_hist_min():
                return ak.stock_board_industry_hist_min_em(symbol=symbol)

            # 调用akshare接口获取行业板块分钟行情
            df = await _get_industry_hist_min()

            if df is None or df.empty:
                self.logger.warning(f"[Akshare] 未能获取到行业板块历史行情，板块: {symbol}")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取行业板块历史行情，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "时间": "datetime",
                    "价格": "price",
                    "成交量": "volume",
                }
            )

            # 添加查询参数
            df["industry_code"] = symbol
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取行业板块历史行情失败，板块 {symbol}: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_sector_spot_em(self) -> pd.DataFrame:
        """
        获取热门行业排行 (akshare.stock_sector_spot_em)

        Returns:
            pd.DataFrame: 热门行业排行数据
                - sector_name: 行业名称
                - sector_code: 行业代码
                - change_percent: 涨跌幅
                - total_market_value: 总市值
                - turnover_rate: 换手率
                - rise_count: 上涨家数
                - fall_count: 下跌家数
                - leading_stocks: 领涨股
        """
        try:
            self.logger.info("[Akshare] 开始获取热门行业排行")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_sector_spot():
                return ak.stock_sector_spot_em()

            # 调用akshare接口获取热门行业排行
            df = await _get_sector_spot()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到热门行业排行")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取热门行业排行，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "板块": "sector_name",
                    "板块代码": "sector_code",
                    "涨跌幅": "change_percent",
                    "总市值": "total_market_value",
                    "换手率": "turnover_rate",
                    "上涨家数": "rise_count",
                    "下跌家数": "fall_count",
                    "领涨股": "leading_stocks",
                }
            )

            # 添加查询参数
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取热门行业排行失败: {str(e)}", exc_info=True)
            return pd.DataFrame()

async def get_stock_sector_fund_flow_rank_em(self) -> pd.DataFrame:
        """
        获取行业资金流向 (akshare.stock_sector_fund_flow_rank_em)

        Returns:
            pd.DataFrame: 行业资金流向排行数据
                - sector_name: 行业名称
                - sector_code: 行业代码
                - main_net_inflow: 主力净流入
                - main_net_inflow_rate: 主力净流入占比
                - super_large_net_inflow: 超大单净流入
                - large_net_inflow: 大单净流入
                - medium_net_inflow: 中单净流入
                - small_net_inflow: 小单净流入
                - change_percent: 涨跌幅
        """
        try:
            self.logger.info("[Akshare] 开始获取行业资金流向")

            # 使用重试装饰器包装API调用
            @_retry_api_call
            async def _get_sector_fund_flow():
                return ak.stock_sector_fund_flow_rank_em()

            # 调用akshare接口获取行业资金流向
            df = await _get_sector_fund_flow()

            if df is None or df.empty:
                self.logger.warning("[Akshare] 未能获取到行业资金流向")
                return pd.DataFrame()

            self.logger.info(f"[Akshare] 成功获取行业资金流向，共 {len(df)} 行")

            # 标准化列名
            df = df.rename(
                columns={
                    "行业板块": "sector_name",
                    "行业代码": "sector_code",
                    "主力净流入-净额": "main_net_inflow",
                    "主力净流入-净占比": "main_net_inflow_rate",
                    "超大单净流入": "super_large_net_inflow",
                    "大单净流入": "large_net_inflow",
                    "中单净流入": "medium_net_inflow",
                    "小单净流入": "small_net_inflow",
                    "行业涨跌幅": "change_percent",
                }
            )

            # 添加查询参数
            df["query_timestamp"] = pd.Timestamp.now()

            return df

        except Exception as e:
            self.logger.error(f"[Akshare] 获取行业资金流向失败: {str(e)}", exc_info=True)
            return pd.DataFrame()
