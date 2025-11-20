#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks AI策略分析和回测自动化系统
第四阶段：构建智能化策略分析和回测框架
"""

import os
import sys
import json
import time
import asyncio
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """策略类型"""
    MOMENTUM = "momentum"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    ARBITRAGE = "arbitrage"
    ML_BASED = "ml_based"

class SignalType(Enum):
    """信号类型"""
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

@dataclass
class MarketData:
    """市场数据"""
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    vwap: float = 0.0

@dataclass
class TradeSignal:
    """交易信号"""
    timestamp: datetime
    symbol: str
    signal_type: SignalType
    confidence: float
    price: float
    quantity: int
    reason: str

@dataclass
class BacktestResult:
    """回测结果"""
    strategy_name: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float

class MockMarketDataGenerator:
    """模拟市场数据生成器"""
    
    def __init__(self, symbols: List[str] = None):
        self.symbols = symbols or ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH", "000858.SZ"]
        self.price_data = {}
        
    def generate_historical_data(self, days: int = 252) -> Dict[str, List[MarketData]]:
        """生成历史数据（模拟一年的交易日）"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        for symbol in self.symbols:
            self.price_data[symbol] = self._generate_symbol_data(symbol, start_date, end_date)
        
        return self.price_data
    
    def _generate_symbol_data(self, symbol: str, start_date: datetime, end_date: datetime) -> List[MarketData]:
        """为单个股票生成数据"""
        data = []
        current_price = random.uniform(10, 100)  # 初始价格10-100
        
        current_date = start_date
        while current_date <= end_date:
            # 跳过周末
            if current_date.weekday() < 5:  # 0-4是周一到周五
                # 模拟价格变动
                daily_return = random.normalvariate(0.001, 0.02)  # 日均收益0.1%，波动2%
                price_change = current_price * daily_return
                
                open_price = current_price
                close_price = current_price + price_change
                
                # 生成高低价
                volatility = abs(random.normalvariate(0, 0.01))
                high_price = max(open_price, close_price) * (1 + volatility)
                low_price = min(open_price, close_price) * (1 - volatility)
                
                # 生成成交量
                volume = random.randint(100000, 1000000)
                
                # 计算VWAP
                vwap = (open_price + high_price + low_price + close_price) / 4
                
                market_data = MarketData(
                    timestamp=current_date,
                    symbol=symbol,
                    open=open_price,
                    high=high_price,
                    low=low_price,
                    close=close_price,
                    volume=volume,
                    vwap=vwap
                )
                
                data.append(market_data)
                current_price = close_price
            
            current_date += timedelta(days=1)
        
        return data

class AITradingStrategy:
    """AI交易策略基类"""
    
    def __init__(self, name: str, strategy_type: StrategyType):
        self.name = name
        self.strategy_type = strategy_type
        self.signals = []
        self.performance_metrics = {}
        
    def generate_signals(self, market_data: List[MarketData]) -> List[TradeSignal]:
        """生成交易信号"""
        raise NotImplementedError
        
    def calculate_confidence(self, market_data: List[MarketData], current_index: int) -> float:
        """计算信号置信度"""
        # 基础置信度计算
        if len(market_data) < 20:
            return 0.5
        
        recent_data = market_data[max(0, current_index-19):current_index+1]
        price_changes = [data.close - data.open for data in recent_data]
        
        volatility = np.std(price_changes)
        trend_strength = abs(np.mean(price_changes))
        
        confidence = min(0.95, max(0.1, trend_strength / (volatility + 0.001)))
        return confidence

class MomentumStrategy(AITradingStrategy):
    """动量策略"""
    
    def __init__(self, lookback_period: int = 20):
        super().__init__("Momentum Strategy", StrategyType.MOMENTUM)
        self.lookback_period = lookback_period
    
    def generate_signals(self, market_data: List[MarketData]) -> List[TradeSignal]:
        """生成动量信号"""
        signals = []
        
        for i in range(self.lookback_period, len(market_data)):
            current_data = market_data[i]
            lookback_data = market_data[i-self.lookback_period:i]
            
            # 计算移动平均
            ma_current = np.mean([d.close for d in lookback_data])
            ma_previous = np.mean([d.close for d in lookback_data[:-5]])
            
            # 动量信号
            if current_data.close > ma_current and ma_current > ma_previous:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.BUY,
                    confidence=self.calculate_confidence(market_data, i),
                    price=current_data.close,
                    quantity=100,
                    reason=f"动量突破：价格{current_data.close:.2f} > MA{ma_current:.2f}"
                )
            elif current_data.close < ma_current and ma_current < ma_previous:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.SELL,
                    confidence=self.calculate_confidence(market_data, i),
                    price=current_data.close,
                    quantity=100,
                    reason=f"动量反转：价格{current_data.close:.2f} < MA{ma_current:.2f}"
                )
            else:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.HOLD,
                    confidence=0.3,
                    price=current_data.close,
                    quantity=0,
                    reason="动量信号不明确"
                )
            
            signals.append(signal)
        
        self.signals = signals
        return signals

