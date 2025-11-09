"""
股票搜索服务模块
支持多数据源：
- AKShare: A股数据和港股数据
- 统一搜索接口

迁移自 OpenStock 项目
"""

import requests
import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import os
from functools import lru_cache

try:
    import akshare as ak

    AKSHARE_AVAILABLE = True
except ImportError:
    AKSHARE_AVAILABLE = False
    print("警告: AKShare 未安装，A股搜索功能将不可用")


def parse_datetime_to_timestamp(value) -> float:
    """
    将各种格式的日期时间转换为 Unix 时间戳

    Args:
        value: 日期时间值（可能是 datetime 对象、字符串或其他类型）

    Returns:
        float: Unix 时间戳
    """
    if isinstance(value, datetime):
        return value.timestamp()
    elif isinstance(value, str):
        try:
            # 尝试解析常见的日期格式
            for fmt in [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%Y/%m/%d %H:%M:%S",
                "%Y/%m/%d",
            ]:
                try:
                    dt = datetime.strptime(value, fmt)
                    return dt.timestamp()
                except ValueError:
                    continue
        except:
            pass
    # 如果无法解析，返回当前时间戳
    return datetime.now().timestamp()


def normalize_stock_code(code: str, market: str = "cn") -> str:
    """
    Normalize stock code by adding exchange suffix if missing

    Args:
        code: 6-digit stock code (e.g., "600519" or "600519.SH")
        market: Market type ("cn" for A-share, "hk" for H-share)

    Returns:
        Normalized code with exchange suffix (e.g., "600519.SH")

    Raises:
        ValueError: If code format is invalid
    """
    import re

    # Remove whitespace and convert to uppercase
    code = code.strip().upper()

    # If already has exchange suffix, validate and return
    if re.match(r"^\d{6}\.(SH|SZ|HK)$", code):
        return code

    # Validate 6-digit code without suffix
    if not re.match(r"^\d{6}$", code):
        raise ValueError(
            f"Invalid stock code format: {code}. Expected 6 digits optionally followed by .SH/.SZ/.HK"
        )

    # Auto-detect exchange for A-share
    if market in ["cn", "auto"]:
        first_digit = code[0]
        first_three = code[:3]

        # Shanghai Stock Exchange
        if first_three in ["600", "601", "603", "688"]:
            return f"{code}.SH"
        elif first_digit == "6":
            return f"{code}.SH"

        # Shenzhen Stock Exchange
        elif first_three in ["000", "001", "002", "003", "300", "301"]:
            return f"{code}.SZ"
        elif first_digit in ["0", "3"]:
            return f"{code}.SZ"

    # H-share (Hong Kong)
    if market == "hk":
        return f"{code}.HK"

    # Default to Shanghai if ambiguous
    return f"{code}.SH"


class StockSearchError(Exception):
    """股票搜索错误"""

    pass


