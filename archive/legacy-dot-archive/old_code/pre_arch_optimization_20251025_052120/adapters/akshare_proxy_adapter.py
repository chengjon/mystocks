#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AkShare通用接口代理适配器

功能：
- 动态调用任何akshare接口，无需提前定义
- 提供统一的错误处理和重试机制
- 支持参数验证和类型转换
- 自动添加时间戳和数据标准化

使用场景：
- 快速接入新的akshare接口
- 测试和验证akshare功能
- 临时数据获取需求

注意：此适配器适合快速原型开发，生产环境建议使用专门的适配器
"""

import pandas as pd
import akshare as ak
import sys
import os
import time
import inspect
from typing import Dict, List, Any, Union
from functools import wraps

# 添加项目路径
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from mystocks.interfaces.data_source import IDataSource

# 常量定义
MAX_RETRIES = 3
RETRY_DELAY = 1
REQUEST_TIMEOUT = 30


class AkshareProxyAdapter(IDataSource):
    """AkShare通用接口代理适配器

    可以动态调用任何akshare接口，提供统一的错误处理和数据标准化
    """

    def __init__(
        self, api_timeout: int = REQUEST_TIMEOUT, max_retries: int = MAX_RETRIES
    ):
        """初始化AkShare代理适配器

        Args:
            api_timeout: API请求超时时间(秒)
            max_retries: 最大重试次数
        """
        self.api_timeout = api_timeout
        self.max_retries = max_retries
        self._available_functions = self._discover_akshare_functions()
        print(
            f"[AkshareProxy] 代理适配器初始化完成 (超时: {api_timeout}s, 重试: {max_retries}次)"
        )
        print(
            f"[AkshareProxy] 发现 {len(self._available_functions)} 个可用的akshare接口"
        )

    def _discover_akshare_functions(self) -> Dict[str, callable]:
        """发现所有可用的akshare函数"""
        functions = {}
        for name in dir(ak):
            obj = getattr(ak, name)
            if callable(obj) and not name.startswith("_"):
                try:
                    # 尝试获取函数签名以验证这是一个真正的API函数
                    sig = inspect.signature(obj)
                    functions[name] = obj
                except (ValueError, TypeError):
                    # 跳过无法获取签名的对象
                    continue
        return functions

    def _retry_api_call(self, func):
        """API调用重试装饰器"""

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    print(f"[AkshareProxy] 第{attempt}次尝试失败: {str(e)}")
                    if attempt < self.max_retries:
                        time.sleep(RETRY_DELAY * attempt)
            raise last_exception if last_exception else Exception("未知错误")

        return wrapper

    def call_akshare_function(
        self, function_name: str, **kwargs
    ) -> Union[pd.DataFrame, Dict, List, Any]:
        """动态调用akshare函数

        Args:
            function_name: akshare函数名称
            **kwargs: 函数参数

        Returns:
            函数执行结果
        """
        try:
            print(f"[AkshareProxy] 调用akshare接口: {function_name}")
            print(f"[AkshareProxy] 参数: {kwargs}")

            # 检查函数是否存在
            if function_name not in self._available_functions:
                available_similar = [
                    name
                    for name in self._available_functions.keys()
                    if function_name.lower() in name.lower()
                ]
                if available_similar:
                    print(
                        f"[AkshareProxy] 未找到函数 '{function_name}'，相似的函数有: {available_similar}"
                    )
                else:
                    print(f"[AkshareProxy] 未找到函数 '{function_name}'")
                return None

            # 使用重试机制调用函数
            @self._retry_api_call
            def _call_function():
                func = self._available_functions[function_name]
                return func(**kwargs)

            # 执行函数调用
            result = _call_function()

            # 处理结果
            if isinstance(result, pd.DataFrame):
                print(
                    f"[AkshareProxy] 成功获取DataFrame数据: {len(result)}行, 列名={result.columns.tolist()}"
                )
                # 添加时间戳
                result["数据获取时间"] = pd.Timestamp.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                result["数据来源"] = f"akshare.{function_name}"
            elif isinstance(result, (list, dict)):
                print(f"[AkshareProxy] 成功获取{type(result).__name__}数据")
            else:
                print(f"[AkshareProxy] 成功获取{type(result).__name__}数据: {result}")

            return result

        except Exception as e:
            print(f"[AkshareProxy] 调用函数 {function_name} 失败: {e}")
            import traceback

            traceback.print_exc()
            return None

    def get_function_info(self, function_name: str) -> Dict:
        """获取akshare函数的信息

        Args:
            function_name: 函数名称

        Returns:
            包含函数信息的字典
        """
        if function_name not in self._available_functions:
            return {"error": f"函数 {function_name} 不存在"}

        func = self._available_functions[function_name]
        try:
            sig = inspect.signature(func)
            doc = func.__doc__ or "无文档说明"

            return {
                "name": function_name,
                "signature": str(sig),
                "parameters": list(sig.parameters.keys()),
                "doc": doc.strip()[:200] + "..." if len(doc) > 200 else doc.strip(),
            }
        except Exception as e:
            return {"error": f"无法获取函数信息: {e}"}

    def search_functions(self, keyword: str) -> List[str]:
        """搜索包含关键词的akshare函数

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的函数名列表
        """
        keyword_lower = keyword.lower()
        matches = [
            name
            for name in self._available_functions.keys()
            if keyword_lower in name.lower()
        ]

        print(
            f"[AkshareProxy] 搜索关键词 '{keyword}' 找到 {len(matches)} 个匹配的函数:"
        )
        for match in matches[:10]:  # 只显示前10个
            print(f"  - {match}")
        if len(matches) > 10:
            print(f"  ... 还有 {len(matches) - 10} 个")

        return matches

    def list_stock_functions(self) -> List[str]:
        """列出所有股票相关的函数"""
        stock_keywords = ["stock", "equity", "share", "zh_a", "sz", "sh"]
        stock_functions = []

        for name in self._available_functions.keys():
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in stock_keywords):
                stock_functions.append(name)

        return sorted(stock_functions)

    def list_industry_functions(self) -> List[str]:
        """列出所有行业板块相关的函数"""
        industry_keywords = ["industry", "board", "sector", "concept", "ths", "em"]
        industry_functions = []

        for name in self._available_functions.keys():
            name_lower = name.lower()
            if any(keyword in name_lower for keyword in industry_keywords):
                industry_functions.append(name)

        return sorted(industry_functions)

    # 实现IDataSource接口的必需方法
    def get_stock_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取股票日线数据"""
        return self.call_akshare_function(
            "stock_zh_a_hist",
            symbol=symbol,
            period="daily",
            start_date=start_date.replace("-", ""),
            end_date=end_date.replace("-", ""),
            adjust="qfq",
        )

    def get_index_daily(
        self, symbol: str, start_date: str, end_date: str
    ) -> pd.DataFrame:
        """获取指数日线数据"""
        return self.call_akshare_function("stock_zh_index_daily", symbol=symbol)

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息"""
        result = self.call_akshare_function("stock_individual_info_em", symbol=symbol)
        if isinstance(result, pd.DataFrame) and not result.empty:
            return result.to_dict("records")
        return {}

    def get_index_components(self, symbol: str) -> List[str]:
        """获取指数成分股"""
        result = self.call_akshare_function("index_stock_cons", symbol=symbol)
        if isinstance(result, pd.DataFrame) and not result.empty:
            # 尝试找到股票代码列
            for col in ["品种代码", "成分券代码", "code", "symbol"]:
                if col in result.columns:
                    return result[col].tolist()
        return []

    def get_real_time_data(self, symbol: str) -> Dict:
        """获取实时数据"""
        result = self.call_akshare_function("stock_zh_a_spot")
        if isinstance(result, pd.DataFrame) and not result.empty:
            filtered = result[result["代码"] == symbol]
            if not filtered.empty:
                return filtered.iloc[0].to_dict()
        return {}

    def get_market_calendar(self, start_date: str, end_date: str) -> pd.DataFrame:
        """获取交易日历"""
        result = self.call_akshare_function("tool_trade_date_hist_sina")
        if isinstance(result, pd.DataFrame):
            return result
        return pd.DataFrame()

    def get_financial_data(self, symbol: str, period: str = "annual") -> pd.DataFrame:
        """获取财务数据"""
        result = self.call_akshare_function("stock_financial_abstract", stock=symbol)
        if isinstance(result, pd.DataFrame):
            return result
        return pd.DataFrame()

    def get_news_data(self, symbol: str = None, limit: int = 10) -> List[Dict]:
        """获取新闻数据"""
        kwargs = {"pageSize": limit}
        if symbol:
            kwargs["symbol"] = symbol

        result = self.call_akshare_function("stock_news_em", **kwargs)
        if isinstance(result, pd.DataFrame) and not result.empty:
            return result.to_dict("records")
        return []


def demo_akshare_proxy():
    """演示AkShare代理适配器的使用"""
    print("=" * 80)
    print("🚀 AkShare代理适配器演示")
    print("=" * 80)

    # 初始化代理适配器
    proxy = AkshareProxyAdapter()

    # 1. 搜索股票相关函数
    print("\n1️⃣ 搜索股票相关函数:")
    stock_functions = proxy.search_functions("stock_zh_a")

    # 2. 动态调用同花顺行业一览表
    print("\n2️⃣ 调用同花顺行业一览表:")
    industry_data = proxy.call_akshare_function("stock_board_industry_summary_ths")
    if isinstance(industry_data, pd.DataFrame):
        print(f"获取到 {len(industry_data)} 行数据")
        print(industry_data.head())

    # 3. 获取函数信息
    print("\n3️⃣ 获取函数信息:")
    func_info = proxy.get_function_info("stock_board_industry_summary_ths")
    print(f"函数签名: {func_info.get('signature', 'N/A')}")

    # 4. 调用任意akshare函数
    print("\n4️⃣ 调用股票实时数据:")
    realtime_data = proxy.call_akshare_function("stock_zh_a_spot")
    if isinstance(realtime_data, pd.DataFrame):
        print(f"获取到 {len(realtime_data)} 行实时数据")

    print("\n✅ 演示完成!")


if __name__ == "__main__":
    demo_akshare_proxy()