class MeanReversionStrategy(AITradingStrategy):
    """均值回归策略"""
    
    def __init__(self, bollinger_period: int = 20, std_dev_threshold: float = 2.0):
        super().__init__("Mean Reversion Strategy", StrategyType.MEAN_REVERSION)
        self.bollinger_period = bollinger_period
        self.std_dev_threshold = std_dev_threshold
    
    def generate_signals(self, market_data: List[MarketData]) -> List[TradeSignal]:
        """生成均值回归信号"""
        signals = []
        
        for i in range(self.bollinger_period, len(market_data)):
            current_data = market_data[i]
            lookback_data = market_data[i-self.bollinger_period:i]
            
            # 计算布林带
            closes = [d.close for d in lookback_data]
            mean_price = np.mean(closes)
            std_price = np.std(closes)
            
            upper_band = mean_price + (self.std_dev_threshold * std_price)
            lower_band = mean_price - (self.std_dev_threshold * std_price)
            
            # 均值回归信号
            if current_data.close < lower_band:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.BUY,
                    confidence=self.calculate_confidence(market_data, i),
                    price=current_data.close,
                    quantity=100,
                    reason=f"均值回归买入：价格{current_data.close:.2f} < 下轨{lower_band:.2f}"
                )
            elif current_data.close > upper_band:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.SELL,
                    confidence=self.calculate_confidence(market_data, i),
                    price=current_data.close,
                    quantity=100,
                    reason=f"均值回归卖出：价格{current_data.close:.2f} > 上轨{upper_band:.2f}"
                )
            else:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.HOLD,
                    confidence=0.2,
                    price=current_data.close,
                    quantity=0,
                    reason="价格在布林带内，均值回归信号不明确"
                )
            
            signals.append(signal)
        
        self.signals = signals
        return signals