class StockSearchService:
    """
    统一股票搜索服务
    支持多市场和多数据源
    """

    def __init__(self):
        """
        初始化股票搜索服务
        """
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "MyStocks/1.0"})
        self.akshare_available = AKSHARE_AVAILABLE

    def _make_request(self, endpoint: str, params: Dict = None) -> Dict:
        """
        发起 API 请求

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            Dict: API 响应数据

        Raises:
            FinnhubAPIError: API 请求失败
        """
        url = f"{self.base_url}/{endpoint}"
        request_params = params or {}
        request_params["token"] = self.api_key

        try:
            response = self.session.get(url, params=request_params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise FinnhubAPIError(f"API request failed: {e}")
        except json.JSONDecodeError as e:
            raise FinnhubAPIError(f"Failed to parse API response: {e}")

    @lru_cache(maxsize=1000)
    def search_stocks(self, query: str) -> List[Dict]:
        """
        搜索股票（带缓存）

        Args:
            query: 搜索关键词

        Returns:
            List[Dict]: 搜索结果列表，每个元素包含股票信息
        """
        try:
            data = self._make_request("search", {"q": query})

            # 提取相关股票信息
            results = []
            for item in data.get("result", [])[:20]:  # 限制返回前20个结果
                stock_info = {
                    "symbol": item.get("symbol"),
                    "description": item.get("description"),
                    "displaySymbol": item.get("displaySymbol"),
                    "type": item.get("type"),
                    "exchange": item.get("exchange"),
                }
                results.append(stock_info)

            return results
        except FinnhubAPIError as e:
            print(f"搜索股票时发生错误: {e}")
            return []

    def get_stock_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取股票实时报价

        Args:
            symbol: 股票代码

        Returns:
            Optional[Dict]: 报价信息
        """
        try:
            data = self._make_request("quote", {"symbol": symbol})

            if not data or data.get("c") is None:
                return None

            return {
                "current": data.get("c"),  # 当前价格
                "change": data.get("d"),  # 变化量
                "percent_change": data.get("dp"),  # 变化百分比
                "high": data.get("h"),  # 最高价
                "low": data.get("l"),  # 最低价
                "open": data.get("o"),  # 开盘价
                "previous_close": data.get("pc"),  # 前收盘价
                "timestamp": data.get("t"),  # 时间戳
            }
        except FinnhubAPIError as e:
            print(f"获取股票报价时发生错误: {e}")
            return None

    def get_company_profile(self, symbol: str) -> Optional[Dict]:
        """
        获取公司基本信息

        Args:
            symbol: 股票代码

        Returns:
            Optional[Dict]: 公司信息
        """
        try:
            data = self._make_request("stock/profile2", {"symbol": symbol})

            if not data:
                return None

            return {
                "country": data.get("country"),
                "currency": data.get("currency"),
                "exchange": data.get("exchange"),
                "ipo": data.get("ipo"),
                "market_cap": data.get("marketCapitalization"),
                "name": data.get("name"),
                "phone": data.get("phone"),
                "share_outstanding": data.get("shareOutstanding"),
                "ticker": data.get("ticker"),
                "weburl": data.get("weburl"),
                "logo": data.get("logo"),
                "industry": data.get("finnhubIndustry"),
            }
        except FinnhubAPIError as e:
            print(f"获取公司信息时发生错误: {e}")
            return None

    def get_company_news(
        self, symbol: str, from_date: str = None, to_date: str = None
    ) -> List[Dict]:
        """
        获取公司新闻

        Args:
            symbol: 股票代码
            from_date: 开始日期 (YYYY-MM-DD)，默认为7天前
            to_date: 结束日期 (YYYY-MM-DD)，默认为今天

        Returns:
            List[Dict]: 新闻列表，每个元素包含新闻信息
        """
        # 设置默认日期范围（最近7天）
        if not to_date:
            to_date = datetime.now().strftime("%Y-%m-%d")
        if not from_date:
            from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        try:
            data = self._make_request(
                "company-news", {"symbol": symbol, "from": from_date, "to": to_date}
            )

            # 提取相关新闻信息
            news_list = []
            for item in data[:50]:  # 限制返回前50条新闻
                news_info = {
                    "headline": item.get("headline"),
                    "summary": item.get("summary"),
                    "source": item.get("source"),
                    "datetime": item.get("datetime"),
                    "url": item.get("url"),
                    "image": item.get("image"),
                    "related": item.get("related"),
                    "category": item.get("category"),
                }
                news_list.append(news_info)

            return news_list
        except FinnhubAPIError as e:
            print(f"获取公司新闻时发生错误: {e}")
            return []

    def get_market_news(self, category: str = "general") -> List[Dict]:
        """
        获取市场新闻

        Args:
            category: 新闻类别 (general, forex, crypto, merger)

        Returns:
            List[Dict]: 新闻列表
        """
        try:
            data = self._make_request("news", {"category": category})

            # 提取新闻信息
            news_list = []
            for item in data[:30]:  # 限制返回前30条新闻
                news_info = {
                    "headline": item.get("headline"),
                    "summary": item.get("summary"),
                    "source": item.get("source"),
                    "datetime": item.get("datetime"),
                    "url": item.get("url"),
                    "image": item.get("image"),
                    "category": item.get("category"),
                }
                news_list.append(news_info)

            return news_list
        except FinnhubAPIError as e:
            print(f"获取市场新闻时发生错误: {e}")
            return []

    def get_recommendation_trends(self, symbol: str) -> List[Dict]:
        """
        获取分析师推荐趋势

        Args:
            symbol: 股票代码

        Returns:
            List[Dict]: 推荐趋势列表
        """
        try:
            data = self._make_request("stock/recommendation", {"symbol": symbol})

            return [
                {
                    "period": item.get("period"),
                    "strong_buy": item.get("strongBuy"),
                    "buy": item.get("buy"),
                    "hold": item.get("hold"),
                    "sell": item.get("sell"),
                    "strong_sell": item.get("strongSell"),
                }
                for item in data
            ]
        except FinnhubAPIError as e:
            print(f"获取推荐趋势时发生错误: {e}")
            return []

    def clear_cache(self):
        """清除搜索缓存"""
        if hasattr(self, "search_a_stocks"):
            self.search_a_stocks.cache_clear()
        if hasattr(self, "search_hk_stocks"):
            self.search_hk_stocks.cache_clear()

    # ========== A股搜索功能 (AKShare) ==========

    @lru_cache(maxsize=1000)
    def search_a_stocks(self, query: str) -> List[Dict]:
        """
        搜索 A 股股票（带缓存）

        Args:
            query: 搜索关键词（股票代码或名称）

        Returns:
            List[Dict]: 搜索结果列表
        """
        if not self.akshare_available:
            print("A股搜索失败: AKShare 未安装")
            return []

        try:
            # 获取所有 A 股股票列表
            stock_info_df = ak.stock_info_a_code_name()

            # 搜索匹配的股票
            query_upper = query.upper()
            matched_stocks = stock_info_df[
                (stock_info_df["code"].str.contains(query_upper, case=False))
                | (stock_info_df["name"].str.contains(query, case=False))
            ]

            # 转换为列表格式
            results = []
            for _, row in matched_stocks.head(20).iterrows():  # 限制返回前20个结果
                stock_info = {
                    "symbol": row["code"],
                    "description": row["name"],
                    "displaySymbol": row["code"],
                    "type": "A股",
                    "exchange": self._get_a_stock_exchange(row["code"]),
                    "market": "CN",
                }
                results.append(stock_info)

            return results
        except Exception as e:
            print(f"搜索 A 股时发生错误: {e}")
            return []

    def _get_a_stock_exchange(self, code: str) -> str:
        """
        根据股票代码判断交易所

        Args:
            code: 股票代码

        Returns:
            str: 交易所名称
        """
        if code.startswith("6"):
            return "上海证券交易所"
        elif code.startswith("0") or code.startswith("3"):
            return "深圳证券交易所"
        elif code.startswith("8") or code.startswith("4"):
            return "北京证券交易所"
        else:
            return "未知"

    # ========== H股(港股)搜索功能 (AKShare) ==========

    @lru_cache(maxsize=1000)
    def search_hk_stocks(self, query: str) -> List[Dict]:
        """
        搜索 H 股（港股）股票（带缓存）

        Args:
            query: 搜索关键词（股票代码或名称）

        Returns:
            List[Dict]: 搜索结果列表
        """
        if not self.akshare_available:
            print("港股搜索失败: AKShare 未安装")
            return []

        try:
            # 获取所有港股股票列表
            hk_stock_df = ak.stock_hk_spot_em()

            # 搜索匹配的股票
            query_upper = query.upper()
            matched_stocks = hk_stock_df[
                (hk_stock_df["代码"].astype(str).str.contains(query_upper, case=False))
                | (hk_stock_df["名称"].str.contains(query, case=False))
            ]

            # 转换为列表格式
            results = []
            for _, row in matched_stocks.head(20).iterrows():  # 限制返回前20个结果
                stock_info = {
                    "symbol": str(row["代码"]),
                    "description": row["名称"],
                    "displaySymbol": str(row["代码"]),
                    "type": "H股",
                    "exchange": "香港证券交易所",
                    "market": "HK",
                }
                results.append(stock_info)

            return results
        except Exception as e:
            print(f"搜索港股时发生错误: {e}")
            return []

    def get_hk_stock_realtime(self, symbol: str) -> Optional[Dict]:
        """
        获取港股实时行情

        Args:
            symbol: 股票代码

        Returns:
            Optional[Dict]: 实时行情信息
        """
        if not self.akshare_available:
            print("获取港股行情失败: AKShare 未安装")
            return None

        try:
            # 获取实时行情
            df = ak.stock_hk_spot_em()
            stock_data = df[df["代码"].astype(str) == symbol]

            if stock_data.empty:
                return None

            row = stock_data.iloc[0]
            return {
                "symbol": symbol,
                "name": row["名称"],
                "current": float(row["最新价"]),
                "change": float(row["涨跌额"]),
                "percent_change": float(row["涨跌幅"]),
                "open": float(row["今开"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "previous_close": float(row["昨收"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]),
                "timestamp": datetime.now().timestamp(),
            }
        except Exception as e:
            print(f"获取港股实时行情时发生错误: {e}")
            return None

    def get_hk_stock_news(self, symbol: str = None) -> List[Dict]:
        """
        获取港股新闻

        Args:
            symbol: 股票代码（可选）

        Returns:
            List[Dict]: 新闻列表
        """
        if not self.akshare_available:
            print("获取港股新闻失败: AKShare 未安装")
            return []

        try:
            # 由于 AKShare 港股新闻接口有限，这里返回空列表
            # 实际使用时可以接入港股新闻API
            return []
        except Exception as e:
            print(f"获取港股新闻时发生错误: {e}")
            return []

    def get_a_stock_realtime(self, symbol: str) -> Optional[Dict]:
        """
        获取 A 股实时行情

        Args:
            symbol: 股票代码（支持 6 位数字或带交易所后缀）

        Returns:
            Optional[Dict]: 实时行情信息
        """
        if not self.akshare_available:
            print("获取 A 股行情失败: AKShare 未安装")
            return None

        try:
            # Normalize stock code (add exchange suffix if missing)
            try:
                normalized_code = normalize_stock_code(symbol, market="cn")
            except ValueError as e:
                print(f"股票代码格式错误: {e}")
                return None

            # Extract numeric code for akshare query (akshare uses 6-digit codes without suffix)
            code_for_query = normalized_code.split(".")[0]

            # 获取实时行情
            df = ak.stock_zh_a_spot_em()
            stock_data = df[df["代码"] == code_for_query]

            if stock_data.empty:
                return None

            row = stock_data.iloc[0]
            return {
                "symbol": normalized_code,  # Return normalized code with exchange suffix
                "name": row["名称"],
                "current": float(row["最新价"]),
                "change": float(row["涨跌额"]),
                "percent_change": float(row["涨跌幅"]),
                "open": float(row["今开"]),
                "high": float(row["最高"]),
                "low": float(row["最低"]),
                "previous_close": float(row["昨收"]),
                "volume": float(row["成交量"]),
                "amount": float(row["成交额"]),
                "turnover_rate": float(row["换手率"]) if "换手率" in row else None,
                "timestamp": datetime.now().timestamp(),
            }
        except Exception as e:
            print(f"获取 A 股实时行情时发生错误: {e}")
            return None

    def get_a_stock_news(self, symbol: str = None, days: int = 7) -> List[Dict]:
        """
        获取 A 股新闻（东方财富）

        Args:
            symbol: 股票代码（可选）
            days: 获取最近几天的新闻

        Returns:
            List[Dict]: 新闻列表
        """
        if not self.akshare_available:
            print("获取 A 股新闻失败: AKShare 未安装")
            return []

        try:
            # 获取东方财富新闻
            if symbol:
                # 获取个股新闻
                try:
                    news_df = ak.stock_news_em(symbol=symbol)
                except:
                    print(f"无法获取股票 {symbol} 的新闻")
                    return []
            else:
                # 获取市场新闻
                news_df = ak.stock_news_em()

            # 转换为列表格式
            news_list = []
            for _, row in news_df.head(30).iterrows():  # 限制返回前30条
                news_info = {
                    "headline": row.get("新闻标题", ""),
                    "summary": (
                        row.get("新闻内容", "")[:200] if "新闻内容" in row else ""
                    ),
                    "source": row.get("新闻来源", "东方财富"),
                    "datetime": parse_datetime_to_timestamp(row.get("发布时间")),
                    "url": row.get("新闻链接", ""),
                    "category": "A股新闻",
                }
                news_list.append(news_info)

            return news_list
        except Exception as e:
            print(f"获取 A 股新闻时发生错误: {e}")
            return []

    def get_a_stock_kline(
        self,
        symbol: str,
        period: str = "daily",
        adjust: str = "qfq",
        start_date: str = None,
        end_date: str = None,
    ) -> Optional[Dict]:
        """
        获取 A 股 K 线数据（日线/周线/月线）

        Args:
            symbol: 股票代码（支持 6 位数字或带交易所后缀）
            period: 时间周期 ("daily", "weekly", "monthly")
            adjust: 复权类型 ("qfq"=前复权, "hfq"=后复权, ""=不复权)
            start_date: 开始日期 (YYYY-MM-DD 格式)
            end_date: 结束日期 (YYYY-MM-DD 格式)

        Returns:
            Optional[Dict]: K线数据 {stock_code, stock_name, period, adjust, data[], count}
        """
        if not self.akshare_available:
            print("获取 K 线数据失败: AKShare 未安装")
            return None

        try:
            # Normalize stock code
            try:
                normalized_code = normalize_stock_code(symbol, market="cn")
            except ValueError as e:
                print(f"股票代码格式错误: {e}")
                return None

            # Validate period
            if period not in ["daily", "weekly", "monthly"]:
                print(f"无效的时间周期: {period}。支持的值: daily, weekly, monthly")
                return None

            # Validate adjust
            if adjust not in ["qfq", "hfq", ""]:
                print(f"无效的复权类型: {adjust}。支持的值: qfq, hfq, 或空字符串")
                return None

            # Extract numeric code for akshare (remove exchange suffix)
            code_for_query = normalized_code.split(".")[0]

            # Format dates for akshare (YYYYMMDD format)
            if start_date:
                start_date_formatted = start_date.replace("-", "")
            else:
                # Default to 60 days ago
                from datetime import datetime, timedelta

                start_date_formatted = (datetime.now() - timedelta(days=90)).strftime(
                    "%Y%m%d"
                )

            if end_date:
                end_date_formatted = end_date.replace("-", "")
            else:
                from datetime import datetime

                end_date_formatted = datetime.now().strftime("%Y%m%d")

            # Get K-line data from AKShare
            df = ak.stock_zh_a_hist(
                symbol=code_for_query,
                period=period,
                start_date=start_date_formatted,
                end_date=end_date_formatted,
                adjust=adjust,
            )

            if df.empty:
                print(f"股票代码 {code_for_query} 不存在或暂无K线数据")
                return None

            # Get stock name from first row
            stock_name = (
                df["股票名称"].iloc[0] if "股票名称" in df.columns else code_for_query
            )

            # Convert DataFrame to list of data points
            data_points = []
            previous_close = None

            for idx, row in df.iterrows():
                date_str = str(row["日期"])
                # Parse date and create timestamp
                from datetime import datetime

                if len(date_str) == 8:  # YYYYMMDD format
                    date_obj = datetime.strptime(date_str, "%Y%m%d")
                else:  # YYYY-MM-DD format
                    date_obj = datetime.strptime(date_str.split(" ")[0], "%Y-%m-%d")

                date_formatted = date_obj.strftime("%Y-%m-%d")
                timestamp = int(date_obj.timestamp())

                open_price = float(row["开盘"])
                high_price = float(row["最高"])
                low_price = float(row["最低"])
                close_price = float(row["收盘"])
                volume = int(row["成交量"]) if "成交量" in row else 0
                amount = float(row["成交额"]) if "成交额" in row else 0.0

                # Calculate amplitude
                if previous_close and previous_close > 0:
                    amplitude = ((high_price - low_price) / previous_close) * 100
                    change_percent = (
                        (close_price - previous_close) / previous_close
                    ) * 100
                else:
                    amplitude = 0.0
                    change_percent = 0.0

                data_point = {
                    "date": date_formatted,
                    "timestamp": timestamp,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": volume,
                    "amount": round(amount, 2),
                    "amplitude": round(amplitude, 2),
                    "change_percent": round(change_percent, 2),
                }
                data_points.append(data_point)
                previous_close = close_price

            # Reverse to get newest first
            data_points.reverse()

            return {
                "stock_code": normalized_code,
                "stock_name": stock_name,
                "period": period,
                "adjust": adjust,
                "data": data_points,
                "count": len(data_points),
            }

        except Exception as e:
            print(f"获取 K 线数据时发生错误: {e}")
            import traceback

            traceback.print_exc()
            return None

    # ========== 统一搜索接口 ==========

    def unified_search(self, query: str, market: str = "auto") -> List[Dict]:
        """
        统一搜索接口，根据市场类型自动选择数据源

        Args:
            query: 搜索关键词
            market: 市场类型 ("auto", "cn", "hk")

        Returns:
            List[Dict]: 搜索结果列表
        """
        results = []

        # 自动检测市场类型
        if market == "auto":
            # 如果查询包含中文，优先搜索 A 股
            if any("\u4e00" <= char <= "\u9fff" for char in query):
                market = "cn"
            # 如果是纯数字且长度为6，可能是 A 股代码
            elif query.isdigit() and len(query) == 6:
                market = "cn"
            # 如果是纯数字且长度为5（港股代码通常5位）
            elif query.isdigit() and len(query) == 5:
                market = "hk"
            # 否则搜索 A 股和港股
            else:
                market = "all"

        # 根据市场类型搜索
        if market == "cn" and self.akshare_available:
            results = self.search_a_stocks(query)
        elif market == "hk" and self.akshare_available:
            results = self.search_hk_stocks(query)
        elif market == "all" and self.akshare_available:
            # 搜索 A 股和港股
            results.extend(self.search_a_stocks(query))
            results.extend(self.search_hk_stocks(query))
        else:
            # 尝试两个市场都搜索
            if self.akshare_available:
                results.extend(self.search_a_stocks(query))
                results.extend(self.search_hk_stocks(query))

        return results


# 创建全局实例
_stock_search_service = None


def get_stock_search_service() -> StockSearchService:
    """
    获取股票搜索服务实例（单例模式）

    Returns:
        StockSearchService: 股票搜索服务实例
    """
    global _stock_search_service
    if _stock_search_service is None:
        _stock_search_service = StockSearchService()
    return _stock_search_service
