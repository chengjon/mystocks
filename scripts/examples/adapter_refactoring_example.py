"""适配器重构示例 - 从旧接口迁移到新接口
展示如何将现有的Akshare适配器重构为使用新的接口设计

本文件展示了：
1. 旧接口实现的问题
2. 新接口的重构方法
3. 向后兼容性的保持
4. 迁移步骤和最佳实践

作者: Claude Code
日期: 2025-11-14
"""

import datetime
import os
import sys
from typing import Dict, Optional, Union

import pandas as pd


# 添加src目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入新接口
from src.interfaces.refactored_interfaces import (
    DataResponse,
    IBasicInfoSource,
    IIndexDataSource,
    IPriceDataSource,
    validate_date,
    validate_symbol,
)


# 导入旧的适配器 (用于对比)
# from src.adapters.akshare_adapter import AkshareDataSource as OldAkshareDataSource


class RefactoredAkshareDataSource(IPriceDataSource, IIndexDataSource, IBasicInfoSource):
    """重构版Akshare数据源适配器

    这个版本展示了如何：
    1. 实现特化接口而不是完整接口
    2. 使用统一的响应格式
    3. 改进错误处理
    4. 保持向后兼容性
    """

    def __init__(self, api_timeout: int = 10, max_retries: int = 3):
        """初始化适配器

        Args:
            api_timeout: API请求超时时间(秒)
            max_retries: 最大重试次数

        """
        super().__init__(name="Akshare")
        self.api_timeout = api_timeout
        self.max_retries = max_retries

        # 检查akshare是否可用
        try:
            import akshare as ak

            self.ak = ak
            self.available = True
            print(
                f"✅ Akshare适配器初始化成功 (超时: {api_timeout}s, 重试: {max_retries}次)",
            )
        except ImportError as e:
            print(f"❌ Akshare不可用: {e}")
            self.available = False
            self.ak = None

    # =============================================================================
    # IPriceDataSource 实现 (核心方法)
    # =============================================================================

    def get_stock_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> DataResponse:
        """获取股票日线数据 - 重构版本"""
        # 1. 输入验证
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        error_msg = self._validate_stock_inputs(symbol, start_date, end_date)
        if error_msg:
            return DataResponse.create_error(error_msg=error_msg)

        try:
            # 2. 数据获取
            stock_code = self._format_stock_code(symbol)
            start_date_fmt, end_date_fmt = self._format_dates(start_date, end_date)

            # 调用akshare API
            df = self.ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date_fmt,
                end_date=end_date_fmt,
                adjust="qfq",  # 前复权
                timeout=self.api_timeout,
            )

            # 3. 数据验证和转换
            if df is None or df.empty:
                return DataResponse.empty(message=f"未能获取股票 {symbol} 的日线数据")

            # 4. 标准化数据格式
            standardized_df = self._standardize_stock_data(df)

            # 5. 返回成功响应
            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "start_date": start_date,
                "end_date": end_date,
                "record_count": len(standardized_df),
                "data_frequency": "daily",
            }

            return DataResponse.create_success(data=standardized_df, metadata=metadata)

        except Exception as e:
            error_msg = f"获取股票日线数据失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    def get_real_time_data(self, symbol: str) -> DataResponse:
        """获取实时数据 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        if not validate_symbol(symbol):
            return DataResponse.create_error(error_msg=f"无效的股票代码格式: {symbol}")

        try:
            # 获取所有股票实时数据
            df = self.ak.stock_zh_a_spot()

            if df is None or df.empty:
                return DataResponse.empty(message="未能获取实时数据")

            # 筛选指定股票
            filtered_df = df[df["代码"] == symbol]
            if filtered_df.empty:
                return DataResponse.empty(message=f"未能找到股票 {symbol} 的实时数据")

            # 转换为字典格式
            real_time_data = filtered_df.iloc[0].to_dict()

            # 添加时间戳
            real_time_data["update_time"] = datetime.datetime.now().isoformat()

            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "update_time": real_time_data["update_time"],
            }

            return DataResponse.create_success(data=real_time_data, metadata=metadata)

        except Exception as e:
            error_msg = f"获取实时数据失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    # =============================================================================
    # IIndexDataSource 实现 (可选方法)
    # =============================================================================

    def get_index_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> DataResponse:
        """获取指数日线数据 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        error_msg = self._validate_stock_inputs(symbol, start_date, end_date)
        if error_msg:
            return DataResponse.create_error(error_msg=error_msg)

        try:
            index_code = self._format_index_code(symbol)
            start_date_fmt, end_date_fmt = self._format_dates(start_date, end_date)

            # 尝试多个API接口
            df = None

            # 方法1: 新浪接口
            try:
                df = self.ak.stock_zh_index_daily(symbol=index_code)
                if df is not None and not df.empty:
                    df["date"] = pd.to_datetime(df["date"])
                    mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
                    df = df[mask]
            except Exception:
                pass

            # 方法2: 如果新浪接口失败，尝试东方财富接口
            if df is None or df.empty:
                try:
                    df = self.ak.stock_zh_index_daily_em(symbol=index_code)
                    if df is not None and not df.empty:
                        df["date"] = pd.to_datetime(df["date"])
                        mask = (df["date"] >= pd.to_datetime(start_date)) & (df["date"] <= pd.to_datetime(end_date))
                        df = df[mask]
                except Exception:
                    pass

            if df is None or df.empty:
                return DataResponse.empty(message=f"未能获取指数 {symbol} 的数据")

            # 标准化数据格式
            standardized_df = self._standardize_index_data(df)

            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "index_code": index_code,
                "start_date": start_date,
                "end_date": end_date,
                "record_count": len(standardized_df),
            }

            return DataResponse.create_success(data=standardized_df, metadata=metadata)

        except Exception as e:
            error_msg = f"获取指数日线数据失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    def get_index_components(self, symbol: str) -> DataResponse:
        """获取指数成分股 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        if not validate_symbol(symbol):
            return DataResponse.create_error(error_msg=f"无效的指数代码格式: {symbol}")

        try:
            df = self.ak.index_stock_cons(symbol=symbol)

            if df is None or df.empty:
                return DataResponse.empty(message=f"未能获取指数 {symbol} 的成分股")

            # 提取股票代码
            if "品种代码" in df.columns:
                components = df["品种代码"].tolist()
            elif "成分券代码" in df.columns:
                components = df["成分券代码"].tolist()
            else:
                return DataResponse.create_error(
                    error_msg=f"无法识别的成分股列名: {df.columns.tolist()}",
                )

            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "component_count": len(components),
            }

            return DataResponse.create_success(data=components, metadata=metadata)

        except Exception as e:
            error_msg = f"获取指数成分股失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    # =============================================================================
    # IBasicInfoSource 实现 (可选方法)
    # =============================================================================

    def get_stock_basic(self, symbol: str) -> DataResponse:
        """获取股票基本信息 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        if not validate_symbol(symbol):
            return DataResponse.create_error(error_msg=f"无效的股票代码格式: {symbol}")

        try:
            stock_code = self._format_stock_code(symbol)
            df = self.ak.stock_individual_info_em(symbol=stock_code)

            if df is None or df.empty:
                return DataResponse.empty(message=f"未能获取股票 {symbol} 的基本信息")

            # 转换为字典
            info_dict = {}
            for _, row in df.iterrows():
                info_dict[row["item"]] = row["value"]

            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "info_fields": list(info_dict.keys()),
            }

            return DataResponse.create_success(data=info_dict, metadata=metadata)

        except Exception as e:
            error_msg = f"获取股票基本信息失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    def get_market_calendar(self, start_date: str, end_date: str) -> DataResponse:
        """获取交易日历 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        if not validate_date(start_date) or not validate_date(end_date):
            return DataResponse.create_error(
                error_msg="无效的日期格式，请使用YYYY-MM-DD格式",
            )

        try:
            df = self.ak.tool_trade_date_hist_sina()

            if df is None or df.empty:
                return DataResponse.empty(message="未能获取交易日历数据")

            # 筛选日期范围
            df["trade_date"] = pd.to_datetime(df["trade_date"])
            start_dt = pd.to_datetime(start_date)
            end_dt = pd.to_datetime(end_date)

            mask = (df["trade_date"] >= start_dt) & (df["trade_date"] <= end_dt)
            filtered_df = df[mask]

            metadata = {
                "source": "akshare",
                "start_date": start_date,
                "end_date": end_date,
                "trading_days": len(filtered_df),
            }

            return DataResponse.create_success(data=filtered_df, metadata=metadata)

        except Exception as e:
            error_msg = f"获取交易日历失败: {e!s}"
            return DataResponse.create_error(error_msg=error_msg)

    # =============================================================================
    # IAdvancedDataSource 实现 (可选方法)
    # =============================================================================

    def get_financial_data(self, symbol: str, period: str = "annual") -> DataResponse:
        """获取财务数据 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        if not validate_symbol(symbol):
            return DataResponse.create_error(error_msg=f"无效的股票代码格式: {symbol}")

        if period not in ["annual", "quarterly"]:
            return DataResponse.create_error(
                error_msg="period必须是'annual'或'quarterly'",
            )

        try:
            stock_code = self._format_stock_code(symbol)
            df = self.ak.stock_financial_abstract(stock=stock_code)

            if df is None or df.empty:
                return DataResponse.empty(message=f"未能获取股票 {symbol} 的财务数据")

            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "period": period,
                "report_count": len(df),
            }

            return DataResponse.create_success(data=df, metadata=metadata)

        except Exception as e:
            error_msg = f"获取财务数据失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    def get_news_data(
        self,
        symbol: Optional[str] = None,
        limit: int = 10,
    ) -> DataResponse:
        """获取新闻数据 - 重构版本"""
        if not self.available:
            return DataResponse.create_error(error_msg="Akshare不可用，请安装akshare库")

        if limit <= 0 or limit > 100:
            return DataResponse.create_error(error_msg="limit必须在1-100之间")

        try:
            if symbol and validate_symbol(symbol):
                stock_code = self._format_stock_code(symbol)
                df = self.ak.stock_news_em(symbol=stock_code, pageSize=limit)
            else:
                df = self.ak.stock_news_em(pageSize=limit)

            if df is None or df.empty:
                return DataResponse.empty(message="未能获取新闻数据")

            news_list = df.to_dict("records")

            metadata = {
                "source": "akshare",
                "symbol": symbol,
                "limit": limit,
                "news_count": len(news_list),
            }

            return DataResponse.create_success(data=news_list, metadata=metadata)

        except Exception as e:
            error_msg = f"获取新闻数据失败: {e!s}"
            return DataResponse.create_error(
                error_msg=error_msg,
                metadata={"symbol": symbol},
            )

    # =============================================================================
    # 私有辅助方法
    # =============================================================================

    def _validate_stock_inputs(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> Optional[str]:
        """验证股票数据输入参数"""
        if not validate_symbol(symbol):
            return f"无效的股票代码格式: {symbol}"

        if not validate_date(start_date):
            return f"无效的开始日期格式: {start_date}"

        if not validate_date(end_date):
            return f"无效的结束日期格式: {end_date}"

        return None

    def _format_stock_code(self, symbol: str) -> str:
        """格式化股票代码"""
        # Akshare需要的格式通常是纯数字
        return symbol

    def _format_index_code(self, symbol: str) -> str:
        """格式化指数代码"""
        # 处理指数代码格式
        if symbol.startswith(("sh", "sz")):
            return symbol
        return symbol

    def _format_dates(self, start_date: str, end_date: str) -> tuple:
        """格式化日期为Akshare需要的格式"""
        start_fmt = start_date.replace("-", "")
        end_fmt = end_date.replace("-", "")
        return start_fmt, end_fmt

    def _standardize_stock_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化股票数据格式"""
        # 确保必要的列存在并重命名
        column_mapping = {
            "日期": "date",
            "代码": "symbol",
            "开盘": "open",
            "最高": "high",
            "最低": "low",
            "收盘": "close",
            "成交量": "volume",
            "成交额": "amount",
            "涨跌幅": "pct_chg",
        }

        # 重命名列
        df_renamed = df.rename(columns=column_mapping)

        # 添加数据源标记
        df_renamed["source"] = "akshare"

        return df_renamed

    def _standardize_index_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化指数数据格式"""
        # 与股票数据类似的标准化处理
        return self._standardize_stock_data(df)


# =============================================================================
# 向后兼容性适配器
# =============================================================================


class BackwardCompatibleAkshareAdapter:
    """向后兼容性适配器

    这个类提供了从新接口到旧API的适配，
    确保现有代码可以继续工作而无需修改。
    """

    def __init__(self):
        self._adapter = RefactoredAkshareDataSource()

    def get_stock_daily(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
    ) -> pd.DataFrame:
        """旧API兼容方法"""
        response = self._adapter.get_stock_daily(symbol, start_date, end_date)
        if response.success:
            return response.data
        # 返回空DataFrame，与旧API行为一致
        return pd.DataFrame()

    def get_real_time_data(self, symbol: str) -> Union[Dict, str]:
        """旧API兼容方法"""
        response = self._adapter.get_real_time_data(symbol)
        if response.success:
            return response.data
        return {"error": response.error}


# =============================================================================
# 使用示例和测试
# =============================================================================


def test_refactored_adapter():
    """测试重构后的适配器"""
    print("=== 测试重构版Akshare适配器 ===")

    # 创建适配器实例
    adapter = RefactoredAkshareDataSource()

    if not adapter.available:
        print("❌ Akshare不可用，跳过测试")
        return

    # 测试股票日线数据
    print("\n--- 测试股票日线数据 ---")
    response = adapter.get_stock_daily("000001", "2024-01-01", "2024-01-10")

    if response.success:
        print(f"✅ 获取成功: {len(response.data)}条记录")
        print(f"📊 数据预览:\n{response.data.head()}")
        print(f"📋 元数据: {response.metadata}")
    else:
        print(f"❌ 获取失败: {response.error}")

    # 测试实时数据
    print("\n--- 测试实时数据 ---")
    response = adapter.get_real_time_data("000001")

    if response.success:
        print(f"✅ 获取成功: 股票 {response.metadata.get('symbol')}")
        print(f"💹 关键数据: {list(response.data.keys())[:5]}")
    else:
        print(f"❌ 获取失败: {response.error}")

    # 测试错误处理
    print("\n--- 测试错误处理 ---")
    response = adapter.get_stock_daily("invalid", "2024-01-01", "2024-01-10")

    if not response.success:
        print(f"✅ 错误处理正常: {response.error}")
    else:
        print("❌ 错误处理异常")


def compare_old_vs_new_api():
    """比较旧API与新API的差异"""
    print("\n=== 旧API vs 新API 对比 ===")

    # 旧API的问题
    print("\n🔴 旧API问题:")
    print("  • 返回类型不一致: 有时返回DataFrame，有时返回Dict")
    print("  • 错误处理不统一: 有些返回空DataFrame，有些抛出异常")
    print("  • 缺少元数据: 无法知道数据来源、时间等关键信息")
    print("  • 接口过于复杂: 8个方法都必须实现")

    # 新API的优势
    print("\n🟢 新API优势:")
    print("  • 统一响应格式: 所有方法返回DataResponse")
    print("  • 标准化错误处理: 明确的成功/失败状态")
    print("  • 丰富的元数据: 数据来源、时间、记录数等")
    print("  • 接口分离设计: 可只实现需要的接口")
    print("  • 向后兼容: 保持现有代码正常工作")


if __name__ == "__main__":
    # 运行测试
    test_refactored_adapter()
    compare_old_vs_new_api()

    print("\n🎉 适配器重构示例完成！")
    print("\n📋 迁移步骤总结:")
    print("1. 识别现有接口问题")
    print("2. 设计新的特化接口")
    print("3. 重构适配器实现")
    print("4. 使用统一响应格式")
    print("5. 改善错误处理")
    print("6. 保持向后兼容性")
    print("7. 全面测试验证")
