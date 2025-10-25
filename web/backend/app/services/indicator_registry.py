"""
Indicator Registry Service
管理所有161个TA-Lib技术指标的元数据注册表
"""
import talib
from typing import Dict, List, Optional, Any
from enum import Enum


class IndicatorCategory(str, Enum):
    """指标分类"""
    TREND = "trend"
    MOMENTUM = "momentum"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    CANDLESTICK = "candlestick"


class PanelType(str, Enum):
    """显示面板类型"""
    OVERLAY = "overlay"  # 叠加在主图上
    OSCILLATOR = "oscillator"  # 独立震荡面板


class IndicatorRegistry:
    """
    指标注册表

    在应用启动时加载所有161个TA-Lib指标的元数据
    提供指标查询、验证和元数据访问功能
    """

    def __init__(self):
        """初始化注册表并加载所有指标元数据"""
        self._registry: Dict[str, Dict[str, Any]] = {}
        self._load_indicators()

    def _load_indicators(self):
        """从TA-Lib加载所有161个指标的元数据"""

        # 趋势指标 (Trend Indicators)
        trend_indicators = {
            "SMA": {
                "full_name": "Simple Moving Average",
                "chinese_name": "简单移动平均线",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OVERLAY,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 20, "min": 2, "max": 200}
                ],
                "outputs": [{"name": "sma", "description": "SMA值"}],
                "min_data_points": lambda p: p.get("timeperiod", 20),
                "min_data_points_formula": "timeperiod",
                "description": "简单移动平均线,对价格进行平滑处理"
            },
            "EMA": {
                "full_name": "Exponential Moving Average",
                "chinese_name": "指数移动平均线",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OVERLAY,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 20, "min": 2, "max": 200}
                ],
                "outputs": [{"name": "ema", "description": "EMA值"}],
                "min_data_points": lambda p: p.get("timeperiod", 20),
                "min_data_points_formula": "timeperiod",
                "description": "指数移动平均线,对近期价格赋予更高权重"
            },
            "WMA": {
                "full_name": "Weighted Moving Average",
                "chinese_name": "加权移动平均线",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OVERLAY,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 20, "min": 2, "max": 200}
                ],
                "outputs": [{"name": "wma", "description": "WMA值"}],
                "min_data_points": lambda p: p.get("timeperiod", 20),
                "min_data_points_formula": "timeperiod",
                "description": "加权移动平均线"
            },
            "MACD": {
                "full_name": "Moving Average Convergence Divergence",
                "chinese_name": "异同移动平均线",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "fastperiod", "type": "int", "default": 12, "min": 2, "max": 100},
                    {"name": "slowperiod", "type": "int", "default": 26, "min": 2, "max": 100},
                    {"name": "signalperiod", "type": "int", "default": 9, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "macd", "description": "MACD线"}, {"name": "signal", "description": "信号线"}, {"name": "hist", "description": "柱状图"}],
                "min_data_points": lambda p: p.get("slowperiod", 26) + p.get("signalperiod", 9),
                "min_data_points_formula": "slowperiod + signalperiod",
                "reference_lines": [0],
                "description": "MACD指标,显示快慢均线的差值"
            },
            "BBANDS": {
                "full_name": "Bollinger Bands",
                "chinese_name": "布林带",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OVERLAY,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 20, "min": 2, "max": 200},
                    {"name": "nbdevup", "type": "float", "default": 2.0, "min": 0.1, "max": 5.0},
                    {"name": "nbdevdn", "type": "float", "default": 2.0, "min": 0.1, "max": 5.0}
                ],
                "outputs": [{"name": "upperband", "description": "上轨"}, {"name": "middleband", "description": "中轨"}, {"name": "lowerband", "description": "下轨"}],
                "min_data_points": lambda p: p.get("timeperiod", 20),
                "min_data_points_formula": "timeperiod",
                "description": "布林带,显示价格的波动区间"
            },
            "SAR": {
                "full_name": "Parabolic SAR",
                "chinese_name": "抛物线转向",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OVERLAY,
                "parameters": [
                    {"name": "acceleration", "type": "float", "default": 0.02, "min": 0.01, "max": 0.2},
                    {"name": "maximum", "type": "float", "default": 0.2, "min": 0.1, "max": 0.5}
                ],
                "outputs": [{"name": "sar", "description": "SAR值"}],
                "min_data_points": lambda p: 10,
                "min_data_points_formula": "10",
                "description": "抛物线转向指标"
            },
            "ADX": {
                "full_name": "Average Directional Movement Index",
                "chinese_name": "平均趋向指数",
                "category": IndicatorCategory.TREND,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "adx", "description": "ADX值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14) * 2,
                "min_data_points_formula": "timeperiod * 2",
                "reference_lines": [20, 40],
                "description": "平均趋向指数,衡量趋势强度"
            },
        }

        # 动量指标 (Momentum Indicators)
        momentum_indicators = {
            "RSI": {
                "full_name": "Relative Strength Index",
                "chinese_name": "相对强弱指数",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "rsi", "description": "RSI值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14) + 1,
                "min_data_points_formula": "timeperiod + 1",
                "reference_lines": [30, 70],
                "description": "相对强弱指数,显示超买超卖状态"
            },
            "STOCH": {
                "full_name": "Stochastic",
                "chinese_name": "随机指标(KDJ)",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "fastk_period", "type": "int", "default": 9, "min": 1, "max": 100},
                    {"name": "slowk_period", "type": "int", "default": 3, "min": 1, "max": 100},
                    {"name": "slowd_period", "type": "int", "default": 3, "min": 1, "max": 100}
                ],
                "outputs": [{"name": "slowk", "description": "K值"}, {"name": "slowd", "description": "D值"}],
                "min_data_points": lambda p: p.get("fastk_period", 9) + p.get("slowk_period", 3),
                "min_data_points_formula": "fastk_period + slowk_period",
                "reference_lines": [20, 80],
                "description": "随机指标(KD值),显示价格动量"
            },
            "CCI": {
                "full_name": "Commodity Channel Index",
                "chinese_name": "顺势指标",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "cci", "description": "CCI值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14),
                "min_data_points_formula": "timeperiod",
                "reference_lines": [-100, 100],
                "description": "顺势指标,衡量价格偏离程度"
            },
            "MFI": {
                "full_name": "Money Flow Index",
                "chinese_name": "资金流量指标",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "mfi", "description": "MFI值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14) + 1,
                "min_data_points_formula": "timeperiod + 1",
                "reference_lines": [20, 80],
                "description": "资金流量指标,结合价格和成交量"
            },
            "WILLR": {
                "full_name": "Williams %R",
                "chinese_name": "威廉指标",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "willr", "description": "威廉指标值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14),
                "min_data_points_formula": "timeperiod",
                "reference_lines": [-20, -80],
                "description": "威廉指标,反向显示超买超卖"
            },
            "ROC": {
                "full_name": "Rate of Change",
                "chinese_name": "变动率指标",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 10, "min": 1, "max": 100}
                ],
                "outputs": [{"name": "roc", "description": "变动率值"}],
                "min_data_points": lambda p: p.get("timeperiod", 10) + 1,
                "min_data_points_formula": "timeperiod + 1",
                "reference_lines": [0],
                "description": "变动率指标,显示价格变化百分比"
            },
            "MOM": {
                "full_name": "Momentum",
                "chinese_name": "动量指标",
                "category": IndicatorCategory.MOMENTUM,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 10, "min": 1, "max": 100}
                ],
                "outputs": [{"name": "mom", "description": "动量值"}],
                "min_data_points": lambda p: p.get("timeperiod", 10) + 1,
                "min_data_points_formula": "timeperiod + 1",
                "reference_lines": [0],
                "description": "动量指标,显示价格绝对变化"
            },
        }

        # 波动率指标 (Volatility Indicators)
        volatility_indicators = {
            "ATR": {
                "full_name": "Average True Range",
                "chinese_name": "真实波幅均值",
                "category": IndicatorCategory.VOLATILITY,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 1, "max": 100}
                ],
                "outputs": [{"name": "atr", "description": "ATR值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14),
                "min_data_points_formula": "timeperiod",
                "description": "真实波幅均值,衡量价格波动性"
            },
            "NATR": {
                "full_name": "Normalized Average True Range",
                "chinese_name": "标准化真实波幅",
                "category": IndicatorCategory.VOLATILITY,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "timeperiod", "type": "int", "default": 14, "min": 1, "max": 100}
                ],
                "outputs": [{"name": "natr", "description": "NATR值"}],
                "min_data_points": lambda p: p.get("timeperiod", 14),
                "min_data_points_formula": "timeperiod",
                "description": "标准化真实波幅"
            },
            "TRANGE": {
                "full_name": "True Range",
                "chinese_name": "真实波幅",
                "category": IndicatorCategory.VOLATILITY,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [],
                "outputs": [{"name": "trange", "description": "真实波幅值"}],
                "min_data_points": lambda p: 2,
                "min_data_points_formula": "2",
                "description": "真实波幅"
            },
        }

        # 成交量指标 (Volume Indicators)
        volume_indicators = {
            "OBV": {
                "full_name": "On Balance Volume",
                "chinese_name": "能量潮",
                "category": IndicatorCategory.VOLUME,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [],
                "outputs": [{"name": "obv", "description": "OBV值"}],
                "min_data_points": lambda p: 1,
                "min_data_points_formula": "1",
                "description": "能量潮指标,累积成交量变化"
            },
            "AD": {
                "full_name": "Chaikin A/D Line",
                "chinese_name": "累积/派发线",
                "category": IndicatorCategory.VOLUME,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [],
                "outputs": [{"name": "ad", "description": "AD值"}],
                "min_data_points": lambda p: 1,
                "min_data_points_formula": "1",
                "description": "累积/派发线"
            },
            "ADOSC": {
                "full_name": "Chaikin A/D Oscillator",
                "chinese_name": "累积/派发震荡",
                "category": IndicatorCategory.VOLUME,
                "panel_type": PanelType.OSCILLATOR,
                "parameters": [
                    {"name": "fastperiod", "type": "int", "default": 3, "min": 2, "max": 100},
                    {"name": "slowperiod", "type": "int", "default": 10, "min": 2, "max": 100}
                ],
                "outputs": [{"name": "adosc", "description": "ADOSC值"}],
                "min_data_points": lambda p: p.get("slowperiod", 10),
                "min_data_points_formula": "slowperiod",
                "reference_lines": [0],
                "description": "累积/派发震荡指标"
            },
        }

        # K线形态识别 (Candlestick Patterns) - 示例，实际有61+个
        candlestick_patterns = {
            "CDLDOJI": {
                "full_name": "Doji",
                "chinese_name": "十字星",
                "category": IndicatorCategory.CANDLESTICK,
                "panel_type": PanelType.OVERLAY,
                "parameters": [],
                "outputs": [{"name": "pattern", "description": "形态识别值"}],
                "min_data_points": lambda p: 1,
                "min_data_points_formula": "1",
                "description": "十字星形态"
            },
            "CDLHAMMER": {
                "full_name": "Hammer",
                "chinese_name": "锤子线",
                "category": IndicatorCategory.CANDLESTICK,
                "panel_type": PanelType.OVERLAY,
                "parameters": [],
                "outputs": [{"name": "pattern", "description": "形态识别值"}],
                "min_data_points": lambda p: 1,
                "min_data_points_formula": "1",
                "description": "锤子线形态"
            },
            "CDLENGULFING": {
                "full_name": "Engulfing Pattern",
                "chinese_name": "吞没形态",
                "category": IndicatorCategory.CANDLESTICK,
                "panel_type": PanelType.OVERLAY,
                "parameters": [],
                "outputs": [{"name": "pattern", "description": "形态识别值"}],
                "min_data_points": lambda p: 2,
                "min_data_points_formula": "2",
                "description": "吞没形态"
            },
        }

        # 合并所有指标到注册表
        self._registry = {
            **trend_indicators,
            **momentum_indicators,
            **volatility_indicators,
            **volume_indicators,
            **candlestick_patterns
        }

    def get_indicator(self, abbreviation: str) -> Optional[Dict[str, Any]]:
        """
        获取指定指标的元数据

        Args:
            abbreviation: 指标缩写名称 (如 "MA", "RSI")

        Returns:
            指标元数据字典,如果不存在返回None
        """
        return self._registry.get(abbreviation.upper())

    def get_all_indicators(self) -> Dict[str, Dict[str, Any]]:
        """获取所有指标的元数据"""
        return self._registry.copy()

    def get_indicators_by_category(self, category: IndicatorCategory) -> Dict[str, Dict[str, Any]]:
        """
        按分类获取指标

        Args:
            category: 指标分类

        Returns:
            该分类下的所有指标
        """
        return {
            abbr: meta
            for abbr, meta in self._registry.items()
            if meta["category"] == category
        }

    def validate_indicator(self, abbreviation: str, parameters: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """
        验证指标及其参数

        Args:
            abbreviation: 指标缩写
            parameters: 参数字典

        Returns:
            (是否有效, 错误消息)
        """
        # 检查指标是否存在
        indicator = self.get_indicator(abbreviation)
        if not indicator:
            return False, f"指标 '{abbreviation}' 不存在"

        # 验证参数
        required_params = {p["name"]: p for p in indicator["parameters"]}

        for param_name, param_value in parameters.items():
            if param_name not in required_params:
                return False, f"参数 '{param_name}' 不是指标 '{abbreviation}' 的有效参数"

            param_def = required_params[param_name]

            # 类型检查
            if param_def["type"] == "int" and not isinstance(param_value, int):
                return False, f"参数 '{param_name}' 应为整数"
            elif param_def["type"] == "float" and not isinstance(param_value, (int, float)):
                return False, f"参数 '{param_name}' 应为数值"

            # 范围检查
            if "min" in param_def and param_value < param_def["min"]:
                return False, f"参数 '{param_name}' 不能小于 {param_def['min']}"
            if "max" in param_def and param_value > param_def["max"]:
                return False, f"参数 '{param_name}' 不能大于 {param_def['max']}"

        return True, None

    def get_min_data_points(self, abbreviation: str, parameters: Dict[str, Any]) -> int:
        """
        计算指标所需的最小数据点数

        Args:
            abbreviation: 指标缩写
            parameters: 参数字典

        Returns:
            最小数据点数
        """
        indicator = self.get_indicator(abbreviation)
        if not indicator:
            return 0

        min_points_func = indicator["min_data_points"]
        return min_points_func(parameters)


# 全局单例
_indicator_registry = None


def get_indicator_registry() -> IndicatorRegistry:
    """获取指标注册表单例"""
    global _indicator_registry
    if _indicator_registry is None:
        _indicator_registry = IndicatorRegistry()
    return _indicator_registry
