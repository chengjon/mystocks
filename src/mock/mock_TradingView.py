"""
Mock数据文件: TradingView
提供接口:
1. get_chart_config() -> Dict - 获取TradingView图表配置
2. get_mini_chart_config() -> Dict - 获取迷你图表配置
3. get_ticker_tape_config() -> Dict - 获取滚动行情配置
4. get_market_overview_config() -> Dict - 获取市场概览配置
5. get_screener_config() -> Dict - 获取股票筛选器配置
6. convert_symbol() -> Dict - 转换股票代码格式

使用说明:
- 所有函数参数需与真实API接口完全对齐
- 返回值字段名需与前端表格列字段一致
- 股票价格保留2位小数，百分比保留4位小数
- 时间字段使用datetime类型，格式：YYYY-MM-DD HH:MM:SS

作者: Claude Code
生成时间: 2025-11-13
"""

from typing import Dict, List, Optional


def get_chart_config(
    symbol: str = "600519",
    market: str = "CN",
    interval: str = "D",
    theme: str = "dark",
    locale: str = "zh_CN",
    container_id: str = "tradingview_chart",
) -> Dict:
    """获取TradingView图表配置

    Args:
        symbol: str - 股票代码
        market: str - 市场类型: CN, US, HK
        interval: str - 时间间隔: 1, 5, 15, 60, D, W, M
        theme: str - 主题: light, dark
        locale: str - 语言: zh_CN, en
        container_id: str - 容器ID

    Returns:
        Dict: TradingView图表配置，包含：
             - symbol: TradingView格式的股票代码
             - interval: 时间间隔
             - container: 容器配置
             - overrides: 样式覆盖
             - studies: 研究指标
    """
    # 转换股票代码为TradingView格式
    tv_symbol = convert_symbol_format(symbol, market)

    # 生成图表配置
    config = {
        "width": "100%",
        "height": 500,
        "symbol": tv_symbol,
        "interval": interval,
        "timezone": "Etc/UTC",
        "theme": theme,
        "style": "1",  # 蜡烛图样式
        "locale": locale,
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": False,
        "allow_symbol_change": True,
        "save_image": False,
        "container_id": container_id,
        "studies": [
            "MASimple@tv-basicstudies",
            "RSI@tv-basicstudies",
            "MACD@tv-basicstudies",
        ],
        "overrides": {
            "paneProperties.background": "#ffffff" if theme == "light" else "#131722",
            "paneProperties.vertGridProperties.color": "#E6E9EF" if theme == "light" else "#2A2E39",
            "paneProperties.horzGridProperties.color": "#E6E9EF" if theme == "light" else "#2A2E39",
            "symbolWatermarkProperties.transparency": 90,
            "scalesProperties.textColor": "#AAA" if theme == "dark" else "#666",
        },
    }

    return config


def get_mini_chart_config(
    symbol: str = "600519",
    market: str = "CN",
    theme: str = "dark",
    locale: str = "zh_CN",
    container_id: str = "tradingview_mini_chart",
) -> Dict:
    """获取TradingView迷你图表配置

    Args:
        symbol: str - 股票代码
        market: str - 市场类型
        theme: str - 主题
        locale: str - 语言
        container_id: str - 容器ID

    Returns:
        Dict: 迷你图表配置
    """
    tv_symbol = convert_symbol_format(symbol, market)

    config = {
        "width": 200,
        "height": 100,
        "symbol": tv_symbol,
        "interval": "D",
        "timezone": "Etc/UTC",
        "theme": theme,
        "style": "1",
        "locale": locale,
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": False,
        "hide_side_toolbar": True,
        "container_id": container_id,
        "overrides": {
            "mainSeriesProperties.candleStyle.borderDownColor": "#FF6B6B",
            "mainSeriesProperties.candleStyle.borderUpColor": "#51CF66",
            "mainSeriesProperties.candleStyle.wickDownColor": "#FF6B6B",
            "mainSeriesProperties.candleStyle.wickUpColor": "#51CF66",
        },
    }

    return config


