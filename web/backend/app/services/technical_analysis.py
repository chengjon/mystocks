"""
技术分析模块

提供股票技术指标计算、图表生成、信号识别、趋势分析功能
"""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

logger = __import__("logging").getLogger(__name__)


class IndicatorType(Enum):
    """指标类型"""
    MA = "moving_average"
    EMA = "exponential_moving_average"
    MACD = "macd"
    RSI = "rsi"
    BOLLINGER_BANDS = "bollinger_bands"
    KDJ = "kdj"
    VOLATILITY = "volatility"
    VOLUME = "volume"
    TURNOVER = "turnover"


class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    STRONG_BUY = "strong_buy"
    STRONG_SELL = "strong_sell"


class TrendType(Enum):
    """趋势类型"""
    UPTREND = "uptrend"
    DOWNTREND = "downtrend"
    SIDEWAYS = "sideways"
    UNKNOWN = "unknown"


@dataclass
class TechnicalIndicator:
    """技术指标数据类"""
    indicator_type: IndicatorType = IndicatorType.MA
    symbol: str = ""
    time_period: str = "daily"
    period: int = 20
    values: List[float] = None
    calculated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'indicator_type': self.indicator_type.value,
            'symbol': self.symbol,
            'time_period': self.time_period,
            'period': self.period,
            'values': self.values,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


@dataclass
class TradingSignal:
    """交易信号数据类"""
    signal_id: str = ""
    symbol: str = ""
    signal_type: SignalType = SignalType.HOLD
    strength: float = 0.0
    price: float = 0.0
    signal_time: datetime = None
    confidence: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'signal_id': self.signal_id,
            'symbol': self.symbol,
            'signal_type': self.signal_type.value,
            'strength': self.strength,
            'price': self.price,
            'signal_time': self.signal_time.isoformat() if self.signal_time else None,
            'confidence': f"{self.confidence:.2f}"
        }


class TrendAnalysis:
    """趋势分析类"""
    trend_type: TrendType = TrendType.UNKNOWN
    strength: float = 0.0
    duration_days: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    price_change_percent: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'trend_type': self.trend_type.value,
            'strength': self.strength,
            'duration_days': self.duration_days,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'price_change_percent': f"{self.price_change_percent:.2f}%",
        }


