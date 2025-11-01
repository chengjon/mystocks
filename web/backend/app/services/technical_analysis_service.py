"""
技术分析服务
Phase 2: ValueCell Migration - Enhanced Technical Analysis

基于 TA-Lib 提供全面的技术指标计算和分析
参考 ValueCell 的 MarketDataProvider 和 TechnicalIndicators
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
import talib
import akshare as ak

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TechnicalAnalysisService:
    """
    技术分析服务 (单例模式)

    提供完整的技术指标计算功能:
    - 趋势指标: MA, EMA, MACD, DMI, SAR
    - 动量指标: RSI, KDJ, CCI, WR
    - 波动指标: Bollinger Bands, ATR, Keltner Channel
    - 成交量指标: OBV, VWAP, Volume Profile
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        # 数据缓存
        self._cache = {}
        self._cache_ttl = 300  # 5分钟缓存

        self._initialized = True
        logger.info("TechnicalAnalysisService initialized")

    # ========================================================================
    # 数据获取
    # ========================================================================

    def get_stock_history(self,
                          symbol: str,
                          period: str = "daily",
                          start_date: Optional[str] = None,
                          end_date: Optional[str] = None,
                          adjust: str = "qfq") -> pd.DataFrame:
        """
        获取股票历史数据

        参数:
        - symbol: 股票代码
        - period: 周期 (daily, weekly, monthly)
        - start_date: 开始日期 YYYY-MM-DD
        - end_date: 结束日期 YYYY-MM-DD
        - adjust: 复权类型 (qfq=前复权, hfq=后复权, "")

        返回: DataFrame with columns: date, open, close, high, low, volume, amount
        """
        try:
            # 缓存键
            cache_key = f"{symbol}_{period}_{start_date}_{end_date}_{adjust}"

            # 检查缓存
            if cache_key in self._cache:
                cached_data, cached_time = self._cache[cache_key]
                if (datetime.now() - cached_time).seconds < self._cache_ttl:
                    logger.info(f"Using cached data for {symbol}")
                    return cached_data

            # 设置默认日期范围
            if end_date is None:
                end_date = datetime.now().strftime("%Y%m%d")
            else:
                end_date = end_date.replace("-", "")

            if start_date is None:
                start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            else:
                start_date = start_date.replace("-", "")

            # 获取数据
            df = ak.stock_zh_a_hist(
                symbol=symbol,
                period=period,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust
            )

            if df.empty:
                logger.warning(f"No data for {symbol}")
                return pd.DataFrame()

            # 重命名列
            df = df.rename(columns={
                '日期': 'date',
                '开盘': 'open',
                '收盘': 'close',
                '最高': 'high',
                '最低': 'low',
                '成交量': 'volume',
                '成交额': 'amount',
                '涨跌幅': 'change_percent',
                '涨跌额': 'change_amount',
                '换手率': 'turnover_rate'
            })

            # 转换日期
            df['date'] = pd.to_datetime(df['date'])

            # 确保数值类型
            numeric_cols = ['open', 'close', 'high', 'low', 'volume', 'amount']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')

            # 按日期排序
            df = df.sort_values('date').reset_index(drop=True)

            # 缓存数据
            self._cache[cache_key] = (df, datetime.now())

            logger.info(f"Fetched {len(df)} records for {symbol}")
            return df

        except Exception as e:
            logger.error(f"Failed to get stock history for {symbol}: {e}")
            return pd.DataFrame()

    # ========================================================================
    # 趋势指标 (Trend Indicators)
    # ========================================================================

    def calculate_trend_indicators(self, df: pd.DataFrame) -> Dict:
        """
        计算趋势指标

        包括:
        - MA (移动平均线): 5, 10, 20, 30, 60, 120, 250日
        - EMA (指数移动平均线): 12, 26, 50日
        - MACD (指数平滑异同移动平均线)
        - DMI (动向指标): ADX, +DI, -DI
        - SAR (抛物线转向指标)
        """
        if df.empty or len(df) < 250:
            logger.warning("Insufficient data for trend indicators")
            return {}

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # 移动平均线 (MA)
            ma_periods = [5, 10, 20, 30, 60, 120, 250]
            for period in ma_periods:
                if len(close) >= period:
                    indicators[f'ma{period}'] = float(talib.MA(close, timeperiod=period)[-1])

            # 指数移动平均线 (EMA)
            ema_periods = [12, 26, 50]
            for period in ema_periods:
                if len(close) >= period:
                    indicators[f'ema{period}'] = float(talib.EMA(close, timeperiod=period)[-1])

            # MACD
            if len(close) >= 34:
                macd, macd_signal, macd_hist = talib.MACD(
                    close, fastperiod=12, slowperiod=26, signalperiod=9
                )
                indicators['macd'] = float(macd[-1])
                indicators['macd_signal'] = float(macd_signal[-1])
                indicators['macd_hist'] = float(macd_hist[-1])

            # DMI (ADX, +DI, -DI)
            if len(close) >= 28:
                adx = talib.ADX(high, low, close, timeperiod=14)
                plus_di = talib.PLUS_DI(high, low, close, timeperiod=14)
                minus_di = talib.MINUS_DI(high, low, close, timeperiod=14)

                indicators['adx'] = float(adx[-1])
                indicators['plus_di'] = float(plus_di[-1])
                indicators['minus_di'] = float(minus_di[-1])

            # SAR (抛物线转向)
            if len(close) >= 2:
                sar = talib.SAR(high, low, acceleration=0.02, maximum=0.2)
                indicators['sar'] = float(sar[-1])

            logger.info(f"Calculated {len(indicators)} trend indicators")
            return indicators

        except Exception as e:
            logger.error(f"Failed to calculate trend indicators: {e}")
            return {}

    # ========================================================================
    # 动量指标 (Momentum Indicators)
    # ========================================================================

    def calculate_momentum_indicators(self, df: pd.DataFrame) -> Dict:
        """
        计算动量指标

        包括:
        - RSI (相对强弱指标): 6, 12, 24日
        - KDJ (随机指标)
        - CCI (顺势指标)
        - WR (威廉指标)
        - ROC (变动率指标)
        """
        if df.empty or len(df) < 50:
            logger.warning("Insufficient data for momentum indicators")
            return {}

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # RSI
            rsi_periods = [6, 12, 24]
            for period in rsi_periods:
                if len(close) >= period + 1:
                    rsi = talib.RSI(close, timeperiod=period)
                    indicators[f'rsi{period}'] = float(rsi[-1])

            # KDJ (使用 STOCH 计算)
            if len(close) >= 14:
                slowk, slowd = talib.STOCH(
                    high, low, close,
                    fastk_period=9,
                    slowk_period=3,
                    slowk_matype=0,
                    slowd_period=3,
                    slowd_matype=0
                )
                # KDJ: K, D, J=3K-2D
                k = slowk[-1]
                d = slowd[-1]
                j = 3 * k - 2 * d

                indicators['kdj_k'] = float(k)
                indicators['kdj_d'] = float(d)
                indicators['kdj_j'] = float(j)

            # CCI (顺势指标)
            if len(close) >= 20:
                cci = talib.CCI(high, low, close, timeperiod=14)
                indicators['cci'] = float(cci[-1])

            # WR (威廉指标)
            if len(close) >= 14:
                willr = talib.WILLR(high, low, close, timeperiod=14)
                indicators['willr'] = float(willr[-1])

            # ROC (变动率)
            if len(close) >= 12:
                roc = talib.ROC(close, timeperiod=12)
                indicators['roc'] = float(roc[-1])

            logger.info(f"Calculated {len(indicators)} momentum indicators")
            return indicators

        except Exception as e:
            logger.error(f"Failed to calculate momentum indicators: {e}")
            return {}

    # ========================================================================
    # 波动性指标 (Volatility Indicators)
    # ========================================================================

    def calculate_volatility_indicators(self, df: pd.DataFrame) -> Dict:
        """
        计算波动性指标

        包括:
        - Bollinger Bands (布林带)
        - ATR (平均真实波幅)
        - Keltner Channel (肯特纳通道)
        - Standard Deviation (标准差)
        """
        if df.empty or len(df) < 30:
            logger.warning("Insufficient data for volatility indicators")
            return {}

        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # Bollinger Bands
            if len(close) >= 20:
                upper, middle, lower = talib.BBANDS(
                    close,
                    timeperiod=20,
                    nbdevup=2,
                    nbdevdn=2,
                    matype=0
                )
                indicators['bb_upper'] = float(upper[-1])
                indicators['bb_middle'] = float(middle[-1])
                indicators['bb_lower'] = float(lower[-1])
                indicators['bb_width'] = float((upper[-1] - lower[-1]) / middle[-1] * 100)

            # ATR (平均真实波幅)
            if len(close) >= 14:
                atr = talib.ATR(high, low, close, timeperiod=14)
                indicators['atr'] = float(atr[-1])
                indicators['atr_percent'] = float(atr[-1] / close[-1] * 100)

            # Keltner Channel
            if len(close) >= 20:
                ema20 = talib.EMA(close, timeperiod=20)
                atr10 = talib.ATR(high, low, close, timeperiod=10)

                kc_upper = ema20 + 2 * atr10
                kc_middle = ema20
                kc_lower = ema20 - 2 * atr10

                indicators['kc_upper'] = float(kc_upper[-1])
                indicators['kc_middle'] = float(kc_middle[-1])
                indicators['kc_lower'] = float(kc_lower[-1])

            # 标准差
            if len(close) >= 20:
                stddev = talib.STDDEV(close, timeperiod=20, nbdev=1)
                indicators['stddev'] = float(stddev[-1])

            logger.info(f"Calculated {len(indicators)} volatility indicators")
            return indicators

        except Exception as e:
            logger.error(f"Failed to calculate volatility indicators: {e}")
            return {}

    # ========================================================================
    # 成交量指标 (Volume Indicators)
    # ========================================================================

    def calculate_volume_indicators(self, df: pd.DataFrame) -> Dict:
        """
        计算成交量指标

        包括:
        - OBV (能量潮指标)
        - VWAP (成交量加权平均价)
        - Volume MA (成交量均线): 5, 10日
        - Volume Ratio (量比)
        """
        if df.empty or len(df) < 20:
            logger.warning("Insufficient data for volume indicators")
            return {}

        close = df['close'].values
        volume = df['volume'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        try:
            # OBV (能量潮)
            if len(close) >= 2:
                obv = talib.OBV(close, volume)
                indicators['obv'] = float(obv[-1])

            # VWAP (成交量加权平均价)
            # VWAP = Σ(Price × Volume) / Σ(Volume)
            if len(df) >= 1 and 'amount' in df.columns:
                typical_price = (high + low + close) / 3
                cumulative_tpv = (typical_price * volume).sum()
                cumulative_volume = volume.sum()

                if cumulative_volume > 0:
                    indicators['vwap'] = float(cumulative_tpv / cumulative_volume)

            # 成交量均线
            volume_ma_periods = [5, 10]
            for period in volume_ma_periods:
                if len(volume) >= period:
                    vol_ma = talib.MA(volume.astype(float), timeperiod=period)
                    indicators[f'volume_ma{period}'] = float(vol_ma[-1])

            # 量比 (今日成交量 / 5日平均成交量)
            if len(volume) >= 6:
                vol_ma5 = talib.MA(volume.astype(float), timeperiod=5)
                if vol_ma5[-2] > 0:  # 使用昨天的均量
                    indicators['volume_ratio'] = float(volume[-1] / vol_ma5[-2])

            logger.info(f"Calculated {len(indicators)} volume indicators")
            return indicators

        except Exception as e:
            logger.error(f"Failed to calculate volume indicators: {e}")
            return {}

    # ========================================================================
    # 综合分析
    # ========================================================================

    def calculate_all_indicators(self,
                                 symbol: str,
                                 period: str = "daily",
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> Dict:
        """
        计算所有技术指标

        返回:
        {
          "symbol": "600519",
          "latest_price": 1800.0,
          "latest_date": "2025-10-23",
          "trend": {...},
          "momentum": {...},
          "volatility": {...},
          "volume": {...}
        }
        """
        try:
            # 获取历史数据
            df = self.get_stock_history(symbol, period, start_date, end_date)

            if df.empty:
                return {"error": "No data available"}

            # 计算各类指标
            result = {
                "symbol": symbol,
                "latest_price": float(df['close'].iloc[-1]),
                "latest_date": df['date'].iloc[-1].strftime("%Y-%m-%d"),
                "data_points": len(df),
                "trend": self.calculate_trend_indicators(df),
                "momentum": self.calculate_momentum_indicators(df),
                "volatility": self.calculate_volatility_indicators(df),
                "volume": self.calculate_volume_indicators(df)
            }

            # 统计信息
            total_indicators = (
                len(result['trend']) +
                len(result['momentum']) +
                len(result['volatility']) +
                len(result['volume'])
            )
            result['total_indicators'] = total_indicators

            logger.info(f"Calculated {total_indicators} indicators for {symbol}")
            return result

        except Exception as e:
            logger.error(f"Failed to calculate all indicators: {e}")
            return {"error": str(e)}

    # ========================================================================
    # 时间序列数据（用于图表）
    # ========================================================================

    def get_indicator_series(self,
                            symbol: str,
                            indicator: str,
                            period: str = "daily",
                            length: int = 100) -> Dict:
        """
        获取指标的时间序列数据（用于前端图表）

        参数:
        - symbol: 股票代码
        - indicator: 指标名称 (ma20, rsi14, macd等)
        - period: 周期
        - length: 数据点数量

        返回:
        {
          "dates": ["2025-01-01", ...],
          "values": [100.5, ...],
          "indicator": "ma20"
        }
        """
        try:
            # 获取历史数据
            df = self.get_stock_history(symbol, period, length=length+50)  # 多取一些数据

            if df.empty:
                return {"error": "No data available"}

            # 根据指标类型计算
            values = []
            dates = df['date'].dt.strftime("%Y-%m-%d").tolist()

            # 这里可以根据indicator参数计算对应的指标序列
            # 简化处理，后续可以扩展

            return {
                "symbol": symbol,
                "indicator": indicator,
                "dates": dates[-length:],
                "values": values[-length:] if values else []
            }

        except Exception as e:
            logger.error(f"Failed to get indicator series: {e}")
            return {"error": str(e)}

    # ========================================================================
    # 交易信号生成
    # ========================================================================

    def generate_trading_signals(self, df: pd.DataFrame) -> Dict:
        """
        基于技术指标生成交易信号

        返回:
        {
          "overall_signal": "buy/sell/hold",
          "signal_strength": 0.75,  # 0-1
          "signals": [
            {"type": "macd_cross", "signal": "buy", "strength": 0.8},
            {"type": "rsi_oversold", "signal": "buy", "strength": 0.6},
            ...
          ]
        }
        """
        if df.empty or len(df) < 50:
            return {"error": "Insufficient data"}

        signals = []

        try:
            close = df['close'].values

            # MACD金叉/死叉
            if len(close) >= 34:
                macd, signal, hist = talib.MACD(close)
                if hist[-1] > 0 and hist[-2] <= 0:
                    signals.append({
                        "type": "macd_golden_cross",
                        "signal": "buy",
                        "strength": 0.7
                    })
                elif hist[-1] < 0 and hist[-2] >= 0:
                    signals.append({
                        "type": "macd_death_cross",
                        "signal": "sell",
                        "strength": 0.7
                    })

            # RSI超买超卖
            if len(close) >= 14:
                rsi = talib.RSI(close, timeperiod=14)[-1]
                if rsi < 30:
                    signals.append({
                        "type": "rsi_oversold",
                        "signal": "buy",
                        "strength": (30 - rsi) / 30
                    })
                elif rsi > 70:
                    signals.append({
                        "type": "rsi_overbought",
                        "signal": "sell",
                        "strength": (rsi - 70) / 30
                    })

            # 计算综合信号
            buy_signals = [s for s in signals if s['signal'] == 'buy']
            sell_signals = [s for s in signals if s['signal'] == 'sell']

            if len(buy_signals) > len(sell_signals):
                overall_signal = "buy"
                signal_strength = sum(s['strength'] for s in buy_signals) / len(buy_signals) if buy_signals else 0
            elif len(sell_signals) > len(buy_signals):
                overall_signal = "sell"
                signal_strength = sum(s['strength'] for s in sell_signals) / len(sell_signals) if sell_signals else 0
            else:
                overall_signal = "hold"
                signal_strength = 0.5

            return {
                "overall_signal": overall_signal,
                "signal_strength": signal_strength,
                "signals": signals,
                "signal_count": {
                    "buy": len(buy_signals),
                    "sell": len(sell_signals),
                    "total": len(signals)
                }
            }

        except Exception as e:
            logger.error(f"Failed to generate trading signals: {e}")
            return {"error": str(e)}


# 创建全局单例
technical_analysis_service = TechnicalAnalysisService()
