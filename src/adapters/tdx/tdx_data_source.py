"""
# 功能：TDX数据源 - 统一入口
# 作者：MyStocks Project
# 创建日期：2025-12-20
# 版本：1.0.0
# 说明：TDX数据源的统一入口点，整合所有TDX相关功能
"""

import pandas as pd
from typing import Dict, List, Optional, Any
from datetime import datetime
from loguru import logger

# 导入MyStocks接口
from src.interfaces.data_source import IDataSource

# 导入TDX服务模块
from .base_tdx_adapter import BaseTdxAdapter
from .kline_data_service import KlineDataService
from .realtime_service import RealtimeService


class TdxDataSource(BaseTdxAdapter, IDataSource):
    """
    TDX数据源 - 统一入口

    整合所有TDX相关功能，提供完整的数据访问接口
    保持与原始TdxAdapter的完全兼容性

    主要功能:
    - 实时行情数据获取
    - K线数据获取（多周期）
    - 股票基本信息查询
    - 行业和概念分类
    - 批量数据操作
    """

    def __init__(self):
        """初始化TDX数据源"""
        super().__init__()

        # 初始化专门的服务
        self.kline_service = KlineDataService()
        self.realtime_service = RealtimeService()

        logger.info("TDX数据源初始化完成")

    # ==================== IDataSource接口实现 ====================

    def get_data(self, params: Dict[str, Any]) -> pd.DataFrame:
        """
        获取数据的主要接口

        Args:
            params: 获取参数，包含symbol、start_date、end_date等

        Returns:
            pd.DataFrame: 获取到的数据
        """
        try:
            symbol = params.get("symbol", "")
            data_type = params.get("data_type", "daily")
            start_date = params.get("start_date")
            end_date = params.get("end_date")
            period = params.get("period", "d1")

            if not symbol:
                raise ValueError("股票代码不能为空")

            # 根据数据类型调用相应的服务
            if data_type in ["daily", "weekly", "monthly"]:
                return self.kline_service.get_stock_daily(symbol, start_date, end_date, params.get("adjust", "qfq"))
            elif data_type == "minute":
                return self.kline_service.get_minute_kline(
                    symbol,
                    period,
                    params.get("count", 240),
                    params.get("adjust", "qfq"),
                )
            elif data_type == "realtime":
                realtime_data = self.realtime_service.get_real_time_data(symbol)
                if realtime_data:
                    return pd.DataFrame([realtime_data])
                else:
                    return pd.DataFrame()
            else:
                raise ValueError(f"不支持的数据类型: {data_type}")

        except Exception as e:
            logger.error("获取数据失败: %s", e)
            return pd.DataFrame()

    def save_data(self, data: pd.DataFrame, params: Dict[str, Any]) -> bool:
        """
        保存数据到数据源

        Args:
            data: 要保存的数据
            params: 保存参数

        Returns:
            bool: 保存是否成功
        """
        # TDX主要用于数据获取，不支持数据保存
        logger.warning("TDX数据源不支持数据保存操作")
        return False

    def validate_connection(self) -> bool:
        """
        验证连接是否正常

        Returns:
            bool: 连接是否正常
        """
        try:
            # 尝试获取TDX连接
            connection = self._get_tdx_connection()
            return connection and hasattr(connection, "connected") and connection.connected
        except Exception as e:
            logger.error("TDX连接验证失败: %s", e)
            return False

    # ==================== 实时行情数据 ====================

    def get_real_time_data(self, symbol: str) -> Optional[Dict]:
        """获取实时行情数据"""
        return self.realtime_service.get_real_time_data(symbol)

    def get_stock_basic(self, symbol: str) -> Dict:
        """获取股票基本信息"""
        return self.realtime_service.get_stock_basic(symbol)

    def get_batch_real_time_data(self, symbols: List[str]) -> List[Dict]:
        """批量获取实时行情数据"""
        return self.realtime_service.get_batch_real_time_data(symbols)

    def get_industry_classify(self) -> pd.DataFrame:
        """获取行业分类数据"""
        return self.realtime_service.get_industry_classify()

    def get_concept_classify(self) -> pd.DataFrame:
        """获取概念分类数据"""
        return self.realtime_service.get_concept_classify()

    def get_stock_industry_concept(self, symbol: str) -> Dict:
        """获取股票的行业和概念信息"""
        return self.realtime_service.get_stock_industry_concept(symbol)

    # ==================== K线数据 ====================

    def get_stock_daily(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "qfq",
    ) -> pd.DataFrame:
        """获取股票日线数据"""
        return self.kline_service.get_stock_daily(symbol, start_date, end_date, adjust)

    def get_index_daily(
        self,
        index_code: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> pd.DataFrame:
        """获取指数日线数据"""
        return self.kline_service.get_index_daily(index_code, start_date, end_date)

    def get_stock_kline(
        self,
        symbol: str,
        period: str = "d1",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        adjust: str = "qfq",
    ) -> Dict:
        """获取股票K线数据（多种周期）"""
        return self.kline_service.get_stock_kline(symbol, period, start_date, end_date, adjust)

    def get_index_kline(
        self,
        index_code: str,
        period: str = "d1",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict:
        """获取指数K线数据（多种周期）"""
        return self.kline_service.get_index_kline(index_code, period, start_date, end_date)

    def get_minute_kline(
        self, symbol: str, period: str = "1min", count: int = 240, adjust: str = "qfq"
    ) -> pd.DataFrame:
        """获取分钟K线数据"""
        return self.kline_service.get_minute_kline(symbol, period, count, adjust)

    # ==================== 高级功能 ====================

    def get_market_overview(self) -> Dict:
        """获取市场概览信息"""
        try:
            # 获取主要指数数据
            major_indices = [
                "000001",
                "399001",
                "399006",
            ]  # 上证指数、深证成指、创业板指

            overview = {
                "timestamp": datetime.now().isoformat(),
                "indices": [],
                "market_status": "开市中" if self._is_trading_time() else "休市",
                "source": "tdx",
            }

            for index_code in major_indices:
                try:
                    index_data = self.get_real_time_data(index_code)
                    if index_data:
                        overview["indices"].append(
                            {
                                "code": index_code,
                                "name": index_data.get("name", ""),
                                "price": index_data.get("price", 0),
                                "change": index_data.get("change", 0),
                                "change_pct": index_data.get("change_pct", 0),
                            }
                        )
                except Exception as e:
                    logger.warning("获取指数 %s 数据失败: %s", index_code, e)

            return overview

        except Exception as e:
            logger.error("获取市场概览失败: %s", e)
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    def get_hot_stocks(self, limit: int = 20) -> List[Dict]:
        """获取热门股票列表"""
        try:
            # 获取沪深两市涨幅榜前N名
            # 这里简化实现，实际可以从涨跌排行获取
            hot_stocks = []

            # 示例：获取部分热门股票的实时数据
            sample_symbols = ["000001", "000002", "600000", "600036", "000858"]

            for symbol in sample_symbols[:limit]:
                try:
                    stock_data = self.get_real_time_data(symbol)
                    if stock_data:
                        hot_stocks.append(
                            {
                                "symbol": symbol,
                                "name": stock_data.get("name", ""),
                                "price": stock_data.get("price", 0),
                                "change_pct": stock_data.get("change_pct", 0),
                                "volume": stock_data.get("volume", 0),
                                "market": stock_data.get("market", ""),
                            }
                        )
                except Exception as e:
                    logger.warning("获取股票 %s 数据失败: %s", symbol, e)

            # 按涨幅排序
            hot_stocks.sort(key=lambda x: x.get("change_pct", 0), reverse=True)

            return hot_stocks

        except Exception as e:
            logger.error("获取热门股票失败: %s", e)
            return []

    def search_stocks(self, keyword: str, limit: int = 10) -> List[Dict]:
        """搜索股票"""
        try:
            if not keyword:
                return []

            results = []

            # 简化的股票搜索实现
            # 实际应用中可以从股票列表中搜索
            sample_stocks = [
                {"code": "000001", "name": "平安银行", "market": "深交所"},
                {"code": "000002", "name": "万科A", "market": "深交所"},
                {"code": "600000", "name": "浦发银行", "market": "上交所"},
                {"code": "600036", "name": "招商银行", "market": "上交所"},
                {"code": "000858", "name": "五粮液", "market": "深交所"},
            ]

            for stock in sample_stocks:
                if keyword in stock["code"] or keyword in stock["name"]:
                    results.append(stock)
                    if len(results) >= limit:
                        break

            return results

        except Exception as e:
            logger.error("搜索股票失败: %s", e)
            return []

    def _is_trading_time(self) -> bool:
        """判断当前是否为交易时间"""
        try:
            now = datetime.now()

            # 周末不交易
            if now.weekday() >= 5:  # 周六、周日
                return False

            # 检查交易时间
            current_time = now.time()

            # 上午交易时间：9:30-11:30
            morning_start = datetime.strptime("09:30", "%H:%M").time()
            morning_end = datetime.strptime("11:30", "%H:%M").time()

            # 下午交易时间：13:00-15:00
            afternoon_start = datetime.strptime("13:00", "%H:%M").time()
            afternoon_end = datetime.strptime("15:00", "%H:%M").time()

            return morning_start <= current_time <= morning_end or afternoon_start <= current_time <= afternoon_end

        except Exception as e:
            logger.error("判断交易时间失败: %s", e)
            return False

    # ==================== 统计和诊断功能 ====================

    def get_connection_status(self) -> Dict:
        """获取连接状态信息"""
        try:
            connection = self._get_tdx_connection()

            return {
                "connected": connection and hasattr(connection, "connected") and connection.connected,
                "server": f"{self.tdx_host}:{self.tdx_port}",
                "server_config": self.server_config is not None,
                "services": {
                    "kline_service": self.kline_service is not None,
                    "realtime_service": self.realtime_service is not None,
                },
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            return {
                "connected": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def test_data_access(self, test_symbol: str = "000001") -> Dict:
        """测试数据访问功能"""
        try:
            test_results = {
                "symbol": test_symbol,
                "tests": {},
                "timestamp": datetime.now().isoformat(),
            }

            # 测试连接
            test_results["tests"]["connection"] = self.validate_connection()

            # 测试实时数据
            try:
                realtime_data = self.get_real_time_data(test_symbol)
                test_results["tests"]["realtime_data"] = realtime_data is not None
            except Exception as e:
                test_results["tests"]["realtime_data"] = False
                test_results["tests"]["realtime_error"] = str(e)

            # 测试K线数据
            try:
                kline_data = self.get_stock_daily(test_symbol)
                test_results["tests"]["kline_data"] = len(kline_data) > 0
            except Exception as e:
                test_results["tests"]["kline_data"] = False
                test_results["tests"]["kline_error"] = str(e)

            # 测试基本信息
            try:
                basic_info = self.get_stock_basic(test_symbol)
                test_results["tests"]["basic_info"] = len(basic_info) > 0
            except Exception as e:
                test_results["tests"]["basic_info"] = False
                test_results["tests"]["basic_error"] = str(e)

            return test_results

        except Exception as e:
            return {
                "symbol": test_symbol,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    # ==================== 向后兼容性方法 ====================
    # 保持与原始TdxAdapter的完全兼容

    def get_security_quotes(self, symbols: List[str], markets: List[int]) -> List[Dict]:
        """获取股票行情（兼容原接口）"""
        return self.get_batch_real_time_data(symbols)

    def get_kline_data(
        self,
        symbol: str,
        start_date: str,
        end_date: str,
        period: str = "1d",
        adjustflag: int = 1,
    ) -> pd.DataFrame:
        """获取K线数据（兼容原接口）"""
        adjust = "qfq" if adjustflag == 1 else ("hfq" if adjustflag == 2 else "none")

        if period == "1d":
            return self.get_stock_daily(symbol, start_date, end_date, adjust)
        elif period == "1w":
            return self.get_stock_kline(symbol, "w1", start_date, end_date, adjust)
        elif period == "1m":
            return self.get_stock_kline(symbol, "m1", start_date, end_date, adjust)
        else:
            raise ValueError(f"不支持的周期: {period}")

    def get_stock_list(self, market: int = 0) -> List[Dict]:
        """获取股票列表（兼容原接口）"""
        try:
            # 获取TDX连接
            tdx_api = self._get_tdx_connection()

            # 获取股票列表
            data = tdx_api.get_security_list(market, 1)

            if not data:
                return []

            return data

        except Exception as e:
            logger.error("获取股票列表失败: %s", e)
            return []