def get_ticker_tape_config(
    symbols: Optional[List[Dict]] = None,
    theme: str = "dark",
    locale: str = "zh_CN",
    container_id: str = "tradingview_ticker_tape",
) -> Dict:
    """获取滚动行情配置

    Args:
        symbols: Optional[List[Dict]] - 股票列表 [{"proName": "NASDAQ:AAPL", "title": "Apple"}]
        theme: str - 主题
        locale: str - 语言
        container_id: str - 容器ID

    Returns:
        Dict: 滚动行情配置
    """
    # 默认股票列表
    if not symbols:
        symbols = [
            {"proName": "SSE:600519", "title": "贵州茅台"},
            {"proName": "SSE:600036", "title": "招商银行"},
            {"proName": "SZSE:000001", "title": "平安银行"},
            {"proName": "SSE:600276", "title": "恒瑞医药"},
            {"proName": "SZSE:000858", "title": "五粮液"},
        ]

    config = {
        "symbols": symbols,
        "showSymbolLogo": True,
        "colorTheme": theme,
        "isTransparent": False,
        "displayMode": "adaptive",
        "locale": locale,
        "container_id": container_id,
        "autosize": True,
        "largeChartUrl": "",
        "width": "100%",
        "height": 80,
    }

    return config


def get_market_overview_config(
    market: str = "china",
    theme: str = "dark",
    locale: str = "zh_CN",
    container_id: str = "tradingview_market_overview",
) -> Dict:
    """获取市场概览配置

    Args:
        market: str - 市场类型: china, us, crypto
        theme: str - 主题
        locale: str - 语言
        container_id: str - 容器ID

    Returns:
        Dict: 市场概览配置
    """
    # 根据市场类型设置不同的板块
    if market == "china":
        tabs = [
            {
                "title": "A股",
                "symbols": [
                    {"s": "SSE:000001", "d": "平安银行"},
                    {"s": "SSE:600519", "d": "贵州茅台"},
                    {"s": "SSE:600036", "d": "招商银行"},
                    {"s": "SZSE:000002", "d": "万科A"},
                    {"s": "SZSE:000858", "d": "五粮液"},
                ],
            },
            {
                "title": "指数",
                "symbols": [
                    {"s": "SSE:000001", "d": "上证指数"},
                    {"s": "SZSE:399001", "d": "深证成指"},
                    {"s": "SSE:000688", "d": "科创50"},
                ],
            },
        ]
    elif market == "us":
        tabs = [
            {
                "title": "美股",
                "symbols": [
                    {"s": "NASDAQ:AAPL", "d": "Apple"},
                    {"s": "NASDAQ:MSFT", "d": "Microsoft"},
                    {"s": "NASDAQ:GOOGL", "d": "Google"},
                ],
            }
        ]
    else:  # crypto
        tabs = [
            {
                "title": "加密货币",
                "symbols": [
                    {"s": "BINANCE:BTCUSDT", "d": "Bitcoin"},
                    {"s": "BINANCE:ETHUSDT", "d": "Ethereum"},
                ],
            }
        ]

    config = {
        "tabs": tabs,
        "colorTheme": theme,
        "isTransparent": False,
        "autosize": True,
        "locale": locale,
        "container_id": container_id,
        "largeChartUrl": "",
        "width": "100%",
        "height": 400,
    }

    return config


def get_screener_config(
    market: str = "china",
    theme: str = "dark",
    locale: str = "zh_CN",
    container_id: str = "tradingview_screener",
) -> Dict:
    """获取股票筛选器配置

    Args:
        market: str - 市场类型: china, america, crypto
        theme: str - 主题
        locale: str - 语言
        container_id: str - 容器ID

    Returns:
        Dict: 股票筛选器配置
    """
    # 根据市场类型设置筛选器
    if market == "china":
        filters = [
            {"left": "name", "operation": "contains", "right": "股票"},
            {"left": "exchange", "operation": "equal", "right": "上海证券交易所"},
        ]
        symbols = [
            "SSE:600519",
            "SSE:600036",
            "SSE:600276",
            "SSE:600000",
            "SZSE:000001",
            "SZSE:000002",
            "SZSE:000858",
        ]
    elif market == "america":
        filters = [
            {
                "left": "market_cap_basic",
                "operation": "greater",
                "right": 1000000000,  # 10亿
            }
        ]
        symbols = [
            "NASDAQ:AAPL",
            "NASDAQ:MSFT",
            "NASDAQ:GOOGL",
            "NYSE:TSLA",
            "NYSE:JPM",
        ]
    else:  # crypto
        filters = [
            {
                "left": "market_cap",
                "operation": "greater",
                "right": 1000000000,  # 10亿
            }
        ]
        symbols = ["BINANCE:BTCUSDT", "BINANCE:ETHUSDT", "BINANCE:BNBUSDT"]

    config = {
        "width": "100%",
        "height": 600,
        "defaultColumn": "overview",
        "defaultScreen": "general",
        "market": market,
        "showToolbar": True,
        "colorTheme": theme,
        "locale": locale,
        "container_id": container_id,
        "filters": filters,
        "symbols": symbols,
        "enableScrolling": True,
        "save_image": False,
    }

    return config


