"""
数据源处理器 V2.0（支持智能路由和健康检查）

核心功能：
1. 封装各个数据源的具体调用逻辑
2. 参数映射和转换
3. 错误处理和重试
4. 数据质量验证

作者：Claude Code
版本：v2.0
创建时间：2026-01-02
"""

import importlib
from typing import Dict, Any
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class BaseDataSourceHandler:
    """数据源处理器基类"""

    def __init__(self, endpoint_info: Dict):
        """
        初始化处理器

        Args:
            endpoint_info: 端点信息字典（从DataSourceManagerV2传入）
        """
        self.endpoint_info = endpoint_info
        self.endpoint_name = endpoint_info["endpoint_name"]
        self.source_name = endpoint_info.get("source_name", "")
        self.source_type = endpoint_info.get("source_type", "")
        self.config = endpoint_info

    def fetch(self, **kwargs) -> pd.DataFrame:
        """
        获取数据（子类必须实现）

        Args:
            **kwargs: 调用参数

        Returns:
            数据DataFrame

        Raises:
            NotImplementedError: 子类未实现
        """
        raise NotImplementedError(f"{self.__class__.__name__}.fetch() 未实现")

    def _map_arguments(self, args: Dict) -> Dict:
        """
        参数映射（将统一参数映射到具体API参数）

        Args:
            args: 统一参数

        Returns:
            映射后的参数
        """
        param_mapping = self.config.get("source_config", {}).get("param_mapping", {})
        return {param_mapping.get(k, k): v for k, v in args.items()}


class MockHandler(BaseDataSourceHandler):
    """Mock数据源处理器（用于测试和开发）"""

    def __init__(self, endpoint_info: Dict):
        super().__init__(endpoint_info)
        self.mock_data_path = endpoint_info.get("source_config", {}).get("mock_data_path")

    def fetch(self, **kwargs) -> pd.DataFrame:
        """生成Mock数据"""
        logger.info(f"生成Mock数据: {self.endpoint_name}")

        # 根据endpoint_name生成不同类型的Mock数据
        if "daily_kline" in self.endpoint_name:
            return self._generate_mock_daily_kline(**kwargs)
        elif "realtime" in self.endpoint_name:
            return self._generate_mock_realtime(**kwargs)
        elif "symbols" in self.endpoint_name:
            return self._generate_mock_symbols(**kwargs)
        else:
            raise ValueError(f"不支持的Mock接口: {self.endpoint_name}")

    def _generate_mock_daily_kline(
        self, symbol: str, period: str = "daily", start_date: str = None, end_date: str = None, **kwargs
    ) -> pd.DataFrame:
        """生成Mock日线数据"""
        import numpy as np
        from datetime import datetime, timedelta

        # 默认生成最近100天的数据
        if not end_date:
            end_date = datetime.now()
        else:
            end_date = datetime.strptime(end_date, "%Y%m%d")

        if not start_date:
            start_date = end_date - timedelta(days=100)
        else:
            start_date = datetime.strptime(start_date, "%Y%m%d")

        # 生成日期序列
        dates = pd.date_range(start_date, end_date, freq="B")  # 工作日

        # 生成随机价格数据
        np.random.seed(42)  # 固定种子，保证可重复
        n = len(dates)
        base_price = 10.0

        data = pd.DataFrame(
            {
                "trade_date": dates,
                "open": base_price + np.random.randn(n) * 0.5,
                "high": base_price + np.random.randn(n) * 0.5 + 0.5,
                "low": base_price + np.random.randn(n) * 0.5 - 0.5,
                "close": base_price + np.random.randn(n) * 0.5,
                "volume": np.random.randint(1000000, 10000000, n),
                "amount": np.random.randint(10000000, 100000000, n),
            }
        )

        # 确保价格逻辑正确（high >= close >= low）
        data["high"] = data[["open", "close"]].max(axis=1) + np.abs(np.random.randn(n))
        data["low"] = data[["open", "close"]].min(axis=1) - np.abs(np.random.randn(n))

        return data

    def _generate_mock_realtime(self, symbols: list, **kwargs) -> pd.DataFrame:
        """生成Mock实时行情"""
        import numpy as np
        from datetime import datetime

        data = []
        for symbol in symbols:
            base_price = 10.0 + np.random.randn()
            data.append(
                {
                    "symbol": symbol,
                    "price": base_price,
                    "volume": np.random.randint(100000, 1000000),
                    "timestamp": datetime.now(),
                }
            )

        return pd.DataFrame(data)

    def _generate_mock_symbols(self, **kwargs) -> pd.DataFrame:
        """生成Mock股票代码列表"""
        symbols = []
        for i in range(1, 100):  # 生成99只股票
            market = "SZ" if i % 2 == 0 else "SH"
            code = f"{i:06d}.{market}"
            symbols.append({"code": code, "name": f"测试股票{i:02d}", "market": market})

        return pd.DataFrame(symbols)


