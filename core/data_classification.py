"""
数据分类枚举模块

定义MyStocks系统的5层数据分类体系(23个子项)和数据库类型枚举。
这是整个系统架构的基础,所有数据路由决策都基于这些枚举。

创建日期: 2025-10-11
版本: 1.0.0
"""

from enum import Enum
from typing import List


class DataClassification(str, Enum):
    """
    数据分类枚举 - 23个子项完整定义

    基于宪法第I节: 5层数据分类体系 (不可协商)
    所有数据必须归属以下23个分类之一
    """

    # ==================== 第1类: 市场数据 (6项) ====================
    # 高频时序数据 → TDengine

    TICK_DATA = "TICK_DATA"
    """Tick数据 - 逐笔成交数据,毫秒级,超高频"""

    MINUTE_KLINE = "MINUTE_KLINE"
    """分钟K线 - 1/5/15/30/60分钟行情数据,分钟级,高频"""

    DAILY_KLINE = "DAILY_KLINE"
    """日线/周线/月线 - 日度及以上K线数据,中低频,历史回溯"""

    ORDER_BOOK_DEPTH = "ORDER_BOOK_DEPTH"
    """深度数据 - 订单簿数据,高频,实时订单队列"""

    LEVEL2_SNAPSHOT = "LEVEL2_SNAPSHOT"
    """盘口快照 - Level-2逐笔委托、十档行情,高频,3秒/次"""

    INDEX_QUOTES = "INDEX_QUOTES"
    """指数行情 - 指数分时和日线数据,分时高频+日线中频"""

    # ==================== 第2类: 参考数据 (9项) ====================
    # 相对静态的描述性数据 → MySQL/MariaDB

    SYMBOLS_INFO = "SYMBOLS_INFO"
    """股票信息 - 代码、名称、上市日期等基础属性,静态"""

    INDUSTRY_CLASS = "INDUSTRY_CLASS"
    """行业分类 - 申万一级/二级、证监会行业等分类标准,半静态"""

    CONCEPT_CLASS = "CONCEPT_CLASS"
    """概念分类 - AI、新能源、国企改革等概念标签,半静态,动态更新"""

    INDEX_CONSTITUENTS = "INDEX_CONSTITUENTS"
    """成分股信息 - 沪深300、中证500等指数成分,半静态,定期调整"""

    TRADE_CALENDAR = "TRADE_CALENDAR"
    """交易日历 - 交易日、节假日信息,静态,预定义"""

    FUNDAMENTAL_METRICS = "FUNDAMENTAL_METRICS"
    """结构化财务指标 - 营收、净利润、EPS、ROE等,低频,季度/年度"""

    DIVIDEND_DATA = "DIVIDEND_DATA"
    """分红送配 - 分红比例、除权除息日、送股数量,低频,不定期"""

    SHAREHOLDER_DATA = "SHAREHOLDER_DATA"
    """股东数据 - 大股东增减持、机构持仓变化,低频,月度"""

    MARKET_RULES = "MARKET_RULES"
    """市场规则 - 涨跌幅限制、停牌规则、退市标准,静态,系统级"""

    # ==================== 第3类: 衍生数据 (6项) ====================
    # 计算分析结果 → PostgreSQL+TimescaleDB

    TECHNICAL_INDICATORS = "TECHNICAL_INDICATORS"
    """技术指标 - MACD、RSI、布林带等,计算密集,时序"""

    QUANT_FACTORS = "QUANT_FACTORS"
    """量化因子 - 动量因子、价值因子、基于财务指标的因子,计算密集,多维度"""

    MODEL_OUTPUT = "MODEL_OUTPUT"
    """模型输出 - AI模型预测结果(结构化),二进制权重可选对象存储"""

    TRADE_SIGNALS = "TRADE_SIGNALS"
    """交易信号 - 策略生成的买卖信号,时序,触发式"""

    BACKTEST_RESULTS = "BACKTEST_RESULTS"
    """回测结果 - 收益曲线、最大回撤、夏普比率等,非时序+时序混合"""

    RISK_METRICS = "RISK_METRICS"
    """风险指标 - VaR、行业暴露度、Beta等,计算密集,多维度"""

    # ==================== 第4类: 交易数据 (7项) ====================
    # 全部 → PostgreSQL（历史+实时）

    ORDER_RECORDS = "ORDER_RECORDS"
    """订单记录 - 历史委托记录,持久化,关联成交"""

    TRADE_RECORDS = "TRADE_RECORDS"
    """成交记录 - 历史成交明细,持久化,时序"""

    POSITION_HISTORY = "POSITION_HISTORY"
    """持仓记录 - 历史持仓快照,持久化,历史回溯"""

    REALTIME_POSITIONS = "REALTIME_POSITIONS"
    """实时持仓 - 当前持仓状态,热数据,高频读写"""

    REALTIME_ACCOUNT = "REALTIME_ACCOUNT"
    """实时账户 - 当前账户资金状态,热数据,高频更新"""

    FUND_FLOW = "FUND_FLOW"
    """资金流水 - 资金转入/转出、手续费、分红到账,持久化,时序,审计"""

    ORDER_QUEUE = "ORDER_QUEUE"
    """委托队列 - 未成交委托排队状态,热数据,实时更新"""

    # ==================== 第5类: 元数据 (6项) ====================
    # 系统配置和监控 → PostgreSQL

    DATA_SOURCE_STATUS = "DATA_SOURCE_STATUS"
    """数据源状态 - 数据源健康度、更新状态、完整性校验,配置型,实时监控"""

    TASK_SCHEDULE = "TASK_SCHEDULE"
    """任务调度 - 定时任务配置和执行记录,配置型,定时触发"""

    STRATEGY_PARAMS = "STRATEGY_PARAMS"
    """策略参数 - 策略配置参数、版本管理,配置型,版本化"""

    SYSTEM_CONFIG = "SYSTEM_CONFIG"
    """系统配置 - 系统级参数、权限配置,配置型,全局生效"""

    DATA_QUALITY_METRICS = "DATA_QUALITY_METRICS"
    """数据质量指标 - 完整性率、缺失率、更新延迟,监控型,时序"""

    USER_CONFIG = "USER_CONFIG"
    """用户配置 - 自定义标的组合、看板设置,个性化,用户关联"""

    @classmethod
    def get_all_classifications(cls) -> List[str]:
        """返回所有23个数据分类的列表"""
        return [c.value for c in cls]

    @classmethod
    def get_market_data_classifications(cls) -> List[str]:
        """返回市场数据分类 (6项)"""
        return [
            cls.TICK_DATA.value,
            cls.MINUTE_KLINE.value,
            cls.DAILY_KLINE.value,
            cls.ORDER_BOOK_DEPTH.value,
            cls.LEVEL2_SNAPSHOT.value,
            cls.INDEX_QUOTES.value,
        ]

    @classmethod
    def get_reference_data_classifications(cls) -> List[str]:
        """返回参考数据分类 (9项)"""
        return [
            cls.SYMBOLS_INFO.value,
            cls.INDUSTRY_CLASS.value,
            cls.CONCEPT_CLASS.value,
            cls.INDEX_CONSTITUENTS.value,
            cls.TRADE_CALENDAR.value,
            cls.FUNDAMENTAL_METRICS.value,
            cls.DIVIDEND_DATA.value,
            cls.SHAREHOLDER_DATA.value,
            cls.MARKET_RULES.value,
        ]

    @classmethod
    def get_derived_data_classifications(cls) -> List[str]:
        """返回衍生数据分类 (6项)"""
        return [
            cls.TECHNICAL_INDICATORS.value,
            cls.QUANT_FACTORS.value,
            cls.MODEL_OUTPUT.value,
            cls.TRADE_SIGNALS.value,
            cls.BACKTEST_RESULTS.value,
            cls.RISK_METRICS.value,
        ]

    @classmethod
    def get_transaction_data_classifications(cls) -> List[str]:
        """返回交易数据分类 (7项)"""
        return [
            cls.ORDER_RECORDS.value,
            cls.TRADE_RECORDS.value,
            cls.POSITION_HISTORY.value,
            cls.REALTIME_POSITIONS.value,
            cls.REALTIME_ACCOUNT.value,
            cls.FUND_FLOW.value,
            cls.ORDER_QUEUE.value,
        ]

    @classmethod
    def get_metadata_classifications(cls) -> List[str]:
        """返回元数据分类 (6项)"""
        return [
            cls.DATA_SOURCE_STATUS.value,
            cls.TASK_SCHEDULE.value,
            cls.STRATEGY_PARAMS.value,
            cls.SYSTEM_CONFIG.value,
            cls.DATA_QUALITY_METRICS.value,
            cls.USER_CONFIG.value,
        ]


class DatabaseTarget(str, Enum):
    """
    数据库类型枚举

    定义系统支持的2种数据库类型,每种数据库针对特定数据特性优化
    """

    TDENGINE = "tdengine"
    """TDengine - 时序数据库,超高压缩比(20:1),极致写入性能,用于高频市场数据"""

    POSTGRESQL = "postgresql"
    """PostgreSQL+TimescaleDB - 复杂时序查询,自动分区,用于历史分析、参考数据和衍生数据"""

    @classmethod
    def get_all_targets(cls) -> List[str]:
        """返回所有数据库类型列表"""
        return [t.value for t in cls]


# 版本信息
__version__ = "1.0.0"
__all__ = ["DataClassification", "DatabaseTarget"]