def convert_symbol_format(symbol: str, market: str) -> Dict:
    """转换股票代码格式

    Args:
        symbol: str - 股票代码
        market: str - 市场类型

    Returns:
        Dict: 转换后的代码信息
    """
    # 股票代码映射
    symbol_mapping = {
        ("600519", "CN"): "SSE:600519",
        ("600036", "CN"): "SSE:600036",
        ("000001", "CN"): "SZSE:000001",
        ("000002", "CN"): "SZSE:000002",
        ("000858", "CN"): "SZSE:000858",
        ("600276", "CN"): "SSE:600276",
        ("600000", "CN"): "SSE:600000",
        ("AAPL", "US"): "NASDAQ:AAPL",
        ("MSFT", "US"): "NASDAQ:MSFT",
        ("GOOGL", "US"): "NASDAQ:GOOGL",
    }

    key = (symbol, market)
    tradingview_symbol = symbol_mapping.get(key, f"SSE:{symbol}")

    # 生成显示名称
    display_names = {
        "SSE:600519": "贵州茅台",
        "SSE:600036": "招商银行",
        "SZSE:000001": "平安银行",
        "SZSE:000002": "万科A",
        "SZSE:000858": "五粮液",
        "SSE:600276": "恒瑞医药",
        "SSE:600000": "浦发银行",
    }

    display_name = display_names.get(tradingview_symbol, f"股票{symbol}")

    return {
        "original_symbol": symbol,
        "tradingview_symbol": tradingview_symbol,
        "display_name": display_name,
        "market": market,
        "exchange": "SSE" if symbol.startswith("6") else "SZSE" if symbol.startswith("0") else "Unknown",
    }


def get_symbol_list_by_market(market: str = "china", limit: int = 10) -> List[Dict]:
    """根据市场获取股票列表

    Args:
        market: str - 市场类型
        limit: int - 返回数量限制

    Returns:
        List[Dict]: 股票列表
    """
    if market == "china":
        stock_list = [
            {"symbol": "600519", "name": "贵州茅台", "exchange": "SSE"},
            {"symbol": "600036", "name": "招商银行", "exchange": "SSE"},
            {"symbol": "000001", "name": "平安银行", "exchange": "SZSE"},
            {"symbol": "000002", "name": "万科A", "exchange": "SZSE"},
            {"symbol": "000858", "name": "五粮液", "exchange": "SZSE"},
            {"symbol": "600276", "name": "恒瑞医药", "exchange": "SSE"},
            {"symbol": "600000", "name": "浦发银行", "exchange": "SSE"},
            {"symbol": "600887", "name": "伊利股份", "exchange": "SSE"},
            {"symbol": "600104", "name": "上汽集团", "exchange": "SSE"},
            {"symbol": "600585", "name": "海螺水泥", "exchange": "SSE"},
        ]
    elif market == "america":
        stock_list = [
            {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "NASDAQ"},
            {"symbol": "MSFT", "name": "Microsoft Corporation", "exchange": "NASDAQ"},
            {"symbol": "GOOGL", "name": "Alphabet Inc.", "exchange": "NASDAQ"},
            {"symbol": "TSLA", "name": "Tesla, Inc.", "exchange": "NASDAQ"},
            {"symbol": "AMZN", "name": "Amazon.com, Inc.", "exchange": "NASDAQ"},
            {"symbol": "META", "name": "Meta Platforms, Inc.", "exchange": "NASDAQ"},
            {"symbol": "NVDA", "name": "NVIDIA Corporation", "exchange": "NASDAQ"},
            {"symbol": "JPM", "name": "JPMorgan Chase & Co.", "exchange": "NYSE"},
            {"symbol": "JNJ", "name": "Johnson & Johnson", "exchange": "NYSE"},
            {"symbol": "V", "name": "Visa Inc.", "exchange": "NYSE"},
        ]
    else:  # crypto
        stock_list = [
            {"symbol": "BTCUSDT", "name": "Bitcoin", "exchange": "BINANCE"},
            {"symbol": "ETHUSDT", "name": "Ethereum", "exchange": "BINANCE"},
            {"symbol": "BNBUSDT", "name": "BNB", "exchange": "BINANCE"},
            {"symbol": "ADAUSDT", "name": "Cardano", "exchange": "BINANCE"},
            {"symbol": "SOLUSDT", "name": "Solana", "exchange": "BINANCE"},
            {"symbol": "DOTUSDT", "name": "Polkadot", "exchange": "BINANCE"},
            {"symbol": "AVAXUSDT", "name": "Avalanche", "exchange": "BINANCE"},
            {"symbol": "LINKUSDT", "name": "Chainlink", "exchange": "BINANCE"},
            {"symbol": "MATICUSDT", "name": "Polygon", "exchange": "BINANCE"},
            {"symbol": "UNIUSDT", "name": "Uniswap", "exchange": "BINANCE"},
        ]

    return stock_list[:limit]


