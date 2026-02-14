"""数据库服务子模块"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Union

import pandas as pd

from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)

postgresql_access = PostgreSQLDataAccess()


class SignalHistoryQueriesMixin:
    """信号、历史数据与批量查询"""

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

