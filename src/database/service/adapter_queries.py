"""数据库服务子模块"""

import logging
from datetime import datetime
from typing import Dict, List, Union

import pandas as pd

from src.data_access import PostgreSQLDataAccess
from src.database.service import DatabaseService

logger = logging.getLogger(__name__)

postgresql_access = PostgreSQLDataAccess()


class AdapterQueriesMixin:
    """适配器调用、故障转移与市场分类查询"""

    def get_data_from_adapter(self, adapter_type: str, method: str, **kwargs) -> Union[Dict, List[Dict], pd.DataFrame]:
        """从指定适配器获取数据

        Args:
            adapter_type: str - 适配器类型 (akshare, tdx, baostock, tushare等)
            method: str - 调用方法名
            **kwargs: 方法参数

        Returns:
            Union[Dict, List[Dict], pd.DataFrame]: 适配器返回的数据
        """
        import time

        start_time = time.time()
        params_summary = str(kwargs)[:200]  # 限制参数摘要长度

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
                result = method_func(**kwargs)
                duration_ms = round((time.time() - start_time) * 1000, 2)
                # 结构化日志 | 分隔，便于 lnav 解析
                logger.info(
                    f"ADAPTER_CALL|{datetime.now().isoformat()}|{adapter_type}|{method}|params={params_summary}|status=SUCCESS|duration_ms={duration_ms}"
                )
                return result
            else:
                raise AttributeError(f"适配器 {adapter_type} 没有方法 {method}")

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            error_msg = str(e)[:200]
            # 结构化日志 | 分隔，便于 lnav 解析
            logger.error(
                f"ADAPTER_CALL|{datetime.now().isoformat()}|{adapter_type}|{method}|params={params_summary}|status=FAIL|error={error_msg}|duration_ms={duration_ms}"
            )
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
            import os

            import yaml

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