class TechnicalAnalysis:
    """技术分析模块"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.indicator_cache = {}
        self.cache_ttl = 300
        self.last_calculation_time = None
        
        logger.info("技术分析模块初始化")
    
    async def calculate_indicator(self, symbol: str, indicator_type: IndicatorType, period: int = 20) -> TechnicalIndicator:
        """
        计算技术指标
        
        Args:
            symbol: 股票代码
            indicator_type: 指标类型
            period: 周期
        
        Returns:
            TechnicalIndicator: 技术指标数据
        """
        try:
            self._log_request_start('calculate_indicator', {'symbol': symbol, 'indicator_type': indicator_type.value})
            
            if indicator_type == IndicatorType.MA:
                values = await self._calculate_ma(symbol, period)
            elif indicator_type == IndicatorType.EMA:
                values = await self._calculate_ema(symbol, period)
            elif indicator_type == IndicatorType.MACD:
                result = await self._calculate_macd(symbol, 12, 26, 9, 2)
                values = [result['macd_line'], result['signal_line'], result['histogram']]
            elif indicator_type == IndicatorType.RSI:
                values = await self._calculate_rsi(symbol, period)
            elif indicator_type == IndicatorType.BOLLINGER_BANDS:
                result = await self._calculate_bollinger_bands(symbol, period, 2.0)
                values = [result['middle_band'], result['upper_band'], result['lower_band']]
            elif indicator_type == IndicatorType.KDJ:
                result = await self._calculate_kdj(symbol, 9, 3, 3)
                values = [result['k'], result['d'], result['j']]
            elif indicator_type == IndicatorType.VOLATILITY:
                values = await self._calculate_volatility(symbol, period)
            elif indicator_type == IndicatorType.VOLUME:
                values = await self._calculate_volume(symbol, period)
            elif indicator_type == IndicatorType.TURNOVER:
                values = await self._calculate_turnover(symbol, period)
            else:
                self.logger.warning(f"不支持的指标类型: {indicator_type.value}")
                values = []
            
            indicator_data = TechnicalIndicator(
                indicator_type=indicator_type,
                symbol=symbol,
                time_period="daily",
                period=period,
                values=values,
                calculated_at=datetime.now()
            )
            
            self._log_request_success('calculate_indicator', indicator_data.to_dict())
            return indicator_data
            
        except Exception as e:
            self._log_request_error('calculate_indicator', e)
            return TechnicalIndicator()
    
    async def _calculate_ma(self, symbol: str, period: int) -> List[float]:
        """计算移动平均线"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT close_price, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < period:
                return []
            
            prices = [r['close_price'] for r in reversed(results)]
            ma_values = []
            
            for i in range(period, len(prices)):
                window = prices[i-period:i] if i >= period else prices[0:i]
                ma = sum(window) / period
                ma_values.append(ma)
            
            return ma_values
            
        except Exception as e:
            self.logger.error(f"计算MA失败: {e}")
            return []
    
    async def _calculate_ema(self, symbol: str, period: int = 20) -> List[float]:
        """计算指数移动平均线"""
        try:
            multiplier = 2 / (period + 1)
            ma_values = await self._calculate_ma(symbol, period)
            
            ema_values = [ma_values[0]]
            
            for i in range(1, len(ma_values)):
                ema = (ma_values[i] * multiplier) + (ema_values[i-1] * (1 - multiplier))
                ema_values.append(ema)
            
            return ema_values
            
        except Exception as e:
            self.logger.error(f"计算EMA失败: {e}")
            return []
    
    async def _calculate_macd(self, symbol: str, fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, ema_period: int = 2) -> Dict:
        """计算MACD指标"""
        try:
            ema_fast = await self._calculate_ema(symbol, fast_period)
            ema_slow = await self._calculate_ema(symbol, slow_period)
            ema_signal = await self._calculate_ema(symbol, ema_period)
            
            macd_line = []
            signal_line = []
            
            for i in range(len(ema_fast)):
                macd = ema_fast[i] - ema_slow[i]
                macd_line.append(macd)
                
                if macd > 0:
                    signal_line.append(1)
                elif macd < 0:
                    signal_line.append(-1)
                else:
                    signal_line.append(0)
            
            # 计算直方图数据
            histogram = []
            
            for i in range(len(ema_signal)):
                macd_histogram = macd_signal[i] if macd_signal[i] > 0 else -macd_signal[i] if macd_signal[i] < 0 else 0
                histogram.append(macd_histogram)
            
            return {
                'macd_line': macd_line,
                'signal_line': signal_line,
                'histogram': histogram,
                'fast_period': fast_period,
                'slow_period': slow_period,
                'signal_period': signal_period,
                'ema_period': ema_period
            }
            
        except Exception as e:
            self.logger.error(f"计算MACD失败: {e}")
            return {}
    
    async def _calculate_rsi(self, symbol: str, period: int = 14) -> List[float]:
        """计算RSI指标"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT close_price, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period + 1}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < period + 1:
                return []
            
            prices = [r['close_price'] for r in reversed(results)][1:]
            
            rsi_values = []
            
            gains = 0
            losses = 0
            
            for i in range(period, len(prices)):
                change = prices[i] - prices[i-1]
                
                if change > 0:
                    gains += change
                else:
                    losses += abs(change)
            
            avg_gain = gains / period if period > 0 else 0
            avg_loss = losses / period if period > 0 else 0
            
            for i in range(period, len(prices)):
                if avg_gain == 0 or avg_loss == 0:
                    rs = 50
                else:
                    rs = 100 - (100 * avg_loss / (avg_gain + avg_loss))
                
                rsi_values.append(rs)
            
            return rsi_values
            
        except Exception as e:
            self.logger.error(f"计算RSI失败: {e}")
            return []
    
    async def _calculate_bollinger_bands(self, symbol: str, period: int = 20, multiplier: float = 2.0) -> Dict:
        """计算布林带"""
        try:
            ma_values = await self._calculate_ma(symbol, period)
            
            std_dev_values = []
            
            for i in range(len(ma_values)):
                window = ma_values[i-period:i] if i >= period else ma_values[0:i]
                std_dev = sum((x - window[len(window)//2]) ** 2 for x in window) / len(window) ** 0.5
                std_dev_values.append(std_dev)
            
            upper_band = []
            lower_band = []
            
            for i in range(len(std_dev_values)):
                upper = ma_values[i] + (std_dev_values[i] * multiplier)
                lower = ma_values[i] - (std_dev_values[i] * multiplier)
                upper_band.append(upper)
                lower_band.append(lower)
            
            return {
                'middle_band': ma_values,
                'upper_band': upper_band,
                'lower_band': lower_band,
                'multiplier': multiplier,
                'period': period
            }
            
        except Exception as e:
            self.logger.error(f"计算布林带失败: {e}")
            return {}
    
    async def _calculate_kdj(self, symbol: str, n: int = 9, m1: int = 3, m2: int = 3) -> Dict:
        """计算KDJ指标"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT 
                high_price, low_price, close_price, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {n * 2}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < n * 2:
                return {}
            
            k_values = []
            d_values = []
            j_values = []
            
            for i in range(n, len(results)):
                window = results[i-n:i+1:i+1] if i >= n+1 else results[:i+1]
                
                high = max(r['high_price'] for r in window)
                low = min(r['low_price'] for r in window)
                close = window[n]['close_price']
                
                if i < n:
                    k_value = (close - low) / (high - low) if high != low else 0
                else:
                    k_value = k_values[i-n]
                
                if high != low:
                    if low > k_value:
                        d_value = 2 * (high - low)
                    else:
                        d_value = 2 * (close - low)
                else:
                    d_value = 0
                
                k_values.append(k_value)
                
                if i >= n:
                    j_value = 2 * (k_values[i] - k_values[i-n])
                else:
                    j_value = k_values[i-1] * 3
                    
                j_values.append(j_value)
            
            return {
                'k': k_values[-1],
                'd': d_values[-1],
                'j': j_values[-1],
                'n': n,
                'm1': m1,
                'm2': m2
            }
            
        except Exception as e:
            self.logger.error(f"计算KDJ失败: {e}")
            return {}
    
    async def _calculate_volatility(self, symbol: str, period: int = 20) -> List[float]:
        """计算波动率"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT close_price, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < period:
                return []
            
            returns = [r['close_price'] for r in results]
            
            log_returns = [math.log(returns[i] / returns[i-1]) for i in range(1, len(returns))]
            
            import math
            variance = sum((lr - log_returns.mean()) ** 2 for lr in log_returns) / (len(log_returns) - 1)
            
            volatility = math.sqrt(variance) * 100
            
            vol_values = []
            
            for i in range(len(returns)):
                vol_values.append(volatility)
            
            return vol_values
            
        except Exception as e:
            self.logger.error(f"计算波动率失败: {e}")
            return []
    
    async def _calculate_volume(self, symbol: str, period: int = 20) -> List[float]:
        """计算成交量"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT volume, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < period:
                return []
            
            volumes = [r['volume'] for r in results]
            
            vol_ma = await self._calculate_volume_ma(volumes)
            
            return volumes
            
        except Exception as e:
            self.logger.error(f"计算成交量失败: {e}")
            return []
    
    async def _calculate_volume_ma(self, volumes: List[float]) -> float:
        """计算成交量移动平均"""
        if not volumes:
            return 0.0
        
        return sum(volumes) / len(volumes)
    
    async def _calculate_turnover(self, symbol: str, period: int = 20) -> List[float]:
        """计算换手率"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT 
                close_price, volume, amount, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < 2:
                return []
            
            amounts = [r['amount'] for r in results]
            volumes = [r['volume'] for r in results]
            
            turnover_values = []
            
            for i in range(1, len(amounts)):
                turnover = amounts[i] / volumes[i] if volumes[i] > 0 else 0
                turnover_values.append(turnover)
            
            return turnover_values
            
        except Exception as e:
            self.logger.error(f"计算换手率失败: {e}")
            return []
    
    async def generate_trading_signal(self, symbol: str, strategy: str = "default") -> TradingSignal:
        """
        生成交易信号
        
        Args:
            symbol: 股票代码
            strategy: 策略名称
        
        Returns:
            TradingSignal: 交易信号
        """
        try:
            self._log_request_start('generate_trading_signal', {'symbol': symbol, 'strategy': strategy})
            
            import uuid
            
            ma_20 = await self.calculate_indicator(symbol, IndicatorType.MA, 20)
            ema_5 = await self.calculate_indicator(symbol, IndicatorType.EMA, 5)
            
            # 判断买入信号
            if ema_5.values[-1] > ma_20.values[-1] and ema_20.values[-2] < ma_20.values[-1]:
                signal_type = SignalType.BUY
                strength = 0.8
                price = ma_20.values[-1]
            elif ema_5.values[-1] < ma_20.values[-1] and ema_20.values[-2] > ma_20.values[-1]:
                signal_type = SignalType.SELL
                strength = 0.7
                price = ma_20.values[-1]
            else:
                signal_type = SignalType.HOLD
                strength = 0.3
                price = ma_20.values[-1]
            
            # 计算信心度
            confidence = min(0.95, abs(ma_20.values[-1] - ema_5.values[-1]) / abs(ma_20.values[-1]) * 100) if ma_20.values[-1] != ema_5.values[-1] else 0.5)
            
            signal = TradingSignal(
                signal_id=f"signal_{uuid.uuid4()}",
                symbol=symbol,
                signal_type=signal_type,
                strength=strength,
                price=price,
                signal_time=datetime.now(),
                confidence=confidence
            )
            
            self._log_request_success('generate_trading_signal', signal.to_dict())
            return signal
            
        except Exception as e:
            self._log_request_error('generate_trading_signal', e)
            return TradingSignal()
    
    async def analyze_trend(self, symbol: str, period: int = 30) -> TrendAnalysis:
        """
        分析趋势
        
        Args:
            symbol: 股票代码
            period: 分析周期（天）
        
        Returns:
            TrendAnalysis: 趋势分析结果
        """
        try:
            self._log_request_start('analyze_trend', {'symbol': symbol, 'period': period})
            
            from app.core.database import db_service
            
            sql = f"""
            SELECT close_price, date
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < 2:
                return TrendAnalysis()
            
            start_price = results[-1]['close_price']
            end_price = results[0]['close_price']
            price_change_percent = ((end_price - start_price) / start_price) * 100 if start_price > 0 else 0
            
            # 判断趋势
            if price_change_percent > 15:
                trend_type = TrendType.UPTREND
                strength = min(1.0, price_change_percent / 15)
            elif price_change_percent < -15:
                trend_type = TrendType.DOWNTREND
                strength = min(1.0, abs(price_change_percent) / 15)
            elif abs(price_change_percent) < 5:
                trend_type = TrendType.SIDEWAYS
                strength = 1.0 - abs(price_change_percent) / 5
            else:
                trend_type = TrendType.UNKNOWN
                strength = 0.5
            
            analysis = TrendAnalysis(
                trend_type=trend_type,
                strength=strength,
                duration_days=period,
                start_date=datetime.now() - timedelta(days=period),
                end_date=datetime.now(),
                price_change_percent=price_change_percent
            )
            
            self._log_request_success('analyze_trend', analysis.to_dict())
            return analysis
            
        except Exception as e:
            self._log_request_error('analyze_trend', e)
            return TrendAnalysis()
    
    def _log_request_start(self, method: str, params: Dict):
        """记录请求开始"""
        self.logger.info(f"开始{method}: {params}")
    
    def _log_request_success(self, method: str, result: Dict):
        """记录请求成功"""
        self.logger.info(f"{method}成功: {result}")
    
    def _log_request_error(self, method: str, error: Exception):
        """记录请求错误"""
        self.logger.error(f"{method}失败: {error}")