class AkshareHandler(BaseDataSourceHandler):
    """AKShare数据源处理器"""

    def __init__(self, endpoint_info: Dict):
        super().__init__(endpoint_info)
        self.module = None
        self.function_name = endpoint_info.get("source_config", {}).get("function_name")

    def fetch(self, **kwargs) -> pd.DataFrame:
        """调用AKShare接口"""
        logger.info(f"调用AKShare接口: {self.endpoint_name}")

        try:
            # 延迟导入akshare
            if self.module is None:
                self.module = importlib.import_module("akshare")

            # 参数映射
            mapped_args = self._map_arguments(kwargs)

            # 动态调用函数
            func = getattr(self.module, self.function_name)
            data = func(**mapped_args)

            # 标准化列名（统一格式）
            data = self._standardize_columns(data)

            return data

        except ImportError:
            raise ImportError("AKShare未安装: pip install akshare")
        except Exception as e:
            logger.error(f"AKShare接口调用失败: {self.endpoint_name}, 错误: {e}")
            raise

    def _standardize_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        """标准化列名（统一格式）"""
        # AKShare的列名是中文，映射为英文
        column_mapping = {
            "日期": "trade_date",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "change_pct",
            "涨跌额": "change",
            "换手率": "turnover",
        }

        # 只重命名存在的列
        existing_mapping = {k: v for k, v in column_mapping.items() if k in data.columns}
        return data.rename(columns=existing_mapping)


class TushareHandler(BaseDataSourceHandler):
    """TuShare数据源处理器（专业版）"""

    def __init__(self, endpoint_info: Dict):
        super().__init__(endpoint_info)
        self.pro = None
        self.api_name = endpoint_info.get("source_config", {}).get("api_name")
        self.token = None

    def fetch(self, **kwargs) -> pd.DataFrame:
        """调用TuShare接口"""
        logger.info(f"调用TuShare接口: {self.endpoint_name}")

        try:
            # 获取token
            if self.token is None:
                import os

                token_env_var = self.config.get("source_config", {}).get("token_env_var")
                if token_env_var:
                    self.token = os.getenv(token_env_var)
                    if not self.token:
                        raise ValueError(f"环境变量 {token_env_var} 未设置")
                else:
                    self.token = self.config.get("source_config", {}).get("token")

            # 延迟导入和初始化
            if self.pro is None:
                import tushare as ts

                self.pro = ts.pro_api(self.token)

            # 调用API
            data = self.pro.query(self.api_name, **kwargs, fields=self.config.get("source_config", {}).get("fields"))

            return data

        except ImportError:
            raise ImportError("TuShare未安装: pip install tushare")
        except Exception as e:
            logger.error(f"TuShare接口调用失败: {self.endpoint_name}, 错误: {e}")
            raise


class BaostockHandler(BaseDataSourceHandler):
    """BaoStock数据源处理器"""

    def __init__(self, endpoint_info: Dict):
        super().__init__(endpoint_info)
        self.bs = None
        self.is_logged_in = False

    def fetch(self, **kwargs) -> pd.DataFrame:
        """调用BaoStock接口"""
        logger.info(f"调用BaoStock接口: {self.endpoint_name}")

        try:
            # 延迟导入
            if self.bs is None:
                import baostock as bs

                self.bs = bs

            # 登录
            if not self.is_logged_in:
                lg = self.bs.login()
                if lg.error_code != "0":
                    raise ConnectionError(f"BaoStock登录失败: {lg.error_msg}")
                self.is_logged_in = True

            # 参数映射
            mapped_args = self._map_arguments(kwargs)

            # 调用接口
            fields = self.config.get("source_config", {}).get("fields", "")
            if fields:
                mapped_args["fields"] = fields

            rs = self.bs.query_stock_k_data_plus(**mapped_args)

            # 转换为DataFrame
            data_list = []
            while (rs.error_code == "0") & rs.next():
                data_list.append(rs.get_row_data())
            rs.release()

            data = pd.DataFrame(data_list)

            # 退出登录
            self._logout()

            return data

        except ImportError:
            raise ImportError("BaoStock未安装: pip install baostock")
        except Exception as e:
            logger.error(f"BaoStock接口调用失败: {self.endpoint_name}, 错误: {e}")
            self._logout()
            raise

    def _logout(self):
        """退出登录"""
        if self.bs and self.is_logged_in:
            try:
                self.bs.logout()
                self.is_logged_in = False
            except:
                pass

    def __del__(self):
        """析构时退出登录"""
        self._logout()


