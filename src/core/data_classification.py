#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyStocks 量化交易数据管理系统 - 重构版
完全基于原始设计理念实现的配置驱动、自动化管理系统

设计理念：
1. 配置驱动 - 通过YAML配置文件管理所有表结构
2. 自动化管理 - 避免人工手工管理数据库和表
3. 完整监控 - 专门的监控数据库记录所有操作
4. 数据分类 - 基于数据特性的5大分类体系
5. 业务分离 - 监控数据库与业务数据库完全分离

作者: MyStocks项目组
版本: v2.0 重构版
日期: 2025-09-21
"""

import logging
from enum import Enum


# 导入现有的数据库管理模块

logger = logging.getLogger("MyStocksSystem")


class DataClassification(Enum):
    """数据分类体系 - 基于原始设计的5大分类"""

    # 第1类：市场数据（Market Data）- 时间序列价格数据
    TICK_DATA = "tick_data"  # Tick数据 → TDengine
    MINUTE_KLINE = "minute_kline"  # 分钟K线 → TDengine
    DAILY_KLINE = "daily_kline"  # 日线数据 → PostgreSQL+TimescaleDB
    REALTIME_QUOTES = "realtime_quotes"  # 实时行情快照 → PostgreSQL
    DEPTH_DATA = "depth_data"  # 深度数据 → TDengine
    ORDER_BOOK_DEPTH = "order_book_depth"  # 订单簿深度 → TDengine
    LEVEL2_SNAPSHOT = "level2_snapshot"  # Level2快照 → TDengine
    INDEX_QUOTES = "index_quotes"  # 指数行情 → TDengine

    # 第2类：参考数据（Reference Data）- 相对静态的描述性数据
    SYMBOLS_INFO = "symbols_info"  # 标的列表 → PostgreSQL
    CONTRACT_INFO = "contract_info"  # 合约信息 → PostgreSQL
    CONSTITUENT_INFO = "constituent_info"  # 成分股信息 → PostgreSQL
    TRADE_CALENDAR = "trade_calendar"  # 交易日历 → PostgreSQL
    INDUSTRY_CLASS = "industry_class"  # 行业分类 → PostgreSQL
    CONCEPT_CLASS = "concept_class"  # 概念分类 → PostgreSQL
    INDEX_CONSTITUENTS = "index_constituents"  # 指数成分 → PostgreSQL
    FUNDAMENTAL_METRICS = "fundamental_metrics"  # 基本面指标 → PostgreSQL
    DIVIDEND_DATA = "dividend_data"  # 分红数据 → PostgreSQL
    SHAREHOLDER_DATA = "shareholder_data"  # 股东数据 → PostgreSQL
    MARKET_RULES = "market_rules"  # 市场规则 → PostgreSQL

    # 第3类：衍生数据（Derived Data）- 通过原始数据计算得出
    TECHNICAL_INDICATORS = "technical_indicators"  # 技术指标 → PostgreSQL+TimescaleDB
    QUANTITATIVE_FACTORS = "quantitative_factors"  # 量化因子 → PostgreSQL+TimescaleDB
    MODEL_OUTPUTS = "model_outputs"  # 模型输出 → PostgreSQL+TimescaleDB
    TRADING_SIGNALS = "trading_signals"  # 交易信号 → PostgreSQL+TimescaleDB
    QUANT_FACTORS = "quant_factors"  # 量化因子 → PostgreSQL+TimescaleDB
    MODEL_OUTPUT = "model_output"  # 模型输出（单数形式）→ PostgreSQL+TimescaleDB
    TRADE_SIGNALS = "trade_signals"  # 交易信号（兼容别名）→ PostgreSQL+TimescaleDB
    BACKTEST_RESULTS = "backtest_results"  # 回测结果 → PostgreSQL+TimescaleDB
    RISK_METRICS = "risk_metrics"  # 风险指标 → PostgreSQL+TimescaleDB

    # 第4类：交易数据（Transaction Data）- 策略执行和账户活动
    ORDER_RECORDS = "order_records"  # 订单记录 → PostgreSQL
    TRANSACTION_RECORDS = "transaction_records"  # 成交记录 → PostgreSQL
    POSITION_RECORDS = "position_records"  # 持仓记录 → PostgreSQL
    ACCOUNT_FUNDS = "account_funds"  # 账户资金 → PostgreSQL
    REALTIME_POSITIONS = "realtime_positions"  # 实时持仓 → PostgreSQL（应用层缓存）
    REALTIME_ACCOUNT = "realtime_account"  # 实时账户 → PostgreSQL（应用层缓存）
    TRADE_RECORDS = "trade_records"  # 交易记录 → PostgreSQL
    POSITION_HISTORY = "position_history"  # 持仓历史 → PostgreSQL
    FUND_FLOW = "fund_flow"  # 资金流向 → PostgreSQL
    ORDER_QUEUE = "order_queue"  # 订单队列 → PostgreSQL

    # 第5类：元数据（Meta Data）- 关于数据的数据和系统配置
    DATA_SOURCE_STATUS = "data_source_status"  # 数据源状态 → PostgreSQL
    TASK_SCHEDULES = "task_schedules"  # 任务调度 → PostgreSQL
    STRATEGY_PARAMETERS = "strategy_parameters"  # 策略参数 → PostgreSQL
    SYSTEM_CONFIG = "system_config"  # 系统配置 → PostgreSQL
    TASK_SCHEDULE = "task_schedule"  # 任务调度（单数形式）→ PostgreSQL
    STRATEGY_PARAMS = "strategy_params"  # 策略参数（简写）→ PostgreSQL
    DATA_QUALITY_METRICS = "data_quality_metrics"  # 数据质量指标 → PostgreSQL
    USER_CONFIG = "user_config"  # 用户配置 → PostgreSQL


class DatabaseTarget(Enum):
    """目标数据库类型 - 基于数据特性选择 (Week 3简化后)"""

    TDENGINE = "TDengine"  # 高频时序数据专用
    POSTGRESQL = "PostgreSQL"  # 通用数据仓库+TimescaleDB时序扩展


def __getattr__(name: str):
    if name == "DeduplicationStrategy":
        from .deduplication_strategy import DeduplicationStrategy

        return DeduplicationStrategy
    raise AttributeError(name)
