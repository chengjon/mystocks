"""
TDX数据服务
提供对TDX适配器的封装和缓存支持
"""

import sys
import os
import logging
from typing import Dict
from datetime import datetime

# 添加项目根目录到路径(web/backend -> mystocks_spec)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
sys.path.insert(0, project_root)

from src.adapters.tdx_adapter import TdxDataSource

logger = logging.getLogger(__name__)


class TdxService:
    """
    TDX数据服务

    功能:
    - 封装TDX适配器
    - 提供实时行情查询
    - 提供历史K线查询(多周期)
    - 提供指数行情查询
    - 数据格式标准化
    """

    def __init__(self):
        """初始化TDX服务"""
        try:
            self.tdx_adapter = TdxDataSource(use_server_config=True)
            logger.info("TDX服务初始化成功")
        except Exception as e:
            logger.error(f"TDX服务初始化失败: {e}")
            raise

    def get_real_time_quote(self, symbol: str) -> Dict:
        """
        获取实时行情

        Args:
            symbol: 股票代码(6位数字)

        Returns:
            Dict: 实时行情数据,包含计算后的涨跌幅等字段
        """
        try:
            # 调用TDX适配器
            result = self.tdx_adapter.get_real_time_data(symbol)

            # 如果返回的是字符串,说明出错了
            if isinstance(result, str):
                logger.warning(f"获取实时行情失败: {result}")
                raise ValueError(result)

            # 计算涨跌额和涨跌幅
            if result["pre_close"] > 0:
                result["change"] = round(result["price"] - result["pre_close"], 2)
                result["change_pct"] = round(
                    (result["price"] - result["pre_close"]) / result["pre_close"] * 100,
                    2,
                )
            else:
                result["change"] = 0.0
                result["change_pct"] = 0.0

            logger.info(f"获取实时行情成功: {symbol}")
            return result

        except Exception as e:
            logger.error(f"获取实时行情异常: {symbol}, 错误: {e}")
            raise

    def get_stock_kline(
        self, symbol: str, start_date: str, end_date: str, period: str = "1d"
    ) -> Dict:
        """
        获取股票K线数据

        Args:
            symbol: 股票代码(6位数字)
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            period: K线周期 ('1m', '5m', '15m', '30m', '1h', '1d')

        Returns:
            Dict: 包含K线数据列表和元信息
        """
        try:
            # 调用TDX适配器获取K线
            df = self.tdx_adapter.get_stock_kline(
                symbol=symbol, start_date=start_date, end_date=end_date, period=period
            )

            if df.empty:
                logger.warning(f"未获取到K线数据: {symbol}, {period}")
                return {"code": symbol, "period": period, "data": [], "count": 0}

            # 转换为字典列表
            data_list = []
            for _, row in df.iterrows():
                data_point = {
                    "date": str(row.get("date", "")),
                    "open": float(row.get("open", 0)),
                    "high": float(row.get("high", 0)),
                    "low": float(row.get("low", 0)),
                    "close": float(row.get("close", 0)),
                    "volume": int(row.get("volume", 0)),
                    "amount": float(row.get("amount", 0)) if "amount" in row else None,
                }
                data_list.append(data_point)

            result = {
                "code": symbol,
                "period": period,
                "data": data_list,
                "count": len(data_list),
            }

            logger.info(f"获取K线成功: {symbol}, {period}, {len(data_list)}条")
            return result

        except Exception as e:
            logger.error(f"获取K线异常: {symbol}, {period}, 错误: {e}")
            raise

    def get_index_quote(self, symbol: str) -> Dict:
        """
        获取指数实时行情

        Args:
            symbol: 指数代码(6位数字)

        Returns:
            Dict: 指数行情数据
        """
        try:
            # 调用TDX适配器(指数也用get_real_time_data)
            result = self.tdx_adapter.get_real_time_data(symbol)

            if isinstance(result, str):
                logger.warning(f"获取指数行情失败: {result}")
                raise ValueError(result)

            # 计算涨跌
            if result["pre_close"] > 0:
                result["change"] = round(result["price"] - result["pre_close"], 2)
                result["change_pct"] = round(
                    (result["price"] - result["pre_close"]) / result["pre_close"] * 100,
                    2,
                )
            else:
                result["change"] = 0.0
                result["change_pct"] = 0.0

            logger.info(f"获取指数行情成功: {symbol}")
            return result

        except Exception as e:
            logger.error(f"获取指数行情异常: {symbol}, 错误: {e}")
            raise

    def get_index_kline(
        self, symbol: str, start_date: str, end_date: str, period: str = "1d"
    ) -> Dict:
        """
        获取指数K线数据

        Args:
            symbol: 指数代码(6位数字)
            start_date: 开始日期
            end_date: 结束日期
            period: K线周期

        Returns:
            Dict: 指数K线数据
        """
        try:
            df = self.tdx_adapter.get_index_kline(
                symbol=symbol, start_date=start_date, end_date=end_date, period=period
            )

            if df.empty:
                return {"code": symbol, "period": period, "data": [], "count": 0}

            # 转换为字典列表
            data_list = []
            for _, row in df.iterrows():
                data_point = {
                    "date": str(row.get("date", "")),
                    "open": float(row.get("open", 0)),
                    "high": float(row.get("high", 0)),
                    "low": float(row.get("low", 0)),
                    "close": float(row.get("close", 0)),
                    "volume": int(row.get("volume", 0)),
                    "amount": float(row.get("amount", 0)) if "amount" in row else None,
                }
                data_list.append(data_point)

            result = {
                "code": symbol,
                "period": period,
                "data": data_list,
                "count": len(data_list),
            }

            logger.info(f"获取指数K线成功: {symbol}, {period}, {len(data_list)}条")
            return result

        except Exception as e:
            logger.error(f"获取指数K线异常: {symbol}, {period}, 错误: {e}")
            raise

    def check_connection(self) -> Dict:
        """
        检查TDX连接状态

        Returns:
            Dict: 连接状态信息
        """
        try:
            # 尝试获取上证指数作为连接测试
            result = self.tdx_adapter.get_real_time_data("000001")

            if isinstance(result, dict):
                return {
                    "status": "healthy",
                    "tdx_connected": True,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "server_info": {
                        "host": self.tdx_adapter.tdx_host,
                        "port": self.tdx_adapter.tdx_port,
                    },
                }
            else:
                return {
                    "status": "unhealthy",
                    "tdx_connected": False,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error": str(result),
                }

        except Exception as e:
            logger.error(f"TDX连接检查失败: {e}")
            return {
                "status": "unhealthy",
                "tdx_connected": False,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "error": str(e),
            }


# 单例模式
_tdx_service_instance = None


def get_tdx_service() -> TdxService:
    """
    获取TDX服务单例
    用于依赖注入
    """
    global _tdx_service_instance
    if _tdx_service_instance is None:
        _tdx_service_instance = TdxService()
    return _tdx_service_instance