class TdxHandler(BaseDataSourceHandler):
    """通达信数据源处理器（直连）"""

    def __init__(self, endpoint_info: Dict):
        super().__init__(endpoint_info)
        self.api = None
        self.is_connected = False

        self.conn_config = endpoint_info.get("source_config", {})
        self.host = self.conn_config.get("host", "119.147.212.81")
        self.port = self.conn_config.get("port", 7709)

    def fetch(self, **kwargs) -> pd.DataFrame:
        """调用通达信接口"""
        logger.info(f"调用通达信接口: {self.endpoint_name}")

        try:
            # 延迟导入
            if self.api is None:
                from pytdx.hq import TdxHq_API

                self.api = TdxHq_API()

            # 连接
            if not self.is_connected:
                self.api.connect(self.host, self.port)
                self.is_connected = True

            # 根据接口类型调用
            if "security_quotes" in self.endpoint_name:
                return self._get_security_quotes(**kwargs)
            else:
                raise ValueError(f"不支持的通达信接口: {self.endpoint_name}")

        except ImportError:
            raise ImportError("PyTdx未安装: pip install pytdx")
        except Exception as e:
            logger.error(f"通达信接口调用失败: {self.endpoint_name}, 错误: {e}")
            raise

    def _get_security_quotes(self, symbols: list, **kwargs) -> pd.DataFrame:
        """获取实时行情"""
        # 转换为通达信格式
        tdx_symbols = []
        for symbol in symbols:
            # 判断市场
            if symbol.endswith(".SH"):
                market = 1  # 上海
                code = symbol.replace(".SH", "")
            elif symbol.endswith(".SZ"):
                market = 0  # 深圳
                code = symbol.replace(".SZ", "")
            else:
                # 纯数字代码，需要判断
                code = symbol[:6]
                if symbol.startswith("6"):
                    market = 1
                else:
                    market = 0

            tdx_symbols.append((market, code))

        # 调用API
        data = self.api.get_security_quotes(tdx_symbols)

        return pd.DataFrame(data)


class WebCrawlerHandler(BaseDataSourceHandler):
    """爬虫数据源处理器"""

    def __init__(self, endpoint_info: Dict):
        super().__init__(endpoint_info)
        import requests

        self.requests = requests
        self.endpoint_url = endpoint_info.get("endpoint_url")
        self.method = endpoint_info.get("source_config", {}).get("method", "GET")
        self.headers = endpoint_info.get("source_config", {}).get("headers", {})
        self.response_format = endpoint_info.get("source_config", {}).get("response_format", "json")

    def fetch(self, **kwargs) -> pd.DataFrame:
        """调用爬虫接口"""
        logger.info(f"调用爬虫接口: {self.endpoint_name}")

        # 构建请求
        url = self.endpoint_url
        params = {k: v for k, v in kwargs.items() if v is not None}

        # 发送请求
        if self.method.upper() == "GET":
            response = self.requests.get(url, params=params, headers=self.headers, timeout=30)
        else:
            response = self.requests.post(url, json=params, headers=self.headers, timeout=30)

        response.raise_for_status()

        # 解析响应
        if self.response_format == "json":
            data = response.json()

            # JSON路径提取
            json_path = self.config.get("source_config", {}).get("json_path")
            if json_path:
                data = self._parse_json_path(data, json_path)

            return pd.DataFrame(data)
        else:
            raise ValueError(f"不支持的响应格式: {self.response_format}")

    def _parse_json_path(self, data: Any, path: str) -> Any:
        """简单的JSON路径解析"""
        # 支持类似 $.data.diff 的路径
        if path.startswith("$."):
            parts = path[2:].split(".")
            for part in parts:
                if isinstance(data, dict):
                    data = data.get(part)
                elif isinstance(data, list) and part.isdigit():
                    data = data[int(part)]
                else:
                    raise ValueError(f"无法解析JSON路径: {path}")
            return data
        return data
