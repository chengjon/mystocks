"""
行情数据解析器
Market Data Parser - Real-time Quote Data Parsing

解析各种格式的实时行情数据，统一转换为标准格式。

Author: Claude Code
Date: 2026-01-09
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

import structlog

logger = structlog.get_logger()


@dataclass
class ParsedQuote:
    """解析后的标准行情数据"""

    symbol: str
    name: str = ""
    price: float = 0.0
    open: float = 0.0
    high: float = 0.0
    low: float = 0.0
    close: float = 0.0
    pre_close: float = 0.0
    volume: int = 0
    amount: float = 0.0
    change: float = 0.0
    change_percent: float = 0.0
    bid_price_1: float = 0.0
    bid_price_2: float = 0.0
    bid_price_3: float = 0.0
    bid_price_4: float = 0.0
    bid_price_5: float = 0.0
    ask_price_1: float = 0.0
    ask_price_2: float = 0.0
    ask_price_3: float = 0.0
    ask_price_4: float = 0.0
    ask_price_5: float = 0.0
    bid_volume_1: int = 0
    bid_volume_2: int = 0
    bid_volume_3: int = 0
    bid_volume_4: int = 0
    bid_volume_5: int = 0
    ask_volume_1: int = 0
    ask_volume_2: int = 0
    ask_volume_3: int = 0
    ask_volume_4: int = 0
    ask_volume_5: int = 0
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "symbol": self.symbol,
            "name": self.name,
            "price": self.price,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "pre_close": self.pre_close,
            "volume": self.volume,
            "amount": self.amount,
            "change": self.change,
            "change_percent": self.change_percent,
            "bid_price": [self.bid_price_1, self.bid_price_2, self.bid_price_3, self.bid_price_4, self.bid_price_5],
            "ask_price": [self.ask_price_1, self.ask_price_2, self.ask_price_3, self.ask_price_4, self.ask_price_5],
            "bid_volume": [
                self.bid_volume_1,
                self.bid_volume_2,
                self.bid_volume_3,
                self.bid_volume_4,
                self.bid_volume_5,
            ],
            "ask_volume": [
                self.ask_volume_1,
                self.ask_volume_2,
                self.ask_volume_3,
                self.ask_volume_4,
                self.ask_volume_5,
            ],
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
        }


class MarketDataParser:
    """行情数据解析器"""

    def __init__(self):
        """初始化解析器"""
        self.parsers: Dict[str, callable] = {}
        self._register_default_parsers()

    def _register_default_parsers(self):
        """注册默认解析器"""
        self.parsers["efinance"] = self._parse_efinance_data
        self.parsers["easyquotation"] = self._parse_easyquotation_data
        self.parsers["websocket"] = self._parse_websocket_data
        self.parsers["akshare"] = self._parse_akshare_data

    def register_parser(self, source: str, parser: callable) -> None:
        """注册自定义解析器"""
        self.parsers[source] = parser
        logger.info("Registered parser for source: %(source)s")

    def parse(self, data: Dict[str, Any], source: str = "auto") -> Optional[ParsedQuote]:
        """
        解析行情数据

        Args:
            data: 原始行情数据
            source: 数据源标识

        Returns:
            ParsedQuote: 解析后的标准行情数据
        """
        try:
            if source == "auto":
                source = self._detect_source(data)

            if source in self.parsers:
                parser = self.parsers[source]
                result = parser(data)
                if result:
                    result.source = source
                return result
            else:
                logger.warning("Unknown source: %(source)s, trying generic parser")
                return self._parse_generic(data)

        except Exception as e:
            logger.error("Failed to parse market data: {e}", exc_info=True)
            return None

    def parse_batch(self, data_list: List[Dict[str, Any]], source: str = "auto") -> List[ParsedQuote]:
        """
        批量解析行情数据

        Args:
            data_list: 原始行情数据列表
            source: 数据源标识

        Returns:
            List[ParsedQuote]: 解析后的标准行情数据列表
        """
        results = []
        for data in data_list:
            parsed = self.parse(data, source)
            if parsed:
                results.append(parsed)
        return results

    def _detect_source(self, data: Dict[str, Any]) -> str:
        """自动检测数据源"""
        if "最新价" in data or "涨跌幅" in data:
            return "efinance"
        if "now" in data or "close" in data:
            return "easyquotation"
        if "price" in data and "volume" in data:
            return "websocket"
        return "akshare"

    def _parse_efinance_data(self, data: Dict[str, Any]) -> Optional[ParsedQuote]:
        """解析 efinance 数据"""
        try:
            symbol = str(data.get("代码", ""))
            if not symbol:
                return None

            return ParsedQuote(
                symbol=self._normalize_symbol(symbol),
                name=str(data.get("名称", "")),
                price=self._safe_float(data.get("最新价", 0)),
                open=self._safe_float(data.get("开盘", 0)),
                high=self._safe_float(data.get("最高", 0)),
                low=self._safe_float(data.get("最低", 0)),
                close=self._safe_float(data.get("最新价", 0)),
                pre_close=self._safe_float(data.get("昨收", 0)),
                volume=self._safe_int(data.get("成交量", 0)),
                amount=self._safe_float(data.get("成交额", 0)),
                change=self._safe_float(data.get("涨跌额", 0)),
                change_percent=self._safe_float(data.get("涨跌幅", 0)),
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.error("Failed to parse efinance data: %(e)s")
            return None

    def _parse_easyquotation_data(self, data: Dict[str, Any]) -> Optional[ParsedQuote]:
        """解析 easyquotation 数据"""
        try:
            symbol = str(data.get("code", ""))
            if not symbol:
                return None

            info = data.get("info", {})

            return ParsedQuote(
                symbol=self._normalize_symbol(symbol),
                name=str(info.get("name", "")),
                price=self._safe_float(data.get("now", 0)),
                open=self._safe_float(info.get("open", 0)),
                high=self._safe_float(info.get("high", 0)),
                low=self._safe_float(info.get("low", 0)),
                close=self._safe_float(data.get("now", 0)),
                pre_close=self._safe_float(info.get("close", 0)),
                volume=self._safe_int(data.get("vol", 0)),
                amount=self._safe_float(data.get("amount", 0)),
                change=self._safe_float(info.get("change", 0)),
                change_percent=self._safe_float(info.get("pct", 0)),
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.error("Failed to parse easyquotation data: %(e)s")
            return None

    def _parse_websocket_data(self, data: Dict[str, Any]) -> Optional[ParsedQuote]:
        """解析 WebSocket 数据"""
        try:
            symbol = str(data.get("symbol", ""))
            if not symbol:
                return None

            return ParsedQuote(
                symbol=self._normalize_symbol(symbol),
                name=str(data.get("name", "")),
                price=self._safe_float(data.get("price", 0)),
                open=self._safe_float(data.get("open", 0)),
                high=self._safe_float(data.get("high", 0)),
                low=self._safe_float(data.get("low", 0)),
                close=self._safe_float(data.get("price", 0)),
                pre_close=self._safe_float(data.get("pre_close", 0)),
                volume=self._safe_int(data.get("volume", 0)),
                amount=self._safe_float(data.get("amount", 0)),
                change=self._safe_float(data.get("change", 0)),
                change_percent=self._safe_float(data.get("change_percent", 0)),
                timestamp=datetime.fromtimestamp(data.get("timestamp", datetime.now().timestamp())),
            )
        except Exception as e:
            logger.error("Failed to parse websocket data: %(e)s")
            return None

    def _parse_akshare_data(self, data: Dict[str, Any]) -> Optional[ParsedQuote]:
        """解析 akshare 数据"""
        try:
            symbol = str(data.get("symbol", ""))
            if not symbol:
                return None

            return ParsedQuote(
                symbol=self._normalize_symbol(symbol),
                name=str(data.get("name", "")),
                price=self._safe_float(data.get("close", data.get("price", 0))),
                open=self._safe_float(data.get("open", 0)),
                high=self._safe_float(data.get("high", 0)),
                low=self._safe_float(data.get("low", 0)),
                close=self._safe_float(data.get("close", 0)),
                pre_close=self._safe_float(data.get("pre_close", 0)),
                volume=self._safe_int(data.get("volume", 0)),
                amount=self._safe_float(data.get("amount", 0)),
                change=self._safe_float(data.get("change", 0)),
                change_percent=self._safe_float(data.get("pct_chg", data.get("change_percent", 0))),
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.error("Failed to parse akshare data: %(e)s")
            return None

    def _parse_generic(self, data: Dict[str, Any]) -> Optional[ParsedQuote]:
        """通用解析（尝试所有可能字段）"""
        try:
            symbol = self._extract_symbol(data)
            if not symbol:
                return None

            return ParsedQuote(
                symbol=symbol,
                name=self._extract_name(data),
                price=self._extract_price(data),
                open=self._extract_price_with_fallback(data, ["open", "开盘价", "open_price"]),
                high=self._extract_price_with_fallback(data, ["high", "最高价", "high_price"]),
                low=self._extract_price_with_fallback(data, ["low", "最低价", "low_price"]),
                close=self._extract_price_with_fallback(data, ["close", "收盘价", "close_price", "price", "最新价"]),
                pre_close=self._extract_price_with_fallback(data, ["pre_close", "昨收", "previous_close"]),
                volume=self._extract_volume(data),
                amount=self._extract_amount(data),
                change=self._extract_change(data),
                change_percent=self._extract_change_percent(data),
                timestamp=datetime.now(),
            )
        except Exception as e:
            logger.error("Failed to parse generic data: %(e)s")
            return None

    def _normalize_symbol(self, symbol: str) -> str:
        """标准化股票代码"""
        if not symbol:
            return ""

        symbol = str(symbol).strip()

        pattern = re.compile(r"^(\d{6})$")
        if pattern.match(symbol):
            return symbol

        if symbol.endswith(".SH") or symbol.endswith(".SZ"):
            return symbol[:6]

        if symbol.startswith("sh") or symbol.startswith("sz"):
            return symbol[2:8]

        if len(symbol) == 8 and symbol[0:2] in ["sh", "sz"]:
            return symbol[2:8]

        return symbol

    def _safe_float(self, value: Any) -> float:
        """安全转换为 float"""
        if value is None:
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0

    def _safe_int(self, value: Any) -> int:
        """安全转换为 int"""
        if value is None:
            return 0
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return 0

    def _extract_symbol(self, data: Dict[str, Any]) -> Optional[str]:
        """提取股票代码"""
        for key in ["symbol", "code", "代码", "股票代码", "ticker"]:
            if key in data:
                return self._normalize_symbol(str(data[key]))
        return None

    def _extract_name(self, data: Dict[str, Any]) -> str:
        """提取股票名称"""
        for key in ["name", "名称", "股票名称", "sec_name"]:
            if key in data:
                return str(data[key])
        return ""

    def _extract_price(self, data: Dict[str, Any]) -> float:
        """提取价格"""
        for key in ["price", "now", "close", "最新价", "当前价格"]:
            if key in data:
                return self._safe_float(data[key])
        return 0.0

    def _extract_price_with_fallback(self, data: Dict[str, Any], keys: List[str]) -> float:
        """提取价格（带备用键）"""
        for key in keys:
            if key in data:
                return self._safe_float(data[key])
        return 0.0

    def _extract_volume(self, data: Dict[str, Any]) -> int:
        """提取成交量"""
        for key in ["volume", "vol", "成交量", "volume"]:
            if key in data:
                return self._safe_int(data[key])
        return 0

    def _extract_amount(self, data: Dict[str, Any]) -> float:
        """提取成交额"""
        for key in ["amount", "成交额", "turnover", "turnover_vol"]:
            if key in data:
                return self._safe_float(data[key])
        return 0.0

    def _extract_change(self, data: Dict[str, Any]) -> float:
        """提取涨跌额"""
        for key in ["change", "涨跌额", "diff"]:
            if key in data:
                return self._safe_float(data[key])
        return 0.0

    def _extract_change_percent(self, data: Dict[str, Any]) -> float:
        """提取涨跌幅"""
        for key in ["change_percent", "pct_chg", "涨跌幅", "pct", "pct_change"]:
            if key in data:
                return self._safe_float(data[key])
        return 0.0


_global_parser: Optional[MarketDataParser] = None


def get_market_data_parser() -> MarketDataParser:
    """获取全局行情解析器实例"""
    global _global_parser
    if _global_parser is None:
        _global_parser = MarketDataParser()
    return _global_parser
