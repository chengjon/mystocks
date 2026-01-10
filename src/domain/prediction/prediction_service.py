"""
Prediction Service
预测服务

提供价格走势预测和指标预测功能。
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


class PredictionService:
    """
    预测服务

    职责：
    - 价格走势预测
    - 指标值预测
    - 预测模型管理
    """

    def __init__(self, data_source_manager=None):
        self.data_source_manager = data_source_manager

    def predict_price_direction(
        self, stock_code: str, lookback_days: int = 30, prediction_days: int = 5
    ) -> Dict[str, Any]:
        """
        预测价格走势方向

        基于历史数据和技术指标进行简单预测。
        """
        try:
            data = self._get_historical_data(stock_code, lookback_days + prediction_days)
            if data is None or len(data) < lookback_days:
                return {"error": "数据不足"}

            recent = data.tail(lookback_days)
            closes = recent["close"].values

            if len(closes) < 5:
                return {"error": "数据点不足"}

            ma5 = np.mean(closes[-5:])
            ma20 = np.mean(closes[-20:]) if len(closes) >= 20 else ma5

            trend = "up" if ma5 > ma20 else "down" if ma5 < ma20 else "neutral"

            volatility = np.std(closes) / np.mean(closes) * 100 if np.mean(closes) > 0 else 0

            return {
                "stock_code": stock_code,
                "prediction_type": "price_direction",
                "predicted_trend": trend,
                "confidence": min(0.6 + volatility * 0.01, 0.85),
                "ma5": float(ma5),
                "ma20": float(ma20),
                "volatility": float(volatility),
                "prediction_days": prediction_days,
                "model_used": "simple_ma_crossover",
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Price prediction failed for {stock_code}: {e}")
            return {"error": str(e)}

    def predict_price_target(self, stock_code: str, lookback_days: int = 60, target_date: str = None) -> Dict[str, Any]:
        """
        预测目标日期的价格

        Args:
            stock_code: 股票代码
            lookback_days: 历史数据天数
            target_date: 目标日期（YYYY-MM-DD格式）
        """
        try:
            data = self._get_historical_data(stock_code, lookback_days)
            if data is None or len(data) < 20:
                return {"error": "数据不足"}

            closes = data["close"].values

            ma20 = np.mean(closes[-20:])
            ma60 = np.mean(closes[-60:]) if len(closes) >= 60 else ma20

            volatility = np.std(closes[-20:]) / ma20 * 100 if ma20 > 0 else 0

            trend = 1 if ma20 > ma60 else -1 if ma20 < ma60 else 0

            predicted_change = trend * volatility * 0.5
            predicted_price = ma20 * (1 + predicted_change / 100)

            return {
                "stock_code": stock_code,
                "prediction_type": "price_target",
                "predicted_price": float(predicted_price),
                "current_price": float(closes[-1]),
                "predicted_change_pct": float(predicted_change),
                "volatility": float(volatility),
                "confidence": max(0.5, 0.8 - volatility * 0.02),
                "target_date": target_date or (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "model_used": "ma_trend_projection",
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Price target prediction failed for {stock_code}: {e}")
            return {"error": str(e)}

    def predict_indicator(self, stock_code: str, indicator_id: str, lookback_days: int = 30) -> Dict[str, Any]:
        """
        预测指标值

        Args:
            stock_code: 股票代码
            indicator_id: 指标ID
            lookback_days: 历史数据天数
        """
        try:
            data = self._get_historical_data(stock_code, lookback_days)
            if data is None or len(data) < 20:
                return {"error": "数据不足"}

            if indicator_id.startswith("sma"):
                period = int(indicator_id.split(".")[1]) if len(indicator_id.split(".")) > 1 else 5
                values = data["close"].rolling(window=period).mean().dropna().values
            elif indicator_id.startswith("rsi"):
                delta = data["close"].diff()
                gain = delta.where(delta > 0, 0).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                values = (100 - (100 / (1 + rs))).dropna().values
            else:
                return {"error": f"不支持的指标: {indicator_id}"}

            if len(values) < 5:
                return {"error": "指标数据不足"}

            recent_values = values[-5:]
            trend = np.polyfit(range(len(recent_values)), recent_values, 1)[0]

            current_value = values[-1]
            predicted_value = current_value + trend * 2

            volatility = np.std(values[-10:]) if len(values) >= 10 else np.std(values)

            return {
                "stock_code": stock_code,
                "prediction_type": "indicator",
                "indicator_id": indicator_id,
                "current_value": float(current_value),
                "predicted_value": float(predicted_value),
                "trend": float(trend),
                "volatility": float(volatility),
                "confidence": 0.65,
                "prediction_horizon": "1 day",
                "model_used": "linear_trend",
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Indicator prediction failed for {stock_code}/{indicator_id}: {e}")
            return {"error": str(e)}

    def predict_volatility(self, stock_code: str, period_days: int = 10) -> Dict[str, Any]:
        """
        预测未来波动率
        """
        try:
            data = self._get_historical_data(stock_code, 60)
            if data is None or len(data) < period_days:
                return {"error": "数据不足"}

            returns = data["close"].pct_change().dropna().values
            historical_vol = np.std(returns) * np.sqrt(252) * 100

            recent_vol = (
                np.std(returns[-period_days:]) * np.sqrt(252) * 100 if len(returns) >= period_days else historical_vol
            )

            predicted_vol = (historical_vol + recent_vol) / 2

            trend = (
                "increasing"
                if recent_vol > historical_vol * 1.1
                else "decreasing"
                if recent_vol < historical_vol * 0.9
                else "stable"
            )

            return {
                "stock_code": stock_code,
                "prediction_type": "volatility",
                "historical_volatility": float(historical_vol),
                "recent_volatility": float(recent_vol),
                "predicted_volatility": float(predicted_vol),
                "trend": trend,
                "period_days": period_days,
                "confidence": 0.7,
                "model_used": "exp_smoothing",
                "created_at": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error(f"Volatility prediction failed for {stock_code}: {e}")
            return {"error": str(e)}

    def batch_predict(self, stock_codes: List[str], prediction_type: str = "price_direction") -> Dict[str, Any]:
        """
        批量预测

        Args:
            stock_codes: 股票代码列表
            prediction_type: 预测类型
        """
        results = {}
        for code in stock_codes:
            if prediction_type == "price_direction":
                results[code] = self.predict_price_direction(code)
            elif prediction_type == "price_target":
                results[code] = self.predict_price_target(code)
            elif prediction_type == "volatility":
                results[code] = self.predict_volatility(code)
            else:
                results[code] = {"error": f"不支持的预测类型: {prediction_type}"}

        return {
            "prediction_type": prediction_type,
            "stock_count": len(stock_codes),
            "results": results,
            "created_at": datetime.now().isoformat(),
        }

    def _get_historical_data(self, stock_code: str, days: int) -> Optional[pd.DataFrame]:
        """获取历史数据"""
        try:
            if self.data_source_manager:
                data = self.data_source_manager.get_data("akshare.stock_zh_a_hist", symbol=stock_code, period="daily")
                if data is not None and not data.empty:
                    return data.tail(days)
        except Exception as e:
            logger.debug(f"Could not get data for {stock_code}: {e}")

        return None


def create_prediction_service(data_source_manager=None) -> PredictionService:
    """工厂方法：创建预测服务"""
    return PredictionService(data_source_manager=data_source_manager)
