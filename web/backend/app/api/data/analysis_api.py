"""
分析数据API模块

提供技术指标计算、基本面分析、报告生成、数据验证功能
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


class TimePeriod(Enum):
    """时间周期"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class AnalysisType(Enum):
    """分析类型"""
    TECHNICAL = "technical"
    FUNDAMENTAL = "fundamental"
    COMPREHENSIVE = "comprehensive"


@dataclass
class IndicatorData:
    """指标数据类"""
    indicator_type: IndicatorType = IndicatorType.MA
    symbol: str = ""
    time_period: TimePeriod = TimePeriod.DAILY
    period: int = 20
    values: List[float] = None
    calculated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'indicator_type': self.indicator_type.value,
            'symbol': self.symbol,
            'time_period': self.time_period.value,
            'period': self.period,
            'values': self.values,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


@dataclass
class FundamentalData:
    """基本面数据类"""
    symbol: str = ""
    name: str = ""
    industry: str = ""
    market_cap: float = 0.0
    pe_ratio: float = 0.0
    pb_ratio: float = 0.0
    ps_ratio: float = 0.0
    roe: float = 0.0
    revenue_growth: float = 0.0
    profit_growth: float = 0.0
    calculated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'symbol': self.symbol,
            'name': self.name,
            'industry': self.industry,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'ps_ratio': self.ps_ratio,
            'roe': self.roe,
            'revenue_growth': self.revenue_growth,
            'profit_growth': self.profit_growth,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None
        }


@dataclass
class AnalysisResult:
    """分析结果数据类"""
    analysis_id: str = ""
    analysis_type: AnalysisType = AnalysisType.TECHNICAL
    symbol: str = ""
    indicators: List[IndicatorData] = None
    fundamental: Optional[FundamentalData] = None
    summary: Dict[str, Any] = None
    generated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            'analysis_id': self.analysis_id,
            'analysis_type': self.analysis_type.value,
            'symbol': self.symbol,
            'indicators': [ind.to_dict() for ind in self.indicators] if self.indicators else [],
            'fundamental': self.fundamental.to_dict() if self.fundamental else None,
            'summary': self.summary,
            'generated_at': self.generated_at.isoformat() if self.generated_at else None
        }