def get_chart_studies(theme: str = "dark") -> Dict:
    """获取图表研究指标

    Args:
        theme: str - 主题

    Returns:
        Dict: 研究指标配置
    """
    # 研究指标配置
    studies = {
        "overrides": {
            "bollingerBands30.upper.line.color": "#FF6B6B" if theme == "dark" else "#FF6B6B",
            "bollingerBands30.lower.line.color": "#51CF66" if theme == "dark" else "#51CF66",
            "bollingerBands20.middle.line.color": "#339AF0" if theme == "dark" else "#339AF0",
            "bollingerBands20.upper.line.color": "#FF6B6B" if theme == "dark" else "#FF6B6B",
            "bollingerBands20.lower.line.color": "#51CF66" if theme == "dark" else "#51CF66",
        },
        "comparisons": [
            {
                "symbol": "SSE:000001",  # 上证指数作为对比
                "displayName": "上证指数",
                "color": "#339AF0",
            }
        ],
        "scalesProperties": {
            "scaleProperties.backgroundColor": "#ffffff" if theme == "light" else "#131722",
            "scaleProperties.fontFamily": "Segoe UI, Roboto, Arial, sans-serif",
            "scaleProperties.fontSize": 12,
            "scaleProperties.lineColor": "#E6E9EF" if theme == "light" else "#2A2E39",
            "scaleProperties.textColor": "#AAA" if theme == "dark" else "#666",
        },
        "paneProperties": {
            "backgroundType": "solid",
            "background": "#ffffff" if theme == "light" else "#131722",
            "backgroundTopColor": "#ffffff" if theme == "light" else "#131722",
            "backgroundBottomColor": "#ffffff" if theme == "light" else "#131722",
            "backgroundLeftColor": "#ffffff" if theme == "light" else "#131722",
            "backgroundRightColor": "#ffffff" if theme == "light" else "#131722",
            "backgroundAllColors": "#ffffff" if theme == "light" else "#131722",
            "backgroundGradientStartColor": "#ffffff" if theme == "light" else "#131722",
            "backgroundGradientEndColor": "#ffffff" if theme == "light" else "#131722",
            "vertGridProperties": {
                "color": "#E6E9EF" if theme == "light" else "#2A2E39",
                "style": 0,
                "visible": True,
            },
            "horzGridProperties": {
                "color": "#E6E9EF" if theme == "light" else "#2A2E39",
                "style": 0,
                "visible": True,
            },
            "crossHairProperties": {
                "color": "#989898",
                "style": 2,
                "transparency": 0,
                "width": 1,
            },
        },
    }

    return studies


if __name__ == "__main__":
    # 测试函数
    print("Mock TradingView模块测试")
    print("=" * 50)

    print("1. 测试图表配置:")
    chart_config = get_chart_config(symbol="600519", market="CN")
    print(f"   图表配置生成成功，容器ID: {chart_config['container_id']}")

    print("\n2. 测试迷你图表配置:")
    mini_config = get_mini_chart_config(symbol="000001", market="CN")
    print(f"   迷你图表配置生成成功，尺寸: {mini_config['width']}x{mini_config['height']}")

    print("\n3. 测试滚动行情配置:")
    ticker_config = get_ticker_tape_config()
    print(f"   滚动行情配置生成成功，包含 {len(ticker_config['symbols'])} 只股票")

    print("\n4. 测试市场概览配置:")
    overview_config = get_market_overview_config(market="china")
    print(f"   市场概览配置生成成功，包含 {len(overview_config['tabs'])} 个标签页")

    print("\n5. 测试股票筛选器配置:")
    screener_config = get_screener_config(market="china")
    print(f"   筛选器配置生成成功，高度: {screener_config['height']}")

    print("\n6. 测试代码转换:")
    converted = convert_symbol_format("600519", "CN")
    print(f"   代码转换结果: {converted['original_symbol']} -> {converted['tradingview_symbol']}")

    print("\n测试完成！")