class MLBasedStrategy(AITradingStrategy):
    """基于机器学习的策略"""
    
    def __init__(self, feature_count: int = 10):
        super().__init__("ML-Based Strategy", StrategyType.ML_BASED)
        self.feature_count = feature_count
    
    def generate_signals(self, market_data: List[MarketData]) -> List[TradeSignal]:
        """生成ML策略信号（模拟）"""
        signals = []
        
        for i in range(20, len(market_data)):
            current_data = market_data[i]
            
            # 模拟特征工程和模型预测
            features = self._extract_features(market_data, i)
            prediction = self._ml_predict(features)
            
            if prediction > 0.6:  # 买入阈值
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.BUY,
                    confidence=prediction,
                    price=current_data.close,
                    quantity=100,
                    reason=f"ML预测买入：置信度{prediction:.3f}"
                )
            elif prediction < 0.4:  # 卖出阈值
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.SELL,
                    confidence=1-prediction,
                    price=current_data.close,
                    quantity=100,
                    reason=f"ML预测卖出：置信度{1-prediction:.3f}"
                )
            else:
                signal = TradeSignal(
                    timestamp=current_data.timestamp,
                    symbol=current_data.symbol,
                    signal_type=SignalType.HOLD,
                    confidence=0.5,
                    price=current_data.close,
                    quantity=0,
                    reason=f"ML预测不确定：{prediction:.3f}"
                )
            
            signals.append(signal)
        
        self.signals = signals
        return signals
    
    def _extract_features(self, market_data: List[MarketData], index: int) -> List[float]:
        """提取特征（模拟）"""
        lookback_data = market_data[max(0, index-19):index+1]
        
        features = []
        closes = [d.close for d in lookback_data]
        volumes = [d.volume for d in lookback_data]
        
        # 基础特征
        features.append(np.mean(closes))  # 平均价格
        features.append(np.std(closes))   # 价格波动
        features.append(np.mean(volumes)) # 平均成交量
        features.append((closes[-1] - closes[0]) / closes[0])  # 价格变化率
        
        # 技术指标特征
        if len(closes) >= 20:
            ma_5 = np.mean(closes[-5:])
            ma_20 = np.mean(closes)
            features.append(ma_5 / ma_20)  # MA5/MA20比率
            
            rsi = self._calculate_rsi(closes)
            features.append(rsi / 100)  # RSI标准化
        
        # 填充到固定长度
        while len(features) < self.feature_count:
            features.append(random.uniform(-1, 1))
        
        return features[:self.feature_count]
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = np.mean(gains[-period:]) if gains else 0
        avg_loss = np.mean(losses[-period:]) if losses else 0
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))
    
    def _ml_predict(self, features: List[float]) -> float:
        """模拟ML模型预测"""
        # 简单的模拟预测逻辑
        feature_sum = sum(features)
        
        # Sigmoid激活函数
        prediction = 1 / (1 + np.exp(-feature_sum / 10))
        
        # 添加一些随机性
        noise = random.normalvariate(0, 0.1)
        prediction = max(0, min(1, prediction + noise))
        
        return prediction

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital
        self.commission_rate = 0.001  # 0.1%手续费
        
    def run_backtest(self, strategy: AITradingStrategy, market_data: List[MarketData], symbol: str) -> BacktestResult:
        """运行回测"""
        logger.info(f"📊 开始回测策略: {strategy.name} ({symbol})")
        
        capital = self.initial_capital
        position = 0
        trades = []
        portfolio_values = []
        
        # 生成交易信号
        signals = strategy.generate_signals(market_data)
        
        for signal in signals:
            if signal.signal_type == SignalType.BUY and position == 0:
                # 买入
                cost = signal.quantity * signal.price
                commission = cost * self.commission_rate
                total_cost = cost + commission
                
                if capital >= total_cost:
                    position = signal.quantity
                    capital -= total_cost
                    
                    trades.append({
                        'timestamp': signal.timestamp,
                        'type': 'BUY',
                        'price': signal.price,
                        'quantity': signal.quantity,
                        'cost': total_cost,
                        'reason': signal.reason
                    })
            
            elif signal.signal_type == SignalType.SELL and position > 0:
                # 卖出
                proceeds = position * signal.price
                commission = proceeds * self.commission_rate
                net_proceeds = proceeds - commission
                
                capital += net_proceeds
                
                trades.append({
                    'timestamp': signal.timestamp,
                    'type': 'SELL',
                    'price': signal.price,
                    'quantity': position,
                    'proceeds': net_proceeds,
                    'reason': signal.reason
                })
                
                position = 0
            
            # 计算组合价值
            if position > 0:
                portfolio_value = capital + (position * signal.price)
            else:
                portfolio_value = capital
            
            portfolio_values.append(portfolio_value)
        
        # 计算性能指标
        final_capital = capital + (position * market_data[-1].close if position > 0 else 0)
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # 计算夏普比率
        if len(portfolio_values) > 1:
            returns = [(portfolio_values[i] - portfolio_values[i-1]) / portfolio_values[i-1] 
                      for i in range(1, len(portfolio_values))]
            sharpe_ratio = np.mean(returns) / (np.std(returns) + 0.0001) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # 计算最大回撤
        max_drawdown = self._calculate_max_drawdown(portfolio_values)
        
        # 计算交易统计
        buy_trades = [t for t in trades if t['type'] == 'BUY']
        sell_trades = [t for t in trades if t['type'] == 'SELL']
        
        winning_trades = 0
        losing_trades = 0
        total_wins = 0
        total_losses = 0
        
        for i in range(min(len(buy_trades), len(sell_trades))):
            buy_trade = buy_trades[i]
            sell_trade = sell_trades[i]
            
            profit = sell_trade['proceeds'] - buy_trade['cost']
            if profit > 0:
                winning_trades += 1
                total_wins += profit
            else:
                losing_trades += 1
                total_losses += abs(profit)
        
        win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0
        avg_win = total_wins / winning_trades if winning_trades > 0 else 0
        avg_loss = total_losses / losing_trades if losing_trades > 0 else 0
        profit_factor = total_wins / total_losses if total_losses > 0 else float('inf')
        
        result = BacktestResult(
            strategy_name=strategy.name,
            start_date=market_data[0].timestamp,
            end_date=market_data[-1].timestamp,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            win_rate=win_rate,
            total_trades=len(trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor
        )
        
        logger.info(f"✅ 回测完成: 总收益{total_return:.2%}, 夏普比率{sharpe_ratio:.2f}, 最大回撤{max_drawdown:.2%}")
        
        return result
    
    def _calculate_max_drawdown(self, portfolio_values: List[float]) -> float:
        """计算最大回撤"""
        if not portfolio_values:
            return 0
        
        peak = portfolio_values[0]
        max_drawdown = 0
        
        for value in portfolio_values:
            if value > peak:
                peak = value
            
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown

class AIStrategyAnalyzer:
    """AI策略分析器"""
    
    def __init__(self):
        self.strategies = {}
        self.backtest_results = {}
        
    def register_strategy(self, strategy: AITradingStrategy):
        """注册策略"""
        self.strategies[strategy.name] = strategy
        logger.info(f"📈 策略已注册: {strategy.name} ({strategy.strategy_type.value})")
    
    def run_comprehensive_analysis(self, market_data: Dict[str, List[MarketData]]) -> Dict[str, Any]:
        """运行综合策略分析"""
        logger.info("🚀 开始AI策略综合分析...")
        
        analysis_results = {
            "timestamp": datetime.now().isoformat(),
            "strategies_analyzed": len(self.strategies),
            "symbols_tested": list(market_data.keys()),
            "strategy_results": {},
            "overall_performance": {},
            "recommendations": []
        }
        
        # 对每个策略进行分析
        for strategy_name, strategy in self.strategies.items():
            logger.info(f"📊 分析策略: {strategy_name}")
            
            strategy_result = {
                "strategy_info": {
                    "name": strategy.name,
                    "type": strategy.strategy_type.value,
                    "signal_count": 0
                },
                "symbol_results": {},
                "aggregated_metrics": {}
            }
            
            symbol_performances = []
            
            # 对每个股票进行回测
            for symbol, data in market_data.items():
                if len(data) < 30:  # 至少需要30天数据
                    continue
                
                backtest_engine = BacktestEngine()
                result = backtest_engine.run_backtest(strategy, data, symbol)
                
                strategy_result["symbol_results"][symbol] = {
                    "total_return": result.total_return,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown,
                    "win_rate": result.win_rate,
                    "total_trades": result.total_trades,
                    "profit_factor": result.profit_factor
                }
                
                symbol_performances.append(result)
                strategy_result["strategy_info"]["signal_count"] += len(strategy.signals)
            
            # 计算聚合指标
            if symbol_performances:
                strategy_result["aggregated_metrics"] = {
                    "avg_total_return": np.mean([r.total_return for r in symbol_performances]),
                    "avg_sharpe_ratio": np.mean([r.sharpe_ratio for r in symbol_performances]),
                    "avg_max_drawdown": np.mean([r.max_drawdown for r in symbol_performances]),
                    "avg_win_rate": np.mean([r.win_rate for r in symbol_performances]),
                    "total_trades": sum([r.total_trades for r in symbol_performances]),
                    "success_rate": len([r for r in symbol_performances if r.total_return > 0]) / len(symbol_performances)
                }
            
            analysis_results["strategy_results"][strategy_name] = strategy_result
        
        # 生成总体评估
        self._generate_overall_assessment(analysis_results)
        
        # 生成建议
        self._generate_recommendations(analysis_results)
        
        logger.info("✅ AI策略综合分析完成")
        return analysis_results
    
    def _generate_overall_assessment(self, analysis_results: Dict[str, Any]):
        """生成总体评估"""
        all_returns = []
        all_sharpe_ratios = []
        all_drawdowns = []
        
        for strategy_result in analysis_results["strategy_results"].values():
            metrics = strategy_result.get("aggregated_metrics", {})
            if metrics:
                all_returns.append(metrics.get("avg_total_return", 0))
                all_sharpe_ratios.append(metrics.get("avg_sharpe_ratio", 0))
                all_drawdowns.append(metrics.get("avg_max_drawdown", 0))
        
        if all_returns:
            analysis_results["overall_performance"] = {
                "best_strategy": max(analysis_results["strategy_results"].keys(), 
                                   key=lambda k: analysis_results["strategy_results"][k].get("aggregated_metrics", {}).get("avg_total_return", 0)),
                "avg_portfolio_return": np.mean(all_returns),
                "avg_sharpe_ratio": np.mean(all_sharpe_ratios),
                "avg_max_drawdown": np.mean(all_drawdowns),
                "strategy_count": len(analysis_results["strategy_results"])
            }
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]):
        """生成建议"""
        recommendations = []
        
        best_strategy = analysis_results["overall_performance"].get("best_strategy", "")
        if best_strategy:
            recommendations.append(f"🏆 推荐策略: {best_strategy} (表现最佳)")
        
        # 风险建议
        avg_drawdown = analysis_results["overall_performance"].get("avg_max_drawdown", 0)
        if avg_drawdown > 0.2:
            recommendations.append("⚠️  风险警示: 平均回撤较高，建议增加风险控制措施")
        elif avg_drawdown < 0.1:
            recommendations.append("✅ 风险控制良好: 平均回撤在可接受范围内")
        
        # 夏普比率建议
        avg_sharpe = analysis_results["overall_performance"].get("avg_sharpe_ratio", 0)
        if avg_sharpe > 1.5:
            recommendations.append("📈 收益风险比优秀: 夏普比率较高，风险调整后收益良好")
        elif avg_sharpe < 0.5:
            recommendations.append("📉 收益风险比需改进: 夏普比率较低，建议优化策略")
        
        # 策略多样化建议
        strategy_count = analysis_results["overall_performance"].get("strategy_count", 0)
        if strategy_count < 3:
            recommendations.append("🔄 策略多样化: 建议增加更多不同类型的策略")
        
        analysis_results["recommendations"] = recommendations

