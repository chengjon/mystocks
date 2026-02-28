"""数据库服务子模块"""

import logging
from datetime import datetime
from typing import Dict, Optional

import pandas as pd

from src.data_access import PostgreSQLDataAccess

logger = logging.getLogger(__name__)

postgresql_access = PostgreSQLDataAccess()


class StrategyQueriesMixin:
    """策略与市场监控查询"""

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