class AnalysisDataService:
    """分析数据服务"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.indicator_cache = {}
        self.fundamental_cache = {}
        
        logger.info("分析数据API模块初始化")
    
    async def calculate_technical_indicator(self, symbol: str, indicator_type: IndicatorType, period: int = 20) -> IndicatorData:
        """
        计算技术指标
        
        Args:
            symbol: 股票代码
            indicator_type: 指标类型
            period: 周期
        
        Returns:
            IndicatorData: 指标数据
        """
        try:
            self._log_request_start('calculate_technical_indicator', {'symbol': symbol, 'indicator_type': indicator_type.value})
            
            if indicator_type == IndicatorType.MA:
                values = await self._calculate_ma(symbol, period)
            elif indicator_type == IndicatorType.EMA:
                values = await self._calculate_ema(symbol, period)
            elif indicator_type == IndicatorType.MACD:
                values = await self._calculate_macd(symbol, period)
            elif indicator_type == IndicatorType.RSI:
                values = await self._calculate_rsi(symbol, period)
            elif indicator_type == IndicatorType.BOLLINGER_BANDS:
                values = await self._calculate_bollinger_bands(symbol, period)
            elif indicator_type == IndicatorType.KDJ:
                values = await self._calculate_kdj(symbol, period)
            elif indicator_type == IndicatorType.VOLATILITY:
                values = await self._calculate_volatility(symbol, period)
            else:
                self.logger.warning(f"不支持的指标类型: {indicator_type.value}")
                values = []
            
            indicator_data = IndicatorData(
                indicator_type=indicator_type,
                symbol=symbol,
                time_period=TimePeriod.DAILY,
                period=period,
                values=values,
                calculated_at=datetime.now()
            )
            
            self._log_request_success('calculate_technical_indicator', indicator_data.to_dict())
            return indicator_data
            
        except Exception as e:
            self._log_request_error('calculate_technical_indicator', e)
            return IndicatorData()
    
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
            
            prices = [r['close_price'] for r in results]
            
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
    
    async def _calculate_macd(self, symbol: str, fast_period: int = 12, slow_period: int = 26) -> Dict:
        """计算MACD指标"""
        try:
            ema_fast = await self._calculate_ema(symbol, fast_period)
            ema_slow = await self._calculate_ema(symbol, slow_period)
            
            macd_line = [fast - slow for fast, slow in zip(ema_fast, ema_slow)]
            signal_line = []
            
            for i in range(9, len(macd_line)):
                if macd_line[i] > 0:
                    signal_line.append(1)
                elif macd_line[i] < 0:
                    signal_line.append(-1)
                else:
                    signal_line.append(0)
            
            histogram = [abs(macd_line[i]) for i in range(len(macd_line))]
            
            return {
                'macd_line': macd_line,
                'signal_line': signal_line,
                'histogram': histogram,
                'fast_period': fast_period,
                'slow_period': slow_period
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
            
            prices = [r['close_price'] for r in results]
            
            rsi_values = []
            
            for i in range(period, len(prices) - 1):
                gains = 0
                losses = 0
                
                for j in range(i, i + period):
                    change = prices[j] - prices[j-1]
                    if change > 0:
                        gains += change
                    else:
                        losses += abs(change)
                
                avg_gain = gains / period if period > 0 else 0
                avg_loss = losses / period if period > 0 else 0
                
                rs = 100 - (100 * avg_loss / (avg_gain + avg_loss)) if (avg_gain + avg_loss) > 0 else 0
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
            
            for i in range(period, len(ma_values)):
                window = ma_values[i-period:i] if i >= period else ma_values[0:i]
                std_dev = (sum((x - window[len(window)//2]) ** 2 for x in window) / len(window)) ** 0.5
                std_dev_values.append(std_dev)
            
            upper_band = []
            lower_band = []
            
            for i in range(len(std_dev_values)):
                ma = ma_values[i] if i < len(ma_values) else ma_values[-1]
                upper = ma + (std_dev_values[i] * multiplier)
                lower = ma - (std_dev_values[i] * multiplier)
                
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
    
    async def _calculate_kdj(self, symbol: str, period: int = 9, k: float = 3.0, d: float = 2.0) -> Dict:
        """计算KDJ指标"""
        try:
            from app.core.database import db_service
            
            sql = f"""
            SELECT 
                high_price, low_price, close_price
            FROM stock_daily
            WHERE code = '{symbol}'
            ORDER BY date DESC
            LIMIT {period}
            """
            
            results = await db_service.fetch_many(sql)
            
            if not results or len(results) < period:
                return {}
            
            highs = [r['high_price'] for r in results]
            lows = [r['low_price'] for r in results]
            closes = [r['close_price'] for r in results]
            
            low_values = []
            
            for i in range(period, len(lows)):
                window = lows[i-period:i] if i >= period else lows[0:i]
                low = min(window)
                low_values.append(low)
            
            high_values = []
            
            for i in range(period, len(highs)):
                window = highs[i-period:i] if i >= period else highs[0:i]
                high = max(window)
                high_values.append(high)
            
            rsv_values = []
            
            for i in range(period, len(closes)):
                if high_values[i] > 0:
                    rsv = (high_values[i] - closes[i]) / (high_values[i] - low_values[i]) * 100
                else:
                    rsv = 0
                rsv_values.append(rsv)
            
            ksv_values = []
            
            for i in range(period, len(closes)):
                if low_values[i] > 0:
                    ksv = (closes[i] - low_values[i]) / (high_values[i] - low_values[i]) * 100
                else:
                    ksv = 0
                ksv_values.append(ksv)
            
            j_values = []
            
            for i in range(period, len(rsv_values)):
                if rsv_values[i] > 0:
                    j = (2 * rsv_values[i]) + ksv_values[i]
                else:
                    j = 0
                j_values.append(j)
            
            k_values = []
            
            for i in range(period, len(j_values)):
                k = j_values[i] * k
                k_values.append(k)
            
            d_values = []
            
            for i in range(period, len(k_values)):
                if k_values[i]:
                    d = k_values[i] - (k_values[i-2] if i >= 2 else 0)
                else:
                    d = 0
                d_values.append(d)
            
            return {
                'k': k_values[-1],
                'd': d_values[-1],
                'j': j_values[-1],
                'rsv': rsv_values[-1],
                'k_value': k_values[-1],
                'd_value': d_values[-1],
                'period': period,
                'k_param': k,
                'd_param': d
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
            
            if not results or len(results) < 2:
                return []
            
            returns = [r['close_price'] for r in results]
            
            log_returns = [math.log(r[i] / r[i-1]) for i in range(1, len(returns))]
            
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
    
    async def get_fundamental_data(self, symbol: str) -> FundamentalData:
        """
        获取基本面数据
        
        Args:
            symbol: 股票代码
        
        Returns:
            FundamentalData: 基本面数据
        """
        try:
            self._log_request_start('get_fundamental_data', {'symbol': symbol})
            
            from app.core.database import db_service
            
            sql = f"""
            SELECT 
                symbol, name, industry,
                market_cap, pe_ratio, pb_ratio, ps_ratio, roe,
                revenue_growth, profit_growth
            FROM stocks
            WHERE code = '{symbol}'
            LIMIT 1
            """
            
            result = await db_service.fetch_one(sql)
            
            if result:
                fundamental_data = FundamentalData(
                    symbol=result['symbol'],
                    name=result['name'],
                    industry=result['industry'],
                    market_cap=result['market_cap'],
                    pe_ratio=result['pe_ratio'],
                    pb_ratio=result['pb_ratio'],
                    ps_ratio=result['ps_ratio'],
                    roe=result['roe'],
                    revenue_growth=result['revenue_growth'],
                    profit_growth=result['profit_growth'],
                    calculated_at=datetime.now()
                )
                
                self._log_request_success('get_fundamental_data', fundamental_data.to_dict())
                return fundamental_data
            
            return FundamentalData()
            
        except Exception as e:
            self._log_request_error('get_fundamental_data', e)
            return FundamentalData()
    
    async def run_comprehensive_analysis(self, symbol: str) -> AnalysisResult:
        """
        运行综合分析
        
        Args:
            symbol: 股票代码
        
        Returns:
            AnalysisResult: 综合分析结果
        """
        try:
            analysis_id = f"analysis_{symbol}_{datetime.now().isoformat()}"
            
            # 技术指标
            ma_20 = await self.calculate_technical_indicator(symbol, IndicatorType.MA, 20)
            ma_5 = await self.calculate_technical_indicator(symbol, IndicatorType.MA, 5)
            
            # 基本面分析
            fundamental = await self.get_fundamental_data(symbol)
            
            # 综合判断
            summary = {
                'symbol': symbol,
                'technical_indicators': {
                    'ma_20': ma_20,
                    'ma_5': ma_5
                },
                'fundamental': fundamental.to_dict(),
                'overall_rating': self._calculate_overall_rating(fundamental, ma_20),
                'recommendation': self._generate_recommendation(fundamental, ma_20)
            }
            
            result = AnalysisResult(
                analysis_id=analysis_id,
                analysis_type=AnalysisType.COMPREHENSIVE,
                symbol=symbol,
                indicators=[ma_20, ma_5],
                fundamental=fundamental,
                summary=summary,
                generated_at=datetime.now()
            )
            
            self._log_request_success('run_comprehensive_analysis', result.to_dict())
            return result
            
        except Exception as e:
            self._log_request_error('run_comprehensive_analysis', e)
            return AnalysisResult()
    
    def _calculate_overall_rating(self, fundamental: FundamentalData, ma_20: IndicatorData) -> str:
        """计算综合评级"""
        try:
            # 基本面评分
            fundamental_score = 0
            
            if fundamental.pe_ratio > 0 and fundamental.pe_ratio < 20:
                fundamental_score += 20
            elif fundamental.pe_ratio >= 20 and fundamental.pe_ratio < 30:
                fundamental_score += 15
            elif fundamental.pe_ratio >= 30:
                fundamental_score += 10
            
            if fundamental.pb_ratio > 0 and fundamental.pb_ratio < 3:
                fundamental_score += 15
            elif fundamental.pb_ratio >= 3 and fundamental.pb_ratio < 5:
                fundamental_score += 10
            elif fundamental.pb_ratio >= 5:
                fundamental_score += 5
            
            if fundamental.roe > 20:
                fundamental_score += 20
            elif fundamental.roe > 15:
                fundamental_score += 15
            elif fundamental.roe > 10:
                fundamental_score += 10
            elif fundamental.roe > 5:
                fundamental_score += 5
            
            if fundamental.revenue_growth > 30:
                fundamental_score += 15
            elif fundamental.revenue_growth > 20:
                fundamental_score += 10
            elif fundamental.revenue_growth > 10:
                fundamental_score += 5
            
            if fundamental.profit_growth > 30:
                fundamental_score += 15
            elif fundamental.profit_growth > 20:
                fundamental_score += 10
            elif fundamental.profit_growth > 10:
                fundamental_score += 5
            
            # 技术面评分
            if ma_20 and ma_20.values:
                recent_ma = ma_20.values[0]
                ma_5 = ma_5.values[0]
                
                if recent_ma > ma_5:
                    technical_score = 20
                elif recent_ma < ma_5:
                    technical_score = 5
                else:
                    technical_score = 0
            else:
                technical_score = 0
            
            # 综合评分
            overall_score = (fundamental_score * 0.6) + (technical_score * 0.4)
            
            if overall_score >= 80:
                return "A"
            elif overall_score >= 60:
                return "B"
            elif overall_score >= 40:
                return "C"
            elif overall_score >= 20:
                return "D"
            else:
                return "E"
            
        except Exception as e:
            self.logger.error(f"计算综合评级失败: {e}")
            return "E"
    
    def _generate_recommendation(self, fundamental: FundamentalData, ma_20: IndicatorData) -> str:
        """生成投资建议"""
        try:
            recommendations = []
            
            # 基于基本面的建议
            if fundamental.pe_ratio < 15 and fundamental.roe > 15:
                recommendations.append("估值合理且盈利能力强，建议买入")
            
            if fundamental.pe_ratio > 25:
                recommendations.append("估值较高，建议谨慎")
            
            if fundamental.revenue_growth < 10:
                recommendations.append("营收增长缓慢，建议观望")
            
            if fundamental.profit_growth < 5:
                recommendations.append("盈利增长停滞，建议观望")
            
            # 基于技术面的建议
            if ma_20 and ma_20.values:
                recent_ma = ma_20.values[0]
                ma_5 = ma_5.values[0]
                
                if recent_ma > ma_5:
                    recommendations.append("短期均线向上，趋势向好")
                elif recent_ma < ma_5:
                    recommendations.append("短期均线向下，趋势转弱")
            
            if not recommendations:
                recommendations.append("数据不足，无法给出建议")
            
            return "\n".join(recommendations[:3])
            
        except Exception as e:
            return "数据不足，无法生成建议"
    
    async def validate_data(self, data: Any, data_type: str) -> Dict:
        """
        验证数据质量
        
        Args:
            data: 待验证数据
            data_type: 数据类型
        
        Returns:
            Dict: 验证结果
        """
        try:
            result = {
                'is_valid': True,
                'data_type': data_type,
                'validation_time': datetime.now().isoformat(),
                'errors': [],
                'warnings': []
            }
            
            if data_type == 'price':
                if not data or data <= 0:
                    result['is_valid'] = False
                    result['errors'].append("价格数据无效")
            
            elif data_type == 'volume':
                if not data or data <= 0:
                    result['is_valid'] = False
                    result['errors'].append("成交量数据无效")
            
            elif data_type == 'ratio':
                if not data or data <= 0:
                    result['is_valid'] = False
                    result['errors'].append("比率数据无效")
                elif data == 0:
                    result['warnings'].append("比率为0可能导致除零错误")
            
            return result
            
        except Exception as e:
            self.logger.error(f"数据验证失败: {e}")
            return {
                'is_valid': False,
                'data_type': data_type,
                'validation_time': datetime.now().isoformat(),
                'errors': [str(e)],
                'warnings': []
            }
    
    def _log_request_start(self, method: str, params: Dict):
        """记录请求开始"""
        self.logger.info(f"开始{method}: {params}")
    
    def _log_request_success(self, method: str, result: Dict):
        """记录请求成功"""
        self.logger.info(f"{method}成功: {result}")
    
    def _log_request_error(self, method: str, error: Exception):
        """记录请求错误"""
        self.logger.error(f"{method}失败: {error}")
