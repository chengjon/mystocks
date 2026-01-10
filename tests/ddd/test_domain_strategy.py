"""
Comprehensive Domain Layer Tests - Strategy
"""
import pytest
from src.domain.strategy.model.strategy import Strategy
from src.domain.strategy.model.rule import Rule
from src.domain.strategy.value_objects.strategy_id import StrategyId
from src.domain.trading.value_objects import OrderSide

class TestStrategyDomain:
    def test_strategy_creation(self):
        strategy = Strategy.create("EMA Cross", "Double EMA strategy")
        assert strategy.name == "EMA Cross"
        assert not strategy.is_active
        assert strategy.rule_count == 0

    def test_add_rule(self):
        strategy = Strategy.create("Test")
        rule = Rule("RSI", ">", 70, "SELL")
        strategy.add_rule(rule)
        assert strategy.rule_count == 1

    def test_execute_inactive_strategy(self):
        strategy = Strategy.create("Test")
        rule = Rule("RSI", ">", 70, "SELL")
        strategy.add_rule(rule)
        
        market_data = {
            'symbol': '000001',
            'price': 10.0,
            'indicators': {'RSI': 80}
        }
        signals = strategy.execute(market_data)
        assert len(signals) == 0 # Inactive strategies produce no signals

    def test_execute_active_strategy(self):
        strategy = Strategy.create("Test")
        rule = Rule("RSI", ">", 70, "SELL")
        strategy.add_rule(rule)
        strategy.activate()
        
        market_data = {
            'symbol': '000001',
            'price': 10.0,
            'indicators': {'RSI': 80}
        }
        signals = strategy.execute(market_data)
        assert len(signals) == 1
        assert signals[0].side == OrderSide.SELL
