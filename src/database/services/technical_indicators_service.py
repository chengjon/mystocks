"""
# 功能：技术指标服务
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：专门处理技术指标数据的服务
"""

from typing import Dict
from loguru import logger

from .base_database_service import BaseDatabaseService


class TechnicalIndicatorsService(BaseDatabaseService):
    """
    技术指标服务

    专门处理各种技术指标的计算和查询
    """

    def __init__(self):
        super().__init__()
        logger.info("技术指标服务初始化完成")

    def get_technical_indicators(self, params: Dict) -> Dict:
        """获取技术指标数据

        Args:
            params: Dict - 查询参数：
                    symbol: str - 股票代码
                    indicators: List[str] - 指标列表
                    start_date: str - 开始日期
                    end_date: str - 结束日期
                    limit: int - 每页数量，默认50

        Returns:
            Dict: 技术指标数据
        """
        try:
            symbol = params.get("symbol")
            indicators = params.get("indicators", [])
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            limit = min(200, max(1, params.get("limit", 50)))  # 限制在1-200之间

            if not symbol:
                raise ValueError("股票代码不能为空")

            # 构建查询条件
            filters = {"symbol": symbol}
            if indicators:
                filters["indicator_name"] = indicators
            if start_date and end_date:
                filters["calculation_date"] = [start_date, end_date]
            elif start_date:
                filters["calculation_date"] = start_date
            elif end_date:
                filters["calculation_date"] = end_date

            # 查询技术指标数据
            df = self._execute_query(
                table_name="technical_indicators",
                filters=filters,
                order_by="calculation_date DESC, indicator_name",
                limit=limit,
            )

            # 按指标类型分组
            result = {}
            for _, row in df.iterrows():
                indicator_type = row.get("indicator_type", "other")
                if indicator_type not in result:
                    result[indicator_type] = []

                result[indicator_type].append(
                    {
                        "indicator_name": row.get("indicator_name", ""),
                        "indicator_value": row.get("indicator_value", 0),
                        "calculation_date": row.get("calculation_date", ""),
                        "symbol": row.get("symbol", ""),
                    }
                )

            return self._build_success_response(
                data=result,
                operation="get_technical_indicators",
                meta={
                    "symbol": symbol,
                    "indicators_count": len(df),
                    "start_date": start_date,
                    "end_date": end_date,
                },
            )

        except Exception as e:
            return self._handle_database_error(e, "获取技术指标")

    def get_trend_indicators(self, stock_code: str) -> Dict:
        """获取趋势指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 趋势指标数据
        """
        try:
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # 查询趋势指标
            trend_indicators = [
                "MA5",
                "MA10",
                "MA20",
                "MA60",
                "MA120",
                "MA250",
                "EMA5",
                "EMA10",
                "EMA20",
                "MACD",
                "MACD_signal",
                "MACD_hist",
            ]

            df = self._execute_query(
                table_name="technical_indicators",
                filters={"symbol": stock_code, "indicator_name": trend_indicators},
                order_by="calculation_date DESC",
            )

            # 按指标组织数据
            result = {}
            for _, row in df.iterrows():
                indicator_name = row.get("indicator_name", "")
                if indicator_name not in result:
                    result[indicator_name] = []

                result[indicator_name].append(
                    {
                        "value": row.get("indicator_value", 0),
                        "date": row.get("calculation_date", ""),
                    }
                )

            return self._build_success_response(
                data=result, operation="get_trend_indicators"
            )

        except Exception as e:
            return self._handle_database_error(e, "获取趋势指标")

    def get_momentum_indicators(self, stock_code: str) -> Dict:
        """获取动量指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 动量指标数据
        """
        try:
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # 查询动量指标
            momentum_indicators = [
                "RSI",
                "RSI14",
                "KDJ_K",
                "KDJ_D",
                "KDJ_J",
                "WMS_R",
                "WMS_R9",
                "BIAS",
                "BIAS6",
                "CCI",
                "CCI14",
            ]

            df = self._execute_query(
                table_name="technical_indicators",
                filters={"symbol": stock_code, "indicator_name": momentum_indicators},
                order_by="calculation_date DESC",
            )

            # 按指标组织数据
            result = {}
            for _, row in df.iterrows():
                indicator_name = row.get("indicator_name", "")
                if indicator_name not in result:
                    result[indicator_name] = []

                result[indicator_name].append(
                    {
                        "value": row.get("indicator_value", 0),
                        "date": row.get("calculation_date", ""),
                    }
                )

            return self._build_success_response(
                data=result, operation="get_momentum_indicators"
            )

        except Exception as e:
            return self._handle_database_error(e, "获取动量指标")

    def get_volatility_indicators(self, stock_code: str) -> Dict:
        """获取波动率指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 波动率指标数据
        """
        try:
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # 查询波动率指标
            volatility_indicators = [
                "BOLL_UPPER",
                "BOLL_MIDDLE",
                "BOLL_LOWER",
                "ATR14",
                "ATR",
                "STDDEV",
                "VOLATILITY",
            ]

            df = self._execute_query(
                table_name="technical_indicators",
                filters={"symbol": stock_code, "indicator_name": volatility_indicators},
                order_by="calculation_date DESC",
            )

            # 按指标组织数据
            result = {}
            for _, row in df.iterrows():
                indicator_name = row.get("indicator_name", "")
                if indicator_name not in result:
                    result[indicator_name] = []

                result[indicator_name].append(
                    {
                        "value": row.get("indicator_value", 0),
                        "date": row.get("calculation_date", ""),
                    }
                )

            return self._build_success_response(
                data=result, operation="get_volatility_indicators"
            )

        except Exception as e:
            return self._handle_database_error(e, "获取波动率指标")

    def get_volume_indicators(self, stock_code: str) -> Dict:
        """获取成交量指标

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 成交量指标数据
        """
        try:
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # 查询成交量指标
            volume_indicators = [
                "VOLUME_MA5",
                "VOLUME_MA10",
                "VOLUME_MA20",
                "VOLUME_RATIO",
                "OBV",
                "VOLATILITY_RATIO",
            ]

            df = self._execute_query(
                table_name="technical_indicators",
                filters={"symbol": stock_code, "indicator_name": volume_indicators},
                order_by="calculation_date DESC",
            )

            # 按指标组织数据
            result = {}
            for _, row in df.iterrows():
                indicator_name = row.get("indicator_name", "")
                if indicator_name not in result:
                    result[indicator_name] = []

                result[indicator_name].append(
                    {
                        "value": row.get("indicator_value", 0),
                        "date": row.get("calculation_date", ""),
                    }
                )

            return self._build_success_response(
                data=result, operation="get_volume_indicators"
            )

        except Exception as e:
            return self._handle_database_error(e, "获取成交量指标")

    def get_all_indicators(self, params: Dict) -> Dict:
        """获取所有类型的指标

        Args:
            params: Dict - 查询参数：
                    symbol: str - 股票代码
                    limit: int - 每类指标的数量限制，默认10

        Returns:
            Dict: 所有指标数据
        """
        try:
            symbol = params.get("symbol")
            limit = min(20, max(1, params.get("limit", 10)))

            if not symbol:
                raise ValueError("股票代码不能为空")

            # 查询所有指标
            df = self._execute_query(
                table_name="technical_indicators",
                filters={"symbol": symbol},
                order_by="calculation_date DESC",
                limit=limit * 6,  # 假设有6种主要指标类型
            )

            # 按指标类型分组
            result = {
                "trend": {},
                "momentum": {},
                "volatility": {},
                "volume": {},
                "pattern": {},
                "other": {},
            }

            for _, row in df.iterrows():
                indicator_type = row.get("indicator_type", "other")
                indicator_name = row.get("indicator_name", "")
                if indicator_name not in result[indicator_type]:
                    result[indicator_type][indicator_name] = []

                result[indicator_type][indicator_name].append(
                    {
                        "value": row.get("indicator_value", 0),
                        "date": row.get("calculation_date", ""),
                    }
                )

                # 限制每种类型的指标数量
                if len(result[indicator_type][indicator_name]) >= limit:
                    continue

            return self._build_success_response(
                data=result,
                operation="get_all_indicators",
                meta={"symbol": symbol, "total_indicators": len(df)},
            )

        except Exception as e:
            return self._handle_database_error(e, "获取所有指标")

    def get_pattern_recognition(self, stock_code: str) -> Dict:
        """获取模式识别结果

        Args:
            stock_code: str - 股票代码

        Returns:
            Dict: 模式识别结果
        """
        try:
            if not stock_code:
                raise ValueError("股票代码不能为空")

            # 查询模式识别结果
            df = self._execute_query(
                table_name="pattern_recognition",
                filters={"symbol": stock_code},
                order_by="recognition_date DESC",
            )

            result = []
            for _, row in df.iterrows():
                result.append(
                    {
                        "pattern_name": row.get("pattern_name", ""),
                        "pattern_type": row.get("pattern_type", ""),
                        "confidence": row.get("confidence", 0),
                        "recognition_date": row.get("recognition_date", ""),
                        "price_target": row.get("price_target", 0),
                        "description": row.get("description", ""),
                    }
                )

            return self._build_success_response(
                data=result, operation="get_pattern_recognition"
            )

        except Exception as e:
            return self._handle_database_error(e, "获取模式识别")
