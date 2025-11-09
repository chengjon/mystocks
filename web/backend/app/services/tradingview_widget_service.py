"""
TradingView Widget 集成服务模块
实现 TradingView 图表和 widgets 的配置生成
迁移自 OpenStock 项目
"""

from typing import Dict, Any, List
import json


class TradingViewWidgetService:
    """TradingView Widget 服务"""

    @staticmethod
    def generate_chart_config(
        symbol: str,
        container_id: str = "tradingview_chart",
        interval: str = "D",
        theme: str = "dark",
        locale: str = "zh_CN",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        生成 TradingView 图表配置

        Args:
            symbol: 股票代码（如 "NASDAQ:AAPL" 或 "SSE:600000"）
            container_id: 容器 ID
            interval: 时间间隔 ("1", "5", "15", "60", "D", "W", "M")
            theme: 主题 ("light" 或 "dark")
            locale: 语言 ("zh_CN", "en")
            **kwargs: 其他自定义配置

        Returns:
            Dict: TradingView 图表配置
        """
        config = {
            "autosize": True,
            "symbol": symbol,
            "interval": interval,
            "timezone": "Asia/Shanghai",
            "theme": theme,
            "style": "1",  # 蜡烛图
            "locale": locale,
            "toolbar_bg": "#f1f3f6" if theme == "light" else "#1e222d",
            "enable_publishing": False,
            "hide_top_toolbar": False,
            "hide_legend": False,
            "save_image": False,
            "container_id": container_id,
            "withdateranges": True,
            "allow_symbol_change": True,
            "studies": [
                "MASimple@tv-basicstudies",  # 移动平均线
                "Volume@tv-basicstudies",  # 成交量
            ],
        }

        # 合并自定义配置
        config.update(kwargs)
        return config

    @staticmethod
    def generate_mini_chart_config(
        symbol: str,
        container_id: str = "tradingview_mini_chart",
        theme: str = "dark",
        locale: str = "zh_CN",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        生成 TradingView 迷你图表配置

        Args:
            symbol: 股票代码
            container_id: 容器 ID
            theme: 主题
            locale: 语言
            **kwargs: 其他自定义配置

        Returns:
            Dict: 迷你图表配置
        """
        config = {
            "symbol": symbol,
            "width": "100%",
            "height": 220,
            "locale": locale,
            "dateRange": "12M",
            "colorTheme": theme,
            "trendLineColor": "rgba(37, 99, 235, 1)",
            "underLineColor": "rgba(37, 99, 235, 0.3)",
            "underLineBottomColor": "rgba(37, 99, 235, 0)",
            "isTransparent": False,
            "autosize": True,
            "largeChartUrl": "",
            "container_id": container_id,
        }

        config.update(kwargs)
        return config

    @staticmethod
    def generate_ticker_tape_config(
        symbols: List[Dict[str, str]] = None,
        container_id: str = "tradingview_ticker_tape",
        theme: str = "dark",
        locale: str = "zh_CN",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        生成 TradingView Ticker Tape 配置

        Args:
            symbols: 股票列表 [{"proName": "NASDAQ:AAPL", "title": "Apple"}, ...]
            container_id: 容器 ID
            theme: 主题
            locale: 语言
            **kwargs: 其他自定义配置

        Returns:
            Dict: Ticker Tape 配置
        """
        if symbols is None:
            symbols = [
                {"proName": "SSE:000001", "title": "上证指数"},
                {"proName": "SZSE:399001", "title": "深证成指"},
                {"proName": "SZSE:399006", "title": "创业板指"},
                {"proName": "NASDAQ:AAPL", "title": "苹果"},
                {"proName": "NASDAQ:TSLA", "title": "特斯拉"},
            ]

        config = {
            "symbols": symbols,
            "showSymbolLogo": True,
            "colorTheme": theme,
            "isTransparent": False,
            "displayMode": "adaptive",
            "locale": locale,
            "container_id": container_id,
        }

        config.update(kwargs)
        return config

    @staticmethod
    def generate_market_overview_config(
        container_id: str = "tradingview_market_overview",
        theme: str = "dark",
        locale: str = "zh_CN",
        market: str = "china",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        生成 TradingView 市场概览配置

        Args:
            container_id: 容器 ID
            theme: 主题
            locale: 语言
            market: 市场类型 ("china", "us", "crypto")
            **kwargs: 其他自定义配置

        Returns:
            Dict: 市场概览配置
        """
        # 根据市场类型选择预设
        market_tabs = {
            "china": [
                {
                    "title": "指数",
                    "symbols": [
                        {"s": "SSE:000001", "d": "上证指数"},
                        {"s": "SZSE:399001", "d": "深证成指"},
                        {"s": "SZSE:399006", "d": "创业板指"},
                        {"s": "SSE:000688", "d": "科创50"},
                    ],
                },
                {
                    "title": "沪深热门",
                    "symbols": [
                        {"s": "SSE:600519", "d": "贵州茅台"},
                        {"s": "SZSE:000858", "d": "五粮液"},
                        {"s": "SZSE:000333", "d": "美的集团"},
                        {"s": "SSE:600036", "d": "招商银行"},
                    ],
                },
            ],
            "us": [
                {
                    "title": "指数",
                    "symbols": [
                        {"s": "FOREXCOM:SPXUSD", "d": "S&P 500"},
                        {"s": "FOREXCOM:NSXUSD", "d": "Nasdaq 100"},
                        {"s": "FOREXCOM:DJI", "d": "Dow 30"},
                    ],
                },
                {
                    "title": "科技股",
                    "symbols": [
                        {"s": "NASDAQ:AAPL", "d": "Apple"},
                        {"s": "NASDAQ:GOOGL", "d": "Alphabet"},
                        {"s": "NASDAQ:MSFT", "d": "Microsoft"},
                        {"s": "NASDAQ:TSLA", "d": "Tesla"},
                    ],
                },
            ],
            "crypto": [
                {
                    "title": "加密货币",
                    "symbols": [
                        {"s": "BINANCE:BTCUSDT", "d": "Bitcoin"},
                        {"s": "BINANCE:ETHUSDT", "d": "Ethereum"},
                        {"s": "BINANCE:BNBUSDT", "d": "BNB"},
                        {"s": "BINANCE:ADAUSDT", "d": "Cardano"},
                    ],
                }
            ],
        }

        config = {
            "colorTheme": theme,
            "dateRange": "12M",
            "showChart": True,
            "locale": locale,
            "width": "100%",
            "height": "100%",
            "largeChartUrl": "",
            "isTransparent": False,
            "showSymbolLogo": True,
            "showFloatingTooltip": False,
            "plotLineColorGrowing": "rgba(41, 98, 255, 1)",
            "plotLineColorFalling": "rgba(41, 98, 255, 1)",
            "gridLineColor": "rgba(240, 243, 250, 0)",
            "scaleFontColor": "rgba(120, 123, 134, 1)",
            "belowLineFillColorGrowing": "rgba(41, 98, 255, 0.12)",
            "belowLineFillColorFalling": "rgba(41, 98, 255, 0.12)",
            "belowLineFillColorGrowingBottom": "rgba(41, 98, 255, 0)",
            "belowLineFillColorFallingBottom": "rgba(41, 98, 255, 0)",
            "symbolActiveColor": "rgba(41, 98, 255, 0.12)",
            "tabs": market_tabs.get(market, market_tabs["china"]),
            "container_id": container_id,
        }

        config.update(kwargs)
        return config

    @staticmethod
    def generate_screener_config(
        container_id: str = "tradingview_screener",
        theme: str = "dark",
        locale: str = "zh_CN",
        market: str = "china",
        **kwargs,
    ) -> Dict[str, Any]:
        """
        生成 TradingView 股票筛选器配置

        Args:
            container_id: 容器 ID
            theme: 主题
            locale: 语言
            market: 市场类型 ("china", "america", "crypto")
            **kwargs: 其他自定义配置

        Returns:
            Dict: 筛选器配置
        """
        config = {
            "width": "100%",
            "height": 490,
            "defaultColumn": "overview",
            "defaultScreen": "general",
            "market": market,
            "showToolbar": True,
            "colorTheme": theme,
            "locale": locale,
            "container_id": container_id,
        }

        config.update(kwargs)
        return config

    @staticmethod
    def convert_symbol_to_tradingview_format(symbol: str, market: str = "CN") -> str:
        """
        将股票代码转换为 TradingView 格式

        Args:
            symbol: 股票代码（如 "600000" 或 "AAPL"）
            market: 市场类型 ("CN", "US", "HK")

        Returns:
            str: TradingView 格式的股票代码
        """
        if market == "CN":
            # A股代码转换
            if symbol.startswith("6"):
                return f"SSE:{symbol}"  # 上海证券交易所
            elif symbol.startswith("0") or symbol.startswith("3"):
                return f"SZSE:{symbol}"  # 深圳证券交易所
            elif symbol.startswith("8") or symbol.startswith("4"):
                return f"BSE:{symbol}"  # 北京证券交易所
            else:
                return f"SSE:{symbol}"
        elif market == "US":
            # 美股代码
            return f"NASDAQ:{symbol}"  # 默认 NASDAQ，也可以根据需要判断 NYSE
        elif market == "HK":
            # 港股代码
            return f"HKEX:{symbol}"
        else:
            return symbol


# 创建全局实例
_tradingview_service = None


def get_tradingview_service() -> TradingViewWidgetService:
    """
    获取 TradingView 服务实例（单例模式）

    Returns:
        TradingViewWidgetService: TradingView 服务实例
    """
    global _tradingview_service
    if _tradingview_service is None:
        _tradingview_service = TradingViewWidgetService()
    return _tradingview_service
