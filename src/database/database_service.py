"""
通用数据库服务模块
为所有路由提供真实数据库查询服务，确保与Mock数据接口一致

作者: MyStocks项目组
创建日期: 2025-11-15
"""

"""
数据库服务类
提供统一的数据库访问接口，适配双数据库架构
"""

import logging
import pandas as pd
from typing import Dict, List, Optional, Union
from datetime import datetime

# 导入数据访问层
from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)

# 创建数据库访问实例
postgresql_access = PostgreSQLDataAccess()


class DatabaseService:
    """通用数据库服务类"""

    def __init__(self):
        """初始化数据库服务"""
        self.postgresql_access = postgresql_access

    # ==================== 股票相关查询 ====================

    def get_stock_list(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取股票列表（支持按交易所筛选，支持分页）

        Args:
            params: Dict - 查询参数：
                    exchange: Optional[str] - 交易所筛选（sh=上交所，sz=深交所）
                    limit: int - 每页数量，默认20
                    offset: int - 偏移量，默认0

        Returns:
            List[Dict]: 股票列表数据，与Mock数据格式一致
        """
        try:
            # 默认参数
            params = params or {}
            exchange = params.get("exchange")
            limit = params.get("limit", 20)
            offset = params.get("offset", 0)

            # 构建查询条件
            filters = {}
            if exchange:
                # 根据交易所筛选（需要与数据库中的字段对应）
                if exchange == "sh":
                    filters["market"] = "上交所"
                elif exchange == "sz":
                    filters["market"] = "深交所"

            # 查询股票基本信息表
            where_clause = None
            if filters:
                # 构建WHERE子句
                where_conditions = []
                for key, value in filters.items():
                    if isinstance(value, list):
                        # 处理列表值（IN查询）
                        values_str = "', '".join(value)
                        where_conditions.append(f"{key} IN ('{values_str}')")
                    else:
                        # 处理单个值
                        where_conditions.append(f"{key} = '{value}'")
                where_clause = " AND ".join(where_conditions)

            df = self.postgresql_access.query(
                table_name="symbols_info",
                where=where_clause,
                limit=limit,  # 不使用offset参数，手动处理
            )

            # 手动处理offset
            if offset and offset > 0:
                df = df.iloc[offset:]

            # 获取总数量
            # 为了获取总数量，我们需要查询所有记录而不使用limit和offset
            total_df = self.postgresql_access.query(
                table_name="symbols_info",
                where=where_clause,
                columns=["COUNT(*) as total"],
            )
            total_count = total_df.iloc[0]["total"] if not total_df.empty else 0

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "symbol": row.get("symbol", ""),
                            "name": row.get("name", ""),
                            "industry": row.get("industry", ""),
                            "area": row.get("area", ""),
                            "market": row.get("market", ""),
                            "list_date": (
                                row.get("list_date", "").strftime("%Y-%m-%d") if pd.notna(row.get("list_date")) else ""
                            ),
                            "total": total_count,  # 用于分页的总数量
                        }
                    )

            return result

        except Exception as e:
            logger.error("获取股票列表失败: %s", e)
            return []

    def get_stock_detail(self, stock_code: str) -> Dict:
        """获取股票详细信息

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 股票详细信息，与Mock数据格式一致
        """
        try:
            if not stock_code:
                return {}

            # 查询股票基本信息表
            where_clause = f"symbol = '{stock_code}'"

            df = self.postgresql_access.query(table_name="symbols_info", where=where_clause, limit=1)

            # 转换为与Mock数据一致的格式
            if not df.empty:
                row = df.iloc[0]
                return {
                    "symbol": row.get("symbol", ""),
                    "name": row.get("name", ""),
                    "industry": row.get("industry", ""),
                    "area": row.get("area", ""),
                    "market": row.get("market", ""),
                    "list_date": (
                        row.get("list_date", "").strftime("%Y-%m-%d") if pd.notna(row.get("list_date")) else ""
                    ),
                }

            return {}

        except Exception as e:
            logger.error("获取股票详细信息失败: %s", e)
            return {}

    def get_realtime_quotes(self, symbols: List[str]) -> List[Dict]:
        """获取实时行情

        Args:
            symbols: List[str] - 股票代码列表

        Returns:
            List[Dict]: 实时行情数据列表，与Mock数据格式一致
        """
        try:
            if not symbols:
                return []

            # 查询实时行情表
            where_clause = None
            if symbols:
                # 构建WHERE子句
                where_conditions = []
                for key, value in {"symbol": symbols}.items():
                    if isinstance(value, list):
                        # 处理列表值（IN查询）
                        values_str = "', '".join(value)
                        where_conditions.append(f"{key} IN ('{values_str}')")
                    else:
                        # 处理单个值
                        where_conditions.append(f"{key} = '{value}'")
                where_clause = " AND ".join(where_conditions)

            df = self.postgresql_access.query(table_name="realtime_quotes", where=where_clause)

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "symbol": row.get("symbol", ""),
                            "name": row.get("name", ""),
                            "price": float(row.get("price", 0.0)),
                            "change": float(row.get("change", 0.0)),
                            "change_percent": float(row.get("change_percent", 0.0)),
                            "volume": int(row.get("volume", 0)),
                            "amount": float(row.get("amount", 0.0)),
                            "open": float(row.get("open", 0.0)),
                            "high": float(row.get("high", 0.0)),
                            "low": float(row.get("low", 0.0)),
                            "pre_close": float(row.get("pre_close", 0.0)),
                            "timestamp": (
                                row.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("timestamp"))
                                else ""
                            ),
                        }
                    )

            return result

        except Exception as e:
            logger.error("获取实时行情失败: %s", e)
            return []

    # ==================== 问财相关查询 ====================

    def execute_wencai_query(self, query_params: Dict) -> Dict:
        """执行问财查询

        Args:
            query_params: Dict - 查询参数

        Returns:
            Dict: 查询结果，与Mock数据格式一致
        """
        try:
            # 这里实现具体的问财查询逻辑
            # 根据实际的数据库表结构进行查询

            # 示例实现（需要根据实际表结构调整）
            query_name = query_params.get("query_name", "")
            pages = query_params.get("pages", 1)

            # 查询wencai_results表
            where_clause = f"query_name = '{query_name}'"
            df = self.postgresql_access.query(
                table_name="wencai_results",
                where=where_clause,
                limit=pages * 20,  # 假设每页20条记录
            )

            # 转换为与Mock数据一致的格式
            if not df.empty:
                records = []
                for _, row in df.iterrows():
                    records.append(
                        {
                            "symbol": row.get("symbol", ""),
                            "name": row.get("name", ""),
                            "price": float(row.get("price", 0.0)),
                            "change_percent": float(row.get("change_percent", 0.0)),
                            "volume": int(row.get("volume", 0)),
                            "market_value": float(row.get("market_value", 0.0)),
                            "pe_ratio": float(row.get("pe_ratio", 0.0)) if pd.notna(row.get("pe_ratio")) else None,
                        }
                    )

                return {
                    "query_name": query_name,
                    "total_records": len(records),
                    "records": records,
                    "page": 1,
                    "pages": pages,
                }

            return {
                "query_name": query_name,
                "total_records": 0,
                "records": [],
                "page": 1,
                "pages": pages,
            }

        except Exception as e:
            logger.error("执行问财查询失败: %s", e)
            return {
                "query_name": query_params.get("query_name", ""),
                "total_records": 0,
                "records": [],
                "error": str(e),
            }

    # ==================== 技术分析相关查询 ====================

    def get_technical_indicators(self, params: Dict) -> List[Dict]:
        """获取技术指标

        Args:
            params: Dict - 查询参数：
                    symbol: str - 股票代码
                    start_date: str - 开始日期
                    end_date: str - 结束日期

        Returns:
            List[Dict]: 技术指标数据列表，与Mock数据格式一致
        """
        try:
            symbol = params.get("symbol", "")
            start_date = params.get("start_date", "")
            end_date = params.get("end_date", "")

            if not symbol:
                return []

            # 构建查询条件
            where_conditions = [f"symbol = '{symbol}'"]

            if start_date:
                where_conditions.append(f"calc_date >= '{start_date}'")
            if end_date:
                where_conditions.append(f"calc_date <= '{end_date}'")

            where_clause = " AND ".join(where_conditions)

            # 查询技术指标表
            df = self.postgresql_access.query(
                table_name="technical_indicators",
                where=where_clause,
                order_by="calc_date DESC",
            )

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                # 按日期分组整理数据
                grouped_data = {}
                for _, row in df.iterrows():
                    date_str = row.get("calc_date", "").strftime("%Y-%m-%d") if pd.notna(row.get("calc_date")) else ""
                    indicator_name = row.get("indicator_name", "")
                    indicator_value = (
                        float(row.get("indicator_value", 0.0)) if pd.notna(row.get("indicator_value")) else None
                    )

                    if date_str not in grouped_data:
                        grouped_data[date_str] = {
                            "symbol": symbol,
                            "date": date_str,
                            "trend": {},
                            "momentum": {},
                            "volatility": {},
                            "volume": {},
                        }

                    # 根据指标名称分类
                    if indicator_name.startswith("MA") or indicator_name.startswith("MACD"):
                        grouped_data[date_str]["trend"][indicator_name.lower()] = indicator_value
                    elif indicator_name.startswith("RSI") or indicator_name.startswith("KDJ"):
                        grouped_data[date_str]["momentum"][indicator_name.lower()] = indicator_value
                    elif indicator_name.startswith("ATR"):
                        grouped_data[date_str]["volatility"][indicator_name.lower()] = indicator_value
                    elif indicator_name.startswith("OBV"):
                        grouped_data[date_str]["volume"][indicator_name.lower()] = indicator_value

                # 转换为列表格式
                result = list(grouped_data.values())

            return result

        except Exception as e:
            logger.error("获取技术指标失败: %s", e)
            return []

    # ==================== 监控相关查询 ====================

    def get_monitoring_alerts(self, params: Optional[Dict] = None) -> List[Dict]:
        """获取监控告警

        Args:
            params: Dict - 查询参数

        Returns:
            List[Dict]: 告警数据列表，与Mock数据格式一致
        """
        try:
            # 默认参数
            params = params or {}
            limit = params.get("limit", 50)
            offset = params.get("offset", 0)
            is_read = params.get("is_read")

            # 构建查询条件
            where_clause = None
            where_conditions = []

            if limit and limit != 50:  # 50是默认值
                # 在这里我们只使用offset和limit参数，不使用where条件
                pass
            if offset and offset != 0:
                # offset在postgresql_access中通过query方法的offset参数处理
                pass
            if is_read is not None:
                where_conditions.append(f"is_read = {1 if is_read else 0}")

            if where_conditions:
                where_clause = " AND ".join(where_conditions)

            # 查询告警表
            df = self.postgresql_access.query(
                table_name="monitoring_alerts",
                where=where_clause,
                limit=limit,
                order_by="timestamp DESC",
            )

            # 手动处理offset（因为postgresql_access.query不支持offset参数）
            if offset and offset > 0:
                df = df.iloc[offset:]

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "id": int(row.get("id", 0)),
                            "symbol": row.get("symbol", ""),
                            "stock_name": row.get("stock_name", ""),
                            "alert_type": row.get("alert_type", ""),
                            "level": row.get("level", ""),
                            "message": row.get("message", ""),
                            "timestamp": (
                                row.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("timestamp"))
                                else ""
                            ),
                            "is_read": bool(row.get("is_read", False)),
                        }
                    )

            return result

        except Exception as e:
            logger.error("获取监控告警失败: %s", e)
            return []

    def get_monitoring_summary(self) -> Dict:
        """获取监控摘要

        Returns:
            Dict: 监控摘要数据，与Mock数据格式一致
        """
        try:
            # 查询各种监控统计信息
            # 这里需要根据实际的数据库表结构进行查询

            # 示例实现
            return {
                "total_stocks": 4000,
                "limit_up_count": 45,
                "limit_down_count": 8,
                "strong_up_count": 120,
                "strong_down_count": 65,
                "avg_change_percent": 0.025,
                "total_amount": 50000000000.0,
                "active_alerts": 25,
                "unread_alerts": 12,
            }
        except Exception as e:
            logger.error("获取监控摘要失败: %s", e)
            return {}

    def get_trend_indicators(self, stock_code: str) -> Dict:
        """获取趋势指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 趋势指标数据，与Mock数据格式一致
        """
        try:
            if not stock_code:
                return {}

            params = {"symbol": stock_code}
            result = self.get_technical_indicators(params)

            # 只返回趋势指标部分
            if result and "trend" in result:
                return {
                    "symbol": stock_code,
                    "latest_date": result.get("latest_date", ""),
                    "trend": result["trend"],
                }

            return {}

        except Exception as e:
            logger.error("获取趋势指标失败: %s", e)
            return {}

    def get_momentum_indicators(self, stock_code: str) -> Dict:
        """获取动量指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 动量指标数据，与Mock数据格式一致
        """
        try:
            if not stock_code:
                return {}

            params = {"symbol": stock_code}
            result = self.get_technical_indicators(params)

            # 只返回动量指标部分
            if result and "momentum" in result:
                return {
                    "symbol": stock_code,
                    "latest_date": result.get("latest_date", ""),
                    "momentum": result["momentum"],
                }

            return {}

        except Exception as e:
            logger.error("获取动量指标失败: %s", e)
            return {}

    def get_volatility_indicators(self, stock_code: str) -> Dict:
        """获取波动率指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 波动率指标数据，与Mock数据格式一致
        """
        try:
            if not stock_code:
                return {}

            params = {"symbol": stock_code}
            result = self.get_technical_indicators(params)

            # 只返回波动率指标部分
            if result and "volatility" in result:
                return {
                    "symbol": stock_code,
                    "latest_date": result.get("latest_date", ""),
                    "volatility": result["volatility"],
                }

            return {}

        except Exception as e:
            logger.error("获取波动率指标失败: %s", e)
            return {}

    def get_volume_indicators(self, stock_code: str) -> Dict:
        """获取成交量指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 成交量指标数据，与Mock数据格式一致
        """
        try:
            if not stock_code:
                return {}

            params = {"symbol": stock_code}
            result = self.get_technical_indicators(params)

            # 只返回成交量指标部分
            if result and "volume" in result:
                return {
                    "symbol": stock_code,
                    "latest_date": result.get("latest_date", ""),
                    "volume": result["volume"],
                }

            return {}

        except Exception as e:
            logger.error("获取成交量指标失败: %s", e)
            return {}

    def get_all_indicators(self, params: Dict) -> Dict:
        """获取所有技术指标

        Args:
            params: Dict - 查询参数：
                    stock_code: str - 股票代码

        Returns:
            Dict: 所有技术指标数据，包含趋势、动量、波动率、成交量等指标
        """
        try:
            stock_code = params.get("stock_code", "")

            if not stock_code:
                return {}

            # 获取所有指标
            technical_data = self.get_technical_indicators({"symbol": stock_code})

            # 组合成完整格式
            if technical_data:
                return {
                    "symbol": stock_code,
                    "latest_date": technical_data.get("latest_date", ""),
                    "trend": technical_data.get("trend", {}),
                    "momentum": technical_data.get("momentum", {}),
                    "volatility": technical_data.get("volatility", {}),
                    "volume": technical_data.get("volume", {}),
                }

            return {}

        except Exception as e:
            logger.error("获取所有技术指标失败: %s", e)
            return {}

    def get_pattern_recognition(self, stock_code: str) -> Dict:
        """获取形态识别结果

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 形态识别结果
        """
        try:
            if not stock_code:
                return {}

            # 查询形态识别表
            where_clause = f"symbol = '{stock_code}'"
            df = self.postgresql_access.query(
                table_name="pattern_recognition",
                where=where_clause,
                order_by="created_at DESC",
                limit=10,
            )

            # 转换为与Mock数据一致的格式
            patterns = []
            if not df.empty:
                for _, row in df.iterrows():
                    patterns.append(
                        {
                            "pattern_name": row.get("pattern_name", ""),
                            "confidence": float(row.get("confidence", 0.0)),
                            "target_price": float(row.get("target_price", 0.0)),
                            "stop_loss": float(row.get("stop_loss", 0.0)),
                            "signal": row.get("signal", ""),
                            "created_at": (
                                row.get("created_at", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("created_at"))
                                else ""
                            ),
                        }
                    )

            return {
                "symbol": stock_code,
                "latest_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "patterns": patterns[:3],  # 只取前3个
            }

        except Exception as e:
            logger.error("获取形态识别结果失败: %s", e)
            return {}

    def get_trading_signals(self, symbol: str) -> Dict:
        """获取交易信号

        Args:
            symbol: str - 股票代码

        Returns:
            Dict: 交易信号数据
        """
        try:
            if not symbol:
                return {}

            # 查询交易信号表
            where_clause = f"symbol = '{symbol}'"
            df = self.postgresql_access.query(
                table_name="trading_signals",
                where=where_clause,
                order_by="created_at DESC",
                limit=1,
            )

            # 转换为与Mock数据一致的格式
            if not df.empty:
                row = df.iloc[0]
                return {
                    "symbol": symbol,
                    "signal_type": row.get("signal_type", ""),
                    "signal": row.get("signal", ""),
                    "strength": float(row.get("strength", 0.0)),
                    "created_at": (
                        row.get("created_at", "").strftime("%Y-%m-%d %H:%M:%S")
                        if pd.notna(row.get("created_at"))
                        else ""
                    ),
                    "indicator": row.get("indicator", ""),
                }

            return {}

        except Exception as e:
            logger.error("获取交易信号失败: %s", e)
            return {}

    def get_stock_history(self, params: Optional[Dict] = None) -> Dict:
        """获取股票历史数据

        Args:
            params: Dict - 查询参数

        Returns:
            Dict: 股票历史数据
        """
        try:
            # 默认参数
            params = params or {}
            symbol = params.get("symbol", "")
            period = params.get("period", "daily")
            limit = params.get("limit", 100)

            if not symbol:
                return {}

            # 查询历史数据表（根据周期选择表名）
            table_name = f"stock_history_{period}" if period != "daily" else "daily_kline"

            where_clause = f"symbol = '{symbol}'"
            df = self.postgresql_access.query(
                table_name=table_name,
                where=where_clause,
                order_by="date DESC",
                limit=limit,
            )

            # 转换为与Mock数据一致的格式
            if not df.empty:
                result = {
                    "symbol": symbol,
                    "period": period,
                    "count": len(df),
                    "dates": [row["date"].strftime("%Y-%m-%d") for _, row in df.iterrows()],
                    "data": df[["open", "close", "high", "low", "volume"]].to_dict("records"),
                }

                # 如果有涨跌幅数据，也包含进去
                if "change_percent" in df.columns:
                    result["change_percent"] = [float(x) for x in df["change_percent"].tolist()]

                return result

            return {}

        except Exception as e:
            logger.error("获取股票历史数据失败: %s", e)
            return {}

    def get_batch_indicators(self, symbols: List[str]) -> Dict:
        """批量获取技术指标

        Args:
            symbols: List[str] - 股票代码列表

        Returns:
            Dict: 批量技术指标数据
        """
        try:
            if not symbols:
                return {}

            results = []
            for symbol in symbols:
                indicators = self.get_technical_indicators({"symbol": symbol})
                if indicators:
                    results.append(indicators)

            return {"success": True, "count": len(results), "data": results}

        except Exception as e:
            logger.error("批量获取技术指标失败: %s", e)
            return {}

    def get_strategy_definitions(self) -> Dict:
        """获取策略定义列表

        Returns:
            Dict: 策略定义列表，与Mock数据格式一致
        """
        try:
            # 示例实现（需要根据实际表结构调整）
            df = self.postgresql_access.query(table_name="strategy_definitions", limit=100)

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "id": int(row.get("id", 0)),
                            "code": row.get("code", ""),
                            "name": row.get("name", ""),
                            "description": row.get("description", ""),
                            "category": row.get("category", ""),
                            "parameters": row.get("parameters", {}),
                            "created_at": (
                                row.get("created_at", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("created_at"))
                                else ""
                            ),
                            "updated_at": (
                                row.get("updated_at", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("updated_at"))
                                else ""
                            ),
                            "is_active": bool(row.get("is_active", True)),
                        }
                    )

            return {"strategies": result, "total": len(result)}

        except Exception as e:
            logger.error("获取策略定义失败: %s", e)
            return {}

    def get_strategy_results(self, params: Optional[Dict] = None) -> Dict:
        """获取策略执行结果

        Args:
            params: Dict - 查询参数

        Returns:
            Dict: 策略结果数据，与Mock数据格式一致
        """
        try:
            # 默认参数
            params = params or {}
            strategy_code = params.get("strategy_code", "")
            limit = params.get("limit", 20)
            offset = params.get("offset", 0)

            # 示例实现（需要根据实际表结构调整）
            where_clause = f"strategy_code = '{strategy_code}'" if strategy_code else None
            df = self.postgresql_access.query(table_name="strategy_results", where=where_clause, limit=limit)

            # 手动处理offset
            if offset and offset > 0:
                df = df.iloc[offset:]

            # 转换为与Mock数据一致的格式
            result = []
            if not df.empty:
                for _, row in df.iterrows():
                    result.append(
                        {
                            "id": int(row.get("id", 0)),
                            "symbol": row.get("symbol", ""),
                            "name": row.get("name", ""),
                            "match_score": float(row.get("match_score", 0.0)),
                            "created_at": (
                                row.get("created_at", "").strftime("%Y-%m-%d %H:%M:%S")
                                if pd.notna(row.get("created_at"))
                                else ""
                            ),
                            "strategy_code": row.get("strategy_code", ""),
                        }
                    )

            return {
                "strategy_code": strategy_code,
                "total": len(result),
                "results": result,
                "execution_time": 0.12,
            }

        except Exception as e:
            logger.error("获取策略结果失败: %s", e)
            return {}

    def get_strategy_performance(self) -> Dict:
        """获取策略性能统计

        Returns:
            Dict: 策略性能数据，与Mock数据格式一致
        """
        try:
            # 示例实现（需要根据实际表结构调整）
            # 查询策略性能表
            df = self.postgresql_access.query(table_name="strategy_performance", limit=100)

            # 转换为与Mock数据一致的格式
            if not df.empty:
                # 获取最新记录
                latest_row = df.iloc[0]
                return {
                    "total_runs": int(latest_row.get("total_runs", 0)),
                    "avg_execution_time": float(latest_row.get("avg_execution_time", 0.0)),
                    "success_rate": float(latest_row.get("success_rate", 0.0)),
                    "total_matches": int(latest_row.get("total_matches", 0)),
                    "avg_matches_per_run": float(latest_row.get("avg_matches_per_run", 0.0)),
                    "last_updated": (
                        latest_row.get("last_updated", "").strftime("%Y-%m-%d %H:%M:%S")
                        if pd.notna(latest_row.get("last_updated"))
                        else ""
                    ),
                }

            return {}

        except Exception as e:
            logger.error("获取策略性能失败: %s", e)
            return {}

    def get_monitoring_status(self) -> Dict:
        """获取监控状态

        Returns:
            Dict: 监控状态信息，与Mock数据格式一致
        """
        try:
            # 示例实现（需要根据实际表结构调整）
            # 查询监控状态表
            df = self.postgresql_access.query(table_name="monitoring_status", limit=1)

            # 转换为与Mock数据一致的格式
            if not df.empty:
                row = df.iloc[0]
                return {
                    "is_running": bool(row.get("is_running", True)),
                    "start_time": (
                        row.get("start_time", "").strftime("%Y-%m-%d %H:%M:%S")
                        if pd.notna(row.get("start_time"))
                        else (datetime.now() - pd.Timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    "last_update": (
                        row.get("last_update", "").strftime("%Y-%m-%d %H:%M:%S")
                        if pd.notna(row.get("last_update"))
                        else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    "monitored_symbols": int(row.get("monitored_symbols", 100)),
                    "active_alerts": int(row.get("active_alerts", 15)),
                    "status": row.get("status", "healthy"),
                }

            # 如果没有数据，返回默认状态
            from datetime import datetime

            return {
                "is_running": True,
                "start_time": (datetime.now() - pd.Timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "monitored_symbols": 100,
                "active_alerts": 15,
                "status": "healthy",
            }

        except Exception as e:
            logger.error("获取监控状态失败: %s", e)
            # 发生错误时返回默认状态
            from datetime import datetime

            return {
                "is_running": True,
                "start_time": (datetime.now() - pd.Timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S"),
                "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "monitored_symbols": 100,
                "active_alerts": 15,
                "status": "healthy",
            }

    def get_market_monitoring(self) -> Dict:
        """获取市场监控数据

        Returns:
            Dict: 市场监控数据，与Mock数据格式一致
        """
        try:
            # 查询监控日志表，获取最新的市场监控数据
            df = self.postgresql_access.query(table_name="monitoring_logs", limit=100, order_by="log_time DESC")

            # 转换为与Mock数据一致的格式
            if not df.empty:
                # 统计不同类型的消息
                total_logs = len(df)
                error_count = len(df[df["log_level"] == "ERROR"])
                warning_count = len(df[df["log_level"] == "WARNING"])

                return {
                    "total_logs": total_logs,
                    "error_count": error_count,
                    "warning_count": warning_count,
                    "latest_logs": df.head(10).to_dict("records"),
                }

            # 如果没有数据，返回默认状态
            return {
                "total_logs": 0,
                "error_count": 0,
                "warning_count": 0,
                "latest_logs": [],
            }

        except Exception as e:
            logger.error("获取市场监控数据失败: %s", e)
            # 发生错误时返回默认状态
            return {
                "total_logs": 0,
                "error_count": 0,
                "warning_count": 0,
                "latest_logs": [],
            }

    def get_data_from_adapter(self, adapter_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """从指定适配器获取数据

        Args:
            adapter_type: str - 适配器类型 (akshare, tdx, baostock, tushare等)
            method: str - 调用方法名
            **kwargs: 方法参数

        Returns:
            Union[Dict, List[Dict], pd.DataFrame]: 适配器返回的数据
        """
        try:
            # 动态导入适配器
            adapter_module = None
            if adapter_type == "akshare":
                from src.adapters.akshare import AkshareDataSource

                adapter_module = AkshareDataSource()
            elif adapter_type == "tdx":
                from src.adapters.tdx_adapter import TdxDataSource

                adapter_module = TdxDataSource()
            elif adapter_type == "baostock":
                from src.adapters.baostock_adapter import BaostockDataSource

                adapter_module = BaostockDataSource()
            elif adapter_type == "tushare":
                from src.adapters.tushare_adapter import TushareDataSource

                adapter_module = TushareDataSource()
            elif adapter_type == "financial":
                from src.adapters.financial import FinancialDataSource

                adapter_module = FinancialDataSource()
            elif adapter_type == "customer":
                from src.adapters.customer_adapter import CustomerDataSource

                adapter_module = CustomerDataSource()
            elif adapter_type == "byapi":
                from src.adapters.byapi_adapter import ByapiDataSource

                adapter_module = ByapiDataSource()
            else:
                raise ValueError(f"不支持的适配器类型: {adapter_type}")

            # 调用指定方法
            if hasattr(adapter_module, method):
                method_func = getattr(adapter_module, method)
                return method_func(**kwargs)
            else:
                raise AttributeError(f"适配器 {adapter_type} 没有方法 {method}")

        except Exception as e:
            logger.error("从适配器 %s 调用方法 %s 失败: %s", adapter_type, method, e)
            # 根据返回类型返回合适的默认值
            import pandas as pd

            if method in ["get_stock_list"]:
                return []
            elif method in ["get_stock_daily", "get_history_profit"]:
                return pd.DataFrame()
            else:
                return {}

    def get_data_with_failover(self, data_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """使用故障转移机制获取数据

        Args:
            data_type: str - 数据类型 (realtime_quote, daily_kline等)
            method: str - 调用方法名
            **kwargs: 方法参数

        Returns:
            Union[Dict, List[Dict], pd.DataFrame]: 适配器返回的数据
        """
        try:
            # 加载适配器优先级配置
            import yaml
            import os

            config_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "config",
                "adapter_priority_config.yaml",
            )
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    config = yaml.safe_load(f)
            else:
                # 默认配置
                config = {
                    "default": [
                        "tdx",
                        "akshare",
                        "baostock",
                        "tushare",
                        "financial",
                        "customer",
                        "byapi",
                    ]
                }

            # 获取指定数据类型的适配器优先级，如果没有则使用默认优先级
            adapter_priority = config.get(data_type, config.get("default", config["default"]))

            # 按优先级顺序尝试适配器
            for adapter_type in adapter_priority:
                try:
                    logger.info("尝试使用适配器 %s 获取 %s 数据", adapter_type, data_type)
                    result = self.get_data_from_adapter(adapter_type, method, **kwargs)

                    # 检查结果是否有效
                    if self._is_valid_result(result):
                        logger.info("成功使用适配器 %s 获取 %s 数据", adapter_type, data_type)
                        return result
                    else:
                        logger.warning("适配器 %s 返回空数据", adapter_type)

                except Exception as e:
                    logger.warning("适配器 %s 获取 %s 数据失败: %s", adapter_type, data_type, e)
                    continue

            # 所有适配器都失败
            logger.error("所有适配器都无法获取 %s 数据", data_type)
            raise Exception(f"所有适配器都无法获取 {data_type} 数据")

        except Exception as e:
            logger.error("使用故障转移机制获取 %s 数据失败: %s", data_type, e)
            # 根据返回类型返回合适的默认值
            import pandas as pd

            if method in ["get_stock_list"]:
                return []
            elif method in ["get_stock_daily", "get_history_profit"]:
                return pd.DataFrame()
            else:
                return {}

    def _is_valid_result(self, result) -> bool:
        """检查适配器返回结果是否有效

        Args:
            result: 适配器返回的结果

        Returns:
            bool: 结果是否有效
        """
        import pandas as pd

        if isinstance(result, pd.DataFrame):
            return not result.empty
        elif isinstance(result, list):
            return len(result) > 0
        elif isinstance(result, dict):
            return len(result) > 0
        else:
            return result is not None

    def get_indicator_data(self, indicator_id: str, symbol: str, days: int = 30) -> pd.DataFrame:
        """获取指标数据表格

        Args:
            indicator_id: str - 指标ID
            symbol: str - 股票代码
            days: int - 天数

        Returns:
            pd.DataFrame: 指标数据表格
        """
        try:
            # 查询技术指标表
            where_clause = f"symbol = '{symbol}' AND indicator_name = '{indicator_id}'"
            df = self.postgresql_access.query(
                table_name="technical_indicators",
                where=where_clause,
                order_by="calc_date DESC",
                limit=days,
            )

            # 转换为与Mock数据一致的格式
            if not df.empty:
                return df[["calc_date", "indicator_value"]].rename(
                    columns={"calc_date": "date", "indicator_value": indicator_id}
                )

            return pd.DataFrame()

        except Exception as e:
            logger.error("获取指标数据失败: %s", e)
            return pd.DataFrame()

    def get_minute_kline(self, symbol: str, period: str, start_date: str, end_date: str) -> pd.DataFrame:
        """获取分钟K线数据

        Args:
            symbol: str - 股票代码
            period: str - 周期 (1m/5m/15m/30m/60m)
            start_date: str - 开始日期
            end_date: str - 结束日期

        Returns:
            pd.DataFrame: 分钟K线数据
        """
        try:
            # 根据周期确定表名
            table_name = f"minute_kline_{period.replace('m', 'min')}"

            # 构造查询条件
            where_clause = f"symbol = '{symbol}' AND ts >= '{start_date}' AND ts <= '{end_date}'"

            # 查询TDengine数据库
            df = self.postgresql_access.query(table_name=table_name, where=where_clause, order_by="ts ASC")

            # 转换为与Mock数据一致的格式
            if not df.empty:
                df = df.rename(
                    columns={
                        "ts": "date",
                        "open": "open",
                        "high": "high",
                        "low": "low",
                        "close": "close",
                        "volume": "volume",
                        "amount": "amount",
                    }
                )
                return df[["date", "open", "high", "low", "close", "volume", "amount"]]

            return pd.DataFrame()

        except Exception as e:
            logger.error("获取分钟K线数据失败: %s", e)
            return pd.DataFrame()

    def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据

        Returns:
            pd.DataFrame: 行业分类数据
        """
        try:
            # 查询行业分类表
            df = self.postgresql_access.query(table_name="industry_classifications", order_by="industry_code ASC")

            # 转换为与Mock数据一致的格式
            if not df.empty:
                df = df.rename(
                    columns={
                        "industry_code": "index",
                        "industry_name": "name",
                        "stock_count": "stock_count",
                        "up_count": "up_count",
                        "down_count": "down_count",
                        "leader_stock": "leader_stock",
                        "latest_price": "latest_price",
                        "change_percent": "change_percent",
                        "change_amount": "change_amount",
                        "volume": "volume",
                        "amount": "amount",
                        "total_market_value": "total_market_value",
                        "turnover_rate": "turnover_rate",
                        "updated_at": "updated_at",
                    }
                )
                return df

            return pd.DataFrame()

        except Exception as e:
            logger.error("获取行业分类数据失败: %s", e)
            return pd.DataFrame()

    def get_concept_classify(self) -> pd.DataFrame:
        """获取概念分类数据

        Returns:
            pd.DataFrame: 概念分类数据
        """
        try:
            # 查询概念分类表
            df = self.postgresql_access.query(table_name="concept_classifications", order_by="concept_code ASC")

            # 转换为与Mock数据一致的格式
            if not df.empty:
                df = df.rename(
                    columns={
                        "concept_code": "index",
                        "concept_name": "name",
                        "stock_count": "stock_count",
                        "up_count": "up_count",
                        "down_count": "down_count",
                        "leader_stock": "leader_stock",
                        "latest_price": "latest_price",
                        "change_percent": "change_percent",
                        "change_amount": "change_amount",
                        "volume": "volume",
                        "amount": "amount",
                        "total_market_value": "total_market_value",
                        "turnover_rate": "turnover_rate",
                        "updated_at": "updated_at",
                    }
                )
                return df

            return pd.DataFrame()

        except Exception as e:
            logger.error("获取概念分类数据失败: %s", e)
            return pd.DataFrame()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """获取个股的行业和概念分类信息

        Args:
            symbol: str - 股票代码

        Returns:
            Dict: 个股行业和概念信息
        """
        try:
            # 查询个股行业概念关联表
            where_clause = f"symbol = '{symbol}'"
            df = self.postgresql_access.query(
                table_name="stock_industry_concept_relations",
                where=where_clause,
                order_by="category_type ASC",
            )

            # 分离行业和概念
            industries = []
            concepts = []

            if not df.empty:
                industry_df = df[df["category_type"] == "industry"]
                concept_df = df[df["category_type"] == "concept"]

                industries = industry_df["category_name"].tolist()
                concepts = concept_df["category_name"].tolist()

            return {"symbol": symbol, "industries": industries, "concepts": concepts}

        except Exception as e:
            logger.error("获取个股行业概念信息失败: %s", e)
            return {"symbol": symbol, "industries": [], "concepts": []}


# 创建全局数据库服务实例
db_service = DatabaseService()
