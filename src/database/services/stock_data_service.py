"""
# 功能：股票数据服务
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：专门处理股票相关数据的服务
"""

from datetime import datetime
from typing import Dict, List, Optional

from loguru import logger

from .base_database_service import BaseDatabaseService


class StockDataService(BaseDatabaseService):
    """
    股票数据服务

    专门处理股票列表、详情、历史数据等
    """

    def __init__(self):
        super().__init__()
        logger.info("股票数据服务初始化完成")

    def get_stock_list(self, params: Optional[Dict] = None) -> Dict:
        """获取股票列表（支持按交易所筛选，支持分页）

        Args:
            params: Dict - 查询参数：
                    exchange: Optional[str] - 交易所筛选（sh=上交所，sz=深交所）
                    limit: int - 每页数量，默认20
                    offset: int - 偏移量，默认0

        Returns:
            Dict: 包含股票列表和分页信息的结果
        """
        try:
            # 默认参数
            params = params or {}
            exchange = params.get("exchange")
            limit, offset = self._validate_pagination_params(params.get("limit"), params.get("offset"))

            # 构建查询条件
            filters = {}
            if exchange:
                # 根据交易所筛选
                if exchange == "sh":
                    filters["market"] = "上交所"
                elif exchange == "sz":
                    filters["market"] = "深交所"

            # 查询股票基本信息表
            df = self._execute_query(table_name="symbols_info", filters=filters)

            # 获取总数量
            total_count = self._count_records("symbols_info", filters)

            # 应用分页
            paginated_df = self._apply_pagination(df, limit, offset)

            # 转换为与Mock数据一致的格式
            result = []
            for _, row in paginated_df.iterrows():
                result.append(
                    {
                        "code": row.get("symbol", ""),
                        "name": row.get("name", ""),
                        "market": row.get("market", ""),
                        "industry": row.get("industry", ""),
                        "sector": row.get("sector", ""),
                        "area": row.get("area", ""),
                        "pe": row.get("pe", 0),
                        "outstanding": row.get("outstanding", 0),
                        "totals": row.get("totals", 0),
                        "total_assets": row.get("total_assets", 0),
                        "liquid_assets": row.get("liquid_assets", 0),
                        "fixed_assets": row.get("fixed_assets", 0),
                        "reserved": row.get("reserved", 0),
                        "reserved_per_share": row.get("reserved_per_share", 0),
                        "eps": row.get("eps", 0),
                        "bvps": row.get("bvps", 0),
                        "pb": row.get("pb", 0),
                        "timeToMarket": row.get("time_to_market", ""),
                        "undp": row.get("undp", 0),
                        "per_undp": row.get("per_undp", 0),
                        "rev_yoy": row.get("rev_yoy", 0),
                        "profit_yoy": row.get("profit_yoy", 0),
                        "gpr": row.get("gpr", 0),
                        "npr": row.get("npr", 0),
                        "nav": row.get("nav", 0),
                        "nav_ps": row.get("nav_ps", 0),
                        "bv": row.get("bv", 0),
                        "per_bv": row.get("per_bv", 0),
                    }
                )

            return self._build_success_response(
                data=result,
                operation="get_stock_list",
                meta={
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "exchange": exchange,
                },
            )

        except Exception as e:
            return self._handle_database_error(e, "获取股票列表")

    def get_stock_detail(self, stock_code: str) -> Dict:
        """获取股票详细信息

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 股票详细信息
        """
        try:
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # 查询股票详细信息
            df = self._execute_query(table_name="symbols_info", filters={"symbol": stock_code})

            if df.empty:
                return self._handle_database_error(ValueError(f"未找到股票 {stock_code} 的信息"), "获取股票详情")

            row = df.iloc[0]
            result = {
                "code": row.get("symbol", ""),
                "name": row.get("name", ""),
                "market": row.get("market", ""),
                "industry": row.get("industry", ""),
                "sector": row.get("sector", ""),
                "area": row.get("area", ""),
                "pe": row.get("pe", 0),
                "outstanding": row.get("outstanding", 0),
                "totals": row.get("totals", 0),
                "total_assets": row.get("total_assets", 0),
                "liquid_assets": row.get("liquid_assets", 0),
                "fixed_assets": row.get("fixed_assets", 0),
                "reserved": row.get("reserved", 0),
                "reserved_per_share": row.get("reserved_per_share", 0),
                "eps": row.get("eps", 0),
                "bvps": row.get("bvps", 0),
                "pb": row.get("pb", 0),
                "timeToMarket": row.get("time_to_market", ""),
                "undp": row.get("undp", 0),
                "per_undp": row.get("per_undp", 0),
                "rev_yoy": row.get("rev_yoy", 0),
                "profit_yoy": row.get("profit_yoy", 0),
                "gpr": row.get("gpr", 0),
                "npr": row.get("npr", 0),
                "nav": row.get("nav", 0),
                "nav_ps": row.get("nav_ps", 0),
                "bv": row.get("bv", 0),
                "per_bv": row.get("per_bv", 0),
            }

            return self._build_success_response(data=result, operation="get_stock_detail")

        except Exception as e:
            return self._handle_database_error(e, "获取股票详情")

    def get_realtime_quotes(self, symbols: List[str]) -> Dict:
        """获取实时行情

        Args:
            symbols: List[str] - 股票代码列表

        Returns:
            Dict: 实时行情数据
        """
        try:
            if not symbols:
                raise ValueError("股票代码列表不能为空")

            # 查询实时行情数据
            "','".join(symbols)
            df = self._execute_query(table_name="realtime_quotes", filters={"symbol": symbols})

            result = []
            for _, row in df.iterrows():
                result.append(
                    {
                        "code": row.get("symbol", ""),
                        "name": row.get("name", ""),
                        "price_start": row.get("open", 0),
                        "price_end": row.get("close", 0),
                        "price_high": row.get("high", 0),
                        "price_low": row.get("low", 0),
                        "volume": row.get("volume", 0),
                        "amount": row.get("amount", 0),
                        "change_percent": row.get("change_percent", 0),
                        "change_amount": row.get("change_amount", 0),
                        "timestamp": row.get("timestamp", datetime.now().isoformat()),
                    }
                )

            return self._build_success_response(data=result, operation="get_realtime_quotes")

        except Exception as e:
            return self._handle_database_error(e, "获取实时行情")

    def get_stock_history(self, params: Optional[Dict] = None) -> Dict:
        """获取股票历史数据

        Args:
            params: Dict - 查询参数：
                    symbol: str - 股票代码
                    start_date: str - 开始日期
                    end_date: str - 结束日期
                    limit: int - 每页数量，默认100
                    offset: int - 偏移量，默认0

        Returns:
            Dict: 历史数据和分页信息
        """
        try:
            params = params or {}
            symbol = params.get("symbol")
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            limit, offset = self._validate_pagination_params(params.get("limit", 100), params.get("offset"))

            if not symbol:
                raise ValueError("股票代码不能为空")

            # 构建查询条件
            filters = {"symbol": symbol}
            if start_date and end_date:
                filters["trade_date"] = [start_date, end_date]
            elif start_date:
                filters["trade_date"] = start_date
            elif end_date:
                filters["trade_date"] = end_date

            # 查询历史数据
            df = self._execute_query(
                table_name="stock_daily_data",
                filters=filters,
                order_by="trade_date DESC",
            )

            # 获取总数量
            total_count = self._count_records("stock_daily_data", filters)

            # 应用分页
            paginated_df = self._apply_pagination(df, limit, offset)

            # 转换数据格式
            result = []
            for _, row in paginated_df.iterrows():
                result.append(
                    {
                        "symbol": row.get("symbol", ""),
                        "trade_date": row.get("trade_date", ""),
                        "open": row.get("open", 0),
                        "high": row.get("high", 0),
                        "low": row.get("low", 0),
                        "close": row.get("close", 0),
                        "volume": row.get("volume", 0),
                        "amount": row.get("amount", 0),
                        "change_percent": row.get("change_percent", 0),
                        "change_amount": row.get("change_amount", 0),
                    }
                )

            return self._build_success_response(
                data=result,
                operation="get_stock_history",
                meta={
                    "total": total_count,
                    "limit": limit,
                    "offset": offset,
                    "symbol": symbol,
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )

        except Exception as e:
            return self._handle_database_error(e, "获取股票历史数据")

    def get_batch_indicators(self, symbols: List[str]) -> Dict:
        """批量获取股票指标

        Args:
            symbols: List[str] - 股票代码列表

        Returns:
            Dict: 批量指标数据
        """
        try:
            if not symbols:
                raise ValueError("股票代码列表不能为空")

            # 限制批量查询数量
            if len(symbols) > 100:
                symbols = symbols[:100]

            # 查询股票指标
            df = self._execute_query(table_name="stock_indicators", filters={"symbol": symbols})

            # 按股票代码分组数据
            result = {}
            for _, row in df.iterrows():
                symbol = row.get("symbol", "")
                if symbol not in result:
                    result[symbol] = []

                result[symbol].append(
                    {
                        "indicator_name": row.get("indicator_name", ""),
                        "indicator_value": row.get("indicator_value", 0),
                        "calculation_date": row.get("calculation_date", ""),
                        "indicator_type": row.get("indicator_type", ""),
                    }
                )

            return self._build_success_response(data=result, operation="get_batch_indicators")

        except Exception as e:
            return self._handle_database_error(e, "批量获取股票指标")
