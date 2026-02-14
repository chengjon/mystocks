"""数据库服务子模块"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)

postgresql_access = PostgreSQLDataAccess()


class TechnicalQueriesMixin:
    """技术指标与监控查询"""

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

