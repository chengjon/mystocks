"""
股票策略模块
实现10个经典股票策略用于筛选和识别交易机会

策略列表：
1. 放量上涨 (Volume Surge)
2. 均线多头 (MA Bullish)
3. 停机坪 (Consolidation Platform)
4. 回踩年线 (MA250 Pullback)
5. 突破平台 (Breakthrough Platform)
6. 无大幅回撤 (Low Drawdown)
7. 海龟交易法则 (Turtle Trading)
8. 高而窄的旗形 (High Tight Flag)
9. 放量跌停 (Volume Limit Down)
10. 低ATR成长 (Low ATR Growth)
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd
import talib as tl
from datetime import datetime


class BaseStrategy(ABC):
    """策略基类"""

    def __init__(self, name: str, name_cn: str, description: str):
        """
        初始化策略

        Args:
            name: 策略英文名
            name_cn: 策略中文名
            description: 策略描述
        """
        self.name = name
        self.name_cn = name_cn
        self.description = description

    @abstractmethod
    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        """
        检查股票是否符合策略条件

        Args:
            symbol: 股票代码
            data: 股票历史数据 (包含 date, open, high, low, close, volume, amount 等字段)
            date: 检查日期 (None表示最新数据)
            threshold: 时间窗口 (天数)

        Returns:
            bool: True表示符合策略条件，False表示不符合
        """
        pass

    def filter_date(self, data: pd.DataFrame, end_date: Optional[str] = None) -> pd.DataFrame:
        """过滤数据到指定日期"""
        if end_date is not None:
            mask = data["date"] <= end_date
            return data.loc[mask].copy()
        return data.copy()


class VolumeSurgeStrategy(BaseStrategy):
    """
    策略1: 放量上涨

    条件：
    1. 当日比前一天上涨小于2%或收盘价小于开盘价
    2. 当日成交额不低于2亿
    3. 当日成交量/5日平均成交量>=2
    """

    def __init__(self):
        super().__init__(
            name="volume_surge",
            name_cn="放量上涨",
            description="成交量放大2倍以上且价格上涨的股票",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        # 计算涨跌幅
        p_change = (
            data.iloc[-1]["p_change"]
            if "p_change" in data.columns
            else (data.iloc[-1]["close"] - data.iloc[-2]["close"]) / data.iloc[-2]["close"] * 100
        )

        # 条件1: 涨幅<2% 或 收盘价<开盘价
        if p_change < 2 or data.iloc[-1]["close"] < data.iloc[-1]["open"]:
            return False

        # 计算5日成交量均线
        data.loc[:, "vol_ma5"] = tl.MA(data["volume"].values, timeperiod=5)
        data["vol_ma5"].fillna(0, inplace=True)

        data = data.tail(n=threshold + 1)
        if len(data) < threshold + 1:
            return False

        last_close = data.iloc[-1]["close"]
        last_vol = data.iloc[-1]["volume"]

        # 条件2: 成交额不低于2亿
        amount = last_close * last_vol
        if amount < 200000000:
            return False

        # 条件3: 成交量/5日均量>=2
        mean_vol = data.iloc[-2]["vol_ma5"]  # 使用前一天的5日均量
        if mean_vol == 0:
            return False

        vol_ratio = last_vol / mean_vol
        return vol_ratio >= 2


class MABullishStrategy(BaseStrategy):
    """
    策略2: 均线多头

    条件：
    1. 30日前的30日均线<20日前的30日均线<10日前的30日均线<当日的30日均线
    2. (当日的30日均线/30日前的30日均线)>1.2
    """

    def __init__(self):
        super().__init__(
            name="ma_bullish",
            name_cn="均线多头",
            description="短期均线在长期均线上方，多条均线向上发散",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 30,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        # 计算30日均线
        data.loc[:, "ma30"] = tl.MA(data["close"].values, timeperiod=30)
        data["ma30"].fillna(0, inplace=True)

        data = data.tail(n=threshold)

        step1 = round(threshold / 3)
        step2 = round(threshold * 2 / 3)

        # 均线递增且涨幅超过20%
        if (
            data.iloc[0]["ma30"] < data.iloc[step1]["ma30"] < data.iloc[step2]["ma30"] < data.iloc[-1]["ma30"]
            and data.iloc[-1]["ma30"] > 1.2 * data.iloc[0]["ma30"]
        ):
            return True

        return False


class TurtleTradingStrategy(BaseStrategy):
    """
    策略7: 海龟交易法则

    条件：
    1. 当日收盘价>=最近60日最高收盘价
    """

    def __init__(self):
        super().__init__(
            name="turtle_trading",
            name_cn="海龟交易法则",
            description="创出60日新高的股票",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        data = data.tail(n=threshold)

        # 找出最高价
        max_price = data["close"].max()
        last_close = data.iloc[-1]["close"]

        # 当日收盘价是否等于或超过最高价
        return last_close >= max_price


class ConsolidationPlatformStrategy(BaseStrategy):
    """
    策略3: 停机坪

    条件：
    1. 最近15日有涨幅大于9.5%，且必须是放量上涨
    2. 紧接的下个交易日必须高开，收盘价必须上涨，且与开盘价不能大于等于相差3%
    3. 接下2、3个交易日必须高开，收盘价必须上涨，且与开盘价不能大于等于相差3%，且每天涨跌幅在5%间
    """

    def __init__(self):
        super().__init__(
            name="consolidation_platform",
            name_cn="停机坪",
            description="股价横盘整理，成交量缩小，蓄势待发",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 15,
    ) -> bool:
        origin_data = data.copy()
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        data = data.tail(n=threshold)

        # 计算p_change如果不存在
        if "p_change" not in data.columns:
            data["p_change"] = data["close"].pct_change() * 100

        # 找出涨停日（涨幅>9.5%）
        for idx, row in data.iterrows():
            if row["p_change"] > 9.5:
                # 检查是否创新高（类似海龟交易）
                check_date = datetime.strptime(row["date"], "%Y-%m-%d")
                turtle_check = TurtleTradingStrategy().check(symbol, origin_data, check_date, threshold)

                if turtle_check and self._check_consolidation(data, row["close"], row["date"]):
                    return True

        return False

    def _check_consolidation(self, data: pd.DataFrame, limitup_price: float, limitup_date: str) -> bool:
        """检查涨停后的整理形态"""
        limitup_end = data.loc[data["date"] > limitup_date].head(n=3)

        if len(limitup_end) < 3:
            return False

        consolidation_day1 = limitup_end.iloc[0]
        consolidation_day23 = limitup_end.tail(n=2)

        # 第一天条件
        if not (
            consolidation_day1["close"] > limitup_price
            and consolidation_day1["open"] > limitup_price
            and 0.97 < consolidation_day1["close"] / consolidation_day1["open"] < 1.03
        ):
            return False

        # 第2、3天条件
        for idx, row in consolidation_day23.iterrows():
            if not (
                0.97 < (row["close"] / row["open"]) < 1.03
                and -5 < row["p_change"] < 5
                and row["close"] > limitup_price
                and row["open"] > limitup_price
            ):
                return False

        return True


class MA250PullbackStrategy(BaseStrategy):
    """
    策略4: 回踩年线

    条件：
    1. 前段由年线(250日)以下向上突破
    2. 后段必须在年线以上运行
    3. 后段最低价日与最高价日相差必须在10-50日间
    4. 回踩伴随缩量：最高价日交易量/后段最低价日交易量>2
    5. 后段最低价/最高价<0.8
    """

    def __init__(self):
        super().__init__(
            name="ma250_pullback",
            name_cn="回踩年线",
            description="股价回踩250日均线获得支撑",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < 250:
            return False

        # 计算250日均线
        data.loc[:, "ma250"] = tl.MA(data["close"].values, timeperiod=250)
        data["ma250"].fillna(0, inplace=True)

        data = data.tail(n=threshold)

        # 找出区间最高点和最低点
        highest_idx = data["close"].idxmax()
        highest_row = data.loc[highest_idx]

        data_front = data.loc[data["date"] < highest_row["date"]]
        data_end = data.loc[data["date"] >= highest_row["date"]]

        if data_front.empty:
            return False

        # 条件1: 前段由年线以下向上突破
        if not (
            data_front.iloc[0]["close"] < data_front.iloc[0]["ma250"]
            and data_front.iloc[-1]["close"] > data_front.iloc[-1]["ma250"]
        ):
            return False

        if data_end.empty:
            return False

        # 条件2: 后段必须在年线以上运行
        if (data_end["close"] < data_end["ma250"]).any():
            return False

        # 找出后段最低点
        recent_lowest_idx = data_end["close"].idxmin()
        recent_lowest_row = data_end.loc[recent_lowest_idx]

        # 条件3: 日期差在10-50日间
        date_diff = (
            datetime.strptime(recent_lowest_row["date"], "%Y-%m-%d")
            - datetime.strptime(highest_row["date"], "%Y-%m-%d")
        ).days

        if not (10 <= date_diff <= 50):
            return False

        # 条件4: 缩量比例>2
        vol_ratio = highest_row["volume"] / recent_lowest_row["volume"]

        # 条件5: 回踩幅度<0.8
        back_ratio = recent_lowest_row["close"] / highest_row["close"]

        return vol_ratio > 2 and back_ratio < 0.8


class BreakthroughPlatformStrategy(BaseStrategy):
    """
    策略5: 突破平台

    条件：
    1. 60日内某日收盘价>=60日均线>开盘价
    2. 且放量上涨
    3. 突破日之前，任意一天收盘价与60日均线偏离在-5%~20%之间
    """

    def __init__(self):
        super().__init__(
            name="breakthrough_platform",
            name_cn="突破平台",
            description="股价突破前期平台高点",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        origin_data = data.copy()
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        # 计算60日均线
        data.loc[:, "ma60"] = tl.MA(data["close"].values, timeperiod=60)
        data["ma60"].fillna(0, inplace=True)

        data = data.tail(n=threshold)

        # 找出突破日
        breakthrough_date = None
        volume_surge = VolumeSurgeStrategy()

        for idx, row in data.iterrows():
            if row["open"] < row["ma60"] <= row["close"]:
                check_date = datetime.strptime(row["date"], "%Y-%m-%d")
                if volume_surge.check(symbol, origin_data, check_date, threshold):
                    breakthrough_date = row["date"]
                    break

        if breakthrough_date is None:
            return False

        # 检查突破前的平台
        data_front = data.loc[(data["date"] < breakthrough_date) & (data["ma60"] > 0)]

        for idx, row in data_front.iterrows():
            deviation = (row["ma60"] - row["close"]) / row["ma60"]
            if not (-0.05 < deviation < 0.2):
                return False

        return True


class LowDrawdownStrategy(BaseStrategy):
    """
    策略6: 无大幅回撤

    条件：
    1. 60日涨幅必须大于60%
    2. 不能有单日跌幅超7%
    3. 不能有高开低走7%
    4. 不能有两日累计跌幅10%
    5. 不能有两日高开低走累计10%
    """

    def __init__(self):
        super().__init__(
            name="low_drawdown",
            name_cn="无大幅回撤",
            description="上涨过程中回撤幅度较小的强势股",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        data = data.tail(n=threshold)

        # 条件1: 60日涨幅必须大于60%
        ratio_increase = (data.iloc[-1]["close"] - data.iloc[0]["close"]) / data.iloc[0]["close"]
        if ratio_increase < 0.6:
            return False

        # 计算p_change如果不存在
        if "p_change" not in data.columns:
            data["p_change"] = data["close"].pct_change() * 100

        # 检查回撤条件
        previous_p_change = 100.0
        previous_open = -1000000.0

        for _, row in data.iterrows():
            p_change = row["p_change"]
            close = row["close"]
            open_price = row["open"]

            # 单日跌幅超7%
            if p_change < -7:
                return False

            # 高开低走7%
            if (close - open_price) / open_price * 100 < -7:
                return False

            # 两日累计跌幅10%
            if previous_p_change + p_change < -10:
                return False

            # 两日高开低走累计10%
            if previous_open > 0 and (close - previous_open) / previous_open * 100 < -10:
                return False

            previous_p_change = p_change
            previous_open = open_price

        return True


class HighTightFlagStrategy(BaseStrategy):
    """
    策略8: 高而窄的旗形

    条件：
    1. 必须至少上市交易60日
    2. 当日最高价/之前24~10日的最低价>=1.9
    3. 之前24~10日必须连续两天涨幅大于等于9.5%
    """

    def __init__(self):
        super().__init__(
            name="high_tight_flag",
            name_cn="高而窄的旗形",
            description="快速上涨后窄幅整理的旗形形态",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        data = data.tail(n=threshold)

        # 计算p_change如果不存在
        if "p_change" not in data.columns:
            data["p_change"] = data["close"].pct_change() * 100

        # 取24~10日前的数据（即倒数第24到倒数第10天）
        if len(data) < 24:
            return False

        flag_data = data.iloc[-24:-10]

        if len(flag_data) < 14:
            return False

        # 条件2: 最高价/最低价>=1.9
        low = flag_data["low"].min()
        high = flag_data["high"].max()
        ratio_increase = high / low

        if ratio_increase < 1.9:
            return False

        # 条件3: 连续两天涨幅>=9.5%
        previous_p_change = 0.0
        found_consecutive = False

        for _, row in flag_data.iterrows():
            p_change = row["p_change"]
            if p_change >= 9.5:
                if previous_p_change >= 9.5:
                    found_consecutive = True
                    break
                previous_p_change = p_change
            else:
                previous_p_change = 0.0

        return found_consecutive


class VolumeLimitDownStrategy(BaseStrategy):
    """
    策略9: 放量跌停

    条件：
    1. 当日跌幅>9.5%
    2. 当日成交额不低于2亿
    3. 当日成交量>=5日平均成交量的4倍
    """

    def __init__(self):
        super().__init__(
            name="volume_limit_down",
            name_cn="放量跌停",
            description="放量且跌停，识别恐慌性抛售",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 60,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        if len(data) < threshold:
            return False

        # 计算涨跌幅
        p_change = (
            data.iloc[-1]["p_change"]
            if "p_change" in data.columns
            else (data.iloc[-1]["close"] - data.iloc[-2]["close"]) / data.iloc[-2]["close"] * 100
        )

        # 条件1: 跌幅>9.5%
        if p_change > -9.5:
            return False

        # 计算5日成交量均线
        data.loc[:, "vol_ma5"] = tl.MA(data["volume"].values, timeperiod=5)
        data["vol_ma5"].fillna(0, inplace=True)

        data = data.tail(n=threshold + 1)
        if len(data) < threshold + 1:
            return False

        last_close = data.iloc[-1]["close"]
        last_vol = data.iloc[-1]["volume"]

        # 条件2: 成交额不低于2亿
        amount = last_close * last_vol
        if amount < 200000000:
            return False

        # 条件3: 成交量/5日均量>=4
        data_prev = data.head(n=threshold)
        mean_vol = data_prev.iloc[-1]["vol_ma5"]

        if mean_vol == 0:
            return False

        vol_ratio = last_vol / mean_vol
        return vol_ratio >= 4


class LowATRGrowthStrategy(BaseStrategy):
    """
    策略10: 低ATR成长

    条件：
    1. 必须至少上市交易250日
    2. 最近10个交易日，最高收盘价/最低收盘价>1.1
    3. 最近10个交易日，平均每日涨跌幅(ATR)<10%
    """

    def __init__(self):
        super().__init__(
            name="low_atr_growth",
            name_cn="低ATR成长",
            description="ATR（平均真实波幅）较低但稳定增长",
        )

    def check(
        self,
        symbol: str,
        data: pd.DataFrame,
        date: Optional[datetime] = None,
        threshold: int = 10,
    ) -> bool:
        end_date = date.strftime("%Y-%m-%d") if date else None
        data = self.filter_date(data, end_date)

        # 条件1: 必须至少上市交易250日
        if len(data) < 250:
            return False

        # 计算p_change如果不存在
        if "p_change" not in data.columns:
            data["p_change"] = data["close"].pct_change() * 100

        # 取最近10个交易日
        data = data.tail(n=threshold)

        if len(data) < threshold:
            return False

        # 找出最高和最低收盘价
        highest_close = data["close"].max()
        lowest_close = data["close"].min()

        # 条件2: 最高/最低>1.1
        ratio = (highest_close - lowest_close) / lowest_close
        if ratio <= 1.1:
            return False

        # 条件3: 计算平均ATR（平均每日涨跌幅绝对值）
        total_change = data["p_change"].abs().sum()
        atr = total_change / len(data)

        if atr > 10:
            return False

        return True


# 策略注册表
STRATEGY_REGISTRY = {
    "volume_surge": VolumeSurgeStrategy(),
    "ma_bullish": MABullishStrategy(),
    "turtle_trading": TurtleTradingStrategy(),
    "consolidation_platform": ConsolidationPlatformStrategy(),
    "ma250_pullback": MA250PullbackStrategy(),
    "breakthrough_platform": BreakthroughPlatformStrategy(),
    "low_drawdown": LowDrawdownStrategy(),
    "high_tight_flag": HighTightFlagStrategy(),
    "volume_limit_down": VolumeLimitDownStrategy(),
    "low_atr_growth": LowATRGrowthStrategy(),
}


def get_strategy(strategy_name: str) -> Optional[BaseStrategy]:
    """获取策略实例"""
    return STRATEGY_REGISTRY.get(strategy_name)


def get_all_strategies() -> Dict[str, BaseStrategy]:
    """获取所有策略"""
    return STRATEGY_REGISTRY