def main():
    """主函数"""
    print("="*60)
    print("🚀 MyStocks AI策略分析和回测自动化系统")
    print("="*60)
    
    # 初始化组件
    analyzer = AIStrategyAnalyzer()
    data_generator = MockMarketDataGenerator()
    
    # 生成模拟市场数据
    print("\\n📊 生成模拟市场数据...")
    market_data = data_generator.generate_historical_data(days=252)  # 一年数据
    
    # 创建策略
    print("\\n🔧 初始化AI交易策略...")
    
    momentum_strategy = MomentumStrategy(lookback_period=20)
    mean_reversion_strategy = MeanReversionStrategy(bollinger_period=20, std_dev_threshold=2.0)
    ml_strategy = MLBasedStrategy(feature_count=10)
    
    # 注册策略
    analyzer.register_strategy(momentum_strategy)
    analyzer.register_strategy(mean_reversion_strategy)
    analyzer.register_strategy(ml_strategy)
    
    print(f"✅ 已注册 {len(analyzer.strategies)} 个策略")
    
    # 运行综合分析
    print("\\n🧠 开始AI策略综合分析...")
    analysis_results = analyzer.run_comprehensive_analysis(market_data)
    
    # 打印结果摘要
    print("\\n" + "="*60)
    print("📋 AI策略分析结果摘要")
    print("="*60)
    
    print(f"\\n📊 策略表现:")
    for strategy_name, result in analysis_results["strategy_results"].items():
        metrics = result.get("aggregated_metrics", {})
        if metrics:
            print(f"  • {strategy_name}:")
            print(f"    - 平均收益: {metrics.get('avg_total_return', 0):.2%}")
            print(f"    - 夏普比率: {metrics.get('avg_sharpe_ratio', 0):.2f}")
            print(f"    - 最大回撤: {metrics.get('avg_max_drawdown', 0):.2%}")
            print(f"    - 胜率: {metrics.get('avg_win_rate', 0):.2%}")
            print(f"    - 成功率: {metrics.get('success_rate', 0):.2%}")
    
    overall = analysis_results.get("overall_performance", {})
    if overall:
        print(f"\\n🏆 总体评估:")
        print(f"  • 最佳策略: {overall.get('best_strategy', 'N/A')}")
        print(f"  • 平均组合收益: {overall.get('avg_portfolio_return', 0):.2%}")
        print(f"  • 平均夏普比率: {overall.get('avg_sharpe_ratio', 0):.2f}")
        print(f"  • 平均最大回撤: {overall.get('avg_max_drawdown', 0):.2%}")
    
    print(f"\\n💡 策略建议:")
    for rec in analysis_results.get("recommendations", []):
        print(f"  • {rec}")
    
    # 保存详细结果
    result_file = Path("ai_strategy_analysis_result.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2, default=str)
    
    print(f"\\n📄 详细分析结果已保存到: {result_file}")
    print("="*60)
    
    return analysis_results

if __name__ == "__main__":
    main()
