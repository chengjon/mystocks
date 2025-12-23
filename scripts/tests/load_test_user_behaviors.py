"""
用户行为建模模块
为Locust压测定义5种不同的用户角色和行为模式

任务14.1: Locust压测脚本和用户行为建模
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Tuple
import structlog

logger = structlog.get_logger()


class UserProfile(Enum):
    """用户角色分类"""

    DAY_TRADER = "day_trader"  # 日内交易者 - 高频
    SWING_TRADER = "swing_trader"  # 波段交易者 - 中频
    INVESTOR = "investor"  # 长期投资者 - 低频
    ANALYST = "analyst"  # 分析师 - 高频深度分析
    MONITORING = "monitoring"  # 监控用户 - 后台监控


@dataclass
class UserBehaviorPattern:
    """用户行为模式"""

    profile: UserProfile
    session_duration: int  # 会话时长(秒)
    request_rate: float  # 每秒请求数
    watchlist_size: int  # 自选股数量
    query_types: List[str]  # 查询类型列表
    weight: float  # 在总用户中的比重


class UserBehaviorFactory:
    """用户行为工厂 - 生成真实的用户行为模式"""

    # 用户行为模式定义
    BEHAVIOR_PATTERNS = {
        UserProfile.DAY_TRADER: UserBehaviorPattern(
            profile=UserProfile.DAY_TRADER,
            session_duration=28800,  # 8小时交易时间
            request_rate=2.0,  # 每秒2个请求
            watchlist_size=20,  # 关注20只股票
            query_types=[
                "realtime_data",  # 40% - 实时行情
                "kline_data",  # 30% - K线数据
                "fund_flow",  # 15% - 资金流向
                "search",  # 10% - 搜索
                "watchlist",  # 5% - 自选股管理
            ],
            weight=0.15,  # 日内交易者占15%
        ),
        UserProfile.SWING_TRADER: UserBehaviorPattern(
            profile=UserProfile.SWING_TRADER,
            session_duration=7200,  # 2小时
            request_rate=0.8,  # 每秒0.8个请求
            watchlist_size=30,
            query_types=[
                "kline_data",  # 35% - 中长期K线
                "fund_flow",  # 25% - 资金流向
                "realtime_data",  # 20% - 实时行情
                "industry_analysis",  # 15% - 行业分析
                "watchlist",  # 5% - 自选股
            ],
            weight=0.25,  # 波段交易者占25%
        ),
        UserProfile.INVESTOR: UserBehaviorPattern(
            profile=UserProfile.INVESTOR,
            session_duration=1800,  # 30分钟
            request_rate=0.2,  # 每秒0.2个请求
            watchlist_size=50,  # 更多的关注股票
            query_types=[
                "market_overview",  # 30% - 市场概览
                "search",  # 30% - 搜索股票
                "watchlist",  # 20% - 自选股管理
                "realtime_data",  # 15% - 实时行情
                "kline_data",  # 5% - 历史K线
            ],
            weight=0.40,  # 长期投资者占40%
        ),
        UserProfile.ANALYST: UserBehaviorPattern(
            profile=UserProfile.ANALYST,
            session_duration=14400,  # 4小时
            request_rate=1.5,  # 每秒1.5个请求
            watchlist_size=100,  # 大量跟踪股票
            query_types=[
                "industry_analysis",  # 25% - 行业分析
                "fund_flow",  # 25% - 资金流向
                "kline_data",  # 20% - 多周期K线
                "alert_history",  # 20% - 告警历史(Task 15)
                "service_health",  # 10% - 服务健康度
            ],
            weight=0.15,  # 分析师占15%
        ),
        UserProfile.MONITORING: UserBehaviorPattern(
            profile=UserProfile.MONITORING,
            session_duration=86400,  # 全天24小时
            request_rate=0.1,  # 每秒0.1个请求(低频)
            watchlist_size=0,  # 无自选股
            query_types=[
                "health_check",  # 40% - 健康检查
                "alert_history",  # 40% - 告警历史
                "service_health",  # 20% - 服务健康度
            ],
            weight=0.05,  # 监控用户占5%
        ),
    }

    @classmethod
    def get_random_user_pattern(cls) -> UserBehaviorPattern:
        """根据权重随机选择用户行为模式"""
        patterns = list(cls.BEHAVIOR_PATTERNS.values())
        weights = [p.weight for p in patterns]
        return random.choices(patterns, weights=weights, k=1)[0]

    @classmethod
    def get_pattern(cls, profile: UserProfile) -> UserBehaviorPattern:
        """获取特定的用户行为模式"""
        return cls.BEHAVIOR_PATTERNS.get(profile)


class RequestSequenceGenerator:
    """请求序列生成器 - 生成现实的请求序列"""

    @staticmethod
    def generate_sequence(
        pattern: UserBehaviorPattern, session_duration: int
    ) -> List[Tuple[str, float]]:
        """
        为用户生成请求序列

        返回: [(请求类型, 延迟时间), ...]
        """
        sequence = []
        elapsed_time = 0
        request_interval = 1.0 / pattern.request_rate  # 请求间隔

        while elapsed_time < session_duration:
            # 根据权重选择请求类型
            request_type = random.choices(
                pattern.query_types,
                weights=[0.40, 0.30, 0.15, 0.10, 0.05][  # 对应的权重
                    : len(pattern.query_types)
                ],
                k=1,
            )[0]

            # 添加一些随机波动
            actual_interval = request_interval * random.uniform(0.5, 1.5)

            sequence.append((request_type, actual_interval))
            elapsed_time += actual_interval

        return sequence


class UserSessionSimulator:
    """用户会话模拟器"""

    def __init__(self, user_id: str, pattern: UserBehaviorPattern):
        self.user_id = user_id
        self.pattern = pattern
        self.session_start_time = None
        self.request_count = 0
        self.requests_by_type = {}
        self.response_times = []

    def start_session(self):
        """开始会话"""
        import time

        self.session_start_time = time.time()
        logger.info(f"Session started: {self.user_id} ({self.pattern.profile.value})")

    def end_session(self):
        """结束会话，返回统计信息"""
        import time

        elapsed_time = time.time() - self.session_start_time

        stats = {
            "user_id": self.user_id,
            "profile": self.pattern.profile.value,
            "elapsed_time": elapsed_time,
            "total_requests": self.request_count,
            "requests_by_type": self.requests_by_type,
            "avg_response_time": (
                sum(self.response_times) / len(self.response_times)
                if self.response_times
                else 0
            ),
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "min_response_time": min(self.response_times) if self.response_times else 0,
        }

        logger.info(f"Session ended: {self.user_id}", stats=stats)
        return stats

    def record_request(self, request_type: str, response_time: float):
        """记录请求"""
        self.request_count += 1
        self.requests_by_type[request_type] = (
            self.requests_by_type.get(request_type, 0) + 1
        )
        self.response_times.append(response_time)


class UserBehaviorScenarios:
    """用户行为场景库 - 定义常见的行为序列"""

    @staticmethod
    def morning_open_scenario() -> List[str]:
        """早盘开盘场景 (9:30-10:30)"""
        return [
            "health_check",
            "market_overview",
            "watchlist",
            "realtime_data",
            "realtime_data",
            "fund_flow",
            "kline_data",
        ]

    @staticmethod
    def midday_scenario() -> List[str]:
        """中午场景 (10:30-15:00)"""
        return [
            "realtime_data",
            "realtime_data",
            "realtime_data",  # 高频
            "kline_data",
            "fund_flow",
            "search",
            "watchlist",
            "industry_analysis",
        ]

    @staticmethod
    def afternoon_close_scenario() -> List[str]:
        """午盘收盘场景 (14:30-15:00)"""
        return [
            "realtime_data",
            "realtime_data",
            "kline_data",
            "fund_flow",
            "market_overview",
            "alert_history",
        ]

    @staticmethod
    def after_hours_scenario() -> List[str]:
        """盘后场景 (15:00-20:00)"""
        return [
            "market_overview",
            "kline_data",
            "kline_data",
            "industry_analysis",
            "alert_history",
            "search",
            "watchlist",
        ]

    @staticmethod
    def get_scenario_by_time_of_day(hour: int) -> List[str]:
        """根据时间段获取对应的场景"""
        if 9 <= hour < 10:
            return UserBehaviorScenarios.morning_open_scenario()
        elif 10 <= hour < 12:
            return UserBehaviorScenarios.midday_scenario()
        elif 14 <= hour < 15:
            return UserBehaviorScenarios.afternoon_close_scenario()
        else:
            return UserBehaviorScenarios.after_hours_scenario()


class TrafficModelGenerator:
    """流量模型生成器 - 生成符合市场规律的流量模式"""

    @staticmethod
    def generate_hourly_traffic_profile() -> dict:
        """
        生成按小时的流量分布

        返回: {小时: 相对流量倍数}
        """
        return {
            6: 0.1,  # 凌晨 - 很低
            7: 0.2,  # 清晨 - 低
            8: 0.5,  # 早晨 - 中等
            9: 1.5,  # 早盘 - 高(开盘)
            10: 1.8,  # 上午 - 最高
            11: 1.2,  # 11点 - 中等偏高
            12: 0.6,  # 午盘 - 低(午休)
            13: 0.7,  # 午后 - 低
            14: 1.5,  # 下午 - 高(开盘)
            15: 1.9,  # 收盘 - 最高
            16: 0.8,  # 盘后 - 中等
            17: 0.6,  # 晚上 - 低
            18: 0.5,  # 晚上 - 低
            19: 0.4,  # 夜间 - 很低
            20: 0.3,  # 夜间 - 很低
            21: 0.2,  # 深夜 - 极低
            22: 0.1,  # 深夜 - 极低
            23: 0.05,  # 深夜 - 极低
            0: 0.05,  # 午夜 - 极低
            1: 0.05,  # 凌晨 - 极低
            2: 0.05,  # 凌晨 - 极低
            3: 0.05,  # 凌晨 - 极低
            4: 0.1,  # 凌晨 - 极低
            5: 0.1,  # 凌晨 - 极低
        }

    @staticmethod
    def generate_user_distribution(total_users: int = 1000) -> dict:
        """
        生成用户分布

        返回: {用户角色: 用户数}
        """
        distribution = {}
        for profile, pattern in UserBehaviorFactory.BEHAVIOR_PATTERNS.items():
            user_count = int(total_users * pattern.weight)
            distribution[profile] = user_count

        return distribution

    @staticmethod
    def generate_request_distribution(total_users: int = 1000) -> dict:
        """
        生成请求分布

        返回: {请求类型: 比例}
        """
        distribution = {}
        patterns = UserBehaviorFactory.BEHAVIOR_PATTERNS

        for profile, pattern in patterns.items():
            user_count = int(total_users * pattern.weight)
            # 基于用户数和请求速率
            request_count = user_count * pattern.request_rate

            for query_type in pattern.query_types:
                if query_type not in distribution:
                    distribution[query_type] = 0
                distribution[query_type] += request_count

        # 转换为比例
        total_requests = sum(distribution.values())
        if total_requests > 0:
            distribution = {k: v / total_requests for k, v in distribution.items()}

        return distribution


class LoadTestMetrics:
    """压测指标收集器"""

    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.response_times = []
        self.requests_by_type = {}

    def record_request(
        self, request_type: str, response_time: float, success: bool = True
    ):
        """记录请求"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1

        self.response_times.append(response_time)

        if request_type not in self.requests_by_type:
            self.requests_by_type[request_type] = {
                "count": 0,
                "total_time": 0,
                "avg_time": 0,
            }

        self.requests_by_type[request_type]["count"] += 1
        self.requests_by_type[request_type]["total_time"] += response_time

    def get_summary(self) -> dict:
        """获取统计摘要"""
        success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 0
        )

        response_times_sorted = sorted(self.response_times)
        n = len(response_times_sorted)

        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": f"{success_rate * 100:.2f}%",
            "avg_response_time": (
                sum(self.response_times) / len(self.response_times)
                if self.response_times
                else 0
            ),
            "min_response_time": min(self.response_times) if self.response_times else 0,
            "max_response_time": max(self.response_times) if self.response_times else 0,
            "p50_response_time": response_times_sorted[n // 2] if n > 0 else 0,
            "p95_response_time": response_times_sorted[int(n * 0.95)] if n > 0 else 0,
            "p99_response_time": response_times_sorted[int(n * 0.99)] if n > 0 else 0,
            "requests_by_type": self.requests_by_type,
        }
